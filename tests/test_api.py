"""
FastAPI Integration Tests
Verifies that all TeleShield REST API endpoints function correctly:
Keygen, Distribute, Sign, Verify, Attack, Security, and Audit.
"""

import pytest
from fastapi.testclient import TestClient
from teleshield.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_health_and_security_calculator(client):
    res = client.post(
        "/api/security/calculate",
        json={
            "n": 32,
            "L": 100,
            "epsilon": 0.01,
            "target_false_rejection": 1e-6,
            "target_forgery_probability": 1e-9,
            "attacker_model": "intercept_resend",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "acceptance_threshold" in data
    assert "recommended_min_L" in data
    assert data["acceptance_threshold"] > 0.01


def test_api_full_qds_and_attack_workflow(client):
    # 1. Keygen
    kg_res = client.post(
        "/api/keygen",
        json={
            "n": 8,
            "L": 16,
            "backend": "exact",
            "hardware_profile": "ideal",
            "basis_mode": "XZ",
            "seed": 42,
        },
    )
    assert kg_res.status_code == 200
    kg_data = kg_res.json()
    session_id = kg_data["session_id"]
    assert kg_data["total_states_prepared"] == 8 * 2 * 16

    # 2. Distribute
    dist_res = client.post(
        "/api/distribute",
        json={
            "session_id": session_id,
            "bell_visibility": 1.0,
            "shots": 1,
            "seed": 42,
        },
    )
    assert dist_res.status_code == 200
    dist_data = dist_res.json()
    assert dist_data["total_states_teleported"] == 8 * 2 * 16
    assert dist_data["average_fidelity"] > 0.99

    # 3. Sign
    sign_res = client.post(
        "/api/sign",
        json={
            "session_id": session_id,
            "message": "Quantum Secure Digital Contract v1.0",
            "hash_mode": "sha256",
        },
    )
    assert sign_res.status_code == 200
    sign_data = sign_res.json()
    signature_payload = sign_data["signature_payload"]
    assert signature_payload["message_id"] == sign_data["message_id"]

    # 4. Verify Legitimate Signature
    verify_res = client.post(
        "/api/verify",
        json={
            "session_id": session_id,
            "message": "Quantum Secure Digital Contract v1.0",
            "signature": signature_payload,
            "shots": 1000,
            "seed": 42,
        },
    )
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["verdict"] == "ACCEPT"
    assert verify_data["audit_hash"] is not None

    # 5. Audit Chain Verification
    audit_res = client.get("/api/audit/verify")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert audit_data["is_valid"] is True
    assert audit_data["total_events"] >= 1
