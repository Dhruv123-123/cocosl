"""YouTube-style thumbnail (1280x720): artwork, a dark side gradient and
2-5 huge words, the last line in the brand accent."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from . import fonts
from .carousel import scrim
from .util import THUMB_SIZE, Palette, save_png_and_jpeg


STYLES = ("left", "right", "band")  # three looks for YouTube's Test & compare


def render_thumbnail(art_path: Path, text: str, palette: Palette, family: str, watermark: str, out: Path,
                     style: str = "left") -> Path:
    """`left`: text on a dark left gradient (the default). `right`: mirrored. `band`: art on top, text on a
    solid band along the bottom. Test & compare needs the variants to differ in more than the words."""
    w, h = THUMB_SIZE
    art = Image.open(art_path).convert("RGB")
    img = ImageOps.fit(art, THUMB_SIZE, Image.LANCZOS, centering=(0.5, 0.4)).convert("RGBA")
    words = " ".join((text or "").split()[:6]).upper() or " "
    margin = 70
    accent = palette.accent_on(palette.dark, 4.5)
    if style == "band":
        band_h = int(h * 0.42)
        d = ImageDraw.Draw(img)
        d.rectangle((0, h - band_h, w, h), fill=(*palette.dark, 245))
        d.rectangle((0, h - band_h, w, h - band_h + 12), fill=(*accent, 255))
        block = fonts.fit(words, fonts.font_path(family, "black"), w - 2 * margin, band_h - 70, 120, 50,
                          leading=1.0, max_lines=2)
        y = h - band_h + 12 + (band_h - 12 - block.height) // 2
        xs = [margin] * len(block.lines)
    else:
        sc = scrim(THUMB_SIZE, palette.dark, 0.95, 0.2, 235, direction="right")
        if style == "right":
            sc = sc.transpose(Image.FLIP_LEFT_RIGHT)
        img.alpha_composite(sc)
        block = fonts.fit(words, fonts.font_path(family, "black"), int(w * 0.62), h - 2 * margin - 40, 150, 60,
                          leading=1.0, max_lines=3)
        y = (h - block.height) // 2
        if style == "right":
            probe = ImageDraw.Draw(Image.new("L", (1, 1)))
            xs = [w - margin - int(probe.textlength(line, font=block.font)) for line in block.lines]
        else:
            xs = [margin] * len(block.lines)
    for i, line in enumerate(block.lines):
        single = fonts.TextBlock(block.font, [line], block.line_height)
        color = accent if i == len(block.lines) - 1 and len(block.lines) > 1 else palette.light
        fonts.draw_block(img, single, (xs[i], y + i * block.line_height), (*color, 255),
                         shadow=(0, 0, 0, 170), shadow_radius=12, stroke=3, stroke_fill=(*palette.dark, 255))
    d = ImageDraw.Draw(img)
    if style != "band":
        bar_x = xs[0] if style == "left" else w - margin - 90
        d.rounded_rectangle((bar_x, y - 34, bar_x + 90, y - 22), radius=6, fill=(*accent, 255))
    if watermark:
        f = fonts.load(fonts.font_path(family, "semibold"), 28)
        if style == "right":
            d.text((w - margin, h - 44), watermark, font=f, fill=(*palette.light, 210), anchor="rs")
        elif style == "band":
            d.text((w - margin, h - 30), watermark, font=f, fill=(*palette.light, 180), anchor="rs")
        else:
            d.text((margin, h - 44), watermark, font=f, fill=(*palette.light, 210), anchor="ls")
    save_png_and_jpeg(img, out)
    return out


TEST_COMPARE_MAX_BYTES = 2 * 1024 * 1024  # YouTube Test & compare: JPG/PNG, up to 2 MB, 16:9


def test_compare_set(paths: list[Path], out_dir: Path) -> list[Path]:
    """A.jpg, B.jpg, C.jpg for Studio's Test & compare, each under 2 MB."""
    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for letter, p in zip("ABC", paths):
        img = Image.open(p).convert("RGB")
        dst = out_dir / f"{letter}.jpg"
        for q in (92, 85, 78, 70, 60):
            img.save(dst, quality=q, optimize=True, progressive=True)
            if dst.stat().st_size <= TEST_COMPARE_MAX_BYTES:
                break
        made.append(dst)
    return made
