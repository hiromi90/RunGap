"""局面分割。Step1 では接地区間から代表局面（接地時）を返す。"""
from __future__ import annotations


def contact_frame(contacts, side):
    for c in contacts:
        if c["side"] == side:
            return c["start"]
    return 0
