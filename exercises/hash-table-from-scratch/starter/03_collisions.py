"""
Stage 3 - Collision handling via chaining.

See EXERCISE.md for the full concept explanation and worked examples.

This file is self-contained: it re-declares hash_string and a full
ChainingHashTable class (rather than importing Stage 2's SimpleHashTable)
so each stage file stands alone. Reuse your own earlier implementation
as a starting point if you'd like.
"""


def hash_string(s: str, num_buckets: int) -> int:
    """
    Hash a string into a bucket index in range [0, num_buckets). Same
    function as Stage 1.
    """
    raise NotImplementedError


class ChainingHashTable:
    """
    A hash table that handles collisions via separate chaining: each
    bucket holds a list of (key, value) pairs instead of a single slot.

    We use chaining rather than open addressing because it's simpler to
    reason about and implement correctly (no probe sequences, no
    tombstones needed for deletion) at the cost of some memory overhead
    and worse cache locality than open addressing.

    Args:
        num_buckets: fixed number of buckets. Must be > 0.
    """

    def __init__(self, num_buckets: int = 8):
        raise NotImplementedError

    def insert(self, key: str, value) -> None:
        """
        Store value under key. Overwrites the value if key already exists
        in its bucket's chain, otherwise appends a new (key, value) pair.

        Example:
            >>> t = ChainingHashTable(4)
            >>> t.insert("a", 1)
            >>> t.insert("e", 2)  # "a" and "e" may collide in a 4-bucket table
            >>> t.lookup("a")
            1
            >>> t.lookup("e")
            2
            >>> t.insert("a", 99)
            >>> t.lookup("a")
            99
        """
        raise NotImplementedError

    def lookup(self, key: str):
        """
        Return the value stored under key by scanning its bucket's chain.

        Raises:
            KeyError: if key is not present.

        Example:
            >>> t = ChainingHashTable(4)
            >>> t.lookup("nope")
            Traceback (most recent call last):
                ...
            KeyError: 'nope'
        """
        raise NotImplementedError

    def __contains__(self, key: str) -> bool:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
