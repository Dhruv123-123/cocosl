"""Carousel and single-image slides (1080x1350, Instagram 4:5).

Slide 1: full-bleed artwork, big hook headline, "Swipe" cue.
Inner slides: paper background, rounded image inset, kicker, headline, body.
Last slide: dark CTA slide with a "Save this" prompt and the brand CTA.
Every slide carries the watermark and a "3/8" counter.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from .. import i18n
from . import fonts
from .util import RGB, SLIDE_SIZE, Palette, mix, save_png_and_jpeg

M = 88  # outer margin


@dataclass
class SlideText:
    headline: str
    body: str = ""
    kicker: str = ""


@dataclass
class SlideKit:
    palette: Palette
    family: str
    watermark: str
    brand_name: str
    cta: str
    language: str = "en"

    def font(self, weight: str) -> str:
        return fonts.font_path(self.family, weight)


# ---------------------------------------------------------------- primitives
def scrim(size: tuple[int, int], color: RGB, start: float, end: float, max_alpha: int = 235,
          direction: str = "down") -> Image.Image:
    """Gradient overlay: transparent at `start`, max_alpha at `end` (fractions)."""
    w, h = size
    horizontal = direction == "right"
    span = w if horizontal else h
    ramp = Image.new("L", (span, 1) if horizontal else (1, span))
    for i in range(span):
        t = max(0.0, min(1.0, (i / span - start) / ((end - start) or 1e-6)))
        ramp.putpixel((i, 0) if horizontal else (0, i), int(max_alpha * t * t * (3 - 2 * t)))
    mask = ramp.resize((w, h))
    layer = Image.new("RGBA", size, (*color, 255))
    layer.putalpha(mask)
    return layer


def rounded(img: Image.Image, size: tuple[int, int], radius: int) -> Image.Image:
    fitted = ImageOps.fit(img.convert("RGBA"), size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    fitted.putalpha(mask)
    return fitted


def pill(img: Image.Image, text: str, font_path: str, size: int, xy: tuple[int, int], fill: RGB, text_fill: RGB,
         anchor: str = "left", alpha: int = 255) -> tuple[int, int, int, int]:
    """Rounded label; xy is the top-left (or top-right with anchor='right')."""
    font = fonts.load(font_path, size)
    tw = int(font.getlength(text))
    pw, ph = tw + int(size * 1.4), int(size * 2.0)
    x = xy[0] - pw if anchor == "right" else xy[0]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x, xy[1], x + pw, xy[1] + ph), radius=ph // 2, fill=(*fill, alpha))
    d.text((x + pw / 2, xy[1] + ph / 2), text, font=font, fill=(*text_fill, 255), anchor="mm")
    img.alpha_composite(layer)
    return x, xy[1], x + pw, xy[1] + ph


def bookmark_icon(draw: ImageDraw.ImageDraw, x: int, y: int, h: int, fill: RGB) -> None:
    w = int(h * 0.72)
    draw.polygon([(x, y), (x + w, y), (x + w, y + h), (x + w // 2, y + int(h * 0.72)), (x, y + h)], fill=fill)


def footer(img: Image.Image, kit: SlideKit, counter: str, on_dark: bool) -> None:
    w, h = img.size
    col = kit.palette.light if on_dark else kit.palette.dark
    font = fonts.load(kit.font("semibold"), 30)
    d = ImageDraw.Draw(img)
    y = h - 64
    if kit.watermark:
        d.text((M, y), kit.watermark, font=font, fill=(*col, 200), anchor="ls")
    if counter:
        d.text((w - M, y), counter, font=font, fill=(*col, 200), anchor="rs")


# ---------------------------------------------------------------- slides
def hook_slide(kit: SlideKit, art: Image.Image, text: SlideText, counter: str, swipe: bool) -> Image.Image:
    w, h = SLIDE_SIZE
    img = ImageOps.fit(art.convert("RGB"), SLIDE_SIZE, Image.LANCZOS).convert("RGBA")
    img.alpha_composite(scrim(SLIDE_SIZE, kit.palette.dark, 0.18, 0.78, 245))
    img.alpha_composite(scrim(SLIDE_SIZE, kit.palette.dark, 0.0, 0.25, 110).transpose(Image.FLIP_TOP_BOTTOM))
    accent = kit.palette.accent_on(kit.palette.dark, 4.5)
    bottom = h - 150
    body_block = None
    if text.body:
        body_block = fonts.fit(text.body, kit.font("medium"), w - 2 * M, 230, 40, 28, leading=1.32, max_lines=4)
        bottom -= body_block.height + 34
    head = fonts.fit(text.headline, kit.font("extrabold"), w - 2 * M, int(h * 0.42), 112, 52, leading=1.06,
                     max_lines=5)
    y = bottom - head.height
    kicker = (text.kicker or kit.brand_name).upper()
    kfont = fonts.load(kit.font("bold"), 30)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((M, y - 74, M + 56, y - 66), radius=4, fill=(*accent, 255))
    d.text((M + 76, y - 70), kicker, font=kfont, fill=(*accent, 255), anchor="lm")
    fonts.draw_block(img, head, (M, y), (*kit.palette.light, 255), shadow=(0, 0, 0, 120), shadow_radius=14)
    if body_block:
        fonts.draw_block(img, body_block, (M, y + head.height + 34), (*mix(kit.palette.light, kit.palette.dark, 0.12), 255))
    if counter:
        pill(img, counter, kit.font("semibold"), 26, (w - M, M - 20), kit.palette.dark, kit.palette.light,
             anchor="right", alpha=190)
    if swipe:
        font = fonts.load(kit.font("bold"), 30)
        label = i18n.t(kit.language, "swipe")
        tw = int(font.getlength(label))
        x1, yy = w - M, h - 64
        d.text((x1 - 54 - tw, yy), label, font=font, fill=(*accent, 255), anchor="ls")
        _arrow(d, x1 - 40, yy - 11, 40, accent)
    footer(img, kit, "", True)
    return img.convert("RGB")


def inner_slide(kit: SlideKit, art: Image.Image, text: SlideText, counter: str) -> Image.Image:
    w, h = SLIDE_SIZE
    p = kit.palette
    img = Image.new("RGBA", SLIDE_SIZE, (*p.light, 255))
    inset_h = int(h * 0.42)
    img.alpha_composite(rounded(art, (w - 2 * M, inset_h), 34), (M, M))
    y = M + inset_h + 56
    ink = p.dark
    accent = p.accent_on(p.light, 3.2)
    d = ImageDraw.Draw(img)
    if text.kicker:
        kfont = fonts.load(kit.font("bold"), 28)
        d.rounded_rectangle((M, y + 4, M + 40, y + 10), radius=3, fill=(*accent, 255))
        d.text((M + 56, y + 7), text.kicker.upper(), font=kfont, fill=(*accent, 255), anchor="lm")
        y += 52
    bottom = h - 120
    head = fonts.fit(text.headline, kit.font("extrabold"), w - 2 * M, int((bottom - y) * 0.5), 76, 44,
                     leading=1.08, max_lines=3)
    y = fonts.draw_block(img, head, (M, y), (*ink, 255)) + 30
    if text.body:
        body = fonts.fit(text.body, kit.font("regular"), w - 2 * M, bottom - y, 46, 28, leading=1.36)
        fonts.draw_block(img, body, (M, y), (*mix(ink, p.light, 0.18), 255))
    footer(img, kit, counter, False)
    return img.convert("RGB")


def cta_slide(kit: SlideKit, art: Image.Image, text: SlideText, counter: str) -> Image.Image:
    w, h = SLIDE_SIZE
    p = kit.palette
    bg = ImageOps.fit(art.convert("RGB"), SLIDE_SIZE, Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.55).convert("RGBA")
    bg.alpha_composite(Image.new("RGBA", SLIDE_SIZE, (*p.dark, 170)))
    img = bg
    accent = p.accent_on(p.dark, 4.5)
    d = ImageDraw.Draw(img)
    y = M + 40
    bookmark_icon(d, M, y, 54, accent)
    d.text((M + 62, y + 27), i18n.t(kit.language, "save_this"), font=fonts.load(kit.font("extrabold"), 34), fill=(*accent, 255),
           anchor="lm")
    y += 110
    cta_block = fonts.fit(kit.cta or i18n.t(kit.language, "follow_for_more"), kit.font("bold"), w - 2 * M - 80, 160, 38, 28,
                          leading=1.25, max_lines=3)
    cta_h = cta_block.height + 64
    cta_top = h - 130 - cta_h
    head = fonts.fit(text.headline, kit.font("extrabold"), w - 2 * M, int((cta_top - y) * 0.45), 100, 48,
                     leading=1.08, max_lines=4)
    gap = 34
    body = None
    if text.body:
        body = fonts.fit(text.body, kit.font("regular"), w - 2 * M, cta_top - y - head.height - gap - 60, 48, 28,
                         leading=1.36)
    content_h = head.height + (gap + body.height if body else 0)
    y += max(0, (cta_top - 60 - y - content_h) // 2)  # centre the text between the label and the CTA
    y = fonts.draw_block(img, head, (M, y), (*p.light, 255)) + gap
    if body:
        fonts.draw_block(img, body, (M, y), (*mix(p.light, p.dark, 0.15), 255))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((M, cta_top, w - M, cta_top + cta_h), radius=28, fill=(*accent, 255))
    ink = p.dark if contrast_ok(accent, p.dark) else p.light
    fonts.draw_block(img, cta_block, (M + 40, cta_top + 32), (*ink, 255), align="center", box_width=w - 2 * M - 80)
    footer(img, kit, counter, True)
    return img.convert("RGB")


def contrast_ok(a: RGB, b: RGB) -> bool:
    from .util import contrast
    return contrast(a, b) >= 4.5


def _arrow(d: ImageDraw.ImageDraw, x: int, y: int, length: int, color: RGB) -> None:
    d.line((x, y, x + length, y), fill=(*color, 255), width=5)
    d.line((x + length - 14, y - 12, x + length, y), fill=(*color, 255), width=5)
    d.line((x + length - 14, y + 12, x + length, y), fill=(*color, 255), width=5)


# ---------------------------------------------------------------- entry points
def render_carousel(kit: SlideKit, arts: list[Path], texts: list[SlideText], out_dir: Path) -> list[Path]:
    """One slide per text; returns the slide paths in order."""
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(texts)
    paths = []
    for i, (art_path, text) in enumerate(zip(arts, texts)):
        art = Image.open(art_path)
        counter = f"{i + 1}/{n}" if n > 1 else ""
        if i == 0:
            slide = hook_slide(kit, art, text, counter, swipe=n > 1)
        elif i == n - 1:
            slide = cta_slide(kit, art, text, counter)
        else:
            slide = inner_slide(kit, art, text, counter)
        path = out_dir / f"slide-{i + 1:02d}.png"
        save_png_and_jpeg(slide, path)
        paths.append(path)
    return paths
