"""
QDS Verifier Module
Verifies signatures by measuring Bob's stored quantum states in the basis
declared by the signer, compiling measurement statistics, and querying Q-STAT.
Enforces the no-cloning physical state consumption rule.
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Optional, Any, TYPE_CHECKING
import numpy as np

from teleshield.backends.base import QuantumBackend
from teleshield.backends.exact import ExactBackend
from teleshield.qds.models import QDSSignature, KeySlot, SlotStatus
from teleshield.quantum.states import StateBasis, Eigenvalue
from teleshield.quantum.measurement import MeasurementResult
from teleshield.qstat.statistics import compute_verification_statistics, VerificationStatistics
from teleshield.qstat.verdict import QSTATVerdict, VerdictType

if TYPE_CHECKING:
    from teleshield.qstat.pipeline import QSTATPipeline


class QDSVerifier:
    """Represents a verifying entity (Bob) possessing quantum memory slots."""

    def __init__(
        self,
        verifier_id: str = "verifier_bob",
        backend: Optional[QuantumBackend] = None,
        pipeline: Optional["QSTATPipeline"] = None,
    ) -> None:
        self.verifier_id = verifier_id
        self.backend = backend or ExactBackend()
        if pipeline is None:
            from teleshield.qstat.pipeline import QSTATPipeline
            self.pipeline = QSTATPipeline()
        else:
            self.pipeline = pipeline

    def verify(
        self,
        message: str,
        signature: QDSSignature,
        slots: Dict[Tuple[int, int, int], KeySlot],
        shots: int = 1,
        seed: Optional[int] = None,
    ) -> Tuple[QSTATVerdict, Optional[VerificationStatistics]]:
        """
        Executes physical projective measurements on verifier's KeySlots,
        computes statistical evidence, and passes to Q-STAT pipeline.
        Quantum states are consumed and cannot be measured again.
        """
        rng = np.random.default_rng(seed)
        n = len(signature.tag_bits)
        total_revealed = len(signature.revealed_states)
        L = max(1, total_revealed // max(1, n))

        # Check authorization / slot availability before measurement
        target_slots: List[KeySlot] = []
        for j, b_j in enumerate(signature.tag_bits):
            for k in range(L):
                slot_key = (j, b_j, k)
                if slot_key in slots:
                    target_slots.append(slots[slot_key])

        # If zero slots available for this signature
        if len(target_slots) == 0:
            verdict = self.pipeline.evaluate(
                message=message,
                signature=signature,
                verifier_id=self.verifier_id,
                stats=None,
                slots=[],
            )
            return verdict, None

        # Execute projective measurements
        measurements: List[MeasurementResult] = []
        state_idx_map: Dict[Tuple[int, int], Dict[str, Any]] = {}

        for st in signature.revealed_states:
            j = int(st["tag_index"])
            k = int(st["state_index"])
            state_idx_map[(j, k)] = st

        for j in range(n):
            b_j = signature.tag_bits[j]
            for k in range(L):
                slot = slots.get((j, b_j, k))
                revealed_info = state_idx_map.get((j, k))

                if slot is None or revealed_info is None or slot.quantum_state is None:
                    # Slot missing, consumed, or empty -> generate synthetic mismatch
                    m = MeasurementResult(
                        basis=StateBasis.Z,
                        expected_eigenvalue=Eigenvalue.PLUS,
                        observed_eigenvalue=Eigenvalue.MINUS,
                        raw_result=1,
                        shots=shots,
                        matches=0,
                        mismatches=shots,
                        mismatch_rate=1.0,
                        p_plus=0.0,
                        p_minus=1.0,
                    )
                    measurements.append(m)
                    continue

                declared_basis = StateBasis(str(revealed_info["basis"]).upper())
                declared_ev = Eigenvalue.from_str(revealed_info["eigenvalue"])

                m_seed = int(rng.integers(0, 2**31 - 1)) if seed is not None else None
                m_res = self.backend.measure(
                    state=slot.quantum_state,
                    basis=declared_basis,
                    expected_eigenvalue=declared_ev,
                    shots=shots,
                    seed=m_seed,
                )
                measurements.append(m_res)

        # Aggregate statistics across blocks and bases
        stats = compute_verification_statistics(
            measurements=measurements,
            tag_bits=signature.tag_bits,
            L=L,
        )

        # Run Q-STAT pipeline evaluation and consume measured slots
        verdict = self.pipeline.evaluate(
            message=message,
            signature=signature,
            verifier_id=self.verifier_id,
            stats=stats,
            slots=target_slots,
            consume_slots_on_complete=True,
        )

        return verdict, stats
