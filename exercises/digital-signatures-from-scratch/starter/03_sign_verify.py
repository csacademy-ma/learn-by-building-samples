"""
Stage 3 - Sign and verify.

See EXERCISE.md for the full concept explanation and worked examples.
"""

import hashlib
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
_modexp_module = importlib.import_module("02_modexp_toy_rsa")
modexp = _modexp_module.modexp


def hash_to_int(message: bytes, n: int) -> int:
    """
    Hash message with SHA-256 and reduce the result mod n.

    Provided already working -- see EXERCISE.md's discussion of why we
    use hashlib.sha256 here rather than Stage 1's rolling_hash.
    """
    digest = hashlib.sha256(message).digest()
    return int.from_bytes(digest, "big") % n


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
