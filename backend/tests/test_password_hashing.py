"""
Tests for password_hashing — PraxisMed Sprint 7 / Module 59

No real DB, no external services.
"""

from __future__ import annotations

import pytest

from backend.app.core.password_hashing import (
    PasswordHashingError,
    hash_password,
    verify_password,
)


# ---------------------------------------------------------------------------
# 1. hash_password returns a non-empty string
# ---------------------------------------------------------------------------


def test_hash_password_returns_string():
    result = hash_password("SecurePass1!")
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# 2. hash_password does not return the plaintext password
# ---------------------------------------------------------------------------


def test_hash_password_not_plaintext():
    pw = "MySecret123"
    assert hash_password(pw) != pw


# ---------------------------------------------------------------------------
# 3. hash_password produces different hashes each call (bcrypt salt)
# ---------------------------------------------------------------------------


def test_hash_password_is_salted():
    pw = "SamePassword"
    assert hash_password(pw) != hash_password(pw)


# ---------------------------------------------------------------------------
# 4. hash_password output starts with bcrypt identifier
# ---------------------------------------------------------------------------


def test_hash_password_is_bcrypt():
    result = hash_password("TestPass99")
    assert result.startswith("$2b$") or result.startswith("$2a$")


# ---------------------------------------------------------------------------
# 5. hash_password rejects empty password
# ---------------------------------------------------------------------------


def test_hash_password_rejects_empty():
    with pytest.raises(PasswordHashingError):
        hash_password("")


# ---------------------------------------------------------------------------
# 6. hash_password rejects whitespace-only password
# ---------------------------------------------------------------------------


def test_hash_password_rejects_whitespace_only():
    with pytest.raises(PasswordHashingError):
        hash_password("   ")


# ---------------------------------------------------------------------------
# 7. verify_password returns True for correct password
# ---------------------------------------------------------------------------


def test_verify_password_correct():
    pw = "CorrectHorse"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True


# ---------------------------------------------------------------------------
# 8. verify_password returns False for wrong password
# ---------------------------------------------------------------------------


def test_verify_password_wrong():
    hashed = hash_password("RightPassword")
    assert verify_password("WrongPassword", hashed) is False


# ---------------------------------------------------------------------------
# 9. verify_password returns False for empty password
# ---------------------------------------------------------------------------


def test_verify_password_empty_password():
    hashed = hash_password("SomePassword")
    assert verify_password("", hashed) is False


# ---------------------------------------------------------------------------
# 10. verify_password returns False for empty hash
# ---------------------------------------------------------------------------


def test_verify_password_empty_hash():
    assert verify_password("SomePassword", "") is False


# ---------------------------------------------------------------------------
# 11. verify_password does not raise on mismatched input
# ---------------------------------------------------------------------------


def test_verify_password_does_not_raise_on_mismatch():
    result = verify_password("anything", hash_password("something_else"))
    assert result is False


# ---------------------------------------------------------------------------
# 12. round-trip: hash then verify
# ---------------------------------------------------------------------------


def test_hash_verify_round_trip():
    passwords = ["simple", "C0mpl3x!P@ss", "αβγδ", "  leading space"]
    for pw in passwords:
        hashed = hash_password(pw)
        assert verify_password(pw, hashed), f"Round-trip failed for {pw!r}"
