import socket
import sys
import time

class AdeptClient:

    def __init__(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print 'Client socket created'
        except:
            print 'Failed to create a socket'
            sys.exit()    
        
    def connect_to_server(self, host, port):
        try:
            dest_pair = (host, port)
            self.s.connect(dest_pair)
            self.t_conn = time.time()
            print '[0]\tconn\t%s:%d' % dest_pair
        except:
            print 'Failed to connect'
            sys.exit()
        
    def send_msg(self, msg):
        try:
            self.s.sendall(msg)
            t_send = time.time() - self.t_conn
            print '[%.3f]\tsend\t%s' % (t_send, msg)
            
        except:
            print 'Failed to send data'
            sys.exit()
        
        try: 
            resp = self.s.recv(2048)
            t_recv = time.time() - self.t_conn
            print '[%.3f]\trecv\t%s' % (t_recv, resp.strip())
        except:
            print 'Failed to receive data'
            sys.exit()
        
    def close(self):    
        self.s.close()
        
    def __destr__(self):
        self.close()
