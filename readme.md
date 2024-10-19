## A conceptual overview of the ideas and objects which power Python's `asyncio`

### Motivation

I've used `asyncio` a couple times in work-related projects. It came up again recently for a web-socket related effort I'm exploring. I felt I had a somewhat fragmented and ultimately fairly weak mental-model of how `asyncio` actually works. The official `asyncio` docs provide pretty good documentation for each specific function available, but, in my opinion, lack a cohesive overview of the package's design and functionality to help the user make informed decisions about which tool in the `asyncio` tool-kit they ought to grab. This is my attempt to fill that gap.

There were a few blog-posts, stack-overflow discussons and other writings about `asyncio` that I found helpful, but didn't fully provide what I was after. For those curious, I've linked the ones I enjoyed and/or found useful below.

A few aspects particually drove my curiosity (read: drove me nuts). I wanted to know what's roughly happening behind the scenes when various objects are awaited. And, how does `asyncio` differentiate between a task which doesn't need cpu-time to make progress towards completion (for example a network-request or file-read) as opposed to a task that does need cpu-time to make progress (for example computing the $n^{th}$ fibonacci number). In other words, how does `asyncio.sleep()` run efficiently while `time.sleep()` does not? 

### Asynchronous Functions (async)

This is a regular 'ol Python function.
```
def simple_func(x: int):
    print(f"I am simple_func and I received the input x: {x}.")

```

This is known as an asynchronous-function or coroutine-function. Note: the only difference is the "async" prefix before "def".
```
async def simple_func(x: int):
    print(f"I am simple_func and I received the input x: {x}.")

```

Calling a regular function invokes it's body or logic. Calling a coroutine-function does not invoke the function's logic, instead it creates and returns a coroutine object. This is very similar to the distinction between functions and generators too. It's common to see the terms (and concepts) coroutine-function and coroutine-object lumped together as just coroutine which I find a tad confusing.

That coroutine object sort-of represents the function's body or logic. The coroutine object has to be explicitly started; merely creating the coroutine object does not start it. Notably, it can also be paused & resumed. That pasuing & resuming ability is what makes it asynchronous and special!

### Futures (asyncio.futures.Future)

A future is an object meant to represent a computation or process's status and it's eventual result, hence the term future i.e. still to come or not yet happened. It has a few important attributes. One is its' state which can be either 'pending', 'cancelled' or 'done'. Another is its' result which is set when the state transitions to 'done' and can be any Python object. To be clear, a Future does not represent the actual computation to be done, like a coroutine does, instead it represents the status of that computation, kind of like a status-light (red, yellow or green) or indicator. 

Here's a bit of a contrived example. The computation in this case is computing a factorial. The future object can let us know when the computation is done and what the result of the computation was. Of course, this isn't a very practical use-case, but perhaps you can imagine how such a Future object could be useful when it comes to file or network I/O. Reading a huge file from disk into memory may take a while and not need cpu resources, which we could devote to running another part of our program rather than merely idling. 

```
class Future:
    def __init__(self):
        self.state = 'pending'
        self.result = None
    
    def mark_done(self, result):
        self.state = 'done'
        self.result = result

def factorial(n: int, future: Future):
    
    multiplicative_total = 1
    for val in range(1, n):
        multiplicative_total *= val
    
    future.mark_done(multiplicative_total)
```

### Tasks (asyncio.tasks.Task)

Tasks are the love-child of Futures & coroutine-objects. In technical terms, Task subclasses Future thereby inherting its' properties and holds an instance attribute of a coroutine-object. In other words, a Task bundles together a computation and that computation's status-light.

Here's some code which illustrates the same idea (if you're into that kind of thing).
```
import collections

class Task(Future):
    def __init__(self, coroutine: collections.abc.Coroutine):
        self.coroutine = coroutine
```

### Event Loop (asyncio.base_events.BaseEventLoop)

The event-loop is kind of like an orchestra conductor or military general. She's the lady behind the scenes responsible for managing resources. 
She has some power explicitly granted to her, but a lot of her ability to get things done comes from the respect & cooperation of her subordinates. 

Most asyncio programs start something like so. And many other ways of invoking asyncio (like asyncio.run or asyncio.run_until_complete) largely 
re-use the main components of this approach.

```
import asyncio

async def def main():
    ...

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(coro=main())
    loop.run_forever()
```

The event-loop contains two queues each filled with Tasks: scheduled & ready. Tasks in the ready queue are ready to be invoked. Tasks
in the scheduled queue are not. For now, we'll only consider the ready-queue. Here's what one pass through the event-loop looks like:
1. Save the number of tasks currently in the ready-queue.
2. Pop a Task from the ready-queue
3. Invoke or resume the Task's coroutine. Run until the coroutine yields control back to the event-loop.
4. Repeat from step 2. until you've run as many tasks as you saved in step 1. This is to prevent running tasks 
    added to the event-loop on this iteration in this iteration. Not to worry, they'll be run next time!

To invoke or resume a coroutine, you can call `coroutine.send(None)`. This will return execution to wherever the coroutine yield-ed
and send along the provided value, in this case None. In other words, the event-loop surrenders control to the Task's coroutine 
and counts on the coroutine to not hog resources and eventually yield control back. But how does a coroutine yield control back? Read on!


### await

Frankly, this part is really fucking confusing to me. I've tried to make it clear.

You can only yield control back to the event-loop from a coroutine by awaiting a non coroutine-object that has a non-async generator method named `__await__`. I know that's a lot of jargon to digest, so here's an example in the hope it helps. Notably, awaiting a coroutine DOES NOT cede control to the event loop. 

```
class CustomAwaitable():
    def __await__(self):
        # This is a generator method rather than a plain method since it features a yield statemen in the body.
        yield

async def simple_print():
    print("Hello. I am a simple_printer. My means are simple and my work is good.")

async def main():
    
    custom_awaitable_obj = CustomAwaitable()
    # This will yield control to the event-loop.
    await custom_awaitable_obj

    coroutine_obj = simple_print()
    # This will NOT yield control to the event-loop.
    await coroutine_obj

...
```

### Wrapping it all together

The Future class defines an `__await__` method (which Task inherits) that also `yield`'s. In practice you'll generally just await Future or Task objects but if you'd like to extend asyncio's available operators or better understand how it works, well that's it.

await calls an object's __await__ method. I know, I know, that's a rather circular and not especially insightful answer. Only a few kinds of objects (or classes) have __await__ methods. Futures do.

The implementation (Future.__await__) is seemingly simple and only a few lines of code. It does two important things. 
First, it yields `yield self`, second, it returns `self.result`. The yield `self` call provides the object being awaited back to the 
event-loop. The event-loop adds it to the queue. It also adds a note to invoke the now-paused coroutine once the awaited object is done 
via Future.add_done_callback().

...

### loop.scheduled


