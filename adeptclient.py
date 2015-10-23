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
            print 'Socket connected to %s:%d' % dest_pair
        except:
            print 'Failed to connect'
            sys.exit()
        
    def send_msg(self, msg):
        try:
            self.s.sendall(msg)
            print 'Message sent'
            time.sleep(0.1)
        except:
            print 'Failed to send data'
            sys.exit()
        
    def close(self):    
        self.s.close()
