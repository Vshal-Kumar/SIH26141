"""
Splice Forgery Attack Module
Splices segments of a valid signature from one message into another message.
Demonstrates why per-block statistical verification is mathematically indispensable.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import copy
import numpy as np

from teleshield.attacks.base import BaseAttack, AttackExecutionResult
from teleshield.qds.models import QDSSignature
from teleshield.qds.hashing import HashMode, compute_message_tag


class SpliceForgeryAttack(BaseAttack):
    """
    Constructs a splice forgery by combining legitimate state claims from
    a donor signature with a new target message.
    """

    def __init__(
        self,
        target_blocks: Optional[List[int]] = None,
        strength: float = 1.0,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(
            name="splice_forgery",
            description="Splice forgery combining disparate signature blocks",
            strength=strength,
        )
        self.target_blocks = target_blocks
        self.seed = seed

    def execute(
        self,
        donor_signature: QDSSignature,
        target_message: str,
        hash_mode: HashMode = HashMode.SHA256,
        toeplitz_seed: int = 1337,
        **kwargs,
    ) -> AttackExecutionResult:
        """
        Creates a spliced signature:
        Calculates tag for target_message.
        Keeps donor's revealed states for blocks where target and donor tags match,
        and artificially inserts donor's claims into differing blocks.
        """
        rng = np.random.default_rng(self.seed)
        n = len(donor_signature.tag_bits)

        # Compute tag for new message
        target_tag_hex, target_tag_bits = compute_message_tag(
            message=target_message,
            mode=hash_mode,
            n_bits=n,
            toeplitz_seed=toeplitz_seed,
        )

        differing_positions = [
            j for j in range(n) if target_tag_bits[j] != donor_signature.tag_bits[j]
        ]

        if self.target_blocks is not None:
            blocks_spliced = [b for b in self.target_blocks if 0 <= b < n]
        else:
            # Splice differing positions according to attack strength
            num_splice = max(1, int(np.ceil(len(differing_positions) * self.strength)))
            if differing_positions:
                blocks_spliced = list(rng.choice(differing_positions, size=min(num_splice, len(differing_positions)), replace=False))
            else:
                blocks_spliced = list(range(min(4, n)))

        # Build spliced signature:
        # Sets tag and tag_bits to target_message's tag
        # Retains donor's revealed state descriptions
        spliced_sig = copy.deepcopy(donor_signature)
        spliced_sig.tag = target_tag_hex
        spliced_sig.tag_bits = target_tag_bits

        return AttackExecutionResult(
            attack_type=self.name,
            description=f"Spliced donor signature onto target message across {len(blocks_spliced)} blocks",
            target_blocks=sorted(blocks_spliced),
            strength=self.strength,
            ground_truth_modified=True,
            manipulated_signature=spliced_sig,
            metadata={
                "target_message": target_message,
                "differing_tag_positions": differing_positions,
                "spliced_blocks": blocks_spliced,
            },
        )
