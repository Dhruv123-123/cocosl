"""Launch pack export: turn a brand's ready-written content.json into a folder
someone can post from without running the software.

    factory launch-pack launch/scam-decoded/content.json --brand scam-decoded --out dist/scam-decoded

Layout (same as the Money Made Simple pack):
  carousels/<nn-title>/slide-01.jpg ... + caption.txt
  videos-need-voice/<nn-title>/caption.txt + thumbnail.jpg (+ video.mp4 when a real voice rendered)
  brand-kit/   (profile picture, banners, highlights, style sheet, bios)
  link-in-bio-page/index.html
  CONTENTS.md  (index of every piece, its platforms, length and affiliate links)

Every piece also goes into the review queue as a post, so nothing here is
"approved": caption.txt lists the claims a human must check before posting.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from .schemas import Script

WPM = 160


def slugify(text: str, limit: int = 50) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].rstrip("-") or "untitled"


def narration_words(script: Script) -> int:
    return sum(len((s.narration or "").split()) for s in script.segments)


def caption_text(brand, item: dict, script: Script) -> str:
    """The caption.txt a human pastes from: caption, disclosure, hashtags, checks, script."""
    fmt = item["format"]
    tags = " ".join("#" + t.lstrip("#").replace(" ", "") for t in script.hashtags)
    platforms = item.get("platforms") or [a.platform for a in brand.accounts if a.enabled and fmt in a.formats]
    lines = [script.title, f"Format: {fmt}", f"Platforms: {', '.join(platforms)}"]
    if fmt in ("short", "long"):
        words = narration_words(script)
        lines.append(f"Estimated length: ~{round(words / WPM * 60)}s ({words} words at {WPM} wpm)")
    lines += ["", "--- CAPTION (paste as-is) ---", script.caption.strip(), "", brand.ai_disclosure, "", tags]
    if script.hook_variants:
        lines += ["", "--- HOOK VARIANTS (for reposts / A-B tests) ---", *[f"- {h}" for h in script.hook_variants]]
    lines += ["", "--- CHECK BEFORE POSTING ---", *[f"[ ] {c}" for c in script.claims_to_verify]]
    if script.sources:
        lines += ["", "Sources:", *script.sources]
    if fmt in ("short", "long"):
        lines += ["", "--- NARRATION SCRIPT ---", *[s.narration for s in script.segments if s.narration]]
        lines += ["", "--- ON-SCREEN TEXT (per beat) ---", *[f"{i + 1}. {s.on_screen_text}"
                                                            for i, s in enumerate(script.segments)]]
    return "\n".join(lines).rstrip() + "\n"


def _affiliates(brand, script: Script) -> list[str]:
    text = script.caption
    return [a.name for a in brand.affiliates if a.url in text or (a.slug and f"/go/{a.slug}" in text)]


def _thumbnail_only(factory, brand, script: Script, out: Path) -> Path:
    """Thumbnail without rendering the whole (voiceless) video."""
    from .media.images import generate_images
    from .media.thumbnail import render_thumbnail
    from .media.util import Palette
    work = out / "_work"
    img = generate_images(factory.settings, brand, [script.segments[0].visual_prompt], (1920, 1080), "16:9",
                          work, family=f"{brand.slug}:{script.title}")[0]
    png = render_thumbnail(img.path, script.thumbnail_text or script.title, Palette.from_brand(brand),
                           brand.visual.font, brand.visual.watermark, work / "thumbnail.png")
    jpg = out / "thumbnail.jpg"
    from PIL import Image
    Image.open(png).convert("RGB").save(jpg, "JPEG", quality=90)
    shutil.rmtree(work, ignore_errors=True)
    return jpg


POSTABLE_VOICES = ("piper", "elevenlabs", "openai")  # espeak and silent are previews, not posts


def real_voice(settings, brand) -> bool:
    from .media.tts import PROVIDERS
    wanted = (settings.tts_provider or "auto").lower()
    names = POSTABLE_VOICES if wanted == "auto" else (wanted,) if wanted in POSTABLE_VOICES else ()
    return any(PROVIDERS[n](settings, brand).available() for n in names)


def build_pack(factory, brand_slug: str, content_path: Path, out: Path, *, render_videos: bool | None = None,
               extras: bool = True) -> dict:
    """Import every item for review, render carousels and thumbnails, and write the pack.

    render_videos: None = only when a real voice provider is configured (a silent
    video isn't postable, so by default voiceless runs just make thumbnails)."""
    brand = factory.brand(brand_slug)
    items = json.loads(Path(content_path).read_text())
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if render_videos is None:
        render_videos = real_voice(factory.settings, brand)
    rows = []
    for i, item in enumerate(items):
        script = Script.model_validate(item["script"])
        fmt = item["format"]
        name = f"{i + 1:02d}-{slugify(script.title)}"
        if item.get("platforms") == ["tiktok"]:
            name += "-tiktok"
        is_video = fmt in ("short", "long")
        folder = out / ("videos-need-voice" if is_video and not render_videos else
                        "videos" if is_video else "carousels") / name
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
        render = (not is_video) or render_videos
        pid = factory.import_script(brand.slug, item["script"], fmt, item.get("pillar", ""),
                                    item.get("idea_angle", ""), render=render, source="launch-pack",
                                    platforms=item.get("platforms"))
        post = factory.db.get("posts", pid)
        assets = post.get("assets") or {}
        root = factory.settings.output_dir
        if fmt == "carousel":
            for n, rel in enumerate(assets.get("slides") or []):
                src = (root / rel).with_suffix(".jpg")
                shutil.copy(src if src.exists() else root / rel, folder / f"slide-{n + 1:02d}.jpg")
        elif render and assets.get("video"):
            shutil.copy(root / assets["video"], folder / "video.mp4")
            thumb = (root / assets["thumbnail"]).with_suffix(".jpg")
            shutil.copy(thumb, folder / "thumbnail.jpg")
        else:
            _thumbnail_only(factory, brand, script, folder)
        (folder / "caption.txt").write_text(caption_text(brand, item, script))
        words = narration_words(script)
        rows.append({"n": i, "post_id": pid, "folder": str(folder.relative_to(out)), "format": fmt,
                     "title": script.title, "pillar": item.get("pillar", ""),
                     "platforms": item.get("platforms") or [], "seconds": round(words / WPM * 60) if is_video else 0,
                     "affiliates": _affiliates(brand, script), "checks": len(script.claims_to_verify),
                     "status": (post.get("checks") or {}).get("status", "")})
    if extras:
        _extras(factory, brand, out, content_path)
    (out / "CONTENTS.md").write_text(contents_md(brand, rows))
    return {"items": rows, "out": str(out)}


def _extras(factory, brand, out: Path, content_path: Path) -> None:
    from .brandkit import build_brand_kit, kit_dir
    from .funnel.linkpage import build_link_page, lead_magnet_path
    build_brand_kit(factory.settings, brand, factory.llm)
    shutil.rmtree(out / "brand-kit", ignore_errors=True)
    shutil.copytree(kit_dir(factory.settings, brand), out / "brand-kit")
    # A hand-written lead-magnet.json next to content.json wins over the generated checklist.
    magnet = lead_magnet_path(factory.settings, brand)
    custom = Path(content_path).parent / "lead-magnet.json"
    if custom.exists():
        magnet.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(custom, magnet)
    page = build_link_page(factory.settings, brand, db=factory.db, llm=factory.llm)
    dest = out / "link-in-bio-page"
    dest.mkdir(exist_ok=True)
    shutil.copy(page, dest / "index.html")
    if magnet.exists():
        shutil.copy(magnet, dest / "lead-magnet.json")


def contents_md(brand, rows: list[dict]) -> str:
    lines = [f"# {brand.name}: launch content index", "",
             f"{len(rows)} pieces. `#` is the position in content.json (0-based). Platforms empty = every "
             "account that takes the format.", "",
             "| # | Format | Platforms | Length | Piece | Affiliate | Checks |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        length = f"~{r['seconds']}s" if r["seconds"] else ""
        lines.append(f"| {r['n']} | {r['format']} | {', '.join(r['platforms']) or 'all'} | {length} | "
                     f"{r['title']} | {', '.join(r['affiliates'])} | {r['checks']} |")
    return "\n".join(lines) + "\n"
