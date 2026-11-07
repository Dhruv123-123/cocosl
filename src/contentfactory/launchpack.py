"""Export ready-written scripts (a content.json list) as a hand-off folder.

For each item: carousels get rendered slides; videos get a thumbnail (and the
full render with --video). Every item gets caption.txt with the caption to
paste (CTA, AI disclosure, hashtags), the facts to check and, for videos, the
narration. Nothing is posted; this is the folder a person works from.

Operator notes (the "CHECK BEFORE POSTING" block) stay in English; for a
non-English brand they also carry a native-speaker sign-off line.
"""
from __future__ import annotations

import dataclasses
import re
import shutil
from pathlib import Path

from . import i18n
from .config import BrandProfile, Settings
from .schemas import Script


def slugify(text: str, limit: int = 50) -> str:
    import unicodedata
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")[:limit].strip("-") or "untitled"


def caption_text(brand: BrandProfile, item: dict) -> str:
    sc = Script.model_validate(item["script"])
    fmt = item.get("format", "short")
    tags = " ".join("#" + h.lstrip("#").replace(" ", "") for h in sc.hashtags)
    paste = "\n\n".join(x for x in [sc.caption.strip(), brand.ai_disclosure.strip(), tags] if x)
    checks = [f"[ ] {c}" for c in sc.claims_to_verify] or ["[ ] No numeric claims; confirm links before posting"]
    if not i18n.is_english(brand):
        checks.insert(0, f"[ ] A fluent {i18n.locale_of(brand)} speaker has read every word on screen, in the "
                         "caption and in the narration, and fixed anything that sounds translated")
    out = [sc.title, f"Format: {fmt}", "", "--- CAPTION (paste as-is) ---", paste, "",
           "--- CHECK BEFORE POSTING ---", *checks]
    if fmt == "long":
        charts = [f"- {s.heading}: chart '{s.chart.title}' ({s.chart.note or 'exact numbers'})" for s in sc.segments if s.chart]
        if charts or sc.original_element:
            out += ["", "--- ORIGINAL ELEMENT (YouTube's inauthentic-content rule) ---", *charts]
            if sc.original_element:
                out.append(f"- To make it stronger, record: {sc.original_element}. Add the clip to a beat's "
                           "footage before rendering.")
    if sc.sources:
        out += ["", "Sources:", *sc.sources]
    if fmt == "long" and sc.description.strip():
        out += ["", "--- YOUTUBE DESCRIPTION (paste as-is; re-time chapters after voicing) ---", sc.description.strip()]
    if fmt in ("short", "mid", "long"):
        out += ["", "--- NARRATION SCRIPT ---", *[s.narration for s in sc.segments if s.narration]]
        if sc.cta and sc.cta not in " ".join(s.narration for s in sc.segments):
            out.append(sc.cta)
    if item.get("source_title"):
        out += ["", f"Adapted from: {item['source_title']}"]
    return "\n".join(out).rstrip() + "\n"


def export_pack(settings: Settings, brand: BrandProfile, items: list[dict], out_dir: Path,
                *, video: bool = False, start: int = 1) -> list[Path]:
    """Render `items` into out_dir/{carousels,videos}/NN-slug/. Returns the item folders."""
    from .media import render_post
    from .media.images import generate_images
    from .media.thumbnail import render_thumbnail
    from .media.util import ASPECTS, VIDEO_SIZES, Palette

    out_dir = Path(out_dir)
    folders = []
    for n, item in enumerate(items, start=start):
        fmt = item.get("format", "short")
        sc = Script.model_validate(item["script"])
        group = "carousels" if fmt in ("carousel", "image") else "videos"
        folder = out_dir / group / f"{n:02d}-{slugify(sc.title)}"
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        if fmt in ("carousel", "image") or video:
            tmp_root = out_dir / ".render"
            post = {"id": f"pack-{n}", "format": fmt, "title": sc.title, "script": item["script"],
                    "meta": {"output_subdir": f"{n:02d}"}}
            assets = render_post(dataclasses.replace(settings, output_dir=tmp_root), brand, post)
            for rel in assets.get("slides") or []:
                p = tmp_root / rel
                shutil.copy(p.with_suffix(".jpg"), folder / p.with_suffix(".jpg").name)
            for key in ("video", "captions_srt"):
                if assets.get(key):
                    shutil.copy(tmp_root / assets[key], folder / Path(assets[key]).name)
            if assets.get("thumbnail"):
                shutil.copy((tmp_root / assets["thumbnail"]).with_suffix(".jpg"), folder / "thumbnail.jpg")
            shutil.rmtree(tmp_root, ignore_errors=True)
        else:
            work = folder / "_work"
            size = VIDEO_SIZES[fmt]
            art = generate_images(settings, brand, [sc.segments[0].visual_prompt if sc.segments else sc.title],
                                  size, ASPECTS[fmt], work, family=f"{brand.slug}:{sc.title}")[0].path
            render_thumbnail(art, sc.thumbnail_text or sc.title, Palette.from_brand(brand), brand.visual.font,
                             brand.visual.watermark, work / "thumbnail.png")
            shutil.copy(work / "thumbnail.jpg", folder / "thumbnail.jpg")
            shutil.rmtree(work)
        (folder / "caption.txt").write_text(caption_text(brand, item))
        folders.append(folder)
    return folders
