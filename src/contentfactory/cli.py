"""`factory` command line.

Run `factory --help` for the full list. Everything the dashboard does is also
available here so it can run from cron or n8n.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from .config import Settings


def _factory(args):
    from .pipeline import Factory
    return Factory.create(Settings.load(args.home))


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, default=str))


def _table(rows: list[dict], cols: list[str]) -> None:
    if not rows:
        print("(none)")
        return
    widths = {c: max(len(c), *(len(str(r.get(c, ""))[:60]) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    print("  ".join("-" * widths[c] for c in cols))
    for r in rows:
        print("  ".join(str(r.get(c, ""))[:60].ljust(widths[c]) for c in cols))


# ---------------------------------------------------------------------------- core
def cmd_init(args):
    home = Path(args.home or ".").resolve()
    pkg_root = Path(__file__).resolve().parents[2]
    examples = Path(__file__).resolve().parent / "examples"  # shipped in the wheel for pip installs
    (home / "brands").mkdir(parents=True, exist_ok=True)
    example_brand = pkg_root / "brands" / "money-made-simple.yaml"
    if not example_brand.exists():
        example_brand = examples / "money-made-simple.yaml"
    if example_brand.exists() and not any((home / "brands").glob("*.yaml")):
        shutil.copy(example_brand, home / "brands" / example_brand.name)
    env_example = pkg_root / ".env.example"
    if not env_example.exists():
        env_example = examples / "env.example"
    if env_example.exists() and not (home / ".env").exists():
        shutil.copy(env_example, home / ".env")
        try:
            (home / ".env").chmod(0o600)  # it will hold API keys and tokens: owner only
        except OSError:
            pass
    s = Settings.load(home)
    from .db import DB
    DB(s.db_path)
    print(f"Initialised factory in {home}\n  db: {s.db_path}\n  brands: {s.brands_dir}\n  output: {s.output_dir}")
    print("Next: edit brands/*.yaml and .env, then run `factory status`.")


def cmd_status(args):
    f = _factory(args)
    from .publish import credential_status
    print(f"LLM provider: {f.llm.provider} ({f.settings.anthropic_model if f.llm.provider == 'anthropic' else 'no API calls'})")
    print(f"Dry run: {'ON (nothing is posted)' if f.settings.dry_run else 'OFF (posts go live)'}")
    print(f"Brands: {', '.join(f.brands()) or 'none'}")
    counts = f.db.query("SELECT status, COUNT(*) n FROM posts GROUP BY status")
    print("Posts: " + (", ".join(f"{r['status']}={r['n']}" for r in counts) or "none"))
    print("\nPlatform credentials:")
    for platform, missing in credential_status(f.settings).items():
        print(f"  {platform:10s} {'ready' if not missing else 'missing ' + ', '.join(missing)}")
    from .health import system_status
    st = system_status(f)
    print("\nPublications: " + (", ".join(f"{k}={v}" for k, v in st["publications"].items()) or "none"))
    rq = {k: v for k, v in st["render_queue"].items() if k != "recent_failures" and v}
    print("Render queue: " + (", ".join(f"{k}={v}" for k, v in rq.items()) or "empty"))
    hb = st["worker"]["heartbeat"]
    print("Worker: " + (f"last tick {st['worker']['minutes_since']} min ago" if hb else "not running"))
    for a in st["alerts"]:
        print(f"  ! {a}")


def cmd_brands(args):
    f = _factory(args)
    rows = [{"slug": b.slug, "name": b.name, "niche": b.niche,
             "accounts": ", ".join(a.platform for a in b.accounts if a.enabled)} for b in f.brands().values()]
    _table(rows, ["slug", "name", "niche", "accounts"])


def cmd_ideas(args):
    f = _factory(args)
    if args.action == "generate":
        ids = f.ideas(args.brand, n=args.n, online=not args.offline)
        print(f"Added {len(ids)} ideas")
    from .ideas import top_ideas
    rows = top_ideas(f.db, args.brand, limit=args.limit, status=args.status)
    _table(rows, ["id", "score", "format", "title"])


def cmd_idea_status(args):
    f = _factory(args)
    f.db.update("ideas", args.id, {"status": args.status})
    print(f"Idea #{args.id} -> {args.status}")


def cmd_produce(args):
    f = _factory(args)
    ids = list(args.ids)
    if args.brand and args.top:
        from .ideas import top_ideas
        ids += [i["id"] for i in top_ideas(f.db, args.brand, limit=args.top)]
    for idea_id in ids:
        post_id = f.produce(idea_id, render=not args.no_render, notes=args.notes or "")
        post = f.db.get("posts", post_id)
        print(f"Idea #{idea_id} -> post #{post_id} [{post['status']}] {post['title']}")
        for c in post["checks"].get("checks", []):
            if c["level"] != "ok":
                print(f"    {c['level'].upper():5s} {c['name']}: {c['message']}")


def cmd_review(args):
    f = _factory(args)
    if args.id is None:
        rows = f.db.query("SELECT id, brand, format, status, title FROM posts WHERE status IN ('in_review','blocked') ORDER BY id")
        _table(rows, ["id", "brand", "format", "status", "title"])
        return
    post = f.db.get("posts", args.id)
    if not post:
        sys.exit(f"No post #{args.id}")
    script = post["script"]
    print(f"#{post['id']} [{post['status']}] {post['format']} - {post['title']}\n")
    print(f"HOOK: {script.get('hook')}\n")
    for i, seg in enumerate(script.get("segments", []), 1):
        print(f"{i}. [{seg.get('heading')}] {seg.get('narration')}\n   on screen: {seg.get('on_screen_text')}")
    print(f"\nCTA: {script.get('cta')}\n\nCAPTION:\n{post['caption']}\n\nDISCLOSURE: {post['disclosure']}")
    print("\nCLAIMS TO VERIFY:")
    for c in script.get("claims_to_verify", []):
        print(f"  [ ] {c}")
    print("\nCHECKS:")
    for c in post["checks"].get("checks", []):
        print(f"  {c['level'].upper():5s} {c['name']}: {c['message']}")
    assets = post.get("assets") or {}
    if assets:
        print("\nFILES:")
        for k in ("video", "thumbnail"):
            if assets.get(k):
                print(f"  {k}: {f.asset_path(assets[k])}")
        for p in assets.get("slides") or []:
            print(f"  slide: {f.asset_path(p)}")


def cmd_approve(args):
    f = _factory(args)
    if not args.yes_i_checked:
        post = f.db.get("posts", args.id)
        claims = (post.get("script") or {}).get("claims_to_verify") or []
        if claims:
            print("Confirm you fact-checked these claims (pass --yes-i-checked):")
            for c in claims:
                print(f"  - {c}")
            sys.exit(1)
    f.approve(args.id, notes=args.notes or "")
    print(f"Approved post #{args.id}")
    if args.schedule:
        at = datetime.fromisoformat(args.at) if args.at else None
        pubs = f.schedule(args.id, platforms=args.platform or None, at=at)
        for p in pubs:
            pub = f.db.get("publications", p)
            print(f"  scheduled {pub['platform']} at {pub['scheduled_at']}")


def cmd_reject(args):
    _factory(args).reject(args.id, args.reason or "")
    print(f"Rejected post #{args.id}")


def cmd_schedule(args):
    f = _factory(args)
    if args.all:
        res = f.schedule_approved(brand=args.brand)
        for pid, slots in res["scheduled"].items():
            print(f"#{pid}: {', '.join(slots)}")
        for pid, why in res["skipped"].items():
            print(f"#{pid}: skipped ({why})")
        print(f"{len(res['scheduled'])} scheduled, {len(res['skipped'])} skipped")
        return
    if args.id is None:
        raise ValueError("give a post id, or --all")
    at = datetime.fromisoformat(args.at) if args.at else None
    for p in f.schedule(args.id, platforms=args.platform or None, at=at):
        pub = f.db.get("publications", p)
        print(f"{pub['platform']}: {pub['scheduled_at']}")


def cmd_rerender(args):
    f = _factory(args)
    f.render(args.id)
    print(f"Re-rendered post #{args.id}: {f.db.get('posts', args.id)['status']}")


def cmd_calendar(args):
    from .planner import entries, export, flag
    from .scheduler import calendar
    f = _factory(args)
    rows = calendar(f.db, days=args.days, brand=args.brand)
    _table(rows, ["scheduled_at", "platform", "status", "brand", "format", "title"])
    problems = flag(f, entries(f, args.days))
    print("\nProblems:" if problems else "\nNo cap or collision problems.")
    for p in problems:
        print("  - " + p)
    if args.export:
        res = export(f, Path(args.export), days=max(args.days, 7))
        print(f"Wrote {res['ics']} (subscribe or import in any calendar app) and {res['html']}")


def cmd_publish(args):
    _print(_factory(args).publish_due())


def cmd_metrics(args):
    print(f"Captured {_factory(args).collect_metrics()} metric snapshots")


def cmd_daily(args):
    f = _factory(args)
    brands = [args.brand] if args.brand else list(f.brands())
    for b in brands:
        _print(f.daily(b, n_ideas=args.ideas, n_produce=args.produce, online=not args.offline))


def cmd_repurpose(args):
    from .repurpose import repurpose_post, text_drafts
    f = _factory(args)
    if args.text or args.text_only:
        paths = text_drafts(f, args.id, force=args.force)
        print("Drafts (edit, then post by hand):")
        for name, path in paths.items():
            print(f"  {name}: {path}")
        if args.text_only:
            return
    for pid in repurpose_post(f, args.id, n_shorts=args.shorts, carousel=not args.no_carousel,
                              render=not args.no_render):
        post = f.db.get("posts", pid)
        print(f"post #{pid} [{post['format']}/{post['status']}] {post['title']}")


def cmd_insights(args):
    from .insights import report, rescore_backlog
    f = _factory(args)
    if args.rescore and args.brand:
        print(f"Rescored {rescore_backlog(f.db, args.brand)} ideas")
    _print(report(f.db, brand=args.brand, days=args.days))


def cmd_import(args):
    """Safe to re-run: scripts already imported are skipped, and ones whose render never finished
    (an interrupted run) are rendered again instead of duplicated."""
    import os
    if args.queue:
        os.environ["RENDER_QUEUE"] = "1"
    f = _factory(args)
    items = json.loads(Path(args.file).read_text())
    for item in items[: args.limit or None]:
        title = (item.get("script") or {}).get("title", "")
        existing = None if args.force else f.db.one(
            "SELECT id, status FROM posts WHERE brand = ? AND title = ? AND status != 'rejected' ORDER BY id DESC",
            [args.brand, title])
        if existing and existing["status"] in ("scripted", "failed") and not args.no_render:
            f._render_or_queue(existing["id"], True)
            pid = existing["id"]
        elif existing:
            _pack_date(f, existing["id"], item.get("date"))
            print(f"post #{existing['id']} [{existing['status']}] {title}: already imported, skipped")
            continue
        else:
            script = dict(item["script"])
            for key in ("original_element", "related_video", "playlist"):  # packs sometimes keep these on the item
                if item.get(key) and not script.get(key):
                    script[key] = item[key]
            pid = f.import_script(args.brand, script, item["format"], item.get("pillar", ""),
                                  item.get("idea_angle", ""), render=not args.no_render,
                                  platforms=item.get("platforms"))
        _pack_review(f, pid, item.get("review"))
        _pack_date(f, pid, item.get("date"))
        post = f.db.get("posts", pid)
        print(f"post #{pid} [{post['format']}/{post['status']}] {post['title']}")


def _pack_date(f, pid: int, value) -> None:
    """A pack item's "date": "YYYY-MM-DD" (its day in the posting plan). Scheduling then uses that day's
    slots instead of the next free one, so the calendar matches the plan (LAUNCH_WEEK.md). A past date
    is ignored at scheduling time. Re-running import adds dates to posts already imported."""
    if not value:
        return
    from datetime import date as _date
    try:
        day = _date.fromisoformat(str(value)[:10]).isoformat()
    except ValueError:
        print(f"  post #{pid}: date '{value}' isn't YYYY-MM-DD, ignored")
        return
    post = f.db.get("posts", pid)
    meta = dict(post.get("meta") or {})
    if meta.get("plan_date") != day:
        meta["plan_date"] = day
        f.db.update("posts", pid, {"meta": meta})


def _pack_review(f, pid: int, value) -> None:
    """A pack item's "review": "native_review" | ["native_review", "legal_review"] marks the post (review gate)."""
    if not value:
        return
    from .review import normalize, required, require
    post = f.db.get("posts", pid)
    new = [s for s in normalize(value) if s not in required(post)]
    if not new:
        return
    try:
        require(f, pid, new, note="from the pack")
    except PermissionError as e:
        print(f"  post #{pid}: {e} (review marker not applied)")


def cmd_launch_pack(args):
    from .launch_pack import build_pack
    f = _factory(args)
    res = build_pack(f, args.brand, Path(args.file), Path(args.out),
                     render_videos=True if args.render_videos else None, extras=not args.no_extras)
    for r in res["items"]:
        print(f"post #{r['post_id']} [{r['format']}] {r['folder']}")
    print(f"\nPack written to {res['out']} (see CONTENTS.md). Everything is in the review queue, unapproved.")


def cmd_niche(args):
    from .niche import score_niche
    for n in args.niches:
        _print(score_niche(n, online=not args.offline).model_dump())


def cmd_new_brand(args):
    from .niche import generate_brand, write_brand
    f = _factory(args)
    data, slug = generate_brand(f.llm, args.niche, args.audience or "", args.platform)
    path = write_brand(f.settings.brands_dir, data, args.slug or slug, overwrite=args.force)
    print(f"Wrote {path}. Edit it, then: factory ideas generate --brand {args.slug or slug}")


def cmd_report(args):
    from .reports import save_report, to_markdown, weekly_report
    f = _factory(args)
    if args.html:
        from .weekly_html import save as save_html
        for path in save_html(f):
            print(path)
        return
    if args.save:
        print(save_report(f))
    else:
        print(to_markdown(weekly_report(f)))


def cmd_serve(args):
    import uvicorn
    from .web.app import create_app
    app = create_app(_factory(args))
    uvicorn.run(app, host=args.host, port=args.port)


def cmd_ui(args):
    """The dashboard on this machine only, opened at /today."""
    import threading
    import webbrowser

    import uvicorn

    from .web.app import create_app
    url = f"http://127.0.0.1:{args.port}/today"
    print(f"Dashboard: {url} (only reachable from this computer; Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(create_app(_factory(args)), host="127.0.0.1", port=args.port, log_level="warning")


def cmd_demo(args):
    """Offline end-to-end run that produces real files you can look at."""
    import os
    os.environ.setdefault("FACTORY_LLM", "offline")
    os.environ.setdefault("FACTORY_TTS", "auto")
    os.environ.setdefault("FACTORY_IMAGES", "auto")
    os.environ["FACTORY_DRY_RUN"] = "1"
    f = _factory(args)
    brand = args.brand or next(iter(f.brands()))
    ids = f.ideas(brand, n=8, online=False)
    made = []
    by_fmt = {}
    for idea_id in ids:
        fmt = f.db.get("ideas", idea_id)["format"]
        if fmt not in by_fmt:
            by_fmt[fmt] = idea_id
    for fmt, idea_id in by_fmt.items():
        pid = f.produce(idea_id)
        made.append(pid)
        print(f"{fmt:8s} post #{pid}: {f.db.get('posts', pid)['status']}")
    print(f"\nFiles are in {f.settings.output_dir}. Review them with `factory review <id>` or `factory serve`.")


# ---------------------------------------------------------------------------- parser
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="factory", description="AI content studio with a human in the loop")
    p.add_argument("--home", default=None, help="factory directory (default: $FACTORY_HOME or cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="create .env, brands/ and the database").set_defaults(func=cmd_init)
    sub.add_parser("status", help="providers, dry-run state, credentials").set_defaults(func=cmd_status)
    sub.add_parser("brands", help="list brand profiles").set_defaults(func=cmd_brands)

    s = sub.add_parser("ideas", help="generate or list ideas")
    s.add_argument("action", choices=["generate", "list"])
    s.add_argument("--brand", required=True)
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--status", default="new")
    s.add_argument("--offline", action="store_true", help="skip live trend signals")
    s.set_defaults(func=cmd_ideas)

    s = sub.add_parser("idea", help="set an idea's status")
    s.add_argument("id", type=int)
    s.add_argument("status", choices=["new", "approved", "rejected", "used"])
    s.set_defaults(func=cmd_idea_status)

    s = sub.add_parser("produce", help="script + render ideas into posts for review")
    s.add_argument("ids", type=int, nargs="*")
    s.add_argument("--brand")
    s.add_argument("--top", type=int, default=0, help="produce the N best-scored new ideas")
    s.add_argument("--no-render", action="store_true")
    s.add_argument("--notes", help="editor notes passed to the writer")
    s.set_defaults(func=cmd_produce)

    s = sub.add_parser("review", help="list the review queue or show one post")
    s.add_argument("id", type=int, nargs="?")
    s.set_defaults(func=cmd_review)

    s = sub.add_parser("approve", help="approve a post (optionally schedule it)")
    s.add_argument("id", type=int)
    s.add_argument("--yes-i-checked", action="store_true", help="confirm claims were fact-checked")
    s.add_argument("--notes")
    s.add_argument("--schedule", action="store_true")
    s.add_argument("--platform", action="append")
    s.add_argument("--at", help="ISO datetime with timezone")
    s.set_defaults(func=cmd_approve)

    s = sub.add_parser("reject", help="reject a post")
    s.add_argument("id", type=int)
    s.add_argument("--reason")
    s.set_defaults(func=cmd_reject)

    s = sub.add_parser("schedule", help="schedule an approved post (or --all approved posts)")
    s.add_argument("id", type=int, nargs="?")
    s.add_argument("--platform", action="append")
    s.add_argument("--at")
    s.add_argument("--all", action="store_true", help="fill the calendar with every approved, rendered post")
    s.add_argument("--brand")
    s.set_defaults(func=cmd_schedule)

    s = sub.add_parser("unschedule", help="cancel a scheduled post's queued publications (back to approved)")
    s.add_argument("id", type=int)
    s.set_defaults(func=lambda a: print(f"cancelled {_factory(a).unschedule(a.id)} publication(s)"))

    s = sub.add_parser("rerender", help="re-render a post's media")
    s.add_argument("id", type=int)
    s.set_defaults(func=cmd_rerender)

    s = sub.add_parser("calendar", help="upcoming publications")
    s.add_argument("--days", type=int, default=14)
    s.add_argument("--brand")
    s.add_argument("--export", metavar="DIR", help="also write calendar.ics and calendar.html (all brands) there")
    s.set_defaults(func=cmd_calendar)

    sub.add_parser("publish", help="publish everything that is due").set_defaults(func=cmd_publish)
    sub.add_parser("metrics", help="pull metrics for published posts").set_defaults(func=cmd_metrics)

    s = sub.add_parser("daily", help="one scheduled tick: ideas, production, publishing, metrics")
    s.add_argument("--brand")
    s.add_argument("--ideas", type=int, default=8)
    s.add_argument("--produce", type=int, default=2)
    s.add_argument("--offline", action="store_true")
    s.set_defaults(func=cmd_daily)

    s = sub.add_parser("repurpose", help="cut a long post into standalone Shorts + a carousel; --text adds "
                                         "blog, newsletter, pin and thread drafts")
    s.add_argument("id", type=int)
    s.add_argument("--text", action="store_true", help="also write blog / newsletter / 3 pins / thread drafts")
    s.add_argument("--text-only", action="store_true", help="only the written drafts, no new videos")
    s.add_argument("--force", action="store_true", help="draft text even if the video isn't published yet")
    s.add_argument("--shorts", type=int, default=3)
    s.add_argument("--no-carousel", action="store_true")
    s.add_argument("--no-render", action="store_true")
    s.set_defaults(func=cmd_repurpose)

    s = sub.add_parser("insights", help="what's working: by format, pillar, platform, hour")
    s.add_argument("--brand")
    s.add_argument("--days", type=int, default=30)
    s.add_argument("--rescore", action="store_true", help="feed results back into idea scores")
    s.set_defaults(func=cmd_insights)

    s = sub.add_parser("import", help="load ready-written scripts (JSON list) as posts for review")
    s.add_argument("file")
    s.add_argument("--brand", required=True)
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--no-render", action="store_true")
    s.add_argument("--queue", action="store_true", help="hand renders to the render queue instead of waiting")
    s.add_argument("--force", action="store_true", help="import even if a post with the same title exists")
    s.set_defaults(func=cmd_import)

    s = sub.add_parser("launch-pack", help="export a postable launch pack (slides, thumbnails, captions, brand kit)")
    s.add_argument("file", help="content.json (same shape as for import)")
    s.add_argument("--brand", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--render-videos", action="store_true", help="render videos even without a real voice")
    s.add_argument("--no-extras", action="store_true", help="skip brand kit and link page")
    s.set_defaults(func=cmd_launch_pack)

    s = sub.add_parser("niche", help="score niche candidates (ad value, demand, risk, saturation)")
    s.add_argument("niches", nargs="+")
    s.add_argument("--offline", action="store_true")
    s.set_defaults(func=cmd_niche)

    s = sub.add_parser("new-brand", help="draft a brand profile YAML for a niche")
    s.add_argument("niche")
    s.add_argument("--audience")
    s.add_argument("--slug")
    s.add_argument("--platform", action="append")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_new_brand)

    s = sub.add_parser("report", help="weekly business report: money, content, funnel, pipeline, next actions")
    s.add_argument("--save", action="store_true", help="write to output/reports/ (also writes the HTML pages)")
    s.add_argument("--html", action="store_true", help="one HTML page per brand from imported stats: best and "
                                                       "worst posts, formats, pillars, next topics")
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("serve", help="run the dashboard")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(func=cmd_serve)

    s = sub.add_parser("ui", help="local dashboard (127.0.0.1 only): calendar, review queue, recordings, launch check")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--no-browser", action="store_true")
    s.set_defaults(func=cmd_ui)

    s = sub.add_parser("demo", help="offline end-to-end demo that renders sample posts")
    s.add_argument("--brand")
    s.set_defaults(func=cmd_demo)

    _extend(sub)
    return p


def _extend(sub) -> None:
    """Optional command groups that live in their own modules."""
    for mod in ("contentfactory.business.cli", "contentfactory.publish.cli", "contentfactory.funnel.cli",
                "contentfactory.community.cli", "contentfactory.site", "contentfactory.pack",
                "contentfactory.channels", "contentfactory.renderq", "contentfactory.doctor", "contentfactory.backup",
                "contentfactory.publish.preflight", "contentfactory.cleanup",
                "contentfactory.planner", "contentfactory.launch_check", "contentfactory.stats",
                "contentfactory.scaffold", "contentfactory.manual", "contentfactory.numbercheck", "contentfactory.ytplan", "contentfactory.triage", "contentfactory.challenge", "contentfactory.whitelabel", "contentfactory.originality", "contentfactory.newsletter_export", "contentfactory.batch_record", "contentfactory.routine", "contentfactory.export_week", "contentfactory.scorecard", "contentfactory.sequence_export", "contentfactory.scheduler", "contentfactory.review", "contentfactory.launchmode", "contentfactory.timelog", "contentfactory.media.stock", "contentfactory.keywords", "contentfactory.weekly_review", "contentfactory.media.motion"):
        try:
            module = __import__(mod, fromlist=["register"])
        except ImportError:
            continue
        module.register(sub, _factory)


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (KeyError, PermissionError, ValueError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
