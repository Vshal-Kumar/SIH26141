"""
Q-STAT Threat Detection Pipeline
Main orchestrator executing the 7-stage deterministic verification pipeline:
  1. Envelope Check -> MALFORMED
  2. Freshness Check -> REPLAY
  3. Authorization Check -> UNAUTHORIZED_VERIFICATION
  4. Message Integrity Check -> MESSAGE_TAMPERED
  5. Quantum Measurement & Binomial Verification
  6. Forensic Fingerprinting & Basis Diagnosis
  7. Final Verdict Synthesis & Slot Consumption
Strictly deterministic; zero AI/ML inference models.
"""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional

from teleshield.qstat.verdict import VerdictType, QSTATVerdict
from teleshield.qstat.envelope import validate_envelope
from teleshield.qstat.freshness import FreshnessTracker
from teleshield.qstat.authorization import validate_authorization
from teleshield.qstat.integrity import validate_message_integrity
from teleshield.qstat.statistics import VerificationStatistics
from teleshield.qstat.binomial import BinomialVerifier, calculate_acceptance_threshold
from teleshield.qstat.fingerprint import FingerprintEngine
from teleshield.qds.models import QDSSignature, KeySlot


class QSTATPipeline:
    """
    Deterministic quantum statistical threat analysis and triage pipeline.
    """

    def __init__(
        self,
        expected_honest_noise: float = 0.01,
        target_false_rejection: float = 1e-6,
        freshness_tracker: Optional[FreshnessTracker] = None,
        toeplitz_seed: int = 1337,
    ) -> None:
        self.expected_honest_noise = expected_honest_noise
        self.target_false_rejection = target_false_rejection
        self.freshness_tracker = freshness_tracker or FreshnessTracker()
        self.binomial_verifier = BinomialVerifier(
            expected_honest_noise=expected_honest_noise,
            target_false_rejection=target_false_rejection,
        )
        self.fingerprint_engine = FingerprintEngine(honest_noise_threshold=expected_honest_noise * 2.5)
        self.toeplitz_seed = toeplitz_seed

    def evaluate(
        self,
        message: str,
        signature: QDSSignature,
        verifier_id: str,
        stats: Optional[VerificationStatistics] = None,
        slots: Optional[List[KeySlot]] = None,
        consume_slots_on_complete: bool = True,
    ) -> QSTATVerdict:
        """
        Executes full verification pipeline against evidence.
        """
        now = time.time()

        # Stage 1: Envelope Validation
        env_res = validate_envelope(signature)
        if not env_res.valid:
            v = env_res.verdict or QSTATVerdict(verdict=VerdictType.MALFORMED, reason=env_res.reason)
            v.timestamp = now
            return v

        # Stage 2: Freshness / Anti-Replay Check
        fresh_res = self.freshness_tracker.check_freshness(signature, slots=slots, current_time=now)
        if not fresh_res.valid:
            v = fresh_res.verdict or QSTATVerdict(verdict=VerdictType.REPLAY, reason=fresh_res.reason)
            v.timestamp = now
            return v

        # Stage 3: Authorization Check
        auth_res = validate_authorization(signature, verifier_id=verifier_id, available_slots=slots)
        if not auth_res.authorized:
            v = auth_res.verdict or QSTATVerdict(verdict=VerdictType.UNAUTHORIZED_VERIFICATION, reason=auth_res.reason)
            v.timestamp = now
            return v

        # Stage 4: Message Integrity (Classical hash binding)
        integ_res = validate_message_integrity(message, signature, toeplitz_seed=self.toeplitz_seed)
        if not integ_res.valid:
            v = integ_res.verdict or QSTATVerdict(verdict=VerdictType.MESSAGE_TAMPERED, reason=integ_res.reason)
            v.timestamp = now
            return v

        # If no quantum statistics were provided (e.g. preliminary check), return inconclusive
        if stats is None:
            return QSTATVerdict(
                verdict=VerdictType.INCONCLUSIVE,
                reason="Pre-measurement checks passed, but quantum statistics have not yet been evaluated",
                timestamp=now,
            )

        # Stage 5: Binomial Statistical Hypothesis Testing
        # Calculate acceptance threshold s_a
        s_a = calculate_acceptance_threshold(
            L=stats.L_per_block,
            n_blocks=stats.n_blocks,
            expected_honest_noise=self.expected_honest_noise,
            target_false_rejection=self.target_false_rejection,
        )

        failed_blocks: List[int] = []
        block_p_values: List[float] = []

        for b in stats.block_statistics:
            test_res = self.binomial_verifier.test_block(b, n_blocks=stats.n_blocks)
            block_p_values.append(test_res.p_value)
            if not test_res.is_valid:
                failed_blocks.append(b.block_index)

        global_test = self.binomial_verifier.test_global(stats)

        # Stage 6: Forensic Fingerprint Classification
        fingerprint = self.fingerprint_engine.analyze(stats, threshold=s_a)

        # Stage 7: Final Verdict Synthesis
        if len(failed_blocks) == 0 and global_test.is_valid:
            # Clean acceptance
            verdict = QSTATVerdict(
                verdict=VerdictType.ACCEPT,
                reason=(
                    f"Signature verified legitimately: all {stats.n_blocks} blocks remained below "
                    f"statistical acceptance threshold s_a = {s_a:.4f} (global mismatch: {stats.global_mismatch_rate:.4f})"
                ),
                observed_rate=stats.global_mismatch_rate,
                threshold=s_a,
                p_value=global_test.p_value,
                confidence_interval=list(global_test.confidence_interval),
                evidence={
                    "fingerprint": fingerprint.to_dict(),
                    "total_states": stats.total_states,
                    "mismatches": stats.total_mismatches,
                    "basis_rates": stats.per_basis_rates,
                },
                timestamp=now,
            )
        else:
            # Determine appropriate threat verdict based on fingerprint
            primary_fail_block = failed_blocks[0] if failed_blocks else None
            max_block_rate = stats.max_block_rate

            if fingerprint.classification == "POSSIBLE_SPLICE_FORGERY":
                v_type = VerdictType.FORGERY_SUSPECTED
                reason_text = (
                    f"Splice forgery suspected: {len(failed_blocks)} of {stats.n_blocks} blocks exceeded threshold s_a = {s_a:.4f}. "
                    f"{fingerprint.block_diagnosis}"
                )
            elif fingerprint.classification == "POSSIBLE_IMPERSONATION_OR_FORGERY":
                if stats.global_mismatch_rate >= 0.40 and len(failed_blocks) >= (stats.n_blocks * 0.7):
                    v_type = VerdictType.IMPERSONATION_SUSPECTED
                    reason_text = (
                        f"Impersonation attack suspected: pervasive error rate ({stats.global_mismatch_rate:.3f}) across "
                        f"{len(failed_blocks)} blocks clustering around random guessing bound (50%)."
                    )
                else:
                    v_type = VerdictType.FORGERY_SUSPECTED
                    reason_text = f"Forgery suspected: block mismatch rate {max_block_rate:.4f} exceeded threshold {s_a:.4f}."
            elif fingerprint.classification == "CHANNEL_ANOMALY":
                v_type = VerdictType.CHANNEL_ANOMALY
                reason_text = (
                    f"Quantum channel anomaly: elevated physical disturbance ({stats.global_mismatch_rate:.4f}). "
                    f"{fingerprint.basis_diagnosis}"
                )
            else:
                v_type = VerdictType.FORGERY_SUSPECTED
                reason_text = (
                    f"Block {primary_fail_block} mismatch rate {max_block_rate:.4f} exceeded "
                    f"acceptance threshold s_a = {s_a:.4f}."
                )

            verdict = QSTATVerdict(
                verdict=v_type,
                reason=reason_text,
                block=primary_fail_block,
                observed_rate=max_block_rate,
                threshold=s_a,
                p_value=min(block_p_values) if block_p_values else global_test.p_value,
                confidence_interval=list(global_test.confidence_interval),
                evidence={
                    "failed_blocks": failed_blocks,
                    "fingerprint": fingerprint.to_dict(),
                    "global_rate": stats.global_mismatch_rate,
                    "basis_rates": stats.per_basis_rates,
                },
                timestamp=now,
            )

        # Mark slots and nonce as consumed
        if consume_slots_on_complete:
            self.freshness_tracker.register_consumed(signature, slots=slots)

        return verdict
