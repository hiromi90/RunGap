"""cm較正：体型寸法から画素↔実長のスケール（cm/単位）を決める。"""
from __future__ import annotations
import numpy as np
from rungap_pipeline.estimators.base import Pose3DSeq, BodySpec
from rungap_pipeline.skeleton.canonical import idx


def calibrate(pose: Pose3DSeq, body: BodySpec) -> float:
    if pose.metric_scale:
        return 100.0
    hip = pose.joints[:, idx("r_hip")]
    ankle = pose.joints[:, idx("r_ankle")]
    leg_units = float(np.median(np.linalg.norm(hip - ankle, axis=1)))
    if leg_units <= 1e-6:
        return 1.0
    return body.inseam_cm / leg_units
