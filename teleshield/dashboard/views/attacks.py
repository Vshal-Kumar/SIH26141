"""
Dashboard View 4: Attack Lab
Interactive quantum cyber threat proving ground.
Inject adversarial manipulations and evaluate deterministic detection by Q-STAT.
Professional styling with zero emojis.
"""

import streamlit as st
import time
import uuid
from teleshield.qds.session import QDSSession
from teleshield.attacks.forgery import RandomForgeryAttack
from teleshield.attacks.splice import SpliceForgeryAttack
from teleshield.attacks.impersonation import ImpersonationAttack
from teleshield.attacks.replay import ReplayAttack
from teleshield.attacks.intercept_resend import InterceptResendAttack
from teleshield.attacks.channel import ChannelManipulationAttack
from teleshield.attacks.unauthorized import UnauthorizedVerificationAttack
from teleshield.attacks.threshold_aware import ThresholdAwareAttack
from teleshield.analysis.plots import plot_per_block_heatmap
from teleshield.database.repository import TeleShieldRepository
from teleshield.audit.hashchain import HashChain


def render_attacks_page():
    st.markdown("## Quantum Cyber Attack Proving Ground")
    st.caption("Inject quantum-level and protocol-level adversarial threats to evaluate Q-STAT deterministic resilience.")

    session: QDSSession = st.session_state.get("current_session")
    sig = st.session_state.get("current_signature")
    msg = st.session_state.get("current_message", "Transaction transfer message")

    if not session or not sig:
        st.warning("[NOTICE] Please generate a baseline QDS session and signature on the QDS Protocol Simulation page first.")
        return

    # Attack configuration panel
    st.markdown("### Adversary Threat Configuration")
    atk_col1, atk_col2, atk_col3 = st.columns(3)

    with atk_col1:
        attack_type = st.selectbox(
            "Attack Vector",
            [
                "Random Forgery",
                "Splice Forgery",
                "Impersonation",
                "Replay Attack",
                "Intercept-Resend",
                "Channel Manipulation",
                "Unauthorized Verification",
                "Threshold-Aware Drift",
            ],
            index=0,
        )
    with atk_col2:
        strength = st.slider("Attack Strength / Disturbance Intensity", min_value=0.01, max_value=1.0, value=0.50, step=0.05)
    with atk_col3:
        seed = st.number_input("Adversary Seed", min_value=1, max_value=999999, value=42)

    # Contextual guidance for attack
    if attack_type == "Random Forgery":
        st.info("**Random Forgery:** Replaces signer's revealed quantum state claims with random guesses. Expected error ~50% on attacked blocks.")
    elif attack_type == "Splice Forgery":
        st.info("**Splice Forgery:** Splices authentic revealed states from a donor message onto a target message. Demonstrates per-block failure localization.")
    elif attack_type == "Impersonation":
        st.info("**Impersonation:** An attacker lacking the private key fabricates a complete signature envelope. Produces widespread ~50% mismatch.")
    elif attack_type == "Replay Attack":
        st.info("**Replay Attack:** Re-submits an identical signature and nonce. Flagged deterministically by the freshness and slot consumption tracker.")
    elif attack_type == "Intercept-Resend":
        st.info("**Intercept-Resend:** Measures quantum states in transit and repropels them. Introduces ~25% error in XZ basis mode.")
    elif attack_type == "Channel Manipulation":
        st.info("**Channel Manipulation:** Injects physical depolarizing/dephasing noise directly into quantum channels.")
    elif attack_type == "Unauthorized Verification":
        st.info("**Unauthorized Verification:** An unauthenticated node without assigned key slots attempts verification.")
    elif attack_type == "Threshold-Aware Drift":
        st.info("**Threshold-Aware Drift:** Keeps disturbance strictly below the single-session threshold s_a to attempt evasion of single-session tests.")

    st.markdown("---")
    btn1, _ = st.columns([1, 4])
    with btn1:
        run_attack_btn = st.button("INJECT & VERIFY ATTACK", type="primary", width="stretch")

    if run_attack_btn:
        with st.spinner(f"Executing {attack_type} against quantum states and evaluating Q-STAT..."):
            # Recreate clean session copy for independent attack simulation
            test_session = QDSSession.create(
                n=session.keypair.n,
                L=session.keypair.L,
                backend=session.backend,
                basis_mode=session.keypair.basis_mode,
                seed=int(seed),
            )
            clean_sig = test_session.sign(msg)

            start_t = time.perf_counter()

            if attack_type == "Random Forgery":
                atk = RandomForgeryAttack(strength=strength, seed=int(seed))
                res = atk.execute(signature=clean_sig)
                verdict, stats = test_session.verify(msg, res.manipulated_signature, seed=int(seed))

            elif attack_type == "Splice Forgery":
                atk = SpliceForgeryAttack(target_blocks=[2, 5, 8], strength=strength, seed=int(seed))
                res = atk.execute(donor_signature=clean_sig, target_message=msg + " [MODIFIED AMOUNT $10,000,000]")
                verdict, stats = test_session.verify(msg + " [MODIFIED AMOUNT $10,000,000]", res.manipulated_signature, seed=int(seed))

            elif attack_type == "Impersonation":
                atk = ImpersonationAttack(seed=int(seed))
                res = atk.execute(
                    message=msg,
                    key_id=test_session.keypair.key_id,
                    verifier_id=test_session.verifier.verifier_id,
                    n_bits=test_session.keypair.n,
                    L=test_session.keypair.L,
                )
                verdict, stats = test_session.verify(msg, res.manipulated_signature, seed=int(seed))

            elif attack_type == "Replay Attack":
                # First legitimate pass consumes slots
                test_session.verify(msg, clean_sig, seed=int(seed))
                # Second replay pass
                atk = ReplayAttack()
                res = atk.execute(valid_signature=clean_sig)
                verdict, stats = test_session.verify(msg, res.manipulated_signature, seed=int(seed))

            elif attack_type == "Intercept-Resend":
                atk = InterceptResendAttack(strength=strength, seed=int(seed))
                res = atk.execute(slots=test_session.slots)
                test_session.slots = res.manipulated_slots
                verdict, stats = test_session.verify(msg, clean_sig, seed=int(seed))

            elif attack_type == "Channel Manipulation":
                atk = ChannelManipulationAttack(channel_type="depolarizing", strength=strength, seed=int(seed))
                res = atk.execute(slots=test_session.slots)
                test_session.slots = res.manipulated_slots
                verdict, stats = test_session.verify(msg, clean_sig, seed=int(seed))

            elif attack_type == "Unauthorized Verification":
                atk = UnauthorizedVerificationAttack(unauthorized_verifier_id="attacker_charlie")
                res = atk.execute(valid_signature=clean_sig)
                unauth_v = test_session.verifier.__class__(verifier_id="attacker_charlie", backend=test_session.backend, pipeline=test_session.pipeline)
                verdict, stats = unauth_v.verify(msg, clean_sig, slots={})

            elif attack_type == "Threshold-Aware Drift":
                atk = ThresholdAwareAttack(sub_threshold_rate=min(0.025, strength * 0.04), seed=int(seed))
                res = atk.execute(slots=test_session.slots)
                test_session.slots = res.manipulated_slots
                verdict, stats = test_session.verify(msg, clean_sig, seed=int(seed))

            latency_ms = (time.perf_counter() - start_t) * 1000.0

            st.session_state["attack_verdict"] = verdict
            st.session_state["attack_stats"] = stats
            st.session_state["attack_latency"] = latency_ms
            st.session_state["attack_name"] = attack_type

            # Log attack triage into SQLite & HashChain
            event_id = f"evt_{uuid.uuid4().hex[:12]}"
            repo = TeleShieldRepository()
            db_events = repo.get_audit_events()
            chain = HashChain()
            chain.events = db_events

            audit_ev = chain.log_verification(
                event_id=event_id,
                message_id=clean_sig.message_id,
                signer_id=clean_sig.signer_id,
                verifier_id=clean_sig.verifier_id,
                verdict=verdict.verdict.value,
                attack_type=attack_type,
                global_mismatch=verdict.observed_rate or 0.0,
                threshold=verdict.threshold or 0.0,
                p_value=verdict.p_value or 1.0,
                shots=1000,
                qubits_consumed=stats.total_states if stats else 0,
                latency=latency_ms,
                block_statistics=stats.to_dict() if stats else {},
                basis_statistics=stats.per_basis_rates if stats else {},
            )
            repo.save_audit_event(audit_ev)
            repo.save_verification_event(
                event_id=event_id,
                signature_id=clean_sig.message_id,
                verifier_id=clean_sig.verifier_id,
                verdict=verdict.verdict.value,
                attack_type=attack_type,
                global_mismatch=verdict.observed_rate or 0.0,
                threshold=verdict.threshold or 0.0,
                p_value=verdict.p_value or 1.0,
                shots=1000,
                qubits_consumed=stats.total_states if stats else 0,
                latency=latency_ms,
                audit_hash=audit_ev.event_hash,
            )

    atk_v = st.session_state.get("attack_verdict")
    atk_s = st.session_state.get("attack_stats")
    atk_lat = st.session_state.get("attack_latency", 0.0)

    if atk_v:
        st.markdown("---")
        st.markdown("### Detection Outcome & Forensic Triage")

        if atk_v.is_accepted:
            st.warning(f"### Detector Decision: {atk_v.verdict.value} (Sub-threshold or unflagged)")
        else:
            st.error(f"### Detector Decision: {atk_v.verdict.value} [THREAT NEUTRALIZED]")

        st.markdown(f"**Explanation:** {atk_v.reason}")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Observed Mismatch Rate", f"{atk_v.observed_rate:.4f}" if atk_v.observed_rate is not None else "N/A")
        with col_m2:
            st.metric("Acceptance Threshold", f"{atk_v.threshold:.4f}" if atk_v.threshold else "N/A")
        with col_m3:
            st.metric("Evaluation Latency", f"{atk_lat:.2f} ms")
        with col_m4:
            st.metric("Ground Truth Attack", st.session_state.get("attack_name", "Attack"))

        if atk_s:
            st.markdown("#### Block-by-Block Error Distribution")
            block_rates = [b.mismatch_rate for b in atk_s.block_statistics]
            fig_atk = plot_per_block_heatmap(block_rates, atk_v.threshold or 0.045)
            st.plotly_chart(fig_atk, width="stretch")
