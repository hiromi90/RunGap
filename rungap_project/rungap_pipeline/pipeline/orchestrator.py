"""段階のオーケストレーション：入力→アダプタ→正規化→較正→検出→指標→信頼度→出力。"""
from __future__ import annotations
from rungap_pipeline.estimators.base import PoseEstimator, FrameSeq, CameraSpec, BodySpec
from rungap_pipeline.calibration.scale import calibrate
from rungap_pipeline.gait.events import detect_contacts
from rungap_pipeline.metrics.compute import compute_all
from rungap_pipeline.confidence.assign import assign
from rungap_pipeline.schema import MetricComparison, PipelineResult

_ORDER = [
    ("knee_angle", "none"), ("trunk_lean", "none"), ("arm_swing", "none"),
    ("ground_contact_time", "right"), ("ground_contact_time", "left"),
    ("stride_length", "none"), ("pitch", "none"),
]


def run_metrics(estimator: PoseEstimator, frames, camera, body):
    pose = estimator.estimate(frames, camera, body)
    scale = calibrate(pose, body)
    contacts = detect_contacts(pose)
    metrics = compute_all(pose, contacts, scale, body, frames.fps)
    return pose, metrics


def run_pipeline(estimator: PoseEstimator, frames: FrameSeq, camera: CameraSpec,
                 body: BodySpec, ideal_metrics: dict, model_variant: str):
    pose, actual = run_metrics(estimator, frames, camera, body)
    result = PipelineResult(model_variant=model_variant, status="done")
    for key in _ORDER:
        metric, side = key
        iv = ideal_metrics[key]["value"]
        av = actual[key]["value"]
        result.metrics.append(MetricComparison(
            metric=metric, side=side, ideal_value=iv, actual_value=av,
            diff=round(av - iv, 1), unit=actual[key]["unit"],
            confidence=assign(key, pose), phase_breakdown=actual[key]["phase"],
        ))
    return result, actual
