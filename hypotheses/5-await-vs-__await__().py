"""
`coroutine.__await__()` does not mimic `await coroutine`.
`task.__await__()` and `future.__await__()` do appear to mimic `await task`
and `await future`
"""

import asyncio

async def printer():
    print("Hi! I am printer().")

async def main():
    
    coro = printer()
    await coro
    
    # Will not invoke the coroutine. Will raise a warning
    # regarding an unexecuted coroutine.
    # coro = printer()
    # coro.__await__()

    task = asyncio.Task(printer())
    await task

    task = asyncio.Task(printer())
    task.__await__()

    future = asyncio.Future()
    future.__await__()


asyncio.run(main())