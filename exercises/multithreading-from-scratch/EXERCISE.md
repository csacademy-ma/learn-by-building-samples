# Multithreading From Scratch

## The Big Picture

A **thread** is the smallest unit of instructions your CPU actually schedules and runs.
A single program (process) can have many threads running "at the same time" inside it,
all sharing the same memory — the same variables, the same objects, the same everything.
That sharing is the whole point (it's how threads cheaply pass data back and forth
without copying it), and it's also exactly where the danger comes from: if two threads
read and write the same piece of memory without any coordination, the result depends on
the precise, unpredictable order in which the operating system happens to interleave
their instructions. **Concurrency** is running multiple threads of work in overlapping
time; **synchronization** is the set of tools you use to keep shared memory correct
despite that overlap. This entire exercise is about synchronization — because
concurrency by itself is easy, it's the "shared state" part that's hard.

**A real-world analogy.** Picture two cashiers sharing one physical till that currently
has $50 in it. Cashier A processes a $10 refund: she opens the till, notes it currently
holds $50, closes it to grab a receipt printout, then reopens it and puts $60 back in.
Cashier B, working at the exact same moment, does a $5 refund: he opens the till (still
showing $50, because Cashier A hasn't put her $60 back yet), walks off to staple a
receipt, comes back, and puts $55 back in. Whoever closes the till *last* wins — the
till ends up with either $60 or $55, when it should have ended up with $65 ($50 + $10 +
$5). One of the two refunds is silently lost, not because either cashier made a mistake,
but because neither of them checked the till's *current* contents at the moment they
actually put money back — they both worked off a stale reading. That is precisely the
shape of every bug in this exercise: a shared value gets read, some independent work
happens, and then the value gets written back based on a now-outdated read.

**You've already benefited from this, whether you noticed or not.** Every web server
that answers hundreds of requests per second without making everyone else queue up
behind one at a time is running a pool of threads (or an equivalent). Every app that
lets you keep scrolling and tapping while a file downloads in the background, instead of
freezing the whole screen, is keeping that download on its own thread so it doesn't
block the one thread drawing your UI. The synchronization primitives you're about to
build by hand are the same category of tool — locks, condition variables, thread pools —
that make both of those things safe rather than a source of silent data corruption.

**How the five stages compose.** Stage 1 makes the bug real and visible: you'll build a
shared counter with zero protection and watch concurrent increments get lost, so "race
condition" stops being an abstract warning and becomes a number on your screen that's
wrong. Stage 2 fixes exactly that bug with the simplest tool available, a
`threading.Lock`, turning the unsafe read-modify-write into an atomic one. Stage 3 asks
you to build something structurally harder: a bounded queue that has to make threads
*wait* (not just briefly block) until a condition becomes true — full producers must
pause until there's room, empty consumers must pause until there's something to take —
which needs a second tool, `threading.Condition`, layered on top of a lock. Stage 4
introduces a worse failure mode than a wrong number: a **deadlock**, where two threads
each wait forever for a resource the other is holding, and you'll both cause one on
purpose and then fix it. Stage 5 is the payoff: you'll discover that `queue.Queue` and
`concurrent.futures.ThreadPoolExecutor`, two standard-library tools you may have used
without knowing what was inside them, are essentially the exact lock+condition machinery
you just built by hand, wrapped up and hardened.

**What this exercise does NOT cover**, so you have an accurate map of the wider topic:

- **`multiprocessing`** — Python's answer to CPU-bound parallelism (actual simultaneous
  computation across CPU cores), which needs separate *processes* rather than threads
  because of the GIL (explained in Stage 1). Not built here; different memory model
  entirely (each process gets its own memory, so it needs its own kind of communication —
  pipes, shared memory segments — instead of the shared-variable problems this exercise
  is about).
- **`async`/`await`** — a completely different concurrency model for high-volume I/O
  (thousands of open network connections, for instance) that uses a single thread and
  cooperative scheduling instead of OS threads. Not built here.
- **Semaphores** — a generalization of a lock that allows up to *N* threads in
  simultaneously (rather than a lock's strict 1), commonly used to cap concurrent access
  to a limited resource pool (e.g. at most 5 simultaneous database connections). Not
  built here.
- **Reader-writer locks** — allow unlimited concurrent *readers* but exclusive
  *writers*. This one is described (not built) as this exercise's stretch section at the
  end, once you have the lock/condition fundamentals to reason about it.

## What you'll build

A tour of thread synchronization built entirely from Python's `threading` and `queue`
standard library modules, working from "watch it break" up to "use the real tools
correctly." By the end you will have:

1. Reproduced a genuine race condition on a shared counter and watched it corrupt data.
2. Fixed it with a hand-used `threading.Lock`.
3. Built a bounded, thread-safe producer/consumer queue from a lock + condition variable
   (the same mechanism `queue.Queue` uses internally).
4. Constructed a two-lock deadlock on purpose, detected it programmatically (with a
   timeout, so a hung program can't hang your test suite), and fixed it via lock ordering.
5. Rebuilt the producer/consumer pipeline using `queue.Queue` and `ThreadPoolExecutor`,
   and confirmed which of your hand-built pieces map to which stdlib pieces.

## Learning objectives

- Understand *why* concurrent access to shared mutable state is unsafe, in concrete
  terms (an interleaved read-modify-write), not just as a rule to follow.
- Use a `threading.Lock` correctly to make a critical section atomic.
- Implement blocking bounded-queue semantics using a lock and a condition variable,
  the actual mechanism behind `queue.Queue`.
- Recognize the two-lock (circular wait) precondition for deadlock, and know the
  standard fix: a single, globally agreed-upon lock acquisition order.
- Map your own hand-built primitives onto `queue.Queue` and `ThreadPoolExecutor`, so
  those stdlib tools stop being black boxes.

## Prerequisites

- Python 3.10+
- `pip install pytest`
- Standard library only: `threading`, `queue`, `concurrent.futures`. No third-party
  packages.
- Comfortable with basic Python (functions, classes, `with` statements). No prior
  concurrency experience assumed.

## Time estimate

**~90 minutes to 2 hours.** This is the fuller, 5-stage version of this exercise (there's
also a trimmed ~45-60 minute version that drops the producer/consumer and deadlock
stages if you're short on time — this file is the full one).

## How to work through this

Each stage below has: a real explanation of the sub-concept (written assuming you may be
hearing terms like "mutex" or "condition variable" for the first time), a worked-by-hand
trace on small numbers so you can see the mechanism happen before any code exists, an
exact function/class signature with a docstring (your target — this is already written
into the matching file in `starter/`), 2-3 worked examples, and the exact `pytest`
command to check your work. Implement the stage in the matching `starter/NN_*.py` file
(replace `raise NotImplementedError` with your code), then run that stage's test file
before moving on. Don't peek at later stages first — each one builds on the shape of the
last.

---

## Stage 1 — See the race

**What a race condition actually is, at the instruction level.** `count = count + 1`
looks like one step in Python source code, but it is not one step to the machine. It is
at least three:

1. **Read** the current value of `count` out of memory.
2. **Compute** the new value (add 1 to what you just read).
3. **Write** the new value back to memory.

If exactly one thread ever runs this sequence at a time, it works perfectly — read 5,
compute 6, write 6. The trouble starts when two threads can interleave those three steps
with each other, because the CPU/OS scheduler is free to pause any thread after any one
of those steps and run a different thread for a while. Nothing in the three-step
sequence above tells the scheduler "don't interrupt me in the middle of this."

**A worked-by-hand trace.** Say the shared counter currently holds `5`, and Thread A and
Thread B each want to increment it once. Here is one legal interleaving the scheduler is
free to choose — a step-by-step trace, not just a description:

| Step | Thread A                  | Thread B                  | Actual value in memory |
|------|----------------------------|----------------------------|-------------------------|
| 1    | reads `count` → gets `5`  |                            | 5                       |
| 2    |                            | reads `count` → gets `5`  | 5                       |
| 3    | computes `5 + 1 = 6`       |                            | 5                       |
| 4    |                            | computes `5 + 1 = 6`       | 5                       |
| 5    | writes `6` back            |                            | 6                       |
| 6    |                            | writes `6` back            | 6                       |

Two increments happened. The counter should now read `7`. It reads `6`. Thread B's
"read 5" happened *before* Thread A's "write 6" landed, so Thread B computed its new
value from data that was about to become stale — and when Thread B writes, it overwrites
Thread A's update with a value computed from the same starting point. This is called a
**lost update**, and it is the single most common shape of race condition you will ever
debug. Note that both threads did completely correct arithmetic (`5 + 1 = 6` is right
both times) — the bug isn't in the math, it's in the *scheduling gap* between reading
and writing shared state.

**Why this is genuinely rare to see by accident on CPython — and why the exercise forces
it.** CPython (the Python interpreter you're almost certainly running) has something
called the **Global Interpreter Lock**, or **GIL**: a single lock that ensures only one
thread executes Python bytecode at any given instant, even on a multi-core machine. This
surprises a lot of people the first time they hear it — doesn't that mean races are
impossible? No: the GIL can still switch which thread is running *between* bytecode
instructions, including in the middle of the read/compute/write sequence above (each of
those is itself several bytecode instructions). What the GIL actually gives you is
"no two threads execute a *single bytecode instruction* simultaneously" — it does not
give you "your three-line increment is atomic." In practice the scheduler's actual switch
points land badly often enough to cause real bugs in production code, but rarely enough
in a tight, fast loop that a test could pass by luck almost every run — which would make
for a useless, flaky test. So this stage adds one deliberate yield point,
`time.sleep(0)`, between the read and the write, to force a scheduling handoff right in
the dangerous gap. **This is not cheating** — it doesn't change what bug exists, only how
reliably the unlucky interleaving happens, exactly like adding an artificial network
delay to reliably reproduce a rare UI race condition. The underlying problem (an
unprotected read-modify-write) is exactly as real without the sleep; you'd just need many
more trials to see it with your own eyes.

**Signature.**

```python
class UnsafeCounter:
    """
    A counter incremented from multiple threads with NO synchronization.

    Attributes:
        value: the running total. Starts at 0.
    """

    def __init__(self) -> None:
        self.value = 0

    def increment(self) -> None:
        """
        Read the current value, yield control, then write back value + 1.

        Example:
            >>> c = UnsafeCounter()
            >>> c.increment()
            >>> c.value
            1
        """
        ...


def run_unsynchronized_increments(num_threads: int, increments_per_thread: int) -> int:
    """
    Spin up `num_threads` threads, each calling `counter.increment()`
    `increments_per_thread` times on a single shared UnsafeCounter, then
    return the final counter value after all threads finish.

    Args:
        num_threads: how many threads to start.
        increments_per_thread: how many times each thread calls increment().

    Returns:
        The final value of a fresh UnsafeCounter after all threads join.
    """
    ...
```

The `threading` module is Python's standard tool for running functions concurrently
inside the current process, sharing the same memory space. A `threading.Thread(target=fn,
args=(...))` object represents one such thread; calling `.start()` on it schedules `fn`
to begin running concurrently with everything else, and calling `.join()` on it blocks
the calling code until that thread has finished. You'll use exactly this pattern —
create several `Thread` objects targeting `increment`-calling work, `start()` them all,
then `join()` them all before reading the final value — in
`run_unsynchronized_increments`.

**Worked examples.**

```python
>>> c = UnsafeCounter()
>>> c.increment()
>>> c.value
1

>>> result = run_unsynchronized_increments(4, 1000)
>>> result <= 4000
True
>>> # result is frequently LESS than 4000 -- lost updates. That's the race.

>>> run_unsynchronized_increments(0, 100)   # edge case: no threads at all
0
>>> run_unsynchronized_increments(4, 0)     # edge case: threads do nothing
0
```

**Implement it in:** `starter/01_see_the_race.py`

**Run it:**
```
pytest tests/test_01_see_the_race.py -v
```

---

## Stage 2 — Lock the counter

**What a lock (mutex) actually guarantees.** A `threading.Lock` — often called a
**mutex**, short for "mutual exclusion" — is a simple object with exactly one guarantee:
at most one thread can be "holding" it at any moment. Any other thread that tries to
acquire it (via `lock.acquire()`, or by entering a `with lock:` block, which acquires on
entry and releases on exit even if an exception is raised) simply pauses — it doesn't
spin, doesn't error, it just waits — until the thread currently holding the lock releases
it. Wrapping a block of code in a lock turns that block into a **critical section**: a
region where the "only one thread at a time" guarantee makes the interleaving from Stage
1's trace table structurally impossible, because a second thread cannot get in between
another thread's read and write anymore — it's stuck waiting at the door.

**The same trace, now with a lock.** Revisit the Stage 1 table, but this time Thread A
wraps its read/compute/write in `with self._lock:`:

| Step | Thread A                                  | Thread B                                   | Actual value |
|------|---------------------------------------------|----------------------------------------------|---------------|
| 1    | acquires lock, reads `count` → `5`          | tries to acquire lock → **blocks, waits**    | 5             |
| 2    | computes `5 + 1 = 6`                        | (still waiting)                              | 5             |
| 3    | writes `6`, releases lock                   | (still waiting)                              | 6             |
| 4    |                                               | acquires lock (now free), reads `count` → `6`| 6             |
| 5    |                                               | computes `6 + 1 = 7`                          | 6             |
| 6    |                                               | writes `7`, releases lock                     | 7             |

Now the counter correctly reads `7`. Thread B was physically prevented from reading until
Thread A's write had already landed and the lock was released — there is no longer a
window where both threads can be holding a stale read at the same time.

Here's the shape, already solved, of the *unsynchronized* version from stage 1, so you
can see exactly what changes:

```python
# Stage 1 (unsafe):
def increment(self) -> None:
    current = self.value
    time.sleep(0)
    self.value = current + 1
```

Your job in stage 2 is the same three lines, wrapped in `with self._lock:`.

**Signature.**

```python
class SafeCounter:
    """
    A counter incremented from multiple threads, protected by a
    threading.Lock so the final value is always correct.

    Attributes:
        value: the running total. Starts at 0.
    """

    def __init__(self) -> None:
        self.value = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        """
        Safely read-modify-write the counter under self._lock.

        Example:
            >>> c = SafeCounter()
            >>> c.increment()
            >>> c.value
            1
        """
        ...


def run_synchronized_increments(num_threads: int, increments_per_thread: int) -> int:
    """
    Same driver shape as stage 1's run_unsynchronized_increments, but
    using SafeCounter. The result must always equal
    num_threads * increments_per_thread -- no exceptions, no flakiness.
    """
    ...
```

**Worked examples.**

```python
>>> run_synchronized_increments(4, 1000)
4000
>>> run_synchronized_increments(8, 500)
4000
>>> run_synchronized_increments(1, 0)   # edge case: no work
0
```

Unlike stage 1, run this one 10 times in your head (or literally, in the test) — it
should be *exactly* right every single time. If it isn't, the lock isn't actually
covering the whole read-modify-write.

**Implement it in:** `starter/02_lock_the_counter.py`

**Run it:**
```
pytest tests/test_02_lock_the_counter.py -v
```

---

## Stage 3 — Producer/consumer with a bounded queue

**The concept, and why a plain lock isn't enough for it.** A bounded queue is a
fixed-capacity FIFO buffer shared between "producer" threads (which add items) and
"consumer" threads (which remove them). It needs two *blocking* behaviors:

- `put(item)` must block while the queue is full (don't overflow the buffer).
- `get()` must block while the queue is empty (don't return nothing).

A plain `Lock` only tells you "wait until nobody else is in this section" — it has no
concept of "wait until some *condition* about the data becomes true." You could try to
fake it by looping: `while queue_is_full(): pass` (this is called **busy-waiting**), but
that burns an entire CPU core spinning in a tight loop doing nothing useful, for
potentially a long time, and you'd still need a lock around the check to avoid racing on
the queue's internal state anyway.

The right tool is a **`threading.Condition`**: it lets a thread call `.wait()`, which
atomically releases an associated lock and puts the thread to sleep (using zero CPU)
until another thread calls `.notify()` (or `.notify_all()`) on the same condition — at
which point the sleeping thread wakes up, reacquires the lock, and continues. A
`Condition` is built *on top of* a `Lock` (you can even construct one from an existing
lock, `threading.Condition(existing_lock)`), which is exactly what lets a `not_full`
condition and a `not_empty` condition below share one underlying lock and both safely
protect the same queue's internal list.

**A small ASCII diagram: the assembly line with limited trays.** Picture a physical
assembly line with exactly 3 trays between a builder (producer) and a packer (consumer):

```
  producer                trays (capacity 3)              consumer
  --------                ------------------               --------
   builds ---> [ 1 ][ 2 ][ 3 ][   ][   ] ---> takes oldest, packs it
               (3 trays full, 2 empty slots)
```

If all 3 trays are full, the builder has nowhere to put the next item — she has to stop
and wait until the packer clears a tray. If all the trays are empty, the packer has
nothing to take — he has to stop and wait until the builder fills one. Neither of them
should spin in place repeatedly asking "is there room yet? is there room yet?" — that's
the busy-waiting problem above. Instead, imagine each of them can ring a bell exactly
when the state they're waiting on changes (a tray just freed up / a tray just got filled)
and otherwise sit down and do nothing until the bell rings. That bell is exactly what
`Condition.notify()` is, and "sit down and do nothing until the bell rings" is exactly
what `Condition.wait()` is.

**A worked-by-hand trace of `put` on a capacity-1 queue.** Say `BoundedQueue(capacity=1)`
is currently empty, and Thread P wants to `put("x")` while Thread C is already blocked
inside `get()` waiting for something to arrive:

1. Thread C entered `get()` earlier, checked "is the queue empty?" → yes, called
   `self._not_empty.wait()`, which released the lock and put Thread C to sleep.
2. Thread P calls `put("x")`: acquires the lock (free, since C released it in step 1),
   checks "is the queue full?" → no (it's empty, capacity 1), appends `"x"`.
3. Thread P calls `self._not_empty.notify()` — this wakes Thread C up, but Thread C
   cannot actually resume running yet because it needs the lock back, which Thread P
   still holds.
4. Thread P exits its `with self._not_full:` block, releasing the lock.
5. Thread C reacquires the lock (now free), resumes right after its `.wait()` call,
   *rechecks* "is the queue empty?" → no, pops `"x"`, returns it.

Step 5's recheck is important: the standard pattern for a blocking wait is always a
`while` loop around the check, not an `if` — you must recheck the condition after waking
up, because in general another thread could have grabbed the newly available slot/item
in the gap between the `notify()` and this thread actually resuming (imagine a second
consumer also waiting — only one of them should get `"x"`, and whichever one reacquires
the lock first and rechecks wins it fairly):

```python
with self._not_full:
    while len(self._items) >= self._capacity:
        self._not_full.wait()
    self._items.append(item)
    self._not_empty.notify()
```

That snippet above is effectively the whole of `put` — `get` is the mirror image
(wait while empty, pop from the left, notify `not_full`).

**Signature.**

```python
class BoundedQueue:
    """
    A fixed-capacity FIFO queue safe for concurrent producers/consumers,
    built from a threading.Lock + threading.Condition.

    Args:
        capacity: maximum number of items the queue can hold at once.
                  Must be >= 1.
    """

    def __init__(self, capacity: int) -> None:
        ...

    def put(self, item) -> None:
        """
        Block until there is room, then append `item` to the queue.

        Example:
            >>> q = BoundedQueue(capacity=2)
            >>> q.put(1)
            >>> q.put(2)
            >>> q.size()
            2
        """
        ...

    def get(self):
        """
        Block until an item is available, then pop and return the oldest one.

        Example:
            >>> q = BoundedQueue(capacity=2)
            >>> q.put("a")
            >>> q.get()
            'a'
        """
        ...


def run_producer_consumer(
    num_items: int, capacity: int, num_producers: int = 1, num_consumers: int = 1
) -> list:
    """
    Produce integers 0..num_items-1 spread across `num_producers` producer
    threads and consume them with `num_consumers` consumer threads sharing
    one BoundedQueue(capacity). Return the sorted list of consumed items.
    """
    ...
```

**Worked examples.**

```python
>>> run_producer_consumer(num_items=10, capacity=3)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> run_producer_consumer(num_items=100, capacity=1, num_producers=4, num_consumers=4)
[0, 1, 2, ..., 99]   # every item delivered exactly once, order of arrival may vary

>>> q = BoundedQueue(capacity=1)
>>> q.put("only slot")
>>> # a second put() here would block until something calls get()
```

**Edge case / hint:** consumers need to know when production is *finished*, or the last
consumer left waiting on `get()` will block forever after the final real item. A common
trick: once all producers are done, push a sentinel object onto the queue. When a
consumer pops the sentinel, it should push it back (so any other still-waiting consumers
also see it) before returning.

**Implement it in:** `starter/03_producer_consumer.py`

**Run it:**
```
pytest tests/test_03_producer_consumer.py -v
```

---

## Stage 4 — Deadlock, on purpose (then fix it)

**What a deadlock actually is.** A **deadlock** happens when two (or more) threads each
hold a resource the other needs, and neither will ever release what it holds — so both
wait forever. This is a fundamentally different, and in some ways worse, failure than
Stage 1's race condition: a race gives you a *wrong number*, which is bad but at least
your program finishes and you can inspect the result. A deadlock gives you a program that
never finishes at all.

**A worked-by-hand trace of the classic two-lock deadlock.** Say Thread 1 needs `lock_a`
then `lock_b`, and Thread 2 needs `lock_b` then `lock_a` (note the opposite order):

| Step | Thread 1                                  | Thread 2                                  |
|------|---------------------------------------------|----------------------------------------------|
| 1    | acquires `lock_a`                            |                                                |
| 2    |                                               | acquires `lock_b`                             |
| 3    | tries to acquire `lock_b` → **blocks** (Thread 2 holds it) |                                |
| 4    |                                               | tries to acquire `lock_a` → **blocks** (Thread 1 holds it) |

At step 4, look at the state: Thread 1 is asleep waiting for `lock_b`, which is held by
Thread 2 — and Thread 2 is asleep waiting for `lock_a`, which is held by Thread 1.
Neither thread can proceed, and neither thread can release what it's holding, because
releasing happens *after* the blocked acquire in each thread's code, which never returns.
This mutual, circular waiting is called a **circular wait**, and it's the defining
precondition of a deadlock. It also is not intermittent, like Stage 1's race — once both
threads reach step 3/4, this configuration never resolves on its own, no matter how long
you wait.

**Why you can't just call the function and see what happens.** Because a genuine deadlock
hangs forever, calling the deadlocking code directly and waiting for it to return would
hang your test (and this exercise's grader) too. The standard way to test for a hang
*without* risking an actual hang is: run the possibly-hanging code in a background
thread, `join(timeout=...)` it, and check `.is_alive()` afterward. `join(timeout=...)`
always returns control to you after at most `timeout` seconds — it just may return while
the background thread is still stuck running. If `.is_alive()` is `True` after a generous
timeout, you've confirmed the thread is stuck, without ever having to wait an unbounded
amount of time yourself.

**The fix: lock ordering.** If *every* thread that needs both locks always acquires them
in the same global order (say, always `lock_a` before `lock_b`), the circular wait
becomes structurally impossible. Trace why: for a cycle to form, some thread would need
to be holding `lock_b` while waiting for `lock_a` — but under a single fixed order,
nothing ever acquires `lock_b` before `lock_a`, so that configuration simply cannot
arise. This is the standard, simplest fix used in real systems (e.g. always locking
database rows in a consistent ID order to prevent transaction deadlocks) — no timeout,
no detection needed, just an invariant that rules the bad interleaving out entirely.

**Signature.**

```python
def run_deadlock_and_detect(timeout: float = 1.0) -> bool:
    """
    Start two threads that acquire two locks in OPPOSITE order (the
    classic two-lock deadlock) and detect whether they actually hang.

    Thread 1: acquire lock_a, sleep briefly (e.g. time.sleep(0.2)), then
    try to acquire lock_b.
    Thread 2: acquire lock_b, sleep briefly, then try to acquire lock_a.

    Start both as daemon threads, then join each with `timeout` seconds
    and report whether either is still alive afterward.

    Returns:
        True if at least one thread was still alive after `timeout`
        seconds (a deadlock was observed). False if both finished.

    Example:
        >>> run_deadlock_and_detect(timeout=1.0)
        True
    """
    ...


def run_safe_transfer_and_detect(timeout: float = 1.0) -> bool:
    """
    Fixed version: make BOTH threads acquire the locks in the SAME
    global order (lock_a, then lock_b, in both threads).

    Returns:
        True if both threads finished within `timeout` seconds (expected:
        always True). False if either was still alive.

    Example:
        >>> run_safe_transfer_and_detect(timeout=1.0)
        True
    """
    ...
```

**Worked examples.**

```python
>>> run_deadlock_and_detect(timeout=1.0)
True     # both threads got stuck -- this IS the expected, "successful" result

>>> run_safe_transfer_and_detect(timeout=1.0)
True     # same workload, consistent lock order -- finishes cleanly every time

>>> # edge case: a very short timeout still correctly reports "stuck" for
>>> # the deadlocking version, since a real deadlock never resolves no
>>> # matter how long you wait
>>> run_deadlock_and_detect(timeout=0.1)
True
```

Notice the inverted intuition here: for `run_deadlock_and_detect`, the test that proves
you did this stage correctly *expects* `True` (i.e. expects the hang). That's the point
of this stage — you're not avoiding the bug yet, you're proving you can reliably cause
it, before fixing it in the second function.

**Implement it in:** `starter/04_deadlock.py`

**Run it:**
```
pytest tests/test_04_deadlock.py -v
```

(This test file has its own internal watchdog thread as a second line of defense, so
even a badly broken submission — e.g. an infinite loop instead of a lock wait — cannot
hang the test run indefinitely.)

---

## Stage 5 — Bridge to `queue.Queue` and `ThreadPoolExecutor`

**What `queue.Queue` actually is.** `queue.Queue` is Python's standard-library,
production-ready bounded queue. Everything you built by hand in Stage 3 — the lock, the
two condition variables, the full/empty blocking logic, the careful `while`-loop recheck
after waking up — is exactly what `queue.Queue(maxsize=N)` already gives you, battle
tested and written in C for speed. `q.put(item)` blocks when full; `q.get()` blocks when
empty. You get the identical correctness guarantees you just hand-built, without writing
the `Condition` bookkeeping yourself ever again.

**What `concurrent.futures.ThreadPoolExecutor` actually is.** Instead of manually
creating `threading.Thread` objects, starting them, and joining them (which is what
Stages 1-4 had you do by hand), `ThreadPoolExecutor` manages a pool of worker threads for
you: you submit callables to it and it hands back `Future` objects. A `Future` represents
"a result that will exist eventually," and calling `.result()` on one blocks until that
particular piece of work finishes and then gives you its return value directly — solving
a real gap in raw `threading.Thread`, which has no built-in way to hand a return value
back to the caller at all (Stage 3's `run_producer_consumer` had to smuggle results out
through a shared list precisely because of this).

This stage asks you to solve the *same* producer/consumer task from stage 3 again,
now using these stdlib tools — and also a second, simpler "task-parallel" example
(no shared mutable state to protect, just independent work farmed out to a pool),
which is the other common reason people reach for threads.

**Signature.**

```python
def run_producer_consumer_stdlib(
    num_items: int, capacity: int, num_producers: int = 1, num_consumers: int = 1
) -> list:
    """
    Same producer/consumer task as stage 3, but built on
    queue.Queue(maxsize=capacity) and ThreadPoolExecutor instead of your
    hand-rolled BoundedQueue and raw threading.Thread.
    """
    ...


def sum_of_squares_threadpool(numbers: list, max_workers: int = 4) -> int:
    """
    Compute sum(n * n for n in numbers) by farming each square out to a
    ThreadPoolExecutor and summing the results.
    """
    ...
```

**Worked examples.**

```python
>>> run_producer_consumer_stdlib(num_items=10, capacity=3)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> sum_of_squares_threadpool([1, 2, 3, 4])
30
>>> sum_of_squares_threadpool([])   # edge case: empty input
0
```

**What maps to what:**

| Your stage 3 piece | stdlib equivalent |
|---|---|
| `BoundedQueue.__init__(capacity)` | `queue.Queue(maxsize=capacity)` |
| `BoundedQueue.put` (blocks when full) | `Queue.put` |
| `BoundedQueue.get` (blocks when empty) | `Queue.get` |
| manually created/joined `threading.Thread`s | `ThreadPoolExecutor` + `Future.result()` |
| a shared list + a lock to collect results | `Future.result()` / `as_completed()` |

**Implement it in:** `starter/05_bridge_to_threadpool.py`

**Run it:**
```
pytest tests/test_05_bridge_to_threadpool.py -v
```

---

## Stretch (described only, not built out here)

**Reader-writer lock.** A plain `Lock` forces every thread to wait even when multiple
threads only want to *read* shared state — reads never conflict with other reads, only
with writes. A reader-writer lock lets any number of readers hold it simultaneously, but
gives a writer exclusive access (blocking all readers and other writers) while it holds
it. If you want to try this yourself: track a reader count and a writer flag, protected
by a plain `Lock` and a `Condition`; `acquire_read()` blocks while a writer holds or is
waiting (to avoid writer starvation), `acquire_write()` blocks while any readers or
another writer hold it. This is a genuinely open-ended design task — there's no single
correct answer for how to balance reader throughput against writer starvation, which is
exactly what makes it a good stretch exercise once you're comfortable with stages 1-5.

---

## Running everything

From inside this exercise's folder:

```
pytest tests/ -v
```

All 5 stages' tests should pass once every `starter/*.py` file is filled in.

---

## Bringing It All Together

Step back and look at what you actually have now. You have a `SafeCounter` that turns an
unprotected, three-step read-modify-write into a single atomic operation using a
`threading.Lock` — the fix for Stage 1's lost updates. You have a `BoundedQueue` that
makes producer and consumer threads wait for exactly the right condition (room to put,
or an item to get) without burning CPU in a busy-loop, using a `threading.Condition`
layered on that same kind of lock. You have a `run_deadlock_and_detect` /
`run_safe_transfer_and_detect` pair that demonstrates the other major way concurrent code
goes wrong — not a wrong answer, but a program that never finishes — and the one-line
discipline (a single global lock order) that rules it out completely. And you've seen
that `queue.Queue` and `ThreadPoolExecutor`, tools you may previously have imported
without a second thought, are just hardened, general-purpose versions of the exact
mechanisms you built by hand in Stages 2 and 3.

That's the core of thread synchronization: shared mutable state is dangerous the moment
more than one thread can touch it without coordination, and the tools that make it safe
— locks for mutual exclusion, condition variables for "wait until a condition holds,"
consistent lock ordering to prevent circular waits — are a small, learnable set that
covers the overwhelming majority of real concurrency bugs.

As flagged in the opening, a few adjacent tools exist that this exercise deliberately did
not build, so you know where the edges of what you just learned are:

- **`multiprocessing`** — when your bottleneck is actual CPU computation rather than
  waiting on I/O, threads don't help you use multiple cores in CPython, because the GIL
  (Stage 1) still only lets one thread run Python bytecode at a time. `multiprocessing`
  sidesteps this by using separate OS processes, each with its own interpreter and its
  own GIL, at the cost of a heavier communication model (no shared memory by default).
- **`async`/`await`** — for workloads dominated by waiting on network I/O across
  thousands of connections at once, an async event loop (a single thread, cooperatively
  switching between tasks at `await` points) often scales better than one OS thread per
  connection. Different programming model, same underlying goal of "do many things that
  spend most of their time waiting."
- **Semaphores** — the generalization of a lock to "at most N threads at once" instead of
  "at most 1," useful for capping concurrent access to a limited pool of some resource
  (e.g. database connections, open file handles).
- **Reader-writer locks** — sketched in the Stretch section above, for workloads with
  many concurrent readers and occasional writers.

**Where this shows up for real.** Web servers use thread pools (or the event-loop
equivalent) to serve many simultaneous requests without one slow client blocking
everyone else. Databases use fine-grained locking (often at the row or page level, with
carefully chosen lock ordering, exactly like Stage 4) to let many transactions run
concurrently without corrupting data or deadlocking. Game engines run physics,
rendering, and audio on separate threads that must synchronize shared world state every
frame. Desktop and mobile apps keep expensive work — network calls, file I/O, large
computations — off the one thread that draws the UI, which is precisely why your screen
doesn't freeze while a file downloads in the background. Every one of those systems is,
underneath, doing some combination of exactly what you just built: an atomic critical
section, a wait-until-ready queue, and a discipline for avoiding deadlock.

---

Want to do this interactively instead, with hints and a review of your finished code?
Install the learn-by-building skill: [learn-by-building](https://github.com/csacademy-ma/learn-by-building)
