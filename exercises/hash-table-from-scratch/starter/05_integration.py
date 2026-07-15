"""
Stage 5 - Integration: does resizing actually help?

See EXERCISE.md for the full concept explanation and worked examples.

The ResizableHashTable class below is provided already working (a
finished version of Stage 4) so you can focus on the two new functions,
average_chain_length and demo_resize_effect, which are your job to
implement.
"""


def _hash_string(s: str, num_buckets: int) -> int:
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) % num_buckets
    return h % num_buckets


class ResizableHashTable:
    """
    A chaining hash table that supports deletion and automatically
    resizes (doubles bucket count and rehashes every entry) once the
    load factor (size / num_buckets) exceeds a threshold.

    Provided already working -- this is a finished version of Stage 4,
    given here so you can focus on the integration functions below.
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


def average_chain_length(table: ResizableHashTable) -> float:
    """
    Compute the average number of entries per bucket in `table`.

    This is a direct proxy for expected lookup cost: `lookup` on a
    chaining hash table scans the whole chain in its bucket, so the
    average chain length is the average number of comparisons a lookup
    does (ignoring hash computation itself).

    Args:
        table: a ResizableHashTable (or any object with a `.buckets`
            list of lists).

    Returns:
        size / num_buckets as a float. 0.0 for an empty table.

    Example:
        >>> t = ResizableHashTable(num_buckets=4, max_load_factor=1.0)
        >>> t.insert("a", 1)
        >>> t.insert("b", 2)
        >>> average_chain_length(t)
        0.5
    """
    raise NotImplementedError


def demo_resize_effect(num_keys: int = 40, num_buckets: int = 8, max_load_factor: float = 0.75) -> dict:
    """
    Insert `num_keys` distinct keys one at a time into a ResizableHashTable
    and record the average chain length just before and just after the
    *first* resize event, to demonstrate that resizing keeps average
    chain length (and therefore average lookup cost) roughly constant
    instead of growing linearly with the number of keys.

    Args:
        num_keys: total number of distinct keys to insert.
        num_buckets: initial bucket count.
        max_load_factor: resize threshold.

    Returns:
        A dict with keys:
            "avg_chain_length_just_before_resize": float, average chain
                length measured right before the insert that triggered
                the first resize (None if no resize happened).
            "avg_chain_length_just_after_resize": float, average chain
                length measured right after that same resize completed.
            "avg_chain_length_final": float, average chain length after
                all num_keys have been inserted.
            "final_num_buckets": int, bucket count at the end.

    Example:
        >>> stats = demo_resize_effect(num_keys=40, num_buckets=8, max_load_factor=0.75)
        >>> stats["avg_chain_length_just_before_resize"] > stats["avg_chain_length_just_after_resize"]
        True
        >>> stats["final_num_buckets"] >= 8
        True
    """
    raise NotImplementedError
