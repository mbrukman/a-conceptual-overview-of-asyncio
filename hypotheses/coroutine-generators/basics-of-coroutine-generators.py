import collections.abc
import typing

import warnings
# This is admittedly overkill, but silence the asyncio never-awaited warnings.
warnings.filterwarnings("ignore")

async def plain_coroutine_func():
    return 5

async def generator_coroutine_func():
    # This yield statement represents the end-point of the first awaited-coroutine that
    # this generator-coroutine will produce. It implicitly raises a StopIteration exception.
    print("a")
    yield 1
    
    # The second returned coroutine will begin just after the prior-yield. And end
    # at the following yield below. Again, the yield will raise a StopIteration exception.
    print("b")
    yield 2

    # The third returned coroutine will follow a similar pattern.
    print("c")
    yield 4

    # The fourth returned coroutine will end after the final statement, then
    # implicitly raise a StopAsyncIteration exception.
    print("d")

coroutine = plain_coroutine_func()
generator_coroutine = generator_coroutine_func()

print(f"{type(plain_coroutine_func) = }")
print(f"{type(generator_coroutine_func) = }")
print()

print(f"{type(coroutine) = }")
print(f"{isinstance(coroutine, collections.abc.Generator) = }")
print(f"{type(generator_coroutine) = }")
print()

# TypeError: 'coroutine' object is not an iterator.
# next(coroutine)
# TypeError: 'async_generator' object is not an iterator.
# next(generator_coroutine)
# TypeError: 'coroutine' object is not an async iterator
# anext(coroutine)
print(f"{anext(generator_coroutine) = }")
print(f"{type(anext(generator_coroutine)) = }")
print()

print(f"{isinstance(anext(generator_coroutine), collections.abc.Generator) = }")
print(f"{isinstance(anext(generator_coroutine), collections.abc.Iterator) = }")
print(f"{isinstance(anext(generator_coroutine), collections.abc.Awaitable) = }")
print(f"{isinstance(anext(generator_coroutine), collections.abc.Coroutine) = }")
print()

print(f"{aiter(generator_coroutine) = }")
print(f"{generator_coroutine = }")
print()

def invoke_generator_coroutine(generator_coroutine: typing.AsyncGenerator):
    next_coroutine = anext(generator_coroutine)
    try:
        print(f"Beginning coroutine: {next_coroutine}.")
        next_coroutine.send(None)
    except StopIteration as exception:
        print(f"coroutine: {next_coroutine} ran and produced: {exception.value}")
    except StopAsyncIteration as exception:
        print(f"The coroutine-generator is exhausted, i.e. it has no more coroutines to provide!")

invoke_generator_coroutine(generator_coroutine)
invoke_generator_coroutine(generator_coroutine)
invoke_generator_coroutine(generator_coroutine)
invoke_generator_coroutine(generator_coroutine)