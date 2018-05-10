"""
"Until focus" loop
"""

import sys
import os
import argparse
import asyncio
import pandas as pd

sys.path.append(os.getcwd())
PHD_CODE = os.environ['PHD_CODE']
sys.path.append(os.path.join(PHD_CODE, 'EPypes'))
sys.path.append(os.path.join(PHD_CODE, 'EPypes/epypes/protobuf'))

from pyadept import rcommands
from pyadept import rprotocol
from pyadept import strutil

from epypes.protobuf.event_pb2 import Event
from epypes.protobuf.pbprocess import get_attributes_dict


def create_request():

    req = Event()
    req.type = 'VisionRequest'
    req.id = strutil.generate_id_str()

    return req


def interpret_response(pb_resp):

    resp_id = pb_resp.id
    resp_attrs = get_attributes_dict(pb_resp.attributes.entries)

    return resp_id, resp_attrs


async def init_move(mcn):
    await mcn.cmdexec(
        rcommands.DirectCommand('movehome'),
        rcommands.DirectCommand('break'),
        rcommands.MoveRelJoints([-90, 60, 30, -90, 0, 0]),
        rcommands.MoveRelTool([40, -25, 185, 0, 0, 0]),
        rcommands.MoveRelJoints([0, 0, 0, 0, 0, 1]),
    )


async def ufloop(mcn, pbcomm):

    await mcn.connect()

    sharpness = []

    await init_move(mcn)

    while True:

        pb_req = create_request()
        pb_resp = await pbcomm.communicate(pb_req)

        resp_attrs = get_attributes_dict(pb_resp.attributes.entries)
        s = resp_attrs['sharpness']
        sharpness.append(s)
        print('s =', s)

        if len(sharpness) > 1 and (sharpness[-1] < sharpness[-2]):
            await mcn.cmdexec(
                rcommands.SetSpeed(2),
                rcommands.MoveToolZ(5)
            )
            break

    await mcn.cmdexec(rcommands.MoveToolZ(-5))


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--rhost', default='127.0.0.1')
    arg_parser.add_argument('--rport', default=1234)
    arg_parser.add_argument('--pub', default='ipc:///tmp/psloop-vision-request')
    arg_parser.add_argument('--sub', default='ipc:///tmp/psloop-vision-response')
    args = arg_parser.parse_args()

    loop = asyncio.get_event_loop()
    t0 = loop.time()

    datacap = rprotocol.RobotVisionDataCapture(loop, t0)

    mcn = rprotocol.MasterControlNode(loop, args.rhost, args.rport)
    mcn.set_on_send(datacap.on_send_robot)
    mcn.set_on_recv(datacap.on_recv_robot)

    pscomm = rprotocol.ProtobufCommunicator(args.pub, args.sub, response_type=Event)
    pscomm.set_on_send(datacap.on_send_vision)
    pscomm.set_on_recv(datacap.on_recv_vision)

    ufloop_coro = ufloop(mcn, pscomm)

    try:
        loop.run_until_complete( ufloop_coro )
    except KeyboardInterrupt:
        print('Stopping the robot client due to keyboard interrupt')
    finally:
        print('Done sending. Closing event loop')
        loop.close()

    df_robot, df_vision = datacap.prepare_data()
    
    df_robot.to_csv('log_robot.cvs')
    df_vision.to_csv('log_vision.csv')


