"""
QDS Signer Module
Signs messages by calculating message tags and revealing the corresponding
L private-key Pauli eigenstate descriptions per tag bit.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
import time
import uuid

from teleshield.qds.keygen import QDSKeyPair
from teleshield.qds.models import QDSSignature
from teleshield.qds.hashing import HashMode, compute_message_tag


class QDSSigner:
    """Represents a signing entity (Alice) holding a QDS private key pair."""

    def __init__(self, keypair: QDSKeyPair) -> None:
        self.keypair = keypair
        self.signer_id = keypair.signer_id

    def sign(
        self,
        message: str,
        hash_mode: HashMode = HashMode.SHA256,
        nonce: Optional[str] = None,
        toeplitz_seed: int = 1337,
    ) -> QDSSignature:
        """
        Signs message:
          1. Computes tag = Hash(message) of length n.
          2. For each tag bit b_j, reveals the L private-key state descriptions.
          3. Bundles envelope into QDSSignature.
        """
        n = self.keypair.n
        tag_hex, tag_bits = compute_message_tag(
            message=message,
            mode=hash_mode,
            n_bits=n,
            toeplitz_seed=toeplitz_seed,
        )

        revealed_states = self.keypair.get_revealed_states_for_tag(tag_bits)
        signature_nonce = nonce or uuid.uuid4().hex[:16]
        message_id = f"msg_{uuid.uuid4().hex[:12]}"

        return QDSSignature(
            message_id=message_id,
            signer_id=self.signer_id,
            verifier_id=self.keypair.verifier_id,
            key_id=self.keypair.key_id,
            epoch=self.keypair.metadata.epoch,
            timestamp=time.time(),
            nonce=signature_nonce,
            tag=tag_hex,
            tag_bits=tag_bits,
            revealed_states=revealed_states,
            protocol_version="1.0",
            hash_mode=hash_mode.value,
        )
