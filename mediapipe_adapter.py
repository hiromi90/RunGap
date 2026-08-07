"""実モデルの第一弾：MediaPipe Pose アダプタ（単眼→3D関節、Tasks API 対応）。

- pip で導入でき CPU で動く。world landmarks はおおよそメートルスケール。
- 現行の mediapipe（Tasks API）は姿勢モデル `pose_landmarker.task` が必要。
  一度ダウンロードして、環境変数 RUNGAP_POSE_MODEL にパスを設定するか、
  作業ディレクトリ／`rungap_pipeline/models/` に `pose_landmarker.task` として置く。
    https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
- 依存・モデルは estimate() 内で遅延解決。未導入・未配置なら分かりやすいエラー。
- 注意（要キャリブレーション）:
  * 関節角度（膝・肘）は座標回転に不変なので、そのまま意味を持つ。
  * 体幹前傾・腕振り・接地タイミング・ピッチは鉛直軸(y)が合っていれば妥当。
  * ストライド長は world landmarks が腰基準（全体の水平移動を含まない）ため、
    画像座標の水平移動＋cm較正が別途必要（TODO。現状は過小に出る）。
  * 進行方向/奥行きの軸対応は撮影セットアップ依存。実映像で確認・較正が前提
    （＝評価モード／Phase 0 の役割）。
"""
from __future__ import annotations
import os
import numpy as np
from rungap_pipeline.estimators.base import (
    PoseEstimator, FrameSeq, CameraSpec, BodySpec, Pose3DSeq, register,
)
from rungap_pipeline.skeleton.canonical import NUM_JOINTS, idx

_MP = {
    "l_shoulder": 11, "r_shoulder": 12, "l_elbow": 13, "r_elbow": 14,
    "l_wrist": 15, "r_wrist": 16, "l_hip": 23, "r_hip": 24,
    "l_knee": 25, "r_knee": 26, "l_ankle": 27, "r_ankle": 28,
    "l_heel": 29, "r_heel": 30, "l_toe": 31, "r_toe": 32,
}

_MODEL_ENV = "RUNGAP_POSE_MODEL"
_MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
              "pose_landmarker_full/float16/latest/pose_landmarker_full.task")


@register
class MediaPipePoseEstimator(PoseEstimator):
    name = "mediapipe"
    provides_mesh = False
    has_metric_scale = True

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path

    def _resolve_model(self) -> str:
        here = os.path.dirname(__file__)
        for c in (self.model_path, os.environ.get(_MODEL_ENV),
                  os.path.join(os.getcwd(), "pose_landmarker.task"),
                  os.path.join(here, "..", "models", "pose_landmarker.task")):
            if c and os.path.isfile(c):
                return c
        raise RuntimeError(
            "姿勢モデル pose_landmarker.task が見つかりません。次からダウンロードし、"
            f"環境変数 {_MODEL_ENV} にパスを設定するか、作業ディレクトリに置いてください。\n  " + _MODEL_URL)

    def estimate(self, frames: FrameSeq, camera: CameraSpec, body: BodySpec) -> Pose3DSeq:
        try:
            import cv2
            import mediapipe as mp
            from mediapipe.tasks import python as mp_py
            from mediapipe.tasks.python import vision
        except ImportError as e:
            raise RuntimeError(
                "mediapipe / opencv が必要です。`pip install -r requirements-models.txt` を実行してください。"
            ) from e
        if not isinstance(frames.frames, str):
            raise RuntimeError("mediapipe アダプタは FrameSeq.frames に動画パス(str)が必要です。")
        model = self._resolve_model()
        from rungap_pipeline.io_video import iter_frames

        opts = vision.PoseLandmarkerOptions(
            base_options=mp_py.BaseOptions(model_asset_path=model),
            running_mode=vision.RunningMode.VIDEO)
        landmarker = vision.PoseLandmarker.create_from_options(opts)

        J = NUM_JOINTS
        joints_list, conf_list = [], []
        try:
            for i, bgr in enumerate(iter_frames(frames.frames)):
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                ts_ms = int(i / frames.fps * 1000)
                res = landmarker.detect_for_video(mp_img, ts_ms)
                jf = np.zeros((J, 3)); cf = np.zeros(J)
                if res.pose_world_landmarks:
                    Pt = res.pose_world_landmarks[0]
                    for name, mpi in _MP.items():
                        p = Pt[mpi]
                        jf[idx(name)] = (p.x, -p.y, p.z)   # y: 上を正に
                        cf[idx(name)] = getattr(p, "visibility", 0.8)
                    nose = np.array((Pt[0].x, -Pt[0].y, Pt[0].z))
                    pelvis = (jf[idx("l_hip")] + jf[idx("r_hip")]) / 2
                    chest = (jf[idx("l_shoulder")] + jf[idx("r_shoulder")]) / 2
                    jf[idx("pelvis")] = pelvis
                    jf[idx("chest")] = chest
                    jf[idx("neck")] = chest + 0.3 * (nose - chest)
                    jf[idx("head")] = nose
                    for n in ("pelvis", "chest", "neck", "head"):
                        cf[idx(n)] = 0.8
                joints_list.append(jf); conf_list.append(cf)
        finally:
            landmarker.close()

        if not joints_list:
            raise RuntimeError("動画からフレームを取得できませんでした。パス・形式をご確認ください。")
        return Pose3DSeq(np.stack(joints_list), np.stack(conf_list), self.has_metric_scale)
