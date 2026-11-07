"""render_post: turn a scripted post into finished media files.

Output goes to settings.output_dir/<brand>/post-<id>/ (built in a .partial
folder and swapped in at the end, so a failed re-render never leaves a
half-written post). Returned paths are relative to settings.output_dir.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image

from ..config import BrandProfile, Settings
from ..schemas import Script, Segment
from . import chapters
from .captions import time_segment, time_segment_words, write_srt
from .carousel import SlideKit, SlideText, render_carousel
from .images import generate_images
from .thumbnail import render_thumbnail
from .tts import concat_narration, synthesize_segments
from .util import (ASPECTS, SHORT_MAX_SECONDS, SLIDE_SIZE, VIDEO_SIZES, MediaError, Palette, RenderOptions,
                   probe, provenance, save_png_and_jpeg)
from .video import Beat, VideoSpec, assemble, pick_music

MIN_BEAT = 1.5      # seconds on screen per beat, even if the line is very short
GAP = 0.3           # breath between beats
TAIL = 0.8          # hold after the last line
LEAD = 0.1          # captions start just after the cut


def render_post(settings: Settings, brand: BrandProfile, post: dict) -> dict:
    fmt = post.get("format") or "short"
    if fmt not in ("short", "mid", "long", "carousel", "image"):
        raise MediaError(f"Unknown post format '{fmt}'")
    script = _script(post)
    root = Path(settings.output_dir).resolve()
    final = post_dir(root, brand, post)
    build = final.with_name(final.name + ".partial")
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir(parents=True)
    try:
        if fmt in ("short", "mid", "long"):
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

    imgs = _images_with_charts(settings, brand, segments, size, ASPECTS[fmt], out / "images", family, palette,
                               reserve_bottom=0.22 if fmt == "long" else 0.36)  # caption zone
    lines = [(s.narration or s.on_screen_text or s.heading).strip() for s in segments]
    heads = [s.on_screen_text for s in segments]
    from .looks import choose, compose
    pid = post.get("id") or 0
    seed = int(pid) if str(pid).isdigit() else __import__("zlib").crc32(str(pid).encode())  # ids may be strings
    look = post.get("look") or choose(post.get("_recent_looks") or [], seed=seed)
    images = [r.path if (i < len(segments) and segments[i].chart) else
              compose(r.path, size, look["layout"], palette, work / f"look-{i:02d}.png")
              for i, r in enumerate(imgs)]
    from .signature import resolve, stamp
    sig = resolve(brand)
    thumb_art = images[0]
    if sig and "intro" in sig["where"] and images:  # the brand's one constant, on the opening frame
        images[0] = stamp(images[0], sig, palette, brand.visual.font, work / "intro-signature.png")
    if script.cta and _norm(script.cta) not in _norm(" ".join(lines)):
        lines.append(script.cta)
        heads.append(brand.name)
        images.append(images[-1])

    from .tts import human_voice
    tts = human_voice(settings, brand, post.get("id"), lines, work / "voice") \
        or synthesize_segments(settings, brand, lines, work / "voice")
    beats, cues, slots, t, starts, owned, stocked = [], [], [], 0.0, [], [], []
    seg_words = tts.words or [None] * len(lines)
    from .charts import render_chart_clip
    for i, (line, head, img, dur) in enumerate(zip(lines, heads, images, tts.durations)):
        slot = max(MIN_BEAT, dur + (TAIL if i == len(lines) - 1 else GAP))
        chart = segments[i].chart if i < len(segments) else None
        clip = render_chart_clip(chart, size, palette, work / f"chart-{i:02d}.mp4", seconds=min(slot, 4.0)) \
            if chart else None
        own = _footage(settings, segments[i]) if i < len(segments) else None
        if own:
            clip, chart = own, None  # the person's own recording beats any generated visual
            owned.append(own)
        elif not chart and i < len(segments) and (getattr(segments[i], "broll", "") or "").strip():
            stock_clip = settings.home / segments[i].broll
            if stock_clip.is_file():
                clip = stock_clip
                stocked.append(stock_clip)
        beats.append(Beat(img, "" if chart else head, t, slot, clip=clip, still=bool(chart)))  # charts: own title, no pan
        if seg_words[i]:
            cues += time_segment_words(line, t, dur, seg_words[i])
        else:
            cues += time_segment(line, t + LEAD, max(0.4, dur - LEAD))
        slots.append(slot)
        starts.append((round(t, 2), segments[i].heading if i < len(segments) else ""))
        t += slot

    voice_paths = list(tts.paths)
    slate_s = 0.0
    if fmt == "long":  # closing slate: room for the Studio end screen, so it never covers content
        from .endslate import render_end_slate
        from .endslate import seconds as slate_seconds
        slate_s = slate_seconds()
        if slate_s:
            slate = render_end_slate(size, palette, brand.visual.font, brand.name, brand.visual.watermark, sig,
                                     work / "end-slate.png")
            beats.append(Beat(slate, "", t, slate_s, still=True))
            hush = work / "voice" / "end-slate-silence.wav"
            hush.parent.mkdir(parents=True, exist_ok=True)
            from .util import ffmpeg as _ff
            _ff(["-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.2", str(hush)])
            voice_paths.append(hush)
            slots.append(slate_s)
            t += slate_s
    audio = out / "audio.wav"
    concat_narration(voice_paths, slots, audio)
    srt = out / "captions.srt"
    write_srt(cues, srt)
    music = pick_music(f"{brand.slug}:{post.get('id')}:{script.title}")
    spec = VideoSpec(fmt, size, palette, brand.visual.font, brand.visual.watermark, opts, look=look)
    video = out / "video.mp4"
    duration = assemble(spec, beats, cues, audio, video, work, music=music, voiced=tts.provider != "silent")
    duration = probe(video)["duration"] or duration

    notes = list(tts.notes)
    if fmt == "short" and duration > SHORT_MAX_SECONDS:
        notes.append(f"WARNING: short runs {duration:.1f}s (> {SHORT_MAX_SECONDS:.0f}s); trim the script "
                     "before posting as a Reel/Short. Nothing was cut automatically.")
    if fmt == "mid" and not 61 <= duration <= 95:
        notes.append(f"WARNING: TikTok cut runs {duration:.1f}s; aim for 65-90s (TikTok's Creator Rewards "
                     "only count videos over a minute).")
    thumb = render_thumbnail(thumb_art, script.thumbnail_text or script.title,
                             palette, brand.visual.font, brand.visual.watermark, out / "thumbnail.png")

    variants = []
    if fmt == "long":  # A/B candidates for YouTube: different art and wording; pick one on the post page
        texts = [script.thumbnail_text or script.title]
        texts += [_short_words(t) for t in [*script.title_variants, script.title] if _short_words(t)]
        texts = list(dict.fromkeys(texts))
        arts = [images[min(i, len(images) - 1)] for i in (len(images) // 2, len(images) - 1)]
        for k, (art, text, style) in enumerate(zip(arts, (texts[1:] + texts)[:2], ("right", "band")), start=1):
            variants.append(render_thumbnail(art, text, palette, brand.visual.font, brand.visual.watermark,
                                             out / f"thumbnail-{k + 1}.png", style=style))
    if sig and "thumbnail" in sig["where"]:
        for v in (thumb, *variants):
            stamp(v, sig, palette, brand.visual.font)
    test_compare = []
    if fmt == "long" and variants:  # three distinct looks, ready for YouTube's Test & compare
        from .thumbnail import test_compare_set
        test_compare = test_compare_set([thumb, *variants], out / "test-and-compare")
    prov = _image_provenance(imgs)
    for v in variants:
        prov.append(provenance(str(v), "rendered", "pillow", "thumbnail variant"))
        prov.append(provenance(str(v.with_suffix(".jpg")), "rendered", "pillow", "thumbnail variant (JPEG)"))
    for v in test_compare:
        prov.append(provenance(str(v), "rendered", "pillow", "YouTube Test & compare thumbnail (under 2 MB)"))
    prov.append(provenance(str(audio), "own" if tts.provider == "human" else "generated", tts.tool, " ".join(lines),
                           provider=tts.provider,
                           note="Voice must be your own or licensed."))
    prov.append(provenance(str(srt), "rendered", "contentfactory.captions",
                           note="word timing from the voice" if tts.timing != "estimated"
                           else "timing estimated from audio length", timing=tts.timing))
    prov.append(provenance(str(thumb), "rendered", "pillow", script.thumbnail_text))
    prov.append(provenance(str(thumb.with_suffix(".jpg")), "rendered", "pillow", script.thumbnail_text,
                           note="JPEG copy for APIs that require JPEG"))
    prov.append(provenance(str(video), "rendered", "ffmpeg", "", fps=opts.fps, notes=notes,
                           music=music.name if music else None))
    for own in dict.fromkeys(owned):
        prov.append(provenance(str(own), "own", "footage", "", "recorded by the channel owner"))
    for clip in dict.fromkeys(stocked):
        side = clip.with_suffix(".json")
        info = json.loads(side.read_text()) if side.is_file() else {}
        prov.append(provenance(str(clip), "licensed", info.get("provider", "stock"), info.get("query", ""),
                               f"{info.get('license', 'stock licence')}; by {info.get('author', '?')} {info.get('page', '')}".strip()))
    if music:
        prov.append(provenance(str(music), "licensed", "user-music", "",
                               "user-supplied via FACTORY_MUSIC_DIR; keep the licence on file"))
    return {"video": video, "audio": audio, "captions_srt": srt, "images": [r.path for r in imgs], "slides": [],
            "thumbnail": thumb, "thumbnail_variants": [thumb, *variants], "duration": round(duration, 3),
            "chapters": chapters.build(starts, duration) if fmt == "long" else [], "look": look,
            "end_slate_seconds": slate_s, "test_compare": test_compare,
            "signature": sig["device"] if sig else None, "provenance": prov}


# ---------------------------------------------------------------- slides
def _render_slides(settings: Settings, brand: BrandProfile, script: Script, fmt: str, out: Path, post: dict) -> dict:
    segments = script.segments[:1] if fmt == "image" else script.segments
    family = f"{brand.slug}:{script.title}"
    imgs = _images_with_charts(settings, brand, segments, SLIDE_SIZE, ASPECTS[fmt], out / "images", family,
                               Palette.from_brand(brand))
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
    for i, seg in enumerate(segments):  # a chart slide is the chart itself (it carries its own title)
        if seg.chart and i < len(slides):
            save_png_and_jpeg(Image.open(imgs[i].path).convert("RGB"), Path(slides[i]))
    from .signature import resolve, stamp
    sig = resolve(brand)
    if sig and "cover" in sig["where"] and slides and not segments[0].chart:
        stamp(Path(slides[0]), sig, Palette.from_brand(brand), brand.visual.font)
    prov = _image_provenance(imgs)
    for p, t in zip(slides, texts):
        prov.append(provenance(str(p), "rendered", "pillow", t.headline))
        prov.append(provenance(str(p.with_suffix(".jpg")), "rendered", "pillow", t.headline,
                               note="JPEG copy for APIs that require JPEG"))
    if fmt == "carousel" and len(slides) > 20:
        prov[-1]["notes"] = ["WARNING: Instagram carousels allow at most 20 items"]
    return {"video": None, "audio": None, "captions_srt": None, "images": [r.path for r in imgs],
            "slides": slides, "thumbnail": None, "duration": 0.0,
            "signature": sig["device"] if sig else None, "provenance": prov}


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


def _footage(settings, seg) -> Path | None:
    """A person's own screen recording or camera clip for this beat (Segment.footage), if it exists."""
    raw = (getattr(seg, "footage", "") or "").strip()
    if not raw:
        return None
    p = Path(raw).expanduser()
    p = p if p.is_absolute() else settings.home / p
    if not p.is_file():
        raise MediaError(f"footage not found: {raw} (paths are relative to {settings.home})")
    return p


def _images_with_charts(settings, brand, segments, size, aspect, out_dir, family, palette, reserve_bottom=0.0):
    """Illustrations for ordinary beats; exact data charts (no AI) for beats that carry a chart."""
    import json as _json

    from .charts import render_chart
    from .images import ImageResult
    plain = [i for i, s in enumerate(segments) if not s.chart]
    made = generate_images(settings, brand, [segments[i].visual_prompt for i in plain], size, aspect, out_dir,
                           family=family) if plain else []
    by_index = dict(zip(plain, made))
    out = []
    for i, s in enumerate(segments):
        if s.chart:
            path = render_chart(s.chart, size, palette, brand.visual.font, out_dir / f"chart-{i:02d}.png",
                                reserve_bottom=reserve_bottom)
            out.append(ImageResult(path, "chart", "contentfactory.charts", _json.dumps(s.chart.model_dump())[:500],
                                   note="drawn from the script's numbers; check them"))
        else:
            out.append(by_index[i])
    return out


def _image_provenance(imgs) -> list[dict]:
    return [provenance(str(r.path), "rendered" if r.provider == "chart" else "generated", r.tool, r.prompt,
                       provider=r.provider, note=r.note) for r in imgs]


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
    if assets.get("thumbnail_variants"):
        out["thumbnail_variants"] = [rel(p) for p in assets["thumbnail_variants"]]
    if assets.get("test_compare"):
        out["test_compare"] = [rel(p) for p in assets["test_compare"]]
    out["provenance"] = [{**e, "path": rel(e["path"])} for e in assets.get("provenance", [])]
    return out


def _short_words(text: str, n: int = 5) -> str:
    """Thumbnail wording from a title: the first few words, without trailing punctuation."""
    words = (text or "").replace(":", " ").split()
    return " ".join(words[:n]).rstrip(",.;:!?") if words else ""
