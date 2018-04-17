'''
Interactive requester tool
'''

import sys, os
sys.path.append(os.getcwd())
PHD_CODE = os.environ['PHD_CODE']
sys.path.append(os.path.join(PHD_CODE, 'EPypes'))
sys.path.append(os.path.join(PHD_CODE, 'EPypes/epypes/protobuf'))

import zmq
import uuid

from epypes.cli import parse_pubsub_args
from epypes.protobuf.event_pb2 import Event
from epypes.protobuf.justbytes_pb2 import JustBytes


def create_zmq_sockets(pub_address, sub_address):

    context = zmq.Context()

    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind(pub_address)

    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect(sub_address)
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    return pub_socket, sub_socket


def announce_request(pub_socket):

    request_id = str(uuid.uuid4())[:8]

    req_event = Event()
    req_event.type = 'VisionRequest'
    req_event.id = request_id

    pub_socket.send(req_event.SerializeToString())


def get_response(sub_socket):

    response_data = sub_socket.recv()

    vision_response = JustBytes()
    vision_response.ParseFromString(response_data)

    return vision_response


if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(
        default_pub_address='ipc:///tmp/vision-request',
        default_sub_address='ipc:///tmp/vision-response'
    )

    pub_socket, sub_socket = create_zmq_sockets(pub_address, sub_address)

    def req():
        announce_request(pub_socket)
        response = get_response(sub_socket)
        return response
