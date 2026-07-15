import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import numpy as np

from importlib import import_module
_mod = import_module("06_integration")
build_edge_image = _mod.build_edge_image
run_pipeline = _mod.run_pipeline


def test_build_edge_image_shape_and_values():
    image = build_edge_image()
    assert image.shape == (6, 6)
    expected = np.array([
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
        [0., 0., 0., 1., 1., 1.],
    ])
    np.testing.assert_allclose(image, expected)


def test_pipeline_detects_edge():
    image = build_edge_image()
    vertical_edge_kernel = np.array([[-1, 1], [-1, 1]])
    result = run_pipeline(image, np.stack([vertical_edge_kernel]), pool_size=2, pool_stride=2)
    expected = np.array([[[0., 2.], [0., 2.]]])
    np.testing.assert_allclose(result, expected)


def test_pipeline_output_shape():
    image = build_edge_image()
    vertical_edge_kernel = np.array([[-1, 1], [-1, 1]])
    result = run_pipeline(image, np.stack([vertical_edge_kernel]), pool_size=2, pool_stride=2)
    assert result.shape == (1, 2, 2)


def test_flat_image_edge_case():
    vertical_edge_kernel = np.array([[-1, 1], [-1, 1]])
    result = run_pipeline(np.zeros((6, 6)), np.stack([vertical_edge_kernel]), pool_size=2, pool_stride=2)
    assert result.sum() == 0.0
