#!/usr/bin/env python3
"""Rebuild the dated part of launch/money-made-simple/LAUNCH_WEEK.md from one setting: Day 1.

    python scripts/launch_week.py --day1 2026-11-16     # default; Dhruv's call
    python scripts/launch_week.py --day1 2026-11-16 --check

The launch set (content.json, Days 1-14 in POSTING_PLAN.md) runs from Day 1 up to the day before month 1
starts (Sat Nov 21, 2026), because month 1, the holiday add-on and the savings challenge are tied to real
dates (Black Friday, December). From then on the dated packs take over, and the unused launch pieces become
swap-ins. Every platform gets its own time (brand platform_times), and the script refuses a calendar where a
platform has two posts at one minute or more than the daily cap.

It also writes each scheduled launch piece's day into content.json as "date": "YYYY-MM-DD", so
`factory import` + approving keeps the table's days whatever order Dhruv approves in, and removes the date
from the swap-ins (they then take the next free slot). Re-run `factory import` after changing Day 1.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from contentfactory.config import load_brand  # noqa: E402
from contentfactory.pack import WEEKDAYS, plan  # noqa: E402

M = ROOT / "launch" / "money-made-simple"
DOC = M / "LAUNCH_WEEK.md"
START, END = "<!-- launch-week:start -->", "<!-- launch-week:end -->"
MONTH1 = date(2026, 11, 21)
PINS_PER_WEEK = 4
HANDOFF = date(2026, 11, 20)  # first dated post: the holiday add-on's Black Friday kickoff
CD = {"carousel": "mon,tue,wed,thu,fri"}


def items(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def launch_days() -> list[tuple[int, int, str]]:
    """(day, content index, format) for Days 1-14 of the original launch plan."""
    text = (M / "POSTING_PLAN.md").read_text().split("## Days 15")[0]
    rows = re.findall(r"^\| Day (\d+) · [^|]+\| [^|]+\| [^|]+\| #(\d+) \| (\w+) \|", text, re.M)
    seen, out = set(), []
    for d, i, f in rows:
        if (d, i) not in seen:
            seen.add((d, i))
            out.append((int(d), int(i), f))
    return out


def launch_dates(day1: date) -> dict[int, str]:
    """Content index -> "YYYY-MM-DD" for the launch pieces that post before the dated packs take over."""
    out = {}
    for d, i, _ in launch_days():
        when = day1 + timedelta(days=d - 1)
        if when < HANDOFF:
            out[i] = when.isoformat()
    return out


def dated_content(day1: date) -> str:
    """content.json with "date" (right after "format") on the scheduled pieces and none on the swap-ins."""
    want = launch_dates(day1)
    out = []
    for i, it in enumerate(items(M / "content.json")):
        it = {k: v for k, v in it.items() if k != "date"}
        if i in want:
            keys = list(it)
            at = keys.index("format") + 1 if "format" in keys else 0
            it = dict(list(it.items())[:at] + [("date", want[i])] + list(it.items())[at:])
        out.append(it)
    return json.dumps(out, indent=2, ensure_ascii=False)


def dated_packs(day1: date) -> list[tuple[str, list[dict], date, int, dict]]:
    chal = items(M / "savings-challenge" / "content.json")
    return [
        ("month 1", items(M / "month-1" / "content.json"), MONTH1, 30, {}),
        ("holiday", items(M / "holiday-2026" / "part-1" / "content.json"), date(2026, 11, 20), 30,
         {"short": "wed,sun", "carousel": "sun"}),
        ("savings challenge", chal[:7], date(2026, 11, 15), 43, {"mid": "sun"}),
        ("Myth vs Math", items(M / "myth-vs-math" / "content.json"), date(2026, 11, 21), 78, {"carousel": "sat"}),
    ]


def build(day1: date, brand) -> tuple[list[tuple], list[str], list[str]]:
    """Rows (when, platforms, source, fmt, title, folder-free note), notes, swap-in titles."""
    last = day1 + timedelta(days=13)
    launch = items(M / "content.json")
    rows, notes, swaps = [], [], []
    for d, i, f in launch_days():
        when = day1 + timedelta(days=d - 1)
        title = launch[i]["script"]["title"]
        if when >= HANDOFF:
            swaps.append(f"#{i} {f}: {title}")
            continue
        slots, _ = plan(brand, [launch[i]], when, 1, {f: WEEKDAYS[when.weekday()]})
        for s in slots:
            rows += [(w, ps, f"launch #{i}", f, title) for w, ps in s.groups()]
    for name, its, start, days, spec in dated_packs(day1):
        slots, _ = plan(brand, its, start, days, spec)
        for s in slots:
            d = s.when.date()
            if d < day1:
                notes.append(f"{name}: \"{s.title}\" was dated {d:%a %b %d}, before Day 1. Post it on Day 1 or drop it.")
            elif d <= last:
                rows += [(w, ps, name, s.fmt, s.title) for w, ps in s.groups()]
    rows.sort(key=lambda r: (r[0], r[1]))
    # A new Pinterest account starts at about 4 pins a week (scouting's playbook): keep the first 4 each week.
    kept, pins = [], {}
    for w, ps, src, fmt, title in rows:
        if "pinterest" in ps:
            wk = (w.date() - day1).days // 7
            if pins.get(wk, 0) >= PINS_PER_WEEK:
                notes.append(f"Pinterest skipped (4-a-week start): {w:%a %b %d} {fmt} \"{title}\" posts on its other platforms only.")
                ps = [p for p in ps if p != "pinterest"]
            else:
                pins[wk] = pins.get(wk, 0) + 1
        if ps:
            kept.append((w, ps, src, fmt, title))
    rows = kept
    minute, per_day = {}, {}
    for w, ps, *_ in rows:
        for p in ps:
            minute[(p, w)] = minute.get((p, w), 0) + 1
            per_day[(p, w.date())] = per_day.get((p, w.date()), 0) + 1
    bad = [k for k, v in minute.items() if v > 1]
    over = [k for k, v in per_day.items() if v > brand.cadence.max_posts_per_day_per_platform]
    if bad or over:
        raise SystemExit(f"collisions {bad} / over the daily cap {over}")
    return rows, notes, swaps


def section(day1: date, brand) -> str:
    rows, notes, swaps = build(day1, brand)
    last = day1 + timedelta(days=13)
    out = [START, "",
           f"**Day 1 = {day1:%a %b} {day1.day}, {day1.year}** (Dhruv's call; change it with "
           f"`python scripts/launch_week.py --day1 YYYY-MM-DD`, which rewrites this section). "
           f"Window: {day1:%a %b} {day1.day} – {last:%a %b} {last.day}. All times America/New_York.", ""]
    if day1 < HANDOFF:
        out.append(f"The launch set runs Days 1–{(HANDOFF - day1).days}. From Fri Nov 20 the dated packs take over "
                   "(the holiday add-on's Black Friday kickoff, then month 1 from Nov 21, the savings challenge "
                   "and Myth vs Math), because they're tied to Black Friday and December.")
    out += ["", "| Day | Date | Time | Platform(s) | From | Format | Piece |", "|---|---|---|---|---|---|---|"]
    for w, ps, src, fmt, title in rows:
        out.append(f"| {(w.date() - day1).days + 1} | {w:%a %b} {w.day} | {w:%H:%M} | {', '.join(ps)} | {src} "
                   f"| {fmt} | {title} |")
    if notes:
        out += ["", "**Notes:**", ""] + [f"- {n}" for n in notes]
    if swaps:
        out += ["", "**Launch pieces that don't fit before the dated packs start** (swap-ins; use one when a dated post is "
                "pulled in review):", ""] + [f"- {s}" for s in swaps]
    out += ["", END]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day1", default="2026-11-16")
    ap.add_argument("--check", action="store_true", help="exit 1 if LAUNCH_WEEK.md is out of date")
    ap.add_argument("--stdout", action="store_true", help="print the section instead of writing it")
    a = ap.parse_args()
    brand = load_brand(ROOT / "brands", "money-made-simple")
    new = section(date.fromisoformat(a.day1), brand)
    if a.stdout:
        print(new)
        return
    text = DOC.read_text()
    cur = text[text.index(START): text.index(END) + len(END)]
    content = dated_content(date.fromisoformat(a.day1))
    if a.check:
        sys.exit(0 if cur == new and (M / "content.json").read_text() == content else 1)
    DOC.write_text(text.replace(cur, new))
    (M / "content.json").write_text(content)
    print(f"wrote {DOC.relative_to(ROOT)} and the launch dates in content.json for Day 1 = {a.day1}")


if __name__ == "__main__":
    main()
