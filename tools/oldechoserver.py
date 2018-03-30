from __future__ import print_function

import argparse
import socket
import sys

arg_parser = argparse.ArgumentParser(description='Launch echo server.')
arg_parser.add_argument('--host', default='0.0.0.0')
arg_parser.add_argument('--port', default=1234, type=int)

args = arg_parser.parse_args()

print(args)

def launch_server(host, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Server socket created')

    socket_pair = (host, port)
    s.bind(socket_pair)
    print('Binding done @ {:s}:{:d}'.format(*s.getsockname()))

    max_conn = 10
    s.listen(max_conn)
    print('Socket listening (max {:d} connections)'.format(max_conn))

    while True:

        conn, addr = s.accept()
        print('Connected with', addr)

        rd = conn.recv(1024)

        print("-> ", rd)

        conn.close()


if __name__ == '__main__':

    launch_server(args.host, args.port)
