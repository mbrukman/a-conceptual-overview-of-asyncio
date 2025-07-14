### When should you use asyncio?

There's generally three options to choose from when it comes to concurrent programming: multi-processing,
multi-threading & asyncio.

For any computationally bound work in Python, you likely want to use multiprocessing. Otherwise, the Global 
Interpreter Lock (GIL) will get in your way! For those who don't know, the GIL is a lock which ensures only 
one Python instruction is executed at a time. Of course, since processes are generally entirely independent
from one another, the GIL in one process won't have issues with the GIL in another process.

Multi-threading and asyncio are much more similar. Multi-threading comes with the downside of having
to manage various thread objects. asyncio can use only a single thread to mimic multi-threading's behavior
but requires dealing with an event-loop. 

`async`: A Python-language keyword that marks a function as a coroutine-function; you can also think of 
that as a coroutine-factory. When invoked a coroutine-factory produces a coroutine object. That object
can be paused & resumed. 

`await {coroutine}`: Directly invokes the coroutine. This is basically the same as invoking a regular function.

`await {task/future}`: Cedes control to the event-loop. Control will resume at this point sometime after the relevant
task or future is finished.

Frankly, I'm somewhat confused by the design decisions surrounding await.

If I had the paint-brush, I'd make await a standalone statement that cedes control to the event-loop. 