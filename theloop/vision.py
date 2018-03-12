import sys
import os
import time
import numpy as np
import cv2

PHD_CODE = os.environ['PHD_CODE']
sys.path.append(os.getcwd())
sys.path.append(os.path.join(PHD_CODE, 'EPypes'))
sys.path.append(os.path.join(PHD_CODE, 'RPALib'))
sys.path.append(os.path.join(PHD_CODE, 'FxIS/build'))
sys.path.append(os.path.join(PHD_CODE, 'FxIS/pyfxis'))

from grabber import AVTGrabber
from fxisext import get_timestamps_snaphot, get_timepoints

from epypes import pipeline
from epypes import compgraph
from epypes.queue import Queue, create_queue_putter
from epypes.zeromq import ZeroMQSubscriber, ZeroMQPublisher
from epypes.pipeline import FullPipeline
from epypes.loop import CommonEventLoop
from epypes.cli import parse_pubsub_args

from rpa.features import create_feature_matching_cg, METHOD_PARAMS


def create_grab_function(grabber):

    def react(event):
        im1, im2 = grabber.grab(meta=False)

    return react

def dispatch_event(two_images):

    return {'image_1': two_images[0], 'image_2': two_images[1]}


def prepare_output(pipe):

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
            dispatch_event,
            prepare_output,
            frozen_tokens=ft
        )

        return pipe


if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(
        default_pub_address='ipc:///tmp/vision-request',
        default_sub_address='ipc:///tmp/vision-response'
    )

    q_in = Queue()
    q_images = Queue()
    q_out = Queue()

    subscriber = ZeroMQSubscriber(sub_address, q_in)

    grabber = AVTGrabber([0, 1])
    grab_pair = create_queue_putter(
        create_grab_function(grabber),
        q_images
    )

    loop = CommonEventLoop(q_in, grab_pair)

    pipe = create_vision_pipeline(q_images, q_out)

    publisher = ZeroMQPublisher(pub_address, q_out)

    try:

        print('Starting AVTGrabber')
        grabber.start(show_video=False)

        print('Starting publisher at', pub_address)
        publisher.start()

        print('Starting FullPipeline')
        pipe.listen()

        print('Starting CommonEventLoop')
        loop.start()

        print('Starting subscriber at', sub_address)
        subscriber.start()

    except KeyboardInterrupt as e:

        print('Stopping AVTGrabber')
        g.stop()
