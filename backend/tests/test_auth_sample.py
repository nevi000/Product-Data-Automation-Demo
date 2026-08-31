import time

from app.services.auth import sign, verify

SECRET = "test-secret"


def test_sign_then_verify_roundtrips():
    token = sign("alice", SECRET)
    assert verify(token, SECRET) == "alice"


def test_tampered_token_rejected():
    token = sign("alice", SECRET)
    assert verify(token[:-1] + ("0" if token[-1] != "0" else "1"), SECRET) is None


def test_wrong_secret_rejected():
    assert verify(sign("alice", SECRET), "other-secret") is None


def test_expired_token_rejected():
    old = sign("alice", SECRET, issued_at=time.time() - 10_000)
    assert verify(old, SECRET, max_age=3600) is None
