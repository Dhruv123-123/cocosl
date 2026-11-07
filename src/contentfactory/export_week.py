"""`factory export-week <brand>`: one zip per week with everything to post by hand, in posting order.

    factory export-week money-made-simple                  # this week (Monday-Sunday, brand time zone)
    factory export-week money-made-simple --week 2026-11-23 --weeks 4   # four zips from that week
    factory export-week money-made-simple --manual-only    # only TikTok / Pinterest (MANUAL_PLATFORMS)

Each zip (output/export-week/<brand>/<brand>-week-<monday>.zip) holds one folder per publication, named
so they sort in posting order (`01-Mon-0900-tiktok-post-12/`), with the same files as a post-by-hand
package: video or pin image, caption.txt (or title/description/link for pins and YouTube), POST_AT.txt.
At the top, WEEK.md lists every post with its time and the full caption ready to paste, and
schedule.csv has one row per post. Only publications whose post's review status is approved (see `factory review-gate`) are included (queued, manual
or dry run), so nothing unreviewed goes in. Nothing is posted; publications keep their status.
"""
from __future__ import annotations

import csv
import io
import shutil
import tempfile
import zipfile
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

STATUSES = ("queued", "manual", "dry_run")


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def publications(factory, brand, monday: date, manual_only: bool = False) -> list[dict]:
    try:
        tz = ZoneInfo(brand.cadence.timezone)
    except Exception:
        tz = timezone.utc
    start = datetime.combine(monday, time(0), tz).astimezone(timezone.utc)
    end = start + timedelta(days=7)
    rows = factory.db.query(
        f"""SELECT pub.* FROM publications pub JOIN posts s ON s.id = pub.post_id
            WHERE s.brand = ? AND pub.status IN ({','.join('?' * len(STATUSES))})
            AND s.status NOT IN ('rejected', 'failed', 'in_review', 'blocked')
            AND pub.scheduled_at >= ? AND pub.scheduled_at < ? ORDER BY pub.scheduled_at, pub.id""",
        [brand.slug, *STATUSES, start.isoformat(), end.isoformat()])
    from .review import status as review_status
    rows = [r for r in rows if review_status(factory.db.get("posts", r["post_id"]), brand) == "approved"]
    if manual_only:
        from .manual import manual_platforms
        rows = [r for r in rows if r["platform"] in manual_platforms()]
    for r in rows:
        r["local"] = datetime.fromisoformat(r["scheduled_at"]).astimezone(tz)
    return rows


def export(factory, slug: str, monday: date, manual_only: bool = False) -> Path | None:
    from .manual import build_package
    brand = factory.brand(slug)
    pubs = publications(factory, brand, monday, manual_only)
    if not pubs:
        return None
    out = factory.settings.output_dir / "export-week" / slug
    out.mkdir(parents=True, exist_ok=True)
    zpath = out / f"{slug}-week-{monday.isoformat()}.zip"
    week = [f"# {brand.name}: week of {monday:%a %d %b %Y}", "",
            f"{len(pubs)} post(s), in posting order. Times are {brand.cadence.timezone}. Every caption already "
            "has the AI disclosure; turn on each app's AI-generated label too.", ""]
    sheet = io.StringIO()
    w = csv.writer(sheet)
    w.writerow(["n", "local_time", "utc", "platform", "post_id", "publication_id", "title", "folder"])
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / f"{slug}-week-{monday.isoformat()}"
        root.mkdir()
        for n, pub in enumerate(pubs, 1):
            post = factory.db.get("posts", pub["post_id"])
            name = f"{n:02d}-{pub['local']:%a-%H%M}-{pub['platform']}-post-{post['id']}"
            d = root / name
            try:
                build_package(factory, pub, post, dest=d)
                req = factory.build_request(post, pub["platform"])
            except Exception as e:  # one bad post shouldn't sink the week
                d.mkdir(exist_ok=True)
                (d / "PROBLEM.txt").write_text(f"Couldn't build this package: {e}\nFix it on the post page, then export again.\n")
                week += [f"## {n}. {pub['local']:%a %d %b %H:%M} · {pub['platform']} · #{post['id']} {post.get('title', '')}",
                         "", f"**Couldn't build: {e}**", ""]
                continue
            if pub["platform"] == "youtube":
                (d / "title.txt").write_text((req.title or post.get("title") or "") + "\n")
                (d / "description.txt").write_text((req.description or "") + "\n")
            files = sorted(p.name for p in d.iterdir())
            caption = (d / "description.txt").read_text() if pub["platform"] == "pinterest" else \
                (d / "caption.txt").read_text() if (d / "caption.txt").exists() else ""
            week += [f"## {n}. {pub['local']:%a %d %b %H:%M} · {pub['platform']} · #{post['id']} {post.get('title', '')}",
                     "", f"Folder `{name}/`: {', '.join(files)}", ""]
            if (d / "title.txt").exists():
                week += ["Title:", "", "```", (d / "title.txt").read_text().strip(), "```", ""]
            week += ["Caption:" if pub["platform"] != "youtube" else "Description:", "", "```",
                     (caption if pub["platform"] != "youtube" else (d / "description.txt").read_text()).strip(), "```", ""]
            if (d / "link.txt").exists():
                week += [f"Link: {(d / 'link.txt').read_text().strip()}", ""]
            week += [f"Then: `factory manual done {pub['id']} --url <link>` (or Mark posted on the Today page)", ""]
            w.writerow([n, pub["local"].strftime("%Y-%m-%d %H:%M"), pub["scheduled_at"], pub["platform"], post["id"],
                        pub["id"], post.get("title", ""), name])
        (root / "WEEK.md").write_text("\n".join(week))
        (root / "schedule.csv").write_text(sheet.getvalue())
        tmpzip = Path(tmp) / "out.zip"
        with zipfile.ZipFile(tmpzip, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(root.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(root.parent))
        shutil.move(str(tmpzip), zpath)
    return zpath


def register(sub, factory_fn) -> None:
    s = sub.add_parser("export-week", help="one zip per week: every scheduled post in posting order, captions "
                                           "ready to paste, for posting by hand")
    s.add_argument("brand")
    s.add_argument("--week", type=date.fromisoformat, default=None, help="any day in the first week (default: this week)")
    s.add_argument("--weeks", type=int, default=1, help="how many weeks, one zip each")
    s.add_argument("--manual-only", action="store_true", help="only the platforms in MANUAL_PLATFORMS")

    def cmd(a):
        f = factory_fn(a)
        if a.brand not in f.brands():
            raise SystemExit(f"Unknown brand '{a.brand}'. Brands: {', '.join(f.brands())}")
        monday = week_start(a.week or date.today())
        made = 0
        for k in range(max(1, a.weeks)):
            m = monday + timedelta(weeks=k)
            path = export(f, a.brand, m, a.manual_only)
            if path:
                made += 1
                print(f"Week of {m}: {path}")
            else:
                print(f"Week of {m}: nothing scheduled")
        if not made:
            print("Nothing to export. Approve and schedule posts first (`factory schedule`).")
    s.set_defaults(func=cmd)
