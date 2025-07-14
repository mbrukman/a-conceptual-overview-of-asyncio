# A conceptual overview of the ideas and objects which power asyncio

## Motivation

I've used Python's asyncio a couple times now, but never really felt confident in my mental model of how it works nor how I should use it. The official docs provide decent documentation for each function in the package, but, in my opinion, lack a cohesive overview of the systems design and architecture. Something that could help the user understand the why and how behind the recommended patterns. And a way to help the user make informed decisions about which tool in the asyncio toolkit they ought to grab, or to recognize when asyncio is the entirely wrong toolkit. This is my attempt to fill that gap. 

There were some articles I found online that partially answered or helped me better understand asyncio, but didn't totally get into what I wanted to know. You can find them linked in the conclusion section.

A few aspects particually drove my curiosity (read: drove me nuts). You should be able to answer all these questions by the end of this article.
- What's roughly happening behind the scenes when an objects is `await`-ed? 
- How does `asyncio` differentiate between a task which doesn't need cpu-time to make progress towards completion (for example a network-request or file-read) as opposed to a task that does need cpu-time to make progress (for example, computing n-factorial)?
- How would I go about writing my own asynchronous variant of some operation (e.g. sleep, network-request, file-read, etc.)?

## Sections

The first and third sections feature some examples but are generally focused on theory. The second and fourth sections are examples
focused on further illustrating and reinforcing ideas practically. The final section wraps up, compares multiprocessing, multithreading & asyncio and offers some opinions on the design of await.

#### [A conceptual overview: part 1](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/1-conceptual-overview-part-1.md)

In part 1, we'll describe the main, high-level building blocks of asyncio: the event-loop, coroutine functions,
coroutine objects, tasks & await. 

#### [Barebones server example](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/4-barebones-network-io-example.md)

A simple but thorough example showing how asyncio can offer an advantage over serial programs. The example doesn't rely on 
any asyncio operators (besides the event-loop). It's all non-blocking sockets & custom awaitables that help you see what's
actually happening under the hood and illustrate how you could do something similar.

#### [A conceptual overview: part 2](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/2-conceptual-overview-part-2.md)

Part 2 goes into detail on the mechanisms asyncio uses to manage control flow. This is where the magic happens. You'll
come away from this section knowing what await does behind the scenes and how to make your own asynchronous operators.

#### [Analyzing an example programs control flow](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/3-detailed-control-flow-analysis-example.md)

We'll walkthrough, step by step, a simple asynchronous program following along in the key methods of Task & Future that are leveraged when asyncio is orchestrating the show. 

#### [multiprocessing, multithreading & asyncio and some closing thoughts]()
