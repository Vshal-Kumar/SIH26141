"""
Random Forgery Attack Module
Generates random basis and eigenvalue claims for target blocks in a signature.
Simulates an adversary forging a signature by blind quantum state guessing.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import copy
import numpy as np

from teleshield.attacks.base import BaseAttack, AttackExecutionResult
from teleshield.qds.models import QDSSignature
from teleshield.quantum.states import StateBasis, Eigenvalue


class RandomForgeryAttack(BaseAttack):
    """
    Randomly alters revealed private-key state descriptions in target blocks.
    In the attacked blocks, random guessing yields an expected mismatch rate of ~50%.
    """

    def __init__(
        self,
        strength: float = 1.0,
        target_blocks: Optional[List[int]] = None,
        basis_mode: str = "XZ",
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(
            name="random_forgery",
            description="Random forgery of basis/eigenvalue state claims",
            strength=strength,
        )
        self.target_blocks = target_blocks
        self.basis_mode = basis_mode.upper()
        self.seed = seed

    def execute(
        self,
        signature: QDSSignature,
        **kwargs,
    ) -> AttackExecutionResult:
        rng = np.random.default_rng(self.seed)
        n_blocks = len(signature.tag_bits)

        # Determine target blocks
        if self.target_blocks is not None:
            blocks_to_attack = [b for b in self.target_blocks if 0 <= b < n_blocks]
        else:
            # Attack a fraction of blocks based on strength
            num_attack = max(1, int(np.ceil(n_blocks * self.strength)))
            blocks_to_attack = list(rng.choice(n_blocks, size=num_attack, replace=False))

        pool = [StateBasis.X, StateBasis.Z] if self.basis_mode == "XZ" else [StateBasis.X, StateBasis.Y, StateBasis.Z]
        ev_pool = [Eigenvalue.PLUS, Eigenvalue.MINUS]

        # Deep copy signature to manipulate revealed states
        forged_sig = copy.deepcopy(signature)
        altered_count = 0

        for st in forged_sig.revealed_states:
            j = int(st["tag_index"])
            if j in blocks_to_attack:
                # With probability proportional to strength, replace claim
                if rng.random() <= self.strength:
                    st["basis"] = pool[int(rng.choice(len(pool)))].value
                    st["eigenvalue"] = ev_pool[int(rng.choice(len(ev_pool)))].value
                    altered_count += 1

        return AttackExecutionResult(
            attack_type=self.name,
            description=f"Forged {altered_count} quantum state claims across {len(blocks_to_attack)} blocks",
            target_blocks=sorted(blocks_to_attack),
            strength=self.strength,
            ground_truth_modified=True,
            manipulated_signature=forged_sig,
            metadata={
                "altered_state_claims": altered_count,
                "target_block_count": len(blocks_to_attack),
            },
        )
