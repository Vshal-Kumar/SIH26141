"""
Intercept-Resend Attack Module
Simulates an active quantum eavesdropper (Eve) who intercepts quantum states,
measures them in a chosen basis, prepares a replacement state matching the outcome,
and forwards it to the verifier.
Introduces an expected 25% disturbance in XZ mode and 33.3% in XYZ mode.
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Optional, Any
import copy
import numpy as np

from teleshield.attacks.base import BaseAttack, AttackExecutionResult
from teleshield.qds.models import KeySlot
from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.measurement import measure_state_projective


class InterceptResendAttack(BaseAttack):
    """
    Physical intercept-resend attack on in-flight or stored quantum key states.
    """

    def __init__(
        self,
        basis_mode: str = "XZ",
        strength: float = 1.0,
        target_blocks: Optional[List[int]] = None,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(
            name="intercept_resend",
            description="Active intercept-resend measurement and state reprojection",
            strength=strength,
        )
        self.basis_mode = basis_mode.upper()
        self.target_blocks = target_blocks
        self.seed = seed

    def execute(
        self,
        slots: Dict[Tuple[int, int, int], KeySlot],
        **kwargs,
    ) -> AttackExecutionResult:
        """
        Intercepts and reprojects quantum states stored in slots.
        """
        rng = np.random.default_rng(self.seed)
        bases_pool = [StateBasis.X, StateBasis.Z] if self.basis_mode == "XZ" else [StateBasis.X, StateBasis.Y, StateBasis.Z]

        attacked_slots = copy.copy(slots)
        modified_count = 0
        affected_blocks_set = set()

        for (j, b, k), slot in list(attacked_slots.items()):
            if self.target_blocks is not None and j not in self.target_blocks:
                continue

            # Apply attack with probability = strength
            if rng.random() <= self.strength and slot.quantum_state is not None:
                affected_blocks_set.add(j)
                # Eve picks a random basis to measure
                eve_basis = bases_pool[int(rng.choice(len(bases_pool)))]
                m_res = measure_state_projective(
                    state=slot.quantum_state,
                    basis=eve_basis,
                    shots=1,
                    seed=int(rng.integers(0, 2**31 - 1)),
                )

                # Eve re-prepares state in the observed eigenstate
                reprepared_state = QuantumState.from_basis_and_eigenvalue(
                    basis=eve_basis,
                    eigenvalue=m_res.observed_eigenvalue,
                )

                # Create modified slot with Eve's reprepared quantum state
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
                    quantum_state=reprepared_state,
                )
                attacked_slots[(j, b, k)] = new_slot
                modified_count += 1

        return AttackExecutionResult(
            attack_type=self.name,
            description=f"Intercepted and reprepared {modified_count} quantum states",
            target_blocks=sorted(list(affected_blocks_set)),
            strength=self.strength,
            ground_truth_modified=True,
            manipulated_slots=attacked_slots,
            metadata={
                "modified_states_count": modified_count,
                "eve_basis_mode": self.basis_mode,
            },
        )
