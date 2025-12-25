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


def save_profile(api_key: str, model: str) -> bool:
    """Save a new profile with format 'model:key'."""
    profiles = load_profiles()
    name = f"{model}:{api_key[:8]}..."
    # Check if same model+key exists
    for p in profiles:
        if p["api_key"] == api_key and p["model"] == model:
            return True  # Already exists
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
