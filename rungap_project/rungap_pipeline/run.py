"""端から端まで通す実演。実行：/home/claude で `python3 -m rungap_pipeline.run`"""
from __future__ import annotations
from rungap_pipeline.estimators.base import FrameSeq, CameraSpec, BodySpec, get_estimator
from rungap_pipeline.estimators.dummy_adapter import DummyPoseEstimator
from rungap_pipeline.pipeline.orchestrator import run_pipeline, run_metrics
from rungap_pipeline.evaluation.compare import compare_to_reference


def main():
    body = BodySpec(height_cm=172, inseam_cm=80, weight_kg=58)
    camera = CameraSpec(view="side", height_m=1.2)
    frames = FrameSeq(frames=None, fps=60, num_frames=180)

    ideal_est = DummyPoseEstimator(foot_cycle_hz=1.55, v=5.15, trunk_deg=8.0,
                                   arm_deg=62.0, contact_ratio=0.335,
                                   knee_bend=0.13, seed=1)
    _, ideal_metrics = run_metrics(ideal_est, frames, camera, body)

    estimator = get_estimator("dummy")
    result, actual = run_pipeline(estimator, frames, camera, body,
                                  ideal_metrics=ideal_metrics, model_variant="dummy")

    print("=== 解析結果（metric_comparisons：理想／実測／差／信頼度）===")
    print(result.to_json())

    reference = {
        ("knee_angle", "none"): 151.0,
        ("ground_contact_time", "right"): actual[("ground_contact_time", "right")]["value"] - 7,
        ("ground_contact_time", "left"): actual[("ground_contact_time", "left")]["value"] - 22,
    }
    print("\n=== 評価モード（参照との一致度：Phase 0）===")
    print(f"{'指標':<20}{'側':<7}{'推定':>7}{'参照':>7}{'差':>7}  判定")
    for r in compare_to_reference(actual, reference):
        print(f"{r['metric']:<20}{r['side']:<7}{r['pipeline']:>7}{r['reference']:>7}{r['diff']:>7}  {r['judge']}")


if __name__ == "__main__":
    main()
