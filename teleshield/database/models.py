"""
Database Models Module
SQLAlchemy ORM models for classical metadata, audit logs, sessions, and key slot records.
Explicitly: Quantum states are NEVER persisted to the database.
"""

from __future__ import annotations
import time
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    user_id = Column(String(64), primary_key=True)
    username = Column(String(64), nullable=False)
    role = Column(String(32), default="participant")
    created_at = Column(Float, default=time.time)


class DBKey(Base):
    __tablename__ = "keys"
    key_id = Column(String(64), primary_key=True)
    signer_id = Column(String(64), nullable=False)
    verifier_id = Column(String(64), nullable=False)
    n = Column(Integer, nullable=False)
    L = Column(Integer, nullable=False)
    basis_mode = Column(String(16), default="XZ")
    epoch = Column(Integer, default=1)
    created_at = Column(Float, default=time.time)


class DBKeySlot(Base):
    __tablename__ = "key_slots"
    slot_id = Column(String(64), primary_key=True)
    key_id = Column(String(64), ForeignKey("keys.key_id"), nullable=False)
    verifier_id = Column(String(64), nullable=False)
    tag_index = Column(Integer, nullable=False)
    bit_value = Column(Integer, nullable=False)
    state_index = Column(Integer, nullable=False)
    basis = Column(String(8), nullable=False)
    eigenvalue = Column(Integer, nullable=False)
    state_reference = Column(String(64), default="")
    epoch = Column(Integer, default=1)
    status = Column(String(32), default="AVAILABLE")
    created_at = Column(Float, default=time.time)
    consumed_at = Column(Float, nullable=True)


class DBSession(Base):
    __tablename__ = "sessions"
    session_id = Column(String(64), primary_key=True)
    key_id = Column(String(64), nullable=False)
    backend_name = Column(String(32), default="aer")
    hardware_profile = Column(String(32), default="ion_trap")
    status = Column(String(32), default="ACTIVE")
    created_at = Column(Float, default=time.time)


class DBSignature(Base):
    __tablename__ = "signatures"
    signature_id = Column(String(64), primary_key=True)
    session_id = Column(String(64), nullable=True)
    message_id = Column(String(64), nullable=False)
    signer_id = Column(String(64), nullable=False)
    verifier_id = Column(String(64), nullable=False)
    key_id = Column(String(64), nullable=False)
    epoch = Column(Integer, default=1)
    timestamp = Column(Float, default=time.time)
    nonce = Column(String(64), nullable=False)
    tag = Column(String(256), nullable=False)
    tag_bits_json = Column(Text, nullable=False)
    revealed_states_json = Column(Text, nullable=False)
    protocol_version = Column(String(16), default="1.0")
    hash_mode = Column(String(32), default="sha256")


class DBVerificationEvent(Base):
    __tablename__ = "verification_events"
    event_id = Column(String(64), primary_key=True)
    signature_id = Column(String(64), nullable=False)
    verifier_id = Column(String(64), nullable=False)
    verdict = Column(String(32), nullable=False)
    attack_type = Column(String(64), default="none")
    global_mismatch = Column(Float, default=0.0)
    threshold = Column(Float, default=0.0)
    p_value = Column(Float, default=1.0)
    shots = Column(Integer, default=1)
    qubits_consumed = Column(Integer, default=0)
    latency = Column(Float, default=0.0)
    config_hash = Column(String(64), default="")
    audit_hash = Column(String(64), default="")
    timestamp = Column(Float, default=time.time)


class DBAttack(Base):
    __tablename__ = "attacks"
    attack_id = Column(String(64), primary_key=True)
    attack_type = Column(String(64), nullable=False)
    strength = Column(Float, default=1.0)
    target_blocks_json = Column(Text, default="[]")
    description = Column(Text, default="")
    timestamp = Column(Float, default=time.time)


class DBAuditEvent(Base):
    __tablename__ = "audit_events"
    event_id = Column(String(64), primary_key=True)
    timestamp = Column(Float, nullable=False)
    message_id = Column(String(64), nullable=False)
    signer_id = Column(String(64), nullable=False)
    verifier_id = Column(String(64), nullable=False)
    verdict = Column(String(32), nullable=False)
    attack_type = Column(String(64), default="none")
    global_mismatch = Column(Float, default=0.0)
    threshold = Column(Float, default=0.0)
    p_value = Column(Float, default=1.0)
    shots = Column(Integer, default=1)
    qubits_consumed = Column(Integer, default=0)
    latency = Column(Float, default=0.0)
    config_hash = Column(String(64), default="")
    previous_hash = Column(String(64), nullable=False)
    event_hash = Column(String(64), nullable=False)
    block_statistics_json = Column(Text, default="{}")
    basis_statistics_json = Column(Text, default="{}")
