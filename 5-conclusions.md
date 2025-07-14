# When should you use asyncio?

There's generally three options to choose from when it comes to concurrent programming: multi-processing,
multi-threading & asyncio.

## Multi-processing

For any computationally bound work in Python, you likely want to use multiprocessing. Otherwise, the Global 
Interpreter Lock (GIL) will generally get in your way! For those who don't know, the GIL is a lock which ensures only 
one Python instruction is executed at a time. Of course, since processes are generally entirely independent
from one another, the GIL in one process won't be impeded by the GIL in another process. I believe there are ways
to also get around the GIL in a single process by leveraging C extensions.

## Multi-threading & asyncio

Multi-threading and asyncio are much more similar in their usage for Python; they're not useful for computationally-bound
work. They are very useful for I/O bound work. And for applications that don't need to manage lots of distinct I/O connections, I think the choice between which to use is somewhat down to taste.

Multi-threading maintains a distinct OS-managed thread for each chunk of work. Whereas asyncio uses Tasks for each 
work-chunk and manages them via the event-loop's queue. I believe the marginal overhead of one more chunk of work is lower for asyncio than threads, which begins to matter for applications that need to manage many, many chunks of work. 

One slight benefit of asyncio is clearer visibility into when and where interleaving occurs. The code chunk between two awaits is certainly synchronous. Whereas with threading, the interleaving is more of a black-box. One slight benefit of multithreading is not really having to worry about greedy threads hogging execution, something that could happen with asyncio where a greedy coroutine never awaits and effectively stalls the event-loop.

## A note about `await`

Frankly, I'm somewhat confused by the design decisions surrounding await. 
If you do know or see a reason I'm missing, please let me know!

If I had the paint-brush, I'd make await a standalone statement that cedes control to the event-loop. 

## Further reading

A good overview of the fundamental Python language features asyncio uses. 
https://stackoverflow.com/questions/49005651/how-does-asyncio-actually-work

Good context and basic-intro to asyncio. In my experience, Real Python is generally excellent quality.
https://realpython.com/async-io-python/

I only skimmed this, but I found the example program at the end very useful to pull apart.
https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/

A good answer to a specific question about why coroutine generators exist.
https://stackoverflow.com/questions/46203876/what-are-the-differences-between-the-purposes-of-generator-functions-and-asynchr

