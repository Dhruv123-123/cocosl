"""Post-by-hand packages, for platforms where the factory must not upload for you.

TikTok's Content Posting API is for apps that let *other* creators post; its guidelines don't allow a
tool that uploads to accounts you or your team manage. So TikTok is manual by default:

* When a TikTok publication comes due, the worker doesn't upload. It writes a package to
  output/manual/<brand>/<YYYY-MM-DD-HHMM>-post-<id>-tiktok/:
    video.mp4      the rendered video (a copy)
    caption.txt    the caption, AI label and hashtags, ready to paste
    POST_AT.txt    when to post it (UTC and the brand's local time) and the checklist
  and marks the publication `manual` ("post by hand").
* `factory ui` (the Today page) and `factory calendar` show it as "post by hand", with a
  "Copy caption" button and a "Mark posted" form.
* `factory manual` lists packages; `factory manual copy <pub id>` puts the caption on the clipboard;
  `factory manual done <pub id> --url <tiktok url>` records it as published.

MANUAL_PLATFORMS (default "tiktok") picks which platforms work this way. Set it to "" only if you run
the factory as an audited TikTok app for other creators. Nothing here posts anything.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


def manual_platforms() -> set[str]:
    return {p.strip() for p in os.environ.get("MANUAL_PLATFORMS", "tiktok").split(",") if p.strip()}


def is_manual(platform: str) -> bool:
    return platform in manual_platforms()


def package_dir(factory, pub: dict, post: dict) -> Path:
    at = datetime.fromisoformat(pub["scheduled_at"]).astimezone(timezone.utc)
    return factory.settings.output_dir / "manual" / post["brand"] / f"{at:%Y-%m-%d-%H%M}-post-{post['id']}-{pub['platform']}"


def build_package(factory, pub: dict, post: dict | None = None) -> dict:
    """Write (or refresh) the package for one publication; returns its paths, relative to output/."""
    post = post or factory.db.get("posts", pub["post_id"])
    req = factory.build_request(post, pub["platform"])
    d = package_dir(factory, pub, post)
    d.mkdir(parents=True, exist_ok=True)
    out = {"dir": d}
    if req.video_path and Path(req.video_path).is_file():
        dst = d / f"video{Path(req.video_path).suffix or '.mp4'}"
        if not dst.exists() or dst.stat().st_mtime < Path(req.video_path).stat().st_mtime:
            shutil.copy2(req.video_path, dst)
        out["video"] = dst
    (d / "caption.txt").write_text(req.caption.strip() + "\n")
    out["caption"] = d / "caption.txt"
    at = datetime.fromisoformat(pub["scheduled_at"]).astimezone(timezone.utc)
    try:
        tz = ZoneInfo(factory.brand(post["brand"]).cadence.timezone)
    except Exception:
        tz = timezone.utc
    account = pub.get("account") or ""
    (d / "POST_AT.txt").write_text(
        f"Post by hand on {pub['platform']}{' as ' + account if account else ''}\n"
        f"When: {at:%a %d %b %Y %H:%M} UTC ({at.astimezone(tz):%a %d %b %H:%M} {tz})\n"
        f"Post #{post['id']}: {post.get('title', '')}\n\n"
        "1. Upload video in the app.\n"
        "2. Paste caption.txt (`factory manual copy " + str(pub["id"]) + "` copies it).\n"
        "3. Turn on the app's AI-generated content label.\n"
        "4. If it promotes a brand or affiliate link, turn on the paid partnership / branded content toggle.\n"
        f"5. Then: factory manual done {pub['id']} --url <link to the post>  (or Mark posted on the Today page)\n")
    out["post_at"] = d / "POST_AT.txt"
    rel = {k: str(v.relative_to(factory.settings.output_dir)) for k, v in out.items()}
    return rel


def hand_off(factory, pub: dict, post: dict) -> dict:
    """Called by the worker when a manual-platform publication is due: package it, mark it `manual`."""
    from .db import now_iso
    rel = build_package(factory, pub, post)
    meta = dict(pub.get("meta") or {})
    meta["manual"] = rel
    factory.db.update("publications", pub["id"], {"status": "manual", "meta": meta, "error": "", "updated_at": now_iso()})
    factory.db.log("publication.manual", "publication", pub["id"], {"platform": pub["platform"], "dir": rel["dir"]})
    return rel


def pending(factory, upcoming: bool = True) -> list[dict]:
    """Manual publications waiting on you (status manual), plus queued ones on manual platforms."""
    plats = sorted(manual_platforms())
    if not plats:
        return []
    statuses = ["manual", "queued"] if upcoming else ["manual"]
    rows = factory.db.query(
        f"""SELECT pub.*, s.brand, s.title, s.format FROM publications pub JOIN posts s ON s.id = pub.post_id
            WHERE pub.platform IN ({','.join('?' * len(plats))}) AND pub.status IN ({','.join('?' * len(statuses))})
            ORDER BY pub.scheduled_at""", [*plats, *statuses])
    for r in rows:
        r["due"] = r["status"] == "manual"
        r["package"] = (r.get("meta") or {}).get("manual") or {}
        try:
            post = factory.db.get("posts", r["post_id"])
            r["caption"] = factory.build_request(post, r["platform"]).caption
        except Exception:
            r["caption"] = ""
    return rows


def mark_done(factory, pub_id: int, url: str = "", actor: str = "human") -> None:
    from .db import now_iso
    pub = factory.db.get("publications", pub_id)
    if not pub:
        raise KeyError(f"No publication #{pub_id}")
    if pub["status"] not in ("manual", "queued") or not is_manual(pub["platform"]):
        raise ValueError(f"Publication #{pub_id} is {pub['status']} on {pub['platform']}; not a post-by-hand item")
    if url and not url.startswith("https://"):
        raise ValueError("url should be the https:// link to the post")
    factory.db.update("publications", pub_id, {"status": "published", "url": url, "published_at": now_iso(),
                                               "error": ""})
    factory.db.update("posts", pub["post_id"], {"status": "published"})
    factory.db.log("publication.manual_done", "publication", pub_id, {"url": url}, actor=actor)


def copy_to_clipboard(text: str) -> str:
    """Best-effort: returns the tool used, or '' if none was found."""
    for cmd in (["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"],
                ["clip.exe"]):
        if shutil.which(cmd[0]):
            subprocess.run(cmd, input=text.encode(), check=True)
            return cmd[0]
    return ""


def register(sub, factory_fn) -> None:
    m = sub.add_parser("manual", help="post-by-hand packages (TikTok): list, copy caption, mark posted")
    ms = m.add_subparsers(dest="manual_cmd")

    def ls(a):
        f = factory_fn(a)
        rows = pending(f)
        if not rows:
            print("Nothing to post by hand.")
        for r in rows:
            when = r["scheduled_at"][:16].replace("T", " ")
            state = "DUE NOW" if r["due"] else "upcoming"
            print(f"#{r['id']:<5} {state:9s} {when} UTC  {r['brand']:20s} {r['platform']:8s} {r['title'][:50]}")
            if r["package"]:
                print(f"       {f.settings.output_dir / r['package']['dir']}")
    m.set_defaults(func=ls)

    s = ms.add_parser("build", help="write packages now for every upcoming post-by-hand item")

    def build(a):
        f = factory_fn(a)
        for r in pending(f):
            print(f"#{r['id']}: {f.settings.output_dir / build_package(f, r)['dir']}")
    s.set_defaults(func=build)

    s = ms.add_parser("copy", help="copy a publication's caption to the clipboard")
    s.add_argument("pub_id", type=int)

    def copy(a):
        f = factory_fn(a)
        pub = f.db.get("publications", a.pub_id)
        if not pub:
            raise SystemExit(f"No publication #{a.pub_id}")
        text = f.build_request(f.db.get("posts", pub["post_id"]), pub["platform"]).caption
        tool = copy_to_clipboard(text)
        print(f"Caption copied ({tool})." if tool else text)
    s.set_defaults(func=copy)

    s = ms.add_parser("done", help="record that you posted it")
    s.add_argument("pub_id", type=int)
    s.add_argument("--url", default="")

    def done(a):
        mark_done(factory_fn(a), a.pub_id, a.url)
        print(f"Publication #{a.pub_id} recorded as published.")
    s.set_defaults(func=done)
