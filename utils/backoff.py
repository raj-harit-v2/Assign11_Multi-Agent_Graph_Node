"""
Exponential Backoff Utility for API Rate Limiting
Handles 429 RESOURCE_EXHAUSTED errors with automatic retry and exponential backoff.
Supports both synchronous and asynchronous functions.
"""

import asyncio
import time
from typing import Callable, Any, Optional
from functools import wraps
import inspect

try:
    from google.genai.errors import ServerError
    GOOGLE_ERRORS_AVAILABLE = True
except ImportError:
    GOOGLE_ERRORS_AVAILABLE = False


def is_429_error(exception: Exception) -> bool:
    """
    Check if exception is a 429 rate limit error.
    
    Args:
        exception: The exception to check
    
    Returns:
        True if it's a 429 error, False otherwise
    """
    if not GOOGLE_ERRORS_AVAILABLE:
        return False
    
    if isinstance(exception, ServerError):
        # Check error code
        error_code = getattr(exception, 'code', None)
        if error_code == 429:
            return True
        
        # Also check error message for 429 indicators
        error_str = str(exception).lower()
        if '429' in error_str or 'resource_exhausted' in error_str or 'rate limit' in error_str:
            return True
    
    # Check error message for 429 indicators (fallback)
    error_str = str(exception).lower()
    if '429' in error_str or 'resource_exhausted' in error_str or 'rate limit' in error_str:
        return True
    
    return False


def _with_exponential_backoff_sync(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    **kwargs
) -> Any:
    """
    Execute a synchronous function with exponential backoff retry on 429 errors.
    
    Args:
        func: The function to execute
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        **kwargs: Keyword arguments for the function
    
    Returns:
        Result from the function call
    
    Raises:
        The last exception if all retries are exhausted
    """
    last_exception = None
    # Fixed delays: 6, 10, 18, 60 seconds for retries
    fixed_delays = [6.0, 10.0, 18.0, 60.0]
    
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            # Execute the function
            result = func(*args, **kwargs)
            return result
        
        except Exception as e:
            last_exception = e
            
            # Only retry on 429 errors
            if not is_429_error(e):
                # Not a 429 error, re-raise immediately
                raise
            
            # Check if we have retries left
            if attempt < max_retries:
                # Use fixed delay based on attempt number
                delay_index = min(attempt, len(fixed_delays) - 1)
                current_delay = fixed_delays[delay_index]
                current_delay = min(current_delay, max_delay)
                
                print(f"[RETRY] 429 error detected. Retrying in {current_delay:.1f} seconds (attempt {attempt + 1}/{max_retries})...")
                
                # Wait before retry (synchronous)
                time.sleep(current_delay)
            else:
                # All retries exhausted
                print(f"[ERROR] All {max_retries} retry attempts exhausted for 429 error.")
                raise
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected error in exponential backoff")


async def _with_exponential_backoff_async(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    **kwargs
) -> Any:
    """
    Execute an async function with exponential backoff retry on 429 errors.
    
    Args:
        func: The async function to execute
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        **kwargs: Keyword arguments for the function
    
    Returns:
        Result from the function call
    
    Raises:
        The last exception if all retries are exhausted
    """
    last_exception = None
    # Fixed delays: 6, 10, 18, 60 seconds for retries
    fixed_delays = [6.0, 10.0, 18.0, 60.0]
    
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            return result
        
        except Exception as e:
            last_exception = e
            
            # Only retry on 429 errors
            if not is_429_error(e):
                # Not a 429 error, re-raise immediately
                raise
            
            # Check if we have retries left
            if attempt < max_retries:
                # Use fixed delay based on attempt number
                delay_index = min(attempt, len(fixed_delays) - 1)
                current_delay = fixed_delays[delay_index]
                current_delay = min(current_delay, max_delay)
                
                print(f"[RETRY] 429 error detected. Retrying in {current_delay:.1f} seconds (attempt {attempt + 1}/{max_retries})...")
                
                # Wait before retry (async)
                await asyncio.sleep(current_delay)
            else:
                # All retries exhausted
                print(f"[ERROR] All {max_retries} retry attempts exhausted for 429 error.")
                raise
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected error in exponential backoff")


def with_exponential_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    **kwargs
) -> Any:
    """
    Execute a function with exponential backoff retry on 429 errors.
    Automatically detects if function is sync or async and handles accordingly.
    
    Args:
        func: The function to execute (sync or async)
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        **kwargs: Keyword arguments for the function
    
    Returns:
        Result from the function call
    
    Raises:
        The last exception if all retries are exhausted
    """
    # Check if function is async
    if asyncio.iscoroutinefunction(func):
        # For async functions, need to be called from async context
        # Return a coroutine that can be awaited
        return _with_exponential_backoff_async(
            func,
            *args,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            backoff_multiplier=backoff_multiplier,
            **kwargs
        )
    else:
        # For sync functions, use sync version
        return _with_exponential_backoff_sync(
            func,
            *args,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            backoff_multiplier=backoff_multiplier,
            **kwargs
        )


def exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0
):
    """
    Decorator for applying exponential backoff to async functions.
    
    Usage:
        @exponential_backoff(max_retries=3, initial_delay=1.0)
        async def my_api_call():
            ...
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
    
    Returns:
        Decorated function with exponential backoff
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await with_exponential_backoff(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                backoff_multiplier=backoff_multiplier,
                **kwargs
            )
        return wrapper
    return decorator

