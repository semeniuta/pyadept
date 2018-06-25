"""
Attempt to implement an MCN TCP client using AsyncIO protocol
(too complicated comparing to using streams)
"""

import asyncio
import functools
import itertools

from pyadept.asioutil import GenericProtocol
from pyadept.rprotocol import generate_id_bytes, join_id_with_message, split_robot_response
from pyadept.strutil import split_data, generate_id_bytes
from pyadept.rcommands import DELIMITER
from pyadept import rcommands


class MCNClientProtocol(GenericProtocol):

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
                cmd_data = join_id_with_message(cmd_id, cmd_bytes)

                self._transport.write(cmd_data)
                self._ids.add(cmd_id)

                self._log('Sent: {}'.format(cmd_data))

    def data_received(self, data):

        self._log('Received: {}'.format(data))

        all_data = self._merge_data_with_rest(data)
        messages, rest = split_data(all_data, DELIMITER)

        if messages is not None:
            for msg in messages:
                msg_id, status, timestamp, tail = split_robot_response(msg)
                self._ids.remove(msg_id)
                if len(self._ids) == 0:
                    self._future_session_completed.set_result(True)
                    # close connection ?

        if rest is not None:
            self._update_rest(rest)

    def connection_lost(self, error):
        self._log('Connection lost: {}'.format(str(error)))
        self._future_session_completed.set_result(True)


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

if __name__ == '__main__':

    commands = [
        rcommands.DirectCommand('move_home'),
        rcommands.MoveRelJoints([-90, 60, 30, -90, 0, 0]),
        rcommands.MoveRelWorld([0, 0, 185, 0, 0, 0]),
        rcommands.MoveRelWorld([0, 0, -100, 0, 0, 0])
    ]

    loop = asyncio.get_event_loop()

    commands_cycle = itertools.cycle(commands)

    client_coro, client_completed, stop_event = create_robot_client_from_protocol(
        loop,
        commands,
        '127.0.0.1',
        1234
    )

    try:
        loop.run_until_complete(client_coro)
        loop.run_until_complete(client_completed)
    except KeyboardInterrupt:
        print('Stopping the robot client due to keyboard interrupt')
    finally:
        print('Done sending. Closing event loop')
        loop.close()

