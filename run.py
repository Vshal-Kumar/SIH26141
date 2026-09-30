"""
TeleShield Unified Service Launcher
Enables running the Streamlit Cyber Command Dashboard, the FastAPI REST Backend,
or both simultaneously from a single command.

Usage:
    python run.py --dashboard   # Launches Streamlit UI on http://localhost:8501
    python run.py --api         # Launches FastAPI REST API on http://localhost:8000
    python run.py --all         # Launches both services concurrently
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable


def launch_dashboard(port: int = 8501):
    cmd = [
        PYTHON_EXE, "-m", "streamlit", "run",
        str(ROOT_DIR / "teleshield" / "dashboard" / "app.py"),
        "--server.port", str(port),
        "--browser.gatherUsageStats", "false",
    ]
    return subprocess.Popen(cmd, cwd=str(ROOT_DIR))


def launch_api(port: int = 8000):
    cmd = [
        PYTHON_EXE, "-m", "uvicorn",
        "teleshield.api.main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
    ]
    return subprocess.Popen(cmd, cwd=str(ROOT_DIR))


def main():
    parser = argparse.ArgumentParser(description="TeleShield Unified Service Launcher")
    parser.add_argument("--dashboard", action="store_true", help="Launch Streamlit Dashboard (default port 8501)")
    parser.add_argument("--api", action="store_true", help="Launch FastAPI REST Service (default port 8000)")
    parser.add_argument("--all", action="store_true", help="Launch both Streamlit Dashboard and FastAPI REST Service")
    parser.add_argument("--api-port", type=int, default=8000, help="Port for FastAPI (default 8000)")
    parser.add_argument("--dashboard-port", type=int, default=8501, help="Port for Streamlit (default 8501)")

    args = parser.parse_args()

    # Default to dashboard if no flags passed
    if not (args.dashboard or args.api or args.all):
        args.dashboard = True

    procs = []

    try:
        if args.api or args.all:
            print(f"[TeleShield] Starting FastAPI REST service on http://localhost:{args.api_port}...")
            p_api = launch_api(port=args.api_port)
            procs.append(p_api)
            time.sleep(1)

        if args.dashboard or args.all:
            print(f"[TeleShield] Starting Streamlit Dashboard on http://localhost:{args.dashboard_port}...")
            p_dash = launch_dashboard(port=args.dashboard_port)
            procs.append(p_dash)

        print("[TeleShield] Services active. Press Ctrl+C to terminate.")
        for p in procs:
            p.wait()

    except KeyboardInterrupt:
        print("\n[TeleShield] Terminating active services...")
        for p in procs:
            p.terminate()
            p.wait()
        print("[TeleShield] Shutdown complete.")


if __name__ == "__main__":
    main()
