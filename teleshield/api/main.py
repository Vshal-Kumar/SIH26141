"""
TeleShield FastAPI Backend
Production REST API for QDS keygen, teleportation distribution, signing,
threat verification, attack execution, and audit integrity verification.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import time
import uuid
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from teleshield.backends.exact import ExactBackend
from teleshield.backends.aer import AerBackend
from teleshield.backends.stim import StimBackend
from teleshield.backends.pulser import PulserBackend
from teleshield.hardware.loaders import load_hardware_profile
from teleshield.qds.session import QDSSession
from teleshield.qds.models import QDSSignature
from teleshield.qds.hashing import HashMode
from teleshield.qstat.pipeline import QSTATPipeline
from teleshield.qstat.verdict import QSTATVerdict
from teleshield.attacks.forgery import RandomForgeryAttack
from teleshield.attacks.splice import SpliceForgeryAttack
from teleshield.attacks.impersonation import ImpersonationAttack
from teleshield.attacks.replay import ReplayAttack
from teleshield.attacks.intercept_resend import InterceptResendAttack
from teleshield.attacks.channel import ChannelManipulationAttack
from teleshield.attacks.unauthorized import UnauthorizedVerificationAttack
from teleshield.attacks.threshold_aware import ThresholdAwareAttack
from teleshield.security.calculator import SecurityParameterCalculator
from teleshield.audit.hashchain import HashChain
from teleshield.database.repository import TeleShieldRepository
from teleshield.analysis.metrics import PerformanceTracker

app = FastAPI(
    title="TeleShield API",
    description="Quantum-Inspired Cyber Threat Detection Framework for Teleportation-Based Quantum Digital Signatures",
    version="1.0.0",
)

# In-memory registry and singletons
ACTIVE_SESSIONS: Dict[str, QDSSession] = {}
VERIFICATION_RESULTS: Dict[str, Dict[str, Any]] = {}
AUDIT_CHAIN = HashChain()
REPOSITORY = TeleShieldRepository()
PERF_TRACKER = PerformanceTracker()


# ==========================================
# Pydantic Request / Response Models
# ==========================================

class KeygenRequest(BaseModel):
    n: int = Field(default=64, description="Number of message tag bits")
    L: int = Field(default=222, description="Number of quantum states per bit value")
    backend: str = Field(default="aer", description="Quantum backend: exact, aer, stim, pulser")
    hardware_profile: Optional[str] = Field(default="ion_trap", description="Hardware profile: ideal, ion_trap, rydberg")
    basis_mode: str = Field(default="XZ", description="Measurement basis set: XZ or XYZ")
    seed: Optional[int] = Field(default=42, description="Random generator seed")


class KeygenResponse(BaseModel):
    session_id: str
    key_id: str
    signer_id: str
    verifier_id: str
    n: int
    L: int
    basis_mode: str
    total_states_prepared: int
    epoch: int


class DistributeRequest(BaseModel):
    session_id: str
    bell_visibility: float = Field(default=0.992, description="Entangled pair visibility")
    shots: int = Field(default=1, description="Shots per teleportation operation")
    seed: Optional[int] = Field(default=42)


class DistributeResponse(BaseModel):
    session_id: str
    key_id: str
    total_states_teleported: int
    average_fidelity: float
    min_fidelity: float
    max_fidelity: float
    elapsed_seconds: float


class SignRequest(BaseModel):
    session_id: str
    message: str
    hash_mode: str = Field(default="sha256", description="Message hash binding mode: sha256 or toeplitz")
    nonce: Optional[str] = None


class SignResponse(BaseModel):
    session_id: str
    message_id: str
    signer_id: str
    verifier_id: str
    key_id: str
    epoch: int
    nonce: str
    tag: str
    tag_bits: List[int]
    revealed_states_count: int
    signature_payload: Dict[str, Any]


class VerifyRequest(BaseModel):
    session_id: str
    message: str
    signature: Dict[str, Any]
    shots: int = Field(default=1000)
    seed: Optional[int] = Field(default=42)


class VerifyResponse(BaseModel):
    event_id: str
    verdict: str
    reason: str
    observed_rate: Optional[float]
    threshold: Optional[float]
    p_value: Optional[float]
    confidence_interval: Optional[List[float]]
    audit_hash: str
    qubits_consumed: int
    evidence: Dict[str, Any]


class AttackRunRequest(BaseModel):
    session_id: str
    message: str
    signature: Dict[str, Any]
    attack_type: str = Field(..., description="random_forgery, splice, impersonation, replay, intercept_resend, channel, unauthorized, threshold_aware")
    strength: float = Field(default=0.20, description="Attack intensity or noise rate")
    target_blocks: Optional[List[int]] = None
    seed: Optional[int] = Field(default=42)


class SecurityCalculateRequest(BaseModel):
    n: int = Field(default=64)
    L: Optional[int] = Field(default=222)
    epsilon: float = Field(default=0.01)
    target_false_rejection: float = Field(default=1e-6)
    target_forgery_probability: float = Field(default=1e-6)
    attacker_model: str = Field(default="random_guessing")


# ==========================================
# REST API Endpoints
# ==========================================

@app.get("/")
def root():
    return {
        "framework": "TeleShield",
        "title": "TeleShield: Quantum-Inspired Cyber Threat Detection Framework for Teleportation-Based Quantum Digital Signatures",
        "version": "1.0.0",
        "status": "OPERATIONAL",
    }


@app.post("/api/keygen", response_model=KeygenResponse)
def api_keygen(req: KeygenRequest):
    PERF_TRACKER.start_timer("keygen")

    # Select backend or profile
    if req.hardware_profile:
        prof = load_hardware_profile(req.hardware_profile)
        backend = prof.create_backend(override_seed=req.seed)
    elif req.backend.lower() == "aer":
        backend = AerBackend(seed=req.seed)
    elif req.backend.lower() == "stim":
        backend = StimBackend(seed=req.seed)
    elif req.backend.lower() == "pulser":
        backend = PulserBackend(seed=req.seed)
    else:
        backend = ExactBackend(seed=req.seed)

    session = QDSSession.create(
        n=req.n,
        L=req.L,
        backend=backend,
        basis_mode=req.basis_mode,
        seed=req.seed,
    )
    ACTIVE_SESSIONS[session.session_id] = session

    # Persist metadata to database
    REPOSITORY.save_key(session.keypair.metadata)
    REPOSITORY.save_slots(list(session.slots.values()))

    PERF_TRACKER.stop_timer("keygen")

    return KeygenResponse(
        session_id=session.session_id,
        key_id=session.keypair.key_id,
        signer_id=session.keypair.signer_id,
        verifier_id=session.keypair.verifier_id,
        n=session.keypair.n,
        L=session.keypair.L,
        basis_mode=session.keypair.basis_mode,
        total_states_prepared=len(session.slots),
        epoch=session.keypair.metadata.epoch,
    )


@app.post("/api/distribute", response_model=DistributeResponse)
def api_distribute(req: DistributeRequest):
    session = ACTIVE_SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    PERF_TRACKER.start_timer("distribution")
    report = session.distribution_report
    PERF_TRACKER.stop_timer("distribution")

    if not report:
        raise HTTPException(status_code=500, detail="Distribution report unavailable")

    return DistributeResponse(
        session_id=session.session_id,
        key_id=session.keypair.key_id,
        total_states_teleported=report.total_states,
        average_fidelity=report.average_fidelity,
        min_fidelity=report.min_fidelity,
        max_fidelity=report.max_fidelity,
        elapsed_seconds=report.elapsed_seconds,
    )


@app.post("/api/sign", response_model=SignResponse)
def api_sign(req: SignRequest):
    session = ACTIVE_SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    PERF_TRACKER.start_timer("sign")
    h_mode = HashMode(req.hash_mode.lower())
    sig = session.sign(message=req.message, hash_mode=h_mode, nonce=req.nonce)
    PERF_TRACKER.stop_timer("sign")

    REPOSITORY.save_signature(sig, session_id=session.session_id)

    return SignResponse(
        session_id=session.session_id,
        message_id=sig.message_id,
        signer_id=sig.signer_id,
        verifier_id=sig.verifier_id,
        key_id=sig.key_id,
        epoch=sig.epoch,
        nonce=sig.nonce,
        tag=sig.tag,
        tag_bits=sig.tag_bits,
        revealed_states_count=len(sig.revealed_states),
        signature_payload=sig.to_dict(),
    )


@app.post("/api/verify", response_model=VerifyResponse)
def api_verify(req: VerifyRequest):
    session = ACTIVE_SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Deserialize QDSSignature
    payload = req.signature
    sig = QDSSignature(
        message_id=payload["message_id"],
        signer_id=payload["signer_id"],
        verifier_id=payload["verifier_id"],
        key_id=payload["key_id"],
        epoch=int(payload["epoch"]),
        timestamp=float(payload["timestamp"]),
        nonce=payload["nonce"],
        tag=payload["tag"],
        tag_bits=payload["tag_bits"],
        revealed_states=payload["revealed_states"],
        protocol_version=payload.get("protocol_version", "1.0"),
        hash_mode=payload.get("hash_mode", "sha256"),
    )

    start_v = time.perf_counter()
    PERF_TRACKER.start_timer("verify")
    verdict, stats = session.verify(message=req.message, signature=sig, shots=req.shots, seed=req.seed)
    latency_ms = (time.perf_counter() - start_v) * 1000.0
    PERF_TRACKER.stop_timer("verify")

    qubits_consumed = stats.total_states if stats else 0
    event_id = f"evt_{uuid.uuid4().hex[:12]}"

    # Append to cryptographic SHA-256 hash chain
    audit_ev = AUDIT_CHAIN.log_verification(
        event_id=event_id,
        message_id=sig.message_id,
        signer_id=sig.signer_id,
        verifier_id=sig.verifier_id,
        verdict=verdict.verdict.value,
        attack_type="none",
        global_mismatch=verdict.observed_rate or 0.0,
        threshold=verdict.threshold or 0.0,
        p_value=verdict.p_value or 1.0,
        shots=req.shots,
        qubits_consumed=qubits_consumed,
        latency=latency_ms,
        block_statistics=stats.to_dict() if stats else {},
        basis_statistics=stats.per_basis_rates if stats else {},
    )

    # Persist in SQLite
    REPOSITORY.save_audit_event(audit_ev)
    REPOSITORY.save_verification_event(
        event_id=event_id,
        signature_id=sig.message_id,
        verifier_id=sig.verifier_id,
        verdict=verdict.verdict.value,
        attack_type="none",
        global_mismatch=verdict.observed_rate or 0.0,
        threshold=verdict.threshold or 0.0,
        p_value=verdict.p_value or 1.0,
        shots=req.shots,
        qubits_consumed=qubits_consumed,
        latency=latency_ms,
        audit_hash=audit_ev.event_hash,
    )

    response_data = {
        "event_id": event_id,
        "verdict": verdict.verdict.value,
        "reason": verdict.reason,
        "observed_rate": verdict.observed_rate,
        "threshold": verdict.threshold,
        "p_value": verdict.p_value,
        "confidence_interval": verdict.confidence_interval,
        "audit_hash": audit_ev.event_hash,
        "qubits_consumed": qubits_consumed,
        "evidence": verdict.evidence,
    }
    VERIFICATION_RESULTS[event_id] = response_data
    return VerifyResponse(**response_data)


@app.post("/api/attack/run", response_model=VerifyResponse)
def api_attack_run(req: AttackRunRequest):
    session = ACTIVE_SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    payload = req.signature
    sig = QDSSignature(
        message_id=payload["message_id"],
        signer_id=payload["signer_id"],
        verifier_id=payload["verifier_id"],
        key_id=payload["key_id"],
        epoch=int(payload["epoch"]),
        timestamp=float(payload["timestamp"]),
        nonce=payload["nonce"],
        tag=payload["tag"],
        tag_bits=payload["tag_bits"],
        revealed_states=payload["revealed_states"],
        protocol_version=payload.get("protocol_version", "1.0"),
        hash_mode=payload.get("hash_mode", "sha256"),
    )

    a_type = req.attack_type.lower()
    attack_res = None

    if a_type == "random_forgery":
        attack = RandomForgeryAttack(strength=req.strength, target_blocks=req.target_blocks, seed=req.seed)
        attack_res = attack.execute(signature=sig)
        target_sig = attack_res.manipulated_signature
    elif a_type == "splice":
        attack = SpliceForgeryAttack(target_blocks=req.target_blocks, strength=req.strength, seed=req.seed)
        attack_res = attack.execute(donor_signature=sig, target_message=req.message)
        target_sig = attack_res.manipulated_signature
    elif a_type == "impersonation":
        attack = ImpersonationAttack(seed=req.seed)
        attack_res = attack.execute(
            message=req.message,
            key_id=session.keypair.key_id,
            verifier_id=session.verifier.verifier_id,
            n_bits=session.keypair.n,
            L=session.keypair.L,
        )
        target_sig = attack_res.manipulated_signature
    elif a_type == "replay":
        attack = ReplayAttack()
        attack_res = attack.execute(valid_signature=sig)
        target_sig = attack_res.manipulated_signature
    elif a_type == "intercept_resend":
        attack = InterceptResendAttack(strength=req.strength, target_blocks=req.target_blocks, seed=req.seed)
        attack_res = attack.execute(slots=session.slots)
        session.slots = attack_res.manipulated_slots
        target_sig = sig
    elif a_type == "channel":
        attack = ChannelManipulationAttack(channel_type="depolarizing", strength=req.strength, target_blocks=req.target_blocks, seed=req.seed)
        attack_res = attack.execute(slots=session.slots)
        session.slots = attack_res.manipulated_slots
        target_sig = sig
    elif a_type == "unauthorized":
        attack = UnauthorizedVerificationAttack(unauthorized_verifier_id="attacker_charlie")
        attack_res = attack.execute(valid_signature=sig)
        # Create an unauthorized verifier instance
        unauth_verifier = session.verifier.__class__(verifier_id="attacker_charlie", backend=session.backend, pipeline=session.pipeline)
        verdict, stats = unauth_verifier.verify(message=req.message, signature=sig, slots={})
        target_sig = sig
    elif a_type == "threshold_aware":
        attack = ThresholdAwareAttack(sub_threshold_rate=req.strength, seed=req.seed)
        attack_res = attack.execute(slots=session.slots)
        session.slots = attack_res.manipulated_slots
        target_sig = sig
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported attack type: {req.attack_type}")

    start_v = time.perf_counter()
    if a_type != "unauthorized":
        verdict, stats = session.verify(message=req.message, signature=target_sig, seed=req.seed)
    latency_ms = (time.perf_counter() - start_v) * 1000.0

    qubits_consumed = stats.total_states if stats else 0
    event_id = f"evt_{uuid.uuid4().hex[:12]}"

    # Audit logging for attack injection
    audit_ev = AUDIT_CHAIN.log_verification(
        event_id=event_id,
        message_id=target_sig.message_id,
        signer_id=target_sig.signer_id,
        verifier_id=target_sig.verifier_id,
        verdict=verdict.verdict.value,
        attack_type=req.attack_type,
        global_mismatch=verdict.observed_rate or 0.0,
        threshold=verdict.threshold or 0.0,
        p_value=verdict.p_value or 1.0,
        shots=1000,
        qubits_consumed=qubits_consumed,
        latency=latency_ms,
        block_statistics=stats.to_dict() if stats else {},
        basis_statistics=stats.per_basis_rates if stats else {},
    )
    REPOSITORY.save_audit_event(audit_ev)

    response_data = {
        "event_id": event_id,
        "verdict": verdict.verdict.value,
        "reason": verdict.reason,
        "observed_rate": verdict.observed_rate,
        "threshold": verdict.threshold,
        "p_value": verdict.p_value,
        "confidence_interval": verdict.confidence_interval,
        "audit_hash": audit_ev.event_hash,
        "qubits_consumed": qubits_consumed,
        "evidence": verdict.evidence,
    }
    VERIFICATION_RESULTS[event_id] = response_data
    return VerifyResponse(**response_data)


@app.post("/api/security/calculate")
def api_security_calculate(req: SecurityCalculateRequest):
    calculator = SecurityParameterCalculator()
    rec = calculator.calculate(
        n=req.n,
        L=req.L,
        epsilon=req.epsilon,
        target_false_rejection=req.target_false_rejection,
        target_forgery_probability=req.target_forgery_probability,
        attacker_model=req.attacker_model,
    )
    return rec.to_dict()


@app.get("/api/session/{session_id}")
def api_get_session(session_id: str):
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@app.get("/api/verification/{event_id}")
def api_get_verification(event_id: str):
    res = VERIFICATION_RESULTS.get(event_id)
    if not res:
        raise HTTPException(status_code=404, detail="Verification event not found")
    return res


@app.get("/api/metrics")
def api_get_metrics():
    summary = REPOSITORY.get_system_summary()
    perf = PERF_TRACKER.create_report().to_dict()
    return {
        "system_summary": summary,
        "performance": perf,
        "active_sessions_count": len(ACTIVE_SESSIONS),
    }


@app.get("/api/audit")
def api_get_audit():
    events = AUDIT_CHAIN.events
    return [e.to_dict() for e in events]


@app.get("/api/audit/verify")
def api_audit_verify():
    result = AUDIT_CHAIN.verify_integrity()
    return result.to_dict()
