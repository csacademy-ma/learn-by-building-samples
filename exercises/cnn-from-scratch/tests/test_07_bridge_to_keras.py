import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import numpy as np
import pytest

# Stage 7 is optional: skip this whole file if tensorflow isn't installed,
# rather than failing the suite for people who haven't done `pip install tensorflow`.
pytest.importorskip("tensorflow")

from importlib import import_module
_mod = import_module("07_bridge_to_keras")
conv2d_with_keras = _mod.conv2d_with_keras


def test_matches_stage2_worked_example():
    image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="float32")
    kernel = np.array([[1, 0], [0, -1]], dtype="float32")
    result = conv2d_with_keras(image, kernel)
    np.testing.assert_allclose(result, [[-4., -4.], [-4., -4.]], rtol=1e-5)


def test_matches_stage6_edge_image():
    edge_image = np.array([
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
    ], dtype="float32")
    vertical_edge_kernel = np.array([[-1, 1], [-1, 1]], dtype="float32")
    result = conv2d_with_keras(edge_image, vertical_edge_kernel)
    expected = np.array([
        [0., 0., 2., 0., 0.],
        [0., 0., 2., 0., 0.],
        [0., 0., 2., 0., 0.],
        [0., 0., 2., 0., 0.],
        [0., 0., 2., 0., 0.],
    ], dtype="float32")
    np.testing.assert_allclose(result, expected, rtol=1e-5)


def test_1x1_scalar_edge_case():
    image = np.array([[5]], dtype="float32")
    kernel = np.array([[2]], dtype="float32")
    result = conv2d_with_keras(image, kernel)
    np.testing.assert_allclose(result, [[10.0]], rtol=1e-5)
