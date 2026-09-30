"""
Channel Manipulation Attack Module
Simulates active physical manipulation or jamming of the quantum teleportation channel.
Supports bit-flip, phase-flip, Y-error, depolarizing, dephasing, and loss channels
with configurable attack strength.
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Optional, Any
import copy
import numpy as np

from teleshield.attacks.base import BaseAttack, AttackExecutionResult
from teleshield.qds.models import KeySlot
from teleshield.quantum.states import QuantumState
from teleshield.quantum.pauli import apply_pauli
from teleshield.quantum.noise import (
    NoiseModelConfig, NoiseType, apply_quantum_noise,
    apply_depolarizing_channel, apply_dephasing_channel,
    apply_bit_flip_channel, apply_bit_phase_flip_channel
)


class ChannelManipulationAttack(BaseAttack):
    """
    Applies adversarial physical channel noise to stored quantum states.
    """

    def __init__(
        self,
        channel_type: str = "depolarizing",
        strength: float = 0.20,
        target_blocks: Optional[List[int]] = None,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(
            name="channel_manipulation",
            description=f"Channel manipulation attack ({channel_type}) with strength {strength}",
            strength=strength,
        )
        self.channel_type = channel_type.lower()
        self.target_blocks = target_blocks
        self.seed = seed

    def execute(
        self,
        slots: Dict[Tuple[int, int, int], KeySlot],
        **kwargs,
    ) -> AttackExecutionResult:
        rng = np.random.default_rng(self.seed)
        attacked_slots = copy.copy(slots)
        modified_count = 0
        affected_blocks_set = set()

        for (j, b, k), slot in list(attacked_slots.items()):
            if self.target_blocks is not None and j not in self.target_blocks:
                continue

            if slot.quantum_state is None:
                continue

            affected_blocks_set.add(j)
            rho = slot.quantum_state.density_matrix

            if self.channel_type in ("depolarizing", "depol"):
                rho = apply_depolarizing_channel(rho, self.strength)
            elif self.channel_type in ("dephasing", "phase_flip"):
                rho = apply_dephasing_channel(rho, self.strength)
            elif self.channel_type in ("bit_flip", "x_error"):
                rho = apply_bit_flip_channel(rho, self.strength)
            elif self.channel_type in ("y_error", "bit_phase_flip"):
                rho = apply_bit_phase_flip_channel(rho, self.strength)
            elif self.channel_type in ("loss", "erasure"):
                # Loss destroys state with probability = strength
                if rng.random() <= self.strength:
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
                        quantum_state=None,  # Lost photon/atom
                    )
                    attacked_slots[(j, b, k)] = new_slot
                    modified_count += 1
                    continue
            else:
                rho = apply_depolarizing_channel(rho, self.strength)

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
            description=f"Manipulated {modified_count} quantum states via {self.channel_type} channel",
            target_blocks=sorted(list(affected_blocks_set)),
            strength=self.strength,
            ground_truth_modified=True,
            manipulated_slots=attacked_slots,
            metadata={
                "channel_type": self.channel_type,
                "modified_states_count": modified_count,
            },
        )
