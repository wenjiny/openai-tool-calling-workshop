# app/session_store.py
import json, os
from pathlib import Path

SESS_DIR = Path(".sessions")
SESS_DIR.mkdir(exist_ok=True)

def _path(name: str) -> Path:
    return SESS_DIR / f"{name}.json"

def load_session(name: str) -> list:
    p = _path(name)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_session(name: str, messages: list) -> None:
    _path(name).write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
