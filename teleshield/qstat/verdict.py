"""
Q-STAT Verdict Module
Defines structured, deterministic, and explainable verdicts for QDS verification.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List


class VerdictType(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    REPLAY = "REPLAY"
    FORGERY_SUSPECTED = "FORGERY_SUSPECTED"
    IMPERSONATION_SUSPECTED = "IMPERSONATION_SUSPECTED"
    CHANNEL_ANOMALY = "CHANNEL_ANOMALY"
    UNAUTHORIZED_VERIFICATION = "UNAUTHORIZED_VERIFICATION"
    MESSAGE_TAMPERED = "MESSAGE_TAMPERED"
    MALFORMED = "MALFORMED"
    INCONCLUSIVE = "INCONCLUSIVE"


# Alias for backward compatibility
Verdict = VerdictType


@dataclass
class QSTATVerdict:
    """
    Structured outcome of the Q-STAT verification pipeline.
    Provides complete mathematical justification, p-values, and forensic evidence.
    """
    verdict: VerdictType
    reason: str
    block: Optional[int] = None
    observed_rate: Optional[float] = None
    threshold: Optional[float] = None
    p_value: Optional[float] = None
    confidence_interval: Optional[List[float]] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    @property
    def is_accepted(self) -> bool:
        return self.verdict == VerdictType.ACCEPT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "reason": self.reason,
            "block": self.block,
            "observed_rate": self.observed_rate,
            "threshold": self.threshold,
            "p_value": self.p_value,
            "confidence_interval": self.confidence_interval,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        rate_str = f", rate={self.observed_rate:.4f}" if self.observed_rate is not None else ""
        thresh_str = f", thresh={self.threshold:.4f}" if self.threshold is not None else ""
        return f"QSTATVerdict({self.verdict.value}: {self.reason}{rate_str}{thresh_str})"
