#### Analyzing an example programs control flow

The actual method that invokes a Tasks' coroutine: `asyncio.tasks.Task.__step_run_and_handle_result` is about 80 lines long. For the sake of clarity, I've removed all of the edge-case error-handling, simplified some aspects and renamed it, but the core logic remains unchanged.

```python
1  class Task:
2  ...
3      def step(self):
4          try:
5              yielded_value = self.coro.send(None)
6          except StopIteration as e:
7              super().set_result(e.value)
8          else:
9              if yielded_value._asyncio_is_future_blocking is True:
10                 yielded_value._asyncio_is_future_blocking = False
11                 yielded_value.add_done_callback(self.__step)
12             ...
```

For reference, here's the Future.__await__() method again.
```python
1  class Future:
2      ...
3      def __await__(self):
4      
5          if not self.done():
6              self._asyncio_is_future_blocking = True
7              yield self
8        
9          if not self.done():
10              raise RuntimeError("await wasn't used with future")
11        
12         return self.result()
```

We'll analyze how control flows through this example program: `program.py` and the methods `Task.step` & `Future.__await__`.

```python
# Filename: program.py
1  async def triple(val: int):
2      return val * 3
3
4  async def main():
5      triple_task = asyncio.Task(coro=triple(val=5))
6      tripled_val = await triple_task
7      return tripled_val + 2
8
9  loop = asyncio.new_event_loop()
10  main_task = asyncio.Task(main(), loop=loop)
11 loop.run_forever()
```

1. Control begins in **`program.py`** 
    * Line 9 creates an event-loop, line 10 creates `main_task` and adds it to the event-loop, line 11 invokes the event-loop. 
1. Control is now in the **`event-loop`**
    * The event-loop pops `main_task` off the queue then invokes it by calling `main_task.step()`. 
1. Control is now in **`main_task.step`**
    * We enter the try-block on line 4 then begin the coroutine `main` on line 5. 
1. Control is now in **`program.main`**
    * It creates `triple_task` on line 5 which also adds `triple_task` to the event-loops' queue. Line 6 awaits `triple_task`. Recall, that calls `__await__` then percolates and yields.
1. Control is now in **`triple_task.__await__`**
    * `triple_task` is not done given it was just created, so we enter the first if-block on line 5. We set a flag on `triple_task` on line 6, then yield `triple_task` on line 7.
1. Control is now in **`program.main`**
    * `await` percolates the yield and the yielded value -- `triple_task`.
1. Control is now in **`main_task.step`**
    * `yielded_value` is now `triple_task`. No StopIteration was raised so the else in the try-block on line 8 executes. The attribute set on `triple_task` informs us we should block `main_task` on it. A done-callback: `main_task.step` is added to the `triple_task`. The `step` method ends and returns to the event-loop.
1. Control is now in the **`event-loop`**
    * The event-loop cycles to the next task in its queue. The event-loop pops `triple_task` from its queue and invokes it by calling `triple_task.step()`.
1. Control is now in **`triple_task.step`**
    * We enter the try-block on line 4 then begin the coroutine `triple` on line 5. 
1. Control is now in **`program.triple`**
    * Control goes to the coroutine `triple` on line 2. It computes 3 times 5, then finishes and raises a StopIteration exception.
1. Control is now in **`triple_task.step`**
    * The StopIteration exception is caught so we go to line 7. The return value of the coroutine `main` is embedded in the `value` attribute of that exception. That result is saved to `triple_task` and `triple_task` is marked as done. The done-callbacks of `triple_task` i.e. (`main_task.step`) are added to the event-loops' queue. The `step` method ends and returns control to the event-loop.
1. Control is now in the **`event-loop`**
    * The event-loop cycles to the next task in its queue. The event-loop pops `main_task` and resumes it by calling `main_task.step()`.
1. Control is now in **`main_task.step`**
    * We enter the try-block on line 4 then resume the coroutine `main` from where it yielded.
1. Control is now in **`triple_task.__await__`**
    * We evaluate the if-statement on line 9 which ensures that `triple_task` is completed. Then, it returns the `result` of `triple_task` which was saved earlier. Finally that `result`
    is returned to the caller (i.e. `... = await triple_task`).
1. Control is now in **`program.main`** 
    * `tripled_val` is now 15. The coroutine finishes and raises a StopIteration exception with the return value of 17 attached.
1. Control is now in **`main-task.step`** 
    * The StopIteration exception is caught and `main_task` is marked as done and its result is saved. The `step` method end and returns control to the event-loop.
1. Control is now in the **`event-loop`** 
    * There's nothing in the queue. The event-loop cycles aimlessly onwards.

Here's another way of writing out that control-flow. 
```
program
    event-loop
        main_task.step
            program.main
                func_task.__await__
            program.main
        main_task.step
    event-loop
        func_task.step
            program.func
        func_task.step
    event-loop
        main_task.step 
            program.main
        main_task.step
    event-loop
```