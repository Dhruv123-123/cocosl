"""`factory weekly-review`: the Sunday one-pager. One read, about five minutes, before the week starts.

    factory weekly-review                 # this week (Monday to today), printed
    factory weekly-review --save          # also output/weekly-review/<sunday>.md and .html
    factory weekly-review --date 2026-11-29

Sections, for the brands in play (`factory launch-mode`):
1. Scorecard: each brand's headline numbers and its stop / change flags (from `factory scorecard`).
2. Time used: this week against the one-hour-a-day limit, and the last four weeks (`factory time`).
3. Brand-3 gates: the five gates from `factory scorecard --gate`, with "too early" before week 8.
4. Queued: next week's posts per brand and platform, and the day each queue runs out.
5. Blocked on you: everything only Dhruv can do: reviews waiting (incl. native / legal), post-by-hand
   items, red launch-check items, search-box checks, recordings, missing keys or brand-file placeholders.
The worker writes it every Sunday evening (after WEEKLY_REVIEW_AT, default 18:00 brand time). Nothing is
posted or changed, except that the scorecard history for this week is saved (as `scorecard --save` does).
"""
from __future__ import annotations

import html
import os
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone


def _brands(factory) -> list[str]:
    from .launchmode import active_brands
    act = active_brands(factory)
    return [s for s in factory.brands() if act is None or s in act]


def queued(factory, slug: str, day: date) -> dict:
    nxt = datetime.combine(day + timedelta(days=1), time(0), timezone.utc)
    end = nxt + timedelta(days=7)
    rows = factory.db.query(
        """SELECT p.platform, p.scheduled_at FROM publications p JOIN posts s ON s.id = p.post_id
           WHERE s.brand = ? AND p.status IN ('queued', 'manual', 'dry_run') AND p.scheduled_at >= ?""",
        [slug, nxt.isoformat()])
    week = [r for r in rows if r["scheduled_at"] < end.isoformat()]
    last = max((r["scheduled_at"] for r in rows), default="")
    return {"next_week": len(week), "by_platform": dict(Counter(r["platform"] for r in week)),
            "runs_out": last[:10], "days_left": (date.fromisoformat(last[:10]) - day).days if last else 0}


def blocked(factory, brands: list[str]) -> list[tuple[str, str, str]]:
    """(brand, what, how) for everything waiting on Dhruv."""
    from .keywords import load as kw_load, todo as kw_todo
    from .review import counts
    from .triage import collect as triage
    out: list[tuple[str, str, str]] = []
    keep = lambda b: b in brands or b == "-"  # noqa: E731
    items = [i for i in triage(factory) if keep(i.brand)]
    groups: dict = {}
    for i in items:
        kind = i.kind.split(" (")[0]
        groups.setdefault((i.urgency, i.brand, kind), []).append(i)
    for (urg, brand, kind), its in sorted(groups.items(), key=lambda x: ({"now": 0, "soon": 1, "setup": 2}[x[0][0]], x[0][1])):
        first = its[0]
        more = f" (+{len(its) - 1} more)" if len(its) > 1 else ""
        out.append((brand, f"{urg} · {kind}: {first.what}{more}", first.how))
    for slug, c in counts(factory).items():
        if slug not in brands:
            continue
        for stage in ("native_review", "legal_review"):
            if c.get(stage):
                out.append((slug, f"{c[stage]} post(s) waiting on {stage.replace('_', ' ')}",
                            f"`factory review-gate list --status {stage} --brand {slug}`"))
    try:
        kw = [r for r in kw_todo(kw_load(factory)) if r.brand in brands]
    except Exception:
        kw = []
    if kw:
        out.append(("-", f"{len(kw)} scheduled title(s) need the search-box check", "`factory keyword-check go` (about 10 min)"))
    return out


def collect(factory, day: date | None = None) -> dict:
    from .scorecard import collect as card, gate
    from .timelog import weeks
    day = day or date.today()
    brands = _brands(factory)
    cards = [card(factory, s, day) for s in brands]
    gates = gate(factory, brands, day) if brands else []
    return {"day": day, "monday": day - timedelta(days=day.weekday()), "brands": brands, "cards": cards,
            "time": weeks(factory, 5, day), "gates": gates, "queued": {s: queued(factory, s, day) for s in brands},
            "blocked": blocked(factory, brands)}


def _min(m: int) -> str:
    return f"{m // 60}h{m % 60:02d}" if m >= 60 else f"{m} min"


KEY_NUMBERS = (("yt_impressions", "YT impressions"), ("yt_ctr", "YT CTR %"), ("tt_avg_views", "TikTok avg views"),
               ("ig_reach", "IG reach"), ("site_visitors", "site visitors"), ("site_signups", "sign-ups"),
               ("money_revenue", "revenue $"))


def to_markdown(r: dict) -> str:
    d = r["day"]
    out = [f"# Weekly review · week of {r['monday']:%a %d %b %Y}", "",
           f"Brands in play: {', '.join(r['brands']) or 'none'} · written {d:%a %d %b}", ""]
    out += ["## 1. Scorecard", ""]
    for c in r["cards"]:
        nums = " · ".join(f"{label} {c['v'][k]}" for k, label in KEY_NUMBERS if c["v"].get(k) is not None) or "no numbers imported yet (`factory stats import`)"
        out.append(f"**{c['brand']}** (day {c['day'] if c['day'] is not None else '?'}): {nums}")
        hits = [f for f in c["flags"] if f.status == "flag" and f.severity in ("stop", "change")]
        for f in hits:
            out.append(f"- {f.severity.upper()}: {f.rule}" + (f" ({f.value})" if f.value else ""))
        if not hits:
            out.append("- no stop or change flags")
        out.append("")
    w = r["time"][0]
    out += ["## 2. Time used", "",
            f"This week: {_min(w['brand_min'])} on the brands of {_min(w['limit_week'])} allowed"
            + (f", over the hour on {', '.join(w['over_days'])}" if w["over_days"] else "")
            + (f" · plus {_min(w['total'] - w['brand_min'])} on ad studio / setup" if w["total"] > w["brand_min"] else ""),
            "Last 4 weeks: " + " · ".join(f"{x['monday']:%d %b} {'OK' if x['ok'] else ('none logged' if not x['total'] else 'OVER')}"
                                          for x in r["time"][1:]), ""]
    out += ["## 3. Brand-3 gates", ""]
    n_day = r["cards"][0]["day"] if r["cards"] else None
    if r["gates"] and (n_day is None or n_day < 56):
        out.append("Too early: the gates count from week 8 (day 56 after launch). Shown so you can see what's on track.")
    for g in r["gates"]:
        out.append(f"- {'PASS' if g['ok'] else 'FAIL'} · {g['gate']}: {g['detail']}")
    out += ["", "## 4. Queued for next week", ""]
    for s, q in r["queued"].items():
        plats = ", ".join(f"{p} {n}" for p, n in sorted(q["by_platform"].items())) or "nothing"
        warn = " · **under 2 weeks left: schedule more**" if q["days_left"] < 14 else ""
        out.append(f"- **{s}**: {q['next_week']} post(s) ({plats}); queue runs to {q['runs_out'] or 'nothing queued'}{warn}")
    out += ["", "## 5. Blocked on you", ""]
    if not r["blocked"]:
        out.append("Nothing. Good week.")
    for brand, what, how in r["blocked"]:
        out.append(f"- [{brand}] {what}" + (f" → {how}" if how else ""))
    return "\n".join(out) + "\n"


def to_html(md: str) -> str:
    """Tiny Markdown subset → one printable page (headings, bullets, bold, code)."""
    import re
    body = []
    in_list = False
    for line in md.splitlines():
        t = html.escape(line)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
        if line.startswith("- "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{t[2:]}</li>")
            continue
        if in_list:
            body.append("</ul>")
            in_list = False
        if line.startswith("## "):
            body.append(f"<h2>{t[3:]}</h2>")
        elif line.startswith("# "):
            body.append(f"<h1>{t[2:]}</h1>")
        elif line.strip():
            body.append(f"<p>{t}</p>")
    if in_list:
        body.append("</ul>")
    return ("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Weekly review</title><style>body{font:15px/1.5 system-ui,sans-serif;max-width:46rem;margin:2rem auto;"
            "padding:0 1rem;color:#1d1d1f;background:#fff}h2{margin-top:1.6rem;border-bottom:1px solid #ddd}"
            "code{background:#f2f2f2;padding:0 .25rem;border-radius:3px}li{margin:.2rem 0}</style></head><body>"
            + "\n".join(body) + "</body></html>\n")


def save(factory, day: date | None = None) -> tuple:
    r = collect(factory, day)
    md = to_markdown(r)
    d = factory.settings.output_dir / "weekly-review"
    d.mkdir(parents=True, exist_ok=True)
    sunday = r["monday"] + timedelta(days=6)
    p = d / f"{sunday.isoformat()}.md"
    p.write_text(md)
    p.with_suffix(".html").write_text(to_html(md))
    return p, md


def due_at() -> tuple[int, int]:
    raw = os.environ.get("WEEKLY_REVIEW_AT", "18:00")
    try:
        h, m = raw.split(":")
        return int(h), int(m)
    except ValueError:
        return 18, 0


def register(sub, factory_fn) -> None:
    s = sub.add_parser("weekly-review", help="Sunday one-pager: scorecard, time used, brand-3 gates, next week's "
                                             "queue, and everything blocked on you")
    s.add_argument("--date", type=date.fromisoformat, default=None)
    s.add_argument("--save", action="store_true", help="also write output/weekly-review/<sunday>.md and .html")

    def cmd(a):
        f = factory_fn(a)
        if a.save:
            p, md = save(f, a.date)
            print(md)
            print(f"Saved {p} (and .html)")
        else:
            print(to_markdown(collect(f, a.date)))
    s.set_defaults(func=cmd)
