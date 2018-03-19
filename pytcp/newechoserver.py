from tcputil import create_server_socket, start_server, read_until_seq, socket_send_bytes

STOP_REQUEST = b'stop'

def handle_command(conn, cmd):

    session_on = True

    print("-> ", cmd)
    socket_send_bytes(conn, cmd)

    if cmd == STOP_REQUEST:
        print('Closing connection')
        conn.close()
        session_on = False

    return session_on


def echo_handler(conn, addr):

    session_on = True
    while session_on:

        try:
            data = read_until_seq(conn, seq=b'\r\n', buffer_size=128)
        except ConnectionResetError as e:
            print('Closing connection')
            conn.close()
            break

        print('Data: ', data)
        for el in data:
            session_on = handle_command(conn, el)

    print('Session finished')


if __name__ == '__main__':

    srv_socket = create_server_socket('0.0.0.0', 1234)
    start_server(srv_socket, echo_handler)
