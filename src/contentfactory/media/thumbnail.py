"""YouTube-style thumbnail (1280x720): artwork, a dark side gradient and
2-5 huge words, the last line in the brand accent."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from . import fonts
from .carousel import scrim
from .util import THUMB_SIZE, Palette, save_png_and_jpeg


def render_thumbnail(art_path: Path, text: str, palette: Palette, family: str, watermark: str, out: Path) -> Path:
    w, h = THUMB_SIZE
    art = Image.open(art_path).convert("RGB")
    img = ImageOps.fit(art, THUMB_SIZE, Image.LANCZOS, centering=(0.5, 0.4)).convert("RGBA")
    img.alpha_composite(scrim(THUMB_SIZE, palette.dark, 0.95, 0.2, 235, direction="right"))
    words = " ".join((text or "").split()[:6]).upper() or " "
    margin = 70
    block = fonts.fit(words, fonts.font_path(family, "black"), int(w * 0.62), h - 2 * margin - 40, 150, 60,
                      leading=1.0, max_lines=3)
    y = (h - block.height) // 2
    accent = palette.accent_on(palette.dark, 4.5)
    for i, line in enumerate(block.lines):
        single = fonts.TextBlock(block.font, [line], block.line_height)
        color = accent if i == len(block.lines) - 1 and len(block.lines) > 1 else palette.light
        fonts.draw_block(img, single, (margin, y + i * block.line_height), (*color, 255),
                         shadow=(0, 0, 0, 170), shadow_radius=12, stroke=3, stroke_fill=(*palette.dark, 255))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((margin, y - 34, margin + 90, y - 22), radius=6, fill=(*accent, 255))
    if watermark:
        f = fonts.load(fonts.font_path(family, "semibold"), 28)
        d.text((margin, h - 44), watermark, font=f, fill=(*palette.light, 210), anchor="ls")
    save_png_and_jpeg(img, out)
    return out
