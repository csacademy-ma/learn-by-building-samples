"""
Stage 3 - Producer/consumer with a bounded queue.

Fill in BoundedQueue.put, BoundedQueue.get, and run_producer_consumer below.
See EXERCISE.md, Stage 3, for the full explanation and worked examples.
"""
import threading
from collections import deque
from typing import Any, List


class BoundedQueue:
    """
    A fixed-capacity FIFO queue safe for concurrent producers/consumers,
    built from a threading.Lock + threading.Condition (do not use
    queue.Queue here -- that's stage 5's bridge).

    put() must block while the queue is full; get() must block while the
    queue is empty. Use a Condition so waiting threads sleep instead of
    busy-polling, and are woken exactly when the state they're waiting on
    changes.

    Args:
        capacity: maximum number of items the queue can hold at once.
                  Must be >= 1.
    """

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._capacity = capacity
        self._items: deque = deque()
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)

    def put(self, item: Any) -> None:
        """
        Block until there is room, then append `item` to the queue.

        Example:
            >>> q = BoundedQueue(capacity=2)
            >>> q.put(1)
            >>> q.put(2)
            >>> q.size()
            2
        """
        raise NotImplementedError

    def get(self) -> Any:
        """
        Block until an item is available, then pop and return the oldest one.

        Example:
            >>> q = BoundedQueue(capacity=2)
            >>> q.put("a")
            >>> q.get()
            'a'
        """
        raise NotImplementedError

    def size(self) -> int:
        """Return the current number of items in the queue (thread-safe snapshot)."""
        with self._lock:
            return len(self._items)


def run_producer_consumer(
    num_items: int, capacity: int, num_producers: int = 1, num_consumers: int = 1
) -> List[int]:
    """
    Produce integers 0..num_items-1 spread across `num_producers` producer
    threads and consume them with `num_consumers` consumer threads sharing
    one BoundedQueue(capacity). Return the sorted list of consumed items.

    Hint: you need a way for consumers to know production is finished, or
    they'll block on get() forever after the last real item. A common
    trick is a sentinel value pushed onto the queue once all producers are
    done -- when a consumer sees the sentinel, it should put it back (so
    other consumers also see it) before returning.

    Args:
        num_items: total number of items to produce across all producers.
        capacity: bounded queue capacity.
        num_producers: number of producer threads.
        num_consumers: number of consumer threads.

    Returns:
        Sorted list of all consumed items -- should equal
        list(range(num_items)) with no duplicates and no missing items.

    Example:
        >>> run_producer_consumer(num_items=10, capacity=3)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        >>> run_producer_consumer(num_items=100, capacity=1, num_producers=4, num_consumers=4)
        [0, 1, 2, ..., 99]
    """
    raise NotImplementedError
