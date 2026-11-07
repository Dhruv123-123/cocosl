"""State-changing operations shared by the HTML pages and the JSON API.

Each wraps a Factory call with the dashboard's own rules (claims must be
verified before approval) and raises PermissionError / KeyError / ValueError,
which app.py maps to 403 / 404 / 400.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from ..db import now_iso
from ..pipeline import Factory
from .jobs import Job, JobRunner
from .queries import claims, require_idea, require_post


def unverified_claims(post: dict, verified: Iterable[Any] | None) -> list[str]:
    """Claims not covered by `verified` (indices, index strings or exact claim texts)."""
    items = claims(post)
    marks = {str(v).strip() for v in (verified or []) if v is not None}
    return [c for i, c in enumerate(items) if str(i) not in marks and c.strip() not in marks]


def approve(factory: Factory, post_id: int, verified: Iterable[Any] | None, notes: str = "",
            actor: str = "human") -> dict:
    post = require_post(factory, post_id)
    missing = unverified_claims(post, verified)
    if missing:
        raise PermissionError(f"{len(missing)} claim(s) not marked as fact-checked: "
                              + "; ".join(m[:80] for m in missing[:3]))
    factory.approve(post_id, actor=actor, notes=notes)
    meta = dict(factory.db.get("posts", post_id).get("meta") or {})
    meta["claims_verified"] = {"claims": claims(post), "by": actor, "at": now_iso()}
    factory.db.update("posts", post_id, {"meta": meta})
    return factory.db.get("posts", post_id)


def schedule(factory: Factory, post_id: int, platforms: list[str] | None = None,
             at: str | None = None) -> list[int]:
    require_post(factory, post_id)
    when = None
    if at:
        try:
            when = datetime.fromisoformat(at.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValueError(f"Bad 'at' timestamp {at!r}; use ISO 8601 like 2026-11-07T17:30:00+00:00") from e
        if when.tzinfo is None:
            raise ValueError("'at' must include a timezone offset")
    return factory.schedule(post_id, platforms=platforms or None, at=when)


def reject(factory: Factory, post_id: int, reason: str, actor: str = "human") -> None:
    require_post(factory, post_id)
    if not reason.strip():
        raise ValueError("Give a reason when rejecting (it trains your future self and the prompts)")
    factory.reject(post_id, reason=reason.strip(), actor=actor)


def edit(factory: Factory, post_id: int, title: str | None, caption: str | None) -> None:
    post = require_post(factory, post_id)
    if post["status"] in ("scheduled", "published"):
        raise PermissionError(f"Post #{post_id} is {post['status']}; edits would not reach the platforms")
    factory.edit(post_id, title=title, caption=caption)


def set_idea_status(factory: Factory, idea_id: int, status: str) -> None:
    if status not in ("new", "approved", "rejected"):
        raise ValueError(f"Unknown idea status {status!r}")
    require_idea(factory, idea_id)
    factory.db.update("ideas", idea_id, {"status": status})
    factory.db.log(f"idea.{status}", "idea", idea_id, actor="human")


# --------------------------------------------------------------------------- background jobs
def start_produce(factory: Factory, jobs: JobRunner, idea_id: int, notes: str = "") -> Job:
    idea = require_idea(factory, idea_id)
    if idea["status"] in ("used", "rejected"):
        raise ValueError(f"Idea #{idea_id} is {idea['status']}")
    running = jobs.active_for("idea", idea_id)
    if running:
        return running
    return jobs.submit("produce", f"Produce idea #{idea_id}: {idea['title'][:60]}",
                       lambda: {"post_id": factory.produce(idea_id, notes=notes)}, "idea", idea_id)


def start_render(factory: Factory, jobs: JobRunner, post_id: int) -> Job:
    post = require_post(factory, post_id)
    if post["status"] in ("scheduled", "published"):
        raise PermissionError(f"Post #{post_id} is {post['status']}; re-rendering would not update the platforms")
    running = jobs.active_for("post", post_id)
    if running:
        return running
    return jobs.submit("render", f"Re-render post #{post_id}",
                       lambda: {"files": len(factory.render(post_id).get("provenance", []))}, "post", post_id)


def start_ideas(factory: Factory, jobs: JobRunner, brand: str, n: int, online: bool) -> Job:
    factory.brand(brand)  # KeyError for unknown brands, before queueing
    if not 1 <= n <= 50:
        raise ValueError("n must be between 1 and 50")
    return jobs.submit("ideas", f"Generate {n} ideas for {brand}",
                       lambda: {"idea_ids": factory.ideas(brand, n=n, online=online)}, "brand", brand)


def start_daily(factory: Factory, jobs: JobRunner, brand: str, **kwargs: Any) -> Job:
    factory.brand(brand)
    return jobs.submit("daily", f"Daily run for {brand}", lambda: factory.daily(brand, **kwargs), "brand", brand)
