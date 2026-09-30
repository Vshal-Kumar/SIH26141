"""
Exact NumPy Quantum Backend
High-precision linear algebra and density matrix simulator implementing the QuantumBackend interface.
Deterministic, fast, and mathematically exact with unified noise channel modeling.
"""

from __future__ import annotations
from typing import Optional, Union, Dict, Any

from teleshield.backends.base import QuantumBackend
from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.pauli import apply_pauli
from teleshield.quantum.bell import BellPair, BellState, create_bell_pair
from teleshield.quantum.teleportation import TeleportationResult, teleport_state
from teleshield.quantum.measurement import MeasurementResult, measure_state
from teleshield.quantum.noise import NoiseModelConfig, apply_quantum_noise


class ExactBackend(QuantumBackend):
    """
    Exact mathematical backend using NumPy matrix algebra and density operators.
    Provides standard reference simulation with exact fidelity and trace preservation.
    """

    def __init__(
        self,
        noise_config: Optional[NoiseModelConfig] = None,
        shots: int = 10000,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(name="exact", noise_config=noise_config, shots=shots, seed=seed)

    def prepare_state(
        self,
        basis: Union[StateBasis, str],
        eigenvalue: Union[Eigenvalue, int, str],
    ) -> QuantumState:
        state = QuantumState.from_basis_and_eigenvalue(basis, eigenvalue)
        if self.noise_config.probability > 0 or self.noise_config.one_qubit_gate_error > 0:
            state = apply_quantum_noise(state, self.noise_config)
        return state

    def create_bell_pair(
        self,
        bell_type: BellState = BellState.PHI_PLUS,
        visibility: float = 1.0,
    ) -> BellPair:
        vis = visibility
        if self.noise_config.probability > 0:
            vis = vis * (1.0 - self.noise_config.probability)
        return create_bell_pair(bell_type=bell_type, visibility=vis)

    def teleport(
        self,
        input_state: QuantumState,
        bell_pair: Optional[BellPair] = None,
        shots: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> TeleportationResult:
        s = shots if shots is not None else self.shots
        sd = seed if seed is not None else self.seed
        bp = bell_pair or self.create_bell_pair()
        result = teleport_state(input_state=input_state, bell_pair=bp, shots=s, seed=sd)
        # Apply gate/channel noise to teleported state if configured
        if self.noise_config.probability > 0 or self.noise_config.depolarizing_rate > 0:
            noisy_out = apply_quantum_noise(result.output_state, self.noise_config)
            result.output_state = noisy_out
            result.fidelity = input_state.fidelity(noisy_out)
        return result

    def apply_pauli(
        self,
        state: QuantumState,
        pauli_name: str,
    ) -> QuantumState:
        res = apply_pauli(state, pauli_name)
        if self.noise_config.one_qubit_gate_error > 0:
            res = apply_quantum_noise(res, self.noise_config)
        return res

    def measure(
        self,
        state: QuantumState,
        basis: Union[StateBasis, str],
        expected_eigenvalue: Optional[Union[Eigenvalue, int, str]] = None,
        shots: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> MeasurementResult:
        s = shots if shots is not None else self.shots
        sd = seed if seed is not None else self.seed
        ro_err = self.noise_config.readout_error
        return measure_state(
            state=state,
            basis=basis,
            expected_eigenvalue=expected_eigenvalue,
            shots=s,
            readout_error=ro_err,
            seed=sd,
        )
