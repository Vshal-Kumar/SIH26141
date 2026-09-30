"""
TeleShield Streamlit Application Entrypoint
Main router orchestrating the 6 operational dashboards via modern st.navigation.
Professional high-tech styling with zero emojis.
"""

import sys
from pathlib import Path
import streamlit as st
import requests

# Ensure root directory is always on sys.path regardless of execution method
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure layout and metadata
st.set_page_config(
    page_title="TeleShield - Quantum Threat Framework",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Cyber Dark CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        color: #00d2ff;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

from teleshield.dashboard.views.overview import render_overview_page
from teleshield.dashboard.views.qds import render_qds_page
from teleshield.dashboard.views.verification import render_verification_page
from teleshield.dashboard.views.attacks import render_attacks_page
from teleshield.dashboard.views.security import render_security_page
from teleshield.dashboard.views.audit import render_audit_page

# Define Pages with modern st.Page
overview_page = st.Page(render_overview_page, title="Overview & Threat Center", default=True)
qds_page = st.Page(render_qds_page, title="QDS Protocol Simulation")
verification_page = st.Page(render_verification_page, title="Signature Verification")
attacks_page = st.Page(render_attacks_page, title="Attack Proving Ground")
security_page = st.Page(render_security_page, title="Security Analysis & Bounds")
audit_page = st.Page(render_audit_page, title="Cryptographic Audit Chain")

# Register navigation groups
pg = st.navigation({
    "Operations": [overview_page, qds_page, verification_page],
    "Security & Analysis": [attacks_page, security_page, audit_page],
})

# Sidebar Telemetry and System Status
with st.sidebar:
    st.markdown("### TeleShield")
    st.caption("Quantum Threat Detection for Teleportation QDS")
    st.markdown("---")

    # REST API Connectivity Probe
    api_online = False
    try:
        r = requests.get("http://127.0.0.1:8000/api/metrics", timeout=0.4)
        api_online = (r.status_code == 200)
    except Exception:
        api_online = False

    st.markdown("### System Telemetry")
    if api_online:
        st.success("**REST API:** ONLINE (Port 8000)")
    else:
        st.info("**REST API:** STANDALONE MODE\n*(Run `uvicorn teleshield.api.main:app` for REST access)*")

    current_session = st.session_state.get("current_session")
    if current_session:
        st.markdown(f"**Session:** `{current_session.session_id[:10]}...`")
        st.markdown(f"**Backend:** `{current_session.backend.name.upper()}`")
        st.markdown(f"**Available Slots:** `{current_session.available_slots_count}`")
    else:
        st.caption("No active session initialized. Configure and teleport states in QDS Protocol Simulation.")

    st.markdown("---")
    st.caption("TeleShield Research Prototype | SIH Local Runtime")

# Run active page
pg.run()
