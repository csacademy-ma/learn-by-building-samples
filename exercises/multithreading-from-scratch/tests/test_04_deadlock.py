import os
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

from importlib import import_module

mod = import_module("04_deadlock")

# Hard ceiling so a genuine bug in a submission (e.g. an infinite loop
# instead of a lock wait) can never hang the whole test run. Each test
# below also uses its own internal timeout, but this watchdog is a second
# line of defense: if the test function itself doesn't return within
# WATCHDOG_SECONDS, we fail loudly instead of hanging CI forever.
WATCHDOG_SECONDS = 10


def _run_with_watchdog(fn, *args, **kwargs):
    result = {}
    exc = {}

    def target():
        try:
            result["value"] = fn(*args, **kwargs)
        except BaseException as e:  # noqa: BLE001
            exc["error"] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=WATCHDOG_SECONDS)

    if t.is_alive():
        raise AssertionError(
            f"{fn.__name__} did not return within {WATCHDOG_SECONDS}s watchdog limit"
        )
    if "error" in exc:
        raise exc["error"]
    return result["value"]


def test_deadlock_is_detected():
    # The deadlock-prone version should leave at least one thread hung.
    deadlocked = _run_with_watchdog(mod.run_deadlock_and_detect, timeout=1.0)
    assert deadlocked is True


def test_deadlock_is_detected_reliably():
    # Timing-dependent: run several times to make sure it's not a fluke.
    for _ in range(3):
        deadlocked = _run_with_watchdog(mod.run_deadlock_and_detect, timeout=1.0)
        assert deadlocked is True


def test_fixed_version_never_deadlocks():
    for _ in range(5):
        finished_cleanly = _run_with_watchdog(mod.run_safe_transfer_and_detect, timeout=1.0)
        assert finished_cleanly is True
