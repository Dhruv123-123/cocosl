"""`factory stats`: weekly scorecards from the analytics exports you download yourself.

No API calls. Download the CSVs, then:

    factory stats import --brand money-made-simple "Table data.csv" tiktok.csv plausible/*.csv
    factory stats --brand money-made-simple              # this week's scorecard (all brands without --brand)
    factory stats --save                                 # also write output/reports/stats-<date>.md

Recognised exports (the columns are matched by name, so small format changes are fine):
* YouTube Studio > Analytics > Advanced mode > Export > CSV: "Table data.csv" with Content (video id),
  Video title, Video publish time, Views, Watch time (hours), Impressions,
  Impressions click-through rate (%), Subscribers.
* TikTok Studio > Analytics > Content > Download: video title or link, post time, views,
  likes, comments, shares, average watch time.
* Plausible > Export: the CSVs in the zip. visitors.csv (date, visitors, pageviews),
  conversions.csv (goal name, conversions: goals with "signup"/"subscribe" count as signups, "outbound"/"click"
  as clicks), utm_campaigns.csv (campaign, visitors).

Rows are matched to posts by platform video id (when the factory published them) or by title. Each
match is stored as a metrics snapshot, which is what the learning loop (insights.py) reads, so the next
ideas lean towards what worked. A post you uploaded by hand gets a `published` record for that platform
(source "csv"), so hand-posted weeks count too.
"""
from __future__ import annotations

import csv
import io
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median

from .db import now_iso

SCHEMA = """
CREATE TABLE IF NOT EXISTS analytics_rows (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  brand TEXT NOT NULL, platform TEXT NOT NULL, import_id TEXT NOT NULL,
  external_id TEXT DEFAULT '', title TEXT DEFAULT '', published_at TEXT DEFAULT '',
  views INTEGER DEFAULT 0, watch_hours REAL DEFAULT 0, impressions INTEGER DEFAULT 0, ctr REAL DEFAULT 0,
  likes INTEGER DEFAULT 0, comments INTEGER DEFAULT 0, shares INTEGER DEFAULT 0, subscribers INTEGER DEFAULT 0,
  post_id INTEGER, imported_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS site_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  brand TEXT NOT NULL, import_id TEXT NOT NULL, kind TEXT NOT NULL,   -- visitors | goal | campaign
  name TEXT DEFAULT '', day TEXT DEFAULT '', value INTEGER DEFAULT 0, imported_at TEXT NOT NULL
);
"""

SYNONYMS = {
    "id": ["content", "video id", "video_id", "id"],
    "link": ["video link", "link", "url", "video url"],
    "title": ["video title", "title", "video name", "description", "caption"],
    "published": ["video publish time", "publish time", "post time", "posted", "create time", "date posted", "date"],
    "views": ["views", "total views", "video views", "plays", "total play"],
    "watch_hours": ["watch time (hours)", "watch time hours"],
    "watch_seconds": ["total watch time", "total play time", "watch time (seconds)"],
    "impressions": ["impressions"],
    "ctr": ["impressions click-through rate (%)", "click-through rate", "ctr"],
    "likes": ["likes", "total likes"],
    "comments": ["comments", "total comments"],
    "shares": ["shares", "total shares"],
    "subscribers": ["subscribers", "subscribers gained", "followers", "new followers"],
}
SIGNUP_GOALS = re.compile(r"sign ?up|subscribe|lead|email|optin|opt-in|register", re.I)
CLICK_GOALS = re.compile(r"outbound|click|affiliate|/go/|buy|checkout", re.I)


def ensure_schema(db) -> None:
    db.conn.executescript(SCHEMA)


def _num(v) -> float:
    s = str(v or "").strip().replace(",", "").replace("%", "")
    m = re.match(r"^(-?\d+(?:\.\d+)?)([kKmM]?)$", s)
    if not m:
        return 0.0
    return float(m.group(1)) * {"": 1, "k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6}[m.group(2)]


def _read(path: Path) -> list[dict]:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    # a ragged row (an unquoted comma in a title) puts the extras under None as a list: drop them
    return [{(k or "").strip().lower(): (v if isinstance(v, str) else "").strip() for k, v in row.items() if k is not None}
            for row in csv.DictReader(io.StringIO(text), dialect=dialect)]


def _col(headers: set[str], key: str) -> str | None:
    for name in SYNONYMS[key]:
        if name in headers:
            return name
    return None


def detect(path: Path, rows: list[dict]) -> str:
    headers = set(rows[0]) if rows else set()
    name = path.name.lower()
    if {"visitors"} & headers and ({"date"} & headers or "visitors" in name):
        return "plausible_visitors"
    if ("conversions" in headers or "unique_conversions" in headers or "total_conversions" in headers) and \
            ({"name", "goal"} & headers):
        return "plausible_goals"
    if "visitors" in headers and ({"name", "utm_campaign", "campaign"} & headers):
        return "plausible_campaigns"
    if "impressions click-through rate (%)" in headers or "watch time (hours)" in headers or \
            ("content" in headers and "video title" in headers):
        return "youtube"
    if any(h in headers for h in ("total play", "total views", "video link")) or "tiktok" in name:
        return "tiktok"
    return "unknown"


def _parse_date(s: str) -> str:
    s = (s or "").strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        for cand in (s, s[:19], s[:10], s[:12]):
            try:
                return datetime.strptime(cand.strip(), fmt).date().isoformat()
            except ValueError:
                continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return ""


def _norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"#\w+", "", (t or "").lower())).strip()


def _match_post(factory, brand: str, platform: str, ext_id: str, title: str) -> tuple[int | None, dict | None]:
    db = factory.db
    if ext_id:
        pub = db.one("SELECT p.* FROM publications p JOIN posts s ON s.id = p.post_id WHERE s.brand = ? "
                     "AND p.platform = ? AND (p.remote_id = ? OR p.url LIKE ?)", [brand, platform, ext_id, f"%{ext_id}%"])
        if pub:
            return pub["post_id"], pub
    nt = _norm_title(title)
    if not nt:
        return None, None
    best, best_score = None, 0.0
    for post in db.query("SELECT id, title, caption FROM posts WHERE brand = ? AND status != 'rejected'", [brand]):
        cand = _norm_title(post["title"])
        if not cand:
            continue
        if cand == nt or (len(cand) > 12 and (cand in nt or nt in cand)):
            score = 1.0
        else:
            a, b = set(cand.split()), set(nt.split())
            score = len(a & b) / max(1, len(a | b))
        if score > best_score:
            best, best_score = post, score
    if best is None or best_score < 0.6:
        return None, None
    pub = db.one("SELECT * FROM publications WHERE post_id = ? AND platform = ? ORDER BY "
                 "CASE status WHEN 'published' THEN 0 WHEN 'dry_run' THEN 1 ELSE 2 END, id DESC LIMIT 1",
                 [best["id"], platform])
    return best["id"], pub


def _record(factory, brand: str, platform: str, post_id: int, pub: dict | None, row: dict, ext_id: str) -> None:
    """Make sure there's a published publication for this post/platform and add a metrics snapshot."""
    db = factory.db
    when = row["published_at"] or now_iso()
    if pub is None or pub["status"] not in ("published",):
        if pub is not None and pub["status"] in ("dry_run", "queued", "failed", "needs_check", "cancelled"):
            meta = pub.get("meta") or {}
            meta["source"] = "csv"
            meta["external_id"] = ext_id
            upd = {"status": "published", "published_at": pub.get("published_at") or when, "meta": meta, "error": ""}
            if str(pub.get("remote_id") or "").startswith("dry-"):
                upd["remote_id"] = ""  # a dry-run id isn't a real platform id: keep the API metrics job away from it
            db.update("publications", pub["id"], upd)
            pub_id = pub["id"]
        else:
            acct = factory.brand(brand).account(platform)
            pub_id = db.insert("publications", {"post_id": post_id, "platform": platform,
                                                "account": acct.handle if acct else "", "status": "published",
                                                "scheduled_at": when, "published_at": when,
                                                "meta": {"source": "csv", "external_id": ext_id}})
        db.update("posts", post_id, {"status": "published"})
        db.log("publication.from_csv", "publication", pub_id, {"platform": platform, "external_id": ext_id})
    else:
        pub_id = pub["id"]
    db.insert("metrics", {"publication_id": pub_id, "captured_at": now_iso(), "views": int(row["views"]),
                          "likes": int(row["likes"]), "comments": int(row["comments"]), "shares": int(row["shares"]),
                          "watch_seconds": row["watch_hours"] * 3600, "follows": int(row["subscribers"]),
                          "reach": int(row["impressions"]), "raw": {"source": "csv", "ctr": row["ctr"]},
                          "created_at": now_iso()})


def import_files(factory, brand: str, paths: list[Path]) -> dict:
    factory.brand(brand)  # must exist
    db = factory.db
    ensure_schema(db)
    import_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    summary = {"import_id": import_id, "files": {}, "matched": 0, "unmatched": []}
    for path in paths:
        path = Path(path)
        rows = _read(path)
        kind = detect(path, rows)
        summary["files"][path.name] = kind
        if kind in ("youtube", "tiktok"):
            headers = set(rows[0]) if rows else set()
            cols = {k: _col(headers, k) for k in SYNONYMS}
            for r in rows:
                ext = r.get(cols["id"] or "", "") or ""
                title = r.get(cols["title"] or "", "")
                if ext.lower() == "total" or title.lower() == "total" or not (ext or title):
                    continue
                link = r.get(cols["link"] or "", "")
                if not ext and link:
                    m = re.search(r"/video/(\d+)|/shorts/([\w-]+)|[?&]v=([\w-]+)", link)
                    ext = next((g for g in (m.groups() if m else ()) if g), "")
                watch_h = _num(r.get(cols["watch_hours"] or "", 0))
                if not watch_h and cols["watch_seconds"]:
                    watch_h = _num(r.get(cols["watch_seconds"], 0)) / 3600
                data = {"views": _num(r.get(cols["views"] or "", 0)), "watch_hours": watch_h,
                        "impressions": _num(r.get(cols["impressions"] or "", 0)),
                        "ctr": _num(r.get(cols["ctr"] or "", 0)), "likes": _num(r.get(cols["likes"] or "", 0)),
                        "comments": _num(r.get(cols["comments"] or "", 0)),
                        "shares": _num(r.get(cols["shares"] or "", 0)),
                        "subscribers": _num(r.get(cols["subscribers"] or "", 0)),
                        "published_at": _parse_date(r.get(cols["published"] or "", ""))}
                post_id, pub = _match_post(factory, brand, kind, ext, title)
                db.insert("analytics_rows", {"brand": brand, "platform": kind, "import_id": import_id,
                                             "external_id": ext, "title": title[:300], "post_id": post_id,
                                             "imported_at": now_iso(), **data})
                if post_id:
                    _record(factory, brand, kind, post_id, pub, data, ext)
                    summary["matched"] += 1
                else:
                    summary["unmatched"].append(f"{kind}: {title[:60] or ext}")
        elif kind.startswith("plausible"):
            for r in rows:
                if kind == "plausible_visitors":
                    db.insert("site_stats", {"brand": brand, "import_id": import_id, "kind": "visitors",
                                             "day": _parse_date(r.get("date", "")), "value": int(_num(r.get("visitors"))),
                                             "imported_at": now_iso()})
                elif kind == "plausible_goals":
                    name = r.get("name") or r.get("goal") or ""
                    value = _num(r.get("unique_conversions") or r.get("conversions") or r.get("total_conversions"))
                    db.insert("site_stats", {"brand": brand, "import_id": import_id, "kind": "goal", "name": name,
                                             "value": int(value), "imported_at": now_iso()})
                else:
                    name = r.get("name") or r.get("utm_campaign") or r.get("campaign") or ""
                    db.insert("site_stats", {"brand": brand, "import_id": import_id, "kind": "campaign", "name": name,
                                             "value": int(_num(r.get("visitors"))), "imported_at": now_iso()})
    db.log("stats.imported", "brand", None, {"brand": brand, **{k: v for k, v in summary.items() if k != "unmatched"}})
    if summary["matched"]:
        from .insights import rescore_backlog
        summary["rescored_ideas"] = rescore_backlog(db, brand)
    return summary


# ---------------------------------------------------------------- scorecard
def _latest_import(db, table: str, brand: str, platform: str | None = None, before: str | None = None) -> str | None:
    sql = f"SELECT MAX(import_id) FROM {table} WHERE brand = ?"
    args: list = [brand]
    if platform:
        sql += " AND platform = ?"
        args.append(platform)
    if before:
        sql += " AND import_id < ?"
        args.append(before)
    return db.scalar(sql, args)


def scorecard(factory, brand: str) -> dict:
    db = factory.db
    ensure_schema(db)
    platforms = {}
    posts = []
    for platform in ("youtube", "tiktok"):
        imp = _latest_import(db, "analytics_rows", brand, platform)
        if not imp:
            continue
        rows = db.query("SELECT * FROM analytics_rows WHERE brand = ? AND platform = ? AND import_id = ?",
                        [brand, platform, imp])
        prev_id = _latest_import(db, "analytics_rows", brand, platform, before=imp)
        prev_views = db.scalar("SELECT SUM(views) FROM analytics_rows WHERE brand = ? AND platform = ? AND import_id = ?",
                               [brand, platform, prev_id]) if prev_id else None
        impressions = sum(r["impressions"] for r in rows)
        weighted_ctr = (sum(r["ctr"] * r["impressions"] for r in rows) / impressions) if impressions else None
        platforms[platform] = {"import": imp, "videos": len(rows), "views": sum(r["views"] for r in rows),
                               "prev_views": prev_views, "watch_hours": round(sum(r["watch_hours"] for r in rows), 1),
                               "impressions": impressions, "ctr": round(weighted_ctr, 2) if weighted_ctr is not None else None,
                               "subscribers": sum(r["subscribers"] for r in rows),
                               "matched": sum(1 for r in rows if r["post_id"])}
        med = median([r["views"] for r in rows]) if rows else 0
        for r in rows:
            posts.append({**r, "rel": round((r["views"] + 1) / (med + 1), 2)})
    site = {}
    imp = _latest_import(db, "site_stats", brand)
    if imp:
        rows = db.query("SELECT * FROM site_stats WHERE brand = ? AND import_id = ?", [brand, imp])
        goals = [r for r in rows if r["kind"] == "goal"]
        site = {"import": imp, "visitors": sum(r["value"] for r in rows if r["kind"] == "visitors"),
                "signups": sum(r["value"] for r in goals if SIGNUP_GOALS.search(r["name"])),
                "clicks": sum(r["value"] for r in goals if CLICK_GOALS.search(r["name"]) and not SIGNUP_GOALS.search(r["name"])),
                "campaigns": sorted(({"name": r["name"], "visitors": r["value"]} for r in rows if r["kind"] == "campaign"),
                                    key=lambda c: -c["visitors"])[:5]}
    ranked = sorted(posts, key=lambda p: -p["rel"])
    return {"brand": brand, "platforms": platforms, "site": site, "top": ranked[:3],
            "bottom": ranked[-3:] if len(ranked) > 3 else []}


def to_markdown(cards: list[dict]) -> str:
    out = [f"# Scorecard: week of {date.today() - timedelta(days=date.today().weekday())}", ""]
    for c in cards:
        out.append(f"## {c['brand']}")
        if not c["platforms"] and not c["site"]:
            out += ["No exports imported yet: `factory stats import --brand " + c["brand"] + " <files>`.", ""]
            continue
        for name, p in c["platforms"].items():
            change = ""
            if p["prev_views"]:
                pct = (p["views"] - p["prev_views"]) / p["prev_views"] * 100
                change = f" ({pct:+.0f}% vs previous export)"
            ctr = f", CTR {p['ctr']}%" if p["ctr"] is not None else ""
            out.append(f"- **{name}**: {int(p['views']):,} views{change}, {p['watch_hours']} watch hours{ctr}, "
                       f"+{int(p['subscribers'])} subscribers · {p['videos']} videos ({p['matched']} matched to posts)")
        if c["site"]:
            s = c["site"]
            out.append(f"- **site**: {s['visitors']:,} visitors, {s['signups']} signups, {s['clicks']} clicks")
            for camp in s["campaigns"]:
                out.append(f"  - {camp['name'] or '(no campaign)'}: {camp['visitors']} visitors")
        if c["top"]:
            out.append("- Top: " + "; ".join(f"{p['title'][:50]} ({p['platform']}, {p['rel']}x usual)" for p in c["top"]))
        if c["bottom"]:
            out.append("- Bottom: " + "; ".join(f"{p['title'][:50]} ({p['platform']}, {p['rel']}x)" for p in c["bottom"]))
        out.append("")
    return "\n".join(out)


def register(sub, factory_fn) -> None:
    s = sub.add_parser("stats", help="weekly scorecard from YouTube Studio / TikTok / Plausible CSV exports (no API)")
    s.add_argument("action", nargs="?", choices=["show", "import"], default="show")
    s.add_argument("files", nargs="*", help="CSV files to import")
    s.add_argument("--brand")
    s.add_argument("--save", action="store_true", help="also write output/reports/stats-<date>.md")

    def run(a):
        f = factory_fn(a)
        if a.action == "import":
            if not a.brand or not a.files:
                raise SystemExit("usage: factory stats import --brand <slug> <csv files...>")
            res = import_files(f, a.brand, [Path(p) for p in a.files])
            for name, kind in res["files"].items():
                print(f"{name}: {kind if kind != 'unknown' else 'not recognised (skipped)'}")
            print(f"Matched {res['matched']} video row(s) to posts; the learning loop now uses them."
                  + (f" Rescored {res.get('rescored_ideas', 0)} idea(s)." if res["matched"] else ""))
            for u in res["unmatched"][:10]:
                print(f"  unmatched: {u}")
            return
        brands = [a.brand] if a.brand else list(f.brands())
        text = to_markdown([scorecard(f, b) for b in brands])
        print(text)
        if a.save:
            out = f.settings.output_dir / "reports" / f"stats-{date.today()}.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text)
            print(f"Saved {out}")
    s.set_defaults(func=run)
