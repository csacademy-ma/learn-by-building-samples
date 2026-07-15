import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib
import pytest

module = importlib.import_module("03_collisions")
ChainingHashTable = module.ChainingHashTable
hash_string = module.hash_string


def test_colliding_keys_both_retrievable():
    # "a" and "e" collide in a 4-bucket table with the polynomial rolling
    # hash from Stage 1 (both hash to index 1).
    t = ChainingHashTable(4)
    t.insert("a", 1)
    t.insert("e", 2)
    assert t.lookup("a") == 1
    assert t.lookup("e") == 2


def test_insert_same_key_updates_in_place_not_appends():
    t = ChainingHashTable(4)
    t.insert("a", 1)
    t.insert("a", 99)
    assert t.lookup("a") == 99
    assert len(t) == 1


def test_len_counts_distinct_keys():
    t = ChainingHashTable(8)
    t.insert("x", 1)
    t.insert("y", 2)
    t.insert("z", 3)
    assert len(t) == 3
    t.insert("x", "updated")
    assert len(t) == 3


def test_contains():
    t = ChainingHashTable(8)
    t.insert("present", 1)
    assert "present" in t
    assert "absent" not in t


def test_lookup_missing_key_in_nonempty_chain_raises_keyerror():
    # Edge case: some bucket has entries, just not for the key we look up.
    # "nonexistent" hashes to the same bucket (1) as "a" and "e" with the
    # Stage 1 polynomial rolling hash in a 4-bucket table, so this
    # specifically exercises "scan a non-empty chain, find no match"
    # rather than "the bucket itself was empty".
    t = ChainingHashTable(4)
    t.insert("a", 1)
    t.insert("e", 2)
    assert hash_string("nonexistent", 4) == hash_string("a", 4)
    with pytest.raises(KeyError):
        t.lookup("nonexistent")
