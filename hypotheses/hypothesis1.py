"""
Hypothesis
    awaiting a Future and/or Task uses no cpu-time until the Future and/or Task is 
    marked complete.
Experiment
    I instantiated a Task, like so asyncio.Task(coroutine, loop=loop), then printed
    some information, then awaited the task. 
Result
    Incorrect. Notably, the task did not begin execution until I awaited it! 

Hypothesis
    awaiting a Task executes (or schedules for execution) its' coroutine.
Experiment
    I instantiated a Task, again like asyncio.Task(coroutine, loop=loop). Then, printed
    some information, waited a long while, then awaited the task. I did the same approach,
    but added an await asyncio.sleep(0) call. 
Result
    The task only began execution once it was awaited. However, it executed prior to the prints 
    and sleep in the second case, where I called await asyncio.sleep(0).
"""

"""
Conclusions

Instantiating a task schedules it for execution. But the task won't execute its' coroutine
until control somehow gets back to the event-loop.
"""

import time
import asyncio

async def other_func():
    print("Executing other_func.")

async def main():
    
    task = asyncio.Task(coro=other_func())
    
    # Uncomment this line to see the effect awaiting a Task has on the order of prints.
    # await asyncio.sleep(0)

    print("hey, hi, hello!")
    time.sleep(3)
    await task

asyncio.run(main())
