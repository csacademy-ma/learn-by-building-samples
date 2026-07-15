"""
Stage 4 - Construct a deadlock on purpose, then fix it.

Fill in run_deadlock_and_detect and run_safe_transfer_and_detect below.
See EXERCISE.md, Stage 4, for the full explanation and worked examples.
"""
import threading
import time


def run_deadlock_and_detect(timeout: float = 1.0) -> bool:
    """
    Start two threads that acquire two locks in OPPOSITE order (the
    classic two-lock deadlock) and detect whether they actually hang.

    Thread 1 should acquire lock_a, sleep briefly (e.g. time.sleep(0.2)),
    then try to acquire lock_b.
    Thread 2 should acquire lock_b, sleep briefly, then try to acquire
    lock_a.
    If both threads reach their second acquire before either releases its
    first lock, each blocks forever waiting on a lock the other holds.

    This function must never block the caller forever: start both worker
    threads as daemon threads, then join each with `timeout` seconds and
    report whether either is still alive afterward (still alive ==
    deadlocked, since a non-deadlocked thread finishes this workload in
    well under a second).

    Args:
        timeout: seconds to wait for each thread before giving up.

    Returns:
        True if at least one thread was still alive after `timeout`
        seconds (a deadlock was observed). False if both finished.

    Example:
        >>> run_deadlock_and_detect(timeout=1.0)
        True
    """
    raise NotImplementedError


def run_safe_transfer_and_detect(timeout: float = 1.0) -> bool:
    """
    Fixed version of the same two-thread workload: make BOTH threads
    acquire the locks in the SAME global order (lock_a, then lock_b, in
    both threads). With a single consistent order there is no cycle in
    the wait-for graph, so a deadlock is structurally impossible here.

    Args:
        timeout: seconds to wait for each thread before giving up.

    Returns:
        True if both threads finished within `timeout` seconds (expected:
        always True). False if either was still alive (would indicate a
        bug in the fix).

    Example:
        >>> run_safe_transfer_and_detect(timeout=1.0)
        True
    """
    raise NotImplementedError
