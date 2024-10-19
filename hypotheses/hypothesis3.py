"""
Hypothesis
    loop.call_later won't work if the main-thread is busy.
Experiment
    loop.call_later with a short delay on a function that prints some output. Then, 
    start a coroutine that takes a longer amount of time.
Result
    As expected! loop.call_later doesn't guarantee the callable will be invoked in 
    exactly delay seconds. 

Hypothesis
    What about loop.call_at? Repeat the same experiment used above for loop.call_later.
Result
    As expected! loop.call_at also doesn't guarantee the callable will be invoked
    at the given time. 
"""

"""
Conclusions

loop.call_later and loop.call_at operate on a best-effort basis and are not guarantees.
That is, the callbacks each method requests to be invoked at a certain time or delay will
not necessarily be invoked at that exact, specified time and may be invoked some while 
later. 
"""

import asyncio
import time
import datetime

def print_msg(msg: str):
    print(f"Executing print() at time: {datetime.datetime.now()}. Message is: \n{msg}.\n")

async def main():
    
    # Request print_msg to be called in 1 second.
    delay = 1
    loop.call_later(delay, print_msg, "I am call-later!")
    loop.call_at(loop.time() + delay, print_msg, "It is I, call-at!")
    print(f"Requested call-later & call-at at time: {datetime.datetime.now()} with a delay of: {delay} seconds.\n")
    time.sleep(10)

loop = asyncio.new_event_loop()
main_task = asyncio.Task(main(), loop=loop)
loop.run_forever()
