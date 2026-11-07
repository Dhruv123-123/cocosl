"""`factory challenge`: a multi-day savings challenge for any brand, with daily posts and a tracker.

    factory challenge new --brand money-made-simple --days 30 --kind ladder --start 2026-12-01 --import
    factory challenge schedule <slug> --brand money-made-simple   # approved day posts, one a day from --start

Kinds (amounts are worked out here, and the totals in every caption are summed from them):
* ladder:    day d saves d x step ($1, $2, ... $30 = $465 over 30 days)
* fixed:     --target split evenly over the days (remainder spread over the first days)
* envelope:  the ladder amounts in a shuffled order (seeded, so a rebuild gives the same order)
* no-spend:  one no-spend day each day; the tracker counts days, not dollars

Writes output/challenges/<brand>/<slug>/:
    tracker.png / tracker.pdf   printable tracker (A4 portrait, 300 dpi) to colour in
    tracker-post.png            1080x1350 version to post on day 0
    day-01.png ... day-NN.png   each day's post: today's amount, the tracker filled to that day
    captions/day-NN.txt         caption per day (tip of the day, running total, CTA)
    kickoff.json                3 short-video scripts (kickoff, halfway, finish) in `factory import` format
    schedule.csv                the day-by-day plan

With --import the day posts go into review as single-image posts (each with a different tip of the
day, so they're not near-duplicates) and the three scripts are imported (and rendered unless
--no-render). Nothing is scheduled or posted until you approve and run `factory challenge schedule`.
"""
from __future__ import annotations

import csv
import json
import random
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

KINDS = ("ladder", "fixed", "envelope", "no-spend")

TIPS = [
    "Move today's amount the moment you see this post. Money you can see in checking gets spent.",
    "Open a separate savings account with a nickname like 'Challenge'. A named pot is harder to raid.",
    "Check your last 30 days of card spending for one subscription you forgot about. Cancel it today.",
    "Before any purchase over $20 today, wait 24 hours. Most of the urge is gone by tomorrow.",
    "Pack lunch tomorrow and put the difference straight into the challenge pot.",
    "Unsubscribe from three store emails. Fewer sale alerts means fewer 'deals' you didn't need.",
    "Look at your phone and internet bills. A five-minute call asking for a loyalty rate often works.",
    "Round up: if today's amount feels easy, add a few dollars. Future you will notice.",
    "Sell one thing you haven't used in a year. Clutter in the closet is cash on a shelf.",
    "Turn off one-click checkout on the shopping apps you use most. A little friction saves a lot.",
    "Write down every purchase today, even the small ones. Just noticing changes what you buy.",
    "Plan tomorrow's meals tonight. Most takeout happens when there's no plan at 6 pm.",
    "Check whether your savings account pays a real rate. If it pays almost nothing, compare a few.",
    "Set up an automatic transfer for payday, even a small one, so saving happens before spending.",
    "Use what's already in the pantry for one meal today and save the grocery money you didn't spend.",
    "Review your insurance deductibles and premiums once a year; today is a good day to diarise it.",
    "Borrow before you buy: a library, a neighbour or a friend might have exactly what you need.",
    "Make coffee at home today and drop what you'd have spent into the pot.",
    "Delete saved card details from one shopping site. Typing the number in makes you think twice.",
    "Halfway habits stick: tell one friend about the challenge, or invite them to do it with you.",
    "Check your bank fees from last month. Overdraft or maintenance fees are often avoidable.",
    "Have a free night in: a walk, a film you already own, a game night. Note what you didn't spend.",
    "Batch your errands into one trip. Fewer trips means less fuel and fewer impulse stops.",
    "Look for a cheaper version of one thing you buy every week, and try it once.",
    "Give each savings goal a date and an amount. 'Emergency fund: $1,000 by March' beats 'save more'.",
    "Return anything you bought this month and haven't used. Receipts in a drawer are refunds waiting.",
    "Turn down the heating or air conditioning by a degree or two for the rest of the challenge.",
    "Before you buy something, work out how many hours of work it costs. Then decide.",
    "Check your progress on the tracker. Every coloured box is a decision you made on purpose.",
    "Decide now what the money is for once the challenge ends, so it doesn't drift back into spending.",
    "Look back at the month: which tip saved you the most? Keep that one going next month.",
    "Pick one category (clothes, games, gadgets) to pause buying for the rest of the challenge.",
    "Use cash for one spending category this week. Handing over notes feels different to tapping a card.",
    "Write a short list before you go shopping today, and buy only what's on it.",
    "Ask for a price match or a discount once today. The worst answer is no.",
    "Find one free thing in your area this week: a park, a museum day, a community event.",
]


@dataclass
class Day:
    n: int
    amount: int
    total: int
    tip: str


def amounts(kind: str, days: int, step: int = 1, target: int = 0, seed: str = "") -> list[int]:
    if kind == "ladder":
        return [d * step for d in range(1, days + 1)]
    if kind == "envelope":
        vals = [d * step for d in range(1, days + 1)]
        random.Random(seed or "envelope").shuffle(vals)
        return vals
    if kind == "fixed":
        if target <= 0:
            raise ValueError("fixed needs --target (the total to save)")
        base, extra = divmod(target, days)
        return [base + (1 if d < extra else 0) for d in range(days)]
    if kind == "no-spend":
        return [0] * days
    raise ValueError(f"kind must be one of {', '.join(KINDS)}")


def plan(kind: str, days: int, step: int = 1, target: int = 0, seed: str = "") -> list[Day]:
    out, total = [], 0
    tips = TIPS[:]
    random.Random(seed or kind).shuffle(tips)
    for i, a in enumerate(amounts(kind, days, step, target, seed), start=1):
        total += a
        out.append(Day(i, a, total, tips[(i - 1) % len(tips)]))
    return out


def title_of(kind: str, days: int, total: int) -> str:
    if kind == "no-spend":
        return f"{days}-day no-spend challenge"
    return f"{days}-day ${total:,} savings challenge"


# --------------------------------------------------------------------------- graphics
def _palette(brand):
    from .media.util import Palette
    return Palette.from_brand(brand)


def tracker(brand, days: list[Day], kind: str, size: tuple[int, int], filled: int, out: Path,
            headline: str = "", sub: str = "") -> Path:
    """Grid of day cells; the first `filled` are coloured in."""
    from .media import fonts
    from .media.signature import draw as draw_sig
    from .media.signature import resolve
    from .media.util import save_png_and_jpeg
    pal = _palette(brand)
    w, h = size
    k = w / 1080
    img = Image.new("RGBA", size, (*pal.light, 255))
    d = ImageDraw.Draw(img)
    from .media.util import contrast
    fill = max(pal.accents or [pal.dark], key=lambda a: contrast(a, pal.dark))  # done boxes: brightest accent
    done_ink = pal.dark if contrast(fill, pal.dark) >= 4.5 else pal.light
    fam = brand.visual.font
    margin = int(70 * k)
    head = headline or title_of(kind, len(days), days[-1].total)
    hb = fonts.fit(head, fonts.font_path(fam, "black"), w - 2 * margin, int(170 * k), int(88 * k), int(40 * k),
                   leading=1.05, max_lines=2)
    fonts.draw_block(img, hb, (margin, int(70 * k)), (*pal.dark, 255))
    y0 = int(70 * k) + hb.height + int(20 * k)
    if sub:
        f = fonts.load(fonts.font_path(fam, "semibold"), int(34 * k))
        d.text((margin, y0), sub, font=f, fill=(*pal.dark, 200), anchor="lt")
        y0 += int(60 * k)
    cols = 5 if len(days) <= 35 else 7 if len(days) <= 70 else 10
    rows = -(-len(days) // cols)
    gap = int(14 * k)
    bottom = h - int(130 * k)
    cell = min((w - 2 * margin - gap * (cols - 1)) // cols, (bottom - y0 - gap * (rows - 1)) // rows)
    gx = (w - (cell * cols + gap * (cols - 1))) // 2
    fnum = fonts.load(fonts.font_path(fam, "semibold"), max(12, int(cell * 0.2)))
    famt = fonts.load(fonts.font_path(fam, "black"), max(14, int(cell * (0.26 if kind != "no-spend" else 0.22))))
    for i, day in enumerate(days):
        r, c = divmod(i, cols)
        x, y = gx + c * (cell + gap), y0 + r * (cell + gap)
        done = i < filled
        d.rounded_rectangle((x, y, x + cell, y + cell), radius=int(cell * 0.14),
                            fill=(*fill, 255) if done else (*pal.light, 255),
                            outline=(*pal.dark, 255 if done else 90), width=max(2, int(3 * k)))
        ink = (*(done_ink if done else pal.dark), 255)
        d.text((x + int(cell * 0.12), y + int(cell * 0.1)), f"{day.n}", font=fnum, fill=ink, anchor="lt")
        label = "done" if kind == "no-spend" and done else ("no spend" if kind == "no-spend" else f"${day.amount:,}")
        d.text((x + cell // 2, y + int(cell * 0.62)), label, font=famt, fill=ink, anchor="mm")
    f = fonts.load(fonts.font_path(fam, "semibold"), int(30 * k))
    d.text((margin, h - int(60 * k)), f"{brand.name}  ·  {brand.visual.watermark}".strip(" ·"), font=f,
           fill=(*pal.dark, 190), anchor="ls")
    img = draw_sig(img, resolve(brand), pal, fam) if resolve(brand) else img
    out.parent.mkdir(parents=True, exist_ok=True)
    save_png_and_jpeg(img, out)
    return out


# --------------------------------------------------------------------------- content
def caption(brand, kind: str, day: Day, n_days: int, total: int, tag: str) -> str:
    if kind == "no-spend":
        lead = f"Day {day.n} of {n_days}: a no-spend day. Only essentials today (rent, bills, groceries you planned)."
    else:
        lead = (f"Day {day.n} of {n_days}: save ${day.amount:,} today. That's ${day.total:,} so far of the "
                f"${total:,} goal.")
    return f"{lead}\n\nTip of the day: {day.tip}\n\nColour in today's box on your tracker. {brand.cta}"


def day_script(brand, kind: str, day: Day, n_days: int, total: int) -> dict:
    head = f"Day {day.n}: no spend" if kind == "no-spend" else f"Day {day.n}: save ${day.amount:,}"
    return {"title": f"{title_of(kind, n_days, total)}: day {day.n}", "hook": head,
            "segments": [{"heading": head, "narration": day.tip, "on_screen_text": head, "visual_prompt": "tracker"}],
            "cta": brand.cta, "caption": "", "hashtags": [], "description": "", "thumbnail_text": head,
            "sources": [], "claims_to_verify": [], "title_variants": [], "hook_variants": []}


def video_scripts(brand, kind: str, days: list[Day]) -> list[dict]:
    n, total = len(days), days[-1].total
    name = title_of(kind, n, total)
    half = days[n // 2 - 1]
    rules = ("Each day has one no-spend day: only essentials, nothing extra." if kind == "no-spend" else
             f"Each day has an amount on the tracker. Day one is ${days[0].amount:,}; it adds up to ${total:,}.")

    def seg(h, n_, o):
        return {"heading": h, "narration": n_, "on_screen_text": o, "visual_prompt": "a savings tracker grid, flat vector"}

    def script(title, hook, segs):
        return {"title": title, "hook": hook, "segments": segs, "cta": brand.cta,
                "caption": f"{hook} Grab the tracker and start today. {brand.cta}",
                "hashtags": [], "description": "", "thumbnail_text": title[:30], "sources": [],
                "claims_to_verify": ["Check the totals on the tracker match the daily amounts"],
                "title_variants": [], "hook_variants": []}
    return [
        {"format": "short", "pillar": "", "script": script(
            f"Start the {name}", f"Let's do a {name}, starting today.",
            [seg("The idea", f"Let's do a {name}, starting today.", name),
             seg("The rules", rules, "The rules"),
             seg("The tracker", "Download the tracker, put it on the fridge, and colour in a box every day.",
                 "Colour a box a day"),
             seg("Why it works", "Small daily wins are easier to keep than one big promise.", "Small wins stick")])},
        {"format": "short", "pillar": "", "script": script(
            f"Halfway through the {name}", f"We're halfway through the {name}.",
            [seg("Halfway", f"We're halfway through the {name}.", "Halfway there"),
             seg("Where you are", "No-spend days so far: " + str(half.n) if kind == "no-spend" else
                 f"If you've kept up, you've saved ${half.total:,} so far.",
                 f"{half.n} days" if kind == "no-spend" else f"${half.total:,} saved"),
             seg("Missed days", "Missed a day? Don't restart. Catch up this weekend and keep going.",
                 "Missed a day? Keep going"),
             seg("Next", "The second half is where the habit sets in.", "Second half")])},
        {"format": "short", "pillar": "", "script": script(
            f"You finished the {name}", f"The {name} is done.",
            [seg("Done", f"The {name} is done.", "You did it"),
             seg("The result", f"{n} no-spend days in a row." if kind == "no-spend" else
                 f"Every box coloured in means ${total:,} saved.",
                 f"{n} days" if kind == "no-spend" else f"${total:,}"),
             seg("Keep it", "Give the money a job now: an emergency fund, a debt, or a goal with a date.",
                 "Give it a job"),
             seg("Again?", "Want to go again? Start the next one on the first of the month.", "Go again")])},
    ]


def slug_for(kind: str, days: int, start: date) -> str:
    return f"{kind}-{days}d-{start:%Y-%m}"


def build(factory, brand_slug: str, kind: str = "ladder", days: int = 30, step: int = 1, target: int = 0,
          start: date | None = None) -> dict:
    brand = factory.brand(brand_slug)
    if not 7 <= days <= 100:
        raise ValueError("days: 7 to 100")
    start = start or (date.today() + timedelta(days=1))
    slug = slug_for(kind, days, start)
    plan_days = plan(kind, days, step, target, seed=f"{brand.slug}:{slug}")
    total = plan_days[-1].total
    out = factory.settings.output_dir / "challenges" / brand.slug / slug
    (out / "captions").mkdir(parents=True, exist_ok=True)
    tag = re.sub(r"[^a-z0-9]", "", f"{days}day{'nospend' if kind == 'no-spend' else 'savings'}challenge")
    printable = tracker(brand, plan_days, kind, (2480, 3508), 0, out / "tracker.png",
                        sub="Colour in a box every day")
    Image.open(printable).convert("RGB").save(out / "tracker.pdf", resolution=300)
    tracker(brand, plan_days, kind, (1080, 1350), 0, out / "tracker-post.png", sub="Save this, then colour a box a day")
    rows = []
    for day in plan_days:
        sub = "No-spend day" if kind == "no-spend" else f"Today: ${day.amount:,} · so far ${day.total:,}"
        tracker(brand, plan_days, kind, (1080, 1350), day.n, out / f"day-{day.n:02d}.png",
                headline=f"Day {day.n} of {days}", sub=sub)
        cap = caption(brand, kind, day, days, total, tag)
        (out / "captions" / f"day-{day.n:02d}.txt").write_text(cap + "\n")
        rows.append({"day": day.n, "date": (start + timedelta(days=day.n - 1)).isoformat(), "amount": day.amount,
                     "total": day.total, "tip": day.tip})
    with open(out / "schedule.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    videos = video_scripts(brand, kind, plan_days)
    (out / "kickoff.json").write_text(json.dumps(videos, indent=2))
    meta = {"slug": slug, "brand": brand.slug, "kind": kind, "days": days, "total": total,
            "start": start.isoformat(), "tag": tag}
    (out / "challenge.json").write_text(json.dumps(meta, indent=2))
    return {**meta, "dir": out, "plan": plan_days}


def import_posts(factory, built: dict, render_videos: bool = True) -> list[int]:
    """Day posts into review as single-image posts; the 3 video scripts through the normal import."""
    from .db import now_iso
    brand = factory.brand(built["brand"])
    out_root = factory.settings.output_dir
    ids = []
    tags = [built["tag"], *[t for t in brand.hashtags[:3]]]
    for day in built["plan"]:
        rel = (built["dir"] / f"day-{day.n:02d}.png").relative_to(out_root).as_posix()
        cap = (built["dir"] / "captions" / f"day-{day.n:02d}.txt").read_text().strip()
        pid = factory.db.insert("posts", {
            "brand": brand.slug, "format": "image", "status": "rendered",
            "title": f"{title_of(built['kind'], built['days'], built['total'])}: day {day.n}",
            "script": day_script(brand, built["kind"], day, built["days"], built["total"]),
            "caption": cap, "hashtags": tags, "disclosure": brand.ai_disclosure,
            "meta": {"challenge": built["slug"], "challenge_day": day.n, "llm": "challenge", "human_edited": True},
            "assets": {"slides": [rel], "images": [], "video": None, "thumbnail": None, "duration": 0.0,
                       "provenance": [{"path": rel, "source": "rendered", "tool": "pillow",
                                       "prompt": f"challenge tracker day {day.n}", "license": "", "created_at": now_iso()}]},
        })
        factory.check(pid)
        ids.append(pid)
    for item in json.loads((built["dir"] / "kickoff.json").read_text()):
        ids.append(factory.import_script(brand.slug, item["script"], item["format"], render=render_videos,
                                         source="challenge"))
    factory.db.log("challenge.imported", "", None, {"slug": built["slug"], "posts": ids})
    return ids


def schedule(factory, brand_slug: str, slug: str) -> list[int]:
    """Schedule the approved day posts one a day from the start date, at the brand's first post time."""
    brand = factory.brand(brand_slug)
    meta = json.loads((factory.settings.output_dir / "challenges" / brand.slug / slug / "challenge.json").read_text())
    start = date.fromisoformat(meta["start"])
    hh, mm = (brand.cadence.post_times or ["12:00"])[0].split(":")
    tz = ZoneInfo(brand.cadence.timezone)
    pubs = []
    for post in factory.db.query("SELECT * FROM posts WHERE brand = ? AND status = 'approved' ORDER BY id", [brand.slug]):
        m = post.get("meta") or {}
        if m.get("challenge") != slug:
            continue
        when = datetime.combine(start + timedelta(days=int(m["challenge_day"]) - 1), time(int(hh), int(mm)), tz)
        pubs += factory.schedule(post["id"], at=when)
    return pubs


def register(sub, factory_fn) -> None:
    c = sub.add_parser("challenge", help="multi-day savings challenge: daily posts + printable tracker")
    cs = c.add_subparsers(dest="challenge_cmd", required=True)
    s = cs.add_parser("new", help="build the challenge (and with --import, put the posts into review)")
    s.add_argument("--brand", required=True)
    s.add_argument("--kind", choices=KINDS, default="ladder")
    s.add_argument("--days", type=int, default=30)
    s.add_argument("--step", type=int, default=1, help="ladder/envelope: dollars per step")
    s.add_argument("--target", type=int, default=0, help="fixed: total to save")
    s.add_argument("--start", type=date.fromisoformat, default=None, help="first day, YYYY-MM-DD (default tomorrow)")
    s.add_argument("--import", dest="do_import", action="store_true")
    s.add_argument("--no-render", action="store_true", help="with --import: queue the 3 videos instead of rendering")

    def new(a):
        f = factory_fn(a)
        built = build(f, a.brand, a.kind, a.days, a.step, a.target, a.start)
        print(f"{built['slug']}: {title_of(a.kind, a.days, built['total'])} -> {built['dir']}")
        if a.do_import:
            ids = import_posts(f, built, render_videos=not a.no_render)
            print(f"{len(ids)} posts in review. After approving: factory challenge schedule {built['slug']} "
                  f"--brand {a.brand}")
    s.set_defaults(func=new)

    s = cs.add_parser("schedule", help="schedule the approved day posts, one a day from the start date")
    s.add_argument("slug")
    s.add_argument("--brand", required=True)

    def sched(a):
        print(f"{len(schedule(factory_fn(a), a.brand, a.slug))} publication(s) scheduled")
    s.set_defaults(func=sched)
