"""
TeleShield Quantum Backend Abstraction Layer
Provides unified quantum execution interface across Exact NumPy, Qiskit Aer,
Stim, and Pulser/Rydberg backends.
"""

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.backends.aer import AerBackend
from teleshield.backends.stim import StimBackend
from teleshield.backends.pulser import PulserBackend

__all__ = [
    "QuantumBackend",
    "ExactBackend",
    "AerBackend",
    "StimBackend",
    "PulserBackend",
]
