## Conceputal Overview Part 2: The Nuts & Bolts

#### coroutine.send(), await, yield & StopIteration

`asyncio` leverages these 4 components to pass around control.

`coroutine.send(arg)` is the fundamental method used to start or resume a coroutine. 

If the coroutine was paused and is now being resumed, the argument `arg` will be sent in as the return-value of the `yield` statement which originally paused it. When starting a coroutine, or when there's no value to send in, you can use `coroutine.send(None)`. The code snippet below illustrates both ways of using `coroutine.send(arg)`.

`yield` pauses execution and returns control to the caller. In the example below, the caller is `... = await custom_awaitable` on line 12. Generally, `await` calls the `__await__` method of the given object and then percolates any yields it receives up the call-chain, in this case, that's back to `... = coroutine.send(None)` on line 21. 

Then, we resume the coroutine with `coroutine.send(42)` on line 26. The coroutine picks back up from where it yielded/paused on line 3. Finally, the coroutine executes the remaining statements in its' body. When a coroutine finishes it raises a `StopIteration` exception with the return-value attached to the exception.

```python
1  class CustomAwaitable:
2      def __await__(self):
3          value_sent_in = yield 7
4          print(f"Awaitable resumed with value: {value_sent_in}.")
5          return value_sent_in
6 
7  async def simple_func():
8      print("Beginning coroutine simple_func().")
9      custom_awaitable = CustomAwaitable()
10     print("Awaiting custom_awaitable...")
11    
12     value_from_awaitable = await custom_awaitable
13     print(f"Coroutine received value: {value_from_awaitable} from awaitable.")     
14     return 23
15
16  # Create the coroutine.
17  coroutine = simple_func()
18  
19  # Begin the coroutine. Store any results yielded or returned by the coroutine into
20  # variable: coroutine_intermediate_result.
21  coroutine_intermediate_result = coroutine.send(None)
22  print(f"Coroutine paused and returned intermediate value: {coroutine_intermediate_result}.")
23  
24  # Resume the coroutine and pass in the number 42 when doing so. 
25  print(f"Resuming coroutine and sending in value: 42.")
26  try:
27      coroutine.send(42)
28  except StopIteration as e:
29      returned_value = e.value
30  print(f"Coroutine finished and provided value: {returned_value}.")
```

That snippet produces this output:
```
Beginning coroutine simple_func().
Awaiting custom_awaitable...
Coroutine paused and returned intermediate value: 7.
Resuming coroutine and sending in value: 42.
Awaitable resumed with value: 42.
Coroutine received value: 42 from awaitable.
Coroutine finished and provided value: 23.
```

The only way to yield (or effectively cede control) from a coroutine is to `await` an object that `yield`s in its `__await__` method. That might sound odd to you. Frankly, it was to me too. 
1. What about a `yield` directly within the coroutine? The coroutine becomes a generator-coroutine, a different beast entirely. I address generator-coroutines in the Appendix if you're curious.
2. What about a `yield from` within the coroutine to a function that `yield`s (i.e. plain generator)? SyntaxError: `yield from` not allowed in a coroutine. I believe Python made this a SyntaxError to mandate only one way of using coroutines for the sake of simplicity. Ideologically, `yield from` and `await` are very similar.

#### Futures

A future is an object meant to represent a computation or process's status and result (if any), hence the term future i.e. still to come or not yet happened. 

A future has a few important attributes. One is its' state which can be either 'pending', 'cancelled' or 'done'. Another is its' result which is set when the state transitions to 'done'. To be clear, a Future does not represent the actual computation to be done, like a coroutine does, instead it represents the status and result of that computation, kind of like a status-light (red, yellow or green) or indicator. Finally, a future stores callbacks or functions it should call once its' state becomes 'done'.

Here's that same description stated in code:

```python
class Future:
    def __init__(self):
        self.state = 'pending'
        self.result = None
        self.callbacks = []
    
    def done(self) -> bool:
        is_future_done = self.state == 'done'
        return is_future_done

    def add_callback(self, fn: typing.Callable):
        self.callbacks.append(fn)

    def mark_done(self, result):
        self.state = 'done'
        self.result = result
        for callback in self.callbacks:
            callback()
```

#### `await`-ing Tasks, Futures & coroutines

Futures also have an important method: `__await__`. Here is the actual, entire implementation found in `asyncio.futures.Future`. It's okay if it doesn't make complete sense now, we'll go through it in detail shortly. 

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

Task is a subclass of Future meaning it inherits its' attributes & methods. And Task does not override Futures' `__await__` implementation. `await`-ing a Task or Future invokes that above `__await__` method and percolates the `yield` to relinquish control. 

***Unlike Tasks and Futures, `await`-ing a coroutine does not cede control!*** That is, wrapping a coroutine in a Task first, then `await`-ing it will cede control. I'm guessing that design was intentional and meant to allow the author to decide when they want to yield control versus keep it. 

```python
async def simple_func():
    ...

async def main():
    
    # This will invoke simple_func() without yielding to the event-loop.
    await simple_func()

    # This line does two things. First it instantiates the Task which will 
    # add it to the event-loops' queue. Then, it awaits the Task which will
    # hit the yield in Future.__await__ and percolate it up allowing the
    # event-loop to regain control. Eventually, the event-loop will invoke
    # simple_func().
    await Task(coro=simple_func())
```
