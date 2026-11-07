"""Drawing primitives for the brand kit: palette roles, fonts, the logo mark
and a small set of line icons, all made with Pillow only.

Everything is drawn at 2-4x and downsampled so edges stay smooth.
"""
from __future__ import annotations

import colorsys
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

RGB = tuple[int, int, int]

FONT_DIRS = [Path("/usr/share/fonts/opentype/inter"), Path("/usr/share/fonts/truetype/inter")]
DEJAVU = {False: Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
          True: Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")}
STOP_WORDS = {"the", "a", "an", "of", "and", "&", "for", "to", "in", "on", "with", "made"}


# ---------------------------------------------------------------- colours
def hex_to_rgb(value: str) -> RGB:
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", v):
        raise ValueError(f"Not a hex colour: {value!r}")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def rgb_to_hex(c: RGB) -> str:
    return "#{:02x}{:02x}{:02x}".format(*c[:3])


def luminance(c: RGB) -> float:
    def ch(x: int) -> float:
        x = x / 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = c[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: RGB, b: RGB) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a: RGB, b: RGB, t: float) -> RGB:
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))  # type: ignore[return-value]


def saturation(c: RGB) -> float:
    return colorsys.rgb_to_hls(*(x / 255 for x in c))[2]


@dataclass
class Palette:
    """Brand colours sorted into roles: `dark` background/ink, `light` paper,
    `accent` the most saturated colour, `accent2` the next one."""
    dark: RGB
    light: RGB
    accent: RGB
    accent2: RGB
    source: list[str]

    @classmethod
    def from_hex(cls, colours: list[str]) -> "Palette":
        rgbs = [hex_to_rgb(c) for c in colours if c] or [hex_to_rgb("#0f172a"), hex_to_rgb("#f8fafc")]
        by_lum = sorted(rgbs, key=luminance)
        dark, light = by_lum[0], by_lum[-1]
        if contrast(dark, light) < 4.5:
            dark, light = mix(dark, (0, 0, 0), 0.7), mix(light, (255, 255, 255), 0.8)
        rest = sorted([c for c in rgbs if c not in (dark, light)], key=saturation, reverse=True)
        accent = rest[0] if rest else mix(dark, light, 0.5)
        accent2 = rest[1] if len(rest) > 1 else mix(accent, light, 0.45)
        return cls(dark, light, accent, accent2, [c if c.startswith("#") else f"#{c}" for c in colours])

    def ink_on(self, bg: RGB) -> RGB:
        """Dark or light, whichever reads better on `bg`."""
        return self.dark if contrast(self.dark, bg) >= contrast(self.light, bg) else self.light

    def roles(self) -> list[tuple[str, RGB, str]]:
        return [("Ink / background", self.dark, "Backgrounds, body text on light"),
                ("Paper", self.light, "Text on dark, light backgrounds"),
                ("Primary accent", self.accent, "Logo, buttons, highlights"),
                ("Secondary accent", self.accent2, "Small details, tags, emphasis")]


# ---------------------------------------------------------------- fonts
@lru_cache(maxsize=32)
def font_file(weight: str = "Bold", display: bool = True) -> str:
    """Inter (Display) at the given weight, falling back to DejaVu Sans."""
    names = ([f"InterDisplay-{weight}.otf"] if display else []) + [f"Inter-{weight}.otf"]
    for d in FONT_DIRS:
        for name in names:
            if (d / name).exists():
                return str(d / name)
    bold = weight.lower() in {"semibold", "bold", "extrabold", "black"}
    if DEJAVU[bold].exists():
        return str(DEJAVU[bold])
    return str(ImageFont.load_default().path) if hasattr(ImageFont.load_default(), "path") else ""


@lru_cache(maxsize=128)
def font(size: int, weight: str = "Bold", display: bool = True) -> ImageFont.FreeTypeFont:
    path = font_file(weight, display)
    if not path:
        raise FileNotFoundError("No usable font: install fonts-inter or fonts-dejavu")
    return ImageFont.truetype(path, size)


def font_family_name() -> str:
    try:
        return font(20, "Regular", display=False).getname()[0]
    except OSError:
        return "DejaVu Sans"


def fit_font(text: str, max_width: int, max_size: int, min_size: int = 14, weight: str = "Bold",
             display: bool = True) -> ImageFont.FreeTypeFont:
    size = max_size
    while size > min_size and font(size, weight, display).getlength(text) > max_width:
        size -= 2
    return font(size, weight, display)


def wrap(text: str, f: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if f.getlength(trial) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return [l for l in lines if l] or [""]


def text_center(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, f, fill) -> None:
    """Draw text optically centred on xy (uses the ink bbox, not the advance box)."""
    l, t, r, b = draw.textbbox((0, 0), text, font=f)
    draw.text((xy[0] - (l + r) / 2, xy[1] - (t + b) / 2), text, font=f, fill=fill)


# ---------------------------------------------------------------- identity
def initials(name: str, max_letters: int = 2) -> str:
    words = [w for w in re.findall(r"[A-Za-z0-9]+", name)]
    key = [w for w in words if w.lower() not in STOP_WORDS] or words or ["X"]
    if len(key) == 1:
        return key[0][:max_letters].upper() if max_letters > 1 and len(key[0]) > 1 else key[0][0].upper()
    picks = [key[0], key[-1]] if max_letters == 2 else key[:max_letters]
    return "".join(w[0] for w in picks).upper()


def logo_mark(size: int, pal: Palette, letters: str, *, background: RGB | None = None,
              ring: bool = True) -> Image.Image:
    """The brand's mark: a filled accent disc with bold initials, a partial ring
    in the second accent and a small dot. Content stays inside the inscribed
    circle so it survives circular crops. Transparent outside the disc when
    `background` is None."""
    s = size * (4 if size <= 400 else 2)  # supersample; 2x is plenty for large marks
    img = Image.new("RGBA", (s, s), (*background, 255) if background else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2
    disc_r = s * (0.40 if ring else 0.5)
    if background is not None:
        _soft_glow(img, (c, c), disc_r * 1.25, pal.accent, 70)
        d = ImageDraw.Draw(img)
    d.ellipse([c - disc_r, c - disc_r, c + disc_r, c + disc_r], fill=pal.accent)
    # subtle inner highlight (top-left) for depth
    hl = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([c - disc_r * 0.95, c - disc_r * 0.98, c + disc_r * 0.55, c + disc_r * 0.35],
                               fill=(255, 255, 255, 28))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse([c - disc_r, c - disc_r, c + disc_r, c + disc_r], fill=255)
    hl = hl.filter(ImageFilter.GaussianBlur(s * 0.02))
    hl.putalpha(ImageChops.multiply(hl.split()[3], mask))
    img.alpha_composite(hl)
    d = ImageDraw.Draw(img)
    if ring:
        rr, w = s * 0.465, int(s * 0.03)
        d.arc([c - rr, c - rr, c + rr, c + rr], start=-200, end=30, fill=pal.accent2, width=w)
        dot = s * 0.035
        # dot at the open end of the arc (angle 70 deg below the x axis -> -40 deg in PIL terms)
        ang = math.radians(55)
        dx, dy = c + rr * math.cos(ang), c + rr * math.sin(ang)
        d.ellipse([dx - dot, dy - dot, dx + dot, dy + dot], fill=pal.accent2)
    ink = pal.ink_on(pal.accent)
    f = fit_font(letters, int(disc_r * 1.3), int(disc_r * (0.95 if len(letters) <= 2 else 0.7)), weight="Black")
    text_center(d, (c, c + s * 0.005), letters, f, ink)
    return img.resize((size, size), Image.LANCZOS)


def _soft_glow(img: Image.Image, centre: tuple[float, float], radius: float, colour: RGB, alpha: int) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    x, y = centre
    ImageDraw.Draw(layer).ellipse([x - radius, y - radius, x + radius, y + radius], fill=(*colour, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.35))
    img.alpha_composite(layer)


def gradient(size: tuple[int, int], a: RGB, b: RGB, vertical: bool = False) -> Image.Image:
    """Diagonal (or vertical) two-stop gradient, drawn small and upscaled."""
    w, h = size
    small = Image.new("RGB", (64, 64))
    px = small.load()
    for y in range(64):
        for x in range(64):
            t = y / 63 if vertical else (x + y) / 126
            px[x, y] = mix(a, b, t)
    return small.resize((w, h), Image.BICUBIC)


# ---------------------------------------------------------------- icons
ICON_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("coin", ("budget", "money", "saving", "cash", "spend", "price", "cost",
              "presupuesto", "dinero", "ahorr", "gasto", "precio", "costo")),
    ("chart", ("invest", "index", "stock", "growth", "retire", "fund", "market", "data",
               "inversi", "invertir", "acciones", "jubila", "retiro", "fondo", "mercado")),
    ("card", ("credit", "debt", "loan", "card", "bank", "payoff",
              "crédito", "credito", "deuda", "préstamo", "prestamo", "tarjeta", "banco")),
    ("phone", ("app", "tool", "tech", "software", "phone", "compare", "review",
               "herramienta", "celular", "compar")),
    ("bulb", ("invent", "idea", "tip", "hack", "learn", "trick", "science")),
    ("hourglass", ("history", "origin", "old", "time", "ancient", "story", "past")),
    ("scales", ("law", "custom", "rule", "legal", "right", "ethic")),
    ("book", ("guide", "basics", "beginner", "read", "lesson", "explain", "101")),
    ("heart", ("health", "habit", "life", "love", "wellness", "fitness")),
    ("leaf", ("food", "plant", "nature", "green", "eco", "garden")),
]
FILLER_ICONS = [("star", "Start here"), ("gift", "Freebies"), ("chat", "FAQ"), ("play", "Videos"),
                ("book", "Guides")]


def pick_icon(label: str, used: set[str]) -> str:
    low = label.lower()
    for name, words in ICON_KEYWORDS:
        if name not in used and any(w in low for w in words):
            return name
    for name, _ in ICON_KEYWORDS + [(n, ()) for n, _ in FILLER_ICONS]:
        if name not in used:
            return name
    return "star"


def draw_icon(name: str, size: int, colour: RGB, bg: RGB) -> Image.Image:
    """A simple bold line icon on a transparent square (size px)."""
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = int(s * 0.06)
    getattr(_Icons, name, _Icons.star)(d, s, w, colour, bg)
    return img.resize((size, size), Image.LANCZOS)


class _Icons:
    """Each method draws into an s*s canvas with stroke width w."""

    @staticmethod
    def coin(d, s, w, c, bg):
        d.ellipse([s * .34, s * .10, s * .90, s * .66], outline=c, width=w)
        d.ellipse([s * .10, s * .34, s * .66, s * .90], fill=bg, outline=c, width=w)
        f = font(int(s * .36), "Black")
        text_center(d, (s * .38, s * .62), "$", f, c)

    @staticmethod
    def chart(d, s, w, c, bg):
        base = s * .84
        for i, h in enumerate((.30, .46, .64)):
            x = s * (.18 + i * .24)
            d.rounded_rectangle([x, base - s * h, x + s * .16, base], radius=w // 2, fill=c)
        d.line([s * .14, s * .44, s * .38, s * .30, s * .56, s * .36, s * .84, s * .12], fill=c, width=w,
               joint="curve")
        d.polygon([(s * .86, s * .08), (s * .86, s * .24), (s * .72, s * .12)], fill=c)

    @staticmethod
    def card(d, s, w, c, bg):
        d.rounded_rectangle([s * .10, s * .24, s * .90, s * .76], radius=s * .07, outline=c, width=w)
        d.rectangle([s * .10, s * .36, s * .90, s * .46], fill=c)
        d.rounded_rectangle([s * .20, s * .58, s * .40, s * .66], radius=w // 3, fill=c)
        d.rounded_rectangle([s * .48, s * .58, s * .60, s * .66], radius=w // 3, fill=c)

    @staticmethod
    def phone(d, s, w, c, bg):
        d.rounded_rectangle([s * .28, s * .10, s * .72, s * .90], radius=s * .08, outline=c, width=w)
        d.line([s * .43, s * .19, s * .57, s * .19], fill=c, width=w)
        for i in range(2):
            for j in range(2):
                x, y = s * (.37 + i * .15), s * (.34 + j * .17)
                d.rounded_rectangle([x, y, x + s * .11, y + s * .11], radius=w // 2, fill=c)
        d.ellipse([s * .46, s * .74, s * .54, s * .82], fill=c)

    @staticmethod
    def bulb(d, s, w, c, bg):
        d.ellipse([s * .24, s * .08, s * .76, s * .60], outline=c, width=w)
        d.rectangle([s * .38, s * .54, s * .62, s * .66], fill=bg)
        d.line([s * .38, s * .52, s * .38, s * .70], fill=c, width=w)
        d.line([s * .62, s * .52, s * .62, s * .70], fill=c, width=w)
        d.line([s * .36, s * .76, s * .64, s * .76], fill=c, width=w)
        d.line([s * .40, s * .86, s * .60, s * .86], fill=c, width=w)
        d.line([s * .44, s * .30, s * .50, s * .42, s * .56, s * .30], fill=c, width=int(w * .7))

    @staticmethod
    def hourglass(d, s, w, c, bg):
        d.line([s * .22, s * .10, s * .78, s * .10], fill=c, width=w)
        d.line([s * .22, s * .90, s * .78, s * .90], fill=c, width=w)
        d.line([s * .30, s * .12, s * .30, s * .26, s * .50, s * .50, s * .30, s * .74, s * .30, s * .88],
               fill=c, width=w, joint="curve")
        d.line([s * .70, s * .12, s * .70, s * .26, s * .50, s * .50, s * .70, s * .74, s * .70, s * .88],
               fill=c, width=w, joint="curve")
        d.polygon([(s * .36, s * .84), (s * .64, s * .84), (s * .50, s * .66)], fill=c)
        d.polygon([(s * .40, s * .30), (s * .60, s * .30), (s * .50, s * .42)], fill=c)

    @staticmethod
    def scales(d, s, w, c, bg):
        d.line([s * .50, s * .12, s * .50, s * .84], fill=c, width=w)
        d.line([s * .16, s * .26, s * .84, s * .26], fill=c, width=w)
        d.line([s * .30, s * .86, s * .70, s * .86], fill=c, width=w)
        for x in (.24, .76):
            d.line([s * x, s * .28, s * (x - .12), s * .56], fill=c, width=int(w * .6))
            d.line([s * x, s * .28, s * (x + .12), s * .56], fill=c, width=int(w * .6))
            d.chord([s * (x - .15), s * .44, s * (x + .15), s * .68], 0, 180, fill=c)

    @staticmethod
    def book(d, s, w, c, bg):
        d.line([s * .50, s * .26, s * .50, s * .84], fill=c, width=w)
        d.line([s * .50, s * .26, s * .30, s * .18, s * .10, s * .22, s * .10, s * .78, s * .30, s * .74,
                s * .50, s * .84], fill=c, width=w, joint="curve")
        d.line([s * .50, s * .26, s * .70, s * .18, s * .90, s * .22, s * .90, s * .78, s * .70, s * .74,
                s * .50, s * .84], fill=c, width=w, joint="curve")

    @staticmethod
    def heart(d, s, w, c, bg):
        d.ellipse([s * .12, s * .18, s * .52, s * .58], fill=c)
        d.ellipse([s * .48, s * .18, s * .88, s * .58], fill=c)
        d.polygon([(s * .135, s * .45), (s * .865, s * .45), (s * .50, s * .86)], fill=c)

    @staticmethod
    def leaf(d, s, w, c, bg):
        d.chord([s * .10, s * .10, s * .90, s * .90], 180, 270, fill=c)
        d.chord([s * .10, s * .10, s * .90, s * .90], 0, 90, fill=c)
        d.polygon([(s * .10, s * .50), (s * .50, s * .10), (s * .90, s * .50), (s * .50, s * .90)], fill=c)
        d.line([s * .24, s * .76, s * .70, s * .30], fill=bg, width=int(w * .7))

    @staticmethod
    def star(d, s, w, c, bg):
        pts = []
        for i in range(10):
            r = s * (.42 if i % 2 == 0 else .18)
            a = math.radians(-90 + i * 36)
            pts.append((s * .5 + r * math.cos(a), s * .52 + r * math.sin(a)))
        d.polygon(pts, fill=c)

    @staticmethod
    def gift(d, s, w, c, bg):
        d.rounded_rectangle([s * .14, s * .32, s * .86, s * .48], radius=w // 2, fill=c)
        d.rounded_rectangle([s * .20, s * .48, s * .80, s * .88], radius=w // 2, outline=c, width=w)
        d.rectangle([s * .45, s * .32, s * .55, s * .88], fill=c)
        d.ellipse([s * .26, s * .12, s * .50, s * .32], outline=c, width=w)
        d.ellipse([s * .50, s * .12, s * .74, s * .32], outline=c, width=w)

    @staticmethod
    def chat(d, s, w, c, bg):
        d.rounded_rectangle([s * .10, s * .16, s * .90, s * .70], radius=s * .14, fill=c)
        d.polygon([(s * .24, s * .66), (s * .44, s * .68), (s * .22, s * .88)], fill=c)
        for x in (.32, .50, .68):
            d.ellipse([s * (x - .05), s * .38, s * (x + .05), s * .48], fill=bg)

    @staticmethod
    def play(d, s, w, c, bg):
        d.rounded_rectangle([s * .08, s * .20, s * .92, s * .80], radius=s * .14, fill=c)
        d.polygon([(s * .42, s * .36), (s * .42, s * .64), (s * .66, s * .50)], fill=bg)
