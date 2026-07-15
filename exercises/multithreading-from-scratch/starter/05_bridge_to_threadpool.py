"""
Stage 5 - Bridge to queue.Queue and ThreadPoolExecutor.

Fill in run_producer_consumer_stdlib and sum_of_squares_threadpool below.
See EXERCISE.md, Stage 5, for the full explanation and worked examples.
"""
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List


def run_producer_consumer_stdlib(
    num_items: int, capacity: int, num_producers: int = 1, num_consumers: int = 1
) -> List[int]:
    """
    Same producer/consumer task as stage 3's run_producer_consumer, but
    built on the standard library's queue.Queue(maxsize=capacity) instead
    of your hand-rolled BoundedQueue. queue.Queue already provides the
    lock + condition-variable blocking behavior stage 3 built by hand --
    put() blocks when full, get() blocks when empty.

    Use a ThreadPoolExecutor to run your producer and consumer callables
    instead of raw threading.Thread (that's the other half of this
    stage's bridge -- ThreadPoolExecutor manages thread lifecycle for you).

    Args:
        num_items: total number of items to produce across all producers.
        capacity: bounded queue capacity (queue.Queue's maxsize).
        num_producers: number of producer threads.
        num_consumers: number of consumer threads.

    Returns:
        Sorted list of all consumed items -- list(range(num_items)).

    Example:
        >>> run_producer_consumer_stdlib(num_items=10, capacity=3)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    raise NotImplementedError


def sum_of_squares_threadpool(numbers: List[int], max_workers: int = 4) -> int:
    """
    Compute sum(n * n for n in numbers) by farming each square out to a
    ThreadPoolExecutor and summing the results -- a task-parallel example
    (no shared mutable state to synchronize, unlike stages 1-4) that shows
    the other common use of the stdlib threading tools: parallelizing
    independent units of work rather than protecting shared state.

    Args:
        numbers: list of integers to square and sum.
        max_workers: size of the thread pool.

    Returns:
        The sum of squares of all numbers.

    Example:
        >>> sum_of_squares_threadpool([1, 2, 3, 4])
        30
        >>> sum_of_squares_threadpool([])
        0
    """
    raise NotImplementedError
