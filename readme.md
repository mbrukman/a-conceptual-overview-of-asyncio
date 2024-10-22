# A conceptual overview of the ideas and objects which power Python's `asyncio`

### Todo's

- [ ] Understanding async generators
- [ ] Add an async generators section (if necessary)
- [ ] Review & rename the hypotheses.
- [ ] A fuller example w/ file I/O
- [ ] Remaining details -- e.g. 3 queues, select/events & async gens
- [ ] Table of contents
- [ ] Final read-through



## Motivation

I've used `asyncio` a couple times now, but never really felt confident in my mental-model of how it works and how I can best use it. The official `asyncio` docs provide pretty-decent documentation for each specific function in the package, but, in my opinion, lack a cohesive overview of the design and functionality to help the user make informed decisions about which tool in the `asyncio` tool-kit they ought to grab, or to recognize when `asyncio` is the entirely wrong tool-kit. This is my attempt to fill that gap. 

There were a few blog-posts, stack-overflow discussons and other writings about `asyncio` that I found helpful, but didn't fully provide what I was looking for. I've linked them below.

A few aspects particually drove my curiosity (read: drove me nuts). You should be able to answer all these questions by the end of this article.
- What's roughly happening behind the scenes when an objects is `await`-ed? 
- How does `asyncio` differentiate between a task which doesn't need cpu-time to make progress towards completion (for example a network-request or file-read) as opposed to a task that does need cpu-time to make progress (for example, computing n-factorial). 
- How does `asyncio.sleep()` run asynchronously while `time.sleep()` does not? 
- How would I go about writing my own asynchronous variant of some operation (e.g. sleep, network-request, file-read, etc.)?

## Introduction

The details of how asyncio works under the hood are fairly hairy and involved, so I broke the conceputal overview into two parts. The first part is meant to provide a fairly sturdy and reliable mental model without getting into too many specifics of how they work. The second part goes deeper explaining the Python-language building blocks `asyncio` leverages and exploring simplified implementations of the key functions of `asyncio`. If you're looking to more deeply understand how asyncio does what it does, or want to build your own operators on top of asyncio, I highly recommend it!

## Conceputal Overview Part 1

#### Event Loop

Everything in asyncio happens relative to the event-loop. It's the star of the show and there's only one. It's kind of like an orchestra conductor or military general. She's behind the scenes managing resources. Some power is explicitly granted to her, but a lot of her ability to get things done comes from the respect & cooperation of her subordinates.

In more technical terms, the event-loop contains a queue of Tasks to be run. Some Tasks are added directly by you, and some indirectly by asyncio. The event-loop pops a Task from the queue and invokes it (or gives it control), similar to a context-switch or calling a function. That Task then runs. Once it pauses or completes, it returns control to the event-loop. The event-loop then pops and invokes the next Task in its' queue. This process repeats indefinitely. Even if the queue is empty, the event-loop continues to cycle (somewhat aimlessly).

Effective overall execution relies on Tasks sharing well. A greedy task could hog control and leave the other tasks to starve rendering the overall event-loop approach rather useless. 

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

The underlying hardware responsible for performing the network request and placing the response-bytes into main-memory can run seperately from the CPU. Fundamentally, that is what enables or makes-possible the asynchronous behavior we desire. But, it's all for nothing if we don't let the CPU something do something in the meantime.

In this case, we want to let the CPU focus on other activities after we call `db.get(user_id)`. Then, have the CPU come back once the networking hardware has done its' part.

To accomplish that we'll cede control from our coroutine to the event-loop after calling `db.get(user_id)`. The event-loop then creates a new Task, that we'll refer to as a watcher-task (though that's not official lingo by any means), with some important responsibilities. That watcher-task will check on the db-request to see if it's done. And it'll keep note of how to resume the `get_user_info` coroutine from where it was paused.

Each time the event-loop iterates over its' queue of tasks, the watcher-task will be run and check how the db-request is getting along. After say 6 cycles through the event-loop, the watcher-task finally sees that the db-request has completed. So, it grabs the result of that request, and adds another Task to the queue to resume the `get_user_info` coroutine with the db-request result. 

## Conceputal Overview Part 2: the nuts & bolts

#### coroutine.send(), await, yield & StopIteration

`coroutine.send(arg)` is the fundamental method used to start or resume a coroutine. 

If the coroutine was paused and is now being resumed, the argument `arg` will be sent in as the return-value of the `yield` statement which originally paused it. When starting a coroutine, or when there's no value to send in, you can use `coroutine.send(None)`. The code snippet below illustrates both ways of using `coroutine.send(arg)`.

`yield` pauses execution and returns control to the caller. In the example below, the caller is `... = await custom_awaitable` on line 12. Generally, `await` calls the `__await__` method of the given object and then percolates any yields it receives up the call-chain, in this case, that's back to `... = coroutine.send(None)` on line 21. 

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

#### `await`-ing Tasks, Futures & coroutines

Futures also have an important method: `__await__`. Here is the actual, entire implementation found in `asyncio.futures.Future`. It's okay if it doesn't make complete sense now, we'll go through it in detail shortly. 

```python
1  class Future:
2      ...
3      def __await__(self):
4      
5          if not self.done():
6              self._asyncio_is_future_blocking = True
7              yield self
8        
9          if not self.done():
10              raise RuntimeError("await wasn't used with future")
11        
12         return self.result()
```

Task is a subclass of Future meaning it inherits its' attributes & methods. And Task does not override Futures' `__await__` implementation. `await`-ing a Task or Future invokes that above `__await__` method and percolates the `yield` to relinquish control. 

***Unlike Tasks and Futures, `await`-ing a coroutine does not cede control!*** That is, wrapping a coroutine in a Task first, then `await`-ing it will cede control. I'm guessing that design was intentional and meant to allow the author to decide when they want to yield control versus keep it. 

```python
async def simple_func():
    ...

async def main():
    
    # This will invoke simple_func() without yielding to the event-loop.
    await simple_func()

    # This line does two things. First it instantiates the Task which will 
    # add it to the event-loops' queue. Then, it awaits the Task which will
    # hit the yield in Future.__await__ and percolate it up allowing the
    # event-loop to regain control. Eventually, the event-loop will invoke
    # simple_func().
    await Task(coro=simple_func())
```

#### Tying it all together

The actual method that invokes a Tasks' coroutine: `asyncio.tasks.Task.__step_run_and_handle_result` is about 80 lines long. For the sake of clarity, I've removed all of the edge-case error-handling, simplified some aspects and renamed it, but the core logic remains unchanged.

```python
1  class Task:
2  ...
3      def step(self):
4          try:
5              result = self.coro.send(None)
6          except StopIteration as e:
7              super().set_result(e.value)
8          else:
9              if result._asyncio_is_future_blocking is True:
10                 result._asyncio_is_future_blocking = False
11                 result.add_done_callback(self.__step)
12             elif result is None:
13                 self._loop.call_soon(self.__step)
```

We'll analyze how control flows through this example program and the methods `Task.step` & `Future.__await__`.

```python
# Filename: program.py
1  async def func():
2      print("I am func().")
3
4  async def main():
5      func_task = asyncio.Task(coro=func())
6      await func_task
7
8  loop = asyncio.new_event_loop()
9  main_task = asyncio.Task(main(), loop=loop)
10 loop.run_forever()
```

* **`program`** 
    * Line 8 creates an event-loop, line 9 creates `main_task` and adds it to the event-loop, line 10 invokes the event-loop. 
* **`event-loop`**
    * The event-loop pops `main_task` off the queue then invokes it by calling `main_task.step()`. 
* **`main_task.step`**
    * We enter the try-block on line 4 then begin the coroutine `main` on line 5. 
* **`program.main`**
    * It creates `func_task` on line 5 which also adds `func_task` to the event-loops' queue. Line 6 awaits `func_task`. 
* **`func_task.__await__`**
    * `func_task` is not done given it was just created, so we enter the first if-block on line 5. We set a flag on `func_task` on line 6, then yield `func_task` on line 7.
* **`program.main`**
    * `await` percolates the yield and the yielded value -- `func_task`.
* **`main_task.step`**
    * `result` is now `func_task`. No StopIteration was raised so the else in the try-block on line 8 executes. The attribute set on `func_task` informs us we should block `main_task` on it. A done-callback: `main_task.step` is added to the func_task.
* **`event-loop`**
    * The event-loop cycles to the next task in its queue. The event-loop pops `func_task` from its queue and invokes it by calling `func_task.step()`.
* **`func_task.step`**
    * We enter the try-block on line 4 then begin the coroutine `func` on line 5. 
* **`program.func`**
    * Control goes to the coroutine `func` on line 2. It prints, then finishes and raises a StopIteration exception.
* **`func_task.step`**
    * The StopIteration exception is caught so we go to line 7. `func_task` is marked as done. So, the done-callbacks of `func_task` i.e. (`main_task.step`) are added to the event-loops' queue.
* **`event-loop`**
    * The event-loop cycles to the next task in its queue. The event-loop pops `main_task` and resumes it by calling `main_task.step()`.

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

