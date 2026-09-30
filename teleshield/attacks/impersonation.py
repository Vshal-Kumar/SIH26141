"""
Impersonation Attack Module
Simulates an unauthenticated adversary lacking the legitimate private key
attempting to produce a valid signature by generating pseudo-random state descriptions.
Expected to produce pervasive high error rates (~50%) clustering around the random guessing bound.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import time
import uuid
import numpy as np

from teleshield.attacks.base import BaseAttack, AttackExecutionResult
from teleshield.qds.models import QDSSignature
from teleshield.qds.hashing import HashMode, compute_message_tag
from teleshield.quantum.states import StateBasis, Eigenvalue


class ImpersonationAttack(BaseAttack):
    """
    Fabricates an entire signature envelope without private key access.
    """

    def __init__(
        self,
        impersonated_signer: str = "signer_alice",
        basis_mode: str = "XZ",
        strength: float = 1.0,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(
            name="impersonation",
            description="Full impersonation attempt by unauthenticated adversary",
            strength=strength,
        )
        self.impersonated_signer = impersonated_signer
        self.basis_mode = basis_mode.upper()
        self.seed = seed

    def execute(
        self,
        message: str,
        key_id: str,
        verifier_id: str,
        n_bits: int = 64,
        L: int = 222,
        hash_mode: HashMode = HashMode.SHA256,
        toeplitz_seed: int = 1337,
        **kwargs,
    ) -> AttackExecutionResult:
        rng = np.random.default_rng(self.seed)

        # Attacker correctly hashes message to avoid trivial message-tampered rejection
        tag_hex, tag_bits = compute_message_tag(
            message=message,
            mode=hash_mode,
            n_bits=n_bits,
            toeplitz_seed=toeplitz_seed,
        )

        pool = [StateBasis.X, StateBasis.Z] if self.basis_mode == "XZ" else [StateBasis.X, StateBasis.Y, StateBasis.Z]
        ev_pool = [Eigenvalue.PLUS, Eigenvalue.MINUS]

        # Fabricate revealed states across all n blocks and L states
        fabricated_states: List[Dict[str, Any]] = []
        for j in range(n_bits):
            for k in range(L):
                b = pool[int(rng.choice(len(pool)))]
                ev = ev_pool[int(rng.choice(len(ev_pool)))]
                fabricated_states.append({
                    "tag_index": j,
                    "bit_value": tag_bits[j],
                    "state_index": k,
                    "basis": b.value,
                    "eigenvalue": ev.value,
                })

        forged_sig = QDSSignature(
            message_id=f"msg_impers_{uuid.uuid4().hex[:8]}",
            signer_id=self.impersonated_signer,
            verifier_id=verifier_id,
            key_id=key_id,
            epoch=1,
            timestamp=time.time(),
            nonce=f"nonce_{uuid.uuid4().hex[:12]}",
            tag=tag_hex,
            tag_bits=tag_bits,
            revealed_states=fabricated_states,
            protocol_version="1.0",
            hash_mode=hash_mode.value,
        )

        return AttackExecutionResult(
            attack_type=self.name,
            description="Fabricated complete signature envelope without legitimate private key",
            target_blocks=list(range(n_bits)),
            strength=self.strength,
            ground_truth_modified=True,
            manipulated_signature=forged_sig,
            metadata={
                "fabricated_states_count": len(fabricated_states),
                "impersonated_signer": self.impersonated_signer,
            },
        )
