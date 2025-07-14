"""
When I await a task, where does control go back to?

The event-loop's _run_once method seems to generally be orchestrating the show.

The event-loop's attributes _ready and _scheduled each contain Handle's. As 
expected the Handle's in _ready are ready to be run now. And those in _scheduled
are slated for a later time.

A Handle is invoked via Handle._run. A Handle has four attributes: 
    context: contextvars.Context
    loop: asyncio.EventLoop
    callback: ???
    args: tuple
Now, what's this callback fellow? Task.__step

I commented out the code (lines 404-410) in task.py which uses the C-implementation 
of Task instead of the Python one because I can't debug into the C-implementation.
I did the same for Future in futures.py (lines 422-429).

Ahhh. I can now better follow what's happening within Task! Task.__step is called
by handle._run. Task.__step then calls Task.__step_run_and_handle_result. And finally
Task.__step_run_and_handle_result invokes coro.send(None).

When that coroutine eventually calls await on a Future or Task, the Future.__await__ 
method is invoked, which calls yield. That yield sends control back to where coro.send 
was called from, i.e. Task.__step_run_and_handle_result.

What's the order of events when I run this script?
1. The event-loop named loop is created.
2. The Task named main_task is created. A related Handle object is made 
    and added to the event-loop via loop._call_soon. The Handle's 
    callback-function was set to main_task.__step.
3. loop.run_forever() is called. That method continuously calls 
    loop._run_once. loop._run_once sees the main_task's Handle object
    in the list of ready Handles. It pops it from the list 
    and invokes the callback: main_task.__step. main_task.__step
    eventually calls main_task.coroutine.send(None). Recall 
    coroutine.send() transfers control to the coroutine. 
4. The coroutine associated with main_task now has control. It
    proceeds with its function body first calling print. Next,
    it creates a new Task work_work_task. Similar to main_task, part
    of Task's __init__ method involves creating a related 
    Handle object with callback work_work_task.__step and adding it
    to the event-loop. Note: control remains with the coroutine
    main_task. 
5. Next, await work_work_task is called which calls 
    work_work_task.__await__ which calls yield self (i.e. 
    yield work_work_task). This yields control back to the most-recent
    .send() call and provides the work_work task object. Recall that .send()
    call was from main_task.__step which was invoked by the event-loop. A
    callback is added to work_work task roughly via 
    work_work_task.add_done_callback(fn=main_task.__wakeup). This adds
    the callback to work_work_task._callbacks. 
6. Finally, the main_task.__step called in (3) has finished. loop._run_once 
    finishes and goes back to loop._run_forever. Unsurprisingly, 
    loop._run_forever once again calls loop._run_once. This eventually
    transfer control to the work_work_task's coroutine. This coroutine
    never awaits something, and eventually implicitly returns None. 
    It doesn't yield, but it does return. I wonder where it returns to? 
    Presumably where it was called i.e. work_work_task.__step. 
    Ahhh!! A StopIteration error is thrown!
7. The handling of StopIteration error in work_work_task.__step handles 
    setting the Task to done. Then it adds any callbacks that Task had 
    added via add_done_callback to the event-loop as Handles.  In this case
    main_task.__wakeup is the callback and the arg provided is self 
    (i.e. work_work_task).
8. Control returns to the event-loop. The _run_once call finishes. _run_forever
    calls _run_once again. Now, main_task.__wakeup is called. First, it ensures
    the future it waited on is done via work_work_task.result() which will 
    raise an Exception if the state is pending (i.e. not done or cancelled).
    Finally, main_task.__wakeup calls main_task.__step. Again, this calls 
    main_task.coroutine.send(None) which returns control to the coroutine
    where it left-off -- in the yield in work_work_task.__await__. 
    The last step of __await__ is return work_work_task.result(), which 
    makes available any result of the awaited task. 
9. The main couroutine now finishes its body, then similarly raises a 
    StopIteration error which yields control back to the most recent 
    .send(), so control is now back in main_task.__step which
    eventually goes back to the event-loop. The event-loop has no more
    tasks and just continues to loop. 


--------

Ahhhh!! yields are still the key to returning control to the event-loop! The 
    __await__ method of the class Future crucially has a line: 'yield self'.
    Which means yield to the caller (event-loop) and pass back this object 
    when you do. 

Ahh. Awaiting a Task or a Future cedes control to the event-loop. Awaiting a coroutine
does not. Instead the coroutine immediately runs. When resuming that Task or Future
where does it resume from? I assume not the yield in Future.__await__ given how 
bare that method is.

I skimmed a snarky canadian's blog-post on asyncio. His code-example was very helpful.
In his case, each task yields the time it should be resumed at. Since each task is 
called from the event-loop, that's also where each task yields back to. 

Now, apparently await is a lot like yield-from. So, when do actual yields happen?
"""

import asyncio
import time


async def work_work():
    print(
        "I am a dutiful worker preparing to work-work. "
        "I promise I won't sleep on the job again."
    )
    time.sleep(1)
    print("I, worker, completed my work!")
    return 7

async def main():
    print("Beginning coroutine main().")
    work_work_task = asyncio.Task(work_work())
    work_work_result = await work_work_task
    print(f"work_work result: {work_work_result}.")
    print("Finished coroutine main().")

# This is the loop chosen by asyncio when using 
# new_event_loop() on my machine.
import ipdb; ipdb.set_trace()
loop = asyncio.unix_events._UnixSelectorEventLoop()
main_task = asyncio.Task(main(), loop=loop)
loop.run_forever()