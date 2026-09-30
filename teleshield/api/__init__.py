"""
TeleShield REST API Layer
FastAPI application exposing quantum digital signature lifecycle,
attack simulations, threat analytics, and cryptographic audit endpoints.
"""

from teleshield.api.main import app

__all__ = ["app"]
