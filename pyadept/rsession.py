import time
from pytcp.tcputil import create_client_socket, socket_send_bytes, read_complete_messages
from pyadept.commands import DELIMITER

LOG_TEMPLATE_STR = '[{:.3f}]\t{:s}\t{:s}'

def log_conn(t, dest_pair):
    host, port = dest_pair
    print(LOG_TEMPLATE_STR.format(t, 'conn', '{:s}:{:d}'.format(host, port)))


def log_send(t, msg):
    print(LOG_TEMPLATE_STR.format(t, 'send', msg))


def log_recv(t, msg):
    print(LOG_TEMPLATE_STR.format(t, 'recv', msg.strip()))


def log_error(t, err):
    print(LOG_TEMPLATE_STR.format(t, 'error', err))


class RobotSession(object):

    def __init__(self):

        self._t0 = time.time()

        try:
            t = time.time() - self._t0
            self._socket = create_client_socket()
        except Exception as e:
            log_error(t, str(e))

    def connect(self, host, port):

        dest_pair = (host, port)

        try:
            t = time.time() - self._t0
            self._socket.connect(dest_pair)
        except Exception as e:
            log_error(t, str(e))

        log_conn(t, dest_pair)

    def cmdsend(self, *commands):

        for cmd in commands:
            msg = cmd.get_bytes()

            try:
                t = time.time() - self._t0
                socket_send_bytes(self._socket, msg)
            except Exception as e:
                log_error(t, str(e))

            log_send(t, msg)

    def receive(self):

        resp_messages = read_complete_messages(self._socket, DELIMITER, buffer_size=2048)
        return resp_messages







