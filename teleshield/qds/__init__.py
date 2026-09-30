"""
TeleShield QDS Protocol Layer
Teleportation-based Quantum Digital Signatures protocol implementation:
key generation, quantum public key distribution, signing, verification,
and slot lifecycle management.
"""

from teleshield.qds.models import (
    SlotStatus, KeySlot, QDSKey, QDSSignature, PrivateKeyState
)
from teleshield.qds.hashing import (
    HashMode, compute_message_tag, verify_message_tag
)
from teleshield.qds.keygen import (
    generate_qds_keypair, QDSKeyPair
)
from teleshield.qds.distribution import (
    distribute_public_key, DistributionReport
)
from teleshield.qds.signer import (
    QDSSigner
)
from teleshield.qds.verifier import (
    QDSVerifier
)
from teleshield.qds.session import (
    QDSSession
)

__all__ = [
    "SlotStatus",
    "KeySlot",
    "QDSKey",
    "QDSSignature",
    "PrivateKeyState",
    "HashMode",
    "compute_message_tag",
    "verify_message_tag",
    "generate_qds_keypair",
    "QDSKeyPair",
    "distribute_public_key",
    "DistributionReport",
    "QDSSigner",
    "QDSVerifier",
    "QDSSession",
]
