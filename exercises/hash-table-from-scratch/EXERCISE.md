# Build a Hash Table From Scratch

## The Big Picture

A **hash table** is a data structure that stores key-value pairs (like `"alice" -> 92`,
`"bob" -> 85`) and answers "what's the value for this key?" in roughly *constant* time,
no matter how many entries it holds. That's the entire pitch, and it's a bigger deal than it
sounds: if you stored the same pairs in a plain list of `(key, value)` tuples, looking one up
means scanning the list from the front until you find a matching key — on average you check
half the list, and in the worst case (key not present, or it's the last one) you check all of
it. That's **O(n)** — cost grows with how much data you have. A hash table gets you to
**O(1) on average** — roughly the same cost whether you have 10 entries or 10 million — by
trading "search for the key" for "compute where the key *must* be," which is the whole trick
this exercise builds, piece by piece.

**A real-world analogy: a wall of PO boxes.** Imagine a post office with 100 numbered PO
boxes instead of one giant room of loose mail. If mail addressed to "Alice Chen" always gets
sorted into box number 37 — via some fixed rule everyone agrees on, like "add up the letters
of the name and take the remainder when divided by 100" — then finding Alice's mail again
never means searching the building. You recompute "37" from her name and walk straight there.
A hash table is that post office: the array of buckets is the wall of PO boxes, and the hash
function is the sorting rule that turns a name into a box number.

**You've already used one, many times, without necessarily knowing it.** Every Python `dict`
you've ever written — `d["name"] = "Alice"`, `config["timeout"]`, `cache[user_id]` — is a hash
table under the hood. So is every database index that makes `WHERE user_id = 42` fast instead
of scanning every row. So is an in-memory cache (Redis, memcached) deciding which server or
slot owns a given key. So is your web browser's DNS cache mapping a hostname to an IP address
without re-asking a DNS server every time. Anywhere you've seen "fast lookup by key," a hash
table (or a close variant of one) was almost certainly doing the work.

**What this exercise builds, and how the pieces compose.** You'll build the mechanism up in
six stages, each one a working piece you can test on its own, that combine into a single
finished class by the end:

1. **The hash function** — the rule that turns a string key into a bucket index (the "which
   PO box does this name go in" rule).
2. **A naive bucket array** — insert and lookup that just trust the hash function completely
   and pretend two keys never land in the same box.
3. **Collision handling (chaining)** — fixing stage 2's lie, because two keys landing in the
   same box is not just possible but *mathematically guaranteed* once you have more keys than
   boxes.
4. **Delete and automatic resizing** — removing entries, and growing the bucket array before
   it gets so crowded that lookups stop being fast.
5. **Seeing it work end to end** — a small experiment that measures, with real numbers,
   whether stage 4's resizing is actually doing its job.
6. **Comparing to the real thing** — running the same operations against Python's built-in
   `dict` and confirming your from-scratch version agrees with it.

By stage 6 you'll have a complete, working `ResizableHashTable` you built entirely yourself,
and a concrete mental model for what CPython does every time you write `d[k] = v`.

**What this exercise does *not* build**, so you have the full conceptual map even for the
parts you won't personally implement: it does not build **open addressing** (the other
standard way to handle collisions, where a colliding key gets probed into a *different* slot
in the same array instead of appending to a list — this is what CPython's real `dict` actually
uses, and Stage 6 explains it at a conceptual level even though you won't implement it), and it
does not build a **Bloom filter** (a different, space-efficient data structure that answers a
weaker question — "have I possibly seen this key?" — using multiple hash functions and a bit
array instead of storing keys at all; mentioned again as a stretch idea at the end).

## What you'll build

A hash table, the same data structure backing Python's `dict`, built up in six stages: a
hash function, then bare-bones insert/lookup, then collision handling via chaining, then
delete and automatic resizing, then a small benchmark that shows *why* resizing matters, and
finally a head-to-head comparison against Python's real `dict`.

By the end you'll have a working `ResizableHashTable` class you wrote yourself, and a clear
mental model of what CPython's `dict` is doing under the hood every time you write `d[k] = v`.

## Learning objectives

By the end of this exercise you should be able to:

- Explain what a hash function needs to guarantee (determinism) and what it should aim for
  (roughly even distribution across buckets) — and why it doesn't need to be cryptographically
  secure.
- Explain why two different keys can land in the same bucket, why this is unavoidable once you
  have more possible keys than buckets (the pigeonhole principle), and implement a strategy
  (chaining) to handle it correctly.
- Explain what "load factor" is, why it's used as a resize trigger, and implement a resize
  that rehashes every existing entry into a larger bucket array.
- Point to the exact place in your code that corresponds to each part of Python's `dict` API,
  and explain (at a high level) how CPython's actual implementation differs from yours.

## Prerequisites

- Python 3.10+
- `pip install pytest`
- No other dependencies. Everything here uses only the standard library.

## Time estimate

**~60-90 minutes** for all six stages. Stage 1 is a five-minute warm-up; stages 2-4 are the
core of the exercise; stages 5-6 are shorter integration/comparison work.

## How to work through this

Each stage below gives you a real explanation of the sub-concept, a worked-by-hand trace on
small concrete numbers, an exact function/class signature with a docstring (worked examples
included), and the pytest command to check your work. Implement each stage in the matching
file under `starter/` before moving to the next — later stages assume you have a working
version of the earlier ones in your head, even though each starter file is self-contained (no
imports between stages, so you can jump around if you want, but the concepts build in order).

---

## Stage 1 — The hash function

**Concept.** A hash table is really just an array (the "buckets") plus a function that turns
a key into an array index. That function — the hash function — has exactly one hard
requirement: it must be **deterministic** (the same key always produces the same index, so
you can find something you already inserted). If `hash_string("cat", 10)` returned a
*different* number every time you called it, you could insert `"cat"` into bucket 2 and then
have no way to know to look in bucket 2 again — the whole structure would be useless. Beyond
determinism, a good hash function should **distribute keys roughly evenly** across the
available buckets, so you don't end up with one overstuffed bucket and a bunch of empty ones
(more on why that matters in Stage 3).

Notice what's *not* required: unlike a cryptographic hash (SHA-256), nothing here needs to be
hard to invert or resistant to someone deliberately engineering collisions — we only care
about speed and spread. (Real-world systems that hash attacker-controlled input, like a web
server, actually do need to worry about deliberately-engineered collisions — that's exactly
why Python randomizes its string hash per process, which Stage 6 explains.)

A simple, effective approach is a **polynomial rolling hash**: treat the string as a base-*k*
number (a common choice is *k* = 31) where each character contributes its ordinal value
(`ord('a') == 97`, `ord('b') == 98`, and so on — every character has a numeric code point), and
reduce modulo the number of buckets as you go, so the running total never needs to grow larger
than `num_buckets`.

**Worked by hand: `hash_string("cat", 10)`.** Start with a running hash `h = 0`. For each
character, update `h = (h * 31 + ord(char)) % num_buckets`, left to right:

```
h = 0
'c': ord('c') = 99   ->  h = (0 * 31 + 99)  % 10 = 99  % 10 = 9
'a': ord('a') = 97   ->  h = (9 * 31 + 97)  % 10 = 376 % 10 = 6
't': ord('t') = 116  ->  h = (6 * 31 + 116) % 10 = 302 % 10 = 2
```

So `hash_string("cat", 10) == 2` — "cat" belongs in bucket 2. Now trace `hash_string("dog",
10)` the same way:

```
h = 0
'd': ord('d') = 100  ->  h = (0 * 31 + 100) % 10 = 100 % 10 = 0
'o': ord('o') = 111  ->  h = (0 * 31 + 111) % 10 = 111 % 10 = 1
'g': ord('g') = 103  ->  h = (1 * 31 + 103) % 10 = 134 % 10 = 4
```

`hash_string("dog", 10) == 4` — a different bucket, no collision between these two. But
collisions absolutely do happen: trace `"rat"`, `"art"`, and `"tar"` (an anagram trio) with
`num_buckets = 10` the same way and you'll find **all three land in bucket 7**. Try it by hand
for at least one of them — it's the same three steps as above, just different letters and a
different order, and the order matters a lot: even though `"rat"`, `"art"`, and `"tar"` use
the exact same three characters, the polynomial hash weights *earlier* characters more heavily
(each one gets multiplied by 31 one extra time for every character that comes after it), so
which order they appear in changes the running total completely — it's a coincidence of the
arithmetic that these three specific rearrangements happen to land on the same bucket anyway.
This is your first real look at a **collision** — two different keys, same bucket index —
which Stage 3 exists entirely to handle.

**Signature.**

```python
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
```

**Worked examples.**

1. `hash_string("cat", 10) == hash_string("cat", 10)` — calling it twice on the same input
   gives the same output (determinism). From the by-hand trace above, this value is `2`.
2. `0 <= hash_string("hello", 8) < 8` — the result is always a valid bucket index, no matter
   the input string.
3. Edge case: `hash_string("", 5) == 0` — the empty string is a valid key; with no characters
   to accumulate, the running hash stays at its initial value of 0.

**Run it.**

```bash
pytest tests/test_01_hash_function.py -v
```

---

## Stage 2 — Insert and lookup, assuming no collisions

**Concept.** Before dealing with the messy case (two keys landing in the same bucket), get
the basic mechanism working: compute a bucket index with `hash_string`, and read/write that
slot directly. Picture the PO-box wall from the intro as an actual array: `buckets[0]`,
`buckets[1]`, ..., `buckets[num_buckets - 1]`, where each slot can hold exactly one `(key,
value)` pair. `insert("cat", 5)` computes `hash_string("cat", num_buckets)`, gets (say) `2`,
and writes `("cat", 5)` straight into `buckets[2]`. `lookup("cat")` recomputes the same index
and reads whatever is sitting in `buckets[2]`.

This stage is deliberately unrealistic — a second `insert` for a colliding key silently
overwrites whatever was there, even if it was a *different* key, quietly losing data. That's a
real bug in general (fixed next stage), but isolating "compute an index and touch an array
slot" from "handle two keys wanting the same slot" makes each piece easier to get right on its
own, which is the same reason a worked-by-hand trace comes before code: get one clean
mechanism working before layering the next concern on top of it.

**Signature.**

```python
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
        ...

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
```

**Worked examples.**

1. Insert `("a", 1)`, look up `"a"` -> `1`.
2. Insert `("a", 1)`, then insert `("a", 2)` (same key again) -> `lookup("a")` returns `2`
   (overwrite, not append).
3. Edge case: `lookup` on a key that was never inserted raises `KeyError`.

**Run it.**

```bash
pytest tests/test_02_insert_lookup.py -v
```

---

## Stage 3 — Collision handling via chaining

**Concept.** Here's why Stage 2's "assume no collisions" premise can't hold up in general —
and it's not just bad luck, it's a mathematical certainty. This is the **pigeonhole
principle**: if you have `num_buckets` boxes and you try to put more than `num_buckets` items
into them, at least one box must hold more than one item — there's simply nowhere else for the
extra ones to go. A hash table's bucket array has a fixed, finite size (say, 8 buckets), but
the space of possible string keys is effectively infinite. The moment you've inserted more
distinct keys than you have buckets, *some* bucket is guaranteed to receive two or more keys —
not "might," but *must*. And in practice it happens far sooner than that, because a hash
function distributing keys "roughly evenly" still means some buckets get unlucky well before
the array is full (this is the same math behind the "birthday paradox": with 23 people in a
room, there's already better-than-even odds two share a birthday, even though there are 365
"buckets" and only 23 "keys"). Stage 1's by-hand trace already produced one: `"rat"`, `"art"`,
and `"tar"` all hash to bucket 7 out of 10. Stage 2's table would let the second and third of
those silently erase each other. A collision, in other words, isn't an edge case to guard
against — it's the normal, expected operating condition of a hash table, and every real hash
table needs a real strategy for it.

**The fix: chaining.** Instead of each bucket holding a single `(key, value)` slot, make each
bucket hold a **list** of pairs — a "chain." Insert appends to (or updates within) the chain at
the computed index; lookup scans that chain for a matching key. Picture the mailbox analogy
again, but now each mailbox is deep enough to hold a small stack of letters instead of exactly
one: mail for both "rat" and "art" goes into box 7, and box 7 simply holds both — retrieving
"rat" means reaching into box 7 and flipping through its stack until you find the letter
addressed to "rat", ignoring "art"'s letter next to it. In ASCII form:

```
buckets:
  [0]  ->  []
  [1]  ->  [("bat", 5)]
  [2]  ->  []
  ...
  [7]  ->  [("rat", 1), ("art", 2), ("tar", 3)]   <- three keys chained in one bucket
  ...
```

`lookup("art")` computes `hash_string("art", 10) == 7`, goes straight to `buckets[7]` (still
O(1) — no searching to *find* the right bucket), and then does a short linear scan through
just that bucket's chain — 3 comparisons here, not all `num_buckets` buckets — to find the
entry whose key equals `"art"`.

We use **chaining** rather than **open addressing** (the other standard approach, where a
colliding key gets probed into a *different* slot in the same array, following some fixed
search sequence until an empty slot is found) because chaining is simpler to implement
correctly — there are no probe sequences to get right and no tombstones needed for deletion —
at the cost of some extra memory (one list per bucket, even if mostly empty) and worse cache
locality than a flat open-addressed array. This exercise builds chaining only; Stage 6 comes
back to open addressing when it explains what Python's real `dict` does instead.

**Signature.**

```python
class ChainingHashTable:
    """
    A hash table that handles collisions via separate chaining: each
    bucket holds a list of (key, value) pairs instead of a single slot.

    Args:
        num_buckets: fixed number of buckets. Must be > 0.
    """

    def __init__(self, num_buckets: int = 8):
        ...

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

    def __contains__(self, key: str) -> bool:
        ...

    def __len__(self) -> int:
        ...
```

**Worked examples.**

1. Insert two keys that happen to collide in a small (e.g. 4-bucket) table — both should still
   be independently retrievable. (Checkable by hand: with `num_buckets = 4`, both `"a"` and
   `"e"` hash to bucket 1 — trace it the same way as Stage 1's examples if you want to confirm
   it yourself.)
2. Insert the same key twice with different values -> the chain gets *updated in place*, not
   appended to (chain length should stay 1 for that key, and `len(table)` should not double
   count it).
3. Edge case: `lookup` on a missing key raises `KeyError`, even when its bucket's chain is
   non-empty (i.e., the chain has *other* keys' entries in it).

**Run it.**

```bash
pytest tests/test_03_collisions.py -v
```

---

## Stage 4 — Delete and resize

**Concept.** Two things a hash table needs to be genuinely useful: removing entries, and not
degrading into a pile of long chains as more keys get inserted into a fixed-size array.
`delete` is the more mechanical of the two — find the key's chain, remove its entry, and raise
`KeyError` if it isn't there.

Resizing is the more interesting piece, and it's the direct payoff of everything Stage 3 set
up. Define the **load factor** as `size / num_buckets` — the average number of entries per
bucket, where `size` is the total count of keys stored across the whole table. A load factor
of `0.5` means, on average, half a key per bucket; a load factor of `3` means, on average,
three keys are chained together in every bucket. Here's why that number matters: `lookup`'s
cost is "jump to the right bucket (O(1)) plus scan its chain (proportional to chain length)."
If chains stay short — a small constant, like 1 or 2 entries — lookup stays effectively O(1)
no matter how many total keys are in the table. But if you keep inserting keys into a
bucket array that never grows, the *average* chain length grows right along with the number of
keys, and lookup degrades toward O(n) — you're back to scanning a list, just a list that
happens to be split into pieces.

The fix is to pick a **load factor threshold** (a common choice is 0.75) and, whenever an
insert pushes the load factor above that threshold, allocate a bigger bucket array (commonly
double the size) and **rehash every existing entry** into it. The "rehash every entry" part is
essential and easy to get wrong: because `hash_string(key, num_buckets)` takes `num_buckets` as
an input, a key's bucket index is only valid for the *specific* bucket count it was computed
with. Grow the array from 4 buckets to 8 and every single existing key's correct new index has
to be recomputed from scratch — you can't just copy old bucket 2's chain into new bucket 2 and
call it done, because `hash_string("cat", 4)` and `hash_string("cat", 8)` are, in general,
different numbers.

**Signature.**

```python
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
        ...

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

    def lookup(self, key: str):
        """
        Return the value stored under key.

        Raises:
            KeyError: if key is not present.
        """

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

    def _resize(self, new_num_buckets: int) -> None:
        """Allocate new_num_buckets buckets and rehash every entry into them."""

    def __contains__(self, key: str) -> bool:
        ...

    def __len__(self) -> int:
        ...

    def load_factor(self) -> float:
        """Return size / num_buckets."""
```

**Worked examples.**

1. Insert 3 keys into a table with `num_buckets=4, max_load_factor=0.5`: the 3rd insert pushes
   load factor to 0.75, which exceeds 0.5, so `num_buckets` should double to 8 — and all three
   keys should still be correctly retrievable afterward (this is the part that catches bugs:
   it's easy to resize the array but forget to rehash a key correctly into its *new* index).
2. Delete a key, then look it up -> `KeyError`. Delete it a *second* time -> also `KeyError`
   (not, say, a silent no-op or an `IndexError` from some internal bookkeeping bug).
3. Edge case: after a resize, `len(table)` is unchanged (resizing moves entries, it doesn't
   add or drop any), and every key that was present before the resize is still present after.

**Run it.**

```bash
pytest tests/test_04_delete_resize.py -v
```

---

## Stage 5 — Integration: does resizing actually help?

**Concept.** Time to see the payoff of Stage 4's resize logic instead of just trusting the unit
tests. If chains got long and stayed long as you inserted more keys, lookup would slowly
degrade toward scanning a long list — the whole point of resizing is to keep the *average*
chain length (and therefore average lookup cost) roughly constant instead of growing with the
number of keys. This stage builds a small helper that measures average chain length right
around a resize event, so you can see the "sawtooth" pattern directly: chain length creeps up,
a resize happens, and it drops back down.

To make this concrete before any code: imagine watching `average_chain_length` after every
single insert as you add 40 keys to a table that starts with 8 buckets and a 0.75 load-factor
threshold. You'd see something like `0.125, 0.25, 0.375, ... , 0.75` — climbing steadily — and
then, the instant a resize fires (bucket count jumps from 8 to 16), the very next measurement
drops back down to roughly half of what it just was, because the same keys are now spread over
twice as many buckets. Then it climbs again until the *next* threshold crossing, and drops
again. That repeating climb-then-drop shape is the "sawtooth," and it's the direct, visible
evidence that resizing is doing its job of keeping lookups fast regardless of how many total
keys have been inserted.

**Signature.**

```python
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
```

**Worked examples.**

1. `average_chain_length` on a table with 2 entries and 4 buckets -> `0.5`.
2. `demo_resize_effect(num_keys=40, num_buckets=8, max_load_factor=0.75)` -> the average chain
   length measured right *before* the first resize should be strictly greater than the average
   chain length measured right *after* it — that drop is resizing doing its job.
3. Edge case: `demo_resize_effect(num_keys=2, num_buckets=100, max_load_factor=0.75)` — with a
   huge initial bucket count and only 2 keys, load factor never crosses the threshold, so no
   resize happens at all; `avg_chain_length_just_before_resize` should be `None`, not a crash.

**Run it.**

```bash
pytest tests/test_05_integration.py -v
```

---

## Stage 6 — Bridge to Python's built-in `dict`

**What `dict` actually is.** Every Python `dict` you've ever written is a hash table — the
exact mechanism you just spent five stages building, engineered far more carefully. Under the
hood, CPython's `dict` maintains an array sized to keep it sparse (well below full), a hash
function (`hash()`, built into the language) that maps each key to a slot, and a strategy for
handling two keys that want the same slot — this is precisely the "array + hash function +
collision strategy" description from the very first paragraph of this exercise, just written
by people who have spent decades optimizing every constant factor. `d[k] = v` is `insert`; `d[k]`
is `lookup`; `del d[k]` is `delete`; `dict` growing automatically as you add keys is exactly
your Stage 4 resize logic, just with different tuning constants.

**Concept — where the real thing diverges from what you built.** A few of the differences
worth knowing about, precisely because you now have your own implementation to compare them
against:

- CPython's `dict` uses **open addressing** (not chaining) with a probing scheme that mixes in
  extra bits of the hash ("perturbation") to avoid clustering. Concretely, instead of each
  bucket holding a list, open addressing has exactly one array and, on a collision, computes a
  *sequence* of alternative slots to try (derived from the key's hash) until it finds one that's
  either empty or already holds that same key. This avoids the extra memory overhead of a list
  per bucket, at the cost of a more intricate implementation (probe sequences, and — for
  deletion — "tombstone" markers so a probe sequence doesn't break when an entry along it gets
  removed). This is the collision-handling alternative Stage 3 mentioned but didn't build.
- Since Python 3.7, insertion order is preserved as a guaranteed language feature (iterating a
  `dict` yields keys in the order they were first inserted) — achieved via a separate compact
  array of insertion-ordered entries layered on top of the open-addressed hash table, not just
  an accidental side effect of the hashing scheme itself.
- `hash()` for strings is randomized per-process (a fresh random seed each time the Python
  interpreter starts), for security — it prevents "hash-flooding" denial-of-service attacks
  where an adversary who knows your hash function crafts many keys that all collide on
  purpose, deliberately degrading every lookup toward O(n) (exactly the failure mode Stage 4's
  resizing is designed to keep at bay under *normal* conditions, but resizing alone doesn't
  protect against someone deliberately engineering collisions the way Stage 1 noted a
  cryptographic hash would resist). Your Stage 1 `hash_string` is deliberately the simpler,
  fixed (non-randomized) polynomial hash, which is fine for this exercise's purposes but would
  be exploitable in exactly this way if it faced adversarial input in production.

The *interface* — insert, lookup, delete, resize automatically — is exactly the mental model
you now have from building it yourself; only the internals of collision handling and the extra
order-preserving bookkeeping differ.

This stage writes a small comparison: run the same operations against your
`ResizableHashTable` and against a real `dict`, and confirm they agree.

**Signature.**

```python
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
```

**Worked examples.**

1. `compare_with_builtin_dict([("a", 1), ("b", 2), ("c", 3)])` -> all three fields `True`.
2. A larger input, e.g. 50 distinct keys, all inserted then compared -> still all `True`, this
   time exercising your resize logic along the way (a `dict` never has to think about this;
   yours does, and it should be invisible to the caller when it's implemented correctly).
3. Edge case: an empty list `[]` -> both tables have length 0, `same_length` is `True`,
   `same_lookups` is vacuously `True` (nothing to check), and `same_after_delete` is `True`
   (no delete attempted, since there's no first key).

**Run it.**

```bash
pytest tests/test_06_bridge_to_dict.py -v
```

---

## Stretch (optional, not built out here)

A natural next step beyond this exercise: a **Bloom filter**, a space-efficient cousin of a
hash table that answers "have I possibly seen this key before?" using multiple hash functions
and a bit array instead of storing full keys — trading a small false-positive rate for much
lower memory use. If you want to keep going after Stage 6, try sketching (or fully
implementing) one using the `hash_string` function from Stage 1 as one of several hash
functions with different seeds.

---

## Bringing It All Together

Step back and look at the whole shape of what you just built. A hash table is "an array plus a
function that maps a key to an index, plus a strategy for what to do when two keys map to the
same index" — and you now have a concrete, working referent for every clause of that sentence,
sitting in your own `ResizableHashTable`:

- **"An array"** is `self.buckets`, allocated fresh every time `_resize` runs.
- **"A function that maps a key to an index"** is `hash_string`, which you traced by hand on
  `"cat"` and `"dog"` back in Stage 1 before you ever wrote a line of the class itself.
- **"A strategy for when two keys map to the same index"** is chaining — each bucket holding a
  small list, scanned linearly on lookup — which you needed because of the pigeonhole
  principle: finite buckets, unbounded possible keys, so collisions are guaranteed, not just
  possible.
- **"Keeping lookups fast as the table grows"** is `load_factor` and `_resize` together —
  doubling the bucket array and rehashing every entry whenever chains would otherwise start
  creeping toward O(n) scans, which Stage 5's `demo_resize_effect` let you actually watch
  happen as a real, measured drop in average chain length rather than something you had to
  take on faith.
- **"The interface a caller actually uses"** is `insert`, `lookup`, `delete`, `__contains__`,
  and `__len__` — the same shape as Python's own `dict`, which Stage 6 confirmed agrees with
  your implementation on every operation you compared.

**What you didn't build, and why that's fine.** This exercise deliberately built chaining, not
**open addressing** — the probing-based collision strategy that CPython's real `dict` actually
uses internally, trading chaining's simplicity for tighter memory use and better cache
behavior at the cost of a trickier implementation (probe sequences, tombstones for deletion).
You also didn't build a **Bloom filter**, a different, more specialized structure that drops
the ability to retrieve the original keys or values entirely in exchange for answering "have I
possibly seen this key?" using a fraction of the memory. Neither omission means this exercise
gave you a toy version of the idea — chaining is a completely legitimate, widely used
production strategy in its own right (Java's `HashMap` used it for years, and many
language runtimes still do) — it just means the conceptual map of "ways to build a hash table"
is bigger than the one slice you personally implemented, and now you know exactly what the
other slices are called and where to look if you want to build them next.

**Where this mechanism shows up once you start looking for it.** Every Python `dict` and every
similar structure in basically every other language (JavaScript objects and `Map`, Java's
`HashMap`, Go's `map`, Ruby's `Hash`) is a hash table doing this same job, just with decades of
tuning behind the constant factors. Database indexes frequently use hash indexes (as opposed to
the tree-based indexes used when range queries matter) for exactly the same reason you built
one: turning "scan every row for a match" into "compute where the match must be." In-memory
caches like Redis and memcached are, at their core, giant distributed hash tables — the whole
point of a cache is O(1) "do I already have this?" lookups, which is precisely the guarantee
your `ResizableHashTable` provides. And your computer's DNS resolver cache maps hostnames to IP
addresses using the same idea, so that visiting a site you loaded five minutes ago doesn't
require asking a DNS server all over again. None of these systems are doing something
conceptually different from what you just built six stages of — they're doing the same three
ideas (array, hash function, collision strategy) at a much larger scale, with much more
engineering, and, in the case of `dict`, a different collision strategy than the one you
picked. That gap between "the idea" and "the production-grade version of the idea" is exactly
the gap this exercise was designed to close.

## Want more than a static exercise?

Want to do this interactively instead, with hints and a review of your finished code? Install
the learn-by-building skill: [learn-by-building](https://github.com/csacademy-ma/learn-by-building)

## Run everything

Once all six stages are implemented, run the full suite from inside this exercise folder:

```bash
pytest tests/ -v
```
