"""
TeleShield Attack Engine Layer
Simulates comprehensive cyber and quantum threats against teleportation-based QDS:
random forgery, splice forgery, impersonation, replay, intercept-resend,
channel manipulation, unauthorized verification, and threshold-aware drift attacks.
"""

from teleshield.attacks.base import BaseAttack, AttackExecutionResult
from teleshield.attacks.forgery import RandomForgeryAttack
from teleshield.attacks.splice import SpliceForgeryAttack
from teleshield.attacks.impersonation import ImpersonationAttack
from teleshield.attacks.replay import ReplayAttack
from teleshield.attacks.intercept_resend import InterceptResendAttack
from teleshield.attacks.channel import ChannelManipulationAttack
from teleshield.attacks.unauthorized import UnauthorizedVerificationAttack
from teleshield.attacks.threshold_aware import ThresholdAwareAttack

__all__ = [
    "BaseAttack",
    "AttackExecutionResult",
    "RandomForgeryAttack",
    "SpliceForgeryAttack",
    "ImpersonationAttack",
    "ReplayAttack",
    "InterceptResendAttack",
    "ChannelManipulationAttack",
    "UnauthorizedVerificationAttack",
    "ThresholdAwareAttack",
]
