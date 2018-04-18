from pyadept.strutil import split_data, generate_id_bytes
from pyadept.asioutil import GenericProtocol

from pyadept.rcommands import DELIMITER


def interpret_robot_response(msg):

    msg_id, status = msg.split(b':')
    return msg_id, status


class MCNClientProtocol(GenericProtocol):
    """
    Master Control Node TCP Client Protocol
    """

    def __init__(self, loop, cmd_iterator, future):

        super(MCNClientProtocol, self).__init__(loop)
        self._cmd_iterator = cmd_iterator
        self._future = future

    def connection_made(self, transport):

        self._transport = transport
        self._ids = set()

        endpoint = self._transport.get_extra_info('peername')
        self._log('Connected with: {}'.format(endpoint))

        for command in self._cmd_iterator:

            for cmd_bytes in command.get_bytes():

                cmd_id = generate_id_bytes()
                cmd_data = cmd_id + cmd_bytes

                self._transport.write(cmd_data)
                self._ids.add(cmd_data)

                self._log('Sent: {}'.format(cmd_data))

    def data_received(self, data):

        self._log('Received: {}'.format(data))

        all_data = self._merge_data_with_rest(data)
        messages, rest = split_data(all_data, DELIMITER)

        if messages is not None:
            for msg in messages:
                msg_id, status = interpret_robot_response(msg)
                self._ids.remove(msg_id)
                if len(self._ids) == 0:
                    self._future.set_result(True)
                    # close connection ?

        if rest is not None:
            self._update_rest(rest)

    def connection_lost(self, error):
        self._log('Connection lost: {}'.format(str(error)))
        self._future.set_result(True)
