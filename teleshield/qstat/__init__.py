"""
TeleShield Q-STAT Threat Detection Layer
Quantum Statistical Threat Analysis and Triage.
Deterministic, explainable, and mathematically grounded detection of forgery,
impersonation, replay, message tampering, channel manipulation, and unauthorized verification.
"""

from teleshield.qstat.verdict import Verdict, QSTATVerdict, VerdictType
from teleshield.qstat.envelope import validate_envelope, EnvelopeValidationResult
from teleshield.qstat.freshness import FreshnessTracker, FreshnessValidationResult
from teleshield.qstat.authorization import validate_authorization, AuthorizationResult
from teleshield.qstat.integrity import validate_message_integrity, IntegrityResult
from teleshield.qstat.statistics import BlockStatistics, compute_verification_statistics
from teleshield.qstat.binomial import BinomialVerifier, calculate_acceptance_threshold
from teleshield.qstat.sprt import SPRTVerifier, SPRTResult
from teleshield.qstat.fingerprint import FingerprintEngine, AttackFingerprint
from teleshield.qstat.chsh import CHSHMonitor, CHSHHealthReport
from teleshield.qstat.cusum import CUSUMMonitor, CUSUMStatus
from teleshield.qstat.pipeline import QSTATPipeline

__all__ = [
    "Verdict",
    "QSTATVerdict",
    "VerdictType",
    "validate_envelope",
    "EnvelopeValidationResult",
    "FreshnessTracker",
    "FreshnessValidationResult",
    "validate_authorization",
    "AuthorizationResult",
    "validate_message_integrity",
    "IntegrityResult",
    "BlockStatistics",
    "compute_verification_statistics",
    "BinomialVerifier",
    "calculate_acceptance_threshold",
    "SPRTVerifier",
    "SPRTResult",
    "FingerprintEngine",
    "AttackFingerprint",
    "CHSHMonitor",
    "CHSHHealthReport",
    "CUSUMMonitor",
    "CUSUMStatus",
    "QSTATPipeline",
]
