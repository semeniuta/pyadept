import zmq
import zmq.asyncio
zmq.asyncio.install()


def create_async_subscriber(server_address, sub_prefix=b''):
    """
    Create asynchronous ZeroMQ subscriber
    """

    ctx = zmq.asyncio.Context()

    sub_sock = ctx.socket(zmq.SUB)
    sub_sock.connect(server_address)
    sub_sock.subscribe(sub_prefix)

    return sub_sock


def create_async_publisher(bind_address):
    """
    Create asynchronous ZeroMQ publisher
    """

    ctx = zmq.asyncio.Context()

    pub_sock = ctx.socket(zmq.PUB)
    pub_sock.bind(bind_address)

    return pub_sock


async def zmq_sub_listener(server_address, stop_event, on_recv=None, sub_prefix=b'', poll_timeout=0.001):
    """
    Continuous asynchronous ZeroMQ subsriber. When an event is received,
    `on_recv` callback is invoked. To stop the subsriber, `stop_event`
    should be set from an other coroutine
    """

    sub_sock = create_async_subscriber(server_address, sub_prefix)

    poller = zmq.asyncio.Poller()
    poller.register(sub_sock)

    while True:

        p_socks = dict(await poller.poll(timeout=poll_timeout))

        if sub_sock in p_socks:
            msg = await sub_sock.recv()

            if on_recv is not None:
                on_recv(msg)

        if stop_event.is_set():
            print('Stopping the subscriber')
            break

    sub_sock.close()


class PubSubPair(object):
    """
    PubSubPair encapsulates a pair of asynchronous
    ZeroMQ publisher and subscriber.

    The `communicate` method is a coroutine. When awaited, it
    publishes the supplied object (at `pub_address`) and polls
    the result of the computation of interest from `sub_address`
    """

    def __init__(self, pub_address, sub_address, poll_timeout=0.001):

        self._pub_sock = create_async_publisher(pub_address)
        self._sub_sock = create_async_subscriber(sub_address)

        self._poller = zmq.asyncio.Poller()
        self._poller.register(self._sub_sock)
        self._poll_timeout = poll_timeout

    async def communicate(self, obj):

        await self._pub_sock.send(obj)

        while True:

            p_socks = dict(await self._poller.poll(timeout=self._poll_timeout))

            if self._sub_sock in p_socks:
                response = await self._sub_sock.recv()
                break

        return response
