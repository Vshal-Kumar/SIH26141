"""
Replay Attack Module
Simulates an adversary eavesdropping on a legitimate verification event
and attempting to replay the identical signature envelope or reuse consumed quantum slots.
Expected outcome: Deterministic REPLAY verdict.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import copy

from teleshield.attacks.base import BaseAttack, AttackExecutionResult
from teleshield.qds.models import QDSSignature


class ReplayAttack(BaseAttack):
    """
    Submits a previously verified signature envelope without modifying its nonce or timestamp.
    """

    def __init__(self, strength: float = 1.0) -> None:
        super().__init__(
            name="replay",
            description="Replay of a previously transmitted and consumed signature",
            strength=strength,
        )

    def execute(
        self,
        valid_signature: QDSSignature,
        **kwargs,
    ) -> AttackExecutionResult:
        """
        Clones signature exactly as-is to trigger nonce reuse or consumed-slot detection.
        """
        replayed_sig = copy.deepcopy(valid_signature)

        return AttackExecutionResult(
            attack_type=self.name,
            description=f"Replaying signature with existing nonce '{valid_signature.nonce}'",
            target_blocks=list(range(len(valid_signature.tag_bits))),
            strength=self.strength,
            ground_truth_modified=True,
            manipulated_signature=replayed_sig,
            metadata={
                "original_nonce": valid_signature.nonce,
                "original_timestamp": valid_signature.timestamp,
            },
        )
