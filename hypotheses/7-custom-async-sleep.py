import asyncio
import time
import datetime


class YieldToEventLoop:
    def __await__(self):
        yield

async def _sleep_watcher(future: asyncio.Future, seconds: float):
    start_time = time.time()
    while True:
        time_elapsed = time.time() - start_time
        if  time_elapsed > seconds:
            # This marks the future as done.
            future.set_result(None)
            break
        else:
            # This is basically the same as asyncio.sleep(0), but I prefer the clarity
            # this approach provides. Not to mention it's kind of cheating to use asyncio.sleep
            # when implementing an equivalent!
            await YieldToEventLoop()

async def async_sleep(seconds: float):
    future = asyncio.Future()
    # Add the watcher-task to the event-loop.
    watcher_task = asyncio.Task(_sleep_watcher(future, seconds))
    await future

async def other_work():
    print(f"I am worker. Work work.")
    time.sleep(0.1)

async def main():
    # Add a variety of other tasks to the event-loop, so there's something to do while
    # asynchronously sleeping.
    asyncio.Task(other_work()), asyncio.Task(other_work()), asyncio.Task(other_work())

    print(f"Starting main() at time: {datetime.datetime.now().strftime("%H:%M:%S")}.")
    await asyncio.Task(async_sleep(3))
    print(f"Done main() at time: {datetime.datetime.now().strftime("%H:%M:%S")}.")

asyncio.run(main())