"""
Q-STAT Authorization Validation Module
Verifies that the verifying entity possesses authorized access to the quantum
key slots corresponding to the signature's claimed key_id and verifier_id.
Failure returns UNAUTHORIZED_VERIFICATION.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

from teleshield.qstat.verdict import VerdictType, QSTATVerdict
from teleshield.qds.models import QDSSignature, KeySlot


@dataclass
class AuthorizationResult:
    authorized: bool
    reason: str
    verdict: Optional[QSTATVerdict] = None


def validate_authorization(
    signature: QDSSignature,
    verifier_id: str,
    available_slots: Optional[List[KeySlot]] = None,
) -> AuthorizationResult:
    """
    Checks authorization:
      1. Signature target verifier_id matches current verifier.
      2. Verifier has valid, assigned quantum slots matching signature key_id.
    """
    # 1. Target verifier match
    if signature.verifier_id != verifier_id:
        verdict = QSTATVerdict(
            verdict=VerdictType.UNAUTHORIZED_VERIFICATION,
            reason=(
                f"Verifier '{verifier_id}' is not the authorized recipient of this signature "
                f"(designated recipient: '{signature.verifier_id}')"
            ),
            evidence={"claimed_verifier": signature.verifier_id, "actual_verifier": verifier_id},
        )
        return AuthorizationResult(authorized=False, reason=verdict.reason, verdict=verdict)

    # 2. Key slot ownership check
    if available_slots is not None:
        if len(available_slots) == 0:
            verdict = QSTATVerdict(
                verdict=VerdictType.UNAUTHORIZED_VERIFICATION,
                reason=(
                    f"Verifier '{verifier_id}' possesses no quantum memory slots for key_id '{signature.key_id}' "
                    f"(Unauthorized verification attempt)"
                ),
                evidence={"key_id": signature.key_id, "verifier_id": verifier_id},
            )
            return AuthorizationResult(authorized=False, reason=verdict.reason, verdict=verdict)

        # Check key_id match on slots
        for s in available_slots:
            if s.key_id != signature.key_id:
                verdict = QSTATVerdict(
                    verdict=VerdictType.UNAUTHORIZED_VERIFICATION,
                    reason=(
                        f"Slot {s.slot_id} belongs to key '{s.key_id}', not signature key '{signature.key_id}'"
                    ),
                    evidence={"slot_key_id": s.key_id, "signature_key_id": signature.key_id},
                )
                return AuthorizationResult(authorized=False, reason=verdict.reason, verdict=verdict)

    return AuthorizationResult(authorized=True, reason="Authorization verified")
