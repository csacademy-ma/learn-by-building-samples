# This stage is OPTIONAL and needs an extra dependency not required by the
# rest of the exercise:
#
#     pip install tensorflow
#
# Nothing else in this exercise imports tensorflow/keras, and the test file
# for this stage skips itself automatically (via pytest.importorskip) if
# tensorflow isn't installed. Feel free to stop at stage 6 if you don't want
# the extra install.

import numpy as np


def conv2d_with_keras(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Run `image` through a single-filter keras.layers.Conv2D layer whose
    weights are manually set to `kernel`, with valid padding and stride 1,
    and return the resulting feature map with the same (out_h, out_w) shape
    your own convolve2d would produce.

    Args:
        image: 2D array, shape (H, W)
        kernel: 2D array, shape (kh, kw)

    Returns:
        2D array, shape (H - kh + 1, W - kw + 1) — the Conv2D output for the
        single filter, with the batch and channel dimensions squeezed out.

    Notes:
        - keras.layers.Conv2D expects input shape (batch, H, W, channels)
          and weights shape (kh, kw, in_channels, out_channels). Reshape
          `image` to (1, H, W, 1) and `kernel` to (kh, kw, 1, 1) accordingly.
        - Set the layer's bias to 0 so the comparison is exact.
        - Build the layer with padding="valid", strides=(1, 1), so its
          output shape matches convolve2d's formula exactly.

    Example:
        >>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="float32")
        >>> kernel = np.array([[1, 0], [0, -1]], dtype="float32")
        >>> conv2d_with_keras(image, kernel)
        array([[-4., -4.],
               [-4., -4.]], dtype=float32)
    """
    raise NotImplementedError
