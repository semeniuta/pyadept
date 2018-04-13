from pytcp.tcputil import create_server_socket, start_server, read_complete_messages, socket_send_bytes

STOP_REQUEST = b'stop'
DELIMITER = b'\r\n'

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

    print('Session started')
    session_on = True
    while session_on:

        try:
            print('Read start')
            data = read_complete_messages(conn, delimiter=DELIMITER, buffer_size=128)
        except ConnectionResetError as e:
            print('Closing connection (due to connection reset by peer)')
            conn.close()
            break

        if data is None:
            print("Closing connection (due to peer's closing its socket)")
            conn.close()
            break

        print('Data: ', data)
        for el in data:
            session_on = handle_command(conn, el)

    print('Session finished')


if __name__ == '__main__':

    srv_socket = create_server_socket('0.0.0.0', 1234)
    start_server(srv_socket, echo_handler)
