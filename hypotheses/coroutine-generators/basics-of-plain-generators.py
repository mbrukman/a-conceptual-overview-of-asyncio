import collections.abc
import asyncio

def plain_func():
    return 5

def generator_func():
    yield 1
    yield 2

async def can_you_await_a_generator():
    generator = generator_func()
    await generator

print()
print(f"{type(generator_func) = }")
print(f"{type(plain_func) = }")
print()

generator = generator_func()
print(f"{type(generator) = }")
print(f"{isinstance(generator, collections.abc.Iterator) = }")
print()

print(f"{next(generator) = }")
print()

print(f"{generator = }")
print(f"{iter(generator) = }")
print()

print(f"{generator.send(None) = }")

asyncio.run(can_you_await_a_generator())