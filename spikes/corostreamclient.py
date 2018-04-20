import asyncio
import itertools
import functools

from pyadept.rprotocol import client_coro
from pyadept import rcommands


if __name__ == '__main__':

    commands = [
        rcommands.DirectCommand('move_home'),
        rcommands.MoveRelJoints([-90, 60, 30, -90, 0, 0]),
        rcommands.MoveRelWorld([0, 0, 185, 0, 0, 0]),
        rcommands.MoveRelWorld([0, 0, -100, 0, 0, 0])
    ]

    loop = asyncio.get_event_loop()

    commands_cycle = itertools.cycle(commands)

    client_coro = client_coro('127.0.0.1', 1234, commands)

    try:
        loop.run_until_complete(client_coro)
    except KeyboardInterrupt:
        print('Stopping the robot client due to keyboard interrupt')
    finally:
        print('Done sending. Closing event loop')
        loop.close()
