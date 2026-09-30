"""
Quantum Backend Base Interface
Abstract base class defining the standard interface for quantum hardware and simulation backends.
Enforces strict decoupling between QDS protocol logic and concrete quantum simulators.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List

from teleshield.quantum.states import QuantumState, StateBasis, Eigenvalue
from teleshield.quantum.bell import BellPair, BellState
from teleshield.quantum.teleportation import TeleportationResult
from teleshield.quantum.measurement import MeasurementResult
from teleshield.quantum.noise import NoiseModelConfig


class QuantumBackend(ABC):
    """
    Abstract interface for quantum computation backends.
    All QDS operations and experiment scripts interact with quantum resources
    exclusively via this interface.
    """

    def __init__(
        self,
        name: str,
        noise_config: Optional[NoiseModelConfig] = None,
        shots: int = 10000,
        seed: Optional[int] = None,
    ) -> None:
        self.name = name
        self.noise_config = noise_config or NoiseModelConfig()
        self.shots = shots
        self.seed = seed

    @abstractmethod
    def prepare_state(
        self,
        basis: Union[StateBasis, str],
        eigenvalue: Union[Eigenvalue, int, str],
    ) -> QuantumState:
        """Prepare single-qubit Pauli eigenstate in specified basis."""
        pass

    @abstractmethod
    def create_bell_pair(
        self,
        bell_type: BellState = BellState.PHI_PLUS,
        visibility: float = 1.0,
    ) -> BellPair:
        """Generate two-qubit Bell pair with optional visibility degradation."""
        pass

    @abstractmethod
    def teleport(
        self,
        input_state: QuantumState,
        bell_pair: Optional[BellPair] = None,
        shots: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> TeleportationResult:
        """Execute quantum teleportation of input_state using bell_pair."""
        pass

    @abstractmethod
    def apply_pauli(
        self,
        state: QuantumState,
        pauli_name: str,
    ) -> QuantumState:
        """Apply Pauli operator (I, X, Y, Z) to state."""
        pass

    @abstractmethod
    def measure(
        self,
        state: QuantumState,
        basis: Union[StateBasis, str],
        expected_eigenvalue: Optional[Union[Eigenvalue, int, str]] = None,
        shots: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> MeasurementResult:
        """Perform projective measurement in target basis and return statistical evidence."""
        pass

    def run_circuit(self, circuit: Any, **kwargs) -> Any:
        """Execute backend-specific low-level quantum circuit."""
        raise NotImplementedError(f"run_circuit not directly supported by {self.name}")

    def get_info(self) -> Dict[str, Any]:
        """Return metadata describing backend, noise configuration, and shot defaults."""
        return {
            "name": self.name,
            "shots": self.shots,
            "seed": self.seed,
            "noise": self.noise_config.to_dict(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', shots={self.shots})"
