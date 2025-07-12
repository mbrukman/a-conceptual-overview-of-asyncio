import time
import asyncio
import random

import aiofiles
import pandas as pd
from pathlib import Path


async def read_db():
    async with aiofiles.open("candy-database", "r") as afh:
        db = await afh.read()
    
    return db

async def compute_cumulative_sum(n: int):
    sum = 0
    
    # Set this value with some trial & error.
    num_yields = 7
    yield_period = int(n / num_yields)

    for val in range(1, n):
        sum += val

        if val % yield_period == 0:
            await asyncio.sleep(0)

    return sum

async def time_many_runs(num_runs: int):
    
    results_filename = f"timing_results_of_{num_runs}_runs.csv"
    if Path(results_filename).exists():
        raise Exception(f"{results_filename} already exists! Terminating.")

    run_results = []
    for run_idx in range(num_runs):
        # Randomize which trial is run first each time.
        run_async_first = random.random() > 0.5

        if run_async_first:
            
            async_start_time = time.time()
            aggregate_future = asyncio.gather(read_db(), compute_cumulative_sum(n=int(1e7)))
            await aggregate_future
            async_end_time = time.time()

            sync_start_time = time.time()
            await read_db()
            await compute_cumulative_sum(n=int(1e7))
            sync_end_time = time.time()
        
        else:
            sync_start_time = time.time()
            await read_db()
            await compute_cumulative_sum(n=int(1e7))
            sync_end_time = time.time()

            async_start_time = time.time()
            aggregate_future = asyncio.gather(read_db(), compute_cumulative_sum(n=int(1e7)))
            await aggregate_future
            async_end_time = time.time()

        async_time_elapsed = async_end_time - async_start_time
        sync_time_elapsed = sync_end_time - sync_start_time

        run_result = (run_idx, run_async_first, sync_time_elapsed, async_time_elapsed)
        run_results.append(run_result)

    run_results_df = pd.DataFrame(run_results, columns=["run_idx", "async_ran_first", "sync_time_elapsed", "async_time_elapsed"])
    run_results_df.to_csv(results_filename, index=False)

res = asyncio.run(time_many_runs(1_000))