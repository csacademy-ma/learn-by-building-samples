import numpy as np


def convolve1d(signal: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Slide `kernel` over `signal` and compute the dot product at each position
    (valid convolution: no padding, stride 1).

    Args:
        signal: 1D array, shape (n,)
        kernel: 1D array, shape (k,), k <= n

    Returns:
        1D array, shape (n - k + 1,)

    Example:
        >>> convolve1d(np.array([1, 2, 3, 4, 5]), np.array([1, 0, -1]))
        array([-2., -2., -2.])
    """
    raise NotImplementedError
