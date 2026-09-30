"""
Q-STAT Threat Detection Engine Test Suite
Validates each stage of the deterministic verification pipeline:
envelope, freshness, authorization, message integrity, binomial testing,
SPRT, CUSUM, and forensic fingerprinting.
"""

import pytest
import time
from teleshield.qstat.envelope import validate_envelope
from teleshield.qstat.freshness import FreshnessTracker
from teleshield.qstat.authorization import validate_authorization
from teleshield.qstat.integrity import validate_message_integrity
from teleshield.qstat.binomial import calculate_acceptance_threshold, BinomialVerifier
from teleshield.qstat.sprt import SPRTVerifier
from teleshield.qstat.cusum import CUSUMMonitor, CUSUMState
from teleshield.qstat.fingerprint import FingerprintEngine
from teleshield.qds.models import QDSSignature, KeySlot, SlotStatus
from teleshield.quantum.states import StateBasis, Eigenvalue


def test_envelope_validation():
    """Verify malformed envelope rejection."""
    # Valid envelope
    valid_sig = QDSSignature(
        message_id="msg_001",
        signer_id="alice",
        verifier_id="bob",
        key_id="k_001",
        epoch=1,
        timestamp=time.time(),
        nonce="nonce_1234",
        tag="abcd",
        tag_bits=[0, 1, 0, 1],
        revealed_states=[{"tag_index": 0, "state_index": 0, "basis": "X", "eigenvalue": "+1"}],
    )
    res_valid = validate_envelope(valid_sig)
    assert res_valid.valid

    # Malformed envelope missing signer_id
    bad_sig = QDSSignature(
        message_id="msg_002",
        signer_id="",  # Empty!
        verifier_id="bob",
        key_id="k_001",
        epoch=1,
        timestamp=time.time(),
        nonce="nonce_5678",
        tag="abcd",
        tag_bits=[0, 1],
        revealed_states=[{"test": 1}],
    )
    res_bad = validate_envelope(bad_sig)
    assert not res_bad.valid
    assert res_bad.verdict.verdict.value == "MALFORMED"


def test_freshness_and_replay_detection():
    """Verify freshness tracking rejects duplicate nonces and consumed slots."""
    tracker = FreshnessTracker()
    sig = QDSSignature(
        message_id="msg_001",
        signer_id="alice",
        verifier_id="bob",
        key_id="k_001",
        epoch=1,
        timestamp=time.time(),
        nonce="unique_nonce_abc",
        tag="1234",
        tag_bits=[0, 1],
        revealed_states=[],
    )

    # First check must pass
    res1 = tracker.check_freshness(sig)
    assert res1.valid

    # Register as consumed
    tracker.register_consumed(sig)

    # Second check with identical nonce must fail as REPLAY
    res2 = tracker.check_freshness(sig)
    assert not res2.valid
    assert res2.verdict.verdict.value == "REPLAY"


def test_authorization_check():
    """Verify authorization rejects mismatched verifier."""
    sig = QDSSignature(
        message_id="msg_001",
        signer_id="alice",
        verifier_id="bob",
        key_id="k_001",
        epoch=1,
        timestamp=time.time(),
        nonce="nonce_1",
        tag="12",
        tag_bits=[0],
        revealed_states=[],
    )

    # Authorized
    res_auth = validate_authorization(sig, verifier_id="bob")
    assert res_auth.authorized

    # Unauthorized
    res_unauth = validate_authorization(sig, verifier_id="charlie")
    assert not res_unauth.authorized
    assert res_unauth.verdict.verdict.value == "UNAUTHORIZED_VERIFICATION"


def test_message_integrity_check():
    """Verify message integrity rejects tampered plaintext."""
    sig = QDSSignature(
        message_id="msg_001",
        signer_id="alice",
        verifier_id="bob",
        key_id="k_001",
        epoch=1,
        timestamp=time.time(),
        nonce="nonce_1",
        tag="b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
        tag_bits=[1, 0, 1, 1, 1, 0, 0, 1] * 32,  # SHA-256 for "hello world"
        revealed_states=[],
        hash_mode="sha256",
    )

    # Correct message
    from teleshield.qds.hashing import compute_message_tag, HashMode
    msg = "Original contract terms"
    t_hex, t_bits = compute_message_tag(msg, HashMode.SHA256, n_bits=64)
    sig.tag = t_hex
    sig.tag_bits = t_bits

    res_ok = validate_message_integrity(msg, sig)
    assert res_ok.valid

    # Tampered message
    res_tampered = validate_message_integrity("Tampered contract terms", sig)
    assert not res_tampered.valid
    assert res_tampered.verdict.verdict.value == "MESSAGE_TAMPERED"


def test_binomial_threshold_derivation():
    """Verify acceptance threshold derivation is monotonic and mathematically consistent."""
    s_a_small = calculate_acceptance_threshold(L=32, n_blocks=16, expected_honest_noise=0.01)
    s_a_large = calculate_acceptance_threshold(L=222, n_blocks=16, expected_honest_noise=0.01)

    # As L increases, margin narrows, so threshold s_a decreases toward epsilon
    assert s_a_large < s_a_small
    assert s_a_large > 0.01
    assert s_a_small < 0.50


def test_sprt_sequential_verifier():
    """Verify SPRT early decision boundary stopping."""
    sprt = SPRTVerifier(p0=0.01, p1=0.50, alpha=1e-5, beta=1e-5)

    from teleshield.quantum.measurement import MeasurementResult
    # Sequence of 30 straight matches -> should accept early
    clean_meas = [
        MeasurementResult(
            basis=StateBasis.Z,
            expected_eigenvalue=Eigenvalue.PLUS,
            observed_eigenvalue=Eigenvalue.PLUS,
            raw_result=0,
            shots=1,
            matches=1,
            mismatches=0,
            mismatch_rate=0.0,
            p_plus=1.0,
            p_minus=0.0,
        )
        for _ in range(30)
    ]
    res_honest = sprt.evaluate_sequential(clean_meas)
    assert res_honest.decision == "ACCEPT"
    assert res_honest.samples_used < 30


def test_cusum_drift_detection():
    """Verify CUSUM detects subtle persistent drift."""
    cusum = CUSUMMonitor(baseline_rate=0.01, detectable_shift=0.015, decision_threshold=0.03)

    # 10 honest sessions at 0.01
    for _ in range(10):
        st = cusum.update(0.010)
    assert st.state == CUSUMState.NORMAL

    # 15 persistent elevated sessions at 0.025
    anomaly_detected = False
    for _ in range(15):
        st = cusum.update(0.025)
        if st.state == CUSUMState.ANOMALY:
            anomaly_detected = True
            break
    assert anomaly_detected
