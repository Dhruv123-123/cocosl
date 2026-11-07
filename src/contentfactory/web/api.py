"""JSON API for automation (n8n, cron, scripts). Same auth as the dashboard:
send `Authorization: Bearer <DASHBOARD_TOKEN>`.

Long jobs (produce, idea generation, daily) run synchronously by default so a
cron `curl` gets the result; pass `"wait": false` to queue them and poll
GET /api/jobs/{id}.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..pipeline import Factory
from . import actions, queries
from .deps import get_factory

router = APIRouter(prefix="/api", tags=["api"])


class GenerateIn(BaseModel):
    brand: str
    n: int = Field(10, ge=1, le=50)
    online: bool = True
    wait: bool = True


class ProduceIn(BaseModel):
    notes: str = ""
    wait: bool = True


class ApproveIn(BaseModel):
    verified: list[Any] = Field(default_factory=list,
                                description="Index or exact text of every claims_to_verify item you fact-checked")
    notes: str = ""
    schedule: bool = False
    platforms: list[str] | None = None


class RejectIn(BaseModel):
    reason: str


class ScheduleIn(BaseModel):
    platforms: list[str] | None = None
    at: str | None = Field(None, description="ISO 8601 with offset; default = next free slot per platform")


class DailyIn(BaseModel):
    brand: str
    n_ideas: int = 8
    n_produce: int = 2
    online: bool = True
    wait: bool = True


def _jobs(request: Request):
    return request.app.state.jobs


def _job_reply(request: Request, job, wait: bool):
    """Queued: 202. Waited and finished: 200. Waited and failed: 500 with the error."""
    if not wait:
        return JSONResponse({"job": job.as_dict()}, status_code=202)
    _jobs(request).wait(job.id, timeout=3600)
    if job.status == "failed":
        return JSONResponse({"error": job.error, "job": job.as_dict()}, status_code=500)
    return {"job": job.as_dict()}


def _post_json(post: dict) -> dict:
    return {**post, "claims_to_verify": queries.claims(post)}


@router.get("/health")
def health(request: Request) -> dict:
    """Unauthenticated liveness probe; reveals nothing beyond 'up'."""
    request.app.state.factory.db.scalar("SELECT 1")
    return {"ok": True}


@router.get("/status")
def status(factory: Factory = Depends(get_factory)) -> dict:
    """Worker heartbeat, publishing and render queues, and anything that needs a human."""
    from ..health import system_status
    return system_status(factory)


@router.get("/posts")
def list_posts(status: str | None = None, brand: str | None = None, limit: int = 50,
               factory: Factory = Depends(get_factory)) -> dict:
    sql, params = "SELECT * FROM posts WHERE 1=1", []
    if status:
        statuses = [s.strip() for s in status.split(",") if s.strip()]
        sql += f" AND status IN ({','.join('?' for _ in statuses)})"
        params += statuses
    if brand:
        sql += " AND brand = ?"
        params.append(brand)
    rows = factory.db.query(sql + " ORDER BY id DESC LIMIT ?", [*params, max(1, min(limit, 500))])
    return {"posts": [_post_json(p) for p in rows]}


@router.get("/posts/{post_id}")
def get_post(post_id: int, factory: Factory = Depends(get_factory)) -> dict:
    post = queries.require_post(factory, post_id)
    return {"post": _post_json(post), "publications": queries.publications_for(factory, post_id)}


@router.post("/ideas/generate")
def generate(body: GenerateIn, request: Request, factory: Factory = Depends(get_factory)) -> dict:
    job = actions.start_ideas(factory, _jobs(request), body.brand, body.n, body.online)
    return _job_reply(request, job, body.wait)


@router.post("/ideas/{idea_id}/produce")
def produce(idea_id: int, request: Request, body: ProduceIn | None = None,
            factory: Factory = Depends(get_factory)) -> dict:
    body = body or ProduceIn()
    job = actions.start_produce(factory, _jobs(request), idea_id, notes=body.notes)
    return _job_reply(request, job, body.wait)


@router.post("/posts/{post_id}/approve")
def approve(post_id: int, body: ApproveIn, factory: Factory = Depends(get_factory)) -> dict:
    post = actions.approve(factory, post_id, body.verified, notes=body.notes, actor="api")
    out: dict = {"post": _post_json(post)}
    if body.schedule:
        out["publications"] = actions.schedule(factory, post_id, body.platforms)
    return out


@router.post("/posts/{post_id}/reject")
def reject(post_id: int, body: RejectIn, factory: Factory = Depends(get_factory)) -> dict:
    actions.reject(factory, post_id, body.reason, actor="api")
    return {"post": _post_json(factory.db.get("posts", post_id))}


@router.post("/posts/{post_id}/schedule")
def schedule(post_id: int, body: ScheduleIn | None = None, factory: Factory = Depends(get_factory)) -> dict:
    body = body or ScheduleIn()
    ids = actions.schedule(factory, post_id, body.platforms, body.at)
    return {"publications": [factory.db.get("publications", i) for i in ids]}


@router.post("/publish/due")
def publish_due(factory: Factory = Depends(get_factory)) -> dict:
    return {"dry_run": factory.settings.dry_run, "results": factory.publish_due()}


@router.post("/metrics/collect")
def collect_metrics(factory: Factory = Depends(get_factory)) -> dict:
    return {"snapshots": factory.collect_metrics()}


@router.post("/daily")
def daily(body: DailyIn, request: Request, factory: Factory = Depends(get_factory)) -> dict:
    job = actions.start_daily(factory, _jobs(request), body.brand, n_ideas=body.n_ideas,
                              n_produce=body.n_produce, online=body.online)
    return _job_reply(request, job, body.wait)


@router.get("/jobs")
def list_jobs(request: Request) -> dict:
    return {"jobs": [j.as_dict() for j in _jobs(request).all()]}


@router.get("/jobs/{job_id}")
def get_job(job_id: int, request: Request) -> dict:
    job = _jobs(request).get(job_id)
    if not job:
        raise KeyError(f"No job #{job_id}")
    return {"job": job.as_dict()}
