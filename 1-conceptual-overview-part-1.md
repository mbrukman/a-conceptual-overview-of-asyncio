# Conceputal Overview Part 1: A Mental Model

## Event Loop

Everything in asyncio happens relative to the event-loop. It's the star of the show and there's only one. It's kind of like an orchestra conductor or military general. She's behind the scenes managing resources. Some power is explicitly granted to her, but a lot of her ability to get things done comes from the respect & cooperation of her subordinates.

In more technical terms, the event-loop contains a queue of Tasks to be run. Some Tasks are added directly by you, and some indirectly by asyncio. The event-loop pops a Task from the queue and invokes it (or gives it control), similar to calling a function. That Task then runs. Once it pauses or completes, it returns control to the event-loop. The event-loop then pops and invokes the next Task in its' queue. This process repeats indefinitely. Even if the queue is empty, the event-loop continues to cycle (somewhat aimlessly).

Effective overall execution relies on Tasks sharing well. A greedy task could hog control and leave the other tasks to starve rendering the overall event-loop approach rather useless. 

```python
import asyncio

# This creates an event-loop and indefinitely cycles through its' queue of tasks.
event_loop = asyncio.new_event_loop()
event_loop.run_forever()
```

## Asynchronous Functions & Coroutines

This is a regular 'ol Python function.
```python
def hello_printer():
    print(
        "Hi, I am a lowly, simple printer, though I have all I "
        "need in life -- fresh paper & a loving octopus-wife."
    )
```

Calling a regular function invokes its' logic or body. 
```python
>>> hello_printer()
Hi, I am simple_print(), a lowly, simple printer, though I have all I need in life -- fresh paper & a loving octopus-wife.
>>>
```

This is an asynchronous-function or coroutine-function.
```python
async def special_fella(magic_number: int):
    print(
        "I am a super special function. Far cooler than that printer. By the way, 
        f"my lucky number is: {magic_number}."
    )
```

Calling an asynchronous function creates and returns a coroutine object. Note it does not execute the function.
```python
>>> special_fella(magic_number=3)
<coroutine object special_fella at 0x104ed2740>
>>> 
```

The terms "asynchronous function" (or "coroutine function") and "coroutine object" are often conflated as coroutine. I find that a tad confusing. In this article, coroutine will exclusively mean "coroutine object" -- the thing produced by executing a coroutine function.

That coroutine represents the function's body or logic. A coroutine has to be explicitly started; again, merely creating the coroutine does not start it. Notably, the coroutine can be paused & resumed. That pausing & resuming ability is what allows
for asynchronous behavior!

## Tasks

Roughly speaking, Tasks are coroutines tied to an event-loop. A Task also maintains a list of callback functions whose importance will become clear in a moment when we discuss `await`. 

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

## `await`

await is a Python keyword that's commonly used in one of two different ways:
```python
await coroutine
await task
```

Unfortunately, it actually does matter which type of object await is applied to.

await-ing a coroutine will immediately invoke that coroutine. Control will **not** be ceded 
to the event-loop. The behavior of `await coroutine` is effectively the same as invoking a regular Python function.

await-ing a task is different. It cedes control to the event-loop, and adds a callback to the awaited task indicating
it should resume this task when its done. In practice, it's slightly more convoluted, but not by too much. If you take the red pill Neo (that is, read part 2), you'll 
see the details that make this possible.