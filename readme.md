# A conceptual overview of the ideas and objects which power Python's `asyncio`

## Motivation

I've used `asyncio` a couple times now, but never really felt confident in my mental-model of how it works and how I can best use it. The official `asyncio` docs provide decent-enough documentation for each specific function in the package, but, in my opinion, lack a cohesive overview of the design and functionality to help the user make informed decisions about which tool in the `asyncio` tool-kit they ought to grab, or to recognize when `asyncio` is the entirely wrong tool-kit. This is my attempt to fill that gap. 

There were a few blog-posts, stack-overflow discussons and other writings about `asyncio` that I found helpful, but didn't fully provide what I was looking for. I've linked them below.

A few aspects particually drove my curiosity (read: drove me nuts). You should be able to answer all these questions by the end of this article.
- What's roughly happening behind the scenes when various objects are `await`-ed? 
- How does `asyncio` differentiate between a task which doesn't need cpu-time to make progress towards completion (for example a network-request or file-read) as opposed to a task that does need cpu-time to make progress (for example computing the $n^{th}$ fibonacci number). 
- How does `asyncio.sleep()` run asynchronously while `time.sleep()` does not? 
- How would I go about writing my own asynchronous variant of some operation (e.g. sleep, network-request, file-read, etc.)?

## Introduction

The details of how asyncio works under the hood are fairly hairy and involved, so I offer two conceputal overviews. The first section titled Overview is meant to provide a sturdy mental model without getting into too many specifics of asyncio. The second titled "More of the nuts & bolts" gets into the nitty-gritty. If nitty-gritty is your jam, you're looking to more deeply understand what's going on or want to build your own operators on top of asyncio, I recommend starting with the first section and then proceeding through the second section. I've tried to ensure they don't repeat each other and instead build on each other.

## Conceputal Overview

#### Event Loop

Everything in asyncio happens relative to the event-loop. It's the star of the show and there's only one. It's kind of like an orchestra conductor or military general. She's behind the scenes managing resources. Some power is explicitly granted to her, but a lot of her ability to get things done comes from the respect & cooperation of her subordinates.

In more technical terms, the event-loop contains a queue of Tasks to be run. Some Tasks are added directly by you, and some indirectly by asyncio. The event-loop pops a Task from the queue and invokes it (or gives it control), similar to a context-switch or calling a function. That Task then runs. Once it pauses or completes, it returns control to the event-loop. The event-loop then pops and invokes the next Task in its' queue. This process repeats indefinitely. Even if the queue is empty, the event-loop continues to cycle (somewhat aimlessly).

Effective overall execution relies on Tasks sharing well. A greedy task could hog control and leave the other tasks to starve rendering the event-loop rather useless. 

```python
import asyncio

# This creates an event-loop and indefinitely cycles through its' queue of tasks.
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

Calling a regular function invokes its' logic or body. 
```python
>>> simple_func(x=5)
I am simple_func. I live a simple life. Someone knocked on my door this morning to give me x: 5.
>>> 
```

And this is an asynchronous-function or coroutine-function.
```python
async def super_special_func(x: int):
    print(
        f"I am super_special_func. I am way cooler than simple_func. "
        f"Someone knocked on my door this morning to give me x: {x}."
    )
```

Calling an asynchronous function creates and returns a coroutine object.
```python
>>> super_special_func(x=5)
<coroutine object super_special_func at 0x104ed2740>
>>> 
```

The terms "asynchronous function" (or "coroutine function") and "coroutine object" are often conflated as coroutine. I find that a tad confusing. In this article, coroutine will exclusively mean "coroutine object". 

That coroutine represents the function's body or logic. A coroutine has to be explicitly started; merely creating the coroutine does not start it. Notably, it can be paused & resumed. That pausing & resuming ability is what makes it asynchronous and special!

#### Tasks

Tasks are coroutines tied to an event-loop.

```python
# This creates a Task object. Instantiating or creating a Task automatically 
# adds it to the event-loop's queue.
super_special_task = asyncio.Task(coro=super_special_func(x=5), loop=event_loop)
```

It's common to see a Task instantiated without explicitly specifying the event-loop it belongs to. Since there's only one event-loop (a global singleton), asyncio made the loop argument optional and will add it for you if it's left unspecified.
```python
# The Task is implicitly tied to the event-loop by asyncio since the loop 
# argument was left unspecified.
super_special_task = asyncio.Task(coro=super_special_func(x=5))
```

#### Network I/O Example

Performing a database request across a network might take half a second or so, and that's ages in computer-time. Your processor could have done millions or even billions of things. The same is true for say downloading a movie, requesting a website, loading a file from disk into memory, etc. The general theme is those are all input/output (I/O) actions.

```python
async def get_user_info(user_id: uuid.UUID):
    # Request the user's information from the database.
    user_info = db.get(user_id)
    return user_info

event_loop = asyncio.new_event_loop()
get_user_info = asyncio.Task(coro=get_user_info(), loop=event_loop)
event_loop.run_forever()
```

The underlying hardware responsible for performing the network request and placing the response-bytes into main-memory can run seperately from the CPU. That's all for nothing if we don't let the CPU something do something in the meantime.

In this case, we want to let the CPU focus on other activities after we call `db.get(user_id)`. Then, have the CPU come back once the networking hardware has done its' part.

To accomplish that we'll cede control from our coroutine to the event-loop after calling `db.get(user_id)`. The event-loop then creates a new Task, that we'll refer to as a watcher-task (though that's not official lingo by any means), with some important responsibilities. That watcher-task will check on the db-request to see if it's done. And it'll keep note of how to resume the `get_user_info` coroutine from where it was paused.

Each time the event-loop iterates over its' queue of tasks, the watcher-task will be run and check how the db-request is getting along. After say 6 cycles through the event-loop, the watcher-task finally sees that the db-request has completed. So, it grabs the result of that request, and adds another Task to the queue to resume the `get_user_info` coroutine with the db-request result. 

## Conceputal Overview Part 2: the nuts & bolts

#### coroutine.send(), await, yield & StopIteration

`coroutine.send(arg)` is the method used to start or resume a coroutine. 

If the coroutine was paused and is now being resumed, the argument `arg` will be sent in as the return-value of the `yield` statement which originally paused it. When starting a coroutine, or when there's no value to send in, you can use `coroutine.send(None)`. The code snippet below illustrates both ways of using `coroutine.send(arg)`.

`yield` pauses execution and returns control to the caller. In the example below, the caller is `await custom_awaitable` on line 12. Generally, `await` calls the `__await__` method of the given object and then percolates any yields it receives up the call-chain, in this case, that's back to `... = coroutine.send(None)` on line 21. 

Then, we resume the coroutine with `coroutine.send(42)` on line 26. The coroutine picks back up from where it yielded/paused on line 3. Finally, the coroutine executes the remaining statements in its' body. When a coroutine finishes it raises a `StopIteration` exception with the return-value attached to the exception.

```python
1  class CustomAwaitable:
2      def __await__(self):
3          value_sent_in = yield 7
4          print(f"Awaitable resumed with value: {value_sent_in}.")
5          return value_sent_in
6 
7  async def simple_func():
8      print("Beginning coroutine simple_func().")
9      custom_awaitable = CustomAwaitable()
10     print("Awaiting custom_awaitable...")
11    
12     value_from_awaitable = await custom_awaitable
13     print(f"Coroutine received value: {value_from_awaitable} from awaitable.")     
14     return 23
15
16  # Create the coroutine.
17  coroutine = simple_func()
18  
19  # Begin the coroutine. Store any results yielded or returned by the coroutine into
20  # variable: coroutine_intermediate_result.
21  coroutine_intermediate_result = coroutine.send(None)
22  print(f"Coroutine paused and returned intermediate value: {coroutine_intermediate_result}.")
23  
24  # Resume the coroutine and pass in the number 42 when doing so. 
25  print(f"Resuming coroutine and sending in value: 42.")
26  try:
27      coroutine.send(42)
28  except StopIteration as e:
29      returned_value = e.value
30  print(f"Coroutine finished and provided value: {returned_value}.")
```

That snippet produces this output:
```
Beginning coroutine simple_func().
Awaiting custom_awaitable...
Coroutine paused and returned intermediate value: 7.
Resuming coroutine and sending in value: 42.
Awaitable resumed with value: 42.
Coroutine received value: 42 from awaitable.
Coroutine finished and provided value: 23.
```

The only way to yield (or effectively cede control) from a coroutine is to `await` an object that `yield`s in its `__await__` method. That might sound odd to you. Frankly, it was to me too. 
1. What about a `yield` directly within the coroutine? The coroutine becomes a generator-coroutine, a different beast entirely.
2. What about a `yield from` within the coroutine to a function that `yield`s (i.e. plain generator)? SyntaxError: `yield from` not allowed in a coroutine.

#### Futures

A future is an object meant to represent a computation or process's status and result (if any), hence the term future i.e. still to come or not yet happened. 

A future has a few important attributes. One is its' state which can be either 'pending', 'cancelled' or 'done'. Another is its' result which is set when the state transitions to 'done'. To be clear, a Future does not represent the actual computation to be done, like a coroutine does, instead it represents the status and result of that computation, kind of like a status-light (red, yellow or green) or indicator. Finally, a future stores callbacks or functions it should call once its' state becomes 'done'.

Here's that same description stated in code:

```python
class Future:
    def __init__(self):
        self.state = 'pending'
        self.result = None
        self.callbacks = []
    
    def done(self) -> bool:
        is_future_done = self.state == 'done'
        return is_future_done

    def add_callback(self, fn: typing.Callable):
        self.callbacks.append(fn)

    def mark_done(self, result):
        self.state = 'done'
        self.result = result
        for callback in self.callbacks:
            callback()
```

Futures also have an important method: `__await__`. Here is a minimally modified snippet of the implementation found in `asyncio.futures.Future`. It's okay if it doesn't really make sense now, we'll go through it in detail shortly.

```python
class Future:
    ...
    def __await__(self):
        if not self.done():
            yield self
        if not self.done():
            raise RuntimeError("await wasn't used with future")
        return self.result()
```

Task is a subclass of Future meaning it inherits its' attributes & methods. And Task does not override Future's `__await__` implementation. `await`-ing a Task or Future invokes that above `__await__` method and percolates the `yield` to relinquish control. 

> [!IMPORTANT]  
>  **Unlike Tasks and Futures, `await`-ing a coroutine does not cede control!**

That is, simply wrapping a coroutine in a Task first, then `await`-ing it will cede control. I imagine that design was intentional to allow the author to decide when they want to yield control versus keep it. 

#### Tying it all together



#### What does await do?

#### How do I cede control from my coroutine to the event-loop? 

#### How does the event-loop know where to resume my coroutine from?

#### How does the event-loop know when the thing I'm waiting for is done (and whether it needs cpu-time to get there)?


Tasks
Async Functions & Coroutines
Resuming a Task
Pausing a Task
Glossary
Things to Remember





### Asynchronous Functions (async)






### Futures (asyncio.futures.Future)



Here's a bit of a contrived example. The computation in this case is computing a factorial. The future object can let us know when the computation is done and what the result of the computation was. Of course, this isn't a very practical use-case, but perhaps you can imagine how such a Future object could be useful when it comes to file or network I/O. Reading a huge file from disk into memory may take a while and not need cpu resources, which we could devote to running another part of our program rather than merely idling. 



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

