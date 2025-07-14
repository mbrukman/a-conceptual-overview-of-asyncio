## Conceputal Overview Part 2: The Nuts & Bolts

#### coroutine.send(), await, yield & StopIteration

`asyncio` leverages those 4 components to pass around control.

`coroutine.send(arg)` is the method used to start or resume a coroutine. 

If the coroutine was paused and is now being resumed, the argument `arg` will be sent in as the return value of the `yield` statement which originally paused it. When starting a coroutine, or when there's no value to send in, you can use `coroutine.send(None)`. The code snippet below illustrates both ways of using `coroutine.send(arg)`.

`yield` pauses execution and returns control to the caller. In the example below, the caller is `... = await custom_awaitable` on line 12. Generally, `await` calls the `__await__` method of the given object. `await` also does one more very special thing: it percolates any yields it receives up the call-chain. In this case, that's back to `... = coroutine.send(None)` on line 16. 

The coroutine resumes due to the `coroutine.send(42)` on line 21. The coroutine picks back up from where it yielded/paused on line 3 and executes the remaining statements in its' body. When a coroutine finishes it raises a `StopIteration` exception with the return value attached to the exception.

```python
1   class Rock:
2       def __await__(self):
3           value_sent_in = yield 7
4           print(f"Rock.__await__ resuming with value: {value_sent_in}.")
5           return value_sent_in
6   
7   async def main():
8       print("Beginning coroutine main().")
9       rock = Rock()
10      print("Awaiting rock...")
11      value_from_rock = await rock
12      print(f"Coroutine received value: {value_from_rock} from rock.")     
13      return 23
14  
15  coroutine = main()
16  intermediate_result = coroutine.send(None)
17  print(f"Coroutine paused and returned intermediate value: {intermediate_result}.")
18   
19  print(f"Resuming coroutine and sending in value: 42.")
20  try:
21      coroutine.send(42)
22  except StopIteration as e:
23      returned_value = e.value
24  print(f"Coroutine main() finished and provided value: {returned_value}.")
```

That snippet produces this output:
```
Beginning coroutine main().
Awaiting rock...
Coroutine paused and returned intermediate value: 7.
Resuming coroutine and sending in value: 42.
Rock.__await__ resuming with value: 42.
Coroutine received value: 42 from rock.
Coroutine main() finished and provided value: 23.
```

It's worth pausing for a moment here and making sure you followed the various ways control flow and values were passed.

The only way to yield (or effectively cede control) from a coroutine is to `await` an object that `yield`s in its `__await__` method. That might sound odd to you. Frankly, it was to me too. You might be thinking:
1. What about a `yield` directly within the coroutine? The coroutine becomes a generator-coroutine, a different beast entirely.
2. What about a `yield from` within the coroutine to a function that `yield`s (i.e. plain generator)? SyntaxError: `yield from` not allowed in a coroutine. I imagine Python made this a SyntaxError to mandate only one way of using coroutines for the sake of simplicity. Ideologically, `yield from` and `await` are very similar.

#### Futures

A future is an object meant to represent a computation or process's status and result (if any), hence the term future i.e. still to come or not yet happened. 

A future has a few important attributes. One is its' state which can be either 'pending', 'cancelled' or 'done'. Another is its' result which is set when the state transitions to 'done'. To be clear, a Future does not represent the actual computation to be done, like a coroutine does, instead it represents the status and result of that computation, kind of like a status-light (red, yellow or green) or indicator. Finally, a future stores callbacks or functions it should call once its' state becomes 'done'.

Here's that same description roughly stated in code:

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

Futures have an important method: `__await__`. Here is the actual, entire implementation found in `asyncio.futures.Future`. It's okay if it doesn't make complete sense now, we'll go through it in detail in the control-flow example.

```python
1  class Future:
2      ...
3      def __await__(self):
4      
5          if not self.done():
6              yield self
7        
8          if not self.done():
9              raise RuntimeError("await wasn't used with future")
10        
11         return self.result()
```

Task is a subclass of Future meaning it inherits its attributes & methods. Task does not override Futures `__await__` implementation. `await`-ing a Task or Future invokes that above `__await__` method and percolates the `yield` on line 7 above to relinquish control to its caller, which is generally the event-loop.

***Unlike Tasks and Futures, `await`-ing a coroutine does not cede control!*** That is, wrapping a coroutine in a Task first, then `await`-ing it will cede control. Frankly, I'm not sure why that design decision was made and can't see a particularly compelling 
reason for it. If you do, please let me know!

```python
async def db_request():
    ...

async def main():
    
    # This will invoke db_request() without yielding to the event-loop.
    await db_request()

    # This line does two things. First it instantiates the Task which will 
    # add it to the event-loops' queue. Then, it awaits the Task which will
    # hit the yield in Future.__await__ and percolate it up allowing the
    # event-loop to regain control (since the event-loop invoked the main() 
    # coroutine). Eventually, the event-loop will invoke db_request().
    await Task(coro=db_request())
```
