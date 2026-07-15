"""
Stage 2 - Lock the counter.

Fill in SafeCounter.increment and run_synchronized_increments below.
See EXERCISE.md, Stage 2, for the full explanation and worked examples.
"""
import threading
import time


class SafeCounter:
    """
    A counter incremented from multiple threads, protected by a
    threading.Lock so the final value is always correct.

    Reuse the same read-yield-write shape as stage 1's
    UnsafeCounter.increment -- the only change is that the whole critical
    section must run under a lock, so the yield point can no longer let
    two threads interleave their read/write.

    Attributes:
        value: the running total. Starts at 0.
    """

    def __init__(self) -> None:
        self.value = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        """
        Safely read-modify-write the counter under self._lock.

        Example:
            >>> c = SafeCounter()
            >>> c.increment()
            >>> c.value
            1
        """
        raise NotImplementedError


def run_synchronized_increments(num_threads: int, increments_per_thread: int) -> int:
    """
    Same driver shape as stage 1's run_unsynchronized_increments, but
    using SafeCounter. The result must always equal
    num_threads * increments_per_thread -- no exceptions, no flakiness.

    Args:
        num_threads: how many threads to start.
        increments_per_thread: how many times each thread calls increment().

    Returns:
        The final value of a fresh SafeCounter after all threads join.
        Always exactly num_threads * increments_per_thread.

    Example:
        >>> run_synchronized_increments(4, 1000)
        4000
        >>> run_synchronized_increments(1, 0)
        0
    """
    raise NotImplementedError
