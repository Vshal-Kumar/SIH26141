"""
Q-STAT Freshness and Anti-Replay Module
Maintains nonce registry, epoch records, timestamp validity window,
and consumed slot tracking to deterministically prevent replay attacks.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, Dict, Optional, List
import time

from teleshield.qstat.verdict import VerdictType, QSTATVerdict
from teleshield.qds.models import QDSSignature, KeySlot, SlotStatus


@dataclass
class FreshnessValidationResult:
    valid: bool
    reason: str
    verdict: Optional[QSTATVerdict] = None


class FreshnessTracker:
    """
    Stateful registry tracking nonces, epochs, and consumed quantum slots.
    Guarantees deterministic replay detection.
    """

    def __init__(self, timestamp_window_seconds: float = 600.0) -> None:
        self.timestamp_window_seconds = timestamp_window_seconds
        self.seen_nonces: Set[str] = set()
        self.current_epochs: Dict[str, int] = {}  # key_id -> epoch
        self.consumed_slots: Set[str] = set()  # slot_id

    def check_freshness(
        self,
        signature: QDSSignature,
        slots: Optional[List[KeySlot]] = None,
        current_time: Optional[float] = None,
    ) -> FreshnessValidationResult:
        now = current_time if current_time is not None else time.time()

        # 1. Nonce uniqueness check
        if signature.nonce in self.seen_nonces:
            verdict = QSTATVerdict(
                verdict=VerdictType.REPLAY,
                reason=f"Signature nonce '{signature.nonce}' has already been processed (Replay detected)",
                evidence={"nonce": signature.nonce, "timestamp": signature.timestamp},
            )
            return FreshnessValidationResult(valid=False, reason=verdict.reason, verdict=verdict)

        # 2. Timestamp window check
        time_diff = abs(now - signature.timestamp)
        if time_diff > self.timestamp_window_seconds:
            verdict = QSTATVerdict(
                verdict=VerdictType.REPLAY,
                reason=(
                    f"Signature timestamp delta {time_diff:.1f}s exceeds freshness window "
                    f"of {self.timestamp_window_seconds:.1f}s (Stale message or replay)"
                ),
                evidence={"delta_seconds": time_diff, "window_seconds": self.timestamp_window_seconds},
            )
            return FreshnessValidationResult(valid=False, reason=verdict.reason, verdict=verdict)

        # 3. Consumed quantum slot check
        if slots:
            for s in slots:
                if s.slot_id in self.consumed_slots or s.status == SlotStatus.CONSUMED:
                    verdict = QSTATVerdict(
                        verdict=VerdictType.REPLAY,
                        reason=f"Quantum key slot {s.slot_id} has already been consumed (Replay of measured quantum state)",
                        block=s.tag_index,
                        evidence={"slot_id": s.slot_id, "status": s.status.value},
                    )
                    return FreshnessValidationResult(valid=False, reason=verdict.reason, verdict=verdict)

        return FreshnessValidationResult(valid=True, reason="Freshness verified")

    def register_consumed(self, signature: QDSSignature, slots: Optional[List[KeySlot]] = None) -> None:
        """Register nonce and slots as permanently consumed."""
        self.seen_nonces.add(signature.nonce)
        self.current_epochs[signature.key_id] = signature.epoch
        if slots:
            for s in slots:
                self.consumed_slots.add(s.slot_id)
                s.consume()

    def reset(self) -> None:
        """Clear all registries (for test isolation)."""
        self.seen_nonces.clear()
        self.current_epochs.clear()
        self.consumed_slots.clear()
