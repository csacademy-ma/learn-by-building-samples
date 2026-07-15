import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

from importlib import import_module

mod = import_module("05_bridge_to_threadpool")


def test_producer_consumer_stdlib_basic():
    result = mod.run_producer_consumer_stdlib(num_items=200, capacity=5)
    assert result == list(range(200))


def test_producer_consumer_stdlib_multi():
    result = mod.run_producer_consumer_stdlib(
        num_items=300, capacity=4, num_producers=3, num_consumers=3
    )
    assert result == list(range(300))


def test_sum_of_squares():
    assert mod.sum_of_squares_threadpool([1, 2, 3, 4]) == 30


def test_sum_of_squares_empty():
    assert mod.sum_of_squares_threadpool([]) == 0


def test_sum_of_squares_larger():
    numbers = list(range(1, 11))
    expected = sum(n * n for n in numbers)
    assert mod.sum_of_squares_threadpool(numbers, max_workers=4) == expected
