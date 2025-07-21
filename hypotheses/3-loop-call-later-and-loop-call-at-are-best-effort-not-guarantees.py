"""
loop.call_later and loop.call_at operate on a best-effort basis and are not guarantees.
That is, the callbacks each method requests to be invoked at a certain time or delay will
not necessarily be invoked at that exact, specified time and may be invoked some while 
later. 
"""

import asyncio
import time
import datetime

def print_msg(msg: str):
    print(f"Executing print_msg() at time: {datetime.datetime.now().strftime('%H:%M:%S')}. Message is: {msg}.")

async def main():
    
    
    delay = 2
    loop.call_later(delay, print_msg, "I am call-later!")
    loop.call_at(loop.time() + delay, print_msg, "It is I, call-at!")
    print(f"Requested call-later & call-at at: {datetime.datetime.now().strftime('%H:%M:%S')} with a delay of: {delay} seconds.\n")

    time.sleep(10)

loop = asyncio.new_event_loop()
main_task = asyncio.Task(main(), loop=loop)
loop.run_until_complete(main_task)
