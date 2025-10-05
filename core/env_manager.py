from core.utils import check_or_create_app_dir, get_app_dir


check_or_create_app_dir()

import os
import json
from pathlib import Path
from dotenv import load_dotenv, set_key, dotenv_values

APP_DIR = Path(get_app_dir())
ENV_PATH = APP_DIR / ".env"

SAMPLE_DATA = {
    "API_KEY": {"value": "123456", "is_secret": True},
    "DEBUG_MODE": {"value": "true", "is_secret": False},
    "SERVICE_URL": {"value": "https://example.com", "is_secret": False},
}


def ensure_env_exists():
    """Create app_dir and .env with sample data if not present."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not ENV_PATH.exists():
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            for k, v in SAMPLE_DATA.items():
                f.write(f"{k}={json.dumps(v)}\n")


ensure_env_exists()


def _load_env_dict():
    """Return current environment dictionary with parsed JSON values."""
    ensure_env_exists()
    load_dotenv(ENV_PATH)
    raw_env = dotenv_values(ENV_PATH)
    parsed = {}
    for key, val in raw_env.items():
        try:
            parsed[key] = json.loads(val)
        except (TypeError, json.JSONDecodeError):
            parsed[key] = {"value": val, "is_secret": False}
    return parsed


# -------------------------------------------------------------------
# CRUD-like methods
# -------------------------------------------------------------------


def get_all():
    """Return all env key/value pairs as Python dict."""
    return _load_env_dict()


def get_value(key):
    """Return a single key’s value dict or None."""
    return _load_env_dict().get(key)


def create_value(key, value, is_secret=False):
    """Create a new key with value and flag (no overwrite)."""
    env = _load_env_dict()
    if key in env:
        raise KeyError(f"{key} already exists.")
    set_key(str(ENV_PATH), key, json.dumps({"value": value, "is_secret": is_secret}))
    return True


def update_value(key, value=None, is_secret=None):
    """Update an existing key’s value or secret flag."""
    env = _load_env_dict()
    if key not in env:
        raise KeyError(f"{key} not found.")
    current = env[key]
    if value is not None:
        current["value"] = value
    if is_secret is not None:
        current["is_secret"] = is_secret
    set_key(str(ENV_PATH), key, json.dumps(current))
    return True


def delete_value(key):
    """Delete a single key."""
    env = _load_env_dict()
    if key not in env:
        raise KeyError(f"{key} not found.")
    # Rewrite .env without this key
    del env[key]
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for k, v in env.items():
            f.write(f"{k}={json.dumps(v)}\n")
    return True


def bulk_create(pairs):
    """
    Create multiple new keys at once.
    pairs: dict -> { key: {"value": ..., "is_secret": ...}, ... }
    """
    env = _load_env_dict()
    for k in pairs:
        if k in env:
            raise KeyError(f"{k} already exists.")
    with open(ENV_PATH, "a", encoding="utf-8") as f:
        for k, v in pairs.items():
            f.write(f"{k}={json.dumps(v)}\n")
    return True


def bulk_update(pairs):
    """
    Bulk update multiple existing keys.
    pairs: dict -> { key: {"value": ..., "is_secret": ...}, ... }
    """
    env = _load_env_dict()
    env.update(pairs)
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for k, v in env.items():
            f.write(f"{k}={json.dumps(v)}\n")
    return True
