"""
Stage 1 - See the race.

Fill in UnsafeCounter.increment and run_unsynchronized_increments below.
See EXERCISE.md, Stage 1, for the full explanation and worked examples.
"""
import threading
import time


class UnsafeCounter:
    """
    A counter incremented from multiple threads with NO synchronization.

    The increment is deliberately split into three steps: read the current
    value, yield control (time.sleep(0)), then write back value + 1. Real
    races don't need an explicit yield -- the OS can preempt a thread
    between any two instructions -- but on CPython the GIL makes the
    unlucky interleaving rare enough that a test suite would flake (or
    never fail) without forcing the handoff. Adding `time.sleep(0)` here
    is not "cheating": it's making a rare bug reproducible on demand, the
    same way you'd add an artificial delay to reproduce a UI race
    condition. The bug (unprotected read-modify-write) is real; only its
    probability of manifesting is being dialed up.

    Attributes:
        value: the running total. Starts at 0.
    """

    def __init__(self) -> None:
        self.value = 0

    def increment(self) -> None:
        """
        Read the current value, yield control, then write back value + 1.

        Example:
            >>> c = UnsafeCounter()
            >>> c.increment()
            >>> c.value
            1
        """
        raise NotImplementedError


def run_unsynchronized_increments(num_threads: int, increments_per_thread: int) -> int:
    """
    Spin up `num_threads` threads, each calling `counter.increment()`
    `increments_per_thread` times on a single shared UnsafeCounter, then
    return the final counter value after all threads finish.

    Args:
        num_threads: how many threads to start.
        increments_per_thread: how many times each thread calls increment().

    Returns:
        The final value of a fresh UnsafeCounter after all threads join.

    Example:
        >>> result = run_unsynchronized_increments(4, 1000)
        >>> result <= 4000
        True
        >>> # `result` is frequently LESS than 4000 -- that's the race.

        >>> run_unsynchronized_increments(0, 100)
        0
        >>> run_unsynchronized_increments(4, 0)
        0
    """
    raise NotImplementedError
