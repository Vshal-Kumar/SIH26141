"""
TeleShield Hardware Layer
Hardware-aware simulation profiles aligning gate and physical parameters with
literature-derived benchmarks (Ion-Trap and Neutral-Atom Rydberg).
"""

from teleshield.hardware.profiles import HardwareProfile
from teleshield.hardware.loaders import (
    load_hardware_profile, list_available_profiles
)

__all__ = [
    "HardwareProfile",
    "load_hardware_profile",
    "list_available_profiles",
]
