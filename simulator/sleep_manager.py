"""
Sleep Manager for Session 10 Simulator
Manages random sleep intervals to prevent API rate limiting.
"""

import random
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Load sleep configuration from environment
SLEEP_MIN = int(os.getenv("SIMULATOR_SLEEP_MIN", "1"))
SLEEP_MAX = int(os.getenv("SIMULATOR_SLEEP_MAX", "3"))
SLEEP_BATCH_MIN = int(os.getenv("SIMULATOR_SLEEP_BATCH_MIN", "3"))
SLEEP_BATCH_MAX = int(os.getenv("SIMULATOR_SLEEP_BATCH_MAX", "10"))


async def sleep_after_test():
    """
    Sleep for a random interval after each test.
    Default: 1-3 seconds
    """
    sleep_time = random.uniform(SLEEP_MIN, SLEEP_MAX)
    await asyncio.sleep(sleep_time)
    return sleep_time


async def sleep_after_batch():
    """
    Sleep for a longer random interval after every 10 tests.
    Default: 3-10 seconds
    """
    sleep_time = random.uniform(SLEEP_BATCH_MIN, SLEEP_BATCH_MAX)
    await asyncio.sleep(sleep_time)
    return sleep_time

