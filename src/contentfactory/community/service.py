"""Entry points for the worker, CLI and dashboard.

    collect_comments(factory)        fetch new comments on published posts, triage, save ideas
    draft_replies(factory, limit)    Claude drafts for untriaged-to-reply comments (drafts only)
    send_reply(factory, comment_id)  only called from a human click in the inbox
    save_as_idea / set_status        inbox buttons

Nothing in here runs on a timer by itself and nothing replies automatically.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import httpx

from ..db import now_iso
from ..guardrails import jaccard, shingles
from ..publish.base import PublishError
from . import store
from .drafting import draft_reply
from .platforms import REPLY_MAX_CHARS, SUPPORTED, CommentsClient, client_for
from .triage import ASKS_IF_BOT, classify, idea_title_from

MAX_REPLIES_PER_HOUR = 30
IDEA_CATEGORIES = ("question", "content_idea")
IDEA_DEDUPE = 0.5


class RateLimited(PermissionError):
    pass


def _own_handles(factory, platform: str) -> set[str]:
    out = set()
    for b in factory.brands().values():
        for a in b.accounts:
            if a.platform == platform and a.handle:
                out.add(a.handle)
    return out


def _publications(factory, platforms: tuple[str, ...], max_age_days: int) -> list[dict]:
    rows = factory.db.query(
        "SELECT pub.*, p.brand AS brand, p.title AS post_title FROM publications pub "
        "JOIN posts p ON p.id = pub.post_id WHERE pub.status = 'published' AND pub.remote_id != '' "
        f"AND pub.platform IN ({','.join('?' for _ in platforms)}) ORDER BY pub.published_at DESC",
        list(platforms))
    if max_age_days <= 0:
        return rows
    cutoff = datetime.now(timezone.utc).timestamp() - max_age_days * 86400
    keep = []
    for r in rows:
        try:
            ts = datetime.fromisoformat(str(r.get("published_at") or "").replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts.timestamp() < cutoff:
                continue
        except ValueError:
            pass
        keep.append(r)
    return keep


def collect_comments(factory, *, platforms: list[str] | None = None, max_age_days: int = 30,
                     max_pages: int = 4, transport: httpx.BaseTransport | None = None,
                     clients: dict[str, CommentsClient] | None = None) -> dict:
    """Fetch comments on published posts (official APIs), store new ones,
    triage them and save viewer questions as ideas.

    Returns {"fetched", "new", "skipped_own", "flagged", "ideas", "errors": [...]}.
    Missing credentials for a platform are reported in errors, not raised.
    """
    db = factory.db
    store.ensure_schema(db)
    wanted = tuple(p for p in (platforms or SUPPORTED) if p in SUPPORTED)
    report = {"fetched": 0, "new": 0, "skipped_own": 0, "flagged": 0, "ideas": 0, "errors": []}
    pubs = _publications(factory, wanted, max_age_days)
    clients = dict(clients or {})
    new_ids: list[int] = []
    for pub in pubs:
        platform = pub["platform"]
        if platform not in clients:
            clients[platform] = client_for(platform, factory.settings, own_usernames=_own_handles(factory, platform),
                                           transport=transport)
        client = clients[platform]
        missing = client.missing_credentials()
        if missing:
            msg = f"{platform}: missing {', '.join(missing)}"
            if msg not in report["errors"]:
                report["errors"].append(msg)
            continue
        try:
            remote = client.fetch(pub["remote_id"], max_pages=max_pages)
        except PublishError as e:
            report["errors"].append(f"publication {pub['id']}: {e}")
            db.log("comments.fetch_failed", "publication", pub["id"], {"error": str(e)})
            continue
        ours = store.own_reply_ids(db, platform)
        for rc in remote:
            report["fetched"] += 1
            if rc.own or rc.remote_id in ours or not rc.remote_id:
                report["skipped_own"] += 1
                continue
            cid, created = store.upsert(db, {
                "publication_id": pub["id"], "brand": pub["brand"], "platform": platform,
                "remote_id": rc.remote_id, "parent_remote_id": rc.parent_remote_id, "author": rc.author,
                "text": rc.text, "created_at_remote": rc.created_at, "like_count": rc.like_count,
                "status": "new", "raw": rc.raw})
            if created:
                new_ids.append(cid)
    report["new"] = len(new_ids)
    t = triage_comments(factory, new_ids)
    report["flagged"], report["ideas"] = t["flagged"], t["ideas"]
    db.log("comments.collected", "", None, {k: v for k, v in report.items() if k != "errors"}
           | {"errors": len(report["errors"])})
    return report


def triage_comments(factory, comment_ids: list[int], batch_size: int = 25) -> dict:
    """Classify comments; flag spam/abuse; save questions/ideas to the backlog."""
    db = factory.db
    brands = factory.brands()
    out = {"flagged": 0, "ideas": 0}
    rows = [store.get(db, i) for i in comment_ids]
    by_brand: dict[str, list[dict]] = {}
    for r in rows:
        by_brand.setdefault(r["brand"], []).append(r)
    for slug, items in by_brand.items():
        brand = brands.get(slug)
        if brand is None:
            continue
        titles = {r["id"]: _post_title(db, r) for r in items}
        for start in range(0, len(items), batch_size):
            chunk = items[start:start + batch_size]
            results = classify(factory.llm, brand, [{"text": r["text"], "post_title": titles[r["id"]]} for r in chunk])
            for r, res in zip(chunk, results):
                changes = {"category": res.category,
                           "meta": {"category": res.category, "reason": res.reason, "idea_title": res.idea_title,
                                      "source": factory.llm.provider}}
                if res.category in store.FLAG_CATEGORIES:
                    changes["status"] = "flagged"
                    out["flagged"] += 1
                db.update("comments", r["id"], changes)
                if res.category in IDEA_CATEGORIES and not ASKS_IF_BOT.search(r["text"] or ""):
                    try:
                        if save_as_idea(factory, r["id"], title=res.idea_title, actor="system") is not None:
                            out["ideas"] += 1
                    except (ValueError, PermissionError):  # too short to be an idea
                        pass
    return out


def _post_title(db, comment: dict) -> str:
    if not comment.get("publication_id"):
        return ""
    row = db.one("SELECT p.title FROM publications pub JOIN posts p ON p.id = pub.post_id WHERE pub.id = ?",
                 [comment["publication_id"]])
    return (row or {}).get("title", "")


def save_as_idea(factory, comment_id: int, title: str = "", actor: str = "human") -> int | None:
    """Add a comment to the brand's idea backlog (source 'comment').
    Returns the idea id, or None when a near-duplicate idea already exists."""
    db = factory.db
    c = store.get(db, comment_id)
    if c.get("idea_id"):
        return None
    if c["status"] == "flagged":
        raise PermissionError("Flagged comments can't become ideas; restore it first if it isn't spam")
    brand = factory.brand(c["brand"])
    title = (title or (c.get("meta") or {}).get("idea_title") or idea_title_from(c["text"])).strip()
    if len(title) < 8:
        raise ValueError("Comment is too short to turn into an idea")
    sh = shingles(title, 2)
    for r in db.query("SELECT id, title FROM ideas WHERE brand = ? ORDER BY id DESC LIMIT 500", [brand.slug]):
        if r["title"].strip().lower() == title.lower() or jaccard(sh, shingles(r["title"], 2)) >= IDEA_DEDUPE:
            db.update("comments", comment_id, {"idea_id": r["id"]})
            return None
    fmt = "short" if "short" in brand.formats else (brand.formats[0] if brand.formats else "short")
    idea_id = db.insert("ideas", {
        "brand": brand.slug, "title": title, "angle": f"Answer a real viewer question: \"{c['text'][:200]}\"",
        "format": fmt, "pillar": "", "score": round(6.0 + min(c.get("like_count") or 0, 20) * 0.1, 2),
        "source": "comment", "status": "new",
        "meta": {"comment_id": comment_id, "platform": c["platform"], "category": c.get("category", ""),
                 "comment_text": c["text"][:500]}})
    db.update("comments", comment_id, {"idea_id": idea_id})
    db.log("idea.from_comment", "idea", idea_id, {"comment": comment_id}, actor=actor)
    return idea_id


def draft_replies(factory, limit: int = 20, *, brand: str | None = None) -> list[int]:
    """Draft replies for triaged comments with status 'new' (never flagged ones).
    Returns the ids of comments that got a draft. Sends nothing."""
    db = factory.db
    store.ensure_schema(db)
    sql = ("SELECT * FROM comments WHERE status = 'new' AND category != '' AND category NOT IN ('spam', 'abuse')"
           + (" AND brand = ?" if brand else "") + " ORDER BY like_count DESC, id LIMIT ?")
    rows = db.query(sql, [brand, limit] if brand else [limit])
    brands = factory.brands()
    done = []
    for c in rows:
        b = brands.get(c["brand"])
        if b is None:
            continue
        try:
            text, notes = draft_reply(factory.llm, b, c, _post_title(db, c))
        except Exception as e:  # one bad draft shouldn't stop the batch
            db.log("comment.draft_failed", "comment", c["id"], {"error": str(e)})
            continue
        db.update("comments", c["id"], {"draft": text, "draft_notes": " ".join(notes), "status": "drafted"})
        done.append(c["id"])
    if done:
        db.log("comments.drafted", "", None, {"count": len(done)})
    return done


def redraft(factory, comment_id: int) -> str:
    c = store.get(factory.db, comment_id)
    if c["status"] in ("flagged", "replied"):
        raise PermissionError(f"Comment #{comment_id} is {c['status']}; nothing to draft")
    if not c.get("category"):
        triage_comments(factory, [comment_id])
        c = store.get(factory.db, comment_id)
        if c["status"] == "flagged":
            raise PermissionError(f"Comment #{comment_id} looks like spam or abuse and was flagged")
    text, notes = draft_reply(factory.llm, factory.brand(c["brand"]), c, _post_title(factory.db, c))
    factory.db.update("comments", comment_id, {"draft": text, "draft_notes": " ".join(notes), "status": "drafted"})
    return text


def save_draft(factory, comment_id: int, text: str) -> None:
    c = store.get(factory.db, comment_id)
    if c["status"] == "replied":
        raise ValueError(f"Comment #{comment_id} was already replied to")
    status = c["status"] if c["status"] in ("flagged", "ignored") else ("drafted" if text.strip() else "new")
    factory.db.update("comments", comment_id, {"draft": text.strip(), "status": status})


def send_reply(factory, comment_id: int, text: str | None = None, *, actor: str = "human",
               transport: httpx.BaseTransport | None = None, client: CommentsClient | None = None,
               now: datetime | None = None) -> dict:
    """Send one reply. Only call this from an explicit human action.

    Respects FACTORY_DRY_RUN (records 'replied (dry run)', calls nothing) and a
    rolling limit of MAX_REPLIES_PER_HOUR real replies per platform.
    Raises PermissionError (flagged / rate limited), ValueError (bad input) or
    PublishError (the platform refused)."""
    db = factory.db
    c = store.get(db, comment_id)
    if c["status"] == "replied":
        raise ValueError(f"Comment #{comment_id} was already replied to")
    if c["status"] == "flagged":
        raise PermissionError("Flagged comments (spam/abuse) are never replied to. Restore it first if it's genuine.")
    body = (text if text is not None else c.get("draft") or "").strip()
    if not body:
        raise ValueError("Reply is empty")
    limit = REPLY_MAX_CHARS.get(c["platform"], 2000)
    if len(body) > limit:
        raise ValueError(f"Reply is {len(body)} characters; {c['platform']} allows {limit}")
    target = c.get("parent_remote_id") or c["remote_id"]  # both platforms reply on the top-level thread
    dry = factory.settings.dry_run
    if dry:
        remote = "dry-" + hashlib.sha1(f"{c['platform']}{target}{body}".encode()).hexdigest()[:12]
    else:
        sent = store.replies_last_hour(db, c["platform"], now)
        if sent >= MAX_REPLIES_PER_HOUR:
            raise RateLimited(f"{c['platform']}: {sent} replies in the last hour; the limit is "
                              f"{MAX_REPLIES_PER_HOUR}/hour. Try again later.")
        client = client or client_for(c["platform"], factory.settings, transport=transport)
        remote = client.reply(target, body)
    when = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat() if now else now_iso()
    db.update("comments", comment_id, {"status": "replied", "reply_text": body, "draft": body,
                                       "reply_remote_id": remote, "replied_at": when, "dry_run": 1 if dry else 0})
    db.log("comment.replied_dry_run" if dry else "comment.replied", "comment", comment_id,
           {"platform": c["platform"], "remote_id": remote, "parent": target}, actor=actor)
    return {"comment": comment_id, "status": "replied (dry run)" if dry else "replied", "remote_id": remote}
