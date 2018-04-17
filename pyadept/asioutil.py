import asyncio


class GenericProtocol(asyncio.Protocol):

    def __init__(self, loop):
        self._loop = loop
        self._t0 = self._loop.time()
        self._rest = b''

    def _current_time(self):
        return self._loop.time() - self._t0

    def _merge_data_with_rest(self, data):

        all_data = self._rest + data
        self._rest = b''
        return all_data

    def _update_rest(self, data):
        self._rest += data

    def _log(self, text):
        t = self._current_time()
        print('[{:.6f}] {}'.format(t, text))
