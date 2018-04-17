import asyncio
import functools

from pyadept.bytesproc import split_data
from pyadept.asioutil import GenericProtocol


DELIMITER = b'\r\n'


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
    server_coro = loop.create_server(server_factory, '', 1234)
    server = loop.run_until_complete(server_coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stopping the server due to keyboard interrupt')
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
