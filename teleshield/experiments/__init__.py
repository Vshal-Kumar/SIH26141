"""
TeleShield Experiment Framework
Automated, reproducible experimental suite comprising 14 research experiments (E01 - E14).
Supports parameter sweeps, Monte Carlo simulation, statistical validation, and artifact export.
"""

from teleshield.experiments.runner import ExperimentRunner, ExperimentResult
from teleshield.experiments.e01_teleportation import run_e01_teleportation
from teleshield.experiments.e02_honest_qds import run_e02_honest_qds
from teleshield.experiments.e03_forgery import run_e03_forgery
from teleshield.experiments.e04_splice import run_e04_splice
from teleshield.experiments.e05_replay import run_e05_replay
from teleshield.experiments.e06_impersonation import run_e06_impersonation
from teleshield.experiments.e07_channel import run_e07_channel
from teleshield.experiments.e08_fingerprint import run_e08_fingerprint
from teleshield.experiments.e09_chsh import run_e09_chsh
from teleshield.experiments.e10_security import run_e10_security
from teleshield.experiments.e11_sprt import run_e11_sprt
from teleshield.experiments.e12_cusum import run_e12_cusum
from teleshield.experiments.e13_backend_parity import run_e13_backend_parity
from teleshield.experiments.e14_hardware_profiles import run_e14_hardware_profiles

__all__ = [
    "ExperimentRunner",
    "ExperimentResult",
    "run_e01_teleportation",
    "run_e02_honest_qds",
    "run_e03_forgery",
    "run_e04_splice",
    "run_e05_replay",
    "run_e06_impersonation",
    "run_e07_channel",
    "run_e08_fingerprint",
    "run_e09_chsh",
    "run_e10_security",
    "run_e11_sprt",
    "run_e12_cusum",
    "run_e13_backend_parity",
    "run_e14_hardware_profiles",
]
