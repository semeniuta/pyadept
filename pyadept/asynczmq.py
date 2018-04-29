import zmq
import zmq.asyncio
zmq.asyncio.install()


def create_async_subscriber(server_address, sub_prefix=b''):

    ctx = zmq.asyncio.Context()

    sub_sock = ctx.socket(zmq.SUB)
    sub_sock.connect(server_address)
    sub_sock.subscribe(sub_prefix)

    return sub_sock


async def zmq_sub_listener(server_address, stop_event, sub_prefix=b'', poll_timeout=0.001):

    sub_sock = create_async_subscriber(server_address, sub_prefix)

    poller = zmq.asyncio.Poller()
    poller.register(sub_sock)

    while True:

        p_socks = dict(await poller.poll(timeout=poll_timeout))

        if sub_sock in p_socks:
            msg = await sub_sock.recv()
            print('ZMQ received', msg) #temp

        if stop_event.is_set():
            print('Stopping the subscriber')
            break

    sub_sock.close()

