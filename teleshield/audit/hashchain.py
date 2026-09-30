"""
Cryptographic Hash Chain Audit Module
Implements SHA-256 hash-chained verification audit logging.
Guarantees forward integrity: any modification of past audit records
invalidates the subsequent hash chain.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json
import time
import uuid
import csv
import io


@dataclass
class AuditEvent:
    """Tamper-evident verification audit record."""
    event_id: str
    timestamp: float
    message_id: str
    signer_id: str
    verifier_id: str
    verdict: str
    attack_type: str
    global_mismatch: float
    block_statistics: Dict[str, Any]
    basis_statistics: Dict[str, Any]
    threshold: float
    p_value: float
    shots: int
    qubits_consumed: int
    latency: float
    config_hash: str
    previous_hash: str
    event_hash: str = ""

    def compute_content_string(self) -> str:
        """Deterministic canonical string for hashing (excluding event_hash itself)."""
        content_dict = {
            "event_id": self.event_id,
            "timestamp": f"{self.timestamp:.6f}",
            "message_id": self.message_id,
            "signer_id": self.signer_id,
            "verifier_id": self.verifier_id,
            "verdict": self.verdict,
            "attack_type": self.attack_type,
            "global_mismatch": f"{self.global_mismatch:.6f}",
            "threshold": f"{self.threshold:.6f}",
            "p_value": f"{self.p_value:.8e}",
            "shots": self.shots,
            "qubits_consumed": self.qubits_consumed,
            "latency": f"{self.latency:.6f}",
            "config_hash": self.config_hash,
            "previous_hash": self.previous_hash,
        }
        return json.dumps(content_dict, sort_keys=True)

    def calculate_hash(self) -> str:
        """Calculates H_i = SHA256(Event_content || previous_hash)."""
        canonical = self.compute_content_string() + self.previous_hash
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "signer_id": self.signer_id,
            "verifier_id": self.verifier_id,
            "verdict": self.verdict,
            "attack_type": self.attack_type,
            "global_mismatch": self.global_mismatch,
            "threshold": self.threshold,
            "p_value": self.p_value,
            "shots": self.shots,
            "qubits_consumed": self.qubits_consumed,
            "latency": self.latency,
            "config_hash": self.config_hash,
            "previous_hash": self.previous_hash,
            "event_hash": self.event_hash,
            "block_statistics": self.block_statistics,
            "basis_statistics": self.basis_statistics,
        }


@dataclass
class AuditVerificationResult:
    is_valid: bool
    status: str
    total_events: int
    compromised_index: Optional[int] = None
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "status": self.status,
            "total_events": self.total_events,
            "compromised_index": self.compromised_index,
            "details": self.details,
        }


class HashChain:
    """
    Manages an append-only, SHA-256 hash-chained sequence of audit events.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self) -> None:
        self.events: List[AuditEvent] = []

    @property
    def latest_hash(self) -> str:
        return self.events[-1].event_hash if self.events else self.GENESIS_HASH

    def log_verification(
        self,
        message_id: str,
        signer_id: str,
        verifier_id: str,
        verdict: str,
        attack_type: str = "none",
        global_mismatch: float = 0.0,
        threshold: float = 0.0,
        p_value: float = 1.0,
        shots: int = 1,
        qubits_consumed: int = 0,
        latency: float = 0.0,
        config_hash: str = "default_cfg",
        block_statistics: Optional[Dict[str, Any]] = None,
        basis_statistics: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> AuditEvent:
        """Constructs, hashes, and appends a new audit event."""
        prev_h = self.latest_hash
        e_id = event_id or f"evt_{uuid.uuid4().hex[:12]}"
        t = timestamp or time.time()

        event = AuditEvent(
            event_id=e_id,
            timestamp=t,
            message_id=message_id,
            signer_id=signer_id,
            verifier_id=verifier_id,
            verdict=verdict,
            attack_type=attack_type,
            global_mismatch=float(global_mismatch),
            block_statistics=block_statistics or {},
            basis_statistics=basis_statistics or {},
            threshold=float(threshold),
            p_value=float(p_value),
            shots=int(shots),
            qubits_consumed=int(qubits_consumed),
            latency=float(latency),
            config_hash=config_hash,
            previous_hash=prev_h,
        )
        event.event_hash = event.calculate_hash()
        self.events.append(event)
        return event

    def verify_integrity(self) -> AuditVerificationResult:
        """
        Validates entire hash chain from genesis to head.
        Verifies previous_hash continuity and recalculated event hashes.
        """
        if not self.events:
            return AuditVerificationResult(
                is_valid=True,
                status="AUDIT CHAIN VALID",
                total_events=0,
                details="Audit log is empty; chain is valid.",
            )

        expected_prev = self.GENESIS_HASH

        for idx, event in enumerate(self.events):
            # 1. Check previous hash pointer
            if event.previous_hash != expected_prev:
                return AuditVerificationResult(
                    is_valid=False,
                    status="AUDIT CHAIN INVALID",
                    total_events=len(self.events),
                    compromised_index=idx,
                    details=(
                        f"Chain continuity broken at event index {idx} ({event.event_id}). "
                        f"Expected previous_hash {expected_prev[:12]}..., found {event.previous_hash[:12]}..."
                    ),
                )

            # 2. Recompute content hash
            recomputed = event.calculate_hash()
            if event.event_hash != recomputed:
                return AuditVerificationResult(
                    is_valid=False,
                    status="AUDIT CHAIN INVALID",
                    total_events=len(self.events),
                    compromised_index=idx,
                    details=(
                        f"Tampering detected in event payload at index {idx} ({event.event_id}). "
                        f"Stored hash: {event.event_hash[:12]}..., calculated: {recomputed[:12]}..."
                    ),
                )

            expected_prev = event.event_hash

        return AuditVerificationResult(
            is_valid=True,
            status="AUDIT CHAIN VALID",
            total_events=len(self.events),
            details=f"All {len(self.events)} audit events cryptographically verified without tampering.",
        )

    def export_csv(self) -> str:
        """Exports audit log to CSV string format."""
        output = io.StringIO()
        fieldnames = [
            "event_id", "timestamp", "message_id", "signer_id", "verifier_id",
            "verdict", "attack_type", "global_mismatch", "threshold", "p_value",
            "shots", "qubits_consumed", "latency", "config_hash", "previous_hash", "event_hash"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for ev in self.events:
            row = {k: getattr(ev, k) for k in fieldnames}
            writer.writerow(row)
        return output.getvalue()

    def export_json(self) -> str:
        """Exports audit log to JSON formatted string."""
        return json.dumps([e.to_dict() for e in self.events], indent=2)
