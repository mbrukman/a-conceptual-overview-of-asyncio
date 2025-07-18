# Network I/O Example

Performing a database request across a network might take half a second or so, but that's ages in computer-time. Your processor could have done millions or even billions of things. The same is true for, say, requesting a website, downloading a car, loading a file from disk into memory, etc. The general theme is those are all input/output (I/O) actions.

Consider performing two tasks: requesting some information from a server and doing some computation locally. A serial approach would look like:
ping the server, idle while waiting for a response, receive the response, perform the local computation. An asynchronous approach would look like:
ping the server, do some of the local computation while waiting for a response, check if the server is ready yet, do a bit more of the local computation,
check again, etc. Basically we're freeing up the CPU to do other activities instead of scratching its belly button.

This example has a server (a separate, local process) compute the sum of many samples from a Gaussian (i.e. normal) distribution. And the local
computation finds the sum of many samples from a uniform distribution. As you'll see, the asynchronous approach runs notably faster, since 
progress can be made on computing the sum of many uniform samples, while waiting for the server to calculate and respond.

The entirety of the implementation is shown at the bottom, copied directly from the `./barebones-network-io-example/` directory. First, here's
the output provided by each script.

## Serial output
```bash
 $ python serial_approach.py
Beginning server_request.
====== Done server_request. total: -2869.04. Ran for: 2.77s. ======
Beginning uniform_sum.
====== Done uniform_sum. total: 60001676.02. Ran for: 4.77s. ======
Total time elapsed: 7.54s.
```

## Asynchronous output
```bash
 $ python async_approach.py
Beginning uniform_sum.
Pausing uniform_sum at sample_num: 26,999,999. time_elapsed: 1.01s.

Beginning server_request.
Pausing server_request. time_elapsed: 0.00s.

Resuming uniform_sum.
Pausing uniform_sum at sample_num: 53,999,999. time_elapsed: 1.05s.

Resuming server_request.
Pausing server_request. time_elapsed: 0.00s.

Resuming uniform_sum.
Pausing uniform_sum at sample_num: 80,999,999. time_elapsed: 1.05s.

Resuming server_request.
Pausing server_request. time_elapsed: 0.00s.

Resuming uniform_sum.
Pausing uniform_sum at sample_num: 107,999,999. time_elapsed: 1.04s.

Resuming server_request.
====== Done server_request. total: -2722.46. ======

Resuming uniform_sum.
====== Done uniform_sum. total: 59999087.62 ======

Total time elapsed: 4.60s.

```

## Serial script

```python
import socket
import time
import random

import server


def uniform_sum(n_samples: int) -> float:
    total = 0.0
    for _ in range(n_samples):
        total += random.random()
    
    return total

# Request and wait for server to perform a computation.
start_time = time.time()
global_start_time = start_time
client = socket.socket()
client.connect(server.SERVER_ADDRESS)
print(f"Beginning server_request.")
response = client.recv(4096)
print(f"====== Done server_request. total: {float(response.decode()):.2f}. Ran for: {time.time() - start_time:.2f}s. ======")

# Perform another computation directly.
start_time = time.time()
print(f"Beginning uniform_sum.")
total = uniform_sum(n_samples=int(1.2e8))
print(f"====== Done uniform_sum. total: {total:.2f}. Ran for: {time.time() - start_time:.2f}s. ======")


print(f"Total time elapsed: {time.time() - global_start_time:.2f}s.")
```

## Asynchronous script

```python
import socket
import asyncio
import random
import time

import server


class YieldToEventLoop:
    def __await__(self):
        yield


async def uniform_sum(n_samples: int, time_allotment: float) -> float:
    print(f"Beginning uniform_sum.")
    
    start_time = time.time()
    total = 0.0
    
    # Without chunking, the runtime savings of asyncio are more than 
    # entirely eaten up by having to check time.time() and an if-condition 
    # on every one of the many iterations of n_samples.
    n_chunks = 40
    chunk_size = int(n_samples / n_chunks)

    for chunk_idx in range(n_chunks):
        for local_idx in range(chunk_size):
            total += random.random()
            
        time_elapsed = time.time() - start_time
        global_idx = chunk_idx * chunk_size + local_idx
        if time_elapsed > time_allotment:
            print(f"Pausing uniform_sum at sample_num: {global_idx:,}. time_elapsed: {time_elapsed:.2f}s.\n")
            await YieldToEventLoop()
            print("Resuming uniform_sum.")
            start_time = time.time()
    
    # Ensure any remainder is processed.
    for _ in range(chunk_size * n_chunks, n_samples):
        total += random.random()

    print(f"====== Done uniform_sum. total: {total:.2f} ====== \n")


async def server_request() -> float:
    print(f"Beginning server_request.")
    
    start_time = time.time()
    client = socket.socket()
    client.connect(server.SERVER_ADDRESS)
    client.setblocking(False)
    
    while True:
        try:
            response = client.recv(4096)
            break
        except BlockingIOError:
            print(f"Pausing server_request. time_elapsed: {time.time() - start_time:.2f}s.\n")
            await YieldToEventLoop()
            print(f"Resuming server_request.")
            start_time = time.time()

    print(f"====== Done server_request. total: {float(response.decode()):.2f}. ====== \n")

async def main():
    task1 = asyncio.Task(uniform_sum(n_samples=int(1.2e8), time_allotment=1.0))
    task2 = asyncio.Task(server_request())
    await task1, task2
    

if __name__ == "__main__":
    start_time = time.time()
    
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(main())
    
    print(f"Total time elapsed: {time.time() - start_time:.2f}s.")
```

## Server code

```python
import socket
import random


def gaussian_sum(n_samples: int) -> float:
    total = 0.0
    for _ in range(n_samples):
        total += random.gauss()
    
    return total

SERVER_ADDRESS = ("127.0.0.1", 8197)

if __name__ == "__main__":
    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)

    max_queue_length = 1024
    server.listen(max_queue_length)
    print(f"Server is running and listening on: {SERVER_ADDRESS}.")

    while True:
        conn, _ = server.accept()
        print(f"Processing new connection: {conn}.")
        
        total = gaussian_sum(n_samples=int(1e7))
        conn.send(f"{total}".encode())
        print(f"Done. Closing connection: {conn}.\n")
        conn.close()
```

### [Next: When to use asyncio & closing thoughts](https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/main/5-conclusions.md)