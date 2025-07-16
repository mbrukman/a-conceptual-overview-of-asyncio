"""
coroutine.__await__(), task.__await__() and future.__await__() are all no-ops. 
The task and future will still be invoked eventually since they are tied to the
event-loop, but the coroutine will not.
"""

import asyncio

async def print1():
    print("Hi! I am print1().")

async def print2():
    print("Hi! I am print2().")

async def print3():
    print("Hi! I am print3().")

async def print4():
    print("Hi! I am print4().")

async def main():
    
    # ------------
    coro1 = print1()
    await coro1
    
    # Will not invoke the coroutine. Will raise a warning
    # regarding an unexecuted coroutine.
    # coro2 = print2()
    # coro2.__await__()

    # ------------

    # Either note the order of prints or follow along with 
    # the trace to see that invoking with .__await__()
    # is a no-op.

    task3 = asyncio.Task(print3())
    # import ipdb; ipdb.set_trace()
    await task3
    print("This print comes after: task3.__await__().")

    task4 = asyncio.Task(print4())
    # import ipdb; ipdb.set_trace()
    task4.__await__()
    print("This print comes after: task4.__await__().")

    # ------------

    # if .__await__() did invoke the __await__() method, this 
    # program should hang, but it doesn't.
    future = asyncio.Future()
    future.__await__()


asyncio.run(main())