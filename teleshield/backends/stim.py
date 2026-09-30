"""
Stim Quantum Backend
Fast Clifford and stabilizer circuit simulator implementing the QuantumBackend interface.
Excels at high-speed Pauli frame simulation, X/Z basis telemetry, and stabilizer verification.
"""

from __future__ import annotations
from typing import Optional, Union, Dict, Any
import numpy as np

from teleshield.backends.base import QuantumBackend
from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.pauli import apply_pauli
from teleshield.quantum.bell import BellPair, BellState, create_bell_pair
from teleshield.quantum.teleportation import TeleportationResult, teleport_state
from teleshield.quantum.measurement import MeasurementResult, measure_state
from teleshield.quantum.noise import NoiseModelConfig, apply_quantum_noise

try:
    import stim
    STIM_AVAILABLE = True
except ImportError:
    STIM_AVAILABLE = False


class StimBackend(QuantumBackend):
    """
    Stabilizer and Clifford tableau backend using Stim.
    Specialized for high-throughput Pauli state generation, teleportation,
    and Pauli channel noise analysis.
    """

    def __init__(
        self,
        noise_config: Optional[NoiseModelConfig] = None,
        shots: int = 10000,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(name="stim", noise_config=noise_config, shots=shots, seed=seed)

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

        res = teleport_state(input_state=input_state, bell_pair=bp, shots=s, seed=sd)
        if self.noise_config.probability > 0 or self.noise_config.depolarizing_rate > 0:
            noisy_out = apply_quantum_noise(res.output_state, self.noise_config)
            res.output_state = noisy_out
            res.fidelity = input_state.fidelity(noisy_out)
        return res

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
        b = StateBasis(str(basis).upper())
        ev = Eigenvalue.from_str(expected_eigenvalue) if expected_eigenvalue is not None else (state.eigenvalue or Eigenvalue.PLUS)

        # If Stim is available and pure stabilizer state in Z or X
        if STIM_AVAILABLE and s > 1 and state.is_pure and b in (StateBasis.Z, StateBasis.X):
            try:
                circuit = stim.Circuit()
                # Prepare state
                if state.basis == StateBasis.Z:
                    if state.eigenvalue == Eigenvalue.MINUS:
                        circuit.append("X", [0])
                elif state.basis == StateBasis.X:
                    if state.eigenvalue == Eigenvalue.PLUS:
                        circuit.append("H", [0])
                    else:
                        circuit.append("X", [0])
                        circuit.append("H", [0])

                # Apply noise
                p_depol = self.noise_config.depolarizing_rate or self.noise_config.probability
                if p_depol > 0:
                    circuit.append("DEPOLARIZE1", [0], p_depol)

                # Basis rotation
                if b == StateBasis.X:
                    circuit.append("H", [0])

                circuit.append("M", [0])

                sampler = circuit.compile_sampler(seed=sd)
                samples = sampler.sample(shots=s)
                c1 = int(np.sum(samples))
                c0 = s - c1

                obs_bit = 0 if c0 >= c1 else 1
                obs_ev = Eigenvalue.PLUS if obs_bit == 0 else Eigenvalue.MINUS

                if ev == Eigenvalue.PLUS:
                    matches, mismatches = c0, c1
                else:
                    matches, mismatches = c1, c0

                mismatch_rate = float(mismatches) / float(max(1, s))
                return MeasurementResult(
                    basis=b,
                    expected_eigenvalue=ev,
                    observed_eigenvalue=obs_ev,
                    raw_result=obs_bit,
                    shots=s,
                    matches=matches,
                    mismatches=mismatches,
                    mismatch_rate=mismatch_rate,
                    p_plus=float(c0) / float(s),
                    p_minus=float(c1) / float(s),
                )
            except Exception:
                pass

        return measure_state(
            state=state,
            basis=b,
            expected_eigenvalue=ev,
            shots=s,
            readout_error=self.noise_config.readout_error,
            seed=sd,
        )
