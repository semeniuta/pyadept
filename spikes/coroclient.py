import asyncio
import functools
import uuid

from pyadept.bytesproc import split_data
from pyadept.asioutil import GenericProtocol


DELIMITER = b'\r\n'


def generate_id():
    return str(uuid.uuid4())[:8].encode()


def create_command(request_id, msg):
    return request_id + b':' + msg + DELIMITER


class EchoClientProtocol(GenericProtocol):

    def __init__(self, loop, messages, future):

        super(EchoClientProtocol, self).__init__(loop)
        self._messages = messages
        self._future = future

    def connection_made(self, transport):

        self._transport = transport
        self._ids = set()

        endpoint = self._transport.get_extra_info('peername')
        self._log('Connected with: {}'.format(endpoint))

        for msg in self._messages:
            for command in msg.split(DELIMITER):

                command_id = generate_id()
                command_data = create_command(command_id, command)

                self._transport.write(command_data)
                self._ids.add(command_id)

                self._log('Sent: {}'.format(command_data))

    def data_received(self, data):

        self._log('Received: {}'.format(data))

        all_data = self._merge_data_with_rest(data)
        messages, rest = split_data(all_data, DELIMITER)

        if messages is not None:
            for msg in messages:
                msg_id = msg.split(b':')[0]
                self._ids.remove(msg_id)
                if len(self._ids) == 0:
                    self._future.set_result(True)

        if rest is not None:
            self._update_rest(rest)

    def connection_lost(self, error):
        self._log('Connection lost: {}'.format(str(error)))
        self._future.set_result(True)


if __name__ == '__main__':

    MESSAGES = [
        b'hello\r\n',
        b'hello again\r\n',
        b'one\r\ntwo\r\nthree\r\nfour\r\nfive\r\n'
    ]

    loop = asyncio.get_event_loop()

    client_completed = loop.create_future()
    client_factory = functools.partial(
        EchoClientProtocol,
        loop=loop,
        messages=MESSAGES,
        future=client_completed
    )

    client_coro = loop.create_connection(client_factory, '127.0.0.1', 1234)

    try:
        loop.run_until_complete(client_coro)
        loop.run_until_complete(client_completed)
    finally:
        print('Done sending. Closing event loop')
        loop.close()
