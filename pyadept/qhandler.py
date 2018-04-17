from threading import Thread
from queue import Queue

from pyadept.strutil import generate_id_str


class QHandler(Thread):

    def __init__(self, handle_func, q_in=None, q_out=None):

        self._hander = handle_func

        self._q_in = Queue() if q_in is None else q_in
        self._q_out = Queue() if q_out is None else q_out

        self._stop_const = generate_id_str()

        super(QHandler, self).__init__(target=self._loop)

    def stop(self):
        self._q_in.put( self._stop_const )

    @property
    def q_in(self):
        return self._q_in

    @property
    def q_out(self):
        return self._q_out

    def _loop(self):

        while True:

            request = self._q_in.get()

            if request == self._stop_const:
                break

            response = self._hander(request)

            self._q_out.put(response)


def create_qhandler_chain(*funcs):

    qhandlers = []

    for i, f in enumerate(funcs):

        if i == 0:
            h = QHandler(f)
            qhandlers.append( h )
            continue

        prev_h = qhandlers[i - 1]
        h = QHandler(f, q_in=prev_h.q_out)
        qhandlers.append(h)

    return qhandlers





