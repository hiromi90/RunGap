"""解析ジョブの実行（ローカルはプロセス内バックグラウンドスレッド）。"""
from __future__ import annotations
import threading
import time

from rungap_server.store import DB, lock
from rungap_pipeline.estimators.base import FrameSeq, CameraSpec, BodySpec, get_estimator
from rungap_pipeline.estimators.dummy_adapter import DummyPoseEstimator
from rungap_pipeline.pipeline.orchestrator import run_pipeline, run_metrics

# 「理想の走り」を表すダミー・パラメータ（実アプリでは登録済みモーション）
IDEAL_PARAMS = dict(foot_cycle_hz=1.55, v=5.15, trunk_deg=8.0, arm_deg=62.0,
                    contact_ratio=0.335, knee_bend=0.13, seed=1)


def _body_spec(bp: dict) -> BodySpec:
    return BodySpec(height_cm=bp["height_cm"], inseam_cm=bp["inseam_cm"],
                    weight_kg=bp["weight_kg"])


def process_analysis(analysis_id: str) -> None:
    a = DB["analyses"][analysis_id]
    job = DB["jobs"][a["job_id"]]
    try:
        job["status"] = "running"
        bp = DB["body_profiles"][a["body_profile_id"]]
        body = _body_spec(bp)
        frames = FrameSeq(frames=None, fps=60, num_frames=180)
        camera = CameraSpec(view="side", height_m=1.2)

        # 理想（登録モーション相当）を同じ体型で算出
        _, ideal_metrics = run_metrics(DummyPoseEstimator(**IDEAL_PARAMS),
                                       frames, camera, body)

        for p in (20, 55, 85):
            job["progress"] = p
            time.sleep(0.12)

        est = get_estimator(a["model_variant"])   # 差し替え式：現状は dummy
        result, actual = run_pipeline(est, frames, camera, body,
                                      ideal_metrics=ideal_metrics,
                                      model_variant=a["model_variant"])
        with lock():
            a["result"] = result.to_dict()
            a["_actual"] = actual            # 評価モード用（メモリ内）
            a["status"] = "done"
            job["status"] = "done"
            job["progress"] = 100
    except Exception as e:  # noqa: BLE001
        with lock():
            a["status"] = "failed"
            job["status"] = "failed"
            job["error"] = str(e)


def enqueue(analysis_id: str) -> None:
    threading.Thread(target=process_analysis, args=(analysis_id,), daemon=True).start()
