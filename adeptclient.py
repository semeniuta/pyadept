from __future__ import print_function

import socket
import sys
import time

LOG_TEMPLATE_STR = '[{:.3f}]\t{:s}\t{:s}'

def log_conn(t, dest_pair):
    print(LOG_TEMPLATE_STR.format(t, 'conn', '{:s}:{:d}'.format(dest_pair)))

def log_send(t, msg):
    print(LOG_TEMPLATE_STR.format(t, 'send', msg))

def log_recv(t, msg):
    print(LOG_TEMPLATE_STR.format(t, 'recv', resp.strip()))

def log_error(t, err):
    print(LOG_TEMPLATE_STR.format(t, 'error', err))


class AdeptClient:

    def __init__(self):

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print('Failed to create client socket')
            sys.exit()


    def connect_to_server(self, host, port):

        try:
            dest_pair = (host, port)
            self.s.connect(dest_pair)
            self.t_conn = time.time()
            log_connected(0, dest_pair)
        except:
            print('Failed to connect to')
            sys.exit()


    def send_msg(self, msg):

        ok = True

        try:
            self.s.sendall(msg)
            t_send = time.time() - self.t_conn
            log_send(t_send, msg)

        except:
            log_error(time.time(), 'Failed to send data')
            ok = False


        if ok:

            try:
                resp = self.s.recv(2048)
                t_recv = time.time() - self.t_conn
                log_recv(t_recv, resp)
            except:
                log_error(time.time(), 'Failed to receive data')


    def close(self):
        self.s.close()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
