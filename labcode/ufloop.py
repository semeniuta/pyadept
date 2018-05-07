"""
"Until focus" loop
"""

import sys
import os
import argparse

sys.path.append(os.getcwd())
PHD_CODE = os.environ['PHD_CODE']
sys.path.append(os.path.join(PHD_CODE, 'EPypes'))
sys.path.append(os.path.join(PHD_CODE, 'EPypes/epypes/protobuf'))

from pyadept import rcommands
from pyadept import rprotocol
from pyadept import asynczmq
from pyadept import strutil

from epypes.protobuf.event_pb2 import Event
from epypes.protobuf.pbprocess import get_attributes_dict


async def init_move(mcn):
    await mcn.cmdexec(
        rcommands.DirectCommand('movehome'),
        rcommands.DirectCommand('break'),
        rcommands.MoveRelJoints([-90, 60, 30, -90, 0, 0]),
        rcommands.MoveRelTool([40, -25, 185, 0, 0, 0]),
        rcommands.MoveRelJoints([0, 0, 0, 0, 0, 1.5]),
    )


async def ufloop(mcn, pspair):

    sharpness = []

    await init_move(mcn)

    while True:

        response_data = await pspair.communicate(strutil.generate_id_bytes())

        vision_response = Event()
        vision_response.ParseFromString(response_data)
        attributes = get_attributes_dict(vision_response.attributes.entries)

        s = attributes['sharpness']
        sharpness.append(s)

        if len(sharpness) > 1 and sharpness[-1] < sharpness[-2]:
            await mcn.cmdexec(rcommands.MoveToolZ(-5))
            break

        await mcn.cmdexec(rcommands.MoveToolZ(5))


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--rhost', default='127.0.0.1')
    arg_parser.add_argument('--rport', default=1234)
    arg_parser.add_argument('--pub', default='ipc:///tmp/psloop-vision-request')
    arg_parser.add_argument('--sub', default='ipc:///tmp/psloop-vision-response')
    args = arg_parser.parse_args()

    mcn = rprotocol.MasterControlNode(args.rhost, args.rport)
    pspair = asynczmq.PubSubPair(args.pub, args.sub)
