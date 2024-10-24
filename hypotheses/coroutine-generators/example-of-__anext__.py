import warnings
# This is admittedly overkill, but silence the asyncio never-awaited warnings.
warnings.filterwarnings("ignore")

class AsyncIterable:
    def __aiter__(self):
        return self

    async def coro(self):
        data = await self.fetch_data()
        return data
    
    # __anext__ is a coroutine-function. 
    # Invoking it should return the next coroutine to be run.
    async def __anext__(self):
        data = await self.fetch_data()
        if data:
            return data
        else:
            raise StopAsyncIteration

    # This example comes from PEP-492 which introduced __anext__.
    # Frankly, I don't totally like this example. fetch_data presumably
    # must rely on some internal state to provide a different coroutine
    # on each call.
    async def fetch_data(self):
        ...

async_iterable = AsyncIterable()
result = anext(async_iterable)
coro = async_iterable.coro()

print(f"{coro.send(None) =}")
print(f"{result.send(None) =}")