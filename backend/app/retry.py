import time
import random
import functools
from typing import Callable, Type

def with_retry(
    retryable: tuple[Type[Exception], ...],
    max_attempts: int = 4,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
) -> Callable:
    """
    Decorator factory. Returns a decorator that retries the wrapped
    function with exponential backoff + jitter.

    Args:
        retryable:    exception types that SHOULD trigger a retry.
                      Anything not in here re-raises immediately.
        max_attempts: total tries before giving up (not "extra" tries).
        base_delay:   first wait, in seconds.
        max_delay:    cap on any single wait.

    Behaviour per attempt:
      - call fn; if it returns, return that.
      - if it raises something in `retryable` AND attempts remain:
            wait, then loop.
      - if it raises anything else, or attempts are used up:
            re-raise.

    Wait for attempt n (0-indexed): min(base_delay * 2**n, max_delay),
    plus a small random jitter added on top.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn) 
        def wrapper(*args, **kwargs):
            for n in range(max_attempts):
                try:
                    return fn(*args, **kwargs)  
                except retryable as e:
                    if n == max_attempts-1:
                        raise e
                    delay = min(base_delay * 2**n, max_delay) + random.uniform(0, base_delay)
                    time.sleep(delay)
        return wrapper
    return decorator
    
                    

                