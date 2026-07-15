import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

from importlib import import_module

mod = import_module("02_lock_the_counter")


def test_single_thread():
    counter = mod.SafeCounter()
    for _ in range(50):
        counter.increment()
    assert counter.value == 50


def test_always_correct_under_concurrency():
    # Unlike stage 1, this must be exactly right every single time.
    for _ in range(10):
        result = mod.run_synchronized_increments(8, 500)
        assert result == 4000


def test_zero_threads_or_zero_increments():
    assert mod.run_synchronized_increments(0, 100) == 0
    assert mod.run_synchronized_increments(4, 0) == 0
