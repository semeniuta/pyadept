"""
Simulator of RobotServer implemented as an AsyncIO protocol,
launched concurrently with a periodic tick task
"""

import sys
import os
sys.path.append(os.getcwd())

import asyncio
import functools

from pyadept.strutil import split_data
from pyadept.asioutil import GenericProtocol, create_server, create_periodic_task
from pyadept.rcommands import DELIMITER


class RobotServerSimulator(GenericProtocol):

    def connection_made(self, transport):

        self._transport = transport

        endpoint = self._transport.get_extra_info('peername')
        self._log('Connected with: {}'.format(endpoint))

    def data_received(self, data):

        t0 = self._current_time()

        self._log('Received: {}'.format(data))

        all_data = self._merge_data_with_rest(data)
        commands, rest = split_data(all_data, DELIMITER)

        if commands is not None:
            for command in commands:

                command_id = command.split(b':')[0]

                t1 = self._current_time()
                msg_back = command_id + b':done:' + '{:.3f},{:.3f}'.format(t0, t1).encode() + DELIMITER

                self._transport.write(msg_back)
                self._log('Sent back: {}'.format(msg_back))

        if rest is not None:
            self._update_rest(rest)


    def connection_lost(self, error):
        self._log('Connection lost: {}'.format(str(error)))


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    server_factory = functools.partial(RobotServerSimulator, loop=loop)
    server = create_server(server_factory, loop, '', 1234)

    t0 = loop.time()
    stop_ticking, tick = create_periodic_task(
        loop,
        lambda: print( 't={:.3f}'.format(loop.time() - t0) )
    )

    future_tick = asyncio.ensure_future( tick(interval=0.1) )

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stopping the server due to keyboard interrupt')
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        stop_ticking.set()
        loop.run_until_complete(future_tick)
        loop.close()
