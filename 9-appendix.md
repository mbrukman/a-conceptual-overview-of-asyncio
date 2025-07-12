#### Asychronous generators

Asynchronous-generators or coroutine-generators are generators that yield coroutines. 

``` python
# This is a coroutine-generator-function. Calling it 
# produces a coroutine-generator.
async def coroutine_generator_func():
    
    # This yield statement represents the end-point 
    # of the first awaited-coroutine that this 
    # generator-coroutine will produce. It implicitly
    # raises a StopIteration exception.
    yield 1
    
    # The second returned coroutine will begin just after
    # the prior-yield. And end at the following yield 
    # below. Again, the yield will raise a StopIteration 
    # exception.
    yield 2

    # The third returned coroutine will follow a similar
    # pattern.
    yield 3

# For review, this is a coroutine-function. Calling it 
# produces a coroutine.
async def coroutine_func():
    await other_coroutine
    return
```

I believe they're meant to be useful for situations like this. 

```python
async def read_file_in_chunks(file):
    while chunk != EOF
        chunk = await read_file_chunk(file)
        yield chunk

async for chunk in read_file_in_chunks(file):
    ...
```

Personally, I find coroutine-generators a bit redundant, questionably useful & rather confusing. They're meant to serve as iterators and save boilerplate by implementing \_\_aiter\_\_ and \_\_anext\_\_ (the asynchronous analogues of \_\_next\_\_ and \_\_iter\_\_). I couldn't find any meaningful online articles about them, besides the [Python Enhancement Proposal (PEP)](https://peps.python.org/pep-0525/) which introduced them.

I don't see why plain-coroutines can't fill the iterator role given they can already pause & yield values. Why not allow plain-coroutines to yield in their body and add an \_\_anext\_\_ method to the parent-class which just returns the coroutine. To iterate over the coroutine and receive values you just repeatedly await or .send on it. 

Though, take my perspective with a grain (or many grains) of salt; there's a decent chance I'm missing something! If you know that something, please let me know!



### Links 

A good overview of the fundamental Python language features asyncio uses. 
https://stackoverflow.com/questions/49005651/how-does-asyncio-actually-work

Good context and basic-intro to asyncio. In my experience, Real Python is generally excellent quality.
https://realpython.com/async-io-python/

I only skimmed this, but I found the example program at the end very useful to pull apart.
https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/

A good answer to a specific question about why coroutine generators exist.
https://stackoverflow.com/questions/46203876/what-are-the-differences-between-the-purposes-of-generator-functions-and-asynchr

