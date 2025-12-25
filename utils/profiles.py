"""API Key and Model profiles management."""
import json
from pathlib import Path

PROFILES_PATH = Path.home() / ".mvguard" / "profiles.json"


def load_profiles() -> list[dict]:
    """Load saved profiles."""
    if not PROFILES_PATH.exists():
        return []
    try:
        return json.loads(PROFILES_PATH.read_text())
    except:
        return []


def save_profile(name: str, api_key: str, model: str) -> bool:
    """Save a new profile."""
    profiles = load_profiles()
    # Update existing or add new
    for p in profiles:
        if p["name"] == name:
            p["api_key"] = api_key
            p["model"] = model
            break
    else:
        profiles.append({"name": name, "api_key": api_key, "model": model})

    PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILES_PATH.write_text(json.dumps(profiles, ensure_ascii=False, indent=2))
    return True


def delete_profile(name: str) -> bool:
    """Delete a profile by name."""
    profiles = load_profiles()
    profiles = [p for p in profiles if p["name"] != name]
    PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILES_PATH.write_text(json.dumps(profiles, ensure_ascii=False, indent=2))
    return True


def get_profile_choices() -> list[str]:
    """Get profile names for dropdown."""
    return [p["name"] for p in load_profiles()]
