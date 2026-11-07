"""The closing slate on long videos: 20 seconds of brand background with room for YouTube's end screen
(two video tiles and the subscribe circle), so the end screen you add in Studio never covers content.

YouTube shows end-screen elements in the last 5-20 seconds and the Data API can't set them, so the
video leaves the space and you import the brand's end-screen layout in Studio (see `factory youtube-plan`).
END_SLATE_SECONDS (default 20, 0 turns it off).
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw

from . import fonts
from .util import Palette, save_png_and_jpeg


def seconds() -> float:
    try:
        return max(0.0, float(os.environ.get("END_SLATE_SECONDS", "20")))
    except ValueError:
        return 20.0


def render_end_slate(size: tuple[int, int], palette: Palette, family: str, brand_name: str, watermark: str,
                     sig: dict | None, out: Path, heading: str = "Watch next") -> Path:
    w, h = size
    img = Image.new("RGBA", size, (*palette.dark, 255))
    d = ImageDraw.Draw(img)
    panel = (*[round(a * 0.86 + b * 0.14) for a, b in zip(palette.dark, palette.light)], 255)
    # Where Studio's elements usually go on 16:9: two video tiles left/centre, subscribe circle right.
    tw, th = int(w * 0.30), int(w * 0.30 * 9 / 16)
    y = int(h * 0.36)
    for x in (int(w * 0.08), int(w * 0.42)):
        d.rounded_rectangle((x, y, x + tw, y + th), radius=int(h * 0.02), fill=panel)
    r = int(h * 0.11)
    cx, cy = int(w * 0.84), y + th // 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=panel)
    accent = palette.accent_on(palette.dark, 3.0)
    f = fonts.load(fonts.font_path(family, "black"), int(h * 0.075))
    d.text((int(w * 0.08), int(h * 0.22)), heading, font=f, fill=(*palette.light, 255), anchor="ls")
    d.rectangle((int(w * 0.08), int(h * 0.245), int(w * 0.08) + int(w * 0.06), int(h * 0.255)), fill=(*accent, 255))
    small = fonts.load(fonts.font_path(family, "semibold"), int(h * 0.035))
    d.text((int(w * 0.08), int(h * 0.88)), brand_name + (f"  ·  {watermark}" if watermark else ""), font=small,
           fill=(*palette.light, 200), anchor="ls")
    if sig:
        from .signature import draw
        img = draw(img, sig, palette, family)
    out.parent.mkdir(parents=True, exist_ok=True)
    save_png_and_jpeg(img, out)
    return out
