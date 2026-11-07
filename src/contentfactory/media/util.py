"""Small shared helpers for the media module: ffmpeg/ffprobe calls, colours,
provenance records and render options."""
from __future__ import annotations

import colorsys
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..config import BrandProfile, Settings

# Target pixel sizes per format.
VIDEO_SIZES = {"short": (1080, 1920), "long": (1920, 1080)}
SLIDE_SIZE = (1080, 1350)
THUMB_SIZE = (1280, 720)
ASPECTS = {"short": "9:16", "long": "16:9", "carousel": "4:5", "image": "4:5"}
SHORT_MAX_SECONDS = 90.0
TIKTOK_CUT_MAX_SECONDS = 180.0  # TikTok-only cuts aim for 60-90s; warn only when far over


class MediaError(RuntimeError):
    """A media step failed in a way the caller should see (bad input, tool error)."""


class ProviderError(MediaError):
    """A TTS/image provider is unavailable or failed; auto mode falls through."""


@dataclass
class RenderOptions:
    """Knobs for speed vs quality. Read from `settings.extra` so tests and
    previews can render faster without touching env vars."""
    fps: int = 30
    preset: str = "medium"
    crf: int = 20
    workers: int = 4
    keep_work: bool = False

    @classmethod
    def from_settings(cls, settings: Settings) -> "RenderOptions":
        extra = settings.extra or {}
        return cls(
            fps=int(extra.get("video_fps", 30)),
            preset=str(extra.get("x264_preset", "medium")),
            crf=int(extra.get("x264_crf", 20)),
            workers=int(extra.get("render_workers", 4)),
            keep_work=bool(extra.get("keep_work", False)),
        )


# ---------------------------------------------------------------- processes
def run(cmd: list[str], *, input_bytes: bytes | None = None, cwd: Path | None = None,
        timeout: float = 1800) -> subprocess.CompletedProcess:
    """Run a command, raising MediaError with the tail of stderr on failure."""
    try:
        proc = subprocess.run(cmd, input=input_bytes, cwd=cwd, capture_output=True, timeout=timeout)
    except FileNotFoundError as e:
        raise MediaError(f"{cmd[0]} not found on PATH") from e
    except subprocess.TimeoutExpired as e:
        raise MediaError(f"{cmd[0]} timed out after {timeout}s") from e
    if proc.returncode != 0:
        tail = proc.stderr.decode(errors="replace")[-1500:]
        raise MediaError(f"{Path(cmd[0]).name} failed ({proc.returncode}): {tail}")
    return proc


def ffmpeg(args: list[str], cwd: Path | None = None) -> None:
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], cwd=cwd)


def probe(path: Path) -> dict:
    """ffprobe a file: {'duration': float, 'width': int|None, 'height': int|None}."""
    proc = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    data = json.loads(proc.stdout or b"{}")
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    return {
        "duration": float(data.get("format", {}).get("duration") or 0.0),
        "width": video.get("width"),
        "height": video.get("height"),
        "streams": [s.get("codec_type") for s in data.get("streams", [])],
    }


# ---------------------------------------------------------------- colours
RGB = tuple[int, int, int]


def hex_to_rgb(value: str) -> RGB:
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    try:
        return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
    except (ValueError, IndexError):
        return (128, 128, 128)


def luminance(rgb: RGB) -> float:
    """WCAG relative luminance."""
    def ch(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: RGB, b: RGB) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a: RGB, b: RGB, t: float) -> RGB:
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))  # type: ignore[return-value]


def shade(rgb: RGB, lightness: float | None = None, sat_mul: float = 1.0) -> RGB:
    """Return the colour with its HLS lightness set (0..1) and saturation scaled."""
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    l = l if lightness is None else lightness
    r, g, b = colorsys.hls_to_rgb(h, max(0, min(1, l)), max(0, min(1, s * sat_mul)))
    return int(r * 255), int(g * 255), int(b * 255)


@dataclass
class Palette:
    """Brand palette resolved into roles: dark (backgrounds), light (paper/text
    on dark), accents (highlights), ordered by saturation."""
    dark: RGB
    light: RGB
    accents: list[RGB]

    @property
    def accent(self) -> RGB:
        return self.accents[0]

    def accent_on(self, bg: RGB, minimum: float = 3.0) -> RGB:
        """An accent readable on `bg`, or a lightened/darkened fallback."""
        for a in self.accents:
            if contrast(a, bg) >= minimum:
                return a
        a = self.accent
        return shade(a, 0.75) if luminance(bg) < 0.3 else shade(a, 0.3)

    @classmethod
    def from_brand(cls, brand: BrandProfile) -> "Palette":
        colors = [hex_to_rgb(c) for c in (brand.visual.palette or [])] or [(15, 23, 42), (248, 250, 252)]
        by_lum = sorted(colors, key=luminance)
        dark, light = by_lum[0], by_lum[-1]
        if luminance(dark) > 0.08:
            dark = shade(dark, 0.12)
        if luminance(light) < 0.7:
            light = (246, 244, 238)
        rest = [c for c in colors if c not in (by_lum[0], by_lum[-1])]

        def sat(c: RGB) -> float:
            return colorsys.rgb_to_hls(*(x / 255 for x in c))[2]
        accents = sorted(rest, key=sat, reverse=True) or [shade(dark, 0.55, 2.0)]
        return cls(dark=dark, light=light, accents=accents)


# ---------------------------------------------------------------- misc
def seed_of(*parts: str) -> int:
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:12], 16)


def word_count(text: str) -> int:
    return len([w for w in (text or "").split() if any(ch.isalnum() for ch in w)])


def provenance(rel: str, source: str, tool: str, prompt: str = "", license: str = "", **extra) -> dict:
    entry = {"path": rel, "source": source, "tool": tool, "prompt": prompt, "license": license}
    entry.update({k: v for k, v in extra.items() if v not in (None, "", [], {})})
    return entry


def save_png_and_jpeg(img, png_path: Path) -> Path:
    """Save a PNG plus a high-quality JPEG twin (Instagram's API only takes JPEG)."""
    rgb = img.convert("RGB")
    rgb.save(png_path, compress_level=3)
    jpg = png_path.with_suffix(".jpg")
    rgb.save(jpg, quality=93, subsampling=0, optimize=True, progressive=True)
    return jpg


def jpeg_twin(rel_png: str) -> str:
    return rel_png[: -len(".png")] + ".jpg" if rel_png.endswith(".png") else rel_png
