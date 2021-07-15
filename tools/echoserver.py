import sys
import os
import argparse
sys.path.append(os.getcwd())

from pyadept.tcputil import create_server_socket, start_server, read_complete_messages, socket_send_bytes
from pyadept.rcommands import DELIMITER

STOP_REQUEST = b'stop'

def handle_command(conn, cmd):

    session_on = True

    print("-> ", cmd)
    socket_send_bytes(conn, cmd + DELIMITER)

    if cmd == STOP_REQUEST:
        print('Closing connection (due to stop request)')
        conn.close()
        session_on = False

    return session_on


def echo_handler(conn, addr):

    client_host, client_port = addr

    print('Session started (connected with {}:{:d})'.format(client_host, client_port))
    session_on = True
    while session_on:

        try:
            data = read_complete_messages(conn, delimiter=DELIMITER, buffer_size=128)
        except ConnectionResetError as e:
            print('Closing connection (due to connection being reset by peer)')
            conn.close()
            break

        if data is None:
            print("Closing connection (due to peer's closing its socket)")
            conn.close()
            break

        print('Read data: ', data)
        for el in data:
            session_on = handle_command(conn, el)

    print('Session finished')


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description='Start a TCP echo server')
    arg_parser.add_argument('--host', default='0.0.0.0')
    arg_parser.add_argument('--port', default=1234)
    args = arg_parser.parse_args()

    print('Starting TCP echo server at {}:{:d}'.format(args.host, args.port))

    srv_socket = create_server_socket(args.host, args.port)
    start_server(srv_socket, echo_handler)
