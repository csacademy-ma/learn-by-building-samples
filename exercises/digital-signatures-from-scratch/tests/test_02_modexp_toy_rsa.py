import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib

module = importlib.import_module("02_modexp_toy_rsa")
modexp = module.modexp
generate_toy_keypair = module.generate_toy_keypair


def test_modexp_matches_hand_computation():
    # Classic textbook example: 4^13 mod 497 = 445
    assert modexp(4, 13, 497) == 445


def test_modexp_matches_builtin_pow():
    assert modexp(7, 128, 3233) == pow(7, 128, 3233)


def test_modexp_exponent_zero():
    assert modexp(5, 0, 97) == 1


def test_modexp_exponent_one():
    assert modexp(9, 1, 100) == 9


def test_toy_keypair_matches_textbook_example():
    public_key, private_key = generate_toy_keypair()
    assert public_key == (17, 3233)
    assert private_key == (2753, 3233)


def test_toy_keypair_roundtrip_with_modexp():
    public_key, private_key = generate_toy_keypair(p=61, q=53, e=17)
    e, n = public_key
    d, n2 = private_key
    assert n == n2

    m = 65  # must be < n
    c = modexp(m, e, n)
    assert modexp(c, d, n) == m


def test_toy_keypair_raises_on_non_coprime_e():
    import pytest

    with pytest.raises(ValueError):
        # phi(61*53) = 60*52 = 3120; e=2 shares a factor of 2 with phi.
        generate_toy_keypair(p=61, q=53, e=2)
