"""出力スキーマ（データモデル設計の metric_comparisons に一致）。
中立性：score/rank/grade などの評価フィールドを持たない。"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, List
import json


@dataclass
class MetricComparison:
    metric: str
    side: str
    ideal_value: float
    actual_value: float
    diff: float
    unit: str
    confidence: str
    phase_breakdown: Optional[dict] = None


@dataclass
class PipelineResult:
    model_variant: str
    status: str
    metrics: List[MetricComparison] = field(default_factory=list)

    def to_dict(self):
        return {"model_variant": self.model_variant, "status": self.status,
                "metrics": [asdict(m) for m in self.metrics]}

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
