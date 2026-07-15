# Build Digital Signatures From Scratch

## The Big Picture

Say Alice sends Bob a message: `"Transfer $1000 to Bob."` Bob wants two guarantees before he
acts on it: **it really came from Alice** (not an impostor pretending to be her), and **nobody
changed it in transit** (it wasn't `"Transfer $10 to Bob"` before someone edited the zero). A
**digital signature** is a piece of data, computed from the message and something only Alice
possesses, that gives Bob both guarantees mathematically — without Alice and Bob ever having
shared a secret password in advance, and without Bob having to trust some middleman who "vouches"
for the message by fiat.

That last part is the interesting bit. If Alice and Bob had already agreed on a shared secret
(like a password), Alice could prove her identity by using that secret. But that requires them to
have met beforehand and exchanged something in private. Digital signatures solve a harder, more
useful problem: Alice can prove a message is hers to a total stranger who she has never
communicated with before, using only a piece of information Alice makes **public**. This is
called **asymmetric cryptography** — "asymmetric" because the two sides use *different* keys
(one private, one public) instead of the *same* shared secret. That asymmetry is what makes it
possible for anyone, anywhere, to check Alice's signature without ever being trusted with the
ability to forge one.

**A real-world analogy.** Think of a wax letter seal from centuries past. A noble would press
their own uniquely-carved signet ring into hot wax on a letter. Anyone receiving the letter could
look at the wax impression and recognize whose ring made it — the pattern was public knowledge,
visible on every letter that noble ever sent. But forging it required physically possessing the
one-of-a-kind ring, which never left the noble's hand. The wax seal is the signature; the
recognizable carved pattern is the public key; the physical ring that makes the impression is
the private key. Nobody needs to have met the noble in person to recognize their seal — they just
need to have seen it once, genuinely, before. A handwritten signature works the same way: easy
for anyone to recognize (roughly), very hard for someone else to reproduce convincingly, and it
becomes suspect the instant something around it looks tampered with.

**You've already relied on this, repeatedly, without noticing.** Every time your browser shows a
padlock icon on an HTTPS website, a digital signature (as part of a larger protocol called TLS)
proved that the server you're talking to really controls the private key associated with that
domain. Every time your phone or laptop downloads a software update, a signature check silently
verifies that the update was really built by Apple/Google/Microsoft/etc. and not tampered with by
whoever runs the WiFi network you're on. Every "Verified" badge next to a commit on GitHub is a
digital signature over that commit's contents, checked against the committer's public key. You
have been a beneficiary of this mechanism dozens of times this week alone.

**What this exercise builds, in order.** You'll build the mechanism underneath all of that, piece
by piece, using numbers small enough to check by hand: **Stage 1** warms up on the general idea
of a "one-way" function using a simple (non-cryptographic) hash. **Stage 2** builds the actual
engine of RSA — modular exponentiation — and uses it to generate a tiny, deliberately insecure
RSA keypair. **Stage 3** wires that keypair into real `sign` and `verify` functions and gets a
genuine sign-then-verify round trip working. **Stage 4** proves, concretely, that tampering with
so much as a single bit breaks verification. **Stage 5** is a design task: your scheme, as built,
has a real vulnerability (replay attacks), and you'll reason about how real systems close it.
**Stage 6** bridges everything to Python's real `cryptography` package, so you see your toy
`sign`/`verify` functions' real-world counterparts in action.

**What a real RSA key actually looks like.** Here's an illustrative (and deliberately truncated
and fake — do not try to use this) example of what an actual RSA private key looks like when
you generate one on a real computer:

```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1c7+9z5Pad7OejecsQ0bu3aumgSFQeeAvxhDkYVZ9L7oNMK4
YQ91kSMboKcNaNSVfa2LKn3aiZLLBSWn/9CGmTaeFhguqzej8gz4Wr8dTJHf1sry
... (many more base64-encoded lines) ...
-----END RSA PRIVATE KEY-----
```

That block of base64 text *is* a real RSA keypair, encoded into a portable text format (called
PEM). Buried inside that base64 gibberish are exactly the same ingredients you're about to build
by hand: two large prime numbers, their product `n`, and the exponents `e` and `d`. The only
difference is scale — those primes are hundreds of digits long, which is precisely why nobody can
trace the arithmetic by eye. This exercise uses primes small enough to write on a napkin (`p = 61`,
`q = 53`) so you can watch the *exact same mechanism* that key uses, just at a size a human brain
can actually verify step by step.

## What you'll build

A digital signature scheme, built up from primitives you already trust: a hash function, then
modular exponentiation, then a *toy* RSA keypair, then sign/verify functions, a demonstration of
why tamper detection matters, a design challenge about a real vulnerability class, and finally a
bridge to Python's real `cryptography` package.

By the end you'll have hand-built `sign` and `verify` functions that actually work
arithmetically, and a clear mental model of what's happening underneath every call to a real
signing library — plus firsthand experience with why "it verifies" is not the same question as
"is this scheme actually secure."

## Learning objectives

By the end of this exercise you should be able to:

- Explain what a one-way function needs to guarantee, and why real cryptography uses a
  battle-tested primitive (SHA-256) instead of a hand-rolled one.
- Implement modular exponentiation from scratch and explain why it's the core operation behind
  RSA.
- Explain, in one or two sentences, what a digital signature actually proves: something only the
  private-key holder could have produced, that anyone with the public key can check, and that an
  attacker without the private key cannot forge.
- Demonstrate why signatures detect tampering — and explain, concretely, why "verifies
  correctly" is not the same claim as "this scheme is secure against every attack."
- Point to the exact place in your toy scheme where a replay/reuse attack would land, and
  describe at least one real-world mitigation.
- Map the API shape of your toy sign/verify functions onto the real `cryptography` package's
  API.

## Prerequisites

- Python 3.10+
- `pip install pytest cryptography` — `cryptography` is only needed for Stage 6 (the bridge
  stage); Stages 1-4 use only the standard library (`hashlib`).

## A big warning before you start

**The toy RSA keypair you'll build in this exercise is NOT secure and must never be used to
protect anything real.** It uses primes small enough to factor by hand or with a pocket
calculator (`n = 3233 = 61 * 53`). Real RSA uses primes on the order of **1024+ bits each**
(so `n` is ~2048+ bits), chosen randomly and tested for primality with serious statistical
tests, plus padding schemes (like OAEP/PSS) this exercise doesn't touch at all. Nothing here is
suitable for signing an actual document, a software release, or a login token. The entire point
is to make the *mechanism* concrete enough that the real thing (Stage 6) stops being a black
box — not to hand you a usable cryptosystem.

## Time estimate

**~90 minutes - 2 hours** for all six stages. Stages 1-2 are shorter warm-ups; Stages 3-4 are
the core of the exercise; Stage 5 is a short prose design task (no code); Stage 6 is a
comparison against a real library.

## How to work through this

Each stage below gives you a concept explanation with a worked-by-hand trace, an exact function
signature with a docstring (worked examples included), and the pytest command to check your
work. Implement each stage in the matching file under `starter/` before moving to the next —
later stages build on earlier ones conceptually (Stage 3 uses Stage 2's `modexp`, Stage 4 uses
Stage 3's `sign`/`verify`), so work through them in order.

---

## Stage 1 — Warm-up: a one-way-ish function

**Concept.** A cryptographic hash function is easy to compute in one direction (message -> a
fixed-size digest) but computationally infeasible to invert (digest -> message) or to find two
different messages that hash to the same digest. This "easy forward, hard backward" property is
called being **one-way**. It's the same intuition as mixing paint: combining blue and yellow into
green takes one second; starting from a can of green paint and recovering the exact original
blue and yellow is, for all practical purposes, not something you can undo.

Before touching real cryptographic hashing, build a **non-cryptographic** one-way-*ish* function
to get the shape of the idea: a **polynomial rolling hash**, which treats a string as a base-*k*
number (each character contributes its ordinal value, i.e. its numeric code point — `ord('a') ==
97`) reduced modulo some large number. It's easy to compute forward, and annoying (though not
actually hard, in a cryptographic sense — a computer could brute-force short strings that produce
a given rolling hash in well under a second) to invert. This is deliberately a much weaker
function than what real systems use; the point of Stage 1 is only to get comfortable with "turn
text into a bounded integer, deterministically" before Stage 3 does the same thing with a real
cryptographic hash.

We use this toy hash only to warm up on "one-way-ish" as a concept. For every real
cryptographic use later in this exercise (Stages 2 onward), we switch to Python's
`hashlib.sha256` rather than reimplementing SHA-256 ourselves. That's a deliberate scope
boundary, not laziness: SHA-256's actual internals (message padding, 64 rounds of bit
operations, a specific set of round constants) are a substantial topic in their own right and
orthogonal to *this* exercise's point, which is how signatures use a hash, not how a
cryptographic hash is built. A rolling hash is easy to invert or collide by hand (small search
space, no avalanche property — flipping one input character only nudges the output by a
small, predictable amount); SHA-256 is designed so that flipping a single input bit scrambles
roughly half the output bits unpredictably (the "avalanche effect"), making inversion or
collision-finding infeasible even with enormous computing power.

**Worked-by-hand trace.** Let's trace `rolling_hash("ab", base=131, mod=10**9 + 7)` exactly the
way the code will need to, before writing any code. The idea: start an accumulator `h = 0`, then
for each character in order, do `h = (h * base + ord(char)) % mod`.

- Start: `h = 0`.
- First character `'a'`, `ord('a') == 97`: `h = (0 * 131 + 97) % mod = 97`.
- Second character `'b'`, `ord('b') == 98`: `h = (97 * 131 + 98) % mod`. Compute `97 * 131 =
  12707`, then `12707 + 98 = 12805`. `12805 % (10**9 + 7) == 12805` (it's far smaller than the
  modulus, so the modulo is a no-op here).
- Result: `12805`.

That's it — the entire "algorithm" is: walk the string once, and at each step, multiply the
running total by `base` and add in the new character's ordinal value, keeping everything reduced
mod `mod` so the number never grows unboundedly large. Everything after this stage in the
exercise reuses this same "walk once, accumulate" shape, just with different (real) building
blocks.

**Signature.**

```python
def rolling_hash(s: str, base: int = 131, mod: int = 10 ** 9 + 7) -> int:
    """
    Hash a string using a polynomial rolling hash: treat s as a base-`base`
    number where each character contributes its ordinal value, reduced
    modulo `mod` at every step.

    Args:
        s: the string to hash. May be empty.
        base: the polynomial base. Should be larger than the alphabet size
            (131 comfortably covers ASCII).
        mod: the modulus to keep the running hash bounded.

    Returns:
        An integer in range [0, mod).

    Example:
        >>> rolling_hash("hello") == rolling_hash("hello")
        True
        >>> rolling_hash("")
        0
        >>> rolling_hash("ab", base=131, mod=10**9 + 7)
        12805
    """
    raise NotImplementedError
```

**Worked examples.**

1. `rolling_hash("hello") == rolling_hash("hello")` — determinism: same input always gives the
   same output.
2. Edge case: `rolling_hash("") == 0` — with no characters to accumulate, the running hash stays
   at its initial value.
3. Hand-traceable example: `rolling_hash("ab", base=131, mod=10**9 + 7)`. Trace it yourself:
   start with `h = 0`. For `'a'` (ord 97): `h = (0 * 131 + 97) % mod = 97`. For `'b'` (ord 98):
   `h = (97 * 131 + 98) % mod = 12707 + 98 = 12805`. Result: `12805` (matches the trace above —
   confirm your implementation agrees).

**Run it.**

```bash
pytest tests/test_01_rolling_hash.py -v
```

---

## Stage 2 — Toy asymmetric keys

**Concept.** RSA's core operation is **modular exponentiation**: computing `base^exp mod n`
efficiently, without ever materializing the astronomically large intermediate number
`base**exp` would be if computed directly. To see why that matters: even with small toy numbers,
`4 ** 13` is only 67,108,864 — perfectly manageable — but real RSA exponents are numbers hundreds
of digits long, and `base ** exp` computed directly would be a number with more digits than atoms
in the observable universe, long before you ever got to the `% mod` part. Modular exponentiation
avoids ever forming that giant intermediate number.

The trick is **repeated squaring**: look at `exp` in binary. Walk through its bits from least
significant to most significant. At each step, square the current base (mod `n`) to get the
"next power of two" contribution, and whenever the current bit of `exp` is `1`, multiply that
contribution into a running result. This turns an exponentiation that would otherwise take `exp`
sequential multiplications into one that takes only about `log2(exp)` — for a 2048-bit RSA
exponent, that's the difference between roughly 2^2048 multiplications (utterly impossible) and
roughly 2048 of them (instant on any computer).

**Worked-by-hand trace: `modexp(4, 13, 497)` via repeated squaring.** First, write `13` in
binary: `13 = 0b1101`, i.e. bits (from least significant / rightmost to most significant) are
`1, 0, 1, 1`. Keep a running `result = 1` and a running squared-base `b`, starting at
`b = base % mod = 4`.

| step | current bit of 13 | action | result after this step | b squared for next step |
|---|---|---|---|---|
| 1 | 1 (rightmost) | bit is 1 -> multiply `result` by `b`: `1 * 4 = 4` | 4 | `4*4 = 16` |
| 2 | 0 | bit is 0 -> skip the multiply | 4 (unchanged) | `16*16 = 256` |
| 3 | 1 | bit is 1 -> multiply: `4 * 256 = 1024`, `1024 % 497 = 30` | 30 | `256*256 mod 497 = 429` |
| 4 | 1 (leftmost) | bit is 1 -> multiply: `30 * 429 = 12870`, `12870 % 497 = 445` | 445 | (no more bits — stop) |

Final result: **445**. That matches the worked example below, and you can check it against
Python's own `pow(4, 13, 497)`, which will also give `445` — that three-argument form of `pow` is
exactly modular exponentiation, already built into the language, which is also why it's such a
convenient way to self-check your own implementation once you've written it.

Once you have `modexp`, you can build a **toy RSA keypair**: pick two (small!) prime numbers
`p` and `q`, compute `n = p * q` and `phi = (p-1) * (q-1)`, pick a public exponent `e` that's
coprime with `phi` (65537 is the real-world standard choice, but any valid coprime works — this
exercise uses small values so you can trace the numbers), and compute the private exponent `d`
as the modular inverse of `e` mod `phi` (given to you below, since modular inverse via the
extended Euclidean algorithm is a detour from this exercise's point). "Coprime" just means two
numbers share no common factors other than 1 — it's the condition that guarantees `e` actually
has a modular inverse `d` at all.

**Worked-by-hand trace: building the toy keypair.** With `p = 61`, `q = 53`, `e = 17`:
`n = p * q = 61 * 53 = 3233`. `phi = (p-1) * (q-1) = 60 * 52 = 3120`. Given `e = 17`, the modular
inverse of `17` mod `3120` turns out to be `d = 2753` (you can sanity check this yourself:
`(17 * 2753) % 3120` should equal `1` — try it on a calculator, since finding `d` from scratch
requires the extended Euclidean algorithm, provided for you below rather than derived here).
`public_key = (e, n) = (17, 3233)`, `private_key = (d, n) = (2753, 3233)`.

**IMPORTANT: this is a toy.** The classic textbook example above uses `p = 61`, `q = 53`
(giving `n = 3233`) — primes small enough to factor by inspection. **Real RSA uses primes with
hundreds of decimal digits (~1024+ bits each)**, chosen randomly and verified probabilistically
prime (e.g. via Miller-Rabin), specifically because factoring their product is intractable.
Never use small primes like these for anything beyond understanding the mechanism.

Already-solved helper (modular inverse via the extended Euclidean algorithm — a standard number
theory routine that's a detour from this exercise's actual point):

```python
def _modinv(a: int, m: int) -> int:
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        g, x1, y1 = extended_gcd(b % a, a)
        return g, y1 - (b // a) * x1, x1
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError("no modular inverse")
    return x % m
```

**Signatures.**

```python
def modexp(base: int, exp: int, mod: int) -> int:
    """
    Compute (base ** exp) % mod efficiently using repeated squaring,
    without computing base ** exp directly.

    Args:
        base: the base.
        exp: the exponent. Must be >= 0.
        mod: the modulus. Must be > 0.

    Returns:
        (base ** exp) % mod.

    Example:
        >>> modexp(4, 13, 497)
        445
        >>> modexp(7, 128, 3233) == pow(7, 128, 3233)
        True
        >>> modexp(5, 0, 97)
        1
    """
    raise NotImplementedError


def generate_toy_keypair(p: int = 61, q: int = 53, e: int = 17):
    """
    Build a toy RSA keypair from two small primes.

    NOT SECURE. p and q here are small enough to factor by hand; this is
    for understanding the mechanism only.

    Args:
        p: a prime number.
        q: a different prime number.
        e: the public exponent. Must be coprime with (p-1)*(q-1).

    Returns:
        A tuple (public_key, private_key), where:
            public_key is (e, n)
            private_key is (d, n)
        with n = p * q and d = modular inverse of e mod (p-1)*(q-1).

    Raises:
        ValueError: if e is not coprime with (p-1)*(q-1).

    Example:
        >>> public_key, private_key = generate_toy_keypair()
        >>> public_key
        (17, 3233)
        >>> private_key
        (2753, 3233)
    """
    raise NotImplementedError
```

**Worked examples.**

1. `modexp(4, 13, 497) == 445` — a classic hand-traceable textbook example (matches the trace
   above).
2. `modexp(7, 128, 3233) == pow(7, 128, 3233)` — your implementation should agree with Python's
   own built-in three-argument `pow`, which does exactly this (a great way to self-check).
3. Edge case: `modexp(5, 0, 97) == 1` — anything to the power 0 is 1, even under a modulus.
4. `generate_toy_keypair()` with the defaults (`p=61, q=53, e=17`) gives `n = 61 * 53 = 3233`,
   `phi = 60 * 52 = 3120`, and `d = 2753` (you can verify `(17 * 2753) % 3120 == 1` by hand).

**Run it.**

```bash
pytest tests/test_02_modexp_toy_rsa.py -v
```

---

## Stage 3 — Sign and verify

**Concept.** A signature scheme needs three properties: something only the private-key holder
can produce, that anyone with the public key can check, and that nobody without the private key
can forge. This is a fundamentally different (and stronger) guarantee than a plain **checksum**
(like a CRC or even a bare SHA-256 hash of a file) — a checksum only proves a message wasn't
*accidentally corrupted* (e.g. by a flaky network), because anyone at all can recompute a
checksum from scratch, including an attacker who wants to forge a new "valid" one for a message
they altered. A signature additionally proves *who* produced it, because computing a valid one
requires a specific private value nobody else has. "This file's checksum matches" means "this
file wasn't scrambled by noise." "This file's signature verifies" means "someone holding this
specific private key deliberately produced exactly these bytes."

RSA gives us this almost for free, using the fact that `modexp` with `e` and `modexp`
with `d` are inverses of each other (that's exactly what Stage 2's key generation set up):
raising a number to the power `e` and then to the power `d` (mod `n`) gets you back where you
started, precisely because `e` and `d` were chosen as modular inverses of each other mod
`phi(n)`. Whoever holds `d` (the private key) can do something nobody else can: transform a
hash `h` into `h^d mod n` in a way that's only "correct" if you actually possess `d`. Everyone
holding the matching public key `(e, n)` can undo that transformation and check that it lands
back on the expected hash — but undoing it doesn't require ever knowing `d` itself, which is the
whole point of the asymmetry.

To **sign** a message: hash it down to a number smaller than `n` (using real `hashlib.sha256`,
per Stage 1's discussion — not the rolling hash), then raise that hash to the power `d` (the
private exponent) mod `n`. Only someone holding `d` can produce this value for a given hash.

To **verify** a signature: hash the message the same way, raise the signature to the power `e`
(the public exponent, which anyone can know) mod `n`, and check whether the result matches the
hash. If the signature was produced with the matching private key, `modexp(modexp(h, d, n), e, n)
== h`, because `e` and `d` are modular inverses mod `phi(n)`.

**Worked-by-hand trace: a full sign-then-verify round trip.** Use the toy keypair from Stage 2:
`public_key = (17, 3233)`, `private_key = (2753, 3233)`. Take the tiny message `b"hi"`.

1. **Hash the message down to a number smaller than `n`.** `hashlib.sha256(b"hi")` produces a
   32-byte digest; interpreting those bytes as one big integer and reducing mod `n = 3233` gives
   some specific number — call it `h`. (You don't need to compute SHA-256 by hand — that's
   exactly why Stage 1 discussed *not* hand-rolling a real cryptographic hash. Trust that `h`
   comes out to a fixed, deterministic integer in `[0, 3233)`; running `hash_to_int(b"hi", 3233)`
   yourself will show you `h = 1686`.)
2. **Sign: raise `h` to the private exponent `d`, mod `n`.** `sig = modexp(1686, 2753, 3233)`.
   Carrying out that modular exponentiation (the same repeated-squaring mechanism you just built
   in Stage 2, just with bigger numbers than the `modexp(4, 13, 497)` trace) gives `sig = 2794`.
3. **Verify: raise the signature back up by the public exponent `e`, mod `n`, and compare to the
   hash.** `modexp(2794, 17, 3233)` comes back out to `1686` — exactly the hash we started with
   in step 1. Since it matches, `verify` returns `True`.

Notice what just happened end to end: the private exponent `2753` transformed the hash into
something ("the signature") that only someone holding `2753` could have produced, and the public
exponent `17` — which anyone can know — was enough to check it, without ever needing `2753`
itself. That round trip, `modexp(modexp(h, d, n), e, n) == h`, is the entire mechanism a
digital signature rests on.

Already-solved helper (hashing a message down to an integer smaller than `n`):

```python
import hashlib

def hash_to_int(message: bytes, n: int) -> int:
    """Hash message with SHA-256 and reduce the result mod n."""
    digest = hashlib.sha256(message).digest()
    return int.from_bytes(digest, "big") % n
```

**What `hashlib.sha256` actually does.** SHA-256 is a specific, standardized algorithm that
takes an input of any length and always produces exactly 256 bits (32 bytes) of output, with the
one-way and avalanche properties discussed in Stage 1, at a strength real cryptographers have
spent decades trying (and failing) to break. To make "hash digest" concrete instead of abstract,
try this yourself:

```python
>>> import hashlib
>>> hashlib.sha256(b"hello").hexdigest()
'2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b982'
```

That's a real SHA-256 digest: 64 hexadecimal characters, representing the same 256 bits shown as
readable text instead of raw bytes. Change even one character of the input (`b"Hello"` instead of
`b"hello"`) and essentially every character of that output changes unpredictably — that's the
avalanche effect from Stage 1, made concrete. `hash_to_int` above just takes that digest, reads
it as one giant integer instead of hex text, and reduces it mod `n` so it fits in the same
numeric range RSA's modular arithmetic operates in.

**Signatures.**

```python
def sign(message: bytes, private_key) -> int:
    """
    Sign message using the private key.

    Args:
        message: the message bytes to sign.
        private_key: a tuple (d, n) as returned by generate_toy_keypair.

    Returns:
        The signature: hash_to_int(message, n) raised to the power d, mod n.

    Example:
        >>> public_key, private_key = generate_toy_keypair()
        >>> sig = sign(b"Attack at dawn", private_key)
        >>> isinstance(sig, int)
        True
    """
    raise NotImplementedError


def verify(message: bytes, signature: int, public_key) -> bool:
    """
    Verify that signature is a valid signature of message under public_key.

    Args:
        message: the message bytes that were (allegedly) signed.
        signature: the signature to check.
        public_key: a tuple (e, n) as returned by generate_toy_keypair.

    Returns:
        True if signature**e mod n equals hash_to_int(message, n),
        False otherwise.

    Example:
        >>> public_key, private_key = generate_toy_keypair()
        >>> sig = sign(b"Attack at dawn", private_key)
        >>> verify(b"Attack at dawn", sig, public_key)
        True
        >>> verify(b"Attack at dusk", sig, public_key)
        False
    """
    raise NotImplementedError
```

**Worked examples.**

1. Using the default toy keypair (`public_key = (17, 3233)`, `private_key = (2753, 3233)`),
   `sign(b"Attack at dawn", private_key)` produces some integer signature, and
   `verify(b"Attack at dawn", that_signature, public_key)` returns `True`.
2. The same signature checked against a *different* message
   (`verify(b"Attack at dusk", that_signature, public_key)`) returns `False` — the signature is
   bound to the exact bytes that were signed.
3. Edge case: a signature that's off by exactly 1 (`sig + 1` instead of `sig`) fails to verify —
   there's no "close enough" in modular exponentiation; a single unit of difference changes the
   result completely.

**Run it.**

```bash
pytest tests/test_03_sign_verify.py -v
```

---

## Stage 4 — Tamper detection

**Concept.** This is the "aha" moment for why signatures matter: a signature isn't just a
label saying "this is legitimate" — it's cryptographically *bound* to the exact bytes of the
message. Flip a single bit anywhere in the message (or the signature), and verification should
fail, because SHA-256 (and modular exponentiation) have no notion of "close" inputs producing
"close" outputs — a one-bit change produces a completely different hash, and a completely
different expected signature. This is exactly why tampering breaks verification: `verify`
recomputes the hash of whatever bytes it's given right now, and compares that fresh hash against
what the signature actually encodes — if even one bit differs, the freshly computed hash and the
signed hash diverge completely (again, the avalanche effect), so the equality check fails.

This stage doesn't add new cryptographic machinery — it's a focused demonstration, using
Stage 3's `sign`/`verify`, of a property they already have. The only new piece is a small
utility to flip a single bit in a byte string so you can construct the "tampered" input
precisely.

**Worked-by-hand trace.** Take the single byte `b"A"`. In binary, the ASCII code for `'A'` is
`65 = 0b01000001`. `bit_index = 0` refers to the least significant bit (the rightmost one) of
the first byte. Flipping that bit turns `0b01000001` (65, `'A'`) into `0b01000000` (64, the `'@'`
character) — a different byte, and therefore different input bytes overall, even though only one
of the eight bits changed. Feed that single-bit-different byte string into `hash_to_int` and
you'll get a wildly different integer back, not a "nearby" one — there is no partial credit in
hashing, which is exactly the property that makes tamper detection work at all.

**Signature.**

```python
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
```

**Worked examples.**

1. `flip_bit(b"A", 0)` differs from `b"A"` (flipping the lowest bit of a single-byte string
   changes that byte, per the trace above: `0b01000001` -> `0b01000000`).
2. `flip_bit(b"hello", 3)` has the same length as `b"hello"` — tampering changes content, not
   size.
3. Putting it together: sign a message, flip one bit of that message, and confirm
   `verify(tampered_message, original_signature, public_key)` returns `False`. Also try
   flipping one bit of the *signature* instead (leaving the message alone) — `verify` should
   fail there too.

**Run it.**

```bash
pytest tests/test_04_tamper_detection.py -v
```

---

## Stage 5 — Design task: replay and reuse

> **Stop and think before reading further.**
>
> Your scheme from Stages 3-4 correctly proves that a message came from the private-key holder
> and hasn't been tampered with *in transit*. But consider this scenario: Alice signs a message
> that says `"Transfer $100 to Bob"` and sends it (with its valid signature) to a bank. The
> signature genuinely proves Alice authorized *those exact bytes*. Nothing in your scheme stops
> Bob from **recording that signed message and replaying it to the bank 50 more times** — each
> copy has the identical message and the identical, perfectly valid signature. `verify` returns
> `True` every single time, because nothing about the message or signature changed. This is
> called a **replay attack**: reusing a genuinely valid, previously-observed signed message to
> trigger an action its original signer never intended to repeat.
>
> **Before reading on:** how would you change the scheme (the message format, not the
> underlying signature math) to prevent this? You don't need to write any code for this stage —
> just sketch your approach in a sentence or two. What has to be true about two "legitimate"
> signed messages that should make replaying an old one detectably different from a new,
> intentional one?
>
> There's no test file for this stage — it's meant to be answered in prose, on your own, before
> you look at the answer below.

<details>
<summary>Click to reveal: how real systems actually solve this</summary>

The core insight: the signature only binds *whatever bytes you fed it*. If those bytes don't
encode enough context to distinguish "this exact authorization, made once, right now" from "a
byte-identical copy of an old authorization," nothing in the math can help you — the
signature will always verify, because it's checking a fact ("Alice signed exactly this") that
remains true forever, even for a replayed copy. The fix is entirely about **what you put into
the message before signing it**, not about the signing algorithm itself. Real systems combine
several of the following:

- **Nonces.** Include a random, single-use number in the signed message. The verifier keeps
  track of nonces it's already seen (e.g., for a time window) and rejects any signed message
  whose nonce has been used before. This directly blocks exact replay.
- **Timestamps (and an expiry window).** Include the time the message was signed, and reject
  anything outside a tolerance window (e.g., 5 minutes). This bounds *how long* a captured
  message stays replayable, and combined with tracking recently-seen timestamps, can block
  replay entirely within that window.
- **Sequence numbers / monotonic counters.** Especially common in banking and TLS-like
  protocols: each party tracks an expected next sequence number per session; a signed message
  with an old or repeated sequence number is rejected outright. This is stronger than a
  timestamp alone because it doesn't depend on clock synchronization.
- **Structured, unambiguous message formats.** Sign a well-defined structure (e.g.,
  `{"action": "transfer", "amount": 100, "to": "Bob", "nonce": "...", "timestamp": "..."}`,
  serialized deterministically) rather than a free-form string. This closes off a *different*
  but related class of bug: ambiguous parsing where two different logical messages could
  serialize to the same bytes (or vice versa), which signatures alone can't protect against if
  the format itself is ambiguous.
- **Binding to a specific recipient/context.** Include the intended recipient or
  session/channel identifier in the signed data, so a signed message intended for one
  recipient/context can't be replayed against a different one.

Notice that every one of these is a change to *what gets signed*, not to `sign`/`verify`
themselves — which is exactly why this is presented as a design task rather than a coding
stage: the interesting decision is what information the message needs to carry, and that's a
protocol design question, not an arithmetic one.

</details>

---

## Stage 6 — Bridge to the real `cryptography` package

**Concept.** Everything so far has been a hand-rolled, deliberately insecure toy. Python's
`cryptography` package is Python's standard toolkit for real-world encryption and signing: a
high-level, well-documented Python API sitting on top of **OpenSSL**, a battle-tested, heavily
audited C library that most of the internet's actual cryptography ultimately runs on. When you
call into `cryptography`, you're not getting a from-scratch reimplementation — you're getting a
thin, safe Python wrapper around the same primitives that secure the HTTPS connection you used to
read this file.

`cryptography` gives you production-grade signature schemes with a strikingly similar
*shape* to what you just built: generate a keypair, sign with the private key, verify with the
public key. This stage uses **Ed25519** (a modern elliptic-curve signature scheme, not RSA) to
show that the interface pattern — keypair, sign, verify — is the same regardless of which
underlying math a scheme uses; you don't need to understand elliptic curves to see the API rhyme
with what you just built. (Elliptic-curve schemes like Ed25519 achieve the same asymmetric
guarantee as RSA — a private operation only the key holder can do, a public operation anyone can
check — using different number theory, with the practical advantage of much smaller keys and
signatures for an equivalent security level. That underlying math is out of scope here; what
matters for this exercise is that the *API shape* — keypair, sign, verify — is the one you
already know.)

A few shape differences worth noticing as you write this stage: the real API returns a
`bytes` signature (not a Python `int`, since real signatures are raw byte strings, not numbers
meant to be read); and instead of returning `True`/`False`, `verify` **raises an exception**
(`InvalidSignature`) on failure and returns `None` (silently) on success — a different but
common convention for "did this succeed" in cryptographic libraries, since silently returning
`False` for a signature failure is an easy thing to accidentally ignore in calling code.

**Signatures.**

```python
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature


def generate_real_keypair():
    """
    Generate a real Ed25519 keypair using the cryptography package.

    Returns:
        A tuple (private_key, public_key) of
        cryptography.hazmat.primitives.asymmetric.ed25519 key objects.

    Example:
        >>> private_key, public_key = generate_real_keypair()
        >>> hasattr(private_key, "sign")
        True
    """
    raise NotImplementedError


def sign_real(message: bytes, private_key) -> bytes:
    """
    Sign message with a real Ed25519 private key.

    Args:
        message: the message bytes to sign.
        private_key: an Ed25519PrivateKey, as returned by generate_real_keypair.

    Returns:
        The raw signature bytes.

    Example:
        >>> private_key, public_key = generate_real_keypair()
        >>> sig = sign_real(b"hello", private_key)
        >>> isinstance(sig, bytes)
        True
    """
    raise NotImplementedError


def verify_real(message: bytes, signature: bytes, public_key) -> bool:
    """
    Verify signature against message using a real Ed25519 public key.

    Unlike your toy verify(), the real API raises InvalidSignature on
    failure instead of returning False -- this function should catch
    that and translate it to a plain bool, so callers can compare
    behavior against the toy version directly.

    Args:
        message: the message bytes that were (allegedly) signed.
        signature: the signature bytes to check.
        public_key: an Ed25519PublicKey, as returned by generate_real_keypair.

    Returns:
        True if the signature is valid for message, False otherwise.

    Example:
        >>> private_key, public_key = generate_real_keypair()
        >>> sig = sign_real(b"hello", private_key)
        >>> verify_real(b"hello", sig, public_key)
        True
        >>> verify_real(b"goodbye", sig, public_key)
        False
    """
    raise NotImplementedError
```

**Worked examples.**

1. `generate_real_keypair()` followed by `sign_real(b"hello", private_key)` and then
   `verify_real(b"hello", sig, public_key)` returns `True` — the same round-trip shape as
   Stage 3, but backed by a real, secure scheme.
2. Verifying against a different message (`verify_real(b"goodbye", sig, public_key)`) returns
   `False` — same tamper-sensitivity as your toy version, but here it's actually
   cryptographically secure, not just arithmetically consistent.
3. Compare the API shape directly: your toy `sign(message, private_key) -> int` vs. the real
   `sign_real(message, private_key) -> bytes`; your toy `verify(...) -> bool` (a plain boolean)
   vs. the real library's raise-on-failure convention, which `verify_real` adapts back into a
   boolean so you can compare behavior apples-to-apples.

**Run it.**

```bash
pytest tests/test_06_bridge_to_cryptography.py -v
```

(If `cryptography` isn't installed, this test file will be skipped automatically rather than
failing the whole suite.)

---

## Bringing It All Together

Step back and look at what you actually built. Your `sign` function takes a message and a private
key `(d, n)`, reduces the message to a fixed-size number with SHA-256, and raises that number to
the power `d` mod `n`. Your `verify` function takes a message, a signature, and a public key
`(e, n)`, and checks whether undoing the signature with `e` lands back on the same hash you'd get
by hashing the message fresh. That's the entire mechanism: an operation only the private-key
holder can perform, and an operation anyone can use to check it, related by the fact that `e` and
`d` are modular inverses of each other. Every claim in the opening section — "proves who sent it,"
"proves it wasn't altered," "no shared secret required" — is just that arithmetic fact, applied.
Stage 4 showed you tamper-evidence isn't a separate feature bolted on; it falls straight out of
SHA-256's avalanche property combined with modular exponentiation having no notion of "almost
equal." Stage 5 showed you that "verifies correctly" is a narrower claim than "is secure" —
your scheme, exactly as built, is legitimately vulnerable to replay, and closing that gap is a
protocol design question that lives in *what gets signed*, not in `sign`/`verify` themselves.

It's also worth being honest about what this exercise deliberately left out, so your mental model
of "digital signatures" is accurate rather than falsely complete:

- **Real hash function internals.** You used `hashlib.sha256` as a trusted black box; you didn't
  build the message padding, the 64 compression rounds, or the round constants that make SHA-256
  actually one-way. That's a substantial topic on its own.
- **Padding schemes.** Real RSA signing never raises a raw hash to the power `d` the way your toy
  `sign` does — it first applies a padding scheme (PKCS#1 v1.5 or, in modern systems, PSS for
  signing and OAEP for encryption) that adds structure and randomness specifically to defeat
  attacks that work against "naive" RSA like the one you built. Your toy scheme is arithmetically
  correct but would be exploitable in exactly the ways padding exists to prevent.
- **Certificate authorities and the PKI trust model.** Your `verify` function assumes you already
  have the *correct* public key for whoever you think you're verifying. In the real world, that's
  a hard problem in its own right: how does your browser know that *this* public key really
  belongs to your bank's website, and not to an attacker? The answer is a whole trust
  infrastructure called PKI (public key infrastructure): certificate authorities are organizations
  that themselves sign a statement saying "we've checked, and this public key really belongs to
  this domain," and your browser ships with a built-in list of certificate authorities it trusts.
  None of that chain-of-trust machinery was part of this exercise — you always started from an
  already-known keypair.

And it's worth pointing back, concretely, at the real systems this mechanism runs underneath, now
that "digital signature" means your own working code instead of an abstract phrase: **TLS/HTTPS**
uses signatures (often with schemes very much like the Ed25519 you called in Stage 6) as part of
proving a server controls the private key associated with a domain before your browser trusts it.
**Signed software updates** on every major OS use exactly this sign-with-private-key,
verify-with-public-key pattern so your machine can refuse to install anything that wasn't signed
by the vendor's private key. **Signed git commits** (the "Verified" badge on GitHub) are a
signature over the commit's contents, checked against the committer's registered public key.
**Cryptocurrency transactions** are, at their core, exactly your Stage 3 round trip: a transaction
message signed by the sender's private key, verified by anyone on the network using the sender's
public key, with no shared secret and no central authority required to settle the question of "did
the owner of this account actually authorize this." You built a small, honest version of the exact
mechanism underneath all four.

## Want more than a static exercise?

Want to do this interactively instead, with hints and a review of your finished code? Install
the learn-by-building skill: https://github.com/<your-username>/<your-learn-by-building-repo>

## Run everything

Once Stages 1-4 and 6 are implemented (Stage 5 is prose-only, no code to write), run the full
suite from inside this exercise folder:

```bash
pytest tests/ -v
```
