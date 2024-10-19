# I don't quite understand how yield is used alongside coroutines. 

# What's the rough-flow when asyncio uses yield?
# 1. event-loop calls main-task via coro.send
# 2. main-task awaits sub-task
# 3. sub-task.__await__ calls yield

# Hypothesis
#   await obj & obj.__await__() have the same effect.
# Experiment
#   await a Task and Task.__await__() and see if the execution differs.
#   await a coroutine and coroutine.__await__() and see if the execution differs.
# Results
#  coroutine.__await__() does not actually invoke the coroutine, whereas await coroutine does.
#  task.__await__() does invoke the coroutine, as does await task.



import asyncio

async def simple_func():
    print(f"Beginning simple_func().")
    print(f"Ending simple_func().")

async def main():
    simple_coroutine = simple_func()
    
    # Coroutine-test.
    # await simple_coroutine
    # simple_coroutine.__await__()

    # Task-test.
    simple_task = asyncio.Task(simple_coroutine)
    await simple_task
    # simple_task.__await__()

loop = asyncio.new_event_loop()
main_task = asyncio.Task(main(), loop=loop)
loop.run_forever()