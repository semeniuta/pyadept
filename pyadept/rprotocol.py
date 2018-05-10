import asyncio
import pandas as pd

from pyadept.strutil import split_data, generate_id_bytes
from pyadept.asynczmq import PubSubPair
from pyadept.rcommands import DELIMITER

from epypes.protobuf.pbprocess import get_attributes_dict


def interpret_robot_response(msg):

    elements = msg.split(b':')

    msg_id, status, timestamps = elements[:3]
    tail = elements[3:]

    return msg_id, status, timestamps, tail


def interpret_vision_response(pb_resp):

    resp_id = pb_resp.id
    resp_attrs = get_attributes_dict(pb_resp.attributes.entries)

    return resp_id, resp_attrs


def add_id(request_id, msg):
    return request_id + b':' + msg


class MasterControlNode(object):

    def __init__(self, loop, r_host, r_port, buffer_size=2048):

        self._loop = loop

        self._host = r_host
        self._port = r_port

        self._buffer_size = buffer_size

        self._reader = None
        self._writer = None

        self._ids = set()

        self._on_send = None
        self._on_recv = None
        self._on_done = None

    def set_on_send(self, callback):
        self._on_send = callback

    def set_on_recv(self, callback):
        self._on_recv = callback

    def set_on_done(self, callback):
        self._on_done = callback

    async def connect(self):

        r, w = await asyncio.open_connection(self._host, self._port)
        self._reader = r
        self._writer = w

    async def cmdexec(self, *commands, wait_t=0):

        await send_command_sequence(
            commands,
            self._reader,
            self._writer,
            self._ids,
            self._buffer_size,
            wait_t,
            self._on_send,
            self._on_recv,
            self._on_done
        )


class ProtobufCommunicator(PubSubPair):
    """
    A subclass of PubSubPair that accepts and returns Protobuf objects
    (and not raw byte strings as PubSubPair)
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


async def connect_and_execute_commands(host, port, commands, buffer_size=1024, wait_t=None):

    reader, writer = await asyncio.open_connection(host, port)
    ids = set()
    await send_command_sequence(commands, reader, writer, ids, buffer_size, wait_t)


async def send_command_sequence(
    commands,
    reader,
    writer,
    ids_set,
    buffer_size=1024,
    wait_t=0,
    on_send=None,
    on_recv=None,
    on_done=None
):
    """
    Execute a sequnces of commands by sending the correspodning byte strings
    using the supplied AsyncIO writer. After each command's bytes are sent,
    responses from reader are received so that every command is acknowledged
    by the server.

    Callback functions with the following signatures:
    on_send accepts (command, command_id, command_data)
    on_recv accepts (messages, rest)
    on_done is called without arguments
    """

    for cmd in commands:

        await send_command(cmd, writer, ids_set, on_send)
        await asyncio.sleep(wait_t)

        try:
            await read_all_responses(reader, ids_set, buffer_size, on_recv, on_done)
        except ServerClosedWhileReading:
            writer.close()
            return

    await writer.drain()


async def send_command(command, writer, ids_set, on_send=None):

    for cmd_bytes in command.get_bytes():

        cmd_id = generate_id_bytes()
        cmd_data = add_id(cmd_id, cmd_bytes)

        writer.write(cmd_data)
        ids_set.add(cmd_id)

        if on_send is not None:
            on_send(command, cmd_id, cmd_data)


async def read_all_responses(reader, ids_set, buffer_size=1024, on_recv=None, on_done=None):

    memory = b''

    while len(ids_set) > 0:

        data = await reader.read(buffer_size)

        if not data:
            raise ServerClosedWhileReading

        all_data = memory + data
        memory = b''

        messages, rest = split_data(all_data, DELIMITER)

        if on_recv is not None:
            on_recv(messages, rest)

        if messages is not None:
            for msg in messages:
                msg_id, status, timestamps, tail = interpret_robot_response(msg)
                ids_set.remove(msg_id)

        if rest is not None:
            memory = rest

    if on_done is not None:
        on_done()


class ServerClosedWhileReading(Exception):
    pass


class RobotVisionDataCapture(object):

    def __init__(self, loop, t0):
        self._loop = loop
        self._t0 = t0

        self._log_robot = dict()
        self._log_vision = dict()

        self._robot_responses = []
        self._vision_responses = []

    def current_time(self):
        return self._loop.time() - self._t0

    def on_send_robot(self, cmd, cmd_id, cmd_data):
        t = self.current_time()
        self._log_robot[cmd_id] = {'data': cmd_data, 't_send': t}

    def on_recv_robot(self, messages, rest):
        t = self.current_time()
        for msg in messages:
            self._robot_responses.append((msg, t))

    def on_send_vision(self, pb_request):
        t = self.current_time()
        self._log_vision[pb_request.id] = {'time_sent': t}

    def on_recv_vision(self, pb_response):
        t = self.current_time()
        self._vision_responses.append((pb_response, t))

    def prepare_data(self):

        for msg, t in self._robot_responses:
            msg_id, status, timestamps, tail = interpret_robot_response(msg)
            robot_t0, robot_t1 = (float(el) for el in timestamps.split(b','))

            self._log_robot[msg_id].update({
                'resp_status': status,
                'robot_t0': robot_t0,
                'robot_t1': robot_t1,
            })

        for pb_resp, t in self._vision_responses:
            resp_id, resp_attrs = interpret_vision_response(pb_resp)
            self._log_vision[resp_id].update(resp_attrs)

        df_robot = pd.DataFrame(self._log_robot)
        df_vision = pd.DataFrame(self._log_vision)

        return df_robot, df_vision

