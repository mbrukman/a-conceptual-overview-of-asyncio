import time
import asyncio
import random

import aiofiles
import pandas as pd
from pathlib import Path


async def read_db():
    start_time = time.time()
    async with aiofiles.open("candy-database", "r") as afh:
        import ipdb; ipdb.set_trace()
        db = await afh.read()
    
    print(f"read_db took: {time.time() - start_time:.2f}s.")
    return db

async def compute_cumulative_sum(n: int):
    sum = 0
    
    # Set this value with some trial & error.
    num_yields = 7
    yield_period = int(n / num_yields)

    start_time = time.time()
    for val in range(1, n):
        sum += val

        if val % yield_period == 0:
            print(f"Pausing compute_cumulative_sum() at {time.time()}.")
            await asyncio.sleep(0)
            print(f"Resuming compute_cumulative_sum() at {time.time()}.")

    print(f"compute_cumulative_sum took: {time.time() - start_time:.2f}s.")
    return sum

async def main():
    start = time.time()
    
    aggregate_future = asyncio.gather(read_db(), compute_cumulative_sum(n=int(1e7)))
    await aggregate_future

    # await read_db()
    # await compute_cumulative_sum(n=int(1e7))

    print(f"Total time elapsed: {time.time() - start: .2f}s.")

res = asyncio.run(main())