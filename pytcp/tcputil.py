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
