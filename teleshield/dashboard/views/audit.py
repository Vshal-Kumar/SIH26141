"""
Dashboard View 6: Cryptographic Audit Log & Chain Verification
Displays append-only SHA-256 hash-chained verification audit records.
Provides interactive chain integrity verification and data export (CSV, JSON).
Professional styling with zero emojis.
"""

import streamlit as st
import pandas as pd
from teleshield.audit.hashchain import HashChain
from teleshield.database.repository import TeleShieldRepository


def render_audit_page():
    st.markdown("## Cryptographic Audit Log & Chain Verification")
    st.caption("Tamper-evident verification audit trail. Any retrofitted tampering permanently invalidates subsequent event hashes.")

    repo = TeleShieldRepository()
    db_events = repo.get_audit_events()

    # Reconstruct in-memory chain to verify
    chain = HashChain()
    chain.events = db_events

    res = chain.verify_integrity()

    # Top Status Banner
    if res.is_valid:
        st.success(f"### [CONFIRMED] {res.status} ({res.total_events} Events Chained)")
        st.markdown(f"**Integrity Report:** {res.details}")
    else:
        st.error(f"### [COMPROMISED] {res.status} (Tampering Detected at Index {res.compromised_index})")
        st.markdown(f"**Forensic Alert:** {res.details}")

    st.markdown("---")
    # Action buttons: Verify, Export CSV, Export JSON
    act_col1, act_col2, act_col3 = st.columns(3)
    with act_col1:
        if st.button("Re-Verify Entire Chain Integrity", type="primary", width="stretch"):
            st.rerun()
    with act_col2:
        csv_data = chain.export_csv()
        st.download_button(
            label="Export Audit Log (CSV)",
            data=csv_data,
            file_name="teleshield_audit_log.csv",
            mime="text/csv",
            width="stretch",
        )
    with act_col3:
        json_data = chain.export_json()
        st.download_button(
            label="Export Audit Log (JSON)",
            data=json_data,
            file_name="teleshield_audit_log.json",
            mime="application/json",
            width="stretch",
        )

    st.markdown("---")
    st.markdown("### Verification Event Log Records")

    if not db_events:
        st.info("No verification events logged yet. Execute a verification in the Signature Verification or Attack Lab pages to populate the chain.")
        return

    table_records = []
    for idx, e in enumerate(db_events):
        table_records.append({
            "Index": idx,
            "Event ID": e.event_id,
            "Signer": e.signer_id,
            "Verifier": e.verifier_id,
            "Verdict": e.verdict,
            "Attack Type": e.attack_type,
            "Mismatch Rate": f"{e.global_mismatch:.4f}",
            "Threshold": f"{e.threshold:.4f}",
            "p-Value": f"{e.p_value:.3e}",
            "Latency (ms)": f"{e.latency:.2f}",
            "Event Hash": f"{e.event_hash[:12]}...",
            "Prev Hash": f"{e.previous_hash[:12]}...",
        })

    df = pd.DataFrame(table_records)
    st.dataframe(df, width="stretch")

    with st.expander("Inspect Cryptographic Hash Sequence"):
        for e in db_events[-5:]:
            st.markdown(f"**Event `{e.event_id}`:**")
            st.code(
                f"Previous Hash: {e.previous_hash}\nEvent Hash:    {e.event_hash}\nPayload Hash:  {e.config_hash}",
                language="text"
            )
