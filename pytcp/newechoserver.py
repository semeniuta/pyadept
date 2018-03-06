from tcputil import create_server_socket, start_server, read_until_char, socket_send_bytes

STOP_REQUEST = b'stop\r\n'

def echo_handler(conn, addr):

    session_on = True
    while session_on:

        data = read_until_char(conn, buffer_size=128)
        print("-> ", data)
        socket_send_bytes(conn, data)

        if data == STOP_REQUEST:
            conn.close()
            session_on = False

srv_socket = create_server_socket('0.0.0.0', 1234)
start_server(srv_socket, echo_handler)
