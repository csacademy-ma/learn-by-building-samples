import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import numpy as np

from importlib import import_module
_mod = import_module("01_warmup_conv1d")
convolve1d = _mod.convolve1d


def test_edge_detector_kernel():
    result = convolve1d(np.array([1, 2, 3, 4, 5]), np.array([1, 0, -1]))
    np.testing.assert_allclose(result, [-2, -2, -2])


def test_averaging_kernel():
    result = convolve1d(np.array([2, 8, -1, 4]), np.array([0.5, 0.5]))
    np.testing.assert_allclose(result, [5.0, 3.5, 1.5])


def test_kernel_same_length_as_signal():
    # edge case: kernel length == signal length -> single output value
    result = convolve1d(np.array([1.0, 2.0, 3.0]), np.array([1.0, 1.0, 1.0]))
    np.testing.assert_allclose(result, [6.0])


def test_output_length():
    signal = np.arange(10.0)
    kernel = np.array([1.0, 1.0, 1.0])
    result = convolve1d(signal, kernel)
    assert result.shape == (10 - 3 + 1,)
