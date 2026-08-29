# backend/scripts/test_retry.py
import time
from app.retry import with_retry


class FlakyError(Exception):
    """A retryable error we control, so the test is deterministic."""


calls = {"n": 0}   # mutable counter shared with the inner function


@with_retry(retryable=(FlakyError,), max_attempts=4, base_delay=0.5)
def flaky():
    """Fail the first 2 times with FlakyError, succeed on the 3rd call."""
    calls["n"] += 1
    attempt = calls["n"]
    print(f"  attempt {attempt} running...")
    if attempt < 3:
        raise FlakyError(f"failed on attempt {attempt}")
    return "ok"


if __name__ == "__main__":
    start = time.time()
    result = flaky()
    print(f"result={result}  total_elapsed={time.time() - start:.2f}s")