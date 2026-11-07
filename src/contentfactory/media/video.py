"""Video assembly with ffmpeg.

Each beat (script segment) becomes a clip: a still image with a slow eased
Ken Burns move, a Pillow-drawn overlay (headline + watermark) and burned-in
word-chunked captions. Clips are encoded in parallel with identical H.264
settings, joined losslessly with the concat demuxer, and muxed with the
narration (plus optional ducked background music) into an MP4 that Reels,
TikTok and YouTube accept: H.264 high / yuv420p, AAC 48 kHz, +faststart.
"""
from __future__ import annotations

import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from . import fonts
from .captions import CaptionStyle, Cue, write_ass
from .util import Palette, RenderOptions, ffmpeg, seed_of

MUSIC_EXTS = {".mp3", ".m4a", ".aac", ".wav", ".ogg", ".flac"}
MOTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left", "drift_up"]


@dataclass
class Beat:
    image: Path
    headline: str
    start: float
    duration: float
    clip: Path | None = None  # an animated chart (Manim) used instead of the still, last frame held
    still: bool = False       # no pan/zoom (charts: every number must stay on screen)


@dataclass
class VideoSpec:
    fmt: str                  # short | long
    size: tuple[int, int]
    palette: Palette
    font_family: str
    watermark: str
    options: RenderOptions


# ---------------------------------------------------------------- overlay
def draw_overlay(spec: VideoSpec, headline: str, out: Path) -> None:
    """Transparent PNG with the headline card and the watermark."""
    w, h = spec.size
    img = Image.new("RGBA", spec.size, (0, 0, 0, 0))
    vertical = h > w
    bold = fonts.font_path(spec.font_family, "extrabold")
    if headline.strip():
        pad_x, pad_y = (44, 34) if vertical else (40, 28)
        max_w = int(w * (0.80 if vertical else 0.52))
        block = fonts.fit(headline.strip(), bold, max_w, int(h * (0.16 if vertical else 0.22)),
                          max_size=78 if vertical else 64, min_size=40, leading=1.12, max_lines=3)
        bw, bh = block.width() + 2 * pad_x, block.height + 2 * pad_y + 14
        x0 = (w - bw) // 2 if vertical else 80
        y0 = int(h * 0.115) if vertical else 70
        card = ImageDraw.Draw(img)
        card.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=30, fill=(*spec.palette.dark, 220))
        accent = spec.palette.accent_on(spec.palette.dark)
        bar_w = 64
        bar_x = x0 + (bw - bar_w) // 2 if vertical else x0 + pad_x
        card.rounded_rectangle((bar_x, y0 + bh - pad_y + 2, bar_x + bar_w, y0 + bh - pad_y + 10), radius=4,
                               fill=(*accent, 255))
        fonts.draw_block(img, block, (x0 + pad_x, y0 + pad_y), (*spec.palette.light, 255),
                         align="center" if vertical else "left", box_width=bw - 2 * pad_x)
    if spec.watermark:
        wm_font = fonts.load(fonts.font_path(spec.font_family, "semibold"), 34 if vertical else 30)
        tw = int(wm_font.getlength(spec.watermark))
        pos = (64, int(h * 0.058)) if vertical else (w - tw - 60, 50)
        layer = Image.new("RGBA", spec.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text(pos, spec.watermark, font=wm_font, fill=(255, 255, 255, 200),
                                   stroke_width=2, stroke_fill=(0, 0, 0, 90))
        img.alpha_composite(layer)
    img.save(out)


# ---------------------------------------------------------------- clips
def _zoompan(motion: str, frames: int, size: tuple[int, int], fps: int) -> str:
    """zoompan filter for an eased (smoothstep) move over `frames` frames."""
    d = max(1, frames - 1)
    p = f"(on/{d})"
    e = f"({p}*{p}*(3-2*{p}))"
    cx, cy = "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
    z, x, y = f"1.0+0.10*{e}", cx, cy
    if motion == "zoom_out":
        z = f"1.10-0.10*{e}"
    elif motion == "pan_right":
        z, x = "1.12", f"(iw-iw/zoom)*{e}"
    elif motion == "pan_left":
        z, x = "1.12", f"(iw-iw/zoom)*(1-{e})"
    elif motion == "drift_up":
        z, y = f"1.06+0.04*{e}", f"(ih-ih/zoom)*(1-{e})"
    w, h = size
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps}"


def render_clip(spec: VideoSpec, beat: Beat, index: int, frames: int, cues: list[Cue], work: Path) -> Path:
    """Encode one beat as an H.264 clip of exactly `frames` frames (no audio)."""
    w, h = spec.size
    fps = spec.options.fps
    overlay = work / f"overlay-{index:02d}.png"
    draw_overlay(spec, "" if (beat.clip or beat.still) else beat.headline, overlay)  # charts carry their own title
    ass = work / f"captions-{index:02d}.ass"
    style = CaptionStyle.for_format(spec.fmt, fonts.family_name(fonts.font_path(spec.font_family, "extrabold")))
    write_ass(cues, style, ass, offset=beat.start)
    motion = MOTIONS[(seed_of(str(beat.image)) + index) % len(MOTIONS)]
    if beat.clip or beat.still:
        bg = (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},"
              f"tpad=stop_mode=clone:stop_duration={frames / fps + 1:.3f},setsar=1[bg];")
    else:
        bg = f"[0:v]scale={w * 2}:{h * 2}:flags=lanczos,{_zoompan(motion, frames, spec.size, fps)},setsar=1[bg];"
    graph = bg + f"[bg][1:v]overlay=0:0:format=auto,ass={ass.name},format=yuv420p[v]"
    out = work / f"clip-{index:02d}.mp4"
    ffmpeg(["-i", str((beat.clip or beat.image).resolve()),
            "-loop", "1", "-framerate", str(fps), "-t", f"{frames / fps + 0.5:.3f}", "-i", overlay.name,
            "-filter_complex", graph, "-map", "[v]", "-frames:v", str(frames), "-r", str(fps),
            *x264_args(spec.options), "-an", out.name], cwd=work)
    return out


def x264_args(opts: RenderOptions) -> list[str]:
    return ["-c:v", "libx264", "-preset", opts.preset, "-crf", str(opts.crf), "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-g", str(opts.fps * 2), "-bf", "2"]


# ---------------------------------------------------------------- assembly
def assemble(spec: VideoSpec, beats: list[Beat], cues: list[Cue], narration: Path, out: Path, work: Path,
             music: Path | None = None, voiced: bool = True) -> float:
    """Render all beats, join them and mux audio. Returns the duration in seconds."""
    fps = spec.options.fps
    bounds = [round(b.start * fps) for b in beats] + [round((beats[-1].start + beats[-1].duration) * fps)]
    frame_counts = [max(1, bounds[i + 1] - bounds[i]) for i in range(len(beats))]
    total = sum(frame_counts) / fps
    with ThreadPoolExecutor(max_workers=max(1, spec.options.workers)) as pool:
        jobs = [pool.submit(render_clip, spec, b, i, frame_counts[i],
                            [c for c in cues if b.start <= c.start < b.start + b.duration], work)
                for i, b in enumerate(beats)]
        clips = [j.result() for j in jobs]
    listing = work / "clips.txt"
    listing.write_text("".join(f"file '{c.name}'\n" for c in clips))
    args = ["-f", "concat", "-safe", "0", "-i", listing.name, "-i", str(narration.resolve())]
    voice = "[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    if voiced:
        voice += ",loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000"
    if music:
        args += ["-stream_loop", "-1", "-i", str(music.resolve())]
        level = 0.16 if voiced else 0.5
        fade = max(0.0, total - 2.0)
        graph = (f"{voice},asplit=2[v1][v2];"
                 f"[2:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={level},"
                 f"afade=t=in:d=1.0,afade=t=out:st={fade:.2f}:d=2.0[m];"
                 f"[m][v2]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=350[duck];"
                 f"[v1][duck]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        graph = f"{voice}[a]"
    ffmpeg([*args, "-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", f"{total:.3f}",
            "-movflags", "+faststart", str(out.resolve())], cwd=work)
    return total


def pick_music(key: str) -> Path | None:
    """Deterministically pick a track from FACTORY_MUSIC_DIR (None if unset/empty)."""
    folder = os.environ.get("FACTORY_MUSIC_DIR", "")
    if not folder or not Path(folder).is_dir():
        return None
    tracks = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in MUSIC_EXTS and p.is_file())
    if not tracks:
        return None
    return tracks[int(hashlib.sha256(key.encode()).hexdigest(), 16) % len(tracks)]
