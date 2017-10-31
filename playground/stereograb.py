
class StereoImageGrabber:

    def __init__(self, grabbers, q):
        pass

if __name__ == '__main__':

    import time
    from datetime import datetime
    import random
    import multiprocessing as mp

    def eventloop(req_q, resp_q):
        while True:
            if not req_q.empty():
                msg = req_q.get()
                if msg == 'stop':
                    break
                elif msg == 'grab':
                    res = dummy_f()
                    resp_q.put(res)
                else:
                    print msg

    def dummy_f():
        t0 = datetime.now()
        time.sleep(1 + random.random())
        t1 = datetime.now()
        span = t1 - t0
        print t0, span
        return t0, span

    q1 = mp.Queue()
    q2 = mp.Queue()
    qres = mp.Queue()

    def grab():
        q1.put('grab')
        q2.put('grab')

    def stop():
        q1.put('stop')
        q2.put('stop')

    p1 = mp.Process(target=eventloop, args=(q1,qres))
    p2 = mp.Process(target=eventloop, args=(q2,qres))

    p1.start()
    p2.start()

    #p1.join()
    #p2.join()