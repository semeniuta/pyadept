import asyncio
import pandas as pd

from pyadept.strutil import split_data, generate_id_bytes
from pyadept.asynczmq import PubSubPair
from pyadept.rcommands import DELIMITER
from pyadept.pbutil import get_attributes_dict

SERVER_BUFFER_SIZE = 2048


def split_robot_response(msg):
    """
    Split byte string from RobotServer into parts corresponding to:
    message id, status, timestamps, tail (rest of the bytes)
    """

    elements = msg.split(b':')

    msg_id, status, timestamps, pose = elements[:4]
    tail = elements[4:]

    return msg_id, status, timestamps, pose, tail


def interpret_vision_response(pb_resp):
    """
    Interpret a Protobuf response object received from the vision system.
    Returns response ID and dictionary of attributes
    """

    resp_id = pb_resp.id
    resp_attrs = get_attributes_dict(pb_resp.attributes.entries)

    return resp_id, resp_attrs


def join_id_with_message(request_id, msg):
    return request_id + b':' + msg


class RobotClient(object):
    """
    AsyncIO-based client of a RobotServer.
    """

    def __init__(self, loop, r_host, r_port, buffer_size=2048, wait_t=0):

        self._loop = loop # FIXME never used

        self._host = r_host
        self._port = r_port

        self._buffer_size = buffer_size
        self._wait_t = wait_t

        self._reader = None
        self._writer = None

        self._on_send = None
        self._on_recv = None
        self._on_done = None

    def set_on_send(self, callback):
        """
        Register on_send callback. Should be a callable
        that accepts (command, command_id, command_data)
        """

        self._on_send = callback

    def set_on_recv(self, callback):
        """
        Register on_recv callback. Should be a callable
        that accepts (messages, rest)
        """

        self._on_recv = callback

    def set_on_done(self, callback):
        """
        Register on_done callback. Should be a callable
        without arguments
        """

        self._on_done = callback

    async def connect(self):
        """
        Connect to RobotServer and initialize
        StreamReader and StreamWriter
        """

        r, w = await asyncio.open_connection(self._host, self._port)
        self._reader = r
        self._writer = w

    async def cmdexec(self, *commands):
        """
        Execute one or more commands by sending them to RobotServer.
        After all command's bytes are sent, responses from reader are
        received so that every command is acknowledged by the server.
        """

        ids = set()
        n_bytes_sent = 0

        for cmd in commands:

            for cmd_bytes in cmd.get_bytes():

                cmd_id = generate_id_bytes()
                cmd_data = join_id_with_message(cmd_id, cmd_bytes)
                data_len = len(cmd_data)

                if n_bytes_sent + data_len <= SERVER_BUFFER_SIZE:

                    print('Sending a message. Current buffer size: {}'.format(n_bytes_sent))
                    
                    self._writer.write(cmd_data)
                    
                    ids.add(cmd_id)
                    n_bytes_sent += data_len
                    
                    if self._on_send is not None:
                        self._on_send(cmd, cmd_id, cmd_data)
                
                else:

                    print('Waiting for responses...')

                    try:
                        await self._read_all_responses(ids)
                        n_bytes_sent = 0
                    except ServerClosedWhileReading:
                        self._writer.close()
                        return
            
            await asyncio.sleep(self._wait_t)
        
        await self._writer.drain()

    async def _read_all_responses(self, ids):
        """
        Read all responses corresponding to IDs in the ids set
        using the supplied StreamReader
        """

        memory = b''

        while len(ids) > 0:

            data = await self._reader.read(self._buffer_size)

            if not data:
                raise ServerClosedWhileReading

            all_data = memory + data
            memory = b''

            messages, rest = split_data(all_data, DELIMITER)

            if self._on_recv is not None:
                self._on_recv(messages, rest)

            if messages is not None:
                for msg in messages:
                    msg_id, status, timestamps, pose, tail = split_robot_response(msg)
                    ids.remove(msg_id)

            if rest is not None:
                memory = rest

        if self._on_done is not None:
            self._on_done()


class ProtobufCommunicator(PubSubPair):
    """
    A subclass of PubSubPair that accepts and returns Protobuf objects
    (and not raw byte strings as PubSubPair).
    The class overrides send and recv coroutine methods
    and adds support for on_send and on_recv callbacks.
    """

    def __init__(self, pub_address, sub_address, response_type, poll_timeout=0.001):

        super(ProtobufCommunicator, self).__init__(pub_address, sub_address, poll_timeout)

        self._response_type = response_type

        self._on_send = None
        self._on_recv = None

    def set_on_send(self, callback):
        self._on_send = callback

    def set_on_recv(self, callback):
        self._on_recv = callback

    async def send(self, pb_request):

        pb_event_bytes = pb_request.SerializeToString()
        await super(ProtobufCommunicator, self).send(pb_event_bytes)

        if self._on_send is not None:
            self._on_send(pb_request)

    async def recv(self):

        pb_response_bytes = await super(ProtobufCommunicator, self).recv()

        pb_response = self._response_type()
        pb_response.ParseFromString(pb_response_bytes)

        if self._on_recv is not None:
            self._on_recv(pb_response)

        return pb_response


class ServerClosedWhileReading(Exception):
    pass


class RobotVisionDataCapture(object):
    """
    The class providing data capture functionality
    when communicating with a vision system.

    on_send_robot and on_recv_robot are handed to
    a RobotClient as callbacks.
    on_send_vision and on_recv_vision are handed to
    a ProtobufCommunicator as callbacks.

    After the session is over, the prepare_data method is
    invoked to return Pandas dataframes
    with robot and vision logs.
    """

    def __init__(self, loop, t0, verbose=False):
        self._loop = loop
        self._t0 = t0

        self._log_robot = dict()
        self._log_vision = dict()

        self._robot_responses = []
        self._vision_responses = []

        self._verbose = verbose

        self._robot_count = 0
        self._vision_count = 0

    def current_time(self):
        return self._loop.time() - self._t0

    def on_send_robot(self, cmd, cmd_id, cmd_data):

        t = self.current_time()

        self._log_robot[cmd_id] = {
            'command': cmd,
            'data': cmd_data,
            't_send': t,
            'count': self._robot_count
        }
        self._robot_count += 1

        if self._verbose:
            print('[{:.3f}] send_robot: {}'.format(t, cmd_data))

    def on_recv_robot(self, messages, rest):

        t = self.current_time()

        for msg in messages:
            self._robot_responses.append((msg, t))

        if self._verbose:
            print('[{:.3f}] recv_robot: {}'.format(t, messages))

    def on_send_vision(self, pb_request):

        t = self.current_time()

        self._log_vision[pb_request.id] = {
            'time_sent': t,
            'count': self._vision_count
        }
        self._vision_count += 1

        if self._verbose:
            print('[{:.3f}] send_vision: {}'.format(t, pb_request.id))

    def on_recv_vision(self, pb_response):

        t = self.current_time()

        self._vision_responses.append((pb_response, t))

        if self._verbose:
            print('[{:.3f}] recv_vision: {}'.format(t, pb_response.id))

    def prepare_data(self):

        for msg, t in self._robot_responses:
            msg_id, status, timestamps, pose, tail = split_robot_response(msg)
            robot_t0, robot_t1 = tuple(float(el) for el in timestamps.split(b','))
            pose_vals = tuple(float(el) for el in pose.split(b','))

            self._log_robot[msg_id].update({
                'resp_status': status,
                'robot_t0': robot_t0,
                'robot_t1': robot_t1,
                'x': pose_vals[0],
                'y': pose_vals[1],
                'z': pose_vals[2],
                'yaw': pose_vals[3],
                'pitch': pose_vals[4],
                'roll': pose_vals[5],
            })

            self._log_robot[msg_id]['t_recv'] = t

        for pb_resp, t in self._vision_responses:
            resp_id, resp_attrs = interpret_vision_response(pb_resp)
            self._log_vision[resp_id].update(resp_attrs)
            self._log_vision[resp_id]['time_recv'] = t

        df_robot = pd.DataFrame.from_dict(self._log_robot, orient='index')
        df_vision = pd.DataFrame.from_dict(self._log_vision, orient='index')

        for df in (df_robot, df_vision):
            df['id'] = df.index
            df.set_index('count', inplace=True)
            df.sort_index(inplace=True)

        return df_robot, df_vision
