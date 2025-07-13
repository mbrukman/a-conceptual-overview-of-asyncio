"""
Conclusions

awaiting a coroutine does not cede control to the event-loop. awaiting a Task does.
"""

import asyncio
import datetime


async def factorial(n: int):
    print(f"Computing factorial(n={n:,}) at time: {datetime.datetime.now().strftime("%H:%M:%S")}.")
    total = 1
    for val in range(1, n+1):
        total *= val
    return total

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
        
        # awaiting a coroutine does not cede control to the event-loop to run other tasks
        # i.e. the print_task created earlier.
        # await factorial(n=50_000)

        # awaiting a Task will cede control to the event-loop.
        await asyncio.Task(factorial(n=50_000))

    await print_task

loop = asyncio.new_event_loop()
task = asyncio.Task(main(), loop=loop)
loop.run_forever()