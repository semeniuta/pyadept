from pytcp.tcputil import create_server_socket, start_server, read_complete_messages, socket_send_bytes
from pytcp.qhandler import QHandler, create_qhandler_chain

STOP_REQUEST = b'stop'
DELIMITER = b'\r\n'

def echo(conn, cmd):

    session_on = True

    print("-> ", cmd)
    socket_send_bytes(conn, cmd + DELIMITER)

    if cmd == STOP_REQUEST:
        print('Closing connection (due to stop request)')
        conn.close()
        session_on = False

    return session_on


def create_connection_handler(handler_thread):

    def on_accept(conn, addr):

        print('Session started')
        session_on = True
        while session_on:

            try:
                print('Read start')
                data = read_complete_messages(conn, DELIMITER, buffer_size=128)
            except ConnectionResetError as e:
                print('Closing connection (due to connection reset by peer)')
                conn.close()
                break

            if data is None:
                print("Closing connection (due to peer's closing its socket)")
                conn.close()
                break

            for message in data:
                handler_thread.q_in.put(message)

        print('Session finished')


if __name__ == '__main__':

    handler_thread = QHandler(handle_func=echo)

    srv_socket = create_server_socket('0.0.0.0', 1234)
    start_server(srv_socket, on_accept)
