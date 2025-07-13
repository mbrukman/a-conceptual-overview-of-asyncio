## Motivation

I've used `asyncio` a couple times now, but never really felt confident in my mental-model of how it works and how I can best use it. The official `asyncio` docs provide pretty-decent documentation for each specific function in the package, but, in my opinion, lack a cohesive overview of the design and functionality to help the user make informed decisions about which tool in the `asyncio` tool-kit they ought to grab, or to recognize when `asyncio` is the entirely wrong tool-kit. This is my attempt to fill that gap. 

There were a few blog-posts, stack-overflow discussons and other writings about `asyncio` that I found helpful, but didn't fully provide what I was looking for. You can find them in the Appendix.

A few aspects particually drove my curiosity (read: drove me nuts). You should be able to answer all these questions by the end of this article.
- What's roughly happening behind the scenes when an objects is `await`-ed? 
- How does `asyncio` differentiate between a task which doesn't need cpu-time to make progress towards completion (for example a network-request or file-read) as opposed to a task that does need cpu-time to make progress (for example, computing n-factorial)?
- How does `asyncio.sleep()` run asynchronously while `time.sleep()` does not? 
- How would I go about writing my own asynchronous variant of some operation (e.g. sleep, network-request, file-read, etc.)?