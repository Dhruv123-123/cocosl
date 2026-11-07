"""Performance feedback loop.

Reads the latest metrics per publication, rolls them up by format, pillar,
platform and posting hour, and feeds the winners back into idea scoring so
the factory makes more of what works and less of what doesn't.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from .db import DB


def latest_metrics(db: DB, days: int = 90, brand: str | None = None) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    sql = """
    SELECT p.id AS publication_id, p.platform, p.published_at, p.scheduled_at, s.id AS post_id, s.brand,
           s.format, s.title, i.pillar, m.views, m.likes, m.comments, m.shares, m.saves, m.reach,
           m.avg_view_pct, m.follows, m.link_clicks
    FROM publications p
    JOIN posts s ON s.id = p.post_id
    LEFT JOIN ideas i ON i.id = s.idea_id
    JOIN metrics m ON m.id = (SELECT id FROM metrics WHERE publication_id = p.id ORDER BY captured_at DESC, id DESC LIMIT 1)
    WHERE p.status = 'published' AND COALESCE(p.published_at, p.scheduled_at) >= ?"""
    params: list = [since]
    if brand:
        sql += " AND s.brand = ?"
        params.append(brand)
    rows = db.query(sql, params)
    for r in rows:
        v = max(r["views"] or 0, 1)
        r["engagement_rate"] = ((r["likes"] or 0) + (r["comments"] or 0) + (r["shares"] or 0) + (r["saves"] or 0)) / v
        r["save_rate"] = (r["saves"] or 0) / v
        ts = r["published_at"] or r["scheduled_at"]
        r["hour"] = datetime.fromisoformat(ts).hour if ts else None
    return rows


def rollup(rows: list[dict], key: str) -> list[dict]:
    groups: dict = defaultdict(list)
    for r in rows:
        groups[r.get(key) or "unknown"].append(r)
    out = []
    for k, items in groups.items():
        n = len(items)
        out.append({
            key: k, "posts": n,
            "avg_views": round(sum(i["views"] or 0 for i in items) / n, 1),
            "avg_engagement": round(sum(i["engagement_rate"] for i in items) / n, 4),
            "avg_save_rate": round(sum(i["save_rate"] for i in items) / n, 4),
            "follows": sum(i["follows"] or 0 for i in items),
            "link_clicks": sum(i["link_clicks"] or 0 for i in items),
        })
    return sorted(out, key=lambda r: -r["avg_views"])


def report(db: DB, brand: str | None = None, days: int = 30) -> dict:
    rows = latest_metrics(db, days=days, brand=brand)
    top = sorted(rows, key=lambda r: -(r["views"] or 0))[:5]
    return {
        "posts_measured": len(rows),
        "total_views": sum(r["views"] or 0 for r in rows),
        "by_format": rollup(rows, "format"),
        "by_pillar": rollup(rows, "pillar"),
        "by_platform": rollup(rows, "platform"),
        "by_hour": rollup(rows, "hour"),
        "top_posts": [{k: r[k] for k in ("post_id", "platform", "title", "views", "engagement_rate")} for r in top],
    }


def score_multipliers(db: DB, brand: str, min_posts: int = 3) -> dict[str, dict[str, float]]:
    """Relative performance per format and pillar (1.0 = average). Groups with
    too little data stay neutral so one viral fluke doesn't steer everything."""
    rows = latest_metrics(db, days=120, brand=brand)
    if not rows:
        return {"format": {}, "pillar": {}}
    overall = sum(r["views"] or 0 for r in rows) / len(rows) or 1
    out: dict[str, dict[str, float]] = {}
    for key in ("format", "pillar"):
        out[key] = {}
        for g in rollup(rows, key):
            if g["posts"] >= min_posts:
                out[key][g[key]] = round(max(0.5, min(2.0, g["avg_views"] / overall)), 2)
    return out


def rescore_backlog(db: DB, brand: str) -> int:
    """Apply learned multipliers to new ideas' base scores. Returns count changed."""
    mult = score_multipliers(db, brand)
    if not (mult["format"] or mult["pillar"]):
        return 0
    changed = 0
    for idea in db.query("SELECT * FROM ideas WHERE brand = ? AND status = 'new'", [brand]):
        meta = idea.get("meta") or {}
        base = meta.get("base_score", idea["score"])
        factor = mult["format"].get(idea["format"], 1.0) * mult["pillar"].get(idea["pillar"], 1.0)
        new = round(base * factor if base >= 0 else base / factor, 2)
        if new != idea["score"]:
            meta["base_score"] = base
            meta["learned_factor"] = factor
            db.update("ideas", idea["id"], {"score": new, "meta": meta})
            changed += 1
    return changed
