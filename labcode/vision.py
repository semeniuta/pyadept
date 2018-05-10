import sys
import os
import numpy as np
import cv2
import pickle
import time

sys.path.append(os.getcwd())
PHD_CODE = os.environ['PHD_CODE']
sys.path.append(os.path.join(PHD_CODE, 'EPypes'))
sys.path.append(os.path.join(PHD_CODE, 'EPypes/epypes/protobuf'))
sys.path.append(os.path.join(PHD_CODE, 'FxIS/build'))
sys.path.append(os.path.join(PHD_CODE, 'UntilFocus/untilfocus'))

from grabber import AVTGrabber
from fxisext import get_timestamps_snaphot, get_timepoints

from epypes.zeromq import ZeroMQSubscriber, ZeroMQPublisher
from epypes.pipeline import FullPipeline
from epypes.cli import parse_pubsub_args
from epypes.reactivevision import ReactiveVisionSystem, create_queues, dispatch_images
from epypes.protobuf.pbprocess import add_attribute, copy_downstream_attributes
from epypes.protobuf.event_pb2 import Event

import ufgraph


def prepare_output(pipe):

    resp_event = Event()
    resp_event.type = 'VisionResponse'

    req_event = pipe.get_attr('req_event')
    resp_event.id = req_event.id

    for k, v in pipe.get_attr('timestamps').items():
        add_attribute(resp_event, k, v)

    add_attribute(resp_event, 'sharpness', pipe['sharpness'])
    add_attribute(resp_event, 'time_visionpipe_reacted', pipe.loop.counter.timestamp_event_arrival)
    add_attribute(resp_event, 'time_visionpipe_pub', time.perf_counter())

    return resp_event.SerializeToString()


def create_vision_pipeline(q_images, q_out):

    pipe = FullPipeline(
        'SharpnessMeasurement',
        ufgraph.computational_graph,
        q_images,
        q_out,
        event_dispatcher=lambda im: {'image': im},
        out_prep_func=prepare_output,
        frozen_tokens=ufgraph.parameters
    )

    return pipe


if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(
        default_sub_address='ipc:///tmp/vision-request',
        default_pub_address='ipc:///tmp/vision-response'
    )

    q_in, q_images, q_out = create_queues()

    subscriber = ZeroMQSubscriber(sub_address, q_in)
    grabber = AVTGrabber([2])
    publisher = ZeroMQPublisher(pub_address, q_out)
    pipe = create_vision_pipeline(q_images, q_out)

    rvs = ReactiveVisionSystem(publisher, grabber, pipe, subscriber)
    rvs.start(verbose=True)

    while True:

        try:

            print('Waiting for request_event')
            req_event_bytes = q_in.get()
            t_react = time.perf_counter()

            req_event = Event()
            req_event.ParseFromString(req_event_bytes)
            pipe.set_attr('req_event', req_event)

            print('Grabbing the image')
            t_grab_0= time.perf_counter()
            images_fxis = grabber.grab(meta=False)
            t_grab_1 = time.perf_counter()

            timestamps = {
                't_vision_reacted': t_react,
                't_imacq_reacted': t_grab_0,
                't_imacq_got_im': t_grab_1
            }
            pipe.set_attr('timestamps', timestamps)

            im = cv2.cvtColor( images_fxis[0], cv2.COLOR_BGR2GRAY )
            q_images.put(im)

        except KeyboardInterrupt as e:

            rvs.stop(verbose=True)
            break
