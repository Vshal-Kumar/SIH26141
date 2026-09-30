"""
Dashboard View 2: QDS Protocol Simulation
Interactive control console for keypair generation, quantum public-key teleportation,
message binding, and signature creation across configurable hardware profiles.
Professional styling with zero emojis.
"""

import streamlit as st
from teleshield.hardware.loaders import load_hardware_profile
from teleshield.qds.session import QDSSession
from teleshield.qds.hashing import HashMode
from teleshield.database.repository import TeleShieldRepository


def render_qds_page():
    st.markdown("## QDS Simulation & Quantum Teleportation Center")
    st.caption("Generate quantum digital signatures and teleport public quantum key states into verifier memory.")

    # Protocol & Simulation Sizing Presets
    st.markdown("### Protocol & Simulation Sizing Presets")
    preset_choice = st.radio(
        "Simulation Workload Profile",
        [
            "Interactive Fast Demo (n=8 bits, L=32 states -> 512 total qubits, ~0.5s)",
            "Standard Research Profile (n=16 bits, L=64 states -> 2,048 total qubits, ~2s)",
            "Full Security Benchmark (n=64 bits, L=222 states -> 28,416 total qubits, ~30s)",
            "Custom Configuration",
        ],
        index=0,
    )

    if "Fast Demo" in preset_choice:
        default_n, default_L = 8, 32
    elif "Standard Research" in preset_choice:
        default_n, default_L = 16, 64
    elif "Full Security" in preset_choice:
        default_n, default_L = 64, 222
    else:
        default_n, default_L = 8, 32

    # Configuration controls
    col1, col2, col3 = st.columns(3)
    with col1:
        prof_name = st.selectbox("Hardware Profile", ["ion_trap", "rydberg", "ideal"], index=0)
        profile = load_hardware_profile(prof_name)
        st.caption(f"**Backend:** `{profile.backend_name.upper()}` | **Reference:** {profile.reference_model}")
    with col2:
        basis_mode = st.selectbox("Quantum Basis Mode", ["XZ", "XYZ"], index=0, help="Primary mode: XZ (2-basis); Six-state mode: XYZ (3-basis)")
        hash_mode_str = st.selectbox("Message Hash Binding", ["SHA-256", "Toeplitz (EAU)"], index=0)
        hash_mode = HashMode.SHA256 if "SHA" in hash_mode_str else HashMode.TOEPLITZ
    with col3:
        is_custom = "Custom" in preset_choice
        n_bits = st.number_input("Tag Bits (n)", min_value=8, max_value=256, value=default_n, step=8, disabled=not is_custom)
        L_states = st.number_input("Qubits per Bit (L)", min_value=16, max_value=500, value=default_L, step=16, disabled=not is_custom)

    # Qubit Resource Accounting Breakdown
    total_key_qubits = int(n_bits) * 2 * int(L_states)
    verify_qubits = int(n_bits) * int(L_states)
    bell_pairs_needed = total_key_qubits

    st.markdown("#### Quantum Resource Accounting for Simulation")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        st.metric(
            label="Instantaneous Circuit Register",
            value="3 Qubits",
            delta="Alice |psi>, Bell 1, Bell 2",
            help="The quantum simulator only requires a 3-qubit circuit at any moment. Teleportation is simulated sequentially, requiring minimal RAM/CPU."
        )
    with q_col2:
        st.metric(
            label="Total Public Qubits Distributed",
            value=f"{total_key_qubits:,} Qubits",
            delta=f"2 * {n_bits} * {L_states}",
            help="Formula: 2 * n * L (Each of the n bits has two branches: bit 0 and bit 1, with L states each)"
        )
    with q_col3:
        st.metric(
            label="Qubits Consumed at Verification",
            value=f"{verify_qubits:,} Qubits",
            delta=f"{n_bits} * {L_states}",
            help="Formula: n * L (For an authentic tag, exactly 1 branch per bit position is revealed and measured)"
        )
    with q_col4:
        st.metric(
            label="EPR Bell Pairs Consumed",
            value=f"{bell_pairs_needed:,} Pairs",
            delta=f"1 Pair per Qubit",
            help="Formula: 1 EPR Bell pair (|Phi+>) is consumed per teleported state"
        )

    with st.expander("Qubit Calculation Guide & Formulas"):
        st.markdown(
            f"""
- **Tag Bits ($n = {n_bits}$):** Length of the message hash tag.
- **States per Bit Value ($L = {L_states}$):** Security parameter determining statistical confidence.
- **Total Key States Prepared & Teleported:** $N_{{\\text{{total}}}} = 2 \\times n \\times L = 2 \\times {n_bits} \\times {L_states} = \\mathbf{{{total_key_qubits:,}}}$ qubits.
  * *Why factor of 2?* The signer must prepare quantum states for both potential bit outcomes ($b = 0$ and $b = 1$) for every tag position.
- **Verification States Consumed:** $N_{{\\text{{verify}}}} = n \\times L = {n_bits} \\times {L_states} = \\mathbf{{{verify_qubits:,}}}$ qubits.
  * In signature verification, the message tag selects exactly one branch per position ($0$ or $1$). Bob measures only those states, and they are destroyed (consumed) upon measurement per the quantum no-cloning theorem.
- **Entangled Bell Pairs ($|\\Phi^+\\rangle$):** Teleportation of $N_{{\\text{{total}}}}$ states requires $N_{{\\text{{total}}}} = \\mathbf{{{bell_pairs_needed:,}}}$ Bell pairs ($2 \\times N_{{\\text{{total}}}}$ physical transmission qubits).
            """
        )

    st.markdown("---")
    st.markdown("### Message Entry & Signature Generation")
    default_msg = "Authorize electronic financial transfer of $1,000,000 to Account-7829-Quantum"
    user_message = st.text_area("Message Plaintext", value=default_msg, height=80)

    btn_col1, _ = st.columns([1, 4])
    with btn_col1:
        generate_btn = st.button("Generate & Teleport QDS", type="primary", width="stretch")

    if generate_btn or "current_session" in st.session_state:
        if generate_btn:
            with st.spinner("Generating Pauli keypairs and executing quantum teleportation..."):
                backend = profile.create_backend()
                session = QDSSession.create(
                    n=int(n_bits),
                    L=int(L_states),
                    backend=backend,
                    basis_mode=basis_mode,
                    bell_visibility=profile.get_param_value("bell_pair_fidelity", 1.0),
                    seed=42,
                )
                sig = session.sign(message=user_message, hash_mode=hash_mode)

                st.session_state["current_session"] = session
                st.session_state["current_signature"] = sig
                st.session_state["current_message"] = user_message
                st.session_state["current_profile"] = profile

                # Persist key and session metadata in SQLite
                repo = TeleShieldRepository()
                repo.save_key(session.keypair.metadata)
                repo.save_session(
                    session_id=session.session_id,
                    key_id=session.keypair.key_id,
                    signer_id=session.keypair.signer_id,
                    verifier_id=session.keypair.verifier_id,
                    status="ACTIVE",
                    backend=session.backend.name,
                )
                st.success("[SUCCESS] QDS Keypair generated, teleported to verifier slots, and message signed.")

        session = st.session_state.get("current_session")
        sig = st.session_state.get("current_signature")
        dist = session.distribution_report if session else None

        if session and sig:
            st.markdown("---")
            st.markdown("### Teleportation Distribution Telemetry")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.metric("Total States Teleported", f"{dist.total_states if dist else 0}")
            with m_col2:
                st.metric("Mean Teleportation Fidelity", f"{dist.average_fidelity:.5f}" if dist else "N/A")
            with m_col3:
                st.metric("Min / Max Fidelity", f"{dist.min_fidelity:.4f} / {dist.max_fidelity:.4f}" if dist else "N/A")
            with m_col4:
                st.metric("Available Verifier Slots", f"{session.available_slots_count}")

            st.markdown("### Generated Signature Envelope")
            env_col1, env_col2 = st.columns([1, 1])
            with env_col1:
                st.markdown(f"**Message ID:** `{sig.message_id}`")
                st.markdown(f"**Signer ID:** `{sig.signer_id}`")
                st.markdown(f"**Verifier ID:** `{sig.verifier_id}`")
                st.markdown(f"**Nonce:** `{sig.nonce}`")
                st.markdown(f"**Hash Mode:** `{sig.hash_mode.upper()}`")
                if sig.hash_mode == "sha256":
                    st.caption("Note: SHA-256 provides computational collision resistance; not information-theoretic.")
                else:
                    st.caption("Note: Toeplitz hashing provides information-theoretically bounded universal hashing.")
            with env_col2:
                st.markdown(f"**Calculated Tag (Hex):** `{sig.tag}`")
                st.markdown(f"**Tag Length:** {len(sig.tag_bits)} bits")
                st.markdown(f"**Revealed Private States:** {len(sig.revealed_states)} states")
                st.markdown(f"**Protocol Version:** `{sig.protocol_version}`")

            # Sample teleportation details
            if dist and dist.teleportation_samples:
                with st.expander("View Sample Teleportation Physics & Pauli Corrections"):
                    for idx, s in enumerate(dist.teleportation_samples[:4]):
                        st.markdown(
                            f"**Sample #{idx + 1}:** Alice measured input qubit $m_0={s['measurement_bits']['m0_alice_input']}$, "
                            f"Bell half $m_1={s['measurement_bits']['m1_alice_bell']} -> "
                            f"Bob applied Pauli correction: `{s['correction_applied']}` ($X^{{m1}} Z^{{m0}}$) | "
                            f"Output State Fidelity: **{s['fidelity']:.5f}**"
                        )
