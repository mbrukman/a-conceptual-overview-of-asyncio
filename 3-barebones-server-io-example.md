### Network I/O Example

Performing a database request across a network might take half a second or so, but that's ages in computer-time. Your processor could have done millions or even billions of things. The same is true for, say, requesting a website, downloading a car, loading a file from disk into memory, etc. The general theme is those are all input/output (I/O) actions.

Consider performing two tasks: requesting some information from a server and doing some computation locally. A serial approach would look like:
ping the server, idle while waiting for a response, receive the response, perform the local computation. An asynchronous approach would look like:
ping the server, do some of the local computation while waiting for a response, check if the server is ready yet, do a bit more of the local computation,
check again, etc. Basically we're freeing up the CPU to do other activities instead of just idling away waiting on other systems.

This example has a server (a separate, local process) compute the sum of many samples from a Gaussian (i.e. normal) distribution. And the local
computation finds the sum of many samples from a uniform distribution. As you'll see, the asynchronous approach runs notably faster, since 
progress can be made on computing the sum of many uniform samples, while waiting for the server to compute the sum of many normal samples.

The entirety of the implementation is shown at the bottom, copied directly from the server-compute-example directory. First, here's
the output provided by each script.

#### Serial output
```bash
 $ python serial_approach.py
Beginning server_request.
====== Done server_request. total: -98.57. Ran for: 2.79s. ======
Beginning uniform_sum.
====== Done uniform_sum. total: 59996185.06. Ran for: 4.75s. ======
Total time elapsed: 7.54s.
```

#### Asynchronous output
```bash
 $ p async_approach.py
Beginning uniform_sum.
Pausing uniform_sum at: 26,999,999. time_elapsed: 1.04s.

Beginning server_request.
Pausing server_request. time_elapsed: 0.00s.

Resuming uniform_sum.
Pausing uniform_sum at: 53,999,999. time_elapsed: 1.05s.

Resuming server_request.
Pausing server_request. time_elapsed: 0.00s.

Resuming uniform_sum.
Pausing uniform_sum at: 80,999,999. time_elapsed: 1.05s.

Resuming server_request.
Pausing server_request. time_elapsed: 0.00s.

Resuming uniform_sum.
Pausing uniform_sum at: 107,999,999. time_elapsed: 1.04s.

Resuming server_request.
====== Done server_request. total: 3242.14. ======

Resuming uniform_sum.
====== Done uniform_sum. total: 60002169.76 ======

Total time elapsed: 4.64s.
```

#### Serial script

https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/f76dd13a34a1a9bcc5a6467f922adb9c76ef6673/server-compute-example/serial_approach.py#L1-L30

#### Asynchronous script

https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/f76dd13a34a1a9bcc5a6467f922adb9c76ef6673/server-compute-example/async_approach.py#L1-L78

#### Server code

https://github.com/anordin95/a-conceptual-overview-of-asyncio/blob/f76dd13a34a1a9bcc5a6467f922adb9c76ef6673/server-compute-example/server.py#L1-L29