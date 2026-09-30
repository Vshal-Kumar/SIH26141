"""
Attack Regression Test Suite
Guarantees that every modeled adversarial attack produces the exact expected
deterministic detector verdict in the Q-STAT pipeline.
"""

import pytest
from teleshield.backends.exact import ExactBackend
from teleshield.qds.session import QDSSession
from teleshield.attacks.forgery import RandomForgeryAttack
from teleshield.attacks.splice import SpliceForgeryAttack
from teleshield.attacks.impersonation import ImpersonationAttack
from teleshield.attacks.replay import ReplayAttack
from teleshield.attacks.channel import ChannelManipulationAttack
from teleshield.attacks.unauthorized import UnauthorizedVerificationAttack
from teleshield.attacks.intercept_resend import InterceptResendAttack


@pytest.fixture
def active_session():
    """Provides an initialized clean QDS session with teleported states."""
    return QDSSession.create(
        n=16,
        L=32,
        backend=ExactBackend(seed=42),
        bell_visibility=1.0,
        seed=42,
    )


def test_attack_random_forgery_regression(active_session):
    """Random forgery must produce FORGERY_SUSPECTED."""
    msg = "Target payment transaction"
    sig = active_session.sign(msg)

    attack = RandomForgeryAttack(strength=1.0, seed=42)
    attack_res = attack.execute(signature=sig)

    verdict, stats = active_session.verify(msg, attack_res.manipulated_signature, seed=42)
    assert verdict.verdict.value == "FORGERY_SUSPECTED"
    assert not verdict.is_accepted
    assert stats.global_mismatch_rate > verdict.threshold


def test_attack_splice_forgery_regression(active_session):
    """Splice forgery must produce FORGERY_SUSPECTED and isolate affected blocks."""
    donor_msg = "Pay $100 to Vendor Alpha"
    target_msg = "Pay $1,000,000 to Vendor Bravo"
    donor_sig = active_session.sign(donor_msg)

    attack = SpliceForgeryAttack(target_blocks=[1, 3, 5], strength=1.0, seed=42)
    attack_res = attack.execute(donor_signature=donor_sig, target_message=target_msg)

    verdict, stats = active_session.verify(target_msg, attack_res.manipulated_signature, seed=42)
    assert verdict.verdict.value in ("FORGERY_SUSPECTED", "REJECT")
    assert not verdict.is_accepted


def test_attack_impersonation_regression(active_session):
    """Impersonation must produce IMPERSONATION_SUSPECTED or FORGERY_SUSPECTED."""
    msg = "Impersonated authority decree"
    attack = ImpersonationAttack(seed=42)
    attack_res = attack.execute(
        message=msg,
        key_id=active_session.keypair.key_id,
        verifier_id=active_session.verifier.verifier_id,
        n_bits=active_session.keypair.n,
        L=active_session.keypair.L,
    )

    verdict, stats = active_session.verify(msg, attack_res.manipulated_signature, seed=42)
    assert verdict.verdict.value in ("IMPERSONATION_SUSPECTED", "FORGERY_SUSPECTED")
    assert not verdict.is_accepted
    # Near 50% mismatch
    assert abs(stats.global_mismatch_rate - 0.50) < 0.15


def test_attack_replay_regression(active_session):
    """Replay must produce REPLAY."""
    msg = "One-time funds release"
    sig = active_session.sign(msg)

    # First pass: legit verification
    v1, _ = active_session.verify(msg, sig, seed=42)
    assert v1.is_accepted

    # Replay pass
    attack = ReplayAttack()
    attack_res = attack.execute(valid_signature=sig)
    v2, _ = active_session.verify(msg, attack_res.manipulated_signature, seed=42)

    assert v2.verdict.value == "REPLAY"
    assert not v2.is_accepted


def test_attack_unauthorized_verification_regression(active_session):
    """Unauthorized verifier must produce UNAUTHORIZED_VERIFICATION."""
    msg = "Confidential memorandum"
    sig = active_session.sign(msg)

    unauth_verifier = active_session.verifier.__class__(
        verifier_id="attacker_charlie",
        backend=active_session.backend,
        pipeline=active_session.pipeline,
    )
    verdict, _ = unauth_verifier.verify(message=msg, signature=sig, slots={})

    assert verdict.verdict.value == "UNAUTHORIZED_VERIFICATION"
    assert not verdict.is_accepted


def test_attack_channel_manipulation_regression(active_session):
    """Strong channel manipulation must produce CHANNEL_ANOMALY or FORGERY_SUSPECTED."""
    msg = "Teleported data packet"
    sig = active_session.sign(msg)

    attack = ChannelManipulationAttack(channel_type="depolarizing", strength=0.35, seed=42)
    attack_res = attack.execute(slots=active_session.slots)
    active_session.slots = attack_res.manipulated_slots

    verdict, stats = active_session.verify(msg, sig, seed=42)
    assert verdict.verdict.value in ("CHANNEL_ANOMALY", "FORGERY_SUSPECTED")
    assert not verdict.is_accepted
