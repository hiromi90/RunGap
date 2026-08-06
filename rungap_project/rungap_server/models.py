"""リクエスト／レスポンスのスキーマ（Pydantic）。"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class BodyProfileIn(BaseModel):
    height_cm: float = Field(gt=0)
    weight_kg: float = Field(gt=0)
    skeletal_muscle_pct: float = Field(ge=0)
    body_fat_pct: float = Field(ge=0)
    inseam_cm: float = Field(gt=0)
    sitting_height_cm: Optional[float] = None
    shoulder_width_cm: Optional[float] = None
    foot_length_cm: Optional[float] = None


class IdealMotionIn(BaseModel):
    name: str


class EnvironmentIn(BaseModel):
    wind_speed_kmh: float = Field(ge=0)           # 符号なし
    wind_direction: Literal["tailwind", "headwind", "cross_right", "cross_left"]
    pace_sec_per_km: int = Field(gt=0)
    surface: Literal["tartan", "dirt", "asphalt"] = "tartan"
    slope_pct: float = 0.0
    temperature_c: float = 20.0


class AnalysisIn(BaseModel):
    ideal_motion_id: str
    body_profile_id: str
    environment: EnvironmentIn
    model_variant: str = "dummy"


class ReferenceIn(BaseModel):
    # {"metric|side": value} 例：{"knee_angle|none": 151, "ground_contact_time|left": 228}
    reference: dict[str, float] = {}
