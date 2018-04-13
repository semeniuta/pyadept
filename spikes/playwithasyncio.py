import asyncio
import time

from pyadept import rsession


DELIMITER = b'\r\n'

# how to use it with Protocol?
async def processing_simulator():
    await asyncio.sleep(0.250)


class EchoServerProtocol(asyncio.Protocol):

    def connection_made(self, transport):

        self._t0 = time.time()
        self._transport = transport

        endpoint = self._transport.get_extra_info('peername')

        #rsession.log_conn(self._current_time(), endpoint)
        print(self._current_time(), 'Connected with', endpoint)

    def data_received(self, data):

        #rsession.log_recv(self._current_time(), data)
        print(self._current_time(), 'Received', data)

        messages = data.split(DELIMITER)
        #yield from processing_simulator()

        self._transport.write(data)

    def connection_lost(self, error):

        #rsession.log_error(self._current_time(), error)
        print(self._current_time(), 'Connection lost:', str(error))

    def _current_time(self):
        return '{:.3f}'.format(time.time() - self._t0)


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    server_coro = loop.create_server(EchoServerProtocol, '', 1234)
    server = loop.run_until_complete(server_coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stopping the server')
        server_coro.close()
        loop.run_until_complete(server_coro.wait_closed())
        loop.close()
