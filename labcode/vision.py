import sys
import os
import time
import numpy as np
import cv2
import pickle

sys.path.append(os.getcwd())
PHD_CODE = os.environ['PHD_CODE']
sys.path.append(os.path.join(PHD_CODE, 'EPypes'))
sys.path.append(os.path.join(PHD_CODE, 'EPypes/epypes/protobuf'))
sys.path.append(os.path.join(PHD_CODE, 'RPALib'))
sys.path.append(os.path.join(PHD_CODE, 'FxIS/build'))
#sys.path.append(os.path.join(PHD_CODE, 'FxIS/pyfxis'))

from grabber import AVTGrabber
from fxisext import get_timestamps_snaphot, get_timepoints

from epypes import pipeline
from epypes import compgraph
from epypes.queue import Queue
from epypes.zeromq import ZeroMQSubscriber, ZeroMQPublisher
from epypes.pipeline import FullPipeline
from epypes.loop import CommonEventLoop
from epypes.cli import parse_pubsub_args
from epypes.reactivevision import ReactiveVisionSystem, create_queues, dispatch_images
from epypes.protobuf.justbytes_pb2 import JustBytes

from rpa.features import create_feature_matching_cg, METHOD_PARAMS


def prepare_fake_output(pipe):

    # in real app: extract data from pipe
    pose = np.array([1, 1, 1])
    pb_out = JustBytes()
    pb_out.contents = pickle.dumps(pose)

    return pb_out.SerializeToString()


def create_vision_pipeline(q_images, q_out):

    CHOSEN_METHOD = 'orb'

    cg_match = create_feature_matching_cg(CHOSEN_METHOD)

    ft = {p: None for p in METHOD_PARAMS[CHOSEN_METHOD]}
    ft['mask_1'] = None
    ft['mask_2'] = None
    ft['normType'] = cv2.NORM_HAMMING
    ft['crossCheck'] = True

    pipe = FullPipeline(
        'StereoMatcher',
        cg_match,
        q_images,
        q_out,
        dispatch_images,
        prepare_fake_output,
        frozen_tokens=ft
    )

    return pipe


if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(
        default_sub_address='ipc:///tmp/vision-request',
        default_pub_address='ipc:///tmp/vision-response'
    )

    q_in, q_images, q_out = create_queues()

    subscriber = ZeroMQSubscriber(sub_address, q_in)
    grabber = AVTGrabber([0, 1])
    publisher = ZeroMQPublisher(pub_address, q_out)
    pipe = create_vision_pipeline(q_images, q_out)

    rvs = ReactiveVisionSystem(publisher, grabber, pipe, subscriber)
    rvs.start(verbose=True)

    while True:

        try:

            print('Waiting for request_event')
            request_event = q_in.get()
            images = grabber.grab(meta=False)
            q_images.put(images)

        except KeyboardInterrupt as e:

            rvs.stop(verbose=True)
            break
