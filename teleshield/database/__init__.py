"""
TeleShield Database Layer
Local metadata and audit persistence repository using SQLite.
Quantum states remain exclusively in quantum memory/session layers.
"""

from teleshield.database.models import (
    Base, DBUser, DBKey, DBKeySlot, DBSession,
    DBSignature, DBVerificationEvent, DBAttack, DBAuditEvent
)
from teleshield.database.repository import TeleShieldRepository

__all__ = [
    "Base",
    "DBUser",
    "DBKey",
    "DBKeySlot",
    "DBSession",
    "DBSignature",
    "DBVerificationEvent",
    "DBAttack",
    "DBAuditEvent",
    "TeleShieldRepository",
]
