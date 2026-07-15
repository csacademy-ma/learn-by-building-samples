"""
Stage 4 - Delete and resize.

See EXERCISE.md for the full concept explanation and worked examples.

This file is self-contained: it re-declares hash_string and a full
ResizableHashTable class (rather than importing Stage 3's
ChainingHashTable) so each stage file stands alone. Reuse your own
earlier implementation as a starting point if you'd like.
"""


def hash_string(s: str, num_buckets: int) -> int:
    """
    Hash a string into a bucket index in range [0, num_buckets). Same
    function as Stage 1.
    """
    raise NotImplementedError


class ResizableHashTable:
    """
    A chaining hash table that supports deletion and automatically
    resizes (doubles bucket count and rehashes every entry) once the
    load factor (size / num_buckets) exceeds a threshold.

    Args:
        num_buckets: initial number of buckets. Must be > 0.
        max_load_factor: resize is triggered right after an insert makes
            size / num_buckets exceed this value.
    """

    def __init__(self, num_buckets: int = 8, max_load_factor: float = 0.75):
        raise NotImplementedError

    def insert(self, key: str, value) -> None:
        """
        Store value under key, then resize if the load factor now
        exceeds max_load_factor.

        Example:
            >>> t = ResizableHashTable(num_buckets=4, max_load_factor=0.5)
            >>> t.insert("a", 1)
            >>> t.insert("b", 2)  # size=2, load factor 2/4=0.5, no resize yet
            >>> t.num_buckets
            4
            >>> t.insert("c", 3)  # size=3, load factor 3/4=0.75 > 0.5 -> resize
            >>> t.num_buckets
            8
            >>> t.lookup("a"), t.lookup("b"), t.lookup("c")
            (1, 2, 3)
        """
        raise NotImplementedError

    def lookup(self, key: str):
        """
        Return the value stored under key.

        Raises:
            KeyError: if key is not present.
        """
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """
        Remove key (and its value) from the table.

        Raises:
            KeyError: if key is not present.

        Example:
            >>> t = ResizableHashTable()
            >>> t.insert("a", 1)
            >>> t.delete("a")
            >>> t.delete("a")
            Traceback (most recent call last):
                ...
            KeyError: 'a'
        """
        raise NotImplementedError

    def _resize(self, new_num_buckets: int) -> None:
        """Allocate new_num_buckets buckets and rehash every entry into them."""
        raise NotImplementedError

    def __contains__(self, key: str) -> bool:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def load_factor(self) -> float:
        """Return size / num_buckets."""
        raise NotImplementedError
