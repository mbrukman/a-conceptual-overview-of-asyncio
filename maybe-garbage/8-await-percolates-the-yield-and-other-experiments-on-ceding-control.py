"""
How do I mimic the way asyncio yields to the event-loop?

1. await a custom_object with an __await__ method which calls yield.
    Success!
2. Call custom_object.__await__() to create a generator, then call next() on it.
    Does not work.
3. Call custom_object.non_await_yield_method() to create a generator then call next() on it.
    Does not work.
3. Create a generator, then call next() on it.
    Does not work. 
4. Call 'yield from' on custom_object.__await__().
    Does not work: SyntaxError: 'yield from' inside async function.

I think what I really need is 'yield from', but it's not allowed! :(

Hypothesis
    The call-flow for obj.__await__() and await obj are identical.
Experiment:
    Use ipdb to follow the execution flow of each method.
    Case 1 .__await__()
        I call next(custom_object.__await__()) from main(). 
        That __await__() method hits the yield, and returns flow 
        to the next-line of its calling function -- main().
    Case 2 await
        I call await custom_object from main().
        That __await__() method also hits the yield and returns flow,
        but to the same line which called it: 'await custom_object'. 
        Then, flow is returned to the function which called main(),
        which is Task.__step_run_and_handle_result; that's where
        coroutine.send is called in asyncio.
Result
    There is a slight difference! 
    When __await__() is invoked like 'obj.__await__()' and it yields, 
    control returns to the next-line of the caller. 
    When __await__() is invoked like 'await obj' and it yields,
    control returns to the same-line, which then returns to the 
    coro.send call in asyncio.

Conclusions
    await calls the .__await__() method and then yields any result. 
    I expect that's why control flow returns directly to the 'await obj' line 
    as opposed to the following line like it does for obj.__await__. 
    I also expect that's why it's the only approach of the five that I tried above
    which succesfully gets control back to the event-loop. It percolates the 
    __await__'s yield upwards.

    Also, a yield is crucial for giving control back to the event-loop.
    It's so odd to me that a yield is disallowed in an async function??

"""
import asyncio

class CustomAwaitable():
    def __await__(self):
        print(f"Beginning __await__ in CustomAwaitable.")
        # Bare yield relinquishes control for one event loop iteration.
        # For more context or details see asyncio/tasks.py (368).
        yield
        print(f"Done __await__ in CustomAwaitable.")

    def non_await_yield_method(self):
        print(f"Beginning non_await_yield_method in CustomAwaitable.")
        yield
        print(f"Done non_await_yield_method in CustomAwaitable.")

def bare_yield_func():
    print("Beginning bare_yield_func().")
    yield
    print("Finished bare_yield_func().")

async def simple_func():
    print("I am simple_func().")

async def main():
    print("Beginning main().")

    # 1. 
    # Invoke yield via a custom-awaitable
    # via the 'await' keyword.
    # import ipdb; ipdb.set_trace()
    # custom_awaitable = CustomAwaitable()
    # await custom_awaitable

    # 2.
    # Invoke yield via a custom-awaitable
    # directly via .__await__().
    # This does not reliquish control to the
    # event-loop!
    # custom_awaitable = CustomAwaitable()
    # gen = custom_awaitable.__await__()
    # import ipdb; ipdb.set_trace()
    # next(gen)

    # 3.
    # Invoke yield via a seperate non-async 
    # (i.e. regular) function.
    # Huh! This also doesn't relinquish control to 
    # the event-loop.
    # gen = bare_yield_func()
    # next(gen)

    # 4. 
    # Invoke yield via a custom-awaitable
    # directly via 'yield from'.
    # SyntaxError: 'yield from' inside async function
    # custom_awaitable = CustomAwaitable()
    # yield from custom_awaitable

    custom_awaitable = CustomAwaitable()
    print(f"{type(custom_awaitable.__await__) = }")
    print(f"{type(custom_awaitable.non_await_yield_method) = }")

    print(f"{type(custom_awaitable.__await__()) = }")
    print(f"{type(custom_awaitable.non_await_yield_method()) = }")

    print("Finished main().")


# This function produces coroutine objects.
# print(f"{type(simple_async_func()) = }")
async def simple_async_func():
    return 4

# This function produces asynchronous generators.
# print(f"{type(another_async_func()) = }")
async def another_async_func():
    yield 1
    yield 2
    
    # SyntaxError: 'return' with value in async generator
    # It's unclear to me (and others) why this limit is imposed. 
    # https://discuss.python.org/t/return-with-value-allowed-in-generators-but-not-async-generators/31969/3
    # return 3

loop = asyncio.new_event_loop()
main_task = asyncio.Task(main(), loop=loop)
# import ipdb; ipdb.set_trace()
loop.run_forever()