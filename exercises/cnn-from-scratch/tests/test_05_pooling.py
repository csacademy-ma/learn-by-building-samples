import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import numpy as np

from importlib import import_module
_mod = import_module("05_pooling")
max_pool2d = _mod.max_pool2d


def test_non_overlapping_windows():
    fm = np.array([[1, 3, 2, 4], [5, 6, 1, 2], [1, 2, 9, 8], [3, 4, 7, 6]])
    result = max_pool2d(fm, size=2, stride=2)
    np.testing.assert_allclose(result, [[6, 4], [4, 9]])


def test_overlapping_windows():
    fm = np.array([[1, 3, 2, 4], [5, 6, 1, 2], [1, 2, 9, 8], [3, 4, 7, 6]])
    result = max_pool2d(fm, size=2, stride=1)
    expected = np.array([[6, 6, 4], [6, 9, 9], [4, 9, 9]])
    np.testing.assert_allclose(result, expected)


def test_window_equals_whole_map_edge_case():
    fm = np.array([[3, 1], [2, 5]])
    result = max_pool2d(fm, size=2, stride=2)
    np.testing.assert_allclose(result, [[5.0]])
