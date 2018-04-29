import functools
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


async def mcn_client(host, port, commands, buffer_size=1024, wait_t=None):

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
            await read_all_responses(reader, ids, buffer_size)
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
                msg_id, status, timestamps, tail = interpret_robot_response(msg)
                ids_set.remove(msg_id)

        if rest is not None:
            memory = rest

    print('Received all')


class ServerClosedWhileReading(Exception):
    pass
