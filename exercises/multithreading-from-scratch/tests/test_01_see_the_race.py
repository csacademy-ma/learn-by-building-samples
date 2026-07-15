import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

from importlib import import_module

mod = import_module("01_see_the_race")


def test_single_thread_no_race():
    counter = mod.UnsafeCounter()
    for _ in range(100):
        counter.increment()
    assert counter.value == 100


def test_race_produces_wrong_total_usually():
    # With the deliberate yield point, unsynchronized increments across
    # many threads should lose updates most of the time. We run several
    # trials and require the race to manifest in at least one of them --
    # this avoids a flaky failure if the OS scheduler happens to get lucky
    # on a single trial, while still proving the race is real.
    num_threads = 8
    increments_per_thread = 500
    expected = num_threads * increments_per_thread

    saw_race = False
    for _ in range(5):
        result = mod.run_unsynchronized_increments(num_threads, increments_per_thread)
        assert result <= expected  # can never be MORE than expected
        if result < expected:
            saw_race = True
            break

    assert saw_race, "expected the unsynchronized counter to lose at least one update"


def test_zero_threads_or_zero_increments():
    assert mod.run_unsynchronized_increments(0, 100) == 0
    assert mod.run_unsynchronized_increments(4, 0) == 0
