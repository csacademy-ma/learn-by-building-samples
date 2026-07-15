"""
Stage 1 - Warm-up: a one-way-ish function (polynomial rolling hash).

See EXERCISE.md for the full concept explanation and worked examples.
"""


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
