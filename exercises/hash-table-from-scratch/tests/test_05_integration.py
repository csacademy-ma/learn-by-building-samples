import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib

module = importlib.import_module("05_integration")
ResizableHashTable = module.ResizableHashTable
average_chain_length = module.average_chain_length
demo_resize_effect = module.demo_resize_effect


def test_average_chain_length_basic():
    t = ResizableHashTable(num_buckets=4, max_load_factor=1.0)
    t.insert("a", 1)
    t.insert("b", 2)
    assert average_chain_length(t) == 0.5


def test_average_chain_length_empty_table():
    t = ResizableHashTable(num_buckets=8, max_load_factor=0.75)
    assert average_chain_length(t) == 0.0


def test_resize_reduces_average_chain_length():
    stats = demo_resize_effect(num_keys=40, num_buckets=8, max_load_factor=0.75)
    assert stats["avg_chain_length_just_before_resize"] is not None
    assert (
        stats["avg_chain_length_just_before_resize"]
        > stats["avg_chain_length_just_after_resize"]
    )


def test_final_bucket_count_grew():
    stats = demo_resize_effect(num_keys=40, num_buckets=8, max_load_factor=0.75)
    assert stats["final_num_buckets"] >= 8


def test_no_resize_edge_case():
    # Huge initial bucket count relative to key count -> load factor never
    # crosses the threshold, so no resize happens at all.
    stats = demo_resize_effect(num_keys=2, num_buckets=100, max_load_factor=0.75)
    assert stats["avg_chain_length_just_before_resize"] is None
    assert stats["avg_chain_length_just_after_resize"] is None
    assert stats["final_num_buckets"] == 100
