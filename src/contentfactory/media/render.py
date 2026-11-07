"""render_post: turn a scripted post into finished media files.

Output goes to settings.output_dir/<brand>/post-<id>/ (built in a .partial
folder and swapped in at the end, so a failed re-render never leaves a
half-written post). Returned paths are relative to settings.output_dir.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from ..config import BrandProfile, Settings
from ..schemas import Script, Segment
from .captions import time_segment, write_srt
from .carousel import SlideKit, SlideText, render_carousel
from .images import generate_images
from .thumbnail import render_thumbnail
from .tts import concat_narration, synthesize_segments
from .util import (ASPECTS, SHORT_MAX_SECONDS, SLIDE_SIZE, TIKTOK_CUT_MAX_SECONDS, VIDEO_SIZES, MediaError, Palette, RenderOptions,
                   probe, provenance)
from .video import Beat, VideoSpec, assemble, pick_music

MIN_BEAT = 1.5      # seconds on screen per beat, even if the line is very short
GAP = 0.3           # breath between beats
TAIL = 0.8          # hold after the last line
LEAD = 0.1          # captions start just after the cut


def render_post(settings: Settings, brand: BrandProfile, post: dict) -> dict:
    fmt = post.get("format") or "short"
    if fmt not in ("short", "long", "carousel", "image"):
        raise MediaError(f"Unknown post format '{fmt}'")
    script = _script(post)
    root = Path(settings.output_dir).resolve()
    final = post_dir(root, brand, post)
    build = final.with_name(final.name + ".partial")
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir(parents=True)
    try:
        if fmt in ("short", "long"):
            assets = _render_video(settings, brand, script, fmt, build, post)
        else:
            assets = _render_slides(settings, brand, script, fmt, build, post)
        work = build / "_work"
        if work.exists() and not RenderOptions.from_settings(settings).keep_work:
            shutil.rmtree(work)
    except BaseException:
        shutil.rmtree(build, ignore_errors=True)
        raise
    shutil.rmtree(final, ignore_errors=True)
    build.rename(final)
    return _relativize(assets, build, final, root)


# ---------------------------------------------------------------- video
def _render_video(settings: Settings, brand: BrandProfile, script: Script, fmt: str, out: Path, post: dict) -> dict:
    opts = RenderOptions.from_settings(settings)
    palette = Palette.from_brand(brand)
    size = VIDEO_SIZES[fmt]
    work = out / "_work"
    segments = script.segments
    family = f"{brand.slug}:{script.title}"

    imgs = generate_images(settings, brand, [s.visual_prompt for s in segments], size, ASPECTS[fmt],
                           out / "images", family=family)
    lines = [(s.narration or s.on_screen_text or s.heading).strip() for s in segments]
    heads = [s.on_screen_text for s in segments]
    images = [r.path for r in imgs]
    if script.cta and _norm(script.cta) not in _norm(" ".join(lines)):
        lines.append(script.cta)
        heads.append(brand.name)
        images.append(images[-1])

    tts = synthesize_segments(settings, brand, lines, work / "voice")
    beats, cues, slots, t = [], [], [], 0.0
    for i, (line, head, img, dur) in enumerate(zip(lines, heads, images, tts.durations)):
        slot = max(MIN_BEAT, dur + (TAIL if i == len(lines) - 1 else GAP))
        beats.append(Beat(img, head, t, slot))
        cues += time_segment(line, t + LEAD, max(0.4, dur - LEAD))
        slots.append(slot)
        t += slot

    audio = out / "audio.wav"
    concat_narration(tts.paths, slots, audio)
    srt = out / "captions.srt"
    write_srt(cues, srt)
    music = pick_music(f"{brand.slug}:{post.get('id')}:{script.title}")
    spec = VideoSpec(fmt, size, palette, brand.visual.font, brand.visual.watermark, opts)
    video = out / "video.mp4"
    duration = assemble(spec, beats, cues, audio, video, work, music=music, voiced=tts.provider != "silent")
    duration = probe(video)["duration"] or duration

    notes = list(tts.notes)
    meta = post.get("meta") or {}
    tiktok_only = isinstance(meta, dict) and meta.get("platforms") == ["tiktok"]
    limit = TIKTOK_CUT_MAX_SECONDS if tiktok_only else SHORT_MAX_SECONDS
    if fmt == "short" and duration > limit:
        notes.append(f"WARNING: short runs {duration:.1f}s (> {limit:.0f}s); trim the script "
                     "before posting. Nothing was cut automatically.")
    thumb = render_thumbnail(images[0], script.thumbnail_text or script.title, palette, brand.visual.font,
                             brand.visual.watermark, out / "thumbnail.png")

    prov = _image_provenance(imgs)
    prov.append(provenance(str(audio), "generated", tts.tool, " ".join(lines), provider=tts.provider,
                           note="Voice must be your own or licensed."))
    prov.append(provenance(str(srt), "rendered", "contentfactory.captions", note="timing estimated from audio length"))
    prov.append(provenance(str(thumb), "rendered", "pillow", script.thumbnail_text))
    prov.append(provenance(str(thumb.with_suffix(".jpg")), "rendered", "pillow", script.thumbnail_text,
                           note="JPEG copy for APIs that require JPEG"))
    prov.append(provenance(str(video), "rendered", "ffmpeg", "", fps=opts.fps, notes=notes,
                           music=music.name if music else None))
    if music:
        prov.append(provenance(str(music), "licensed", "user-music", "",
                               "user-supplied via FACTORY_MUSIC_DIR; keep the licence on file"))
    return {"video": video, "audio": audio, "captions_srt": srt, "images": [r.path for r in imgs], "slides": [],
            "thumbnail": thumb, "duration": round(duration, 3), "provenance": prov}


# ---------------------------------------------------------------- slides
def _render_slides(settings: Settings, brand: BrandProfile, script: Script, fmt: str, out: Path, post: dict) -> dict:
    segments = script.segments[:1] if fmt == "image" else script.segments
    family = f"{brand.slug}:{script.title}"
    imgs = generate_images(settings, brand, [s.visual_prompt for s in segments], SLIDE_SIZE, ASPECTS[fmt],
                           out / "images", family=family)
    kit = SlideKit(Palette.from_brand(brand), brand.visual.font, brand.visual.watermark, brand.name,
                   script.cta or brand.cta)
    texts = []
    for i, s in enumerate(segments):
        head = s.on_screen_text or s.heading or script.title
        if i == 0:
            body = s.narration if fmt == "image" else ""
            texts.append(SlideText(head, body))
        else:
            kicker = s.heading if s.heading and _norm(s.heading) != _norm(head) else ""
            texts.append(SlideText(head, s.narration, kicker))
    slides = render_carousel(kit, [r.path for r in imgs], texts, out / "slides")
    prov = _image_provenance(imgs)
    for p, t in zip(slides, texts):
        prov.append(provenance(str(p), "rendered", "pillow", t.headline))
        prov.append(provenance(str(p.with_suffix(".jpg")), "rendered", "pillow", t.headline,
                               note="JPEG copy for APIs that require JPEG"))
    if fmt == "carousel" and len(slides) > 20:
        prov[-1]["notes"] = ["WARNING: Instagram carousels allow at most 20 items"]
    return {"video": None, "audio": None, "captions_srt": None, "images": [r.path for r in imgs],
            "slides": slides, "thumbnail": None, "duration": 0.0, "provenance": prov}


# ---------------------------------------------------------------- helpers
def post_dir(root: Path, brand: BrandProfile, post: dict) -> Path:
    """<root>/<meta.output_subdir> if set, else <root>/<brand>/post-<id>. Ids may be strings."""
    meta = post.get("meta") or {}
    if isinstance(meta, str):
        import json
        meta = json.loads(meta or "{}")
    sub = str(meta.get("output_subdir") or "").strip().strip("/")
    if sub:
        rel = Path(sub)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts:
            raise MediaError(f"meta.output_subdir must be a relative path inside the output folder: {sub!r}")
        return root / rel
    if post.get("id") in (None, ""):
        raise MediaError("post needs an 'id' (int or string) or meta.output_subdir")
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "-", str(post["id"])).strip(".-") or "untitled"
    return root / brand.slug / f"post-{safe_id}"


def _script(post: dict) -> Script:
    raw = post.get("script") or {}
    if isinstance(raw, str):
        import json
        raw = json.loads(raw or "{}")
    script = Script.model_validate({
        "title": post.get("title") or raw.get("title") or "Untitled", "hook": "", "segments": [], "cta": "",
        "caption": "", "hashtags": [], "description": "", "thumbnail_text": "", "sources": [],
        "claims_to_verify": [], **raw})
    if not script.segments:
        script.segments = [Segment(heading=script.title, narration=script.hook or script.title,
                                   on_screen_text=script.title, visual_prompt=script.title)]
    return script


def _image_provenance(imgs) -> list[dict]:
    return [provenance(str(r.path), "generated", r.tool, r.prompt, provider=r.provider, note=r.note) for r in imgs]


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (text or "").lower()).strip()


def _relativize(assets: dict, build: Path, final: Path, root: Path) -> dict:
    """Map build-folder paths to final paths relative to the output root."""
    def rel(p) -> str | None:
        if p is None:
            return None
        p = Path(p)
        try:
            p = final / p.relative_to(build)
        except ValueError:
            return str(p)  # outside the post folder (e.g. a music track): keep absolute
        return p.relative_to(root).as_posix()

    out = dict(assets)
    for key in ("video", "audio", "captions_srt", "thumbnail"):
        out[key] = rel(assets.get(key))
    out["images"] = [rel(p) for p in assets.get("images", [])]
    out["slides"] = [rel(p) for p in assets.get("slides", [])]
    out["provenance"] = [{**e, "path": rel(e["path"])} for e in assets.get("provenance", [])]
    return out
