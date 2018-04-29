"""
Playing with asynchronous ZeroMQ
"""

import asyncio

from pyadept import asioutil
from pyadept import asynczmq


async def long_operation(duration, stop_event):
    await asyncio.sleep(duration)
    stop_event.set()


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    t0 = loop.time()

    stop_ticking, tick = asioutil.create_periodic_task(
        loop,
        lambda: print('t={:.3f}'.format(loop.time() - t0))
    )
    future_tick = asyncio.ensure_future(tick(interval=0.25))

    task_long_op = asyncio.ensure_future(
        long_operation(duration=10, stop_event=stop_ticking),
        loop=loop
    )

    task_subscriber = asynczmq.zmq_subscribe(
        'tcp://127.0.0.1:1235',
        stop_event=stop_ticking
    )

    loop.run_until_complete(
        asyncio.gather(future_tick, task_long_op, task_subscriber)
    )
