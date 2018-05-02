"""
"Until focus" loop
"""

import argparse

from pyadept import rcommands
from pyadept import rprotocol
from pyadept import asynczmq
from pyadept import strutil


async def init_move(mcn):
    await mcn.exec(
        rcommands.DirectCommand('movehome'),
        rcommands.MoveRelJoints([-90, 60, 30, -90, 0, 0])
    )


async def ufloop(mcn, pspair):

    sharpness = []

    await init_move(mcn)

    while True:

        s = await pspair.communicate(strutil.generate_id_bytes())
        sharpness.append(s)

        if len(sharpness) > 1 and sharpness[-1] < sharpness[-2]:
            await mcn.exec(rcommands.MoveToolZ(-5))
            break

        await mcn.exec(rcommands.MoveToolZ(5))


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--rhost', default='127.0.0.1')
    arg_parser.add_argument('--rport', default=1234)
    arg_parser.add_argument('--pub', default='ipc:///tmp/psloop-vision-request')
    arg_parser.add_argument('--sub', default='ipc:///tmp/psloop-vision-response')
    args = arg_parser.parse_args()

    mcn = rprotocol.MasterControlNode(args.rhost, args.rport)
    pspair = asynczmq.PubSubPair(args.pub, args.sub)








