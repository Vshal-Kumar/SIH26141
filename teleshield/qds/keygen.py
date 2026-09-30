"""
QDS Key Generation Module
Generates classical private key state descriptions and corresponding physical
quantum states across n tag positions and L states per bit value (0 and 1).
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Optional
import uuid
import time
import numpy as np

from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.models import PrivateKeyState, QDSKey


class QDSKeyPair:
    """Encapsulates the classical private key and prepared quantum states."""

    def __init__(
        self,
        key_id: str,
        signer_id: str,
        verifier_id: str,
        n: int,
        L: int,
        basis_mode: str,
        private_states: Dict[Tuple[int, int], List[PrivateKeyState]],
        quantum_states: Dict[Tuple[int, int, int], QuantumState],
        created_at: float,
    ) -> None:
        self.key_id = key_id
        self.signer_id = signer_id
        self.verifier_id = verifier_id
        self.n = n
        self.L = L
        self.basis_mode = basis_mode
        self.private_states = private_states  # (tag_idx, bit_val) -> [PrivateKeyState]
        self.quantum_states = quantum_states  # (tag_idx, bit_val, state_idx) -> QuantumState
        self.created_at = created_at
        self.metadata = QDSKey(
            key_id=key_id,
            signer_id=signer_id,
            verifier_id=verifier_id,
            n=n,
            L=L,
            basis_mode=basis_mode,
            epoch=1,
            created_at=created_at,
        )

    @property
    def public_key(self) -> QDSKey:
        """Returns the public key metadata container."""
        return self.metadata

    def get_revealed_states_for_tag(self, tag_bits: List[int]) -> List[Dict[str, Any]]:
        """
        Extract the signer's revealed private states corresponding to the given tag bits.
        For each bit j in tag, reveals the L state descriptions for bit value b_j.
        """
        revealed = []
        for j, bit_val in enumerate(tag_bits):
            states_for_bit = self.private_states.get((j, bit_val), [])
            for st in states_for_bit:
                revealed.append(st.to_dict())
        return revealed


def generate_qds_keypair(
    n: int = 64,
    L: int = 222,
    backend: Optional[QuantumBackend] = None,
    signer_id: str = "signer_alice",
    verifier_id: str = "verifier_bob",
    basis_mode: str = "XZ",
    seed: Optional[int] = None,
) -> QDSKeyPair:
    """
    Generates a full QDS key pair.
    For each tag bit j in [0, n-1]:
      Bit value 0: L Pauli eigenstates
      Bit value 1: L Pauli eigenstates
    Total states prepared: 2 * n * L.
    """
    rng = np.random.default_rng(seed)
    q_backend = backend or ExactBackend()
    key_id = f"key_{uuid.uuid4().hex[:12]}"
    now = time.time()

    mode = basis_mode.upper()
    if mode == "XYZ":
        bases_pool = [StateBasis.X, StateBasis.Y, StateBasis.Z]
    else:
        bases_pool = [StateBasis.X, StateBasis.Z]

    private_dict: Dict[Tuple[int, int], List[PrivateKeyState]] = {}
    quantum_dict: Dict[Tuple[int, int, int], QuantumState] = {}

    for j in range(n):
        for bit_val in (0, 1):
            states_list: List[PrivateKeyState] = []
            for k in range(L):
                chosen_basis = bases_pool[int(rng.choice(len(bases_pool)))]
                chosen_ev = Eigenvalue.PLUS if rng.random() < 0.5 else Eigenvalue.MINUS

                p_state = PrivateKeyState(
                    tag_index=j,
                    bit_value=bit_val,
                    state_index=k,
                    basis=chosen_basis,
                    eigenvalue=chosen_ev,
                )
                states_list.append(p_state)

                # Prepare the physical state using backend
                q_state = q_backend.prepare_state(chosen_basis, chosen_ev)
                quantum_dict[(j, bit_val, k)] = q_state

            private_dict[(j, bit_val)] = states_list

    return QDSKeyPair(
        key_id=key_id,
        signer_id=signer_id,
        verifier_id=verifier_id,
        n=n,
        L=L,
        basis_mode=basis_mode,
        private_states=private_dict,
        quantum_states=quantum_dict,
        created_at=now,
    )
