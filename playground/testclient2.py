from __future__ import print_function

import socket
import sys

host = '172.16.120.134'
port = 1234

message = "Hello"

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Client socket created')
except:
    print('Failed to create a socket')
    sys.exit()

try:
    dest_pair = (host, port)
    s.connect(dest_pair)
    print('Socket connected to %s:%d' % dest_pair)
except:
    print('Failed to connect')
    sys.exit()


try:
    s.sendall(message)
    print('Message sent')
except:
    print('Failed to send data')
    sys.exit()


s.close()
