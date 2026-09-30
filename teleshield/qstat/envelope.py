"""
Q-STAT Envelope Validation Module
Checks signature envelope structure, schema integrity, and protocol fields.
Failure returns MALFORMED verdict.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional

from teleshield.qds.models import QDSSignature
from teleshield.qstat.verdict import VerdictType, QSTATVerdict


@dataclass
class EnvelopeValidationResult:
    valid: bool
    reason: str
    verdict: Optional[QSTATVerdict] = None


def validate_envelope(
    signature: Any,
    expected_protocol_version: str = "1.0",
) -> EnvelopeValidationResult:
    """
    Validates signature envelope for required fields, type consistency,
    and non-empty values.
    """
    if not isinstance(signature, QDSSignature):
        verdict = QSTATVerdict(
            verdict=VerdictType.MALFORMED,
            reason="Payload is not an instance of QDSSignature",
            evidence={"type": type(signature).__name__},
        )
        return EnvelopeValidationResult(valid=False, reason=verdict.reason, verdict=verdict)

    # Required string fields
    required_fields = [
        ("message_id", signature.message_id),
        ("signer_id", signature.signer_id),
        ("verifier_id", signature.verifier_id),
        ("key_id", signature.key_id),
        ("nonce", signature.nonce),
        ("tag", signature.tag),
        ("protocol_version", signature.protocol_version),
    ]

    for field_name, val in required_fields:
        if not val or not isinstance(val, str) or len(val.strip()) == 0:
            verdict = QSTATVerdict(
                verdict=VerdictType.MALFORMED,
                reason=f"Envelope missing or empty required field: {field_name}",
                evidence={"missing_field": field_name},
            )
            return EnvelopeValidationResult(valid=False, reason=verdict.reason, verdict=verdict)

    if signature.protocol_version != expected_protocol_version:
        verdict = QSTATVerdict(
            verdict=VerdictType.MALFORMED,
            reason=f"Unsupported protocol version: {signature.protocol_version} (expected {expected_protocol_version})",
            evidence={"expected": expected_protocol_version, "found": signature.protocol_version},
        )
        return EnvelopeValidationResult(valid=False, reason=verdict.reason, verdict=verdict)

    if not isinstance(signature.tag_bits, list) or len(signature.tag_bits) == 0:
        verdict = QSTATVerdict(
            verdict=VerdictType.MALFORMED,
            reason="Envelope tag_bits must be a non-empty list of bits",
            evidence={"tag_bits_len": len(signature.tag_bits) if isinstance(signature.tag_bits, list) else None},
        )
        return EnvelopeValidationResult(valid=False, reason=verdict.reason, verdict=verdict)

    if not isinstance(signature.revealed_states, list) or len(signature.revealed_states) == 0:
        verdict = QSTATVerdict(
            verdict=VerdictType.MALFORMED,
            reason="Envelope revealed_states must be a non-empty list",
            evidence={"revealed_len": len(signature.revealed_states) if isinstance(signature.revealed_states, list) else None},
        )
        return EnvelopeValidationResult(valid=False, reason=verdict.reason, verdict=verdict)

    return EnvelopeValidationResult(valid=True, reason="Envelope structure valid")
