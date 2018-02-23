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
        print('Connected to {}:{:d}'.format(host, port))
    except:
        print('Failed to connect to {}:{:d}'.format(host, port))
        sys.exit()

    try:
        data = msg.encode()
        s.sendall(data)
        print('Message sent to {}:{}: {}'.format(host, port, data))
    except Exception  as e:
        print('Failed to send data')
        print(e)
        sys.exit()

    s.close()

if __name__ == '__main__':


    if len(sys.argv) != 3:

        print("Not correct number of arguments supplied")

    else:

        host, port = sys.argv[1].split(':')
        message = sys.argv[2]

        send_msg(host, int(port), message)
