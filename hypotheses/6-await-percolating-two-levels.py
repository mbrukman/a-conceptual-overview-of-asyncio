"""
A yield can and will be percolated through multiple awaits. 
"""

import asyncio

class YieldToEventLoop:
    def __await__(self):
        import ipdb; ipdb.set_trace()
        yield

async def coro():
    await YieldToEventLoop()

async def main():
    await coro()


asyncio.run(main())
