"""
Playing with the stream-based MCN client
"""

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
        rcommands.DirectCommand('break'),
        rcommands.MoveRelJoints([-90, 60, 30, -90, 0, 0]),
        rcommands.SetSpeed(5),
        rcommands.MoveRelTool([40, -25, 185, 0, 0, 0]),
        rcommands.MoveRelJoints([0, 0, 0, 0, 0, 1.5]),

    ]

    loop = asyncio.get_event_loop()

    commands_cycle = itertools.cycle(commands) # not yet used

    mcn = rprotocol.MasterControlNode(loop, args.host, args.port, args.buffersize)

    mcn.set_on_recv( lambda messages, rest: print('messages={}, rest={}'.format(messages, rest)) )
    mcn.set_on_send( lambda cmd, cmd_id, cmd_data: print('Sent:', cmd_data) )
    mcn.set_on_done( lambda: print('Received all') )

    async def client():
        await mcn.connect()
        await mcn.cmdexec(*commands, wait_t=args.sleep)

    client_coro = client()

    try:
        loop.run_until_complete( client_coro )
    except KeyboardInterrupt:
        print('Stopping the robot client due to keyboard interrupt')
    finally:
        print('Done sending. Closing event loop')
        loop.close()
