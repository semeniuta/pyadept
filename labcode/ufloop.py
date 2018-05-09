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
        rcommands.MoveRelJoints([0, 0, 0, 0, 0, 1]),
    )


async def ufloop(mcn, pspair):

    await mcn.connect()

    sharpness = []

    await init_move(mcn)

    while True:

        response_data = await pspair.communicate(strutil.generate_id_bytes())

        vision_response = Event()
        vision_response.ParseFromString(response_data)
        attributes = get_attributes_dict(vision_response.attributes.entries)

        s = attributes['sharpness']
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

    log_dict = dict()
    responses = []

    def on_send(cmd, cmd_id, cmd_data):
        t = loop.time() - t0
        log_dict[cmd_id] = {'data': cmd_data, 't_send': t}

    def on_recv(messages, rest):
        t = loop.time() - t0
        for msg in messages:
            responses.append( (msg, t) )

    mcn = rprotocol.MasterControlNode(loop, args.rhost, args.rport)
    mcn.set_on_send(on_send)
    mcn.set_on_recv(on_recv)

    pspair = asynczmq.PubSubPair(args.pub, args.sub)

    ufloop_coro = ufloop(mcn, pspair)

    try:
        loop.run_until_complete( ufloop_coro )
    except KeyboardInterrupt:
        print('Stopping the robot client due to keyboard interrupt')
    finally:
        print('Done sending. Closing event loop')
        loop.close()

    for msg, t in responses:

        msg_id, status, timestamps, tail = rprotocol.interpret_robot_response(msg)
        robot_t0, robot_t1 = ( float(el) for el in timestamps.split(b',') )

        log_dict[msg_id].update({
            'resp_status': status,
            'robot_t0': robot_t0,
            'robot_t1': robot_t1,
        })

    df = pd.DataFrame(log_dict)
    df.to_csv('log.cvs')


