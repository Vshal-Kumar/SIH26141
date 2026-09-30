"""
Qiskit Aer Quantum Backend
Primary quantum backend for ion-trap-aligned gate-model simulation.
Constructs Qiskit QuantumCircuit instances, configures AerSimulator with
noise models, and executes realistic projective measurements and teleportation.
"""

from __future__ import annotations
from typing import Optional, Union, Dict, Any, Tuple
import numpy as np

from teleshield.backends.base import QuantumBackend
from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.pauli import apply_pauli, get_correction_operator
from teleshield.quantum.bell import BellPair, BellState, create_bell_pair
from teleshield.quantum.teleportation import TeleportationResult, teleport_state
from teleshield.quantum.measurement import MeasurementResult, measure_state
from teleshield.quantum.noise import NoiseModelConfig, apply_quantum_noise

# Check Qiskit / Aer availability
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


class AerBackend(QuantumBackend):
    """
    Qiskit Aer simulator backend configured for gate-model circuits
    and ion-trap hardware profiles.
    """

    def __init__(
        self,
        noise_config: Optional[NoiseModelConfig] = None,
        shots: int = 10000,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(name="aer", noise_config=noise_config, shots=shots, seed=seed)
        self._simulator = None
        self._qiskit_noise_model = None
        if QISKIT_AVAILABLE:
            self._init_qiskit_simulator()

    def _init_qiskit_simulator(self) -> None:
        noise_model = None
        if self.noise_config:
            noise_model = NoiseModel()
            # 1-qubit gate error
            p1 = self.noise_config.one_qubit_gate_error or self.noise_config.depolarizing_rate or self.noise_config.probability
            if p1 > 0:
                err_1q = depolarizing_error(p1, 1)
                noise_model.add_all_qubit_quantum_error(err_1q, ['u', 'u1', 'u2', 'u3', 'h', 'x', 'y', 'z', 's', 'sdg', 'rx', 'ry', 'rz'])

            # 2-qubit gate error
            p2 = self.noise_config.two_qubit_gate_error or (p1 * 2.0)
            if p2 > 0:
                err_2q = depolarizing_error(min(1.0, p2), 2)
                noise_model.add_all_qubit_quantum_error(err_2q, ['cx', 'cz'])

            # Readout error
            ro = self.noise_config.readout_error
            if ro > 0:
                ro_err = ReadoutError([[1.0 - ro, ro], [ro, 1.0 - ro]])
                noise_model.add_all_qubit_readout_error(ro_err)

            self._qiskit_noise_model = noise_model

        if noise_model is not None and len(noise_model.to_dict().get("errors", [])) > 0:
            self._simulator = AerSimulator(noise_model=noise_model)
        else:
            self._simulator = AerSimulator()

    def prepare_state(
        self,
        basis: Union[StateBasis, str],
        eigenvalue: Union[Eigenvalue, int, str],
    ) -> QuantumState:
        # Generate canonical state
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

        # Execute teleportation using statevector/density operator simulation
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

        # If Qiskit is available and circuit execution requested, we can run via AerSimulator
        if QISKIT_AVAILABLE and self._simulator is not None and s > 1:
            try:
                qc = QuantumCircuit(1, 1)
                # Prepare state from statevector if pure
                if state.vector is not None:
                    qc.initialize(state.vector, 0)
                elif state.is_pure:
                    w, v = np.linalg.eigh(state.density_matrix)
                    vec = v[:, -1]
                    qc.initialize(vec, 0)
                else:
                    raise ValueError("Mixed state circuit simulation fallback")
                # Basis rotation to Z
                if b == StateBasis.X:
                    qc.h(0)
                elif b == StateBasis.Y:
                    qc.sdg(0)
                    qc.h(0)
                qc.measure(0, 0)

                job = self._simulator.run(qc, shots=s, seed_simulator=sd)
                counts = job.result().get_counts()
                c0 = counts.get("0", 0)
                c1 = counts.get("1", 0)
                obs_bit = 0 if c0 >= c1 else 1
                obs_ev = Eigenvalue.PLUS if obs_bit == 0 else Eigenvalue.MINUS

                if ev == Eigenvalue.PLUS:
                    matches, mismatches = c0, c1
                else:
                    matches, mismatches = c1, c0

                mismatch_rate = float(mismatches) / float(max(1, s))
                p0 = float(c0) / float(max(1, s))
                p1 = float(c1) / float(max(1, s))

                return MeasurementResult(
                    basis=b,
                    expected_eigenvalue=ev,
                    observed_eigenvalue=obs_ev,
                    raw_result=obs_bit,
                    shots=s,
                    matches=matches,
                    mismatches=mismatches,
                    mismatch_rate=mismatch_rate,
                    p_plus=p0,
                    p_minus=p1,
                )
            except Exception:
                # Fall back gracefully to high-precision numerical projective measurement
                pass

        return measure_state(
            state=state,
            basis=b,
            expected_eigenvalue=ev,
            shots=s,
            readout_error=self.noise_config.readout_error,
            seed=sd,
        )
