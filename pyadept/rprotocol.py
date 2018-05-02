import asyncio

from pyadept.strutil import split_data, generate_id_bytes
from pyadept.rcommands import DELIMITER


def interpret_robot_response(msg):

    elements = msg.split(b':')

    msg_id, status, timestamps = elements[:3]
    tail = elements[3:]

    return msg_id, status, timestamps, tail


def add_id(request_id, msg):
    return request_id + b':' + msg


class MasterControlNode(object):

    def __init__(self, r_host, r_port, buffer_size=2048):

        self._host = r_host
        self._port = r_port

        self._buffer_size = buffer_size

        self._reader = None
        self._writer = None

        self._ids = set()

    async def connect(self):

        r, w = await asyncio.open_connection(self._host, self._port)
        self._reader = r
        self._writer = w

    async def exec(self, *commands, wait_t=0):

        await send_command_sequence(
            commands,
            self._reader,
            self._writer,
            self._ids,
            self._buffer_size,
            wait_t
        )


async def connect_and_execute_commands(host, port, commands, buffer_size=1024, wait_t=None):

    reader, writer = await asyncio.open_connection(host, port)
    ids = set()
    await send_command_sequence(commands, reader, writer, ids, buffer_size, wait_t)


async def send_command_sequence(commands, reader, writer, ids_set, buffer_size=1024, wait_t=0):
    """
    Execute a sequnces of commands by sending the correspodning byte strings
    using the supplied AsyncIO writer. After each command's bytes are sent,
    responses from reader are received so that every command is acknowledged
    by the server
    """

    for cmd in commands:

        await send_command(cmd, writer, ids_set)
        await asyncio.sleep(wait_t)

        try:
            await read_all_responses(reader, ids_set, buffer_size)
        except ServerClosedWhileReading:
            writer.close()
            return

    await writer.drain()


async def send_command(command, writer, ids_set):

    for cmd_bytes in command.get_bytes():

        cmd_id = generate_id_bytes()
        cmd_data = add_id(cmd_id, cmd_bytes)

        writer.write(cmd_data)
        ids_set.add(cmd_id)

        print('Sent:', cmd_data)


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
                msg_id, status, timestamps, tail = interpret_robot_response(msg)
                ids_set.remove(msg_id)

        if rest is not None:
            memory = rest

    print('Received all')


class ServerClosedWhileReading(Exception):
    pass
