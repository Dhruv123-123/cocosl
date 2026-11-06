"""Read-only queries that feed the dashboard pages. Pure functions of a Factory."""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from ..pipeline import Factory
from .deps import localtime, parse_dt

POST_STATUSES = ["draft", "scripted", "rendered", "in_review", "blocked", "approved", "scheduled",
                 "published", "rejected", "failed"]
REVIEW_STATUSES = ("in_review", "blocked")


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _ago(days: int) -> str:
    return _iso(datetime.now(timezone.utc) - timedelta(days=days))


def display_tz(factory: Factory) -> str:
    """Timezone used to group the calendar: the first brand's, else UTC."""
    try:
        brands = factory.brands()
    except Exception:
        return "UTC"
    first = next(iter(brands.values()), None)
    return first.cadence.timezone if first else "UTC"


def require_post(factory: Factory, post_id: int) -> dict:
    post = factory.db.get("posts", post_id)
    if not post:
        raise KeyError(f"No post #{post_id}")
    return post


def require_idea(factory: Factory, idea_id: int) -> dict:
    idea = factory.db.get("ideas", idea_id)
    if not idea:
        raise KeyError(f"No idea #{idea_id}")
    return idea


def claims(post: dict) -> list[str]:
    script = post.get("script") or {}
    return [str(c) for c in (script.get("claims_to_verify") or [])]


# --------------------------------------------------------------------------- overview
def status_counts(factory: Factory) -> dict[str, int]:
    rows = factory.db.query("SELECT status, COUNT(*) AS n FROM posts GROUP BY status")
    counts = {r["status"]: r["n"] for r in rows}
    ordered = OrderedDict((s, counts.pop(s, 0)) for s in POST_STATUSES)
    ordered.update(counts)
    return dict(ordered)


def views_last(factory: Factory, days: int = 30) -> int:
    """Views gained in the window: per publication, latest snapshot minus the
    latest snapshot taken before the window began (metrics are cumulative)."""
    start = _ago(days)
    row = factory.db.one(
        """SELECT COALESCE(SUM(MAX(0, cur.v - COALESCE(prev.v, 0))), 0) AS views FROM
             (SELECT publication_id, MAX(views) AS v FROM metrics GROUP BY publication_id) cur
           LEFT JOIN
             (SELECT publication_id, MAX(views) AS v FROM metrics WHERE captured_at < ? GROUP BY publication_id) prev
           ON prev.publication_id = cur.publication_id""", [start])
    return int(row["views"] or 0) if row else 0


def kpis(factory: Factory) -> dict:
    db = factory.db
    now = datetime.now(timezone.utc)
    revenue = db.query("SELECT currency, SUM(amount_cents) AS cents FROM revenue WHERE date >= ? "
                       "GROUP BY currency ORDER BY cents DESC", [(now - timedelta(days=30)).date().isoformat()])
    return {
        "in_review": db.scalar("SELECT COUNT(*) FROM posts WHERE status = 'in_review'") or 0,
        "blocked": db.scalar("SELECT COUNT(*) FROM posts WHERE status = 'blocked'") or 0,
        "scheduled_7d": db.scalar(
            "SELECT COUNT(*) FROM publications WHERE status = 'queued' AND scheduled_at >= ? AND scheduled_at < ?",
            [_iso(now), _iso(now + timedelta(days=7))]) or 0,
        "published_30d": db.scalar(
            "SELECT COUNT(*) FROM publications WHERE status = 'published' AND published_at >= ?", [_ago(30)]) or 0,
        "dry_run_30d": db.scalar(
            "SELECT COUNT(*) FROM publications WHERE status = 'dry_run' AND published_at >= ?", [_ago(30)]) or 0,
        "views_30d": views_last(factory, 30),
        "revenue_30d": revenue,
        "llm_30d": db.one("SELECT COALESCE(SUM(cost_usd), 0) AS cost, COUNT(*) AS calls FROM llm_usage WHERE ts >= ?",
                          [_ago(30)]),
        "llm_total": db.scalar("SELECT COALESCE(SUM(cost_usd), 0) FROM llm_usage") or 0,
        "ideas_new": db.scalar("SELECT COUNT(*) FROM ideas WHERE status IN ('new', 'approved')") or 0,
    }


def upcoming(factory: Factory, limit: int = 6) -> list[dict]:
    """Queued publications from now on, one row per post+slot with its platforms."""
    rows = factory.db.query(
        """SELECT p.*, s.title, s.brand, s.format FROM publications p JOIN posts s ON s.id = p.post_id
           WHERE p.status = 'queued' AND p.scheduled_at >= ? ORDER BY p.scheduled_at, p.platform LIMIT ?""",
        [_ago(1), limit * 6])
    grouped: OrderedDict[tuple, dict] = OrderedDict()
    for r in rows:
        item = grouped.setdefault((r["post_id"], r["scheduled_at"]), {**r, "platforms": []})
        item["platforms"].append(r["platform"])
    return list(grouped.values())[:limit]


def activity(factory: Factory, limit: int = 15, entity: str | None = None,
             entity_ids: list[int] | None = None) -> list[dict]:
    if entity and entity_ids is not None:
        if not entity_ids:
            return []
        marks = ",".join("?" for _ in entity_ids)
        return factory.db.query(
            f"SELECT * FROM audit_log WHERE entity = ? AND entity_id IN ({marks}) ORDER BY id DESC LIMIT ?",
            [entity, *entity_ids, limit])
    return factory.db.query("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", [limit])


def blocked_posts(factory: Factory) -> list[dict]:
    posts = factory.db.query("SELECT * FROM posts WHERE status = 'blocked' ORDER BY updated_at DESC LIMIT 20")
    for p in posts:
        checks = (p.get("checks") or {}).get("checks", [])
        p["reasons"] = [c for c in checks if c.get("level") == "block"]
    return posts


def credentials(factory: Factory) -> dict[str, dict]:
    """Platform -> {ready, missing, note}. Adapters that fail to import show a note."""
    from ..publish import credential_status
    out = {}
    for platform, missing in credential_status(factory.settings).items():
        errors = [m for m in missing if str(m).startswith("error:")]
        out[platform] = {
            "ready": not missing,
            "missing": [m for m in missing if m not in errors],
            "note": "adapter not available yet" if errors else "",
            "error": errors[0] if errors else "",
        }
    return out


# --------------------------------------------------------------------------- pages
def ideas_for(factory: Factory, brand: str, include_rejected: bool = False) -> list[dict]:
    statuses = ("new", "approved", "rejected") if include_rejected else ("new", "approved")
    marks = ",".join("?" for _ in statuses)
    return factory.db.query(
        f"SELECT * FROM ideas WHERE brand = ? AND status IN ({marks}) "
        "ORDER BY CASE status WHEN 'approved' THEN 0 WHEN 'new' THEN 1 ELSE 2 END, score DESC, id",
        [brand, *statuses])


def review_queue(factory: Factory, brand: str | None = None) -> list[dict]:
    sql = "SELECT * FROM posts WHERE status IN ('in_review', 'blocked')"
    params: list = []
    if brand:
        sql += " AND brand = ?"
        params.append(brand)
    return factory.db.query(sql + " ORDER BY CASE status WHEN 'in_review' THEN 0 ELSE 1 END, created_at", params)


def calendar_days(factory: Factory, days: int = 14) -> tuple[str, list[tuple[str, list[dict]]]]:
    """Publications for the next `days`, grouped by local day label."""
    from ..scheduler import calendar
    tz = display_tz(factory)
    groups: OrderedDict[str, list[dict]] = OrderedDict()
    for pub in calendar(factory.db, days=days):
        key = localtime(pub["scheduled_at"], tz, "%Y-%m-%d|%A %d %B")
        groups.setdefault(key, []).append(pub)
    return tz, [(k.split("|", 1)[1], v) for k, v in groups.items()]


def published(factory: Factory, limit: int = 100) -> list[dict]:
    pubs = factory.db.query(
        """SELECT p.*, s.title, s.brand, s.format FROM publications p JOIN posts s ON s.id = p.post_id
           WHERE p.status IN ('published', 'dry_run', 'failed') ORDER BY COALESCE(p.published_at, p.created_at) DESC
           LIMIT ?""", [limit])
    for pub in pubs:
        series = factory.db.query(
            "SELECT * FROM metrics WHERE publication_id = ? ORDER BY captured_at", [pub["id"]])
        pub["metrics"] = series[-1] if series else None
        pub["series"] = [m["views"] for m in series][-20:]
    return pubs


def publications_for(factory: Factory, post_id: int) -> list[dict]:
    return factory.db.query("SELECT * FROM publications WHERE post_id = ? ORDER BY scheduled_at", [post_id])


def post_history(factory: Factory, post_id: int) -> list[dict]:
    pub_ids = [p["id"] for p in publications_for(factory, post_id)]
    rows = activity(factory, 200, "post", [post_id]) + activity(factory, 200, "publication", pub_ids)
    return sorted(rows, key=lambda r: r["id"], reverse=True)


def is_due(pub: dict) -> bool:
    dt = parse_dt(pub.get("scheduled_at"))
    return bool(dt and pub.get("status") == "queued" and dt <= datetime.now(timezone.utc))
