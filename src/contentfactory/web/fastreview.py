"""Fast review (`/review/fast`): one post at a time, keyboard first, so a 15-minute session clears more.

Keys:  A approve (and schedule)  ·  R reject (asks why)  ·  E edit caption  ·  1-9 tick claim N  ·  C tick all claims
       J / K next / previous     ·  N pass native review  ·  L pass legal review  ·  ? help
Batch: "Approve the week" approves every post drafted that week that's ready: not blocked, every review it needs
passed (`factory review-gate`), and every claim already ticked here (ticks are saved as you press them). Anything
else is listed with the reason, never approved silently.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse

from ..pipeline import Factory
from .. import review as gate
from . import actions, queries
from .deps import get_factory

router = APIRouter(include_in_schema=False)


def _ticked(post: dict) -> set[str]:
    return {str(x) for x in ((post.get("meta") or {}).get("claims_ticked") or [])}


def _queue(factory: Factory, brand: str | None) -> list[dict]:
    return queries.review_queue(factory, brand)


def ready(factory: Factory, post: dict) -> str:
    """'' when the post can be approved without more input, else why not."""
    if post["status"] == "blocked":
        return "blocked by a guardrail"
    waiting = gate.pending(post, factory.brands().get(post["brand"]))
    if waiting:
        return "needs " + ", ".join(w.replace("_", " ") for w in waiting)
    missing = actions.unverified_claims(post, _ticked(post))
    if missing:
        return f"{len(missing)} claim(s) not ticked"
    if factory.render_pending(post["id"]):
        return "still rendering"
    return ""


def week_of(post: dict) -> date:
    d = datetime.fromisoformat(str(post["created_at"])[:19]).date()
    return d - timedelta(days=d.weekday())


@router.get("/review/fast")
def fast_page(request: Request, brand: str | None = None, i: int = 0,
              factory: Factory = Depends(get_factory)) -> HTMLResponse:
    from .pages import _post_view, render
    items = _queue(factory, brand)
    i = max(0, min(i, len(items) - 1)) if items else 0
    view = _post_view(factory, request, items[i]) if items else None
    weeks: dict = {}
    for p in items:
        w = weeks.setdefault(week_of(p).isoformat(), {"total": 0, "ready": 0})
        w["total"] += 1
        w["ready"] += 0 if ready(factory, p) else 1
    post = items[i] if items else None
    brand_obj = factory.brands().get(post["brand"]) if post else None
    return render(request, "review_fast.html", it=view, i=i, n=len(items), brand=brand or "", brands=factory.brands(),
                  ticked=sorted(_ticked(post)) if post else [], why=ready(factory, post) if post else "",
                  gate_status=gate.status(post, brand_obj) if post else "", needs=gate.pending(post, brand_obj) if post else [],
                  weeks=sorted(weeks.items()))


@router.post("/review/fast/{post_id}/tick")
def tick(post_id: int, claims: list[str] = Form(default=[]), factory: Factory = Depends(get_factory)):
    post = queries.require_post(factory, post_id)
    meta = dict(post.get("meta") or {})
    meta["claims_ticked"] = sorted({c for c in claims if c.isdigit()})
    factory.db.update("posts", post_id, {"meta": meta})
    return JSONResponse({"ok": True, "ticked": meta["claims_ticked"],
                         "why": ready(factory, factory.db.get("posts", post_id))})


@router.post("/review/fast/{post_id}/pass")
def pass_review(post_id: int, request: Request, stage: str = Form(...), by: str = Form(""),
                factory: Factory = Depends(get_factory)):
    from .pages import back
    gate.pass_stage(factory, post_id, stage, by=by or "dashboard")
    return back(request, "/review/fast", msg=f"Post #{post_id}: {stage.replace('_', ' ')} passed")


@router.post("/review/fast/approve-week")
def approve_week(request: Request, week: str = Form(...), brand: str = Form(""), and_schedule: str = Form(""),
                 factory: Factory = Depends(get_factory)):
    from .pages import back
    done, skipped = [], []
    for p in _queue(factory, brand or None):
        if week_of(p).isoformat() != week:
            continue
        why = ready(factory, p)
        if why:
            skipped.append(f"#{p['id']} ({why})")
            continue
        try:
            actions.approve(factory, p["id"], _ticked(p), notes=f"batch approve, week of {week}")
            if and_schedule:
                actions.schedule(factory, p["id"])
            done.append(p["id"])
        except (PermissionError, ValueError, RuntimeError) as e:
            skipped.append(f"#{p['id']} ({e})")
    msg = f"Approved {len(done)} post(s) from the week of {week}" + (" and scheduled them" if and_schedule and done else "")
    return back(request, "/review/fast", msg=msg, err=("Skipped: " + "; ".join(skipped[:8])) if skipped else "")
