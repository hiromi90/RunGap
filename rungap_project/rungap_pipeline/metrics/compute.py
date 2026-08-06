"""6指標の算出（モデル非依存）。共通スケルトンの3D関節から計算する。
Step1 は配線の実証が目的で、算出式は簡易版（要精緻化の箇所は TODO）。"""
from __future__ import annotations
import numpy as np
from rungap_pipeline.estimators.base import Pose3DSeq, BodySpec
from rungap_pipeline.skeleton.canonical import idx
from rungap_pipeline.gait.phases import contact_frame

_UP = np.array([0.0, 1.0, 0.0])


def _ang(a, b, c):
    v1, v2 = a - b, c - b
    cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
    return float(np.degrees(np.arccos(np.clip(cos, -1, 1))))


def _ang_vert(v):
    cos = np.dot(v, _UP) / (np.linalg.norm(v) + 1e-9)
    return float(np.degrees(np.arccos(np.clip(cos, -1, 1))))


def compute_all(pose: Pose3DSeq, contacts, scale: float, body: BodySpec, fps: float):
    J = pose.joints
    out = {}

    cf = contact_frame(contacts, "r")
    knee = _ang(J[cf, idx("r_hip")], J[cf, idx("r_knee")], J[cf, idx("r_ankle")])
    out[("knee_angle", "none")] = {"value": round(knee, 1), "unit": "deg",
                                   "phase": {"contact": round(knee, 1)}}

    trunk = np.mean([_ang_vert(J[f, idx("chest")] - J[f, idx("pelvis")])
                     for f in range(J.shape[0])])
    out[("trunk_lean", "none")] = {"value": round(float(trunk), 1), "unit": "deg", "phase": None}

    a = [_ang_vert(J[f, idx("r_wrist")] - J[f, idx("r_shoulder")]) for f in range(J.shape[0])]
    out[("arm_swing", "none")] = {"value": round(max(a) - min(a), 1), "unit": "deg", "phase": None}

    for side in ("right", "left"):
        s = side[0]
        durs = [(c["end"] - c["start"] + 1) / fps * 1000.0
                for c in contacts if c["side"] == s]
        val = round(float(np.mean(durs)), 0) if durs else 0.0
        out[("ground_contact_time", side)] = {"value": val, "unit": "ms", "phase": None}

    rc = [(c["start"] + c["end"]) / 2 for c in contacts if c["side"] == "r"]
    rx = [float(J[int(round(m)), idx("r_ankle"), 0]) for m in rc]
    step = float(np.mean(np.diff(rx))) * scale / 2.0 if len(rx) >= 2 else 0.0
    out[("stride_length", "none")] = {"value": round(step, 0), "unit": "cm", "phase": None}

    dur_s = J.shape[0] / fps
    pitch = len(contacts) / dur_s * 60.0 if dur_s > 0 else 0.0
    out[("pitch", "none")] = {"value": round(pitch, 0), "unit": "spm", "phase": None}
    return out
