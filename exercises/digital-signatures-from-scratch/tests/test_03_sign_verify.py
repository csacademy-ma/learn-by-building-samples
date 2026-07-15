import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib

keys_module = importlib.import_module("02_modexp_toy_rsa")
sign_module = importlib.import_module("03_sign_verify")

generate_toy_keypair = keys_module.generate_toy_keypair
sign = sign_module.sign
verify = sign_module.verify
hash_to_int = sign_module.hash_to_int


def test_sign_then_verify_roundtrip():
    public_key, private_key = generate_toy_keypair()
    msg = b"Attack at dawn"
    sig = sign(msg, private_key)
    assert verify(msg, sig, public_key) is True


def test_signature_is_an_int():
    public_key, private_key = generate_toy_keypair()
    sig = sign(b"Attack at dawn", private_key)
    assert isinstance(sig, int)


def test_verify_fails_for_different_message():
    public_key, private_key = generate_toy_keypair()
    sig = sign(b"Attack at dawn", private_key)
    assert verify(b"Attack at dusk", sig, public_key) is False


def test_verify_fails_for_signature_off_by_one():
    public_key, private_key = generate_toy_keypair()
    msg = b"hello"
    sig = sign(msg, private_key)
    assert verify(msg, sig + 1, public_key) is False


def test_hash_to_int_is_in_range():
    _, n = (17, 3233)
    h = hash_to_int(b"hello", n)
    assert 0 <= h < n


def test_hash_to_int_deterministic():
    n = 3233
    assert hash_to_int(b"same input", n) == hash_to_int(b"same input", n)
