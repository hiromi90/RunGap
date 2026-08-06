"""ダミーアダプタ：実モデルの代わりに合成した歩行モーションを返す。"""
from __future__ import annotations
import numpy as np
from rungap_pipeline.estimators.base import (
    PoseEstimator, FrameSeq, CameraSpec, BodySpec, Pose3DSeq, register,
)
from rungap_pipeline.skeleton.canonical import NUM_JOINTS, idx


@register
class DummyPoseEstimator(PoseEstimator):
    name = "dummy"
    provides_mesh = False
    has_metric_scale = False

    def __init__(self, foot_cycle_hz: float = 1.50, v: float = 4.95,
                 trunk_deg: float = 5.0, arm_deg: float = 58.0,
                 contact_ratio: float = 0.345, knee_bend: float = 0.11,
                 seed: int = 2):
        self.fch = foot_cycle_hz
        self.v = v
        self.trunk_deg = trunk_deg
        self.arm_deg = arm_deg
        self.contact_ratio = contact_ratio
        self.knee_bend = knee_bend
        self.seed = seed

    def estimate(self, frames: FrameSeq, camera: CameraSpec, body: BodySpec) -> Pose3DSeq:
        T, fps = frames.num_frames, frames.fps
        J = NUM_JOINTS
        t = np.arange(T) / fps
        P = fps / self.fch
        joints = np.zeros((T, J, 3))
        conf = np.full((T, J), 0.9)

        tl = np.radians(self.trunk_deg)
        torso, neck_ext = 0.55, 0.68
        px = self.v * t
        py = 1.0 + 0.02 * np.sin(2 * np.pi * self.fch * 2 * t)
        pelvis = np.stack([px, py, np.zeros(T)], axis=1)
        d_up = np.array([np.sin(tl), np.cos(tl), 0.0])
        chest = pelvis + torso * d_up
        neck = pelvis + neck_ext * d_up
        head = pelvis + (neck_ext + 0.12) * d_up
        joints[:, idx("pelvis")] = pelvis
        joints[:, idx("chest")] = chest
        joints[:, idx("neck")] = neck
        joints[:, idx("head")] = head

        for side, zc in (("l", +1), ("r", -1)):
            sh = chest + np.array([0, 0, zc * 0.18])
            ph = ((np.arange(T) + (0 if side == "r" else P * 0.5)) % P) / P
            sw = np.radians(self.arm_deg / 2) * np.sin(2 * np.pi * ph)
            dirv = np.stack([np.sin(sw), -np.cos(sw), np.zeros(T)], axis=1)
            elbow = sh + 0.28 * dirv
            wrist = elbow + 0.26 * dirv
            joints[:, idx(f"{side}_shoulder")] = sh
            joints[:, idx(f"{side}_elbow")] = elbow
            joints[:, idx(f"{side}_wrist")] = wrist

        hipw = 0.12
        for side, zc, off in (("l", +1, P * 0.5), ("r", -1, 0.0)):
            hip = pelvis + np.array([0, 0, zc * hipw])
            ph = ((np.arange(T) + off) % P) / P
            footy = np.where(ph < self.contact_ratio, 0.0,
                             0.16 * np.sin(np.pi * (ph - self.contact_ratio) /
                                           (1 - self.contact_ratio)))
            footx = 0.33 * np.cos(2 * np.pi * ph)
            ankle = np.stack([hip[:, 0] + footx, footy, hip[:, 2]], axis=1)
            mid = (hip + ankle) / 2
            bend = self.knee_bend * (1 + 0.5 * np.sin(2 * np.pi * ph))
            knee = mid + np.stack([bend, np.zeros(T), np.zeros(T)], axis=1)
            toe = ankle + np.array([0.08, 0, 0])
            heel = ankle + np.array([-0.08, 0, 0])
            joints[:, idx(f"{side}_hip")] = hip
            joints[:, idx(f"{side}_knee")] = knee
            joints[:, idx(f"{side}_ankle")] = ankle
            joints[:, idx(f"{side}_toe")] = toe
            joints[:, idx(f"{side}_heel")] = heel
            if side == "l":
                for jn in ("l_hip", "l_knee", "l_ankle", "l_toe", "l_heel"):
                    conf[:, idx(jn)] = 0.5

        return Pose3DSeq(joints=joints, per_joint_conf=conf,
                         metric_scale=self.has_metric_scale)
