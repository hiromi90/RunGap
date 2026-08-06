"""インメモリ・ストア（ローカル開発用。再起動で消える）。"""
from __future__ import annotations
import threading
import uuid

_lock = threading.Lock()
DEMO_USER = "user_demo"

DB = {
    "users": {DEMO_USER: {"id": DEMO_USER, "display_name": "ピー",
                          "role": "athlete", "affiliation": "長距離ブロック"}},
    "body_profiles": {},
    "ideal_motions": {},
    "analyses": {},
    "jobs": {},
}


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def lock():
    return _lock
