"""
QDS Protocol Test Suite
Validates key generation, public key distribution, message binding,
signing, verification, and slot lifecycle state transitions.
"""

import pytest
from teleshield.backends.exact import ExactBackend
from teleshield.qds.keygen import generate_qds_keypair
from teleshield.qds.distribution import distribute_public_key
from teleshield.qds.hashing import HashMode, compute_message_tag, verify_message_tag
from teleshield.qds.session import QDSSession
from teleshield.qds.models import SlotStatus


def test_qds_keygen():
    """Verify key generation produces 2 * n * L states with correct metadata."""
    n = 8
    L = 16
    backend = ExactBackend(seed=42)
    kp = generate_qds_keypair(n=n, L=L, backend=backend, seed=42)

    assert kp.n == n
    assert kp.L == L
    assert len(kp.private_states) == n * 2  # Each tag position has bit 0 and bit 1
    assert len(kp.quantum_states) == 2 * n * L

    for (j, b), states_list in kp.private_states.items():
        assert len(states_list) == L
        assert 0 <= j < n
        assert b in (0, 1)


def test_message_binding_hashes():
    """Verify SHA-256 and Toeplitz message binding and verification."""
    msg = "Quantum financial authorization $50,000"
    n_bits = 32

    # Mode 1: SHA-256
    tag_hex_1, tag_bits_1 = compute_message_tag(msg, mode=HashMode.SHA256, n_bits=n_bits)
    assert len(tag_bits_1) == n_bits
    assert verify_message_tag(msg, tag_bits_1, mode=HashMode.SHA256, n_bits=n_bits)
    assert not verify_message_tag("Tampered message", tag_bits_1, mode=HashMode.SHA256, n_bits=n_bits)

    # Mode 2: Toeplitz EAU
    tag_hex_2, tag_bits_2 = compute_message_tag(msg, mode=HashMode.TOEPLITZ, n_bits=n_bits)
    assert len(tag_bits_2) == n_bits
    assert verify_message_tag(msg, tag_bits_2, mode=HashMode.TOEPLITZ, n_bits=n_bits)


def test_qds_end_to_end_verification():
    """Verify that a legitimate noiseless signature passes verification with ACCEPT verdict."""
    session = QDSSession.create(
        n=16,
        L=32,
        backend=ExactBackend(seed=42),
        bell_visibility=1.0,
        seed=42,
    )

    msg = "Authorize transaction #9842"
    sig = session.sign(msg)
    verdict, stats = session.verify(msg, sig, seed=42)

    assert verdict.is_accepted
    assert verdict.verdict.value == "ACCEPT"
    assert stats is not None
    assert stats.global_mismatch_rate <= verdict.threshold


def test_slot_consumption_enforcement():
    """Verify that measured quantum states are consumed and marked CONSUMED."""
    session = QDSSession.create(
        n=8,
        L=16,
        backend=ExactBackend(seed=42),
        bell_visibility=1.0,
        seed=42,
    )

    msg = "One-time execution payload"
    sig = session.sign(msg)

    # Initial slots must be available
    avail_before = session.available_slots_count
    assert avail_before > 0

    # Execute verification
    session.verify(msg, sig, seed=42)

    # Measured slots must now be consumed
    avail_after = session.available_slots_count
    assert avail_after < avail_before
