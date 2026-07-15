import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import numpy as np

from importlib import import_module
_mod = import_module("04_conv_layer")
relu = _mod.relu
ConvLayer = _mod.ConvLayer


def test_relu_basic():
    result = relu(np.array([-2, -1, 0, 1, 2]))
    np.testing.assert_allclose(result, [0, 0, 0, 1, 2])


def test_conv_layer_two_filters_one_dies_one_survives():
    image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    k1 = np.array([[1, 0], [0, -1]])   # raw output is -4 everywhere -> ReLU kills it
    k2 = np.array([[-1, 0], [0, 1]])   # raw output is +4 everywhere -> ReLU keeps it
    layer = ConvLayer(np.stack([k1, k2]), stride=1, padding=0)
    result = layer.forward(image)
    expected = np.array([
        [[0., 0.], [0., 0.]],
        [[4., 4.], [4., 4.]],
    ])
    np.testing.assert_allclose(result, expected)


def test_conv_layer_output_shape():
    image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    k1 = np.array([[1, 0], [0, -1]])
    k2 = np.array([[-1, 0], [0, 1]])
    layer = ConvLayer(np.stack([k1, k2]), stride=1, padding=0)
    result = layer.forward(image)
    assert result.shape == (2, 2, 2)


def test_all_zero_image_edge_case():
    kernel = np.array([[1, 1], [1, 1]])
    layer = ConvLayer(np.stack([kernel]), stride=2, padding=1)
    result = layer.forward(np.zeros((2, 2)))
    assert result.shape == (1, 2, 2)
    np.testing.assert_allclose(result, np.zeros((1, 2, 2)))
