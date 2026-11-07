"""Check a post's media against each platform's published limits before it is scheduled or uploaded.

A problem found here costs nothing; the same problem found by the platform
costs an upload, a retry loop and sometimes a half-made post. Limits are the
documented ones for the official APIs this project uses (see each adapter's
docstring for the source pages). `block` stops scheduling or publishing,
`warn` is shown but doesn't stop anything.

    factory preflight 12            # one post, every platform its brand posts it to
    factory preflight --scheduled   # everything queued to go out
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

MB = 1024 * 1024

# seconds (min, max) for video by (platform, format); None = no documented limit we enforce
VIDEO_SECONDS = {
    ("youtube", "short"): (1, 180),        # Shorts: up to 3 minutes, vertical or square
    ("youtube", "long"): (1, 15 * 60),     # unverified channels: 15 min (verified: 12 h, so only a warning)
    ("instagram", "short"): (3, 15 * 60),  # Reels via the content publishing API
    ("facebook", "short"): (3, 90),        # Page Reels API: 3-90 s
    ("facebook", "long"): (1, 240 * 60),
    ("threads", "short"): (1, 5 * 60),
    ("threads", "long"): (1, 5 * 60),
    ("tiktok", "short"): (3, 10 * 60),     # the real cap is per creator (creator_info); 10 min is the common one
    ("tiktok", "long"): (3, 10 * 60),
    ("tiktok", "mid"): (3, 10 * 60),
}
VIDEO_BYTES = {"youtube": 256 * 1024 * MB, "instagram": 300 * MB, "facebook": 1024 * MB, "threads": 1024 * MB,
               "tiktok": 4096 * MB}
IMAGE_BYTES = {"instagram": 8 * MB, "threads": 8 * MB, "facebook": 10 * MB}
CAROUSEL_ITEMS = {"instagram": (2, 10), "threads": (2, 20), "facebook": (1, 10)}
SOFT_LIMITS = {("youtube", "long")}  # over the limit is fine for verified channels


@dataclass
class Issue:
    platform: str
    level: str  # block | warn
    message: str

    def __str__(self) -> str:
        return f"{self.platform}: {self.message}"


def check(post: dict, platform: str, output_dir: Path, public_base: str = "") -> list[Issue]:
    from . import REGISTRY
    fmt = post.get("format", "")
    assets = post.get("assets") or {}
    issues: list[Issue] = []

    def add(level: str, msg: str) -> None:
        issues.append(Issue(platform, level, msg))

    if platform not in REGISTRY:
        add("block", "unknown platform")
        return issues
    import importlib
    mod, name = REGISTRY[platform]
    cls = getattr(importlib.import_module(mod), name)
    if not cls.supports(cls.__new__(cls), fmt):
        add("block", f"doesn't take {fmt} posts")
        return issues

    if fmt in ("short", "mid", "long"):
        video = assets.get("video")
        path = output_dir / video if video else None
        if not path or not path.is_file():
            add("block", "video file is missing; re-render the post")
        else:
            limit = VIDEO_BYTES.get(platform)
            if limit and path.stat().st_size > limit:
                add("block", f"video is {path.stat().st_size / MB:.0f} MB, over the {limit / MB:.0f} MB limit")
        seconds = float(assets.get("duration") or 0)
        lo_hi = VIDEO_SECONDS.get((platform, fmt))
        if lo_hi and seconds:
            lo, hi = lo_hi
            if seconds < lo:
                add("block", f"video is {seconds:.1f}s; the minimum is {lo}s")
            elif seconds > hi:
                soft = (platform, fmt) in SOFT_LIMITS
                add("warn" if soft else "block",
                    f"video is {seconds:.0f}s; the limit is {hi}s" + (" unless the channel is verified" if soft else ""))
        if platform in ("instagram", "threads") and not public_base:
            add("block", "PUBLIC_MEDIA_BASE_URL is not set; Meta fetches video from a public HTTPS URL")
        if fmt == "mid" and seconds and seconds <= 60:
            add("warn", f"TikTok cut is {seconds:.0f}s; Creator Rewards only count videos over a minute")
        if platform == "youtube" and fmt == "long" and not assets.get("thumbnail"):
            add("warn", "no thumbnail; YouTube will pick a frame")
    else:
        slides = assets.get("slides") or assets.get("images") or []
        if not slides:
            add("block", "no images; re-render the post")
        lo, hi = CAROUSEL_ITEMS.get(platform, (1, 99)) if fmt == "carousel" else (1, 1)
        if fmt == "carousel" and slides and not lo <= len(slides) <= hi:
            add("block", f"{len(slides)} slides; {platform} takes {lo}-{hi}")
        cap = IMAGE_BYTES.get(platform)
        for rel in slides:
            p = output_dir / rel
            if not p.is_file():
                add("block", f"missing image {rel}")
                continue
            if platform in ("instagram", "threads"):
                jpg = p.with_suffix(".jpg")
                if not jpg.is_file():
                    add("block", f"no JPEG for {rel} (Instagram's API only takes JPEG)")
                elif cap and jpg.stat().st_size > cap:
                    add("block", f"{jpg.name} is {jpg.stat().st_size / MB:.1f} MB, over {cap / MB:.0f} MB")
            elif cap and p.stat().st_size > cap:
                add("block", f"{p.name} is {p.stat().st_size / MB:.1f} MB, over {cap / MB:.0f} MB")
        if platform in ("instagram", "threads") and not public_base:
            add("block", "PUBLIC_MEDIA_BASE_URL is not set; Meta fetches images from a public HTTPS URL")
    return issues


def check_post(factory, post: dict, platforms: list[str] | None = None) -> list[Issue]:
    brand = factory.brand(post["brand"])
    targets = platforms or [a.platform for a in brand.accounts if a.enabled and post["format"] in a.formats]
    out: list[Issue] = []
    for platform in targets:
        out += check(post, platform, factory.settings.output_dir, factory.settings.public_media_base_url)
    return out


def enabled() -> bool:
    import os
    return os.environ.get("FACTORY_PREFLIGHT", "1") != "0"


def blocking(issues: list[Issue], dry_run: bool) -> list[Issue]:
    """Issues that stop scheduling. In dry run a missing public URL doesn't block (nothing is fetched).
    FACTORY_PREFLIGHT=0 turns the automatic check off (the `factory preflight` command still reports)."""
    if not enabled():
        return []
    return [i for i in issues if i.level == "block" and not (dry_run and "PUBLIC_MEDIA_BASE_URL" in i.message)]


def register(sub, factory_fn) -> None:
    s = sub.add_parser("preflight", help="check posts' media against each platform's limits (posts nothing)")
    s.add_argument("ids", type=int, nargs="*")
    s.add_argument("--scheduled", action="store_true", help="every post with queued publications")

    def run(a):
        f = factory_fn(a)
        ids = list(a.ids)
        if a.scheduled:
            ids += [r["post_id"] for r in f.db.query(
                "SELECT DISTINCT post_id FROM publications WHERE status = 'queued' ORDER BY post_id")]
        if not ids:
            print("nothing to check (give post ids or --scheduled)")
            return
        bad = 0
        for pid in dict.fromkeys(ids):
            post = f._post(pid)
            platforms = None
            if a.scheduled:
                platforms = [r["platform"] for r in f.db.query(
                    "SELECT platform FROM publications WHERE post_id = ? AND status = 'queued'", [pid])] or None
            issues = check_post(f, post, platforms)
            stop = [i for i in issues if i.level == "block"
                    and not (f.settings.dry_run and "PUBLIC_MEDIA_BASE_URL" in i.message)]
            bad += bool(stop)
            print(f"#{pid} {post['format']:8s} " + ("OK" if not issues else ("BLOCKED" if stop else "warnings")))
            for i in issues:
                print(f"    [{i.level}] {i}")
        if bad:
            raise SystemExit(1)
    s.set_defaults(func=run)
