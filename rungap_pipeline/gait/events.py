"""歩行周期検出：足首の鉛直位置から接地区間を検出する。"""
from __future__ import annotations
from rungap_pipeline.estimators.base import Pose3DSeq
from rungap_pipeline.skeleton.canonical import idx


def _runs(mask):
    runs, s = [], None
    for i, m in enumerate(mask):
        if m and s is None:
            s = i
        elif not m and s is not None:
            runs.append((s, i - 1)); s = None
    if s is not None:
        runs.append((s, len(mask) - 1))
    return runs


def detect_contacts(pose: Pose3DSeq):
    out = []
    for side in ("l", "r"):
        y = pose.joints[:, idx(f"{side}_ankle"), 1]
        thr = float(y.min()) + 0.05 * (float(y.max()) - float(y.min()) + 1e-9)
        for s, e in _runs(y <= thr):
            out.append({"side": side, "start": s, "end": e})
    return out
