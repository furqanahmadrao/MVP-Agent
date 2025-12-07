"""
Google Quota Tracker - Simple daily quota tracker for Google Custom Search usage.

Stores daily usage in logs/google_quota.json:
{
  "date": "YYYY-MM-DD",
  "used": 12
}

Functions:
- get_quota_config() -> dict
- get_daily_usage() -> int
- can_reserve_requests(n) -> bool
- increment_usage(n) -> None
- reset_if_new_day() -> None
"""
from datetime import datetime
import json
import os
from typing import Dict

LOG_DIR = "logs"
QUOTA_FILE = os.path.join(LOG_DIR, "google_quota.json")

# Defaults (can be overridden via env vars in calling code)
DEFAULTS = {
    "DAILY_QUOTA": 100,
    "MAX_RESULTS_PER_REQUEST": 10,
    "MAX_REQUESTS_PER_TASK": 5,
    "RETRY_ATTEMPTS": 3
}


def _ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def _read_quota_file() -> Dict:
    _ensure_log_dir()
    if not os.path.exists(QUOTA_FILE):
        return {"date": datetime.utcnow().strftime("%Y-%m-%d"), "used": 0}
    try:
        with open(QUOTA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # Corrupt or unreadable file -> reset
        data = {"date": datetime.utcnow().strftime("%Y-%m-%d"), "used": 0}
    return data


def _write_quota_file(data: Dict):
    _ensure_log_dir()
    tmp = QUOTA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, QUOTA_FILE)


def reset_if_new_day():
    data = _read_quota_file()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if data.get("date") != today:
        data = {"date": today, "used": 0}
        _write_quota_file(data)


def get_daily_usage() -> int:
    reset_if_new_day()
    data = _read_quota_file()
    return int(data.get("used", 0))


def can_reserve_requests(requests_needed: int, daily_quota: int) -> bool:
    """
    Check if we can reserve the requested number of Google calls without exceeding quota.
    This function does NOT modify the persisted counter; call increment_usage() after successful calls.
    """
    reset_if_new_day()
    data = _read_quota_file()
    used = int(data.get("used", 0))
    return (used + requests_needed) <= int(daily_quota)


def increment_usage(n: int = 1):
    """
    Increment the usage counter by n. Persists the new value.
    """
    reset_if_new_day()
    data = _read_quota_file()
    used = int(data.get("used", 0))
    data["used"] = used + int(n)
    _write_quota_file(data)


def get_quota_config(env: Dict[str, str]) -> Dict:
    """
    Build quota config from environment mapping (os.environ or similar).
    Returns dict with keys: DAILY_QUOTA, MAX_RESULTS_PER_REQUEST, MAX_REQUESTS_PER_TASK, RETRY_ATTEMPTS
    """
    cfg = {
        "DAILY_QUOTA": int(env.get("GOOGLE_DAILY_QUOTA", DEFAULTS["DAILY_QUOTA"])),
        "MAX_RESULTS_PER_REQUEST": int(env.get("GOOGLE_MAX_RESULTS_PER_REQUEST", DEFAULTS["MAX_RESULTS_PER_REQUEST"])),
        "MAX_REQUESTS_PER_TASK": int(env.get("GOOGLE_MAX_REQUESTS_PER_TASK", DEFAULTS["MAX_REQUESTS_PER_TASK"])),
        "RETRY_ATTEMPTS": int(env.get("GOOGLE_RETRY_ATTEMPTS", DEFAULTS["RETRY_ATTEMPTS"]))
    }
    return cfg
