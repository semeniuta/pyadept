from __future__ import print_function

import argparse
import socket
import sys


def send_msg(host, port, msg):

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print('Failed to create a socket')
        sys.exit()

    try:
        dest_pair = (host, port)
        s.connect(dest_pair)
    except:
        print('Failed to connect to {:s}:{:d}'.format(host, port))
        sys.exit()

    try:
        data = msg.encode()
        s.sendall(data)
        print('Message sent to {:s}:{:d}: {:s}'.format(host, port. data))
    except:
        print('Failed to send data')
        sys.exit()

    s.close()

if __name__ == '__main__':


    if len(sys.argv) != 3:

        print("Not correct number of arguments supplied")

    else:

        host, port = sys.argv[1].split(':')
        message = sys.argv[2]

        send_msg(host, int(port), message)
