"""
Quantum Public Key Distribution Module
Distributes public quantum states from signer (Alice) to verifier (Bob)
via quantum teleportation, generates KeySlot records, and calculates fidelity telemetry.
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Optional, Any
import time
import numpy as np

from teleshield.backends.base import QuantumBackend
from teleshield.quantum.bell import BellState, BellPair, create_bell_pair
from teleshield.quantum.teleportation import TeleportationResult
from teleshield.qds.keygen import QDSKeyPair
from teleshield.qds.models import KeySlot, SlotStatus


class DistributionReport:
    """Telemetry report summarizing quantum public key distribution."""

    def __init__(
        self,
        key_id: str,
        total_states: int,
        average_fidelity: float,
        min_fidelity: float,
        max_fidelity: float,
        elapsed_seconds: float,
        slots: Dict[Tuple[int, int, int], KeySlot],
        teleportation_samples: List[Dict[str, Any]],
    ) -> None:
        self.key_id = key_id
        self.total_states = total_states
        self.average_fidelity = float(average_fidelity)
        self.min_fidelity = float(min_fidelity)
        self.max_fidelity = float(max_fidelity)
        self.elapsed_seconds = float(elapsed_seconds)
        self.slots = slots
        self.teleportation_samples = teleportation_samples

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_id": self.key_id,
            "total_states": self.total_states,
            "average_fidelity": self.average_fidelity,
            "min_fidelity": self.min_fidelity,
            "max_fidelity": self.max_fidelity,
            "elapsed_seconds": self.elapsed_seconds,
            "sample_teleportations": self.teleportation_samples[:5],
        }


def distribute_public_key(
    keypair: QDSKeyPair,
    backend: QuantumBackend,
    bell_visibility: float = 1.0,
    shots_per_teleport: int = 1,
    seed: Optional[int] = None,
) -> DistributionReport:
    """
    Simulates distribution of all 2 * n * L public quantum key states
    via quantum teleportation into verifier KeySlots.
    """
    start_time = time.perf_counter()
    rng = np.random.default_rng(seed)
    slots: Dict[Tuple[int, int, int], KeySlot] = {}
    fidelities: List[float] = []
    samples: List[Dict[str, Any]] = []

    total = 2 * keypair.n * keypair.L
    subsample_step = max(1, total // 10)  # Record details for sample teleportations

    counter = 0
    for j in range(keypair.n):
        for bit_val in (0, 1):
            private_states = keypair.private_states[(j, bit_val)]
            for k in range(keypair.L):
                p_state = private_states[k]
                q_in = keypair.quantum_states[(j, bit_val, k)]

                # Teleport state to verifier
                bp = backend.create_bell_pair(BellState.PHI_PLUS, visibility=bell_visibility)
                t_seed = int(rng.integers(0, 2**31 - 1)) if seed is not None else None
                t_res = backend.teleport(
                    input_state=q_in,
                    bell_pair=bp,
                    shots=shots_per_teleport,
                    seed=t_seed,
                )

                fidelities.append(t_res.fidelity)

                # Create KeySlot at verifier
                slot = KeySlot(
                    key_id=keypair.key_id,
                    verifier_id=keypair.verifier_id,
                    tag_index=j,
                    bit_value=bit_val,
                    state_index=k,
                    basis=p_state.basis,
                    eigenvalue=p_state.eigenvalue,
                    epoch=keypair.metadata.epoch,
                    status=SlotStatus.AVAILABLE,
                    quantum_state=t_res.output_state,
                )
                slots[(j, bit_val, k)] = slot

                if counter % subsample_step == 0 and len(samples) < 10:
                    samples.append(t_res.to_dict())
                counter += 1

    elapsed = time.perf_counter() - start_time
    avg_fid = float(np.mean(fidelities)) if fidelities else 1.0
    min_fid = float(np.min(fidelities)) if fidelities else 1.0
    max_fid = float(np.max(fidelities)) if fidelities else 1.0

    return DistributionReport(
        key_id=keypair.key_id,
        total_states=len(slots),
        average_fidelity=avg_fid,
        min_fidelity=min_fid,
        max_fidelity=max_fid,
        elapsed_seconds=elapsed,
        slots=slots,
        teleportation_samples=samples,
    )
