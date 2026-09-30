"""
Forensic Report Generator Module
Compiles verification sessions and experiment runs into structured Markdown,
JSON, and tabular formats for researcher dissemination.
"""

from __future__ import annotations
import json
import time
from typing import Dict, Any, List, Optional

from teleshield.qstat.verdict import QSTATVerdict
from teleshield.qstat.statistics import VerificationStatistics
from teleshield.audit.hashchain import AuditEvent


def generate_verification_markdown_report(
    verdict: QSTATVerdict,
    stats: Optional[VerificationStatistics] = None,
    audit_event: Optional[AuditEvent] = None,
    message: str = "",
) -> str:
    """Generates structured Markdown report of a verification outcome."""
    lines = [
        "# TeleShield Verification Analysis Report",
        f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        "",
        "## Executive Summary",
        f"- **Verdict:** `{verdict.verdict.value}`",
        f"- **Rationale:** {verdict.reason}",
        f"- **Observed Error Rate:** {f'{verdict.observed_rate:.4f}' if verdict.observed_rate is not None else 'N/A'}",
        f"- **Decision Threshold:** {f'{verdict.threshold:.4f}' if verdict.threshold is not None else 'N/A'}",
        f"- **p-Value:** {f'{verdict.p_value:.6e}' if verdict.p_value is not None else 'N/A'}",
        "",
    ]

    if audit_event:
        lines.extend([
            "## Cryptographic Audit Provenance",
            f"- **Event ID:** `{audit_event.event_id}`",
            f"- **Signer:** `{audit_event.signer_id}`",
            f"- **Verifier:** `{audit_event.verifier_id}`",
            f"- **Event Hash:** `{audit_event.event_hash}`",
            f"- **Previous Chain Hash:** `{audit_event.previous_hash}`",
            "",
        ])

    if stats:
        lines.extend([
            "## Quantum Measurement Statistics",
            f"- **Total Quantum States:** {stats.total_states}",
            f"- **Total Matches:** {stats.total_matches}",
            f"- **Total Mismatches:** {stats.total_mismatches}",
            f"- **Global Mismatch Rate:** {stats.global_mismatch_rate:.4f}",
            f"- **Per-Basis Error (X):** {stats.per_basis_rates.get('X', 0.0):.4f}",
            f"- **Per-Basis Error (Y):** {stats.per_basis_rates.get('Y', 0.0):.4f}",
            f"- **Per-Basis Error (Z):** {stats.per_basis_rates.get('Z', 0.0):.4f}",
            "",
            "### Per-Block Dispersion",
            "| Block Index | Bit Value | Matches | Mismatches | Error Rate |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])
        for b in stats.block_statistics[:16]:  # Show first 16 blocks in summary
            lines.append(f"| B{b.block_index} | {b.bit_value} | {b.matches} | {b.mismatches} | {b.mismatch_rate:.4f} |")
        if len(stats.block_statistics) > 16:
            lines.append(f"| ... | ... | ... | ... | ({len(stats.block_statistics) - 16} additional blocks) |")
        lines.append("")

    return "\n".join(lines)


def export_experiment_results_json(experiment_id: str, results: Dict[str, Any]) -> str:
    """Serializes experiment output dictionary to clean formatted JSON."""
    payload = {
        "experiment_id": experiment_id,
        "timestamp": time.time(),
        "results": results,
    }
    return json.dumps(payload, indent=2)
