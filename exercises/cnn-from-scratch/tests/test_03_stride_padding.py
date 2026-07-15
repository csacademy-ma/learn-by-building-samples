import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import numpy as np

from importlib import import_module
_mod = import_module("03_stride_padding")
convolve2d_strided = _mod.convolve2d_strided


def test_stride_1_padding_0_matches_plain_conv():
    image = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    kernel = np.array([[1, 0], [0, -1]])
    result = convolve2d_strided(image, kernel, stride=1, padding=0)
    np.testing.assert_allclose(result, np.full((3, 3), -5.0))


def test_stride_2():
    image = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    kernel = np.array([[1, 0], [0, -1]])
    result = convolve2d_strided(image, kernel, stride=2, padding=0)
    np.testing.assert_allclose(result, np.full((2, 2), -5.0))


def test_padding_1():
    image = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    kernel = np.array([[1, 0], [0, -1]])
    result = convolve2d_strided(image, kernel, stride=1, padding=1)
    expected = np.array([
        [-1., -2., -3., -4., 0.],
        [-5., -5., -5., -5., 4.],
        [-9., -5., -5., -5., 8.],
        [-13., -5., -5., -5., 12.],
        [0., 13., 14., 15., 16.],
    ])
    np.testing.assert_allclose(result, expected)


def test_image_smaller_than_kernel_needs_padding_edge_case():
    image = np.array([[7]])
    kernel = np.array([[1, 1], [1, 1]])
    result = convolve2d_strided(image, kernel, stride=1, padding=1)
    np.testing.assert_allclose(result, [[7., 7.], [7., 7.]])
