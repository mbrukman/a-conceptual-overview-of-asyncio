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
    await asyncio.gather(task1, task2)
    

if __name__ == "__main__":
    start_time = time.time()
    
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(main())
    
    print(f"Total time elapsed: {time.time() - start_time:.2f}s.")
    