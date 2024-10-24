"""
Hypothesis
    awaiting a Task or coroutine does not cede control to the event-loop. However,
    awaiting a Future does.
Experiment
    await a Task (and coroutine) while there's another Task waiting in the 
    event-loop. 
Result
    awaiting a Task allowed the other Task to run! That is, awaiting a Task did in fact
    cede control to the event-loop. awaiting a coroutine did not allow the task to run. 
    
Perhaps the coroutine just got lucky and kept getting scheduled first over the Task?

Hypothesis
    awaiting a coroutine does not cede control to the event-loop.
Experiment
    use a debugger to follow the execution flow when awaiting a coroutine. 
Result
    await coroutine does not go to any asyncio library code, it instead goes 
    straight to the coroutine's logic/body, whereas await task did jump to some 
    asyncio library code.
"""

"""
Conclusions

awaiting a coroutine does not cede control to the event-loop. awaiting a Task or Future
does cede control.
"""

import asyncio
import datetime


async def factorial(n: int):
    """Iteratively compute n factorial. For n=50,000 this takes about 1
    second to run on my machine -- an M1 Macbook Air with 16GB Ram.
    """
    print(f"Computing factorial(n={n:,}) at time: {datetime.datetime.now()}")
    multiplicative_total = 1
    for val in range(1, n+1):
        multiplicative_total *= val
    
    return multiplicative_total

async def simple_print():
    print(
        "Hi, I am simple_print(). I am but a lowly, simple printer, "
        "though I have all I need in life -- fresh paper & a loving octopus-wife."
    )

async def main():
    
    print_task = asyncio.Task(simple_print())
    num_factorials_to_compute = 15
    
    for _ in range(num_factorials_to_compute):
        
        # Toggle between commenting the following two-lines (Task vs coroutine) to see 
        # how awaiting a coroutine and awaiting a Task change the script's overall 
        # behavior.
        # Alternatively, uncomment the set_trace() to follow the flow with a debugger.
        
        # import ipdb; ipdb.set_trace()
        
        await factorial(n=50_000)
        # await asyncio.Task(factorial(n=50_000))

    await print_task

loop = asyncio.new_event_loop()
task = asyncio.Task(main(), loop=loop)
loop.run_forever()