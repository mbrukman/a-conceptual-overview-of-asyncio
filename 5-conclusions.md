## When should you use asyncio?

There's generally three options to choose from when it comes to concurrent programming: multi-processing,
multi-threading & asyncio.

### Multi-processing

For any computationally bound work in Python, you likely want to use multiprocessing. Otherwise, the Global 
Interpreter Lock (GIL) will generally get in your way! For those who don't know, the GIL is a lock which ensures only 
one Python instruction is executed at a time. Of course, since processes are generally entirely independent
from one another, the GIL in one process won't be impeded by the GIL in another process. Granted, I believe there are ways
to also get around the GIL in a single process by leveraging C extensions.

### Multi-threading & asyncio

Multi-threading and asyncio are much more similar in where they're useful with Python; not at all for computationally-bound
work. And very useful for I/O bound work. For applications that don't need to manage absolutely tons of distinct I/O connections, I think the choice between which to use is somewhat down to taste.

Multi-threading maintains an OS-managed thread for each chunk of work. Whereas asyncio uses Tasks for each 
work-chunk and manages them via the event-loop's queue. I believe the marginal overhead of one more chunk of work is a fair bit lower for asyncio than threads, which can matter a lot for applications that need to manage many, many chunks of work. 

There are some other benefits associated with using asyncio. One is clearer visibility into when and where interleaving occurs. The code chunk between two awaits is certainly synchronous. Another is simpler debugging, since it's easier to attach and follow a trace and reason about code execution. With threading, the interleaving is more of a black-box. One benefit of multithreading is not really having to worry about greedy threads hogging execution, something that could happen with asyncio where a greedy coroutine never awaits and effectively stalls the event-loop.

## Opinions and suggestions on certain design choices

I'm somewhat confused by a few of the design decisions in asyncio. If you do know or see a reason I'm missing for why they're beneficial, please let me know! I see two possible changes that could simplify people's experience working with asyncio. I feel much more strongly about the first one than the second.

### 1. await coroutine should be disallowed or should yield to the event-loop

When you see an `await object` statement in some codebase, you need to know whether that object is a coroutine or a task/future to understand its impact. If object is a coroutine, an asynchronous wait is not actually going to occur and the event-loop cannot intercede. I think that makes skimming a codebase harder than it needs to be and obfuscates the meaning of the await keyword.

The downside is there'd be no way to synchronously invoke a coroutine. Of course, there are already ways to synchronously invoke chunks of code: regular Python functions. I imagine the edge case where someone sometimes wants to invoke a coroutine synchronously in some places and in other places asynchronously is somewhat rare. My gut also says if an applications needs the same coroutine synchronous in some cases and asynchronous in others, there may be flaws in its broader usage of async that explain the problem. Nonetheless I think that problem could still be addressed in one of two ways: have a synchronous variant of the function or use coroutine.send(arg).

To me, simplifying and clarifying await is easily worth that minor downside.

### 2. The Task constructor should accept coroutine functions

I think one common source of confusion for folks is coroutine functions versus coroutine objects. Building off of the first suggestion, if `await coroutine` is disallowed, there will be far fewer instances of needing to work with coroutine objects or even to have them around. Instead, let the Task constructor manage creation of them. This change would also mean the stylistic approach of asyncio could match multiprocessing and multithreading -- directly passing a callable-looking object to the Process, Thread, or Task constructor. Additionally, this would remove the red-herrings that look like function calls by mimicking their notation but are instead calls to create coroutine objects.

```python
async def do_work(x, y):
    pass

def thread_target(x, y):
    pass

def main():
    t = threading.Thread(thread_target, args=(1, 2))
    t = asyncio.Task(do_work, args=(3,4))
```

## Further reading

A good overview of the fundamental Python language features asyncio uses. 
https://stackoverflow.com/questions/49005651/how-does-asyncio-actually-work

Good context and basic-intro to asyncio. In my experience, Real Python is generally excellent quality.
https://realpython.com/async-io-python/

I only skimmed this, but I found the example program at the end very useful to pull apart.
https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/

A good answer to a specific question about why coroutine generators exist.
https://stackoverflow.com/questions/46203876/what-are-the-differences-between-the-purposes-of-generator-functions-and-asynchr

