import numpy as np


def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Slide `kernel` over `image` and compute the dot product at each position
    (valid convolution, no padding, stride 1).

    Args:
        image: 2D array, shape (H, W)
        kernel: 2D array, shape (kh, kw), kh <= H and kw <= W

    Returns:
        2D array, shape (H - kh + 1, W - kw + 1)

    Example:
        >>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> kernel = np.array([[1, 0], [0, -1]])
        >>> convolve2d(image, kernel)
        array([[-4., -4.],
               [-4., -4.]])
    """
    raise NotImplementedError
