import time
from pytcp.tcputil import create_connected_client_socket, socket_send_bytes


socket = create_connected_client_socket('127.0.0.1', 1234)

socket_send_bytes(socket, b'hello\r\n')
time.sleep(0.25)

socket_send_bytes(socket, b'hello again\r\n')
time.sleep(0.25)

socket_send_bytes(socket, b'one\r\ntwo\r\nthree\r\nfour\r\nfive\r\n')
time.sleep(0.25)

#socket_send_bytes(socket, b'stop\r\n')
