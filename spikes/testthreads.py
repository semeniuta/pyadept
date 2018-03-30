import threading
import queue

if __name__ == '__main__':

    q = queue.Queue()

    def infinite_loop():
        while True:
            obj = q.get()
            print(obj)

    t = threading.Thread(target=infinite_loop)
    t.start()

    for i in range(10):
        q.put(2**i)
