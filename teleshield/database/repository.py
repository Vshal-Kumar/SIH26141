"""
TeleShield Database Repository
Provides SQLite persistence operations for metadata, sessions, keys,
verification telemetry, and hash-chained audit events.
"""

from __future__ import annotations
import json
import time
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker, Session

from teleshield.database.models import (
    Base, DBKey, DBKeySlot, DBSession, DBSignature,
    DBVerificationEvent, DBAttack, DBAuditEvent
)
from teleshield.audit.hashchain import AuditEvent
from teleshield.qds.models import QDSKey, KeySlot, QDSSignature


class TeleShieldRepository:
    """Repository managing local SQLite storage for metadata and audit logging."""

    def __init__(self, db_url: str = "sqlite:///teleshield.db") -> None:
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def save_key(self, key: QDSKey) -> None:
        with self.SessionLocal() as session:
            db_k = DBKey(
                key_id=key.key_id,
                signer_id=key.signer_id,
                verifier_id=key.verifier_id,
                n=key.n,
                L=key.L,
                basis_mode=key.basis_mode,
                epoch=key.epoch,
                created_at=key.created_at,
            )
            session.merge(db_k)
            session.commit()

    def save_slots(self, slots: List[KeySlot]) -> None:
        with self.SessionLocal() as session:
            for s in slots:
                db_s = DBKeySlot(
                    slot_id=s.slot_id,
                    key_id=s.key_id,
                    verifier_id=s.verifier_id,
                    tag_index=s.tag_index,
                    bit_value=s.bit_value,
                    state_index=s.state_index,
                    basis=s.basis.value,
                    eigenvalue=s.eigenvalue.value,
                    epoch=s.epoch,
                    status=s.status.value,
                    created_at=s.created_at,
                    consumed_at=s.consumed_at,
                )
                session.merge(db_s)
            session.commit()

    def update_slot_status(self, slot_id: str, status: str, consumed_at: Optional[float] = None) -> None:
        with self.SessionLocal() as session:
            db_s = session.get(DBKeySlot, slot_id)
            if db_s:
                db_s.status = status
                if consumed_at is not None:
                    db_s.consumed_at = consumed_at
                session.commit()

    def save_signature(self, sig: QDSSignature, session_id: Optional[str] = None) -> None:
        with self.SessionLocal() as session:
            db_sig = DBSignature(
                signature_id=sig.message_id,
                session_id=session_id,
                message_id=sig.message_id,
                signer_id=sig.signer_id,
                verifier_id=sig.verifier_id,
                key_id=sig.key_id,
                epoch=sig.epoch,
                timestamp=sig.timestamp,
                nonce=sig.nonce,
                tag=sig.tag,
                tag_bits_json=json.dumps(sig.tag_bits),
                revealed_states_json=json.dumps(sig.revealed_states),
                protocol_version=sig.protocol_version,
                hash_mode=sig.hash_mode,
            )
            session.merge(db_sig)
            session.commit()

    def save_verification_event(
        self,
        event_id: str,
        signature_id: str,
        verifier_id: str,
        verdict: str,
        attack_type: str = "none",
        global_mismatch: float = 0.0,
        threshold: float = 0.0,
        p_value: float = 1.0,
        shots: int = 1,
        qubits_consumed: int = 0,
        latency: float = 0.0,
        config_hash: str = "",
        audit_hash: str = "",
    ) -> None:
        with self.SessionLocal() as session:
            db_ve = DBVerificationEvent(
                event_id=event_id,
                signature_id=signature_id,
                verifier_id=verifier_id,
                verdict=verdict,
                attack_type=attack_type,
                global_mismatch=global_mismatch,
                threshold=threshold,
                p_value=p_value,
                shots=shots,
                qubits_consumed=qubits_consumed,
                latency=latency,
                config_hash=config_hash,
                audit_hash=audit_hash,
                timestamp=time.time(),
            )
            session.merge(db_ve)
            session.commit()

    def save_audit_event(self, event: AuditEvent) -> None:
        with self.SessionLocal() as session:
            db_ae = DBAuditEvent(
                event_id=event.event_id,
                timestamp=event.timestamp,
                message_id=event.message_id,
                signer_id=event.signer_id,
                verifier_id=event.verifier_id,
                verdict=event.verdict,
                attack_type=event.attack_type,
                global_mismatch=event.global_mismatch,
                threshold=event.threshold,
                p_value=event.p_value,
                shots=event.shots,
                qubits_consumed=event.qubits_consumed,
                latency=event.latency,
                config_hash=event.config_hash,
                previous_hash=event.previous_hash,
                event_hash=event.event_hash,
                block_statistics_json=json.dumps(event.block_statistics),
                basis_statistics_json=json.dumps(event.basis_statistics),
            )
            session.merge(db_ae)
            session.commit()

    def get_audit_events(self) -> List[AuditEvent]:
        with self.SessionLocal() as session:
            stmt = select(DBAuditEvent).order_by(DBAuditEvent.timestamp.asc())
            rows = session.scalars(stmt).all()
            events = []
            for r in rows:
                ev = AuditEvent(
                    event_id=r.event_id,
                    timestamp=r.timestamp,
                    message_id=r.message_id,
                    signer_id=r.signer_id,
                    verifier_id=r.verifier_id,
                    verdict=r.verdict,
                    attack_type=r.attack_type,
                    global_mismatch=r.global_mismatch,
                    block_statistics=json.loads(r.block_statistics_json or "{}"),
                    basis_statistics=json.loads(r.basis_statistics_json or "{}"),
                    threshold=r.threshold,
                    p_value=r.p_value,
                    shots=r.shots,
                    qubits_consumed=r.qubits_consumed,
                    latency=r.latency,
                    config_hash=r.config_hash,
                    previous_hash=r.previous_hash,
                    event_hash=r.event_hash,
                )
                events.append(ev)
            return events

    def get_system_summary(self) -> Dict[str, Any]:
        with self.SessionLocal() as session:
            total_events = session.query(DBVerificationEvent).count()
            accepted = session.query(DBVerificationEvent).filter(DBVerificationEvent.verdict == "ACCEPT").count()
            replays = session.query(DBVerificationEvent).filter(DBVerificationEvent.verdict == "REPLAY").count()
            forgeries = session.query(DBVerificationEvent).filter(DBVerificationEvent.verdict == "FORGERY_SUSPECTED").count()
            impersonations = session.query(DBVerificationEvent).filter(DBVerificationEvent.verdict == "IMPERSONATION_SUSPECTED").count()
            channel_anomalies = session.query(DBVerificationEvent).filter(DBVerificationEvent.verdict == "CHANNEL_ANOMALY").count()
            unauthorized = session.query(DBVerificationEvent).filter(DBVerificationEvent.verdict == "UNAUTHORIZED_VERIFICATION").count()

            return {
                "total_verifications": total_events,
                "accepted": accepted,
                "rejected": total_events - accepted,
                "replays_detected": replays,
                "forgeries_detected": forgeries,
                "impersonations_detected": impersonations,
                "channel_anomalies_detected": channel_anomalies,
                "unauthorized_attempts_detected": unauthorized,
            }
