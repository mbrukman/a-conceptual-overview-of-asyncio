# A conceptual overview of the ideas and objects which power Python's `asyncio`

## Motivation

I've used `asyncio` a couple times in work-related projects. It came up again recently for a web-socket related effort I'm exploring. I felt I had a somewhat fragmented and ultimately fairly weak mental-model of how `asyncio` actually works. The official `asyncio` docs provide pretty decent documentation for each specific function, but, in my opinion, lack a cohesive overview of the package's design and functionality to help the user make informed decisions about which tool in the `asyncio` tool-kit they ought to grab, or to recognize when `asyncio` is the entirely wrong tool-kit. This is my attempt to fill that gap. 

There were a few blog-posts, stack-overflow discussons and other writings about `asyncio` that I found helpful, but didn't fully provide what I was looking for. I've linked the ones I enjoyed and/or found useful below.

A few aspects particually drove my curiosity (read: drove me nuts). I wanted to know what's roughly happening behind the scenes when various objects are awaited. And, how does `asyncio` differentiate between a task which doesn't need cpu-time to make progress towards completion (for example a network-request or file-read) as opposed to a task that does need cpu-time to make progress (for example computing the $n^{th}$ fibonacci number). In other words, how does `asyncio.sleep()` run asynchronously while `time.sleep()` does not? 

## Introduction

The details of how asyncio works under the hood are pretty hairy, so I offer two conceputal overviews. The first section titled Overview is meant to provide a sturdy mental model without getting into too many specifics of asyncio. The second titled "More of the nuts & bolts" gets into the nitty-gritty. If nitty-gritty is your jam or you're looking to more deeply understand what's going on, I recommend starting with the first section and then proceeding through the second section. I've tried to ensure they don't repeat each other, i.e. they're complementary.

## Overview

#### Event Loop

Everything in asyncio happens relative to the event-loop. It's the star of the show. It's also kind of like an orchestra conductor or military general. She's behind the scenes managing resources. Some power is explicitly granted to her, but a lot of her ability to get things done comes from the respect & cooperation of her subordinates.

In more technical terms, the event-loop contains a queue of Tasks it should run. Some Tasks are added directly by you, and some indirectly by asyncio. The event-loop invokes a Task by giving it control, similar to a context-switch or calling a function. That Task then runs. Once it pauses or completes, it returns control to the event-loop. The event-loop then invokes the next Task in the queue. This process repeats indefinitely. 

```python
import asyncio

# This creates an event-loop.
event_loop = asyncio.new_event_loop()
event_loop.run_forever()
```

#### Asynchronous Functions & Coroutines

This is a regular 'ol Python function.
```python
def simple_func(x: int):
    print(
        f"I am simple_func. I live a simple life. Someone knocked "
        f"on my door this morning to give me x: {x}."
    )
```

And this is an asynchronous-function or coroutine-function.
```python
async def super_special_func(x: int):
    print(
        f"I am super_special_func. I am way cooler than simple_func. "
        f"Someone knocked on my door this morning to give me x: {x}."
    )
```

Calling a regular function invokes its' logic or body. 
```python
>>> simple_func(x=5)
I am simple_func. I live a simple life. Someone knocked on my door this morning to give me x: 5.
>>> 
```

Calling an asynchronous function creates and returns a coroutine object.
```python
>>> super_special_func(x=5)
<coroutine object super_special_func at 0x104ed2740>
>>> 
```

The terms "asynchronous function" (or "coroutine function") and "coroutine object" are often conflated as coroutine. I find that a tad confusing. In this article, coroutine will exclusively mean "coroutine object". 

That coroutine sort-of represents the function's body or logic. A coroutine has to be explicitly started; merely creating the coroutine does not start it. Notably, it can be paused & resumed. That pasuing & resuming ability is what makes it asynchronous and special!

#### Tasks

Tasks are coroutines tied to an event-loop. That's a simplified definition that we'll flesh out later.

```python
# This creates a Task object. Instantiating or creating a Task automatically 
# adds it to the event-loop's queue.
super_special_task = asyncio.Task(coro=super_special_func(x=5), loop=event_loop)
```

#### Network I/O Example

Performing a database request across a network might take half a second or so, but that's ages in computer-time. Your processor could have done millions or even billions of things in that time. The same is true for say downloading a movie, requesting a website, loading a file from disk into memory, etc. The general theme is those are all input/output (I/O) actions.

```python
async def get_user_info(user_id: uuid.UUID):
    # Request the user's information from the database.
    user_info = db.get(user_id)
    return user_info

event_loop = asyncio.new_event_loop()
get_user_info = asyncio.Task(coro=get_user_info(), loop=event_loop)
event_loop.run_forever()
```

The underlying hardware responsible for performing the network request, parsing the response bytes and putting them into main-memory can run seperately from the CPU. Of course, that's all for nothing if we don't give the CPU something to do in the meantime.

In this case, we want to cede control back to the event-loop from the `get_user_info` coroutine just after calling `db.get(user_id)`. Then, return to the coroutine once that db-request has finished. 

To accomplish that we'll first cede control from our coroutine to the event-loop. The event-loop then creates a new Task, we'll refer to it as a watcher-task (though that's not official lingo by any means), with some important responsibilities. That watcher-task will check on the db-request to see if it's done. And it'll keep note of how to resume the `get_user_info` coroutine from where it was paused.

Each time the event-loop iterates over its' queue of tasks, the watcher-task will be run and check how the db-request is getting along. After say 6 cycles through the event-loop, the watcher-task finally sees that the db-request has completed. So, it grabs the result of that request, and adds another Task to the queue to resume the `get_user_info` coroutine with the db-request result. 


## More of the nuts & bolts


Tasks
Async Functions & Coroutines
Resuming a Task
Pausing a Task
Glossary
Things to Remember





### Asynchronous Functions (async)






### Futures (asyncio.futures.Future)

A future is an object meant to represent a computation or process's status and it's result (if any), hence the term future i.e. still to come or not yet happened. 

A future has a few important attributes. One is its' state which can be either 'pending', 'cancelled' or 'done'. Another is its' result which is set when the state transitions to 'done' and can be any Python object. To be clear, a Future does not represent the actual computation to be done, like a coroutine does, instead it represents the status of that computation, kind of like a status-light (red, yellow or green) or indicator. 

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


### Links 

A good overview of the fundamental Python language features asyncio uses. 
https://stackoverflow.com/questions/49005651/how-does-asyncio-actually-work

Great context and basic-intro to asyncio. In my experience, Real Python is generally excellent quality.
https://realpython.com/async-io-python/

I only skimmed this, but I found the example program at the end very useful to pull apart.
https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/

A good answer to a specific question about why coroutine generators exist.
https://stackoverflow.com/questions/46203876/what-are-the-differences-between-the-purposes-of-generator-functions-and-asynchr

