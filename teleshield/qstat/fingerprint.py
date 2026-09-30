"""
Q-STAT Statistical Fingerprint Engine
Performs forensic classification of physical quantum anomalies and adversarial attacks.
Evaluates per-block dispersion, basis asymmetry (X, Y, Z), and temporal profiles.
Uses rigorous scientific language: 'consistent with' rather than 'proves'.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np

from teleshield.qstat.statistics import VerificationStatistics, BlockStatistics


@dataclass
class AttackFingerprint:
    """Forensic classification and diagnostic report of quantum evidence."""
    classification: str
    primary_anomaly: str
    basis_diagnosis: str
    block_diagnosis: str
    affected_blocks: List[int]
    confidence_score: float
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classification": self.classification,
            "primary_anomaly": self.primary_anomaly,
            "basis_diagnosis": self.basis_diagnosis,
            "block_diagnosis": self.block_diagnosis,
            "affected_blocks": self.affected_blocks,
            "confidence_score": self.confidence_score,
            "evidence": self.evidence,
        }


class FingerprintEngine:
    """
    Forensic classification engine analyzing multi-dimensional quantum measurement evidence.
    """

    def __init__(self, honest_noise_threshold: float = 0.05) -> None:
        self.honest_noise_threshold = honest_noise_threshold

    def analyze(
        self,
        stats: VerificationStatistics,
        threshold: float,
    ) -> AttackFingerprint:
        """
        Analyzes statistics to identify attack signatures and channel anomalies.
        """
        block_rates = [b.mismatch_rate for b in stats.block_statistics]
        bad_blocks = [b.block_index for b in stats.block_statistics if b.mismatch_rate > threshold]
        n_blocks = stats.n_blocks

        # 1. Block Distribution Analysis
        bad_fraction = len(bad_blocks) / max(1, n_blocks)
        is_isolated_splice = 0 < len(bad_blocks) < n_blocks and bad_fraction <= 0.85
        is_pervasive_attack = bad_fraction > 0.85 or (stats.global_mismatch_rate >= 0.35 and len(bad_blocks) > 0)

        # 2. Basis Asymmetry Analysis
        bx = stats.per_basis_rates.get("X", 0.0)
        by = stats.per_basis_rates.get("Y", 0.0)
        bz = stats.per_basis_rates.get("Z", 0.0)

        basis_diff_xz = abs(bx - bz)
        max_b = max(bx, by, bz)
        min_b = min(bx, by, bz)

        # Basis diagnosis
        basis_diagnosis = ""
        channel_type = "unknown"

        if max_b > threshold:
            # Check for dephasing (Z-noise causes X and Y flips, Z basis unaffected)
            if bx > threshold and bz <= threshold + 0.02 and (by > threshold or by == 0.0):
                basis_diagnosis = "Pattern consistent with phase/dephasing-type disturbance (Z-noise rotates X and Y eigenstates while preserving Z)."
                channel_type = "dephasing"
            # Check for bit-flip (X-noise causes Z and Y flips, X basis unaffected)
            elif bz > threshold and bx <= threshold + 0.02 and (by > threshold or by == 0.0):
                basis_diagnosis = "Pattern consistent with bit-flip-type disturbance (X-noise rotates Z and Y eigenstates while preserving X)."
                channel_type = "bit_flip"
            # Uniform basis disturbance
            elif abs(bx - bz) < 0.10:
                basis_diagnosis = (
                    "Pattern may be consistent with depolarizing noise or intercept-resend; "
                    "basis statistics alone do not uniquely distinguish them because both isotropic depolarizing "
                    "channels and random intercept-resend generate uniform disturbance across all measurement bases."
                )
                channel_type = "isotropic"
            else:
                basis_diagnosis = f"Asymmetric basis disturbance observed: X={bx:.3f}, Y={by:.3f}, Z={bz:.3f}."
                channel_type = "asymmetric"
        else:
            basis_diagnosis = "All basis mismatch rates are within expected honest channel tolerances."
            channel_type = "nominal"

        # 3. Comprehensive Classification Synthesis
        classification = "NOMINAL"
        primary_anomaly = "None detected"
        block_diagnosis = ""
        confidence = 0.95

        if len(bad_blocks) == 0:
            classification = "LEGITIMATE_SIGNATURE"
            primary_anomaly = "Honest transmission within calibrated noise envelope"
            block_diagnosis = f"All {n_blocks} blocks verified successfully below threshold {threshold:.4f}."
            confidence = 0.99
        elif is_isolated_splice:
            classification = "POSSIBLE_SPLICE_FORGERY"
            primary_anomaly = f"Isolated block mismatch concentration ({len(bad_blocks)} of {n_blocks} blocks failed)"
            block_diagnosis = (
                f"Blocks {bad_blocks} show high error rates (mean {np.mean([block_rates[i] for i in bad_blocks]):.3f}) "
                f"while remaining blocks pass cleanly. Consistent with signature splicing attack combining "
                f"disparate message segments."
            )
            confidence = 0.92
        elif is_pervasive_attack:
            # Check if rates are near 50% (random guess / impersonation)
            if 0.40 <= stats.global_mismatch_rate <= 0.60:
                classification = "POSSIBLE_IMPERSONATION_OR_FORGERY"
                primary_anomaly = (
                    f"Near-maximal error rate across all blocks (global mismatch: {stats.global_mismatch_rate:.3f})"
                )
                block_diagnosis = (
                    f"Pervasive failure across {len(bad_blocks)}/{n_blocks} blocks with error rate clustering around 50%. "
                    f"Consistent with an unauthenticated entity lacking the private key attempting random forgery or impersonation."
                )
                confidence = 0.96
            else:
                classification = "CHANNEL_ANOMALY"
                primary_anomaly = f"Excessive channel degradation or active quantum manipulation (global rate {stats.global_mismatch_rate:.3f})"
                block_diagnosis = f"Widespread elevated mismatch rates exceeding honest bounds across {len(bad_blocks)} blocks."
                confidence = 0.88
        else:
            classification = "POSSIBLE_FORGERY"
            primary_anomaly = f"Statistical mismatch detected in {len(bad_blocks)} blocks"
            block_diagnosis = f"Blocks {bad_blocks} exceeded derived acceptance threshold."
            confidence = 0.85

        return AttackFingerprint(
            classification=classification,
            primary_anomaly=primary_anomaly,
            basis_diagnosis=basis_diagnosis,
            block_diagnosis=block_diagnosis,
            affected_blocks=bad_blocks,
            confidence_score=confidence,
            evidence={
                "global_mismatch": stats.global_mismatch_rate,
                "threshold": threshold,
                "bad_blocks_count": len(bad_blocks),
                "basis_rates": stats.per_basis_rates,
                "channel_type": channel_type,
            },
        )
