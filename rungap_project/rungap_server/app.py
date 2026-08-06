"""FastAPI アプリ本体。ローカル起動：uvicorn rungap_server.app:app --reload"""
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from rungap_server.store import DB, DEMO_USER, new_id, lock
from rungap_server.models import (
    BodyProfileIn, IdealMotionIn, AnalysisIn, ReferenceIn,
)
from rungap_server.jobs import enqueue
from rungap_pipeline.evaluation.compare import compare_to_reference

app = FastAPI(title="RunGap (local dev server)", version="0.1.0-local")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])
API = "/api/v1"
_WEB = os.path.join(os.path.dirname(__file__), "web", "index.html")


@app.get("/", response_class=HTMLResponse)
def index():
    with open(_WEB, encoding="utf-8") as f:
        return f.read()


@app.get("/healthz")
def healthz():
    return {"status": "ok", "mode": "local", "storage": "in-memory"}


# ---- 体型プロファイル（F1）----
@app.post(f"{API}/users/me/body-profiles", status_code=201)
def create_body_profile(inp: BodyProfileIn):
    bid = new_id("bp")
    rec = {"id": bid, "user_id": DEMO_USER, **inp.model_dump(), "model_params": {}}
    with lock():
        DB["body_profiles"][bid] = rec
    return rec


@app.get(f"{API}/users/me/body-profiles")
def list_body_profiles():
    return [r for r in DB["body_profiles"].values() if r["user_id"] == DEMO_USER]


# ---- 理想モーション（F2）----
@app.post(f"{API}/ideal-motions", status_code=201)
def create_ideal_motion(inp: IdealMotionIn):
    iid = new_id("ideal")
    with lock():
        DB["ideal_motions"][iid] = {"id": iid, "user_id": DEMO_USER, "name": inp.name}
    return {"id": iid, "name": inp.name}


@app.get(f"{API}/ideal-motions")
def list_ideal_motions():
    return [{"id": r["id"], "name": r["name"]}
            for r in DB["ideal_motions"].values() if r["user_id"] == DEMO_USER]


# ---- 解析（F3・F4・F5）----
@app.post(f"{API}/analyses", status_code=202)
def create_analysis(inp: AnalysisIn):
    if inp.ideal_motion_id not in DB["ideal_motions"]:
        raise HTTPException(404, "ideal_motion が見つかりません")
    if inp.body_profile_id not in DB["body_profiles"]:
        raise HTTPException(404, "body_profile が見つかりません")
    aid, jid = new_id("an"), new_id("job")
    with lock():
        DB["jobs"][jid] = {"id": jid, "analysis_id": aid, "status": "queued",
                           "progress": 0}
        DB["analyses"][aid] = {
            "id": aid, "user_id": DEMO_USER, "job_id": jid,
            "ideal_motion_id": inp.ideal_motion_id,
            "body_profile_id": inp.body_profile_id,
            "environment": inp.environment.model_dump(),
            "model_variant": inp.model_variant,
            "status": "queued", "result": None, "memo": None,
        }
    enqueue(aid)
    return {"analysis_id": aid, "job_id": jid, "status": "queued"}


@app.get(f"{API}/jobs/{{job_id}}")
def get_job(job_id: str):
    j = DB["jobs"].get(job_id)
    if not j:
        raise HTTPException(404, "job が見つかりません")
    return {"status": j["status"], "progress": j["progress"]}


@app.get(f"{API}/analyses/{{analysis_id}}")
def get_analysis(analysis_id: str):
    a = DB["analyses"].get(analysis_id)
    if not a:
        raise HTTPException(404, "analysis が見つかりません")
    return {"id": a["id"], "status": a["status"],
            "environment": a["environment"], "memo": a["memo"],
            "metrics": (a["result"] or {}).get("metrics", [])}


@app.get(f"{API}/analyses")
def list_analyses():
    return [{"id": a["id"], "status": a["status"],
             "ideal_motion_id": a["ideal_motion_id"]}
            for a in DB["analyses"].values() if a["user_id"] == DEMO_USER]


# ---- 評価モード（Phase 0：参照との一致度）----
@app.post(f"{API}/analyses/{{analysis_id}}/evaluate")
def evaluate(analysis_id: str, inp: ReferenceIn):
    a = DB["analyses"].get(analysis_id)
    if not a or a.get("_actual") is None:
        raise HTTPException(404, "解析が未完了か、見つかりません")
    actual = a["_actual"]
    if inp.reference:
        ref = {}
        for k, v in inp.reference.items():
            metric, _, side = k.partition("|")
            ref[(metric, side or "none")] = v
    else:  # 既定のダミー参照
        gr = actual[("ground_contact_time", "right")]["value"]
        gl = actual[("ground_contact_time", "left")]["value"]
        ref = {("knee_angle", "none"): 151.0,
               ("ground_contact_time", "right"): gr - 7,
               ("ground_contact_time", "left"): gl - 22}
    return {"rows": compare_to_reference(actual, ref)}
