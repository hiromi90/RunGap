"""評価モード（Phase 0 をコード化）：パイプライン出力と参照値の一致度。"""
from __future__ import annotations

THRESHOLDS = {"knee_angle": 5.0, "ground_contact_time": 20.0,
              "trunk_lean": None, "arm_swing": None,
              "stride_length": None, "pitch": None}


def compare_to_reference(actual_metrics: dict, reference: dict):
    rows = []
    for key, ref in reference.items():
        metric, side = key
        act = actual_metrics[key]["value"]
        diff = round(act - ref, 1)
        thr = THRESHOLDS.get(metric)
        judge = "—" if thr is None else ("採用見込み" if abs(diff) <= thr else "要注意")
        rows.append({"metric": metric, "side": side, "pipeline": act,
                     "reference": ref, "diff": diff, "judge": judge})
    return rows
