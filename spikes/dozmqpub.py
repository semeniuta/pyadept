import zmq
import time

if __name__ == '__main__':

    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUB)
    sock.bind('tcp://127.0.0.1:1235')

    for i in range(5):
        time.sleep(1)
        data = 'zmq-event-{:d}'.format(i).encode()
        sock.send(data)
        print('Sent', data)



