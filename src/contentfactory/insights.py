"""Performance feedback loop.

Reads the latest metrics per publication, rolls them up by format, pillar,
platform and posting hour, and feeds the winners back into idea scoring so
the factory makes more of what works and less of what doesn't.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import median

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


def relative(rows: list[dict]) -> list[dict]:
    """Add `rel`: views vs. the median on the same platform (a TikTok view isn't a YouTube view)."""
    by_platform: dict = defaultdict(list)
    for r in rows:
        by_platform[r["platform"]].append(r["views"] or 0)
    med = {p: median(v) for p, v in by_platform.items()}
    for r in rows:
        r["rel"] = ((r["views"] or 0) + 1) / (med[r["platform"]] + 1)
    return rows


def _geo(xs) -> float:
    xs = list(xs)
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else 1.0


def score_multipliers(db: DB, brand: str, min_posts: int = 3) -> dict[str, dict[str, float]]:
    """Relative performance per format and pillar (1.0 = typical), measured against each
    platform's median so a platform with big raw numbers doesn't skew it. Groups with
    too little data stay neutral so one viral fluke doesn't steer everything."""
    rows = relative(latest_metrics(db, days=120, brand=brand))
    out: dict[str, dict[str, float]] = {"format": {}, "pillar": {}}
    for key in ("format", "pillar"):
        groups: dict = defaultdict(list)
        for r in rows:
            groups[r.get(key) or "unknown"].append(r["rel"])
        for k, rels in groups.items():
            if len(rels) >= min_posts:
                out[key][k] = round(max(0.5, min(2.0, _geo(rels))), 2)
    return out


def winners_prompt(db: DB, brand: str, min_posts: int = 3, settle_days: int = 3) -> str:
    """'What worked / what flopped' with real titles, for the idea prompt. Empty until there's data.
    Posts younger than `settle_days` are left out: their numbers are still climbing."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=settle_days)).isoformat()
    rows = relative([r for r in latest_metrics(db, days=120, brand=brand)
                     if (r["published_at"] or r["scheduled_at"] or "") <= cutoff])
    posts: dict = {}
    for r in rows:
        posts.setdefault(r["post_id"], {"title": r["title"], "format": r["format"], "pillar": r["pillar"],
                                        "rels": []})["rels"].append(r["rel"])
    if len(posts) < min_posts:
        return ""
    ranked = sorted(({**p, "x": round(_geo(p["rels"]), 1)} for p in posts.values()), key=lambda p: -p["x"])
    lines = ["How past posts did (views vs. this channel's usual on each platform):"]
    lines += [f"- {p['x']}x: {p['title']} ({p['format']}, {p['pillar'] or 'no pillar'})" for p in ranked[:5]]
    if len(ranked) > 5:
        lines.append("Underperformed:")
        lines += [f"- {p['x']}x: {p['title']} ({p['format']})" for p in ranked[-3:]]
    lines.append("Lean toward what worked, but keep variety: new angles, not copies of the winners' titles.")
    return "\n".join(lines)


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
