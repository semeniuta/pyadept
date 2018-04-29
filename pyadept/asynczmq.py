import zmq
import zmq.asyncio
zmq.asyncio.install()


async def zmq_subscribe(server_address, stop_event, sub_prefix=b''):

    ctx = zmq.asyncio.Context()

    sub_sock = ctx.socket(zmq.SUB)
    sub_sock.connect(server_address)
    sub_sock.setsockopt(zmq.SUBSCRIBE, sub_prefix)

    poller = zmq.asyncio.Poller()
    poller.register(sub_sock)

    while True:

        p_socks = dict(await poller.poll(timeout=0.001))

        if sub_sock in p_socks:
            msg = await sub_sock.recv()
            print('ZMQ received', msg) #temp

        if stop_event.is_set():
            print('Stopping the subscriber')
            break

    sub_sock.close()

