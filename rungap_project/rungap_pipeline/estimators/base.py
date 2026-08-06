"""共通インターフェース。下流は Pose3DSeq（共通スケルトン）だけを見る。"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Type
import numpy as np


@dataclass
class FrameSeq:
    frames: object
    fps: float
    num_frames: int


@dataclass
class CameraSpec:
    view: str = "side"
    height_m: Optional[float] = None


@dataclass
class BodySpec:
    height_cm: float
    inseam_cm: float
    weight_kg: float
    segments: dict = field(default_factory=dict)


@dataclass
class Pose3DSeq:
    joints: np.ndarray
    per_joint_conf: np.ndarray
    metric_scale: bool
    mesh: object = None


class PoseEstimator(ABC):
    name: str = "base"
    provides_mesh: bool = False
    has_metric_scale: bool = False

    @abstractmethod
    def estimate(self, frames: FrameSeq, camera: CameraSpec, body: BodySpec) -> Pose3DSeq:
        ...


REGISTRY: Dict[str, Type[PoseEstimator]] = {}


def register(cls):
    REGISTRY[cls.name] = cls
    return cls


def get_estimator(name: str) -> PoseEstimator:
    if name not in REGISTRY:
        raise KeyError(f"未登録のモデル: {name!r}. 登録済み: {list(REGISTRY)}")
    return REGISTRY[name]()
