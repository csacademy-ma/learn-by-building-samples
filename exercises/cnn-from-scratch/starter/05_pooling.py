import numpy as np


def max_pool2d(feature_map: np.ndarray, size: int, stride: int) -> np.ndarray:
    """
    Slide a `size` x `size` window over `feature_map` and take the max in
    each window.

    Args:
        feature_map: 2D array, shape (H, W)
        size: window side length, >= 1
        stride: step size between windows, >= 1

    Returns:
        2D array, shape:
            out_h = (H - size) // stride + 1
            out_w = (W - size) // stride + 1

    Example:
        >>> fm = np.array([[1, 3, 2, 4], [5, 6, 1, 2], [1, 2, 9, 8], [3, 4, 7, 6]])
        >>> max_pool2d(fm, size=2, stride=2)
        array([[6., 4.],
               [4., 9.]])
    """
    raise NotImplementedError
