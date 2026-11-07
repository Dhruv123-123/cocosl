"""One-page weekly HTML summary per brand, built from the analytics exports you import
(`factory stats import`: YouTube Studio, TikTok, Plausible CSVs). No API calls.

    factory report --html            # output/reports/week-<date>/<brand>.html + index.html
    (the worker writes it every Monday next to the Markdown business report)

Each page: headline numbers per platform (and change since the previous import), the site's visitors,
signups and clicks, the 3 best and 3 worst posts (views against that platform's median), how each
format and pillar did, and suggested next topics: unused ideas that look like the winners, follow-ups
to the best posts, and pillars that went quiet.
"""
from __future__ import annotations

import html
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean

STOP = set("a an and are as at be but by for from how i if in into is it its of on or that the this to was what "
           "when why with you your my our".split())


def _words(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", (t or "").lower()) if w not in STOP and len(w) > 2}


def _rows(factory, brand: str) -> list[dict]:
    """Latest import per platform, with views relative to that platform's median, format and pillar."""
    from .stats import _latest_import, ensure_schema
    db = factory.db
    ensure_schema(db)
    out = []
    for platform in ("youtube", "tiktok"):
        imp = _latest_import(db, "analytics_rows", brand, platform)
        if not imp:
            continue
        rows = db.query("""SELECT a.*, s.format, COALESCE(i.pillar, '') pillar FROM analytics_rows a
                           LEFT JOIN posts s ON s.id = a.post_id LEFT JOIN ideas i ON i.id = s.idea_id
                           WHERE a.brand = ? AND a.platform = ? AND a.import_id = ?""", [brand, platform, imp])
        views = sorted(r["views"] for r in rows)
        med = views[len(views) // 2] if views else 0
        out += [{**r, "rel": round((r["views"] + 1) / (med + 1), 2)} for r in rows]
    return out


def _groups(rows: list[dict], key: str) -> list[tuple[str, float, int]]:
    g = defaultdict(list)
    for r in rows:
        if r.get(key):
            g[r[key]].append(r["rel"])
    return sorted(((k, round(mean(v), 2), len(v)) for k, v in g.items()), key=lambda x: -x[1])


def suggestions(factory, brand, rows: list[dict], n: int = 6) -> list[dict]:
    ranked = sorted(rows, key=lambda r: -r["rel"])
    top = [r for r in ranked[:5] if r["rel"] > 1]
    win_words = set().union(*(_words(r["title"]) for r in top)) if top else set()
    pillars = {k: v for k, v, _ in _groups(rows, "pillar")}
    out: list[dict] = []
    ideas = factory.db.query("SELECT id, title, angle, pillar, format FROM ideas WHERE brand = ? "
                             "AND status IN ('new', 'approved') ORDER BY id DESC LIMIT 300", [brand.slug])
    scored = sorted(ideas, key=lambda i: -(len(win_words & _words(f"{i['title']} {i['angle']}"))
                                           + pillars.get(i["pillar"], 1.0)))
    for i in scored[: n // 2]:
        if win_words & _words(f"{i['title']} {i['angle']}") or pillars.get(i["pillar"], 0) > 1:
            out.append({"topic": i["title"], "why": f"idea #{i['id']} in your backlog; looks like this week's winners"
                        + (f" ({i['pillar']})" if i["pillar"] else "")})
    for r in top[:2]:
        out.append({"topic": f"Follow-up to “{r['title'][:70]}”",
                    "why": f"{r['rel']}x your usual views on {r['platform']}: answer the next question it raises"})
    seen = {r.get("pillar") for r in rows if r.get("pillar")}
    for p in brand.pillars:
        if p not in seen and len(out) < n:
            out.append({"topic": f"Something from “{p}”", "why": "no posts from this pillar in the latest exports"})
    return out[:n]


def brand_page(factory, brand) -> dict:
    from .stats import scorecard
    card = scorecard(factory, brand.slug)
    rows = _rows(factory, brand.slug)
    ranked = sorted(rows, key=lambda r: -r["rel"])
    return {"brand": brand, "card": card, "best": ranked[:3], "worst": ranked[-3:][::-1] if len(ranked) > 3 else [],
            "formats": _groups(rows, "format"), "pillars": _groups(rows, "pillar"),
            "ideas": suggestions(factory, brand, rows), "has_data": bool(rows or card["site"])}


CSS = """
:root{--bg:#f7f6f2;--card:#fff;--ink:#16181d;--muted:#5f6670;--line:#e3e1da;--ok:#1a7f4b;--bad:#b42318;--acc:%s}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121417;--card:#1b1e23;--ink:#eceae4;--muted:#9aa1ab;--line:#2c3036}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:960px;margin:0 auto;padding:24px 16px 48px}h1{font-size:1.6rem;margin:0}h2{font-size:1.05rem;margin:0 0 10px}
.sub{color:var(--muted);margin:4px 0 20px}.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(min(100%%,200px),1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:12px}
.tile .n{font-size:1.5rem;font-weight:700;font-variant-numeric:tabular-nums}.tile .l{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.04em}
.up{color:var(--ok)}.down{color:var(--bad)}table{width:100%%;border-collapse:collapse;font-size:.9rem}
th{text-align:left;color:var(--muted);font-weight:600;font-size:.75rem;text-transform:uppercase}td,th{padding:7px 6px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0}.num{text-align:right;font-variant-numeric:tabular-nums}.bar{height:6px;border-radius:3px;background:var(--acc)}
ol{margin:0;padding-left:20px}li{margin:6px 0}.why{color:var(--muted);font-size:.85rem}.two{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(min(100%%,380px),1fr))}
a{color:inherit}
"""


def _e(x) -> str:
    return html.escape(str(x if x is not None else ""))


def _post_rows(items: list[dict]) -> str:
    if not items:
        return "<p class='why'>Not enough posts yet.</p>"
    body = "".join(f"<tr><td>{_e(r['title'][:80])}</td><td>{_e(r['platform'])}</td>"
                   f"<td class='num'>{int(r['views']):,}</td><td class='num'>{r['rel']}x</td></tr>" for r in items)
    return f"<table><tr><th>Post</th><th>Where</th><th class='num'>Views</th><th class='num'>vs usual</th></tr>{body}</table>"


def _group_rows(items: list[tuple[str, float, int]]) -> str:
    if not items:
        return "<p class='why'>Match posts to imports to see this (titles or video IDs).</p>"
    top = max(v for _, v, _ in items) or 1
    return "<table>" + "".join(
        f"<tr><td>{_e(k)}</td><td style='width:40%'><div class='bar' style='width:{min(100, v / top * 100):.0f}%'></div></td>"
        f"<td class='num'>{v}x</td><td class='num why'>{n}</td></tr>" for k, v, n in items) + "</table>"


def to_html(page: dict, week: str) -> str:
    b, c = page["brand"], page["card"]
    acc = (b.visual.palette[2] if len(b.visual.palette) > 2 else "#3aa0ff")
    tiles = []
    for name, p in c["platforms"].items():
        change = ""
        if p["prev_views"]:
            pct = (p["views"] - p["prev_views"]) / p["prev_views"] * 100
            change = f" <span class='{'up' if pct >= 0 else 'down'}'>{pct:+.0f}%</span>"
        extra = f" · CTR {p['ctr']}%" if p["ctr"] is not None else ""
        tiles.append(f"<div class='card tile'><div class='l'>{_e(name)} views</div><div class='n'>{int(p['views']):,}{change}</div>"
                     f"<div class='why'>{p['watch_hours']} watch hours{extra} · +{int(p['subscribers'])} subscribers</div></div>")
    if c["site"]:
        s = c["site"]
        tiles.append(f"<div class='card tile'><div class='l'>site visitors</div><div class='n'>{s['visitors']:,}</div>"
                     f"<div class='why'>{s['signups']} signups · {s['clicks']} clicks</div></div>")
    ideas = "".join(f"<li>{_e(i['topic'])}<div class='why'>{_e(i['why'])}</div></li>" for i in page["ideas"])
    body = (f"<div class='grid'>{''.join(tiles)}</div>"
            f"<div class='two'><div class='card'><h2>Best posts</h2>{_post_rows(page['best'])}</div>"
            f"<div class='card'><h2>Worst posts</h2>{_post_rows(page['worst'])}</div></div>"
            f"<div class='two'><div class='card'><h2>By format</h2>{_group_rows(page['formats'])}</div>"
            f"<div class='card'><h2>By pillar</h2>{_group_rows(page['pillars'])}</div></div>"
            f"<div class='card'><h2>Suggested next topics</h2><ol>{ideas or '<li>Import a few weeks of exports first.</li>'}</ol></div>"
            ) if page["has_data"] else (
            "<div class='card'><p>No exports imported yet. Download them from YouTube Studio, TikTok and Plausible, then run "
            f"<code>factory stats import --brand {_e(b.slug)} &lt;files&gt;</code>.</p></div>")
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{_e(b.name)} weekly</title><style>{CSS % acc}</style></head><body><main>"
            f"<h1>{_e(b.name)}: week of {_e(week)}</h1><p class='sub'>From your imported analytics exports. "
            "“vs usual” is views against that platform's median, so TikTok and YouTube compare fairly.</p>"
            f"{body}</main></body></html>")


def save(factory, end: date | None = None) -> list[Path]:
    end = end or date.today()
    week = (end - timedelta(days=end.weekday())).isoformat()
    out = factory.settings.output_dir / "reports" / f"week-{week}"
    out.mkdir(parents=True, exist_ok=True)
    made, links = [], []
    for slug, brand in factory.brands().items():
        page = brand_page(factory, brand)
        path = out / f"{slug}.html"
        path.write_text(to_html(page, week))
        made.append(path)
        best = page["best"][0]["title"][:60] if page["best"] else "no data yet"
        links.append(f"<li><a href='{slug}.html'>{_e(brand.name)}</a> <span class='why'>best: {_e(best)}</span></li>")
    (out / "index.html").write_text(
        f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>Weekly reports</title><style>{CSS % '#3aa0ff'}</style></head><body><main><h1>Week of {week}</h1>"
        f"<div class='card'><ul>{''.join(links)}</ul></div></main></body></html>")
    return [out / "index.html", *made]
