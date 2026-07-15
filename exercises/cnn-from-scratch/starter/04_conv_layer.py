import numpy as np


def relu(x: np.ndarray) -> np.ndarray:
    """
    Elementwise rectified linear unit: max(0, x).

    Example:
        >>> relu(np.array([-2, -1, 0, 1, 2]))
        array([0, 0, 0, 1, 2])
    """
    raise NotImplementedError


class ConvLayer:
    """
    A convolutional layer: a stack of kernels (filters) applied to the same
    input, each followed by ReLU.

    Args:
        kernels: 3D array, shape (num_filters, kh, kw) — one kernel per filter
        stride: shared stride for every filter
        padding: shared zero-padding for every filter
    """

    def __init__(self, kernels: np.ndarray, stride: int = 1, padding: int = 0):
        raise NotImplementedError

    def forward(self, image: np.ndarray) -> np.ndarray:
        """
        Apply every filter to `image`, then ReLU each result.

        Args:
            image: 2D array, shape (H, W)

        Returns:
            3D array, shape (num_filters, out_h, out_w) — one feature map
            per filter, using the same out_h/out_w formula as
            convolve2d_strided.

        Example:
            >>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            >>> k1 = np.array([[1, 0], [0, -1]])
            >>> k2 = np.array([[-1, 0], [0, 1]])
            >>> layer = ConvLayer(np.stack([k1, k2]), stride=1, padding=0)
            >>> layer.forward(image)
            array([[[0., 0.],
                    [0., 0.]],
            <BLANKLINE>
                   [[4., 4.],
                    [4., 4.]]])
        """
        raise NotImplementedError
