"""
TeleShield Security Analysis Layer
Mathematical bounds, analytical proofs, and security parameter calculations
for teleportation-based Quantum Digital Signatures.
"""

from teleshield.security.bounds import (
    calculate_honest_false_rejection_bound,
    calculate_forgery_acceptance_bound,
    calculate_analytical_threshold,
)
from teleshield.security.calculator import (
    SecurityParameterCalculator, SecurityRecommendation
)
from teleshield.security.parameters import (
    SecurityProfile, get_security_profile
)

__all__ = [
    "calculate_honest_false_rejection_bound",
    "calculate_forgery_acceptance_bound",
    "calculate_analytical_threshold",
    "SecurityParameterCalculator",
    "SecurityRecommendation",
    "SecurityProfile",
    "get_security_profile",
]
