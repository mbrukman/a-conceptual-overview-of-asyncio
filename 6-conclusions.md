# When should you use asyncio?

There's generally three options to choose from when it comes to concurrent programming: multi-processing,
multi-threading & asyncio.

## Multi-processing

For any computationally bound work in Python, you likely want to use multiprocessing. Otherwise, the Global 
Interpreter Lock (GIL) will get in your way! For those who don't know, the GIL is a lock which ensures only 
one Python instruction is executed at a time. Of course, since processes are generally entirely independent
from one another, the GIL in one process won't be impeded by the GIL in another process.

## Multi-threading & asyncio

Multi-threading and asyncio are much more similar in their usage for Python; they're not useful for computationally-bound
work. They are very useful for I/O bound work.

Multi-threading comes with the downside of having
to manage various thread objects. asyncio can use only a single thread to mimic multi-threading's behavior
but requires dealing with an event-loop. 

## A note about `await`

Frankly, I'm somewhat confused by the design decisions surrounding await.

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

