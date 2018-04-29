import sys
import os
sys.path.append(os.getcwd())

import asyncio
import itertools
import argparse

from pyadept import rprotocol
from pyadept import rcommands


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--host', default='127.0.0.1')
    arg_parser.add_argument('--port', default=1234)
    arg_parser.add_argument('--sleep', type=float, default=0.)
    arg_parser.add_argument('--buffersize', type=int, default=32)
    args = arg_parser.parse_args()

    commands = [
        rcommands.DirectCommand('movehome'),
        rcommands.MoveRelJoints([-90, 60, 30, -90, 0, 0]),
        rcommands.MoveRelWorld([0, 0, 185, 0, 0, 0]),
        rcommands.MoveRelWorld([0, 0, -100, 0, 0, 0])
    ]

    loop = asyncio.get_event_loop()

    commands_cycle = itertools.cycle(commands)

    client_coro = rprotocol.client_coro(
        args.host,
        args.port, commands,
        buffer_size=args.buffersize,
        wait_t=args.sleep
    )

    try:
        loop.run_until_complete(client_coro)
    except KeyboardInterrupt:
        print('Stopping the robot client due to keyboard interrupt')
    finally:
        print('Done sending. Closing event loop')
        loop.close()
