"""
Stage 4 - Tamper detection.

See EXERCISE.md for the full concept explanation and worked examples.
"""


def flip_bit(data: bytes, bit_index: int) -> bytes:
    """
    Return a copy of data with exactly one bit flipped.

    Args:
        data: the original bytes.
        bit_index: which bit to flip, counting from 0 at the least
            significant bit of the first byte. Must satisfy
            0 <= bit_index < len(data) * 8.

    Returns:
        A new bytes object, same length as data, differing from it in
        exactly one bit.

    Example:
        >>> flip_bit(b"A", 0) != b"A"
        True
        >>> len(flip_bit(b"hello", 3)) == len(b"hello")
        True
    """
    raise NotImplementedError
