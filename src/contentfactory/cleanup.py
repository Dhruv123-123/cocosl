"""Free disk space from old, finished posts.

Videos and narration audio are the bulk of output/. Once a post has been live
everywhere for a while, the platform holds the copy people watch. This removes
the heavy files (video.mp4, audio.wav, generated images) of posts that are
`published` with no publication still queued, publishing or waiting for a
check, and whose last publish is older than N days. Thumbnails, slides,
captions and the provenance record stay, so the post page still shows what went
out and where its parts came from.

    factory cleanup --older-than 60            # list what would go (nothing is deleted)
    factory cleanup --older-than 60 --yes      # delete it

The worker runs it daily only when CLEANUP_AFTER_DAYS is set (off by default).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

HEAVY_KEYS = ("video", "audio")


def candidates(factory, older_than_days: int) -> list[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=older_than_days)).replace(microsecond=0).isoformat()
    rows = factory.db.query(
        """SELECT p.* FROM posts p WHERE p.status = 'published'
           AND NOT EXISTS (SELECT 1 FROM publications q WHERE q.post_id = p.id
                           AND q.status IN ('queued', 'publishing', 'needs_check', 'manual'))
           AND (SELECT MAX(published_at) FROM publications q WHERE q.post_id = p.id AND q.status = 'published') < ?
           ORDER BY p.id""", [cutoff])
    out = []
    root = factory.settings.output_dir
    for post in rows:
        assets = post.get("assets") or {}
        files = [assets.get(k) for k in HEAVY_KEYS if assets.get(k)]
        if post["format"] in ("short", "mid", "long"):  # carousel images are the post itself; keep them
            files += assets.get("images") or []
        paths = [root / f for f in files if f and not Path(f).is_absolute() and (root / f).is_file()]
        if paths:
            out.append({"post_id": post["id"], "paths": paths, "bytes": sum(p.stat().st_size for p in paths)})
    return out


def run(factory, older_than_days: int, confirm: bool = False) -> dict:
    found = candidates(factory, older_than_days)
    total = sum(c["bytes"] for c in found)
    if confirm:
        for c in found:
            for p in c["paths"]:
                p.unlink(missing_ok=True)
            post = factory.db.get("posts", c["post_id"])
            assets = dict(post.get("assets") or {})
            assets["cleaned"] = {"at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                                 "removed": [str(p.relative_to(factory.settings.output_dir)) for p in c["paths"]]}
            factory.db.update("posts", c["post_id"], {"assets": assets})
            factory.db.log("post.media_cleaned", "post", c["post_id"], {"bytes": c["bytes"]}, actor="cleanup")
    return {"posts": len(found), "bytes": total, "deleted": confirm}


def from_env() -> int | None:
    raw = os.environ.get("CLEANUP_AFTER_DAYS", "").strip()
    return int(raw) if raw.isdigit() and int(raw) >= 14 else None


def register(sub, factory_fn) -> None:
    s = sub.add_parser("cleanup", help="free disk space from old published posts (lists unless --yes)")
    s.add_argument("--older-than", type=int, default=60, help="days since the last publish (min 14)")
    s.add_argument("--yes", action="store_true", help="actually delete")

    def cmd(a):
        if a.older_than < 14:
            raise SystemExit("--older-than must be at least 14 days")
        f = factory_fn(a)
        res = run(f, a.older_than, confirm=a.yes)
        verb = "Freed" if a.yes else "Would free"
        print(f"{verb} {res['bytes'] / 1e9:.2f} GB from {res['posts']} post(s)"
              + ("" if a.yes else "; rerun with --yes to delete"))
    s.set_defaults(func=cmd)
