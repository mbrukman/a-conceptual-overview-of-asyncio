# asyncio was added to the standard library in Python3.5.

# asyncio's big selling-point (or reason for existing) is the ability 
# to create, run and control coroutines. 
# A coroutine is a program or component that can be paused & resumed, 
# unlike a subroutine which runs until completion. A subroutine can 
# of course be interrupted, but it must then be re-started; it 
# cannot be resumed.

# In practice, coroutines are implemented or managed by essentially
# breaking them up into many smaller subroutines. And, the broader coroutine
# can be paused/resumed at any of the break-points between each of the smaller
# subroutines. It's a bit like the derivative from calculus where you can 
# approximate a continuous form with many, tiny discrete slices.

import asyncio
import time

# In seconds.
TIME_TO_SOLVE = 0.2

def solve(x) -> int:
    time.sleep(TIME_TO_SOLVE)
    return x * 3

# Raises a ValueError that complains asyncio.run did not receive a coroutine
# and instead received a function.
# asyncio.run(main=solve)

# An asynchronous (or async) or coroutine function is defined like this.
# Note the function name does not need the "async_" prefix, that's for 
# clarity later on when we reference it.
async def async_solve(x) -> int:
    # time.sleep(TIME_TO_SOLVE)
    await asyncio.sleep(TIME_TO_SOLVE)
    return x * 3

# Both solve and async_solve are of type 'function'. 
print(f"type(solve): {type(solve)}.")
print(f"type(async_solve): {type(async_solve)}.")

# Invoking the async_solve function doesn't actually perform the steps
# detailed in the function body. Instead, the invocation returns a 
# coroutine object. That coroutine object represents the function-to-be-run.
solve_coroutine = async_solve(x=5)

# When the coroutine is invoked (not the function which produced it), the steps
# in the function body (i.e. the code) is run and the result is returned.
_ = asyncio.run(solve_coroutine)
print(f"The coroutine, async_solve(x=5), returned value: {_} once invoked.")

async def solver():
    values = []
    # async_solve(3) is a coroutine object. As is async_solve(5). 
    # await (i.e. asynchronous wait) invokes the coroutine.
    _ = await async_solve(3); values.append(_)
    _ = await async_solve(5); values.append(_)
    _ = await async_solve(7); values.append(_)
    _ = await async_solve(12); values.append(_)
    return values

_ = asyncio.run(solver())
print(f"The coroutine, solver(), returned values: {_} once invoked.")

async def task_based_solver():
    tasks = []
    coroutines = [async_solve(3), async_solve(5), async_solve(7), async_solve(12)]
    for coroutine in coroutines:
        # The create-task function does two things. It turns the coroutine
        # into a task, and schedules that task to run asynchronously.
        # Each task is an instance of asyncio.Task. Notably, these task instances are not 
        # also coroutine objects. In other words, Task does not inherit from coroutine.
        task = asyncio.create_task(coro=coroutine)
        tasks.append(task)
    
    print(f"isinstance(coroutine, asyncio.Future): {isinstance(coroutines[-1], asyncio.Future)}")
    print(f"isinstance(task, asyncio.Future): {isinstance(task, asyncio.Future)}")
    
    # Ensure all the tasks finish, before we attempt to access their result.
    # Without this, we may encounter an error that looks like:
    # asyncio.exceptions.InvalidStateError: Result is not set.
    # when trying to access the task's result.
    for task in tasks:
        # Like coroutines, tasks can be awaited. I'm not entirely sure what 'await' does here!
        # Presumably, it blocks this thread of computation from continuing until the task is done.
        # While waiting, the scheduler effectively pauses this thread and resumes a different thread 
        # (or at least checks if other threads can be resumed).
        await task
        
    return [t.result() for t in tasks]

start = time.time()
_ = asyncio.run(task_based_solver())
print(f"Time elapsed: {time.time() - start:.2}s.")
print(f"The coroutine, task_based_solver(), returned values: {_} once invoked.")
