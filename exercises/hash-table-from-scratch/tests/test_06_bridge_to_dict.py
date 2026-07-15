import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib

module = importlib.import_module("06_bridge_to_dict")
compare_with_builtin_dict = module.compare_with_builtin_dict


def test_small_case_matches_dict():
    result = compare_with_builtin_dict([("a", 1), ("b", 2), ("c", 3)])
    assert result["same_length"] is True
    assert result["same_lookups"] is True
    assert result["same_after_delete"] is True


def test_larger_case_exercising_resize_matches_dict():
    pairs = [(f"key{i}", i) for i in range(50)]
    result = compare_with_builtin_dict(pairs)
    assert result["same_length"] is True
    assert result["same_lookups"] is True
    assert result["same_after_delete"] is True


def test_empty_input_edge_case():
    result = compare_with_builtin_dict([])
    assert result["same_length"] is True
    assert result["same_lookups"] is True
    assert result["same_after_delete"] is True
