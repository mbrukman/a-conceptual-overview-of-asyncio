import datetime
import heapq
import types
import time


class Task:

    """Represent how long a coroutine should wait before starting again.

    Comparison operators are implemented for use by heapq. Two-item
    tuples unfortunately don't work because when the datetime.datetime
    instances are equal, comparison falls to the coroutine and they don't
    implement comparison methods, triggering an exception.
    
    Think of this as being like asyncio.Task/curio.Task.
    """

    def __init__(self, coro, time_to_resume_coro: datetime.datetime):
        self.coro = coro
        self.time_to_resume_coro = time_to_resume_coro

    def __eq__(self, other):
        return self.time_to_resume_coro == other.time_to_resume_coro

    def __lt__(self, other):
        return self.time_to_resume_coro < other.time_to_resume_coro


class SleepingLoop:

    """An event loop focused on delaying execution of coroutines.

    Think of this as being like asyncio.BaseEventLoop/curio.Kernel.
    """

    def __init__(self, *coros):
        self.coros = coros
        self.pending_tasks = []

    def run_until_complete(self):
        
        # Start all the coroutines.
        for coro in self.coros:
            time_to_resume_coro = coro.send(None)
            heapq.heappush(self.pending_tasks, Task(coro, time_to_resume_coro))
        
        # Keep running until there is no more work to do.
        while len(self.pending_tasks) > 0:
            now = datetime.datetime.now()
            # Get the coroutine with the soonest resumption time.
            task = heapq.heappop(self.pending_tasks)
            if now < task.time_to_resume_coro:
                # We're ahead of schedule; wait until it's time to resume.
                delta = task.time_to_resume_coro - now
                time.sleep(delta.total_seconds())
                now = datetime.datetime.now()
            try:
                # It's time to resume the coroutine.
                print(f"Resuming task: {task}.")
                wait_until = task.coro.send(now)
                heapq.heappush(self.pending_tasks, Task(task.coro, wait_until))
            except StopIteration:
                # The coroutine is done.
                pass


@types.coroutine
def sleep(seconds):
    """Pause a coroutine for the specified number of seconds.

    Think of this as being like asyncio.sleep()/curio.sleep().
    """

    now = datetime.datetime.now()
    sleep_until = now + datetime.timedelta(seconds=seconds)
    
    # Make all coroutines on the call stack pause; the need to use `yield`
    # necessitates this be generator-based and not an async-based coroutine.
    print(f"Yielding sleep_until: {sleep_until}")
    actual = yield sleep_until
    
    # Resume the execution stack, sending back how long we actually waited.
    print(f"Returning actual - now: {actual - now}")
    return actual - now


async def countdown(rocket_name: str, countdown_secs: int, *, delay=0):
    """Countdown a launch for `length` seconds, waiting `delay` seconds.

    This is what a user would typically write.
    """
    
    print(f"{rocket_name} waiting {delay} seconds before starting countdown.")
    time_waited = await sleep(delay)
    print(f"{rocket_name} beginning countdown after delaying: {time_waited} seconds.")

    while countdown_secs:
        print(f"{rocket_name} T-minus {countdown_secs}")
        time_waited = await sleep(1)
        countdown_secs -= 1

    print(rocket_name, 'lift-off!')


def main():
    """Start the event loop, counting down 3 separate launches.

    This is what a user would typically write.
    """
    loop = SleepingLoop(
        # countdown('A', 5), 
        countdown('B', 3, delay=0),
        countdown('C', 3, delay=0)
    )
    start_time = datetime.datetime.now()
    loop.run_until_complete()
    print('Total elapsed time is', datetime.datetime.now() - start_time)


if __name__ == '__main__':
    main()