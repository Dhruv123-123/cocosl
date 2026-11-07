"""Offline "cards" artwork: deterministic abstract compositions in the brand
palette, made with Pillow only. Same prompt -> same picture.

Four styles (orbit, bauhaus, waves, grid) share a look within one post (the
style is picked from the post, the details from each prompt), so an offline
render reads as a designed series rather than placeholders.
"""
from __future__ import annotations

import colorsys
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .util import RGB, Palette, mix, seed_of, shade

STYLES = ["orbit", "bauhaus", "waves", "grid"]


def abstract_art(palette: Palette, size: tuple[int, int], prompt: str, family: str = "") -> Image.Image:
    """Render one artwork. `family` (e.g. the post title) fixes the style."""
    rng = random.Random(seed_of(prompt, family))
    # Style comes from the post (cohesion), alternating between two neighbours per image (variety).
    style = STYLES[(seed_of(family or prompt) + seed_of(prompt) % 2) % len(STYLES)]
    w, h = size
    sw, sh = max(64, int(w * 1.5)), max(64, int(h * 1.5))  # supersample: Pillow shapes have no anti-aliasing
    colors = _scheme(palette, rng)
    img = _gradient((sw, sh), colors["bg_a"], colors["bg_b"], rng.uniform(0, math.tau))
    img = Image.alpha_composite(img.convert("RGBA"), _blobs((sw, sh), colors, rng))
    img = Image.alpha_composite(img, globals()[f"_{style}"]((sw, sh), colors, rng))
    img = img.convert("RGB").resize((w, h), Image.LANCZOS)
    img = _vignette(img, 0.38)
    return _grain(img, rng.randrange(1 << 30), strength=0.06)


def _scheme(p: Palette, rng: random.Random) -> dict[str, RGB]:
    accents = p.accents[:] or [shade(p.dark, 0.5, 2)]
    tint = min(accents, key=lambda a: _hue_gap(a, p.dark))  # background tint that agrees with the dark
    rng.shuffle(accents)
    a1 = accents[0]
    a2 = accents[1] if len(accents) > 1 else shade(a1, 0.65)
    return {
        "bg_a": p.dark,
        "bg_b": mix(p.dark, shade(tint, 0.2), 0.8),
        "a1": a1, "a2": a2,
        "deep": mix(p.dark, tint, 0.35),
        "light": p.light,
    }


def _hue_gap(a: RGB, b: RGB) -> float:
    ha = colorsys.rgb_to_hls(*(x / 255 for x in a))[0]
    hb = colorsys.rgb_to_hls(*(x / 255 for x in b))[0]
    return min(abs(ha - hb), 1 - abs(ha - hb))


def _gradient(size: tuple[int, int], a: RGB, b: RGB, angle: float) -> Image.Image:
    w, h = size
    diag = int(math.hypot(w, h)) + 2
    ramp = Image.linear_gradient("L").resize((diag, diag)).rotate(math.degrees(angle), resample=Image.BICUBIC)
    left, top = (diag - w) // 2, (diag - h) // 2
    mask = ramp.crop((left, top, left + w, top + h))
    return Image.composite(Image.new("RGB", size, b), Image.new("RGB", size, a), mask)


def _blobs(size: tuple[int, int], c: dict, rng: random.Random) -> Image.Image:
    w, h = size
    small = (max(16, w // 4), max(16, h // 4))
    layer = Image.new("RGBA", small, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(rng.randint(3, 5)):
        col = [c["a1"], c["a2"], c["deep"], c["a1"]][i % 4]
        r = rng.uniform(0.25, 0.55) * max(small)
        x, y = rng.uniform(0, small[0]), rng.uniform(0, small[1])
        d.ellipse((x - r, y - r * rng.uniform(0.6, 1.2), x + r, y + r), fill=(*col, rng.randint(60, 120)))
    layer = layer.filter(ImageFilter.GaussianBlur(max(small) * 0.12))
    return layer.resize(size, Image.BICUBIC)


def _orbit(size, c, rng) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = rng.uniform(0.25, 0.75) * w, rng.uniform(0.25, 0.6) * h
    base = min(w, h)
    sun = base * rng.uniform(0.16, 0.24)
    for k in range(7):  # concentric rings
        r = sun * (1.5 + k * 0.55)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*c["light"], max(14, 70 - k * 8)),
                  width=max(1, base // 260))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - sun * 1.6, cy - sun * 1.6, cx + sun * 1.6, cy + sun * 1.6),
                                 fill=(*c["a1"], 110))
    layer = Image.alpha_composite(layer, glow.filter(ImageFilter.GaussianBlur(sun * 0.5)))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - sun, cy - sun, cx + sun, cy + sun), fill=(*c["a1"], 255))
    for k in range(3):  # small moons on the rings
        r = sun * (1.5 + rng.randint(1, 6) * 0.55)
        t = rng.uniform(0, math.tau)
        mr = base * rng.uniform(0.018, 0.04)
        mx, my = cx + r * math.cos(t), cy + r * math.sin(t)
        d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=(*(c["a2"] if k else c["light"]), 255))
    return layer


def _bauhaus(size, c, rng) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cols, rows = 3, max(3, round(3 * h / w))
    cw, ch = w / cols, h / rows
    fills = [c["a1"], c["a2"], c["light"], c["deep"]]
    cells = [(i, j) for i in range(cols) for j in range(rows)]
    rng.shuffle(cells)
    big_i, big_j = rng.randrange(cols - 1), rng.randrange(rows - 1)
    r = min(cw, ch) * 0.95
    mx, my = (big_i + 1) * cw, (big_j + 1) * ch
    d.ellipse((mx - r, my - r, mx + r, my + r), fill=(*c["deep"], 255))
    d.pieslice((mx - r, my - r, mx + r, my + r), rng.choice([0, 90, 180, 270]), 0, fill=(*c["a1"], 255))
    cells = [(i, j) for i, j in cells if not (big_i <= i <= big_i + 1 and big_j <= j <= big_j + 1)]
    for n, (i, j) in enumerate(cells[: max(4, int(len(cells) * 0.6))]):
        x0, y0 = i * cw, j * ch
        x1, y1 = x0 + cw, y0 + ch
        col = fills[n % len(fills)]
        alpha = 235 if col != c["light"] else 200
        kind = rng.choice(["quarter", "half", "circle", "ring", "stripes"])
        pad = cw * 0.06
        if kind == "quarter":
            corner = rng.randrange(4)
            ox, oy = (x0, y0) if corner == 0 else (x1, y0) if corner == 1 else (x1, y1) if corner == 2 else (x0, y1)
            r = min(cw, ch) - pad
            d.pieslice((ox - r, oy - r, ox + r, oy + r), 90 * corner, 90 * corner + 90, fill=(*col, alpha))
        elif kind == "half":
            r = min(cw, ch) / 2 - pad
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            start = rng.choice([0, 90, 180, 270])
            d.pieslice((mx - r, my - r, mx + r, my + r), start, start + 180, fill=(*col, alpha))
        elif kind == "circle":
            r = min(cw, ch) / 2 - pad * 2
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            d.ellipse((mx - r, my - r, mx + r, my + r), fill=(*col, alpha))
        elif kind == "ring":
            r = min(cw, ch) / 2 - pad * 2
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            d.ellipse((mx - r, my - r, mx + r, my + r), outline=(*col, alpha), width=max(2, int(r * 0.22)))
        else:
            n_str = 5
            for k in range(n_str):
                yy = y0 + pad + k * (ch - 2 * pad) / n_str
                d.rectangle((x0 + pad, yy, x1 - pad, yy + (ch - 2 * pad) / (n_str * 2)), fill=(*col, alpha))
    return layer


def _waves(size, c, rng) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sun_r = min(w, h) * rng.uniform(0.12, 0.18)
    sx, sy = rng.uniform(0.25, 0.75) * w, h * rng.uniform(0.2, 0.32)
    d.ellipse((sx - sun_r, sy - sun_r, sx + sun_r, sy + sun_r), fill=(*c["a2"], 240))
    bands = 6
    for k in range(bands):
        t = k / (bands - 1)
        base_y = h * (0.42 + 0.5 * t)
        amp = h * rng.uniform(0.02, 0.05)
        freq = rng.uniform(1.0, 2.2)
        phase = rng.uniform(0, math.tau)
        pts = [(x, base_y + amp * math.sin(freq * math.tau * x / w + phase)
                + amp * 0.25 * math.sin(2.3 * freq * math.tau * x / w + phase * 2)) for x in range(0, w + 8, 8)]
        col = mix(c["a1"], c["bg_a"], t * 0.85)
        d.polygon([*pts, (w, h), (0, h)], fill=(*col, 255))
    return layer


def _grid(size, c, rng) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    step = max(12, min(w, h) // 14)
    dot = max(1, step // 10)
    for x in range(step // 2, w, step):
        for y in range(step // 2, h, step):
            d.ellipse((x - dot, y - dot, x + dot, y + dot), fill=(*c["light"], 46))
    # a big arch
    aw = w * rng.uniform(0.45, 0.65)
    ax = rng.uniform(0.1, 0.9 - aw / w) * w
    ay = h * rng.uniform(0.3, 0.5)
    d.rounded_rectangle((ax, ay, ax + aw, h * 1.2), radius=int(aw / 2), fill=(*c["a1"], 235))
    inner = aw * 0.32
    d.rounded_rectangle((ax + inner, ay + inner, ax + aw - inner, h * 1.2), radius=int((aw - 2 * inner) / 2),
                        fill=(*c["deep"], 255))
    # diagonal stripes block
    bx, by = rng.uniform(0.05, 0.6) * w, rng.uniform(0.06, 0.2) * h
    bw, bh = w * 0.32, h * 0.12
    stripes = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripes)
    for k in range(-int(bh), int(bw), max(6, step // 3)):
        sd.line((bx + k, by + bh, bx + k + bh, by), fill=(*c["a2"], 220), width=max(2, step // 8))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((bx, by, bx + bw, by + bh), fill=255)
    layer.alpha_composite(Image.composite(stripes, Image.new("RGBA", size, (0, 0, 0, 0)), mask))
    return layer


def _vignette(img: Image.Image, strength: float) -> Image.Image:
    w, h = img.size
    radial = Image.radial_gradient("L").resize((int(w * 1.5), int(h * 1.5)))
    left, top = (radial.width - w) // 2, (radial.height - h) // 2
    mask = radial.crop((left, top, left + w, top + h)).point(lambda v: int(min(255, v * 1.1) * strength))
    return Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, mask)


def _grain(img: Image.Image, seed: int, strength: float) -> Image.Image:
    """Film grain from a seeded noise tile (deterministic, unlike effect_noise)."""
    rng = random.Random(seed)
    tile = Image.frombytes("L", (256, 256), rng.randbytes(256 * 256)).filter(ImageFilter.GaussianBlur(0.6))
    tile = tile.point(lambda v: int(128 + (v - 128) * 1.6))
    noise = Image.new("L", img.size)
    for x in range(0, img.width, 256):
        for y in range(0, img.height, 256):
            noise.paste(tile, (x, y))
    grained = ImageChops.overlay(img, Image.merge("RGB", (noise, noise, noise)))
    return Image.blend(img, grained, strength * 3)
