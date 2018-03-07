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


def read_until_seq(socket, seq=NEWLINE_CHAR, buffer_size=2048, data=b''):

    chunk = socket.recv(buffer_size)

    components = chunk.split(seq)
    n = len(components)

    if n == 1:
        data += chunk
        return read_until_seq(socket, seq, buffer_size, data)

    elif n == 2:
        return data + chunk

    else:
        return [data + components[0]] + components[1:-1]
