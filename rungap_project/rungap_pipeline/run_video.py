"""実動画で姿勢推定→6指標を算出。
例：python3 -m rungap_pipeline.run_video side_view.mp4 --model mediapipe \\
        --model-path pose_landmarker.task --inseam 80"""
from __future__ import annotations
import argparse
import json
import os
import sys
import rungap_pipeline.estimators  # noqa: F401  アダプタ登録
from rungap_pipeline.estimators.base import FrameSeq, CameraSpec, BodySpec, get_estimator
from rungap_pipeline.calibration.scale import calibrate
from rungap_pipeline.gait.events import detect_contacts
from rungap_pipeline.metrics.compute import compute_all
from rungap_pipeline.confidence.assign import assign
from rungap_pipeline.io_video import probe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--model", default="mediapipe")
    ap.add_argument("--model-path", default=None, help="pose_landmarker.task のパス")
    ap.add_argument("--height", type=float, default=172)
    ap.add_argument("--inseam", type=float, default=80)
    ap.add_argument("--weight", type=float, default=58)
    a = ap.parse_args()
    if a.model_path:
        os.environ["RUNGAP_POSE_MODEL"] = a.model_path

    try:
        fps, n = probe(a.video)
        frames = FrameSeq(frames=a.video, fps=fps, num_frames=n)
        body = BodySpec(height_cm=a.height, inseam_cm=a.inseam, weight_kg=a.weight)
        est = get_estimator(a.model)
        pose = est.estimate(frames, CameraSpec(view="side"), body)
        scale = calibrate(pose, body)
        contacts = detect_contacts(pose)
        metrics = compute_all(pose, contacts, scale, body, fps)
    except RuntimeError as e:
        print("エラー:", e, file=sys.stderr)
        sys.exit(1)

    detected = int((pose.per_joint_conf.mean(axis=1) > 0.1).sum())
    total = int(pose.per_joint_conf.shape[0])
    print(f"検出できたフレーム: {detected}/{total}", file=sys.stderr)
    if detected == 0:
        print("※ 人物が検出されませんでした。側方から全身が明るく映った動画かご確認ください。",
              file=sys.stderr)

    rows = [{"metric": k[0], "side": k[1], "value": v["value"],
             "unit": v["unit"], "confidence": assign(k, pose)}
            for k, v in metrics.items()]
    print(json.dumps({"model": a.model, "fps": round(fps, 1), "frames": n,
                      "detected_frames": detected, "metrics": rows},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
