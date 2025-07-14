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