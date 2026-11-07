"""Dashboard routes for the community inbox (mount with app.include_router(router)).

GET  /inbox                          filter by brand / status / category
POST /inbox/collect                  fetch new comments (background job)
POST /inbox/draft                    draft replies for new comments (background job)
POST /inbox/{id}/send                send the (edited) reply: the only path that replies
POST /inbox/{id}/save                save an edited draft without sending
POST /inbox/{id}/redraft             ask Claude for a fresh draft
POST /inbox/{id}/status              ignore | flag | new (restore)
POST /inbox/{id}/idea                save the comment as an idea
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from ..pipeline import Factory
from ..publish.base import PublishError
from ..web.deps import get_factory
from ..web.pages import back, render
from . import service, store

router = APIRouter(include_in_schema=False)

STATUS_TABS = [("", "To do"), ("drafted", "Drafted"), ("new", "New"), ("flagged", "Flagged"),
               ("replied", "Replied"), ("ignored", "Ignored"), ("all", "All")]


@router.get("/inbox")
def inbox_page(request: Request, brand: str = "", status: str = "", category: str = "",
               factory: Factory = Depends(get_factory)) -> HTMLResponse:
    brands = factory.brands()
    if brand and brand not in brands:
        raise KeyError(f"Unknown brand '{brand}'")
    if status and status not in (*store.STATUSES, "all"):
        raise ValueError(f"Unknown status '{status}'")
    if category and category not in store.CATEGORIES:
        raise ValueError(f"Unknown category '{category}'")
    items = store.inbox(factory.db, brand=brand, status=status, category=category)
    s = factory.settings
    return render(request, "inbox.html", items=items, brands=brands, brand=brand, status=status,
                  category=category, counts=store.counts(factory.db, brand), tabs=STATUS_TABS,
                  categories=store.CATEGORY_LABELS, limit=service.MAX_REPLIES_PER_HOUR,
                  sent_hour={p: store.replies_last_hour(factory.db, p) for p in ("instagram", "youtube")},
                  dry_run=s.dry_run)


def _jobs(request: Request):
    return request.app.state.jobs


@router.post("/inbox/collect")
def inbox_collect(request: Request, factory: Factory = Depends(get_factory)):
    job = _jobs(request).submit("comments", "Fetch comments", lambda: service.collect_comments(factory), "", None)
    return back(request, "/inbox", msg=f"Fetching comments (job #{job.id}). Refresh in a moment.")


@router.post("/inbox/draft")
def inbox_draft(request: Request, brand: str = Form(""), limit: int = Form(20),
                factory: Factory = Depends(get_factory)):
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    job = _jobs(request).submit("drafts", "Draft replies",
                                lambda: {"drafted": service.draft_replies(factory, limit, brand=brand or None)}, "", None)
    return back(request, "/inbox", msg=f"Drafting up to {limit} replies (job #{job.id}). Nothing is sent.")


@router.post("/inbox/{comment_id}/send")
def inbox_send(comment_id: int, request: Request, reply: str = Form(...),
               factory: Factory = Depends(get_factory)):
    try:
        res = service.send_reply(factory, comment_id, reply, actor="human")
    except PublishError as e:
        service.save_draft(factory, comment_id, reply)
        return back(request, "/inbox", err=f"Not sent: {e}", anchor=f"c-{comment_id}")
    return back(request, "/inbox", msg=f"Comment #{comment_id}: {res['status']}", anchor=f"c-{comment_id}")


@router.post("/inbox/{comment_id}/save")
def inbox_save(comment_id: int, request: Request, reply: str = Form(""),
               factory: Factory = Depends(get_factory)):
    service.save_draft(factory, comment_id, reply)
    return back(request, "/inbox", msg=f"Saved draft for comment #{comment_id}", anchor=f"c-{comment_id}")


@router.post("/inbox/{comment_id}/redraft")
def inbox_redraft(comment_id: int, request: Request, factory: Factory = Depends(get_factory)):
    service.redraft(factory, comment_id)
    return back(request, "/inbox", msg=f"New draft for comment #{comment_id}", anchor=f"c-{comment_id}")


@router.post("/inbox/{comment_id}/status")
def inbox_status(comment_id: int, request: Request, status: str = Form(...),
                 factory: Factory = Depends(get_factory)):
    if status not in ("ignored", "flagged", "new"):
        raise ValueError("status must be ignored, flagged or new")
    store.set_status(factory.db, comment_id, status)
    word = {"ignored": "ignored", "flagged": "flagged", "new": "restored"}[status]
    return back(request, "/inbox", msg=f"Comment #{comment_id} {word}", anchor=f"c-{comment_id}")


@router.post("/inbox/{comment_id}/idea")
def inbox_idea(comment_id: int, request: Request, factory: Factory = Depends(get_factory)):
    idea_id = service.save_as_idea(factory, comment_id)
    if idea_id is None:
        c = store.get(factory.db, comment_id)
        return back(request, "/inbox", msg=f"Already in the backlog as idea #{c.get('idea_id')}",
                    anchor=f"c-{comment_id}")
    return back(request, "/inbox", msg=f"Saved as idea #{idea_id}", anchor=f"c-{comment_id}")
