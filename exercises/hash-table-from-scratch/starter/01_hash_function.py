"""
Stage 1 - The hash function.

See EXERCISE.md for the full concept explanation and worked examples.
"""


def hash_string(s: str, num_buckets: int) -> int:
    """
    Hash a string into a bucket index in range [0, num_buckets).

    Uses a polynomial rolling hash: treat the string as a base-31 number
    where each character contributes its ordinal value, then reduce mod
    num_buckets.

    Args:
        s: the key to hash. May be empty.
        num_buckets: number of buckets to hash into. Must be > 0.

    Returns:
        An integer index i such that 0 <= i < num_buckets.

    Example:
        >>> hash_string("cat", 10) == hash_string("cat", 10)
        True
        >>> 0 <= hash_string("hello", 8) < 8
        True
        >>> hash_string("", 5)
        0
    """
    raise NotImplementedError
