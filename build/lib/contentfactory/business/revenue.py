"""Revenue/expense ledger, CSV importers and reports.

All amounts are stored as integer cents. Reports return plain dicts/lists so
the dashboard and CLI can render them however they like.

Importers are tolerant: each `ImportSpec` lists candidate column names per
field, the header row is found even after report preambles, and every row gets
an `external_id` (the export's own id, or a hash of the row) so re-importing
the same file never double-counts.
"""
from __future__ import annotations

import calendar
import hashlib
import os
import re
import sqlite3
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path
from typing import Any, Callable

from ..db import DB
from ._util import parse_date, pick, read_csv_rows, to_cents, today

REVENUE_SOURCES = ["affiliate", "adsense", "creator_fund", "sponsorship", "ugc", "product", "other"]
EXPENSE_CATEGORIES = ["llm", "gpu", "tts", "stock", "software", "ads", "other"]


# --------------------------------------------------------------------------- ledger
def add_revenue(db: DB, source: str, amount: Any = None, *, amount_cents: int | None = None,
                date: str | None = None, brand: str = "", post_id: int | None = None,
                client_id: int | None = None, note: str = "", external_id: str = "",
                currency: str = "USD") -> int | None:
    """Record income. `amount` is in currency units ('12.50', 12.5); or pass `amount_cents`.

    Returns the new row id, or None if (source, external_id) was already recorded."""
    if source not in REVENUE_SOURCES:
        raise ValueError(f"Unknown revenue source '{source}'. Options: {', '.join(REVENUE_SOURCES)}")
    cents = amount_cents if amount_cents is not None else to_cents(amount)
    try:
        return db.insert("revenue", {
            "date": parse_date(date) if date else today().isoformat(), "source": source, "brand": brand or "",
            "post_id": post_id, "client_id": client_id, "amount_cents": int(cents),
            "currency": (currency or "USD").upper(), "note": note, "external_id": external_id or "",
        })
    except sqlite3.IntegrityError:
        if external_id:
            return None
        raise


def add_expense(db: DB, category: str, amount: Any = None, *, amount_cents: int | None = None,
                date: str | None = None, note: str = "", currency: str = "USD") -> int:
    if category not in EXPENSE_CATEGORIES:
        raise ValueError(f"Unknown expense category '{category}'. Options: {', '.join(EXPENSE_CATEGORIES)}")
    cents = amount_cents if amount_cents is not None else to_cents(amount)
    return db.insert("expenses", {
        "date": parse_date(date) if date else today().isoformat(), "category": category,
        "amount_cents": abs(int(cents)), "currency": (currency or "USD").upper(), "note": note,
    })


def ledger(db: DB, limit: int = 100, start: str | None = None, end: str | None = None) -> list[dict]:
    """Most recent revenue and expense rows merged (expenses negative), newest first."""
    where, params = _range(start, end)
    rev = db.query(f"SELECT id, date, source AS kind, brand, amount_cents, currency, note, 'revenue' AS type "
                   f"FROM revenue WHERE {where}", params)
    exp = db.query(f"SELECT id, date, category AS kind, '' AS brand, -amount_cents AS amount_cents, currency, "
                   f"note, 'expense' AS type FROM expenses WHERE {where}", params)
    return sorted(rev + exp, key=lambda r: (r["date"], r["id"]), reverse=True)[:limit]


def _range(start: str | None, end: str | None, col: str = "date") -> tuple[str, list]:
    clauses, params = ["1=1"], []
    if start:
        clauses.append(f"{col} >= ?")
        params.append(start)
    if end:
        clauses.append(f"{col} <= ?")
        params.append(end if len(end) > 10 else end + "T99")
    return " AND ".join(clauses), params


# --------------------------------------------------------------------------- importers
@dataclass
class ImportSpec:
    """How to read one kind of export. Each field lists candidate column names."""
    source: str
    date: list[str]
    amount: list[str]
    external_id: list[str] = field(default_factory=list)
    note: list[str] = field(default_factory=list)
    brand: list[str] = field(default_factory=list)
    post_id: list[str] = field(default_factory=list)
    source_col: list[str] = field(default_factory=list)   # generic CSV: per-row source
    skip: Callable[[dict], bool] | None = None
    header_hints: list[str] = field(default_factory=list)
    id_prefix: str = ""


def _truthy(v: str) -> bool:
    return str(v).strip().lower() in ("true", "yes", "1", "y", "refunded", "chargeback")


SPECS: dict[str, ImportSpec] = {
    "generic": ImportSpec(
        source="other", date=["date", "day", "paid_at", "created_at"],
        amount=["amount", "amount_usd", "revenue", "earnings", "net", "value", "total"],
        external_id=["external_id", "id", "transaction_id", "reference"],
        note=["note", "description", "memo", "product"], brand=["brand", "channel"],
        post_id=["post_id"], source_col=["source", "type", "category"],
        header_hints=["date", "amount"]),
    "gumroad": ImportSpec(
        source="product", date=["Purchase Date", "Sale Date", "Date", "Created At", "created_at"],
        amount=["Net Total ($)", "Net Total", "Net", "Sale Price ($)", "Sale Price", "Price ($)", "Price", "Amount"],
        external_id=["Purchase ID", "Sale ID", "Order Number", "ID"],
        note=["Item Name", "Product Name", "Product", "Variants"],
        skip=lambda r: _truthy(pick(r, ["Refunded?", "Refunded", "Disputed?", "Chargebacked?"])),
        header_hints=["purchase", "item name", "sale"], id_prefix="gumroad-"),
    "amazon": ImportSpec(
        source="affiliate", date=["Date Shipped", "Date", "Shipped Date", "Day"],
        amount=["Ad Fees($)", "Ad Fees ($)", "Ad Fees", "Earnings", "Fees", "Advertising Fees($)", "Total Earnings"],
        note=["Name", "Title", "Product Name", "ASIN"], brand=["Tracking ID", "Tracking Id", "Tag"],
        header_hints=["ad fees", "tracking id", "asin"], id_prefix="amazon-"),
    "youtube": ImportSpec(
        source="adsense", date=["Date", "Day", "Video publish time"],
        amount=["Estimated revenue (USD)", "Estimated revenue", "Your estimated revenue (USD)",
                "Estimated partner revenue (USD)", "Revenue"],
        note=["Video title", "Content", "Video"], post_id=["Content", "Video ID", "Video"],
        skip=lambda r: pick(r, ["Date", "Content", "Video title"]).strip().lower() == "total",
        header_hints=["estimated revenue", "revenue"], id_prefix="yt-"),
    "impact": ImportSpec(
        source="affiliate", date=["Action Date", "Event Date", "Locking Date", "Date", "Transaction Date"],
        amount=["Payout", "Action Earnings", "Earnings", "Commission", "Amount"],
        external_id=["Action Id", "Action ID", "Id", "Transaction Id"],
        note=["Campaign", "Brand", "Advertiser", "Ad"], post_id=["SubId1", "Sub Id 1", "Sub ID 1", "SharedId"],
        skip=lambda r: pick(r, ["Status", "Action Status", "State"]).lower() in ("reversed", "rejected", "voided"),
        header_hints=["action", "payout", "campaign"], id_prefix="impact-"),
    "shareasale": ImportSpec(
        source="affiliate", date=["Trans Date", "Transaction Date", "Date", "Click Date"],
        amount=["Commission", "Affiliate Commission", "Earnings", "Amount"],
        external_id=["Trans ID", "Transaction ID", "Trans Id", "ID"],
        note=["Merchant", "Merchant Name", "Organization"], post_id=["afftrack", "Afftrack", "Sub ID"],
        skip=lambda r: _truthy(pick(r, ["Voided", "Void", "Locked/Voided"])) or
        pick(r, ["Status"]).lower() in ("voided", "reversed"),
        header_hints=["trans", "commission", "merchant"], id_prefix="sas-"),
}
SPECS["affiliate"] = SPECS["impact"]


def _post_id_from(db: DB, value: str) -> int | None:
    """'post-12' / 'p12' / '12' sub-ids, or a YouTube video id matching a publication."""
    if not value:
        return None
    m = re.fullmatch(r"\s*(?:post|p)?[-_]?(\d+)\s*", value, re.I)
    if m:
        pid = int(m.group(1))
        return pid if db.get("posts", pid) else None
    pub = db.one("SELECT post_id FROM publications WHERE remote_id = ?", [value.strip()])
    return pub["post_id"] if pub else None


def import_csv(db: DB, source: str | Path | bytes, kind: str = "generic", *, brand: str = "",
               mapping: dict[str, str | list[str]] | None = None, revenue_source: str | None = None,
               currency: str = "USD", brand_map: dict[str, str] | None = None) -> dict:
    """Import a revenue export.

    kind: generic | gumroad | amazon | youtube | impact | shareasale.
    mapping: override columns, e.g. {"amount": "My Payout Col", "date": ["When"]}.
    brand: default brand for every row; brand_map maps values of the brand column
    (e.g. Amazon tracking ids) to brand slugs.
    Returns {imported, duplicates, skipped, errors, total_cents}."""
    if kind not in SPECS:
        raise ValueError(f"Unknown import kind '{kind}'. Options: {', '.join(SPECS)}")
    spec = SPECS[kind]
    if mapping:
        spec = replace(spec, **{k: [v] if isinstance(v, str) else list(v) for k, v in mapping.items()})
    rows = read_csv_rows(source, header_hints=spec.header_hints)
    result = {"kind": kind, "imported": 0, "duplicates": 0, "skipped": 0, "errors": [], "total_cents": 0}
    seen: dict[str, int] = {}
    for line, row in enumerate(rows, start=2):
        if spec.skip and spec.skip(row):
            result["skipped"] += 1
            continue
        try:
            entry = _row_to_entry(db, spec, row, kind, brand, revenue_source, brand_map, seen)
        except ValueError as e:
            result["errors"].append(f"row {line}: {e}")
            continue
        if entry is None:
            result["skipped"] += 1
            continue
        rid = add_revenue(db, currency=currency, **entry)
        if rid is None:
            result["duplicates"] += 1
        else:
            result["imported"] += 1
            result["total_cents"] += entry["amount_cents"]
    db.log("revenue.import", "revenue", None, {k: v for k, v in result.items() if k != "errors"})
    return result


def _row_to_entry(db: DB, spec: ImportSpec, row: dict, kind: str, brand: str, revenue_source: str | None,
                  brand_map: dict[str, str] | None, seen: dict[str, int]) -> dict | None:
    raw_amount = pick(row, spec.amount)
    if not raw_amount:
        return None
    cents = to_cents(raw_amount)
    if cents == 0:
        return None
    day = parse_date(pick(row, spec.date))
    src = revenue_source or spec.source
    row_source = pick(row, spec.source_col).lower() if spec.source_col else ""
    if row_source:
        src = row_source if row_source in REVENUE_SOURCES else "other"
    ext = pick(row, spec.external_id) if spec.external_id else ""
    if not ext:
        digest = hashlib.sha1("|".join(f"{k}={v}" for k, v in sorted(row.items())).encode()).hexdigest()[:16]
        seen[digest] = seen.get(digest, 0) + 1   # identical rows in one file stay distinct
        ext = f"{digest}-{seen[digest]}"
    row_brand = pick(row, spec.brand) if spec.brand else ""
    if row_brand and brand_map:
        row_brand = brand_map.get(row_brand, row_brand)
    post_id = None
    if spec.post_id:
        post_id = _post_id_from(db, pick(row, spec.post_id))
    return {"source": src, "amount_cents": cents, "date": day, "brand": row_brand or brand,
            "post_id": post_id, "note": pick(row, spec.note)[:200] if spec.note else "",
            "external_id": f"{spec.id_prefix}{ext}"}


# --------------------------------------------------------------------------- reports
def _month(d: str) -> str:
    return d[:7]


def pnl_by_month(db: DB, start: str | None = None, end: str | None = None,
                 include_llm_usage: bool = True) -> list[dict]:
    """Monthly P&L. LLM API cost from `llm_usage` is counted as a cost unless that
    month already has manual 'llm' expenses (assumed to be the real bill)."""
    where, params = _range(start, end)
    months: dict[str, dict] = {}

    def row(m: str) -> dict:
        return months.setdefault(m, {"month": m, "revenue_cents": 0, "expense_cents": 0, "llm_cents": 0})

    for r in db.query(f"SELECT substr(date,1,7) AS m, SUM(amount_cents) AS c FROM revenue WHERE {where} GROUP BY m",
                      params):
        row(r["m"])["revenue_cents"] = int(r["c"] or 0)
    manual_llm: set[str] = set()
    for r in db.query(f"SELECT substr(date,1,7) AS m, category, SUM(amount_cents) AS c FROM expenses "
                      f"WHERE {where} GROUP BY m, category", params):
        row(r["m"])["expense_cents"] += int(r["c"] or 0)
        if r["category"] == "llm":
            manual_llm.add(r["m"])
    if include_llm_usage:
        w2, p2 = _range(start, end, "ts")
        for r in db.query(f"SELECT substr(ts,1,7) AS m, SUM(cost_usd) AS usd FROM llm_usage WHERE {w2} GROUP BY m",
                          p2):
            if r["m"] not in manual_llm and r["usd"]:
                row(r["m"])["llm_cents"] = round(r["usd"] * 100)
    out = []
    for m in sorted(months):
        r = months[m]
        r["cost_cents"] = r["expense_cents"] + r["llm_cents"]
        r["profit_cents"] = r["revenue_cents"] - r["cost_cents"]
        r["margin_pct"] = round(100 * r["profit_cents"] / r["revenue_cents"], 1) if r["revenue_cents"] else None
        out.append(r)
    return out


def pnl_totals(rows: list[dict]) -> dict:
    keys = ["revenue_cents", "expense_cents", "llm_cents", "cost_cents", "profit_cents"]
    return {k: sum(r[k] for r in rows) for k in keys}


def revenue_by(db: DB, column: str, start: str | None = None, end: str | None = None) -> list[dict]:
    """Revenue grouped by 'source', 'brand', 'client_id' or 'post_id'."""
    if column not in ("source", "brand", "client_id", "post_id"):
        raise ValueError("column must be source, brand, client_id or post_id")
    where, params = _range(start, end)
    rows = db.query(f"SELECT {column} AS key, SUM(amount_cents) AS cents, COUNT(*) AS n FROM revenue "
                    f"WHERE {where} GROUP BY {column} ORDER BY cents DESC", params)
    total = sum(int(r["cents"] or 0) for r in rows) or 1
    return [{"key": r["key"] if r["key"] not in (None, "") else "(none)", "cents": int(r["cents"] or 0),
             "count": r["n"], "share_pct": round(100 * int(r["cents"] or 0) / total, 1)} for r in rows]


def revenue_by_source(db: DB, start: str | None = None, end: str | None = None) -> list[dict]:
    return revenue_by(db, "source", start, end)


def revenue_by_brand(db: DB, start: str | None = None, end: str | None = None) -> list[dict]:
    return revenue_by(db, "brand", start, end)


def llm_spend(db: DB, start: str | None = None, end: str | None = None) -> dict:
    """LLM API spend from llm_usage (estimated from token counts)."""
    where, params = _range(start, end, "ts")
    total = db.one(f"SELECT COALESCE(SUM(cost_usd),0) AS usd, COUNT(*) AS calls, COALESCE(SUM(input_tokens),0) AS tin, "
                   f"COALESCE(SUM(output_tokens),0) AS tout FROM llm_usage WHERE {where}", params)

    def group(col: str) -> list[dict]:
        return [{"key": r["k"] or "(none)", "usd": round(r["usd"] or 0, 4), "calls": r["n"]}
                for r in db.query(f"SELECT {col} AS k, SUM(cost_usd) AS usd, COUNT(*) AS n FROM llm_usage "
                                  f"WHERE {where} GROUP BY k ORDER BY usd DESC", params)]
    return {"total_usd": round(total["usd"], 4), "calls": total["calls"], "input_tokens": total["tin"],
            "output_tokens": total["tout"], "by_purpose": group("purpose"), "by_model": group("model"),
            "by_month": group("substr(ts,1,7)")}


def _latest_metrics(db: DB) -> dict[int, dict]:
    """Latest metrics snapshot per publication (metrics are cumulative snapshots)."""
    rows = db.query("""SELECT m.* FROM metrics m JOIN (SELECT publication_id, MAX(id) AS mid FROM metrics
                       GROUP BY publication_id) x ON x.mid = m.id""")
    return {r["publication_id"]: r for r in rows}


def _publication_views(db: DB) -> list[dict]:
    latest = _latest_metrics(db)
    pubs = db.query("SELECT p.id, p.post_id, p.platform, s.brand, s.title FROM publications p "
                    "JOIN posts s ON s.id = p.post_id")
    for p in pubs:
        m = latest.get(p["id"]) or {}
        p["views"] = int(m.get("views") or 0)
        p["link_clicks"] = int(m.get("link_clicks") or 0)
    return pubs


def post_attribution(db: DB, brand: str | None = None, limit: int = 50) -> list[dict]:
    """Per-post revenue (rows with post_id) next to its views/clicks across platforms."""
    pubs = _publication_views(db)
    revenue = {r["post_id"]: int(r["c"]) for r in db.query(
        "SELECT post_id, SUM(amount_cents) AS c FROM revenue WHERE post_id IS NOT NULL GROUP BY post_id")}
    posts: dict[int, dict] = {}
    for p in pubs:
        e = posts.setdefault(p["post_id"], {"post_id": p["post_id"], "brand": p["brand"], "title": p["title"],
                                            "views": 0, "link_clicks": 0, "platforms": []})
        e["views"] += p["views"]
        e["link_clicks"] += p["link_clicks"]
        e["platforms"].append(p["platform"])
    for pid in revenue:
        if pid not in posts:
            post = db.get("posts", pid) or {}
            posts[pid] = {"post_id": pid, "brand": post.get("brand", ""), "title": post.get("title", ""),
                          "views": 0, "link_clicks": 0, "platforms": []}
    out = []
    for pid, e in posts.items():
        if brand and e["brand"] != brand:
            continue
        e["revenue_cents"] = revenue.get(pid, 0)
        e["rpm_cents"] = round(e["revenue_cents"] * 1000 / e["views"]) if e["views"] else None
        out.append(e)
    out.sort(key=lambda e: (e["revenue_cents"], e["views"]), reverse=True)
    return out[:limit]


def effective_rpm(db: DB, start: str | None = None, end: str | None = None) -> dict:
    """Revenue per 1,000 views.

    by_brand: all revenue tagged with the brand / all views of that brand's posts.
    by_platform: post-attributed revenue split across the post's publications in
    proportion to their views, plus untagged-to-post 'adsense' revenue counted
    for YouTube."""
    pubs = _publication_views(db)
    where, params = _range(start, end)
    brand_views: dict[str, int] = {}
    for p in pubs:
        brand_views[p["brand"]] = brand_views.get(p["brand"], 0) + p["views"]
    brand_rev = {r["brand"]: int(r["c"]) for r in db.query(
        f"SELECT brand, SUM(amount_cents) AS c FROM revenue WHERE {where} AND brand != '' GROUP BY brand", params)}
    by_brand = [_rpm_row("brand", b, brand_rev.get(b, 0), brand_views.get(b, 0))
                for b in sorted(set(brand_views) | set(brand_rev))]

    plat_views: dict[str, int] = {}
    post_pubs: dict[int, list[dict]] = {}
    for p in pubs:
        plat_views[p["platform"]] = plat_views.get(p["platform"], 0) + p["views"]
        post_pubs.setdefault(p["post_id"], []).append(p)
    plat_rev: dict[str, float] = {}
    for r in db.query(f"SELECT post_id, SUM(amount_cents) AS c FROM revenue WHERE {where} AND post_id IS NOT NULL "
                      f"GROUP BY post_id", params):
        group = post_pubs.get(r["post_id"]) or []
        views = sum(p["views"] for p in group)
        for p in group:
            share = p["views"] / views if views else 1 / len(group)
            plat_rev[p["platform"]] = plat_rev.get(p["platform"], 0) + r["c"] * share
    yt = db.scalar(f"SELECT COALESCE(SUM(amount_cents),0) FROM revenue WHERE {where} AND post_id IS NULL "
                   f"AND source = 'adsense'", params)
    if yt:
        plat_rev["youtube"] = plat_rev.get("youtube", 0) + yt
    by_platform = [_rpm_row("platform", k, round(plat_rev.get(k, 0)), plat_views.get(k, 0))
                   for k in sorted(set(plat_views) | set(plat_rev))]
    return {"by_brand": by_brand, "by_platform": by_platform}


def _rpm_row(key: str, value: str, cents: int, views: int) -> dict:
    return {key: value, "revenue_cents": cents, "views": views,
            "rpm_cents": round(cents * 1000 / views) if views else None}


def monthly_goal_cents() -> int:
    try:
        return to_cents(os.environ.get("FACTORY_MONTHLY_GOAL", "1000") or "1000")
    except ValueError:
        return 100_000


def goal_progress(db: DB, month: str | None = None, goal_cents: int | None = None,
                  on: date | None = None) -> dict:
    """Progress toward the monthly revenue goal (env FACTORY_MONTHLY_GOAL, USD, default 1000)
    with a straight-line run-rate projection for the month."""
    on = on or today()
    month = month or on.strftime("%Y-%m")
    year, mon = int(month[:4]), int(month[5:7])
    days = calendar.monthrange(year, mon)[1]
    if (year, mon) < (on.year, on.month):
        elapsed = days
    elif (year, mon) > (on.year, on.month):
        elapsed = 0
    else:
        elapsed = on.day
    goal = goal_cents if goal_cents is not None else monthly_goal_cents()
    rows = pnl_by_month(db, start=f"{month}-01", end=f"{month}-{days:02d}")
    r = rows[0] if rows else {"revenue_cents": 0, "profit_cents": 0, "cost_cents": 0}
    revenue = r["revenue_cents"]
    projected = round(revenue / elapsed * days) if elapsed else 0
    remaining_days = days - elapsed
    remaining = max(0, goal - revenue)
    return {
        "month": month, "goal_cents": goal, "revenue_cents": revenue, "profit_cents": r["profit_cents"],
        "cost_cents": r["cost_cents"], "pct": round(100 * revenue / goal, 1) if goal else None,
        "days_elapsed": elapsed, "days_in_month": days, "projected_cents": projected,
        "projected_pct": round(100 * projected / goal, 1) if goal else None,
        "on_track": projected >= goal, "remaining_cents": remaining,
        "needed_per_day_cents": round(remaining / remaining_days) if remaining_days else remaining,
    }


def summary(db: DB, months: int = 12) -> dict:
    """Everything the revenue dashboard shows, in one call."""
    start = _months_ago(months)
    pnl = pnl_by_month(db, start=start)
    return {
        "pnl": pnl, "totals": pnl_totals(pnl), "goal": goal_progress(db),
        "by_source": revenue_by_source(db, start=start), "by_brand": revenue_by_brand(db, start=start),
        "llm": llm_spend(db, start=start), "rpm": effective_rpm(db), "top_posts": post_attribution(db, limit=10),
    }


def _months_ago(n: int, on: date | None = None) -> str:
    on = on or today()
    y, m = on.year, on.month - (n - 1)
    while m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}-01"
