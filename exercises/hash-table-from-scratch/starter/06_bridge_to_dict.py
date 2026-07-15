"""
Stage 6 - Bridge to Python's built-in dict.

See EXERCISE.md for the full concept explanation and worked examples.

The ResizableHashTable class below is provided already working (a
finished version of Stage 4) so you can focus on writing the comparison
function, compare_with_builtin_dict.
"""


def _hash_string(s: str, num_buckets: int) -> int:
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) % num_buckets
    return h % num_buckets


class ResizableHashTable:
    """
    A chaining hash table that supports deletion and automatic resizing.

    Provided already working -- this is a finished version of Stage 4,
    given here so you can focus on compare_with_builtin_dict below.
    """

    def __init__(self, num_buckets: int = 8, max_load_factor: float = 0.75):
        self.num_buckets = num_buckets
        self.max_load_factor = max_load_factor
        self.buckets = [[] for _ in range(num_buckets)]
        self.size = 0

    def _bucket_for(self, key: str):
        idx = _hash_string(key, self.num_buckets)
        return self.buckets[idx]

    def insert(self, key: str, value) -> None:
        chain = self._bucket_for(key)
        for i, (k, _) in enumerate(chain):
            if k == key:
                chain[i] = (key, value)
                return
        chain.append((key, value))
        self.size += 1
        if self.size / self.num_buckets > self.max_load_factor:
            self._resize(self.num_buckets * 2)

    def lookup(self, key: str):
        for k, v in self._bucket_for(key):
            if k == key:
                return v
        raise KeyError(key)

    def delete(self, key: str) -> None:
        chain = self._bucket_for(key)
        for i, (k, _) in enumerate(chain):
            if k == key:
                del chain[i]
                self.size -= 1
                return
        raise KeyError(key)

    def _resize(self, new_num_buckets: int) -> None:
        old_items = [(k, v) for chain in self.buckets for (k, v) in chain]
        self.num_buckets = new_num_buckets
        self.buckets = [[] for _ in range(new_num_buckets)]
        for k, v in old_items:
            self.buckets[_hash_string(k, self.num_buckets)].append((k, v))

    def __contains__(self, key: str) -> bool:
        return any(k == key for k, _ in self._bucket_for(key))

    def __len__(self) -> int:
        return self.size

    def load_factor(self) -> float:
        return self.size / self.num_buckets


def compare_with_builtin_dict(keys_and_values: list) -> dict:
    """
    Insert the same (key, value) pairs into both a ResizableHashTable
    (your implementation) and a Python built-in dict, then confirm they
    agree on every lookup, on membership, on length, and on delete.

    Args:
        keys_and_values: list of (key, value) tuples with distinct keys.

    Returns:
        A dict with keys:
            "same_length": bool, whether len(table) == len(builtin) after
                all inserts.
            "same_lookups": bool, whether every key looks up to the same
                value in both.
            "same_after_delete": bool, whether deleting the first key
                from both leaves them agreeing on membership for that key.

    Example:
        >>> result = compare_with_builtin_dict([("a", 1), ("b", 2), ("c", 3)])
        >>> result["same_length"], result["same_lookups"], result["same_after_delete"]
        (True, True, True)
    """
    raise NotImplementedError
