"""
Hardware Profile Loader
Parses YAML hardware profile files from the profiles/ directory and instantiates HardwareProfile objects.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

from teleshield.hardware.profiles import HardwareProfile


def get_profiles_dir() -> Path:
    """Resolve profiles directory path."""
    # Check project root profiles directory
    candidate = Path(__file__).resolve().parent.parent.parent / "profiles"
    if candidate.exists():
        return candidate
    # Fallback to local
    local_candidate = Path("profiles")
    if local_candidate.exists():
        return local_candidate
    return candidate


def load_hardware_profile(name_or_path: str) -> HardwareProfile:
    """
    Loads hardware profile from name (e.g. 'ion_trap', 'rydberg', 'ideal')
    or direct file path.
    """
    p_path = Path(name_or_path)
    if not p_path.exists():
        if not name_or_path.endswith(".yaml") and not name_or_path.endswith(".yml"):
            p_path = get_profiles_dir() / f"{name_or_path}.yaml"
        else:
            p_path = get_profiles_dir() / name_or_path

    if not p_path.exists():
        raise FileNotFoundError(f"Hardware profile not found: {name_or_path} (checked {p_path})")

    with open(p_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return HardwareProfile(
        name=data.get("name", p_path.stem),
        display_name=data.get("display_name", p_path.stem.title()),
        profile_type=data.get("profile_type", "custom"),
        backend_name=data.get("backend", "exact"),
        description=data.get("description", ""),
        reference_model=data.get("reference_model", "Custom Baseline"),
        parameters=data.get("parameters", {}),
        shots=int(data.get("shots", 10000)),
        seed=data.get("seed", 42),
    )


def list_available_profiles() -> List[str]:
    """Returns list of profile names found in profiles directory."""
    p_dir = get_profiles_dir()
    if not p_dir.exists():
        return ["ideal", "ion_trap", "rydberg"]
    return [p.stem for p in p_dir.glob("*.yaml")]
