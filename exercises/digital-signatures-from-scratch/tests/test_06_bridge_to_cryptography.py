import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib

import pytest

pytest.importorskip("cryptography")

module = importlib.import_module("06_bridge_to_cryptography")
generate_real_keypair = module.generate_real_keypair
sign_real = module.sign_real
verify_real = module.verify_real


def test_sign_then_verify_roundtrip():
    private_key, public_key = generate_real_keypair()
    msg = b"hello real crypto"
    sig = sign_real(msg, private_key)
    assert verify_real(msg, sig, public_key) is True


def test_signature_is_bytes():
    private_key, public_key = generate_real_keypair()
    sig = sign_real(b"msg", private_key)
    assert isinstance(sig, bytes)


def test_verify_fails_for_different_message():
    private_key, public_key = generate_real_keypair()
    sig = sign_real(b"original message", private_key)
    assert verify_real(b"different message", sig, public_key) is False


def test_different_keypairs_produce_different_signatures():
    private_key_1, _ = generate_real_keypair()
    private_key_2, _ = generate_real_keypair()
    msg = b"same message"
    assert sign_real(msg, private_key_1) != sign_real(msg, private_key_2)
