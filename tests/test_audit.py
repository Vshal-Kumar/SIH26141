"""
Cryptographic Audit Test Suite
Validates SHA-256 hash chaining, forward integrity, tamper detection,
and forensic export functions.
"""

import pytest
from teleshield.audit.hashchain import HashChain


def test_audit_hash_chain_creation_and_validation():
    """Verify clean hash chain appends events and passes validation."""
    chain = HashChain()
    assert chain.verify_integrity().is_valid

    # Log 3 verification events
    e1 = chain.log_verification(
        message_id="msg_1",
        signer_id="alice",
        verifier_id="bob",
        verdict="ACCEPT",
        global_mismatch=0.012,
        threshold=0.045,
    )
    e2 = chain.log_verification(
        message_id="msg_2",
        signer_id="alice",
        verifier_id="bob",
        verdict="FORGERY_SUSPECTED",
        global_mismatch=0.485,
        threshold=0.045,
    )
    e3 = chain.log_verification(
        message_id="msg_3",
        signer_id="alice",
        verifier_id="bob",
        verdict="REPLAY",
        global_mismatch=0.0,
        threshold=0.045,
    )

    # Chain continuity check
    assert e2.previous_hash == e1.event_hash
    assert e3.previous_hash == e2.event_hash

    res = chain.verify_integrity()
    assert res.is_valid
    assert res.status == "AUDIT CHAIN VALID"
    assert res.total_events == 3


def test_audit_tampering_detection():
    """Verify modifying a past audit event immediately breaks chain integrity."""
    chain = HashChain()
    chain.log_verification("m1", "alice", "bob", "ACCEPT")
    chain.log_verification("m2", "alice", "bob", "ACCEPT")
    chain.log_verification("m3", "alice", "bob", "ACCEPT")

    # Tamper with event 1 payload (e.g. change verdict maliciously to 'REJECT')
    chain.events[0].verdict = "REJECT"

    # Integrity verification must catch tampering
    res = chain.verify_integrity()
    assert not res.is_valid
    assert res.status == "AUDIT CHAIN INVALID"
    assert res.compromised_index == 0


def test_audit_export():
    """Verify CSV and JSON export formats."""
    chain = HashChain()
    chain.log_verification("m1", "alice", "bob", "ACCEPT")

    csv_data = chain.export_csv()
    assert "event_id" in csv_data
    assert "ACCEPT" in csv_data

    json_data = chain.export_json()
    assert '"verdict": "ACCEPT"' in json_data
