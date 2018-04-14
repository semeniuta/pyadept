import asyncio


async def tick(loop, interval, future, t0):

    while not future.done():
        await asyncio.sleep(interval)
        now = loop.time()
        print('t={:.3f}'.format(now - t0))


async def long_operation(duration):
    await asyncio.sleep(duration)


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    t0 = loop.time()

    task_long_op = asyncio.ensure_future(
        long_operation(duration=5),
        loop=loop
    )

    coro_tick = tick(loop, interval=0.5, future=task_long_op, t0=t0)

    loop.run_until_complete(
        asyncio.gather(coro_tick, task_long_op)
    )
