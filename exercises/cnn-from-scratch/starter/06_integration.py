import os
from importlib import import_module

import numpy as np

# Stage file names start with digits, so they can't be imported with a plain
# `import 04_conv_layer` statement — we load them dynamically by path instead.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, _THIS_DIR)

_conv_layer_mod = import_module("04_conv_layer")
_pooling_mod = import_module("05_pooling")

ConvLayer = _conv_layer_mod.ConvLayer
max_pool2d = _pooling_mod.max_pool2d


def build_edge_image() -> np.ndarray:
    """
    A 6x6 image with a vertical edge: the left half is 0, the right half is 1.

    Returns:
        2D array, shape (6, 6):
        array([[0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.]])
    """
    raise NotImplementedError


def run_pipeline(
    image: np.ndarray,
    kernels: np.ndarray,
    pool_size: int,
    pool_stride: int,
) -> np.ndarray:
    """
    Run `image` through a ConvLayer (stride=1, padding=0) built from `kernels`,
    then max-pool every resulting feature map.

    Args:
        image: 2D array, shape (H, W)
        kernels: 3D array, shape (num_filters, kh, kw)
        pool_size: pooling window size
        pool_stride: pooling stride

    Returns:
        3D array, shape (num_filters, pooled_h, pooled_w)

    Example:
        >>> image = build_edge_image()
        >>> kernel = np.array([[-1, 1], [-1, 1]])
        >>> run_pipeline(image, np.stack([kernel]), pool_size=2, pool_stride=2)
        array([[[0., 2.],
                [0., 2.]]])
    """
    raise NotImplementedError
