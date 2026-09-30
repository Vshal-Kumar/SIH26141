"""
Q-STAT Message Integrity Check Module
Recalculates message tag from input plaintext and compares against
claimed signature tag. Mismatch indicates classical message tampering.
Failure returns MESSAGE_TAMPERED.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from teleshield.qstat.verdict import VerdictType, QSTATVerdict
from teleshield.qds.models import QDSSignature
from teleshield.qds.hashing import HashMode, compute_message_tag


@dataclass
class IntegrityResult:
    valid: bool
    reason: str
    calculated_tag: str
    received_tag: str
    verdict: Optional[QSTATVerdict] = None


def validate_message_integrity(
    message: str,
    signature: QDSSignature,
    toeplitz_seed: int = 1337,
) -> IntegrityResult:
    """
    Recalculates the expected tag from message and compares with signature.tag and tag_bits.
    """
    try:
        h_mode = HashMode(signature.hash_mode.lower())
    except ValueError:
        h_mode = HashMode.SHA256

    n_bits = len(signature.tag_bits)
    calc_tag_hex, calc_tag_bits = compute_message_tag(
        message=message,
        mode=h_mode,
        n_bits=n_bits,
        toeplitz_seed=toeplitz_seed,
    )

    if calc_tag_bits != signature.tag_bits or calc_tag_hex != signature.tag:
        # Find which bit positions differ
        differing_bits = [
            i for i, (b_c, b_r) in enumerate(zip(calc_tag_bits, signature.tag_bits))
            if b_c != b_r
        ]
        verdict = QSTATVerdict(
            verdict=VerdictType.MESSAGE_TAMPERED,
            reason=(
                f"Classical message hash mismatch: calculated tag '{calc_tag_hex[:12]}...' "
                f"does not match signature tag '{signature.tag[:12]}...' "
                f"({len(differing_bits)} bit differences detected)"
            ),
            block=differing_bits[0] if differing_bits else None,
            evidence={
                "calculated_tag": calc_tag_hex,
                "received_tag": signature.tag,
                "differing_positions": differing_bits[:10],
                "hash_mode": h_mode.value,
            },
        )
        return IntegrityResult(
            valid=False,
            reason=verdict.reason,
            calculated_tag=calc_tag_hex,
            received_tag=signature.tag,
            verdict=verdict,
        )

    return IntegrityResult(
        valid=True,
        reason="Message integrity verified (tag match)",
        calculated_tag=calc_tag_hex,
        received_tag=signature.tag,
    )
