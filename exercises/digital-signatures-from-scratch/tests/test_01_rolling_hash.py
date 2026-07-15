import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

import importlib

hash_module = importlib.import_module("01_rolling_hash")
rolling_hash = hash_module.rolling_hash


def test_deterministic():
    assert rolling_hash("hello") == rolling_hash("hello")
    assert rolling_hash("Attack at dawn") == rolling_hash("Attack at dawn")


def test_different_strings_usually_differ():
    assert rolling_hash("hello") != rolling_hash("world")


def test_empty_string_is_zero():
    assert rolling_hash("") == 0


def test_matches_hand_traced_value():
    # base=131, mod=10**9+7, s="ab"
    # h = 0
    # h = (0*131 + ord('a')) % mod = 97
    # h = (97*131 + ord('b')) % mod = 97*131 + 98 = 12805
    assert rolling_hash("ab", base=131, mod=10 ** 9 + 7) == 12805


def test_default_args_match_hand_traced_value():
    # Same trace as above, but relying on the default base/mod.
    assert rolling_hash("ab") == 12805
