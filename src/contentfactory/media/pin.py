"""A 2:3 Pinterest pin (1000x1500) from a post's art: image on top, title band below, brand signature."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from . import fonts
from .signature import draw as draw_signature
from .util import Palette, save_png_and_jpeg

PIN_SIZE = (1000, 1500)


def render_pin(art_path: Path, title: str, palette: Palette, family: str, watermark: str, sig: dict | None,
               out: Path) -> Path:
    w, h = PIN_SIZE
    art_h = int(h * 0.62)
    img = Image.new("RGBA", PIN_SIZE, (*palette.dark, 255))
    art = ImageOps.fit(Image.open(art_path).convert("RGB"), (w, art_h), Image.LANCZOS, centering=(0.5, 0.45))
    img.paste(art, (0, 0))
    d = ImageDraw.Draw(img)
    accent = palette.accent_on(palette.dark, 3.0)
    d.rectangle((0, art_h, w, art_h + 14), fill=(*accent, 255))
    margin = 70
    block = fonts.fit(title or " ", fonts.font_path(family, "black"), w - 2 * margin, h - art_h - 200, 96, 44,
                      leading=1.05, max_lines=4)
    fonts.draw_block(img, block, (margin, art_h + 70), (*palette.light, 255))
    if watermark:
        f = fonts.load(fonts.font_path(family, "semibold"), 34)
        d.text((margin, h - 60), watermark, font=f, fill=(*accent, 255), anchor="ls")
    if sig:
        img = draw_signature(img, sig, palette, family)
    out.parent.mkdir(parents=True, exist_ok=True)
    save_png_and_jpeg(img, out)
    return out
