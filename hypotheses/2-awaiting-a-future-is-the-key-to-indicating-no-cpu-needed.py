"""
Hypothesis
    awaiting a Future (not a Task!) indicates no cpu-time is needed, until that Future's state magically 
    changes from pending to cancelled or complete. In other words, awaiting a Future blocks
    that thread or stack of execution and returns control to the event-loop to do whatever
    else the event-loop pleases.
Experiment
    await a Future in the main-thread. wait for a long-time, then, magically 
    (loop.call_later) change the Future's state to complete.
Result
    As expected. An awaited Future does nothing until that Future's state changes.
"""

"""
Conclusions

A Future is the key to indicating no cpu-time is needed to make forward progress.
"""
import asyncio
import datetime

async def main():
    future = asyncio.Future()
    # The arguments to call_later here are 'delay', 'callback' and '*args'.
    loop.call_later(45, future.set_result, None)
    print(f"Awaiting future at: {datetime.datetime.now()}")
    await future
    print(f"Future done awaiting at: {datetime.datetime.now()}")

loop = asyncio.new_event_loop()
main_task = asyncio.Task(main(), loop=loop)
loop.run_forever()
