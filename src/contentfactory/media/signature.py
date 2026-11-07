"""A brand's signature visual: one recognisable graphic device, the same on every thumbnail,
video intro and carousel cover.

The variety rules (media/looks.py) change layout, motion, captions and headlines from video to
video so a channel doesn't look mass-produced. The signature is the one thing that does NOT
change: it's how a viewer scrolling past knows it's this brand. No mascot, no faces, no logos
of anyone else: just a shape in the brand's colour.

Brand YAML (all optional; `device: auto` picks one from the slug so every brand has one):

    visual:
      signature:
        device: corner_block   # corner_block | stripe | ring | bracket | dot_grid | none | auto
        color: accent          # accent | accent2 | light | dark | "#ff8a00"
        corner: top-right      # top-left | top-right | bottom-left | bottom-right
        size: 0.14             # fraction of the short side
        label: "MMS"           # optional, short text on corner_block
        where: [thumbnail, intro, cover]
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from . import fonts
from .util import Palette, hex_to_rgb, save_png_and_jpeg

DEVICES = ("corner_block", "stripe", "ring", "bracket", "dot_grid")


def resolve(brand) -> dict | None:
    """The brand's signature as a plain dict, or None when it's switched off."""
    sig = getattr(brand.visual, "signature", None)
    data = sig.model_dump() if sig is not None else {}
    device = data.get("device") or "auto"
    if device == "none":
        return None
    if device == "auto":
        device = DEVICES[sum(map(ord, brand.slug)) % len(DEVICES)]
    return {"device": device, "color": data.get("color") or "accent", "corner": data.get("corner") or "top-right",
            "size": float(data.get("size") or 0.14), "label": data.get("label") or "",
            "where": list(data.get("where") or ["thumbnail", "intro", "cover"])}


def _color(sig: dict, palette: Palette) -> tuple:
    c = sig["color"]
    if c.startswith("#"):
        return hex_to_rgb(c)
    if c == "accent2" and len(palette.accents) > 1:
        return palette.accents[1]
    return {"light": palette.light, "dark": palette.dark}.get(c, palette.accent)


def draw(img: Image.Image, sig: dict, palette: Palette, family: str = "Inter") -> Image.Image:
    """Draw the device onto a copy of `img` and return it (RGBA)."""
    img = img.convert("RGBA")
    w, h = img.size
    s = int(min(w, h) * max(0.04, min(sig["size"], 0.4)))
    col = (*_color(sig, palette), 255)
    right, bottom = "right" in sig["corner"], "bottom" in sig["corner"]
    inset = int(min(w, h) * 0.045)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0 = w - inset - s if right else inset
    y0 = h - inset - s if bottom else inset
    dev = sig["device"]
    if dev == "corner_block":
        # a solid block flush with the edge, with a notch: reads as a "tab" of brand colour
        bx0, bx1 = (w - s, w) if right else (0, s)
        by0, by1 = (h - int(s * 0.62), h) if bottom else (0, int(s * 0.62))
        d.rectangle((bx0, by0, bx1, by1), fill=col)
        if sig["label"]:
            f = fonts.load(fonts.font_path(family, "black"), max(14, int(s * 0.24)))
            d.text(((bx0 + bx1) // 2, (by0 + by1) // 2), sig["label"][:6].upper(), font=f,
                   fill=(*palette.dark, 255), anchor="mm")
    elif dev == "stripe":
        bw = max(8, int(w * 0.03))
        bx = w - bw if right else 0
        d.rectangle((bx, 0, bx + bw, h), fill=col)
        d.rectangle((bx - bw // 2 if right else bw + bw // 3, 0, (bx - bw // 3) if right else bw + bw // 2 + bw // 3, h),
                    fill=(*col[:3], 140))
    elif dev == "ring":
        r = s
        cx = w - inset if right else inset
        cy = h - inset if bottom else inset
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=max(6, s // 6))
    elif dev == "bracket":
        t = max(6, s // 9)
        # two corner brackets: the chosen corner and the opposite one
        for c_right, c_bottom in ((right, bottom), (not right, not bottom)):
            ex = w - inset if c_right else inset
            ey = h - inset if c_bottom else inset
            dx = -s if c_right else s
            dy = -s if c_bottom else s
            d.rectangle(sorted_box(ex, ey, ex + dx, ey + (t if not c_bottom else -t)), fill=col)
            d.rectangle(sorted_box(ex, ey, ex + (t if not c_right else -t), ey + dy), fill=col)
    elif dev == "dot_grid":
        n, gap = 4, s / 4
        rr = max(3, int(gap * 0.22))
        for i in range(n):
            for j in range(n):
                cx, cy = x0 + gap * (i + 0.5), y0 + gap * (j + 0.5)
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col)
    img.alpha_composite(layer)
    return img


def sorted_box(x0, y0, x1, y1):
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def stamp(path: Path, sig: dict | None, palette: Palette, family: str = "Inter", out: Path | None = None) -> Path:
    """Draw the signature onto an image file (in place, or to `out`); keeps the JPEG twin in sync."""
    if not sig:
        return path
    out = out or path
    img = draw(Image.open(path), sig, palette, family)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() == ".png":
        save_png_and_jpeg(img, out)
    else:
        img.convert("RGB").save(out)
    return out
