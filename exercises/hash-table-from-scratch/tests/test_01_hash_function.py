import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib

hash_function_module = importlib.import_module("01_hash_function")
hash_string = hash_function_module.hash_string


def test_deterministic():
    assert hash_string("cat", 10) == hash_string("cat", 10)
    assert hash_string("hello world", 16) == hash_string("hello world", 16)


def test_result_in_valid_range():
    for key in ["hello", "a", "zzzzzz", "Hash Table", "12345"]:
        for num_buckets in [1, 2, 8, 100]:
            idx = hash_string(key, num_buckets)
            assert 0 <= idx < num_buckets


def test_empty_string_edge_case():
    assert hash_string("", 5) == 0
    assert hash_string("", 1) == 0


def test_different_keys_can_produce_different_indices():
    # Not a strict requirement for any single pair, but across many keys
    # we should see more than one distinct bucket index used.
    num_buckets = 16
    keys = [f"user_{i}" for i in range(50)]
    indices = {hash_string(k, num_buckets) for k in keys}
    assert len(indices) > 1


def test_rough_distribution_over_many_keys():
    # Statistical check, not exact: hash a few thousand distinct keys into
    # a moderate number of buckets and confirm no single bucket gets a
    # wildly disproportionate share. This is the kind of test that checks
    # "roughly even," not "exactly this."
    num_buckets = 32
    num_keys = 4000
    counts = [0] * num_buckets
    for i in range(num_keys):
        idx = hash_string(f"key-{i}", num_buckets)
        counts[idx] += 1

    expected_per_bucket = num_keys / num_buckets  # 125
    # Every bucket should have gotten at least some keys.
    assert min(counts) > 0
    # No bucket should have wildly more than its fair share -- allow a
    # generous 3x margin above the expected average to avoid flaking on
    # a reasonable (not perfect) hash function.
    assert max(counts) < expected_per_bucket * 3
