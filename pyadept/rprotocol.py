import asyncio

from pyadept.strutil import split_data, generate_id_bytes
from pyadept.asynczmq import PubSubPair
from pyadept.rcommands import DELIMITER


def interpret_robot_response(msg):

    elements = msg.split(b':')

    msg_id, status, timestamps = elements[:3]
    tail = elements[3:]

    return msg_id, status, timestamps, tail


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
    by the server
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
