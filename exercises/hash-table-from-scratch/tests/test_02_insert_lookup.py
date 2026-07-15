import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib
import pytest

module = importlib.import_module("02_insert_lookup")
SimpleHashTable = module.SimpleHashTable


def test_insert_then_lookup():
    t = SimpleHashTable(8)
    t.insert("a", 1)
    assert t.lookup("a") == 1


def test_insert_overwrites_same_key():
    t = SimpleHashTable(8)
    t.insert("a", 1)
    t.insert("a", 2)
    assert t.lookup("a") == 2


def test_multiple_distinct_keys():
    t = SimpleHashTable(16)
    t.insert("apple", 1)
    t.insert("banana", 2)
    assert t.lookup("apple") == 1
    assert t.lookup("banana") == 2


def test_lookup_missing_key_raises_keyerror():
    t = SimpleHashTable(8)
    with pytest.raises(KeyError):
        t.lookup("missing")


def test_lookup_missing_key_after_other_inserts_raises_keyerror():
    t = SimpleHashTable(8)
    t.insert("a", 1)
    with pytest.raises(KeyError):
        t.lookup("nonexistent-key")
