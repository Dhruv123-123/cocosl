"""Ready-to-post content packs: content.json -> a posting calendar plus one folder per post.

    factory pack plan   --brand money-made-simple --file month.json --start 2026-11-21 --days 30
    factory pack export --brand money-made-simple --file month.json --start 2026-11-21 --days 30 --out month-1/

`plan` only prints the calendar. `export` also imports every item into the review queue (nothing is
approved), renders carousel slides and video thumbnails, and writes for each post a folder with the
media and a caption.txt holding the exact caption (brand AI disclosure and any affiliate disclosure
included), the facts to check before posting and, for videos, the narration script. It also writes
POSTING_PLAN.md, calendar.csv, calendar.ics and CHECKS.md (guardrail results per post).

A short may carry `tiktok_extra` (segments for a 60-90s TikTok cut) and `series` (e.g. "Rate My Budget").
The TikTok cut is written to tiktok-cut.json beside the post and printed in caption.txt; it is not imported as
a separate post, since it is the same video for another platform.

Slots come from the brand cadence: shorts at the first post time on short days (to every account that
takes shorts), carousels at the last post time on carousel days, long videos at the last post time on
long days. Items fill slots in file order, so order the file the way you want it to go out. Days left
empty get leftover items. Nothing is published by this module; the human review gate still applies.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import BrandProfile

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DEFAULT_DAYS = {
    "short": ["mon", "tue", "thu", "fri", "sat"],
    "carousel": ["mon", "wed", "fri"],
    "long": ["sun"],
    "mid": ["sun"],  # TikTok-only 65-90 s video (accounts whose formats include "mid")
}
FORMATS = ("short", "carousel", "long", "mid")
AFFILIATE_RE = re.compile(r"affiliate link|commission", re.I)


@dataclass
class Slot:
    day: int                    # 1-based day number in the window
    when: datetime              # local time
    fmt: str
    platforms: list[str]
    index: int | None = None    # position in the content list
    title: str = ""
    tags: list[str] = field(default_factory=list)
    folder: str = ""
    post_id: int | None = None

    @property
    def label(self) -> str:
        return f"Day {self.day} · {self.when.strftime('%a %b')} {self.when.day}"


def parse_days(spec: str | None, fmt: str) -> list[int]:
    names = [d.strip().lower()[:3] for d in spec.split(",")] if spec else DEFAULT_DAYS[fmt]
    bad = [d for d in names if d not in WEEKDAYS]
    if bad:
        raise ValueError(f"Unknown weekday(s) for {fmt}: {', '.join(bad)} (use mon,tue,...)")
    return [WEEKDAYS.index(d) for d in names]


def platforms_for(brand: BrandProfile, fmt: str) -> list[str]:
    return [a.platform for a in brand.accounts if fmt in a.formats]


def revenue_tags(brand: BrandProfile, caption: str) -> list[str]:
    tags = []
    if AFFILIATE_RE.search(caption) or any(a.url in caption for a in brand.affiliates):
        tags.append("affiliate")
    for p in brand.products:
        name = (p.get("name") if isinstance(p, dict) else getattr(p, "name", "")) or ""
        short = name.split("(")[0].strip()
        if short and short.lower() in caption.lower():
            tags.append("product")
            break
    return tags


def plan(brand: BrandProfile, items: list[dict], start: date, days: int,
         day_spec: dict[str, str | None] | None = None) -> tuple[list[Slot], list[int]]:
    """Return (filled slots sorted by time, indexes of items that didn't fit)."""
    day_spec = day_spec or {}
    tz = ZoneInfo(brand.cadence.timezone)
    times = brand.cadence.post_times or ["12:30", "19:00"]
    early, late = times[0], times[-1]
    at = {"short": early, "carousel": late, "long": late, "mid": late}
    weekdays = {fmt: parse_days(day_spec.get(fmt), fmt) for fmt in DEFAULT_DAYS}
    cap = brand.cadence.max_posts_per_day_per_platform

    def local(d: date, hhmm: str) -> datetime:
        h, m = (int(x) for x in hhmm.split(":"))
        return datetime(d.year, d.month, d.day, h, m, tzinfo=tz)

    queues = {fmt: [i for i, it in enumerate(items) if it.get("format") == fmt] for fmt in DEFAULT_DAYS}
    slots: list[Slot] = []
    for n in range(days):
        d = start + timedelta(days=n)
        for fmt in FORMATS:
            if d.weekday() in weekdays[fmt] and queues[fmt]:
                slots.append(Slot(n + 1, local(d, at[fmt]), fmt, platforms_for(brand, fmt), queues[fmt].pop(0)))

    # Empty days get leftovers (short first, then carousel), still inside the per-platform cap.
    used_days = {s.day for s in slots}
    for n in range(days):
        if n + 1 in used_days:
            continue
        d = start + timedelta(days=n)
        for fmt in FORMATS:
            if queues[fmt]:
                slots.append(Slot(n + 1, local(d, at[fmt]), fmt, platforms_for(brand, fmt), queues[fmt].pop(0)))

    # Enforce the per-platform daily cap (drops the platform from later slots that day).
    per_day: dict[tuple[int, str], int] = {}
    for s in sorted(slots, key=lambda s: s.when):
        keep = []
        for p in s.platforms:
            k = (s.day, p)
            if per_day.get(k, 0) < cap:
                per_day[k] = per_day.get(k, 0) + 1
                keep.append(p)
        s.platforms = keep

    for s in slots:
        sc = items[s.index]["script"]
        s.title = sc["title"]
        s.tags = revenue_tags(brand, sc.get("caption", ""))
        if items[s.index].get("series"):
            s.tags.insert(0, items[s.index]["series"])
        if items[s.index].get("tiktok_extra"):
            s.tags.append("TikTok long cut")
    leftover = [i for q in queues.values() for i in q]
    return sorted(slots, key=lambda s: s.when), leftover


# ---------------------------------------------------------------- output files
def slugify(text: str, n: int = 52) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:n].strip("-")


WORDS_PER_SECOND = 2.6


def est_seconds(lines: list[str]) -> int:
    """Rough spoken length, before pauses and the closing call to action."""
    return round(sum(len(x.split()) for x in lines) / WORDS_PER_SECOND)


def tiktok_segments(item: dict) -> list[dict]:
    """The long TikTok cut: the base script with `tiktok_extra` inserted before its last segment.

    Research (Nov 2026) found 60-90s TikToks break out about twice as often as short ones, while Reels and
    Shorts don't reward length, so shorts can carry an optional `tiktok_extra` list of segments."""
    segs = item["script"]["segments"]
    extra = item.get("tiktok_extra") or []
    return segs[:-1] + extra + segs[-1:] if extra else list(segs)


def caption_txt(brand: BrandProfile, item: dict, slot: Slot | None) -> str:
    sc = item["script"]
    tags = " ".join(f"#{t.lstrip('#')}" for t in sc.get("hashtags", []))
    lines = [sc["title"], f"Format: {item['format']}"]
    if slot:
        lines.append(f"Post: {slot.when.strftime('%a %b %d, %Y %H:%M')} {brand.cadence.timezone} "
                     f"→ {', '.join(slot.platforms)}")
    lines += ["", "--- CAPTION (paste as-is) ---", sc["caption"].strip(), "", brand.ai_disclosure.strip(), "", tags, ""]
    if item["format"] == "long" and sc.get("description"):
        lines += ["--- YOUTUBE DESCRIPTION ---", sc["description"].strip(), "", brand.ai_disclosure.strip(), ""]
    lines.append("--- CHECK BEFORE POSTING ---")
    lines += [f"[ ] {c}" for c in sc.get("claims_to_verify", [])]
    lines += ["[ ] Platform AI-label toggle set where required", "", "Sources:"]
    lines += sc.get("sources", [])
    if item.get("tiktok_extra"):
        base = [s["narration"] for s in sc["segments"]]
        cut = [s["narration"] for s in tiktok_segments(item)]
        lines += ["", f"--- NARRATION: Reels / Shorts cut (~{est_seconds(base)}s) ---"] + base
        lines += ["", f"--- NARRATION: TikTok cut (~{est_seconds(cut)}s, adds a worked example) ---"] + cut
    elif item["format"] in ("short", "long", "mid"):
        lines += ["", "--- NARRATION SCRIPT ---"] + [s["narration"] for s in sc["segments"]]
    else:
        lines += ["", "--- SLIDE TEXT ---"] + [f"{i + 1}. {s['on_screen_text']}" for i, s in enumerate(sc["segments"])]
    return "\n".join(lines).rstrip() + "\n"


def plan_markdown(brand: BrandProfile, items: list[dict], slots: list[Slot], leftover: list[int],
                  start: date, days: int) -> str:
    end = start + timedelta(days=days - 1)
    counts = {f: sum(1 for s in slots if s.fmt == f) for f in DEFAULT_DAYS}
    out = [f"# {brand.name}: {days}-day posting plan", "",
           f"Window: {start.strftime('%a %b')} {start.day} – {end.strftime('%a %b')} {end.day}, {end.year}. "
           f"All times {brand.cadence.timezone}.",
           f"{counts['short']} shorts, {counts['carousel']} carousels, {counts['long']} long videos"
           + (f", {counts['mid']} TikTok-only videos." if counts["mid"] else "."), "",
           "Rules this plan follows:",
           f"- At most {brand.cadence.max_posts_per_day_per_platform} posts per platform per day (brand cap).",
           f"- Shorts go to {', '.join(platforms_for(brand, 'short')) or 'no account'} at the first post time; "
           f"carousels to {', '.join(platforms_for(brand, 'carousel')) or 'no account'} and long videos to "
           f"{', '.join(platforms_for(brand, 'long')) or 'no account'} at the last post time.",
           "- Before each post: human review in the dashboard, tick every line under CHECK BEFORE POSTING, keep the "
           "AI disclosure in the caption and set the platform AI-label toggle where required.",
           "- Revenue pieces are marked: **affiliate** (has the affiliate disclosure) and **product** (mentions the "
           "product). Make sure the link-in-bio page has both links on those days.", "",
           "| Day | Time | Platform(s) | Folder | Format | Piece |", "|---|---|---|---|---|---|"]
    for s in slots:
        tag = f" · **{' + '.join(s.tags)}**" if s.tags else ""
        out.append(f"| {s.label} | {s.when.strftime('%H:%M')} | {', '.join(s.platforms)} | {s.folder or '—'} "
                   f"| {s.fmt} | {s.title}{tag} |")
    if leftover:
        out += ["", "Spare pieces (not scheduled; use them if a post is pulled in review):", ""]
        out += [f"- {items[i]['format']}: {items[i]['script']['title']}" for i in leftover]
    return "\n".join(out) + "\n"


def write_calendar_files(brand: BrandProfile, slots: list[Slot], out: Path) -> None:
    with (out / "calendar.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["day", "date", "time", "timezone", "format", "platforms", "title", "revenue", "folder"])
        for s in slots:
            w.writerow([s.day, s.when.date().isoformat(), s.when.strftime("%H:%M"), brand.cadence.timezone, s.fmt,
                        "; ".join(s.platforms), s.title, "; ".join(s.tags), s.folder])
    stamp = datetime.now(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//contentfactory//{brand.slug}//EN"]
    for s in slots:
        utc = s.when.astimezone(ZoneInfo("UTC"))
        summary = f"Post {s.fmt}: {s.title}".replace(",", "\\,").replace(";", "\\;")
        ics += ["BEGIN:VEVENT", f"UID:{brand.slug}-{utc.strftime('%Y%m%dT%H%M')}-{s.index}@contentfactory",
                f"DTSTAMP:{stamp}", f"DTSTART:{utc.strftime('%Y%m%dT%H%M%SZ')}",
                f"DTEND:{(utc + timedelta(minutes=15)).strftime('%Y%m%dT%H%M%SZ')}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{', '.join(s.platforms)} · folder {s.folder}".replace(",", "\\,"), "END:VEVENT"]
    ics.append("END:VCALENDAR")
    (out / "calendar.ics").write_text("\r\n".join(ics) + "\r\n")


# ---------------------------------------------------------------- export
def export(factory, brand_slug: str, items: list[dict], out: Path, start: date, days: int,
           day_spec: dict | None = None, render_video: bool = False) -> dict:
    from .media.images import generate_images
    from .media.thumbnail import render_thumbnail
    from .media.util import Palette

    brand = factory.brand(brand_slug)
    slots, leftover = plan(brand, items, start, days, day_spec)
    out.mkdir(parents=True, exist_ok=True)
    by_index = {s.index: s for s in slots}
    order = [s.index for s in slots] + leftover
    checks_md = ["# Guardrail results", "", "Every post was run through the factory's checks (originality, "
                 "disclosures, testimonials, hype, engagement bait, asset rights). Warnings need a human look; "
                 "blocks must be fixed before posting.", ""]
    summary = {"posts": 0, "warn": 0, "block": 0}
    root = Path(factory.settings.output_dir).resolve()
    for n, idx in enumerate(order, start=1):
        item = items[idx]
        fmt = item["format"]
        slot = by_index.get(idx)
        group = "carousels" if fmt == "carousel" else ("videos" if render_video else "videos-need-voice")
        if slot is None and days:  # with --days 0 the whole file is an undated library
            group = "spares"
        folder = f"{group}/{n:02d}-{slugify(item['script']['title'])}"
        dest = out / folder
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True)
        render = fmt == "carousel" or render_video
        pid = factory.import_script(brand_slug, item["script"], fmt, item.get("pillar", ""),
                                    item.get("idea_angle", ""), render=render, source="pack")
        post = factory.db.get("posts", pid)
        assets = post.get("assets") or {}
        if fmt == "carousel":
            for i, rel in enumerate(assets.get("slides") or [], start=1):
                src = (root / rel).with_suffix(".jpg")
                shutil.copy(src if src.exists() else root / rel, dest / f"slide-{i:02d}{src.suffix}")
        else:
            if render_video and assets.get("video"):
                shutil.copy(root / assets["video"], dest / "video.mp4")
            if render_video and assets.get("thumbnail"):
                thumb = (root / assets["thumbnail"])
                shutil.copy(thumb.with_suffix(".jpg") if thumb.with_suffix(".jpg").exists() else thumb,
                            dest / "thumbnail.jpg")
            else:
                work = dest / "_art"
                art = generate_images(factory.settings, brand, [item["script"]["segments"][0]["visual_prompt"]],
                                      (1920, 1080), "16:9", work, family=f"{brand.slug}:{item['script']['title']}")
                t = render_thumbnail(art[0].path, item["script"]["thumbnail_text"] or item["script"]["title"],
                                     Palette.from_brand(brand), brand.visual.font, brand.visual.watermark,
                                     work / "thumbnail.png")
                jpg = t.with_suffix(".jpg")
                shutil.copy(jpg if jpg.exists() else t, dest / f"thumbnail{jpg.suffix if jpg.exists() else t.suffix}")
                shutil.rmtree(work, ignore_errors=True)
        if item.get("tiktok_extra"):
            cut = {**item["script"], "segments": tiktok_segments(item)}
            (dest / "tiktok-cut.json").write_text(json.dumps(cut, indent=1, ensure_ascii=False))
        if slot:
            slot.folder, slot.post_id = folder, pid
        (dest / "caption.txt").write_text(caption_txt(brand, item, slot))
        res = (factory.db.get("posts", pid) or {}).get("checks") or {}
        status = res.get("status", "ok")
        summary["posts"] += 1
        summary[status] = summary.get(status, 0) + 1
        flagged = [c for c in res.get("checks", []) if c.get("level") in ("warn", "block")]
        checks_md.append(f"- **{folder}** (post #{pid}): {status}")
        checks_md += [f"  - {c['level']}: {c.get('name', '')}: {c.get('message', '')}" for c in flagged]
    (out / "POSTING_PLAN.md").write_text(plan_markdown(brand, items, slots, leftover, start, days))
    write_calendar_files(brand, slots, out)
    (out / "CHECKS.md").write_text("\n".join(checks_md) + "\n")
    (out / "content.json").write_text(json.dumps(items, indent=1, ensure_ascii=False))
    return {**summary, "slots": len(slots), "spares": len(leftover), "out": str(out)}


# ---------------------------------------------------------------- CLI
def register(sub, factory_from_args) -> None:
    p = sub.add_parser("pack", help="plan or export a ready-to-post content pack from a content.json")
    p.add_argument("action", choices=["plan", "export"])
    p.add_argument("--brand", required=True)
    p.add_argument("--file", required=True, help="content.json (list of {format, pillar, idea_angle, script})")
    p.add_argument("--start", required=True, help="first day, YYYY-MM-DD")
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--out", help="output folder (export)")
    p.add_argument("--short-days", help="weekdays for shorts, e.g. mon,tue,thu,fri,sat")
    p.add_argument("--carousel-days", help="weekdays for carousels, e.g. mon,wed,fri")
    p.add_argument("--long-days", help="weekdays for long videos, e.g. sun")
    p.add_argument("--mid-days", help="weekdays for TikTok-only 65-90 s videos, e.g. sun")
    p.add_argument("--render-video", action="store_true", help="render full videos (needs a voice for narration)")

    def run(args):
        f = factory_from_args(args)
        items = json.loads(Path(args.file).read_text())
        start = date.fromisoformat(args.start)
        spec = {"short": args.short_days, "carousel": args.carousel_days, "long": args.long_days,
                "mid": args.mid_days}
        if args.action == "plan":
            brand = f.brand(args.brand)
            slots, leftover = plan(brand, items, start, args.days, spec)
            print(plan_markdown(brand, items, slots, leftover, start, args.days))
            return
        if not args.out:
            raise ValueError("--out is required for export")
        print(json.dumps(export(f, args.brand, items, Path(args.out), start, args.days, spec, args.render_video),
                         indent=1))

    p.set_defaults(func=run)
