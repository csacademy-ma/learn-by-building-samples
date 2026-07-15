import os
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

from importlib import import_module

mod = import_module("03_producer_consumer")


def test_put_get_basic():
    q = mod.BoundedQueue(capacity=2)
    q.put(1)
    q.put(2)
    assert q.size() == 2
    assert q.get() == 1
    assert q.get() == 2
    assert q.size() == 0


def test_put_blocks_when_full():
    q = mod.BoundedQueue(capacity=1)
    q.put("a")

    put_finished = threading.Event()

    def blocked_put():
        q.put("b")
        put_finished.set()

    t = threading.Thread(target=blocked_put, daemon=True)
    t.start()
    # Give the thread a moment: it should NOT have finished, since the
    # queue is full and put() should block.
    put_finished.wait(timeout=0.2)
    assert not put_finished.is_set()

    # Draining one item should unblock the pending put.
    assert q.get() == "a"
    t.join(timeout=1.0)
    assert put_finished.is_set()
    assert q.get() == "b"


def test_get_blocks_when_empty():
    q = mod.BoundedQueue(capacity=1)
    got = {}

    def blocked_get():
        got["value"] = q.get()

    t = threading.Thread(target=blocked_get, daemon=True)
    t.start()
    t.join(timeout=0.2)
    assert "value" not in got  # still blocked, queue was empty

    q.put(42)
    t.join(timeout=1.0)
    assert got["value"] == 42


def test_single_producer_single_consumer_all_items_delivered():
    result = mod.run_producer_consumer(num_items=200, capacity=5)
    assert result == list(range(200))


def test_multiple_producers_and_consumers_all_items_delivered():
    for _ in range(5):
        result = mod.run_producer_consumer(
            num_items=300, capacity=4, num_producers=3, num_consumers=3
        )
        assert result == list(range(300))
