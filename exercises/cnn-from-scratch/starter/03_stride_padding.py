import numpy as np


def convolve2d_strided(
    image: np.ndarray,
    kernel: np.ndarray,
    stride: int = 1,
    padding: int = 0,
) -> np.ndarray:
    """
    Slide `kernel` over `image` with the given stride and zero-padding.

    Padding is applied symmetrically on all four sides before convolving.
    Stride controls how many pixels the kernel moves between positions.

    Args:
        image: 2D array, shape (H, W)
        kernel: 2D array, shape (kh, kw)
        stride: step size between kernel positions, >= 1
        padding: number of zero-pixels added to each side of the image, >= 0

    Returns:
        2D array, shape:
            out_h = (H + 2*padding - kh) // stride + 1
            out_w = (W + 2*padding - kw) // stride + 1

    Example:
        >>> image = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
        >>> kernel = np.array([[1, 0], [0, -1]])
        >>> convolve2d_strided(image, kernel, stride=2, padding=0)
        array([[-5., -5.],
               [-5., -5.]])
    """
    raise NotImplementedError
