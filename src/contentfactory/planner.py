"""One calendar across every brand, and one to-do list of what's waiting on you.

    factory calendar --days 14                      # table + any problems
    factory calendar --export output/calendar       # also calendar.ics (subscribe in any calendar app)
                                                    # and calendar.html (a week grid)
    factory recordings                              # posts waiting on your voice or a screen recording

Problems flagged on the calendar:
* over cap: a brand has more posts on a platform that local day than
  cadence.max_posts_per_day_per_platform, or more of a format in 7 days than
  its weekly cadence;
* collision: two brands post to the same platform within COLLIDE_MINUTES of
  each other (90 by default). It matters most when they share an account or a
  login, and it also spreads the work you check by hand.
"""
from __future__ import annotations

import html
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ACTIVE = ("queued", "publishing", "published", "dry_run", "needs_check", "manual")


def _zone(name: str):
    try:
        return ZoneInfo(name)
    except Exception:
        return timezone.utc


def is_manual(platform: str) -> bool:
    from .manual import is_manual as _m
    return _m(platform)


def entries(factory, days: int = 14, start: datetime | None = None) -> list[dict]:
    start = start or datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=days)
    rows = factory.db.query(
        f"""SELECT pub.id pub_id, pub.platform, pub.status, pub.scheduled_at, pub.account, s.id post_id, s.brand,
                   s.format, s.title FROM publications pub JOIN posts s ON s.id = pub.post_id
            WHERE pub.status IN ({','.join('?' * len(ACTIVE))}) AND pub.scheduled_at >= ? AND pub.scheduled_at < ?
            ORDER BY pub.scheduled_at, s.brand""", [*ACTIVE, start.isoformat(), end.isoformat()])
    brands = factory.brands()
    for r in rows:
        b = brands.get(r["brand"])
        tz = _zone(b.cadence.timezone) if b else timezone.utc
        r["at"] = datetime.fromisoformat(r["scheduled_at"])
        r["local"] = r["at"].astimezone(tz)
        r["flags"] = []
        r["by_hand"] = is_manual(r["platform"])
    return rows


def flag(factory, rows: list[dict], collide_minutes: int | None = None) -> list[str]:
    """Annotate rows with problems; returns one line per problem."""
    from .scheduler import WEEKLY_CAP
    collide = timedelta(minutes=collide_minutes if collide_minutes is not None
                        else int(os.environ.get("COLLIDE_MINUTES", "90")))
    brands = factory.brands()
    problems: list[str] = []
    day = defaultdict(list)
    for r in rows:
        day[(r["brand"], r["platform"], r["local"].date())].append(r)
    for (brand, platform, d), items in sorted(day.items(), key=lambda kv: (kv[0][2], kv[0][0], kv[0][1])):
        b = brands.get(brand)
        cap = b.cadence.max_posts_per_day_per_platform if b else None
        if cap and len(items) > cap:
            msg = f"{d} {brand} has {len(items)} posts on {platform} (cap {cap})"
            problems.append("over cap: " + msg)
            for r in items:
                r["flags"].append(f"over daily cap ({len(items)}/{cap})")
    # weekly per-format cadence: any 7-day window starting at a post
    by_fmt = defaultdict(list)
    for r in rows:
        by_fmt[(r["brand"], r["platform"], r["format"])].append(r)
    for (brand, platform, fmt), items in by_fmt.items():
        b = brands.get(brand)
        limit = getattr(b.cadence, WEEKLY_CAP.get(fmt, ""), None) if b else None
        if not limit:
            continue
        for i, r in enumerate(items):
            window = [x for x in items[i:] if x["at"] < r["at"] + timedelta(days=7)]
            if len(window) > limit:
                problems.append(f"over cap: {brand} has {len(window)} {fmt} posts on {platform} in the 7 days "
                                f"from {r['local'].date()} (weekly cadence {limit})")
                for x in window:
                    if "over weekly cadence" not in x["flags"]:
                        x["flags"].append("over weekly cadence")
                break
    by_platform = defaultdict(list)
    for r in rows:
        by_platform[r["platform"]].append(r)
    for platform, items in by_platform.items():
        items.sort(key=lambda r: r["at"])
        for a, b2 in zip(items, items[1:]):
            if a["brand"] != b2["brand"] and b2["at"] - a["at"] < collide:
                same = a.get("account") and a.get("account") == b2.get("account")
                gap = int((b2["at"] - a["at"]).total_seconds() // 60)
                problems.append(f"collision: {a['brand']} and {b2['brand']} both post to {platform} within "
                                f"{gap} min at {a['at']:%Y-%m-%d %H:%M} UTC" + (" on the SAME account" if same else ""))
                for x in (a, b2):
                    x["flags"].append(f"collides with {b2['brand'] if x is a else a['brand']} on {platform}")
    return problems


# ---------------------------------------------------------------- exports
def _ics_text(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def to_ics(rows: list[dict], duration_minutes: int = 15) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//contentfactory//calendar//EN", "CALSCALE:GREGORIAN",
             "X-WR-CALNAME:Content calendar"]
    for r in rows:
        start = r["at"].astimezone(timezone.utc)
        end = start + timedelta(minutes=duration_minutes)
        summary = f"[{r['brand']}] {r['platform']} {r['format']}: {r['title']}"
        desc = f"Post #{r['post_id']}, publication #{r['pub_id']}, status {r['status']}"
        if r.get("by_hand"):
            summary = "POST BY HAND: " + summary
            desc += "\nThe factory doesn't upload this one. Open the package (factory manual) and post it from the app."
        if r["flags"]:
            summary = "⚠ " + summary
            desc += "\nProblems: " + "; ".join(r["flags"])
        lines += ["BEGIN:VEVENT", f"UID:pub-{r['pub_id']}@contentfactory", f"DTSTAMP:{stamp}",
                  f"DTSTART:{start:%Y%m%dT%H%M%SZ}", f"DTEND:{end:%Y%m%dT%H%M%SZ}",
                  f"SUMMARY:{_ics_text(summary)[:250]}", f"DESCRIPTION:{_ics_text(desc)}",
                  "END:VEVENT"]
    lines.append("END:VCALENDAR")
    # RFC 5545: CRLF line endings, lines folded at 75 octets
    out = []
    for line in lines:
        raw = line.encode()
        while len(raw) > 75:
            cut = 75
            while cut > 0 and (raw[cut] & 0xC0) == 0x80:  # don't split a UTF-8 character
                cut -= 1
            out.append(raw[:cut].decode())
            raw = b" " + raw[cut:]
        out.append(raw.decode())
    return "\r\n".join(out) + "\r\n"


COLORS = ["#2563eb", "#16a34a", "#d97706", "#9333ea", "#dc2626", "#0891b2", "#4d7c0f"]


def to_html(rows: list[dict], problems: list[str], start: datetime, days: int) -> str:
    brands = sorted({r["brand"] for r in rows})
    color = {b: COLORS[i % len(COLORS)] for i, b in enumerate(brands)}
    cells = defaultdict(list)
    for r in rows:
        cells[r["at"].astimezone(timezone.utc).date()].append(r)
    weeks = []
    d0 = start.date() - timedelta(days=start.weekday())
    for w in range((days + start.weekday()) // 7 + 1):
        week = []
        for i in range(7):
            d = d0 + timedelta(days=7 * w + i)
            items = "".join(
                f'<div class="item{" bad" if r["flags"] else ""}" style="border-left-color:{color[r["brand"]]}" '
                f'title="{html.escape("; ".join(r["flags"]) or r["status"])}">'
                f'<b>{r["at"]:%H:%M}</b> {html.escape(r["platform"])} · {html.escape(r["format"])}'
                f'{" · <em>post by hand</em>" if r.get("by_hand") else ""}<br>'
                f'<span>{html.escape(r["title"][:70])}</span></div>' for r in cells.get(d, []))
            week.append(f'<td><div class="d">{d:%a %b %d}</div>{items}</td>')
        weeks.append("<tr>" + "".join(week) + "</tr>")
    legend = " ".join(f'<span class="key" style="background:{color[b]}"></span>{html.escape(b)}' for b in brands)
    probs = "".join(f"<li>{html.escape(p)}</li>" for p in problems) or "<li>None: every brand is within its caps.</li>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Content calendar</title><style>
body{{font:14px system-ui,sans-serif;margin:16px;color:#111;background:#fff}}
table{{border-collapse:collapse;width:100%;table-layout:fixed}}td{{border:1px solid #ddd;vertical-align:top;padding:4px;height:90px}}
.d{{font-size:12px;color:#555;margin-bottom:4px}}.item{{border-left:4px solid;padding:2px 4px;margin:2px 0;background:#f6f7f9;font-size:12px}}
.item span{{color:#444}}.bad{{background:#fee2e2}}.key{{display:inline-block;width:12px;height:12px;margin:0 4px 0 12px;vertical-align:middle}}
@media(prefers-color-scheme:dark){{body{{background:#111;color:#eee}}td{{border-color:#333}}.item{{background:#1e1f23}}.item span{{color:#bbb}}.bad{{background:#4c1d1d}}.d{{color:#aaa}}}}
</style></head><body><h1>Content calendar</h1><p>Times are UTC. {legend}</p>
<h2>Problems</h2><ul>{probs}</ul><table>{''.join(weeks)}</table></body></html>"""


def export(factory, out_dir: Path, days: int = 28) -> dict:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = entries(factory, days, start)
    problems = flag(factory, rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "calendar.ics").write_text(to_ics(rows), newline="")
    (out_dir / "calendar.html").write_text(to_html(rows, problems, start, days))
    return {"publications": len(rows), "problems": problems, "ics": out_dir / "calendar.ics",
            "html": out_dir / "calendar.html"}


# ---------------------------------------------------------------- recordings to-do
def recordings(factory) -> list[dict]:
    """Posts waiting on the owner: a narration take (brand.own_voice or meta.own_voice) or footage
    (a long video's planned original element, or a footage file that isn't on disk yet)."""
    from .media.tts import human_voice_source
    home = factory.settings.home
    brands = factory.brands()
    todo = []
    for post in factory.db.query("SELECT * FROM posts WHERE status NOT IN ('rejected','published','failed') "
                                 "AND format IN ('short','mid','long') ORDER BY id"):
        brand = brands.get(post["brand"])
        if not brand:
            continue
        script = post.get("script") or {}
        segs = script.get("segments") or []
        needs = []
        if (brand.own_voice or (post.get("meta") or {}).get("own_voice")) and \
                human_voice_source(factory.settings, brand, post["id"]) is None:
            needs.append(f"voice: record the narration, then `factory voice {post['id']} <file>`")
        for i, s in enumerate(segs):
            f = (s.get("footage") or "").strip()
            if f and not ((Path(f).expanduser() if Path(f).is_absolute() else home / f).is_file()):
                needs.append(f"footage: beat {i + 1} expects {f}")
        from .originality import element_text
        planned = element_text(script.get("original_element"))
        if post["format"] == "long" and planned and not any(s.get("chart") or s.get("footage") for s in segs):
            needs.append(f"screen recording: {planned[:140]}")
        if not needs:
            continue
        when = factory.db.scalar("SELECT MIN(scheduled_at) FROM publications WHERE post_id = ? AND status = 'queued'",
                                 [post["id"]])
        todo.append({"post_id": post["id"], "brand": post["brand"], "format": post["format"],
                     "title": post["title"], "status": post["status"], "publish_at": when or "", "needs": needs})
    return sorted(todo, key=lambda t: (t["publish_at"] == "", t["publish_at"], t["post_id"]))


def register(sub, factory_fn) -> None:
    s = sub.add_parser("recordings", help="posts waiting on your voice or a screen recording, soonest first")

    def run(a):
        todo = recordings(factory_fn(a))
        if not todo:
            print("Nothing waiting on you.")
            return
        for t in todo:
            when = t["publish_at"][:16].replace("T", " ") + " UTC" if t["publish_at"] else "not scheduled"
            print(f"#{t['post_id']} [{t['brand']}] {t['format']} · {when} · {t['title']}")
            for n in t["needs"]:
                print(f"    - {n}")
    s.set_defaults(func=run)
