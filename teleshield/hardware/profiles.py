"""
Hardware Profile Definition
Encapsulates hardware parameters, experimental provenance, and backend instantiation.
Explicitly labels all parameter values as: assumed, literature-derived, or experimentally configured.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from teleshield.quantum.noise import NoiseModelConfig, NoiseType
from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.backends.aer import AerBackend
from teleshield.backends.stim import StimBackend
from teleshield.backends.pulser import PulserBackend


@dataclass
class HardwareProfile:
    """
    Hardware-aware simulation profile with explicit parameter provenance.
    Strictly marked as literature-derived / assumed simulation baselines;
    does not represent proprietary commercial vendor hardware.
    """
    name: str
    display_name: str
    profile_type: str
    backend_name: str
    description: str
    reference_model: str
    parameters: Dict[str, Dict[str, Any]]
    shots: int = 10000
    seed: Optional[int] = 42

    def get_param_value(self, param_name: str, default: float = 0.0) -> float:
        param = self.parameters.get(param_name, {})
        if isinstance(param, dict):
            return float(param.get("value", default))
        return float(param) if param else default

    def to_noise_config(self) -> NoiseModelConfig:
        """Translates hardware profile parameters into unified NoiseModelConfig."""
        p1 = self.get_param_value("one_qubit_gate_error", 0.0)
        p2 = self.get_param_value("two_qubit_gate_error", 0.0)
        ro = self.get_param_value("readout_error", 0.0)
        deph = self.get_param_value("dephasing_rate", 0.0)
        depol = self.get_param_value("depolarizing_rate", 0.0)
        loss = self.get_param_value("loss_rate", 0.0)

        # Composite noise configuration
        return NoiseModelConfig(
            noise_type=NoiseType.COMPOSITE if (p1 > 0 or p2 > 0 or deph > 0 or depol > 0) else NoiseType.NONE,
            probability=depol or p1,
            one_qubit_gate_error=p1,
            two_qubit_gate_error=p2,
            readout_error=ro,
            dephasing_rate=deph,
            depolarizing_rate=depol,
            loss_rate=loss,
        )

    def create_backend(
        self,
        override_shots: Optional[int] = None,
        override_seed: Optional[int] = None,
    ) -> QuantumBackend:
        """Instantiates matching QuantumBackend configured with profile noise."""
        shots = override_shots if override_shots is not None else self.shots
        seed = override_seed if override_seed is not None else self.seed
        noise_cfg = self.to_noise_config()

        b_name = self.backend_name.lower()
        if b_name == "aer":
            return AerBackend(noise_config=noise_cfg, shots=shots, seed=seed)
        elif b_name == "stim":
            return StimBackend(noise_config=noise_cfg, shots=shots, seed=seed)
        elif b_name == "pulser":
            return PulserBackend(noise_config=noise_cfg, shots=shots, seed=seed)
        else:
            return ExactBackend(noise_config=noise_cfg, shots=shots, seed=seed)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "profile_type": self.profile_type,
            "backend": self.backend_name,
            "description": self.description,
            "reference_model": self.reference_model,
            "parameters": self.parameters,
            "shots": self.shots,
            "seed": self.seed,
        }
