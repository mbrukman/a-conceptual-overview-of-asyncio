import collections.abc
import asyncio

# This is a generator-coroutine-function. 
async def stream_generator_coroutine_func():
    for num in range(100):
        yield num
        await asyncio.sleep(0.5)

# This is a coroutine-function.
async def stream_coroutine_func():
    class AwaitableIter:
        def __await__(self):
            for num in range(100):
                yield num
    
    awaitable_iter = AwaitableIter()
    await awaitable_iter
    await asyncio.sleep(0.5)

def invoke_coroutine(coroutine: collections.abc.Coroutine):
    try:
        return coroutine.send(None)
    except StopIteration as e:
        return e.value

# This is a generator-coroutine.
generator_coroutine = stream_generator_coroutine_func()

# These are both coroutines.
coroutine_from_coro_gen = anext(generator_coroutine)
coroutine_from_coro = stream_coroutine_func()

# This runs the coroutine.
result_from_gen = invoke_coroutine(coroutine_from_coro_gen)
result_from_func = invoke_coroutine(coroutine_from_coro)

print(f"{result_from_gen = }")
print(f"{result_from_func = }")