"""
Stage 6 - Bridge to the real `cryptography` package.

See EXERCISE.md for the full concept explanation and worked examples.

This stage only requires the `cryptography` package. The import is
guarded so that the rest of the exercise's test suite still runs (and the
Stage 6 test gets skipped, not failed) if `cryptography` isn't installed.
"""

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.exceptions import InvalidSignature
except ImportError:  # pragma: no cover - exercised only when uninstalled
    ed25519 = None
    InvalidSignature = None


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
