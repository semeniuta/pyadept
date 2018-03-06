import socket

NEWLINE_CHAR = b'\n'[0]

def create_server_socket(host, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    socket_pair = (host, port)
    s.bind(socket_pair)

    return s


def start_server(srv_socket, handler, max_conn=10):

    srv_socket.listen(max_conn)

    while True:
        conn, addr = srv_socket.accept()
        handler(conn, addr)


def create_client_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


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


def read_until_char(socket, terminate_char=NEWLINE_CHAR, buffer_size=2048):

    data = b''
    do_read = True

    while do_read:

        rd = socket.recv(buffer_size)
        data += rd

        if rd[-1] == terminate_char:
            do_read = False

    return data
