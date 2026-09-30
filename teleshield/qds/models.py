"""
QDS Data Models
Defines data structures for key slots, private key descriptors, signatures,
and slot lifecycle states.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import uuid

from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue


class SlotStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    CONSUMED = "CONSUMED"
    EXPIRED = "EXPIRED"


@dataclass
class PrivateKeyState:
    """Classical specification of a single private key Pauli eigenstate."""
    tag_index: int
    bit_value: int
    state_index: int
    basis: StateBasis
    eigenvalue: Eigenvalue

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag_index": self.tag_index,
            "bit_value": self.bit_value,
            "state_index": self.state_index,
            "basis": self.basis.value,
            "eigenvalue": self.eigenvalue.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrivateKeyState":
        return cls(
            tag_index=int(data["tag_index"]),
            bit_value=int(data["bit_value"]),
            state_index=int(data["state_index"]),
            basis=StateBasis(str(data["basis"]).upper()),
            eigenvalue=Eigenvalue.from_str(data["eigenvalue"]),
        )


class KeySlot:
    """
    Represents a single quantum memory slot at a verifier node.
    Holds a teleported physical quantum state and its verification metadata.
    """

    def __init__(
        self,
        slot_id: Optional[str] = None,
        key_id: str = "",
        verifier_id: str = "verifier_bob",
        tag_index: int = 0,
        bit_value: int = 0,
        state_index: int = 0,
        basis: StateBasis = StateBasis.Z,
        eigenvalue: Eigenvalue = Eigenvalue.PLUS,
        epoch: int = 1,
        status: SlotStatus = SlotStatus.AVAILABLE,
        created_at: Optional[float] = None,
        consumed_at: Optional[float] = None,
        quantum_state: Optional[QuantumState] = None,
    ) -> None:
        self.slot_id = slot_id or str(uuid.uuid4())
        self.key_id = key_id
        self.verifier_id = verifier_id
        self.tag_index = tag_index
        self.bit_value = bit_value
        self.state_index = state_index
        self.basis = basis
        self.eigenvalue = eigenvalue
        self.epoch = epoch
        self.status = status
        self.created_at = created_at or time.time()
        self.consumed_at = consumed_at
        self.quantum_state = quantum_state

    def consume(self) -> None:
        """Mark slot as consumed upon verification measurement."""
        self.status = SlotStatus.CONSUMED
        self.consumed_at = time.time()
        # Quantum state is physically destroyed/projected upon measurement
        self.quantum_state = None

    def expire(self) -> None:
        """Mark slot as expired."""
        self.status = SlotStatus.EXPIRED
        self.quantum_state = None

    @property
    def is_available(self) -> bool:
        return self.status == SlotStatus.AVAILABLE and self.quantum_state is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "key_id": self.key_id,
            "verifier_id": self.verifier_id,
            "tag_index": self.tag_index,
            "bit_value": self.bit_value,
            "state_index": self.state_index,
            "basis": self.basis.value,
            "eigenvalue": self.eigenvalue.value,
            "epoch": self.epoch,
            "status": self.status.value,
            "created_at": self.created_at,
            "consumed_at": self.consumed_at,
            "has_state": self.quantum_state is not None,
        }

    def __repr__(self) -> str:
        return (
            f"KeySlot(id={self.slot_id[:8]}, tag={self.tag_index}, b={self.bit_value}, "
            f"k={self.state_index}, status={self.status.value})"
        )


@dataclass
class QDSKey:
    """Metadata describing a generated QDS key pair."""
    key_id: str
    signer_id: str
    verifier_id: str
    n: int  # Number of tag bits
    L: int  # Number of quantum states per bit value
    basis_mode: str  # "XZ" or "XYZ"
    epoch: int = 1
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_id": self.key_id,
            "signer_id": self.signer_id,
            "verifier_id": self.verifier_id,
            "n": self.n,
            "L": self.L,
            "basis_mode": self.basis_mode,
            "epoch": self.epoch,
            "created_at": self.created_at,
        }


@dataclass
class QDSSignature:
    """
    Quantum Digital Signature envelope.
    Contains message binding, tag bits, and signer's revealed private key state descriptions.
    """
    message_id: str
    signer_id: str
    verifier_id: str
    key_id: str
    epoch: int
    timestamp: float
    nonce: str
    tag: str
    tag_bits: List[int]
    revealed_states: List[Dict[str, Any]]
    protocol_version: str = "1.0"
    hash_mode: str = "sha256"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "signer_id": self.signer_id,
            "verifier_id": self.verifier_id,
            "key_id": self.key_id,
            "epoch": self.epoch,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "tag": self.tag,
            "tag_bits": self.tag_bits,
            "revealed_states": self.revealed_states,
            "protocol_version": self.protocol_version,
            "hash_mode": self.hash_mode,
        }
