"""
Threshold-Aware Attack Module
Simulates an intelligent adversary who knows the single-session acceptance threshold s_a
and carefully tunes perturbation intensity to stay strictly below s_a in individual sessions.
Evaluated across consecutive sessions to validate CUSUM cumulative drift detection.
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Optional, Any
import copy
import numpy as np

from teleshield.attacks.base import BaseAttack, AttackExecutionResult
from teleshield.qds.models import KeySlot
from teleshield.quantum.states import QuantumState
from teleshield.quantum.noise import apply_depolarizing_channel


class ThresholdAwareAttack(BaseAttack):
    """
    Sub-threshold drift attack designed to evade single-session hypothesis testing.
    """

    def __init__(
        self,
        sub_threshold_rate: float = 0.025,
        session_threshold: float = 0.045,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(
            name="threshold_aware",
            description=f"Sub-threshold evasion attack (rate {sub_threshold_rate} < threshold {session_threshold})",
            strength=sub_threshold_rate,
        )
        self.sub_threshold_rate = sub_threshold_rate
        self.session_threshold = session_threshold
        self.seed = seed

    def execute(
        self,
        slots: Dict[Tuple[int, int, int], KeySlot],
        **kwargs,
    ) -> AttackExecutionResult:
        """
        Applies depolarizing channel with noise parameter carefully calibrated below s_a.
        """
        attacked_slots = copy.copy(slots)
        modified_count = 0

        for (j, b, k), slot in list(attacked_slots.items()):
            if slot.quantum_state is None:
                continue

            rho = apply_depolarizing_channel(slot.quantum_state.density_matrix, self.sub_threshold_rate)
            new_state = QuantumState(
                density_matrix=rho,
                basis=slot.quantum_state.basis,
                eigenvalue=slot.quantum_state.eigenvalue,
            )

            new_slot = KeySlot(
                slot_id=slot.slot_id,
                key_id=slot.key_id,
                verifier_id=slot.verifier_id,
                tag_index=slot.tag_index,
                bit_value=slot.bit_value,
                state_index=slot.state_index,
                basis=slot.basis,
                eigenvalue=slot.eigenvalue,
                epoch=slot.epoch,
                status=slot.status,
                created_at=slot.created_at,
                quantum_state=new_state,
            )
            attacked_slots[(j, b, k)] = new_slot
            modified_count += 1

        return AttackExecutionResult(
            attack_type=self.name,
            description=f"Injected sub-threshold noise ({self.sub_threshold_rate:.4f}) below s_a ({self.session_threshold:.4f})",
            target_blocks=[],
            strength=self.sub_threshold_rate,
            ground_truth_modified=True,
            manipulated_slots=attacked_slots,
            metadata={
                "sub_threshold_rate": self.sub_threshold_rate,
                "session_threshold": self.session_threshold,
                "states_disturbed": modified_count,
            },
        )
