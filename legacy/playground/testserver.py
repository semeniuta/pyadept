import socket
import sys

host = '172.16.0.125'
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Server socket created'

socket_pair = (host, port)
s.bind(socket_pair)
print 'Binding complete on %s:%d' % s.getsockname()

max_conn = 10
s.listen(max_conn)
print 'Socket listening (max %d connections)' % max_conn

while True:
    conn, addr = s.accept()
    print 'Connected with', addr
    print conn.getsockname(), conn.getpeername()
    
    print 'Processing...'    
    
    rd = conn.recv(1024)            
    
    print "Received: ", rd
    
    
    conn.close()
