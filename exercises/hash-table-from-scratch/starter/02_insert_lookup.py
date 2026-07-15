"""
Stage 2 - Insert and lookup, assuming no collisions.

See EXERCISE.md for the full concept explanation and worked examples.

This file is self-contained: it re-declares hash_string so you can work
on this stage without depending on your Stage 1 file. Feel free to reuse
your own Stage 1 implementation here once you have it working.
"""


def hash_string(s: str, num_buckets: int) -> int:
    """
    Hash a string into a bucket index in range [0, num_buckets). Same
    function as Stage 1 -- implement it here too (or paste your Stage 1
    solution in).
    """
    raise NotImplementedError


class SimpleHashTable:
    """
    A fixed-size hash table that assumes no two keys ever collide.

    (This is unrealistic in general -- it's here to isolate "compute an
    index and read/write an array slot" from collision handling, which
    comes in the next stage.)

    Args:
        num_buckets: fixed number of buckets. Must be > 0.
    """

    def __init__(self, num_buckets: int = 8):
        raise NotImplementedError

    def insert(self, key: str, value) -> None:
        """
        Store value under key. Overwrites any existing value for key.

        Example:
            >>> t = SimpleHashTable(8)
            >>> t.insert("a", 1)
            >>> t.lookup("a")
            1
            >>> t.insert("a", 2)
            >>> t.lookup("a")
            2
        """
        raise NotImplementedError

    def lookup(self, key: str):
        """
        Return the value stored under key.

        Raises:
            KeyError: if key was never inserted.

        Example:
            >>> t = SimpleHashTable(8)
            >>> t.lookup("missing")
            Traceback (most recent call last):
                ...
            KeyError: 'missing'
        """
        raise NotImplementedError
