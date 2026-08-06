"""信頼度の一次付与（ヒューリスティック）。二次＝評価モードで較正（設計書9章）。"""
from __future__ import annotations
import numpy as np
from rungap_pipeline.estimators.base import Pose3DSeq
from rungap_pipeline.skeleton.canonical import idx

_ORDER = {"high": 2, "medium": 1, "low": 0}
_INV = {v: k for k, v in _ORDER.items()}

_INVOLVED = {
    ("knee_angle", "none"): ["r_hip", "r_knee", "r_ankle"],
    ("trunk_lean", "none"): ["pelvis", "chest"],
    ("arm_swing", "none"): ["r_shoulder", "r_wrist"],
    ("ground_contact_time", "right"): ["r_ankle", "r_heel"],
    ("ground_contact_time", "left"): ["l_ankle", "l_heel"],
    ("stride_length", "none"): ["r_ankle"],
    ("pitch", "none"): ["r_ankle", "l_ankle"],
}
_CAP = {("arm_swing", "none"): "medium", ("stride_length", "none"): "medium"}


def _cap(a, b):
    return _INV[min(_ORDER[a], _ORDER[b])]


def assign(metric_key, pose: Pose3DSeq) -> str:
    names = _INVOLVED.get(metric_key, [])
    if not names:
        return "medium"
    c = float(np.mean([pose.per_joint_conf[:, idx(n)].mean() for n in names]))
    lvl = "high" if c >= 0.8 else "medium" if c >= 0.6 else "low"
    if metric_key in _CAP:
        lvl = _cap(lvl, _CAP[metric_key])
    return lvl
