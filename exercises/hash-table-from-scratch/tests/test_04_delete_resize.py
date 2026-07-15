import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib
import pytest

module = importlib.import_module("04_delete_resize")
ResizableHashTable = module.ResizableHashTable


def test_resize_triggers_and_preserves_all_keys():
    t = ResizableHashTable(num_buckets=4, max_load_factor=0.5)
    t.insert("a", 1)
    t.insert("b", 2)
    assert t.num_buckets == 4  # load factor 2/4 = 0.5, not > 0.5 yet

    t.insert("c", 3)  # load factor 3/4 = 0.75 > 0.5 -> resize
    assert t.num_buckets == 8

    # all three keys must still be retrievable after the rehash
    assert t.lookup("a") == 1
    assert t.lookup("b") == 2
    assert t.lookup("c") == 3


def test_delete_then_lookup_raises_keyerror():
    t = ResizableHashTable()
    t.insert("a", 1)
    t.delete("a")
    with pytest.raises(KeyError):
        t.lookup("a")


def test_delete_twice_raises_keyerror_both_times():
    t = ResizableHashTable()
    t.insert("a", 1)
    t.delete("a")
    with pytest.raises(KeyError):
        t.delete("a")


def test_delete_missing_key_raises_keyerror():
    t = ResizableHashTable()
    with pytest.raises(KeyError):
        t.delete("never-inserted")


def test_len_unchanged_across_resize():
    t = ResizableHashTable(num_buckets=4, max_load_factor=0.5)
    keys = [f"k{i}" for i in range(10)]
    for k in keys:
        t.insert(k, k)
    assert len(t) == 10
    assert t.num_buckets > 4  # resize(s) must have happened
    for k in keys:
        assert t.lookup(k) == k


def test_load_factor_reported_correctly():
    t = ResizableHashTable(num_buckets=10, max_load_factor=0.99)
    t.insert("a", 1)
    t.insert("b", 2)
    assert t.load_factor() == pytest.approx(0.2)
