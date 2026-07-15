"""
Stage 2 - Toy asymmetric keys: modular exponentiation + a toy RSA keypair.

See EXERCISE.md for the full concept explanation and worked examples.

NOT SECURE. The keypairs generated here use primes small enough to factor
by hand. Real RSA uses primes with hundreds of decimal digits (~1024+ bits
each). This is for understanding the mechanism only -- never use this for
anything real.
"""


def _modinv(a: int, m: int) -> int:
    """
    Modular inverse of a mod m via the extended Euclidean algorithm.

    Provided already working -- this is a standard number theory routine
    that's a detour from this exercise's actual point (see EXERCISE.md).
    """
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        g, x1, y1 = extended_gcd(b % a, a)
        return g, y1 - (b // a) * x1, x1
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError("no modular inverse")
    return x % m


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
