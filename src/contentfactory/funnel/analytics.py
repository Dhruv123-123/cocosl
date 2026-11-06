"""Funnel numbers per brand: views -> link clicks -> subscribers -> sales.

Views come from the latest metrics snapshot of each publication (metrics are
cumulative snapshots, so we never sum across snapshots). Link clicks are the
tracked /go/<slug> counter in affiliate_links plus any platform-reported
link_clicks. Sales are revenue rows with source 'product' or 'affiliate'.
"""
from __future__ import annotations

from ..db import DB
from . import store


def _rate(num: int, den: int) -> float:
    return round(num / den * 100, 2) if den else 0.0


def _views(db: DB, since: str | None) -> dict[str, dict[str, int]]:
    where = "AND pub.published_at >= ?" if since else ""
    rows = db.query(
        "SELECT p.brand, COALESCE(SUM(m.views), 0) views, COALESCE(SUM(m.link_clicks), 0) clicks FROM metrics m "
        "JOIN (SELECT publication_id, MAX(captured_at) mx FROM metrics GROUP BY publication_id) last "
        "ON last.publication_id = m.publication_id AND last.mx = m.captured_at "
        "JOIN publications pub ON pub.id = m.publication_id JOIN posts p ON p.id = pub.post_id "
        f"WHERE 1=1 {where} GROUP BY p.brand", [since] if since else [])
    return {r["brand"]: {"views": int(r["views"]), "platform_clicks": int(r["clicks"])} for r in rows}


def funnel_stats(db: DB, brands: list[str] | None = None, since: str | None = None) -> list[dict]:
    """One dict per brand:
    {brand, views, link_clicks, subscribers, pending, sales, revenue_cents,
     click_rate, signup_rate, sale_rate}  (rates are percentages of the previous step).

    `since` (ISO date) limits views, signups and sales to that period; the
    affiliate click counter is all-time because it has no timestamps."""
    store.ensure_schema(db)
    views = _views(db, since)
    clicks = {r["brand"]: int(r["n"]) for r in db.query(
        "SELECT brand, COALESCE(SUM(clicks), 0) n FROM affiliate_links GROUP BY brand")}
    sub_where = "AND confirmed_at >= ?" if since else ""
    subs = {r["brand"]: int(r["n"]) for r in db.query(
        f"SELECT brand, COUNT(*) n FROM subscribers WHERE status = 'confirmed' {sub_where} GROUP BY brand",
        [since] if since else [])}
    pending = {r["brand"]: int(r["n"]) for r in db.query(
        "SELECT brand, COUNT(*) n FROM subscribers WHERE status = 'pending' GROUP BY brand")}
    rev_where = "AND date >= ?" if since else ""
    sales = {r["brand"]: (int(r["n"]), int(r["c"])) for r in db.query(
        "SELECT brand, COUNT(*) n, COALESCE(SUM(amount_cents), 0) c FROM revenue "
        f"WHERE source IN ('product', 'affiliate') {rev_where} GROUP BY brand", [since] if since else [])}
    names = brands if brands is not None else sorted(
        {b for b in [*views, *clicks, *subs, *pending, *sales] if b})
    out = []
    for b in names:
        v = views.get(b, {}).get("views", 0)
        c = clicks.get(b, 0) + views.get(b, {}).get("platform_clicks", 0)
        s = subs.get(b, 0)
        n, cents = sales.get(b, (0, 0))
        out.append({"brand": b, "views": v, "link_clicks": c, "subscribers": s, "pending": pending.get(b, 0),
                    "sales": n, "revenue_cents": cents, "click_rate": _rate(c, v), "signup_rate": _rate(s, c),
                    "sale_rate": _rate(n, s)})
    return out
