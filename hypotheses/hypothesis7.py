"""
I've got a decent idea of how control is passed between the 
various Tasks in an event-loop. But, how does the event-loop
know it's ok to skip/wait for some Tasks to finish rather
than needing to schedule them in order to finish? That's
a bit vaguely phrased. Let me illustrate with an example.

Case 1:
    main-task instantiates a compute-task, then awaits it
    that await gives control to the event-loop which in turn
        gives control to the compute-task.
    the compute-task finishes. Control returns to the event-loop's
        call of Task.__step where that method finishes by requesting 
        each of it's done-callbacks be put on the event-loop as Handles via
        loop.call_soon. Then, the method exits and the event-loop
        continues cycling.

Case 2:
    main-task instantiates a sleep-task, then awaits it
    that await gives control to the event-loop which
        gives control to the sleep-task. Now,
        how does the sleep-task indicate to the event
        -loop it doesn't need control to make progress
        towards completion?


Let's consider Case 2 with something like asyncio.sleep(delay)
    1. asyncio.sleep instantiates a Future that's attached to
        the loop. 
    2. Then, it adds a Task (well, really a Handle) to be invoked 
        'delay' seconds later via loop.call_later. The callback
        of that Handle is Future.set_done(). In other words
        once invoked, it'll mark that Future done. 
    3. Finally, it awaits that Future. Awaiting the future
        adds a done-callback which will resume the asyncio.sleep
        coroutine. Then, control goes back to the event-loop. 

Under the hood loop.call_later uses loop.call_at and specifies
an exact time. The rest feels pretty clear from here.
    1. On each iteration of _run_once, the loop checks whether
        the Task should be invoked (i.e. is 
        current_time > Task.start_time).
    2. Once that condition is True, the Task is added to the list
        of Tasks ready for execution. That is it's moved from
        loop._scheduled to loop._ready. 
    3. The task is invoked. Recall it's job is to set the
        Future created in asyncio.sleep to Done. And when that
        Future was awaited in asyncio.sleep, a callback was
        added to that Future's done_callbacks attribute. So,
        once that Future is set to done, it resumes the 
        asyncio.sleep coroutine which just finishes and
        returns control to the sleep() coroutine.

What about something like a file-read or network-request whose 
'delay' is unknown? I suspect loop._process_events is involved.
Ah, I think the event-loop just checks on each iteration of
_run_once whether the relevant file-read/network-request/etc
is done. 
"""
import asyncio

async def sleep():
    print("Beginning sleep() coroutine.")
    import ipdb; ipdb.set_trace()
    await asyncio.sleep(2)
    print("Finished sleep() coroutine.")

async def main():
    print("Beginning main() coroutine.")
    sleep_task = asyncio.Task(sleep())
    await sleep_task
    print("Finished main() coroutine.")

loop = asyncio.new_event_loop()
main_task = asyncio.Task(main(), loop=loop)
loop.run_forever()