"""
QDS Session Management Module
Orchestrates active QDS sessions, linking keypairs, distributed verifier slots,
signing actions, verification executions, and threat detection pipelines.
"""

from __future__ import annotations
from typing import Dict, Tuple, Optional, Any, List, TYPE_CHECKING
import uuid

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.keygen import QDSKeyPair, generate_qds_keypair
from teleshield.qds.distribution import distribute_public_key, DistributionReport
from teleshield.qds.signer import QDSSigner
from teleshield.qds.verifier import QDSVerifier
from teleshield.qds.models import KeySlot, QDSSignature, SlotStatus
from teleshield.qds.hashing import HashMode
from teleshield.qstat.verdict import QSTATVerdict
from teleshield.qstat.statistics import VerificationStatistics

if TYPE_CHECKING:
    from teleshield.qstat.pipeline import QSTATPipeline


class QDSSession:
    """
    Manages end-to-end lifecycle of an active QDS session:
    distribution -> signing -> physical measurement -> threat analysis.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        keypair: Optional[QDSKeyPair] = None,
        backend: Optional[QuantumBackend] = None,
        slots: Optional[Dict[Tuple[int, int, int], KeySlot]] = None,
        signer: Optional[QDSSigner] = None,
        verifier: Optional[QDSVerifier] = None,
        pipeline: Optional["QSTATPipeline"] = None,
    ) -> None:
        self.session_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"
        self.backend = backend or ExactBackend()
        if pipeline is None:
            from teleshield.qstat.pipeline import QSTATPipeline
            self.pipeline = QSTATPipeline()
        else:
            self.pipeline = pipeline
        self.keypair = keypair
        self.slots = slots or {}
        self.signer = signer or (QDSSigner(keypair) if keypair else None)
        self.verifier = verifier or QDSVerifier(
            verifier_id=keypair.verifier_id if keypair else "verifier_bob",
            backend=self.backend,
            pipeline=self.pipeline,
        )
        self.distribution_report: Optional[DistributionReport] = None
        self.signature_history: List[QDSSignature] = []
        self.verification_history: List[Tuple[QSTATVerdict, Optional[VerificationStatistics]]] = []

    @classmethod
    def create(
        cls,
        n: int = 64,
        L: int = 222,
        backend: Optional[QuantumBackend] = None,
        signer_id: str = "signer_alice",
        verifier_id: str = "verifier_bob",
        basis_mode: str = "XZ",
        bell_visibility: float = 1.0,
        shots: int = 1,
        seed: Optional[int] = None,
    ) -> "QDSSession":
        """Factory method: generates keypair and teleports public quantum key states."""
        q_backend = backend or ExactBackend()
        kp = generate_qds_keypair(
            n=n,
            L=L,
            backend=q_backend,
            signer_id=signer_id,
            verifier_id=verifier_id,
            basis_mode=basis_mode,
            seed=seed,
        )

        dist_report = distribute_public_key(
            keypair=kp,
            backend=q_backend,
            bell_visibility=bell_visibility,
            shots_per_teleport=shots,
            seed=seed,
        )

        from teleshield.qstat.pipeline import QSTATPipeline
        pipeline = QSTATPipeline()
        signer = QDSSigner(kp)
        verifier = QDSVerifier(verifier_id=verifier_id, backend=q_backend, pipeline=pipeline)

        session = cls(
            keypair=kp,
            backend=q_backend,
            slots=dist_report.slots,
            signer=signer,
            verifier=verifier,
            pipeline=pipeline,
        )
        session.distribution_report = dist_report
        return session

    def sign(
        self,
        message: str,
        hash_mode: HashMode = HashMode.SHA256,
        nonce: Optional[str] = None,
    ) -> QDSSignature:
        """Sign message using active session's private key."""
        if self.signer is None:
            raise RuntimeError("Signer not configured for this session")
        sig = self.signer.sign(message=message, hash_mode=hash_mode, nonce=nonce)
        self.signature_history.append(sig)
        return sig

    def verify(
        self,
        message: str,
        signature: QDSSignature,
        shots: int = 1,
        seed: Optional[int] = None,
    ) -> Tuple[QSTATVerdict, Optional[VerificationStatistics]]:
        """Verify signature by measuring Bob's stored quantum states."""
        if self.verifier is None:
            raise RuntimeError("Verifier not configured for this session")
        verdict, stats = self.verifier.verify(
            message=message,
            signature=signature,
            slots=self.slots,
            shots=shots,
            seed=seed,
        )
        self.verification_history.append((verdict, stats))
        return verdict, stats

    @property
    def available_slots_count(self) -> int:
        return sum(1 for s in self.slots.values() if s.is_available)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "key_id": self.keypair.key_id if self.keypair else None,
            "signer_id": self.keypair.signer_id if self.keypair else None,
            "verifier_id": self.verifier.verifier_id if self.verifier else None,
            "backend": self.backend.name,
            "total_slots": len(self.slots),
            "available_slots": self.available_slots_count,
            "signatures_generated": len(self.signature_history),
            "verifications_performed": len(self.verification_history),
        }
