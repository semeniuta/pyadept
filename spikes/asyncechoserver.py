from pyadept.tcputil import create_server_socket, start_server, read_complete_messages
from pyadept.qhandler import QHandler

STOP_REQUEST = b'stop'
DELIMITER = b'\r\n'


def create_acceptor(cmd_q, session_on_q):

    def on_accept(conn, addr):

        print( 'Session started (connected with {})'.format(addr) )

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
                token = (message, conn)
                cmd_q.put(token)

            for i in range(len(data)):
                session_on = session_on_q.get()

        print('Session finished')

    return on_accept


def echo(token):

    cmd, conn = token
    print("-> ", cmd)

    session_on = True
    if cmd == STOP_REQUEST:
        print('Closing connection (due to stop request)')
        conn.close()
        session_on = False

    return session_on


if __name__ == '__main__':

    cmd_handler = QHandler(handle_func=echo)
    cmd_handler.start()

    srv_socket = create_server_socket('0.0.0.0', 1234)

    on_accept = create_acceptor(cmd_q=cmd_handler.q_in, session_on_q=cmd_handler.q_out)
    on_exit = lambda: cmd_handler.stop()

    start_server(srv_socket, on_accept, on_exit)
