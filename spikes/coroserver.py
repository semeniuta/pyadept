import asyncio
import functools

from pyadept.strutil import split_data
from pyadept.asioutil import GenericProtocol, create_server


DELIMITER = b'\r\n'


def create_tick(loop):

    future_server_closed = loop.create_future()

    async def tick(interval, t0):

        while not future_server_closed.done():
            await asyncio.sleep(interval)
            now = loop.time()
            print('t={:.3f}'.format(now - t0))

    return future_server_closed, tick


class EchoServerProtocol(GenericProtocol):

    def connection_made(self, transport):

        self._transport = transport

        endpoint = self._transport.get_extra_info('peername')
        self._log('Connected with: {}'.format(endpoint))

    def data_received(self, data):

        self._log('Received: {}'.format(data))

        all_data = self._merge_data_with_rest(data)
        commands, rest = split_data(all_data, DELIMITER)

        if commands is not None:
            for command in commands:

                command_id = command.split(b':')[0]
                msg_back = command_id + b':done' + DELIMITER

                self._transport.write(msg_back)
                self._log('Sent back: {}'.format(msg_back))

        if rest is not None:
            self._update_rest(rest)


    def connection_lost(self, error):
        self._log('Connection lost: {}'.format(str(error)))


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    server_factory = functools.partial(EchoServerProtocol, loop=loop)
    server = create_server(server_factory, loop, '', 1234)

    future_server_closed, tick = create_tick(loop)
    future_tick = asyncio.ensure_future(
        tick(interval=0.1, t0=loop.time())
    )

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stopping the server due to keyboard interrupt')
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        future_server_closed.set_result(True)
        loop.run_until_complete(future_tick)
        loop.close()
