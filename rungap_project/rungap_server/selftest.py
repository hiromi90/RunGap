"""ローカルサーバーを実サーバー起動なしで検証（TestClient）。
実行：/home/claude で python3 -m rungap_server.selftest"""
from __future__ import annotations
import time
import json
from fastapi.testclient import TestClient
from rungap_server.app import app

c = TestClient(app)


def main():
    assert c.get("/healthz").json()["status"] == "ok"

    bp = c.post("/api/v1/users/me/body-profiles", json={
        "height_cm": 172, "weight_kg": 58, "skeletal_muscle_pct": 42.5,
        "body_fat_pct": 11.0, "inseam_cm": 80}).json()
    print("体型プロファイル:", bp["id"])

    im = c.post("/api/v1/ideal-motions", json={"name": "自己ベスト時の走り"}).json()
    print("理想モーション:", im["id"], im["name"])

    r = c.post("/api/v1/analyses", json={
        "ideal_motion_id": im["id"], "body_profile_id": bp["id"],
        "environment": {"wind_speed_kmh": 2.0, "wind_direction": "tailwind",
                        "pace_sec_per_km": 210}}).json()
    aid, jid = r["analysis_id"], r["job_id"]
    print("解析を投入:", aid, "→ status", r["status"])

    for _ in range(30):
        j = c.get(f"/api/v1/jobs/{jid}").json()
        if j["status"] in ("done", "failed"):
            break
        time.sleep(0.1)
    print("ジョブ完了:", j)

    res = c.get(f"/api/v1/analyses/{aid}").json()
    print("\n=== 解析結果（metric_comparisons）===")
    print(json.dumps(res["metrics"], ensure_ascii=False, indent=2))

    ev = c.post(f"/api/v1/analyses/{aid}/evaluate", json={"reference": {}}).json()
    print("\n=== 評価モード（参照との一致度：Phase 0）===")
    for row in ev["rows"]:
        print(f"{row['metric']:<20}{row['side']:<7}"
              f"推定{row['pipeline']:>7}  参照{row['reference']:>7}  "
              f"差{row['diff']:>6}  {row['judge']}")

    print("\nSELFTEST: PASS")


if __name__ == "__main__":
    main()
