import socket
import time

def create_server_socket(host, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    socket_pair = (host, port)
    s.bind(socket_pair)

    return s


def start_server(srv_socket, handler, max_conn=10):

    srv_socket.listen(max_conn)

    while True:

        try:
            conn, addr = srv_socket.accept()
            handler(conn, addr)
        except KeyboardInterrupt:
            print('\nStopping the server due to keyborard interrupt')
            break


def create_client_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def create_connected_client_socket(remote_host, remote_port):

    s = create_client_socket()

    dest_pair = (remote_host, remote_port)
    s.connect(dest_pair)

    return s


def socket_send_string(socket, msg):

    data = msg.encode()
    socket.sendall(data)


def socket_send_bytes(socket, buff):
    socket.sendall(buff)


def read_messages(socket, delimiter=b'\n', buffer_size=2048):
    '''
    Reads data from socket, where sequences of bytes separated by the delimiter
    constitute separate messages. Returns a tuple (messages, rest), where
    messages correspond to the a list of messages and rest corresponds to
    the remaining byte  string. Possible return compinations are the following:

    (messages, rest) -- one or more complete messages are received + the rest of bytes
    (messages, None) -- a complete set of messages is received
    (None, rest) -- a single sequence of bytes is received (without delimiter)
    (None, None) -- peer has closed its socket

    :param socket: a TCP socket object
    :param delimiter: a bytes object used as a delimiter between messages
    :param buffer_size: size of the buffer used for reading from the socket
    :return: a tuple of messages and rest of bytes
    '''

    data = socket.recv(buffer_size)

    if not data:
        return None, None

    messages = data.split(delimiter)
    n = len(messages)

    if n == 1:
        return None, data

    else:

        if data.endswith(delimiter):
            return messages[:-1], None
        else:
            return messages[:-1], messages[-1]


def read_complete_messages(socket, delimiter=b'\n', buffer_size=2048):
    '''
    Reads data from socket, where sequences of bytes separated by the delimiter
    constitute separate messages. Continue reading from the socket until a set
    of complete messages is obtained (the correspinding list of bytes object is returned)
    or the peer has closed its socket (the function returns None)

    :param socket: a TCP socket object
    :param delimiter: a bytes object used as a delimiter between messages
    :param buffer_size: size of the buffer used for reading from the socket
    :return: a list of messages or None
    '''

    def perform_read(data=b''):

        messages, rest = read_messages(socket, delimiter, buffer_size)

        if messages is None and rest is None:
            return None

        if messages is None:
            return perform_read(rest)

        if rest is None:
            return messages

        return messages + perform_read(rest)

    return perform_read()


def read_until_seq(socket, seq=b'\n', buffer_size=2048, data=b''):

    chunk = socket.recv(buffer_size)

    if not chunk: # peer has closed its socket
        return None

    updated_data = data + chunk

    components = updated_data.split(seq)
    n = len(components)

    if n == 1:
        return read_until_seq(socket, seq, buffer_size, updated_data)

    else:

        if updated_data.endswith(seq):
            return components[:-1]
        else:
            return components[:-1] + read_until_seq(socket, seq, buffer_size, components[-1])
