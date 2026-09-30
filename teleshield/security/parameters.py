"""
Security Parameter Profiles Module
Predefined standard operating configurations for different assurance requirements.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class SecurityProfileName(str, Enum):
    DEMO = "demo"
    STANDARD = "standard"
    HIGH_ASSURANCE = "high_assurance"
    MAXIMUM = "maximum"


@dataclass
class SecurityProfile:
    name: str
    n_tag_bits: int
    L_states_per_bit: int
    target_false_rejection: float
    target_forgery_prob: float
    expected_noise: float
    shots_default: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "n_tag_bits": self.n_tag_bits,
            "L_states_per_bit": self.L_states_per_bit,
            "target_false_rejection": self.target_false_rejection,
            "target_forgery_prob": self.target_forgery_prob,
            "expected_noise": self.expected_noise,
            "shots_default": self.shots_default,
            "description": self.description,
        }


SECURITY_PROFILES: Dict[str, SecurityProfile] = {
    "demo": SecurityProfile(
        name="demo",
        n_tag_bits=16,
        L_states_per_bit=64,
        target_false_rejection=1e-4,
        target_forgery_prob=1e-4,
        expected_noise=0.01,
        shots_default=1000,
        description="Fast simulation profile for demonstrations and interactive exploration.",
    ),
    "standard": SecurityProfile(
        name="standard",
        n_tag_bits=64,
        L_states_per_bit=222,
        target_false_rejection=1e-6,
        target_forgery_prob=1e-6,
        expected_noise=0.01,
        shots_default=10000,
        description="Recommended baseline research configuration offering high security bounds.",
    ),
    "high_assurance": SecurityProfile(
        name="high_assurance",
        n_tag_bits=128,
        L_states_per_bit=450,
        target_false_rejection=1e-9,
        target_forgery_prob=1e-9,
        expected_noise=0.01,
        shots_default=10000,
        description="High-assurance cryptographic profile for sensitive enterprise communications.",
    ),
    "maximum": SecurityProfile(
        name="maximum",
        n_tag_bits=256,
        L_states_per_bit=800,
        target_false_rejection=1e-12,
        target_forgery_prob=1e-12,
        expected_noise=0.005,
        shots_default=20000,
        description="Maximum-security theoretical model for mission-critical national infrastructure.",
    ),
}


def get_security_profile(name: str = "standard") -> SecurityProfile:
    """Retrieve predefined security profile by name."""
    p_name = name.strip().lower()
    if p_name not in SECURITY_PROFILES:
        return SECURITY_PROFILES["standard"]
    return SECURITY_PROFILES[p_name]
