"""
Time Utilities for Session 10
Helper functions for time calculations and formatting.
"""

from datetime import datetime
from typing import Tuple


def get_current_datetime() -> str:
    """Get current datetime as formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_elapsed_time(start_time: float, end_time: float) -> str:
    """
    Calculate elapsed time in seconds and format as string.
    
    Args:
        start_time: Start time from time.perf_counter()
        end_time: End time from time.perf_counter()
    
    Returns:
        str: Formatted elapsed time (e.g., "2.345")
    """
    elapsed = end_time - start_time
    return f"{elapsed:.3f}"


def format_timedelta(seconds: float) -> str:
    """
    Format seconds as human-readable string.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        str: Formatted time (e.g., "00:02:34")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

