import asyncio
import time


DELIMITER = b'\r\n'


class EchoServerProtocol(asyncio.Protocol):

    def __init__(self):
        self._rest = b''

    def connection_made(self, transport):

        self._t0 = time.time()
        self._transport = transport

        endpoint = self._transport.get_extra_info('peername')
        print(self._current_time(), 'Connected with', endpoint)

    def data_received(self, data):

        print(self._current_time(), 'Received', data)

        all_data = self._merge_data_with_rest(data)
        messages = all_data.split(DELIMITER)

        for m in messages:
            self._transport.write(data)

    def connection_lost(self, error):
        print(self._current_time(), 'Connection lost:', str(error))

    def _current_time(self):
        return '{:.3f}'.format(time.time() - self._t0)

    def _merge_data_with_rest(self, data):

        all_data = self._rest  + data
        self._rest = b''
        return all_data


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    server_coro = loop.create_server(EchoServerProtocol, '', 1234)
    server = loop.run_until_complete(server_coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stopping the server due to keyboard interrupt')
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
