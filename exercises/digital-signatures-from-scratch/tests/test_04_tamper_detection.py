import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib

keys_module = importlib.import_module("02_modexp_toy_rsa")
sign_module = importlib.import_module("03_sign_verify")
tamper_module = importlib.import_module("04_tamper_detection")

generate_toy_keypair = keys_module.generate_toy_keypair
sign = sign_module.sign
verify = sign_module.verify
flip_bit = tamper_module.flip_bit


def test_flip_bit_changes_the_data():
    data = b"hello"
    flipped = flip_bit(data, 0)
    assert flipped != data


def test_flip_bit_preserves_length():
    data = b"hello"
    flipped = flip_bit(data, 3)
    assert len(flipped) == len(data)


def test_flip_bit_changes_exactly_one_bit():
    data = b"A"  # 0x41 = 01000001
    flipped = flip_bit(data, 0)
    original_bits = f"{data[0]:08b}"
    flipped_bits = f"{flipped[0]:08b}"
    diff = sum(1 for a, b in zip(original_bits, flipped_bits) if a != b)
    assert diff == 1


def test_flipping_one_bit_of_message_breaks_verification():
    public_key, private_key = generate_toy_keypair()
    msg = b"Attack at dawn"
    sig = sign(msg, private_key)

    tampered_msg = flip_bit(msg, 3)
    assert verify(tampered_msg, sig, public_key) is False


def test_flipping_one_bit_of_signature_breaks_verification():
    public_key, private_key = generate_toy_keypair()
    msg = b"Attack at dawn"
    sig = sign(msg, private_key)

    tampered_sig = sig ^ 1
    assert verify(msg, tampered_sig, public_key) is False


def test_untampered_message_and_signature_still_verify():
    public_key, private_key = generate_toy_keypair()
    msg = b"no tampering happened here"
    sig = sign(msg, private_key)
    assert verify(msg, sig, public_key) is True
