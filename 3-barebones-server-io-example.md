#### Network I/O Example

Performing a database request across a network might take half a second or so, but that's ages in computer-time. Your processor could have done millions or even billions of things. The same is true for, say, requesting a website, downloading a car, loading a file from disk into memory, etc. The general theme is those are all input/output (I/O) actions.

Consider performing two tasks: requesting some information from a server and doing some computation locally. A serial approach would look like:
ping the server, idle while waiting for a response, receive the response, perform the local computation. An asynchronous approach would look like:
ping the server, do some of the local computation while waiting for a response, check if the server is ready yet, do a bit more of the local computation,
check again, etc.

Basically we're freeing up the CPU to do other activities instead of just idling away waiting on other systems.

The entirety of the implementation is shown below, copied directly from the server-compute-example directory. Here's
what the output of each approach looks like.

```bash
 $ python serial_approach.py
Requesting computation from server.
Server returned 1599.99. Ran for: 2.78s.
Computed total: 60004745.57 in 4.74s.
Total time elapsed: 7.52 seconds.
```


```bash
$ python async_approach.py
Beginning uniform_sum.
Pausing uniform_sum at: 26,999,999. time_elapsed: 1.03s.

Beginning server_request.
Pausing server_request.

Resuming uniform_sum.
Pausing uniform_sum at: 53,999,999. time_elapsed: 1.05s.

Resuming server_request.
Pausing server_request.

Resuming uniform_sum.
Pausing uniform_sum at: 80,999,999. time_elapsed: 1.06s.

Resuming server_request.
Pausing server_request.

Resuming uniform_sum.
Pausing uniform_sum at: 107,999,999. time_elapsed: 1.05s.

Resuming server_request.
====== Done server_request. total: -2542.28. ======

Resuming uniform_sum.
====== Done uniform_sum. total: 59999986.44 ======

Total time elapsed: 4.65s.
```


Here's what the server implementation looks like:
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

Here's the serial approach.
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
print(f"Requesting computation from server.")
response = client.recv(4096)
print(f"Server returned {float(response.decode()):.2f}. Ran for: {time.time() - start_time:.2f}s.")

# Perform another computation directly.
start_time = time.time()
total = uniform_sum(n_samples=int(1.2e8))
print(f"Computed total: {total:.2f} in {time.time() - start_time:.2f}s.")


print(f"Total time elapsed: {time.time() - global_start_time:.2f} seconds.")
```

And finally the async approach:
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
    
    # Without chunking the runtime savings of asyncio are more than 
    # entirely eaten up by having to check time.time() and an if-condition 
    # on every one of the many iterations of n_samples. In this approach
    # we only check the elapsed time against the time_allotment after each 
    # chunk.
    n_chunks = 40
    chunk_size = int(n_samples / n_chunks)

    for chunk_idx in range(n_chunks):
        for local_idx in range(chunk_size):
            total += random.random()
            
        time_elapsed = time.time() - start_time
        global_idx = chunk_idx * chunk_size + local_idx
        if time_elapsed > time_allotment:
            print(f"Pausing uniform_sum at: {global_idx:,}. time_elapsed: {time_elapsed:.2f}s.\n")
            await YieldToEventLoop()
            print("Resuming uniform_sum.")
            start_time = time.time()
    
    # Ensure any remainder is still processed.
    for _ in range(chunk_size * n_chunks, n_samples):
        total += random.random()

    print(f"====== Done uniform_sum. total: {total:.2f} ====== \n")


async def server_request() -> float:
    print(f"Beginning server_request.")

    client = socket.socket()
    client.connect(server.SERVER_ADDRESS)
    client.setblocking(False)
    
    while True:
        try:
            response = client.recv(4096)
            break
        except BlockingIOError:
            print(f"Pausing server_request.\n")
            await YieldToEventLoop()
            print(f"Resuming server_request.")

    print(f"====== Done server_request. total: {float(response.decode()):.2f}. ====== \n")

async def main():
    task1 = asyncio.Task(uniform_sum(n_samples=int(1.2e8), time_allotment=1.0))
    task2 = asyncio.Task(server_request())
    await asyncio.gather(task1, task2)
    

if __name__ == "__main__":
    start_time = time.time()
    
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(main())
    
    print(f"Total time elapsed: {time.time() - start_time:.2f}s.")
```