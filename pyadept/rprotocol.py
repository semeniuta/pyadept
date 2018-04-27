import functools
import asyncio

from pyadept.strutil import split_data, generate_id_bytes
from pyadept.asioutil import GenericProtocol
from pyadept.rcommands import DELIMITER


def interpret_robot_response(msg):

    elements = msg.split(b':')

    msg_id, status, timestamp = elements[:3]
    tail = elements[3:]

    return msg_id, status, timestamp, tail


def add_id(request_id, msg):
    return request_id + b':' + msg


def create_robot_client_from_protocol(loop, commands, host, port):

    f_completed = loop.create_future()
    stop_event = asyncio.Event()

    client_factory = functools.partial(
        MCNClientProtocol,
        loop=loop,
        commands=commands,
        future_session_completed=f_completed,
        stop_event=stop_event
    )

    client_coro = loop.create_connection(client_factory, host, port)

    return client_coro, f_completed, stop_event


async def client_coro(host, port, commands, wait_t=None):

    reader, writer = await asyncio.open_connection(host, port)

    ids = set()

    for cmd in commands:

        for cmd_bytes in cmd.get_bytes():

            cmd_id = generate_id_bytes()
            cmd_data = add_id(cmd_id, cmd_bytes)

            writer.write(cmd_data)
            ids.add(cmd_id)

            print('Sent:', cmd_data)

        if wait_t is not None:
            await asyncio.sleep(wait_t)

        try:
            await read_all_responses(reader, ids, 32)
        except ServerClosedWhileReading:
            writer.close()
            return

    await writer.drain()


async def read_all_responses(reader, ids_set, buffer_size=1024):

    memory = b''

    while len(ids_set) > 0:

        data = await reader.read(buffer_size)

        if not data:
            raise ServerClosedWhileReading

        all_data = memory + data
        memory = b''

        messages, rest = split_data(all_data, DELIMITER)
        print('messages={}, rest={}'.format(messages, rest))

        if messages is not None:
            for msg in messages:
                msg_id, status, timestamp, tail = interpret_robot_response(msg)
                ids_set.remove(msg_id)

        if rest is not None:
            memory = rest

    print('Received all')


class ServerClosedWhileReading(Exception):
    pass


class MCNClientProtocol(GenericProtocol):
    """
    Master Control Node TCP Client Protocol
    """

    def __init__(self, loop, commands, future_session_completed, stop_event):

        super(MCNClientProtocol, self).__init__(loop)
        self._commands = commands
        self._future_session_completed = future_session_completed
        self._stop_event = stop_event # <- not yet used

    def connection_made(self, transport):

        self._transport = transport
        self._ids = set()

        endpoint = self._transport.get_extra_info('peername')
        self._log('Connected with: {}'.format(endpoint))

        for command in self._commands:

            for cmd_bytes in command.get_bytes():

                cmd_id = generate_id_bytes()
                cmd_data = add_id(cmd_id, cmd_bytes)

                self._transport.write(cmd_data)
                self._ids.add(cmd_id)

                self._log('Sent: {}'.format(cmd_data))

    def data_received(self, data):

        self._log('Received: {}'.format(data))

        all_data = self._merge_data_with_rest(data)
        messages, rest = split_data(all_data, DELIMITER)

        if messages is not None:
            for msg in messages:
                msg_id, status = interpret_robot_response(msg)
                self._ids.remove(msg_id)
                if len(self._ids) == 0:
                    self._future_session_completed.set_result(True)
                    # close connection ?

        if rest is not None:
            self._update_rest(rest)

    def connection_lost(self, error):
        self._log('Connection lost: {}'.format(str(error)))
        self._future_session_completed.set_result(True)
