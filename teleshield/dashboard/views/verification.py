"""
Dashboard View 3: Signature Verification & Q-STAT Evidence Analysis
Executes physical measurements, compiles per-block and per-basis evidence,
and renders explainable verdicts with confidence intervals and p-values.
Professional styling with zero emojis.
"""

import streamlit as st
import uuid
from teleshield.analysis.plots import plot_per_block_heatmap, plot_per_basis_radar
from teleshield.qds.session import QDSSession
from teleshield.database.repository import TeleShieldRepository
from teleshield.audit.hashchain import HashChain


def render_verification_page():
    st.markdown("## Quantum Signature Verification & Forensic Triage")
    st.caption("Perform projective quantum measurements on verifier KeySlots and evaluate multi-dimensional Q-STAT evidence.")

    session: QDSSession = st.session_state.get("current_session")
    sig = st.session_state.get("current_signature")
    msg = st.session_state.get("current_message", "")

    if not session or not sig:
        st.warning("[NOTICE] No active QDS signature found. Please navigate to the QDS Protocol Simulation page to generate a signature first.")
        return

    st.markdown(f"**Target Message:** *\"{msg}\"*")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Signer ID:** `{sig.signer_id}`")
        st.markdown(f"**Verifier ID:** `{sig.verifier_id}`")
    with col2:
        st.markdown(f"**Key ID:** `{sig.key_id}`")
        st.markdown(f"**Nonce:** `{sig.nonce}`")
    with col3:
        st.markdown(f"**Tag (Hex):** `{sig.tag[:16]}...`")
        st.markdown(f"**Available Quantum Slots:** {session.available_slots_count}")

    st.markdown("---")
    shots = st.slider("Measurement Shots per State", min_value=100, max_value=10000, value=2000, step=500)

    btn_v1, _ = st.columns([1, 4])
    with btn_v1:
        execute_v_btn = st.button("Execute Verification Measurements", type="primary", width="stretch")

    if execute_v_btn:
        with st.spinner("Executing projective measurements and evaluating Q-STAT pipeline..."):
            verdict, stats = session.verify(message=msg, signature=sig, shots=shots, seed=42)
            st.session_state["latest_verdict"] = verdict
            st.session_state["latest_stats"] = stats

            # Persist verification in SQLite and Audit Log
            event_id = f"evt_{uuid.uuid4().hex[:12]}"
            repo = TeleShieldRepository()
            db_events = repo.get_audit_events()
            chain = HashChain()
            chain.events = db_events

            audit_ev = chain.log_verification(
                event_id=event_id,
                message_id=sig.message_id,
                signer_id=sig.signer_id,
                verifier_id=sig.verifier_id,
                verdict=verdict.verdict.value,
                attack_type="none",
                global_mismatch=verdict.observed_rate or 0.0,
                threshold=verdict.threshold or 0.0,
                p_value=verdict.p_value or 1.0,
                shots=shots,
                qubits_consumed=stats.total_states if stats else 0,
                latency=12.4,
                block_statistics=stats.to_dict() if stats else {},
                basis_statistics=stats.per_basis_rates if stats else {},
            )
            repo.save_audit_event(audit_ev)
            repo.save_verification_event(
                event_id=event_id,
                signature_id=sig.message_id,
                verifier_id=sig.verifier_id,
                verdict=verdict.verdict.value,
                attack_type="none",
                global_mismatch=verdict.observed_rate or 0.0,
                threshold=verdict.threshold or 0.0,
                p_value=verdict.p_value or 1.0,
                shots=shots,
                qubits_consumed=stats.total_states if stats else 0,
                latency=12.4,
                audit_hash=audit_ev.event_hash,
            )

    verdict = st.session_state.get("latest_verdict")
    stats = st.session_state.get("latest_stats")

    if verdict and stats:
        st.markdown("---")
        # Final Verdict Display
        if verdict.is_accepted:
            st.success(f"### Verdict: {verdict.verdict.value} [ACCEPTED]")
        else:
            st.error(f"### Verdict: {verdict.verdict.value} [REJECTED]")

        st.markdown(f"**Explanation:** {verdict.reason}")

        v_col1, v_col2, v_col3, v_col4 = st.columns(4)
        with v_col1:
            st.metric("Global Mismatch Rate", f"{stats.global_mismatch_rate:.4f}")
        with v_col2:
            st.metric("Acceptance Threshold s_a", f"{verdict.threshold:.4f}" if verdict.threshold else "N/A")
        with v_col3:
            st.metric("Statistical p-Value", f"{verdict.p_value:.6e}" if verdict.p_value is not None else "N/A")
        with v_col4:
            ci = verdict.confidence_interval
            ci_str = f"[{ci[0]:.3f}, {ci[1]:.3f}]" if ci else "N/A"
            st.metric("95% Confidence Interval", ci_str)

        st.markdown("---")
        # Visualization Tabs
        tab_blocks, tab_basis, tab_evidence = st.tabs(["Per-Block Heatmap", "Per-Basis Radar", "Forensic Evidence"])

        with tab_blocks:
            st.markdown("#### Per-Block Quantum Mismatch Rate vs Threshold")
            st.caption("Each block corresponds to a tag position bit. Blocks exceeding threshold trigger rejection/forgery alarms.")
            block_rates = [b.mismatch_rate for b in stats.block_statistics]
            fig_blocks = plot_per_block_heatmap(block_rates, verdict.threshold or 0.045)
            st.plotly_chart(fig_blocks, width="stretch")

        with tab_basis:
            st.markdown("#### Quantum Basis Asymmetry (X, Y, Z)")
            st.caption("Asymmetric error dispersion diagnoses specific physical channel noise (dephasing vs bit-flip vs depolarizing).")
            fig_basis = plot_per_basis_radar(stats.per_basis_rates)
            st.plotly_chart(fig_basis, width="stretch")

        with tab_evidence:
            st.markdown("#### Forensic Evidence Payload")
            st.json({
                "verdict": verdict.to_dict(),
                "total_states_measured": stats.total_states,
                "total_matches": stats.total_matches,
                "total_mismatches": stats.total_mismatches,
                "per_basis_counts": stats.per_basis_counts,
            })
