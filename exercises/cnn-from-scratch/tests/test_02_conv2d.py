import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import numpy as np

from importlib import import_module
_mod = import_module("02_conv2d")
convolve2d = _mod.convolve2d


def test_edge_detector_kernel():
    image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    kernel = np.array([[1, 0], [0, -1]])
    result = convolve2d(image, kernel)
    np.testing.assert_allclose(result, [[-4, -4], [-4, -4]])


def test_all_ones():
    image = np.ones((4, 4))
    kernel = np.array([[1, 1], [1, 1]])
    result = convolve2d(image, kernel)
    np.testing.assert_allclose(result, np.full((3, 3), 4.0))


def test_1x1_scalar_edge_case():
    result = convolve2d(np.array([[5]]), np.array([[2]]))
    np.testing.assert_allclose(result, [[10.0]])


def test_output_shape():
    image = np.zeros((5, 7))
    kernel = np.zeros((2, 3))
    result = convolve2d(image, kernel)
    assert result.shape == (5 - 2 + 1, 7 - 3 + 1)
