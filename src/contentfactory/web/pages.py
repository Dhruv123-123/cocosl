"""Server-rendered dashboard pages and their form handlers.

Every form POST redirects back (303) with ?msg= or ?err= so pages work with
plain HTML forms and no JavaScript.
"""
from __future__ import annotations

import hmac
from urllib.parse import parse_qsl, urlencode, urlparse

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..pipeline import Factory
from . import actions, queries
from .auth import COOKIE, LoginLimiter, safe_next, session_value
from .deps import get_factory, templates

router = APIRouter(include_in_schema=False)
limiter = LoginLimiter()

ENV_CHECKLIST = [
    ("DASHBOARD_TOKEN", "Protects this dashboard; required before exposing it beyond localhost"),
    ("ANTHROPIC_API_KEY", "Claude for ideas and scripts (otherwise the offline placeholder writer runs)"),
    ("PUBLIC_MEDIA_BASE_URL", "HTTPS base URL where rendered media is reachable (Instagram fetches from it)"),
    ("FACTORY_DRY_RUN", "Set to 0 to actually publish; default 1 records what would be posted"),
    ("FACTORY_TTS", "Voice provider: auto | piper | espeak | elevenlabs | openai | silent"),
    ("FACTORY_IMAGES", "Image provider: auto | comfyui | openai | replicate | cards"),
]


def back(request: Request, default: str = "/", msg: str = "", err: str = "", anchor: str = "") -> RedirectResponse:
    """303 to the referring page (same host only) with a flash message."""
    ref = urlparse(request.headers.get("referer", ""))
    if ref.path and (not ref.netloc or ref.netloc == request.headers.get("host")):
        path, query = ref.path, [(k, v) for k, v in parse_qsl(ref.query) if k not in ("msg", "err")]
    else:
        path, query = default, []
    if msg:
        query.append(("msg", msg))
    if err:
        query.append(("err", err))
    url = path + (f"?{urlencode(query)}" if query else "") + (f"#{anchor}" if anchor else "")
    return RedirectResponse(url, status_code=303)


def render(request: Request, name: str, status_code: int = 200, **ctx) -> HTMLResponse:
    return templates.TemplateResponse(request, name, ctx, status_code=status_code)


def _jobs(request: Request):
    return request.app.state.jobs


def _brand_choice(factory: Factory, brand: str | None) -> tuple[dict, str]:
    brands = factory.brands()
    if brand and brand not in brands:
        raise KeyError(f"Unknown brand '{brand}'")
    return brands, brand or next(iter(brands), "")


def _post_view(factory: Factory, request: Request, post: dict) -> dict:
    """Everything the review card / detail page needs for one post."""
    checks = (post.get("checks") or {}).get("checks", [])
    order = {"block": 0, "warn": 1, "ok": 2}
    return {
        "post": post,
        "script": post.get("script") or {},
        "assets": post.get("assets") or {},
        "claims": queries.claims(post),
        "checks": sorted(checks, key=lambda c: order.get(c.get("level"), 3)),
        "check_status": (post.get("checks") or {}).get("status", ""),
        "editor": (post.get("meta") or {}).get("editor") or {},
        "job": _jobs(request).active_for("post", post["id"]),
        "pubs": queries.publications_for(factory, post["id"]),
    }


# --------------------------------------------------------------------------- auth
@router.get("/login")
def login_form(request: Request, next: str = "/") -> HTMLResponse:
    return render(request, "login.html", next=safe_next(next), error="")


@router.post("/login")
def login(request: Request, token: str = Form(""), next: str = Form("/")):
    expected = request.app.state.factory.settings.dashboard_token
    key = request.client.host if request.client else "?"
    if not expected:
        return RedirectResponse(safe_next(next), status_code=303)
    if limiter.blocked(key):
        return render(request, "login.html", 429, next=safe_next(next),
                      error="Too many attempts. Wait 10 minutes and try again.")
    if not hmac.compare_digest(token.strip().encode(), expected.encode()):
        limiter.fail(key)
        return render(request, "login.html", 401, next=safe_next(next), error="That token didn't match.")
    resp = RedirectResponse(safe_next(next), status_code=303)
    resp.set_cookie(COOKIE, session_value(expected), max_age=30 * 86400, httponly=True, samesite="lax",
                    secure=request.url.scheme == "https", path="/")
    return resp


@router.post("/logout")
def logout() -> RedirectResponse:
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(COOKIE, path="/")
    return resp


# --------------------------------------------------------------------------- overview
@router.get("/")
def overview(request: Request, factory: Factory = Depends(get_factory)) -> HTMLResponse:
    return render(
        request, "overview.html",
        counts=queries.status_counts(factory), k=queries.kpis(factory),
        upcoming=queries.upcoming(factory), activity=queries.activity(factory, 12),
        blocked=queries.blocked_posts(factory), creds=queries.credentials(factory),
        llm_provider=factory.llm.provider, tz=queries.display_tz(factory),
    )


# --------------------------------------------------------------------------- ideas
@router.get("/ideas")
def ideas_page(request: Request, brand: str | None = None, show_rejected: bool = False,
               factory: Factory = Depends(get_factory)) -> HTMLResponse:
    brands, current = _brand_choice(factory, brand)
    ideas = queries.ideas_for(factory, current, show_rejected) if current else []
    producing = {j.entity_id: j for j in _jobs(request).running() if j.entity == "idea"}
    recent_jobs = [j for j in _jobs(request).all() if j.kind in ("ideas", "produce")][:8]
    return render(request, "ideas.html", brands=brands, brand=current, ideas=ideas, producing=producing,
                  recent_jobs=recent_jobs, show_rejected=show_rejected)


@router.post("/ideas/generate")
def ideas_generate(request: Request, brand: str = Form(...), n: int = Form(8), online: str = Form(""),
                   factory: Factory = Depends(get_factory)):
    job = actions.start_ideas(factory, _jobs(request), brand, n, online == "1")
    return back(request, f"/ideas?brand={brand}", msg=f"Generating {n} ideas (job #{job.id}). Refresh in a moment.")


@router.post("/ideas/{idea_id}/status")
def idea_status(idea_id: int, request: Request, status: str = Form(...),
                factory: Factory = Depends(get_factory)):
    actions.set_idea_status(factory, idea_id, status)
    return back(request, "/ideas", msg=f"Idea #{idea_id} {status}", anchor=f"idea-{idea_id}")


@router.post("/ideas/{idea_id}/produce")
def idea_produce(idea_id: int, request: Request, notes: str = Form(""),
                 factory: Factory = Depends(get_factory)):
    job = actions.start_produce(factory, _jobs(request), idea_id, notes=notes)
    return back(request, "/ideas", msg=f"Producing idea #{idea_id} (job #{job.id}). It lands in Review when done.",
                anchor=f"idea-{idea_id}")


# --------------------------------------------------------------------------- review
@router.get("/review")
def review_page(request: Request, brand: str | None = None,
                factory: Factory = Depends(get_factory)) -> HTMLResponse:
    posts = [_post_view(factory, request, p) for p in queries.review_queue(factory, brand)]
    failed = factory.db.query("SELECT * FROM posts WHERE status = 'failed' ORDER BY updated_at DESC LIMIT 10")
    return render(request, "review.html", items=posts, failed=failed, brands=factory.brands(), brand=brand or "")


@router.post("/posts/{post_id}/edit")
def post_edit(post_id: int, request: Request, title: str = Form(...), caption: str = Form(...),
              factory: Factory = Depends(get_factory)):
    actions.edit(factory, post_id, title=title.strip(), caption=caption.strip())
    status = factory.db.get("posts", post_id)["status"]
    return back(request, "/review", msg=f"Saved post #{post_id} and re-ran checks: now {status.replace('_', ' ')}",
                anchor=f"post-{post_id}")


@router.post("/posts/{post_id}/approve")
def post_approve(post_id: int, request: Request, verified: list[str] = Form(default=[]), notes: str = Form(""),
                 and_schedule: str = Form(""), factory: Factory = Depends(get_factory)):
    actions.approve(factory, post_id, verified, notes=notes)
    if and_schedule:
        try:
            ids = actions.schedule(factory, post_id)
        except (PermissionError, ValueError, RuntimeError) as e:
            return back(request, "/review", err=f"Approved #{post_id}, but scheduling failed: {e}")
        return back(request, "/review", msg=f"Approved and scheduled post #{post_id} on {len(ids)} platform(s)")
    return back(request, "/review", msg=f"Approved post #{post_id}. Schedule it from its page or the API.")


@router.post("/posts/{post_id}/reject")
def post_reject(post_id: int, request: Request, reason: str = Form(""),
                factory: Factory = Depends(get_factory)):
    actions.reject(factory, post_id, reason)
    return back(request, "/review", msg=f"Rejected post #{post_id}")


@router.post("/posts/{post_id}/rerender")
def post_rerender(post_id: int, request: Request, factory: Factory = Depends(get_factory)):
    job = actions.start_render(factory, _jobs(request), post_id)
    return back(request, "/review", msg=f"Re-rendering post #{post_id} (job #{job.id})", anchor=f"post-{post_id}")


@router.post("/posts/{post_id}/schedule")
def post_schedule(post_id: int, request: Request, factory: Factory = Depends(get_factory)):
    ids = actions.schedule(factory, post_id)
    return back(request, f"/posts/{post_id}", msg=f"Scheduled on {len(ids)} platform(s)")


@router.get("/posts/{post_id}")
def post_detail(post_id: int, request: Request, factory: Factory = Depends(get_factory)) -> HTMLResponse:
    post = queries.require_post(factory, post_id)
    view = _post_view(factory, request, post)
    tz = factory.brand(post["brand"]).cadence.timezone if post["brand"] in factory.brands() else "UTC"
    idea = factory.db.get("ideas", post["idea_id"]) if post.get("idea_id") else None
    return render(request, "post.html", **view, idea=idea, history=queries.post_history(factory, post_id), tz=tz)


# --------------------------------------------------------------------------- calendar / published
@router.get("/calendar")
def calendar_page(request: Request, factory: Factory = Depends(get_factory)) -> HTMLResponse:
    tz, days = queries.calendar_days(factory, 14)
    due = sum(1 for _, pubs in days for p in pubs if queries.is_due(p))
    approved = factory.db.query("SELECT * FROM posts WHERE status = 'approved' ORDER BY updated_at")
    return render(request, "calendar.html", tz=tz, days=days, due=due, approved=approved,
                  is_due=queries.is_due)


@router.post("/publish/due")
def publish_due(request: Request, factory: Factory = Depends(get_factory)):
    results = factory.publish_due()
    ok = sum(1 for r in results if r["status"] != "failed")
    failed = len(results) - ok
    word = "recorded (dry run)" if factory.settings.dry_run else "published"
    if failed:
        return back(request, "/calendar", err=f"{ok} {word}, {failed} failed: "
                    + "; ".join(r.get("error", "")[:120] for r in results if r["status"] == "failed")[:400])
    return back(request, "/calendar", msg=f"{ok} publication(s) {word}" if results else "Nothing due right now")


@router.get("/published")
def published_page(request: Request, factory: Factory = Depends(get_factory)) -> HTMLResponse:
    return render(request, "published.html", pubs=queries.published(factory), tz=queries.display_tz(factory))


@router.post("/metrics/collect")
def metrics_collect(request: Request, factory: Factory = Depends(get_factory)):
    n = factory.collect_metrics()
    return back(request, "/published", msg=f"Captured {n} metrics snapshot(s)")


# --------------------------------------------------------------------------- settings
@router.get("/settings")
def settings_page(request: Request, factory: Factory = Depends(get_factory)) -> HTMLResponse:
    s = factory.settings
    brand_files = {p.stem: p.read_text() for p in sorted(s.brands_dir.glob("*.y*ml"))} if s.brands_dir.exists() else {}
    brand_errors = ""
    try:
        brands = factory.brands()
    except Exception as e:  # show a broken YAML instead of a 500
        brands, brand_errors = {}, f"{type(e).__name__}: {e}"
    env = [(k, bool(s.env(k)), why) for k, why in ENV_CHECKLIST]
    return render(request, "settings.html", s=s, brands=brands, brand_files=brand_files,
                  brand_errors=brand_errors, env=env, creds=queries.credentials(factory),
                  llm_provider=factory.llm.provider, llm_model=factory.llm.model)


@router.get("/report")
def report_page(request: Request, factory: Factory = Depends(get_factory)) -> HTMLResponse:
    from ..reports import weekly_report
    return render(request, "report.html", r=weekly_report(factory))


@router.post("/report/save")
def report_save(factory: Factory = Depends(get_factory)):
    from fastapi.responses import RedirectResponse
    from ..reports import save_report
    path = save_report(factory)
    return RedirectResponse(f"/report?msg=Saved+{path}", status_code=303)
