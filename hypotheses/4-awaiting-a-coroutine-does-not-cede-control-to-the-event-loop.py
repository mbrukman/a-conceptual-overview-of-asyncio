"""
Conclusions

awaiting a coroutine does not cede control to the event-loop. awaiting a Task does.
"""

import asyncio
import datetime


async def factorial(n: int):
    print(f"Beginning factorial(n={n:,}) at time: {datetime.datetime.now().strftime("%H:%M:%S")}.")
    total = 1
    for val in range(1, n+1):
        total *= val
    print(f"Done factorial(n={n:,}) at time: {datetime.datetime.now().strftime("%H:%M:%S")}.\n")
    return total

async def simple_print():
    print(
        "============================================\n"
        f"Hi, I am simple_print() coming to you live at: {datetime.datetime.now().strftime("%H:%M:%S")}. "
        "I am but a lowly, simple printer, though I have all I need in life"
        " -- fresh paper & a loving octopus-wife."
        "\n============================================"
    )

async def main():
    
    print_task = asyncio.Task(simple_print())
    
    num_repeats = 5
    for _ in range(num_repeats):
        
        # There are two ways you could prove to yourself that await-ing a coroutine 
        # does not cede control to the event-loop.
        
        # One, follow the control flow by stepping with a debugger.
        # import ipdb; ipdb.set_trace()

        # Two, run this program many times. Alternate which of the following two 
        # lines you comment out and note how the behavior differs.
        # await factorial(n=50_000)
        await asyncio.Task(factorial(n=50_000))

    await print_task

loop = asyncio.new_event_loop()
task = asyncio.Task(main(), loop=loop)
loop.run_until_complete(task)