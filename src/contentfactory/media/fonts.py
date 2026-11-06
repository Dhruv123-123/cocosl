"""Font discovery and text layout for Pillow-rendered graphics.

Uses fonts already installed on the system (fontconfig), preferring the
brand's font family, then Inter, then DejaVu Sans. Nothing is bundled.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WEIGHTS = {"regular": 400, "medium": 500, "semibold": 600, "bold": 700, "extrabold": 800, "black": 900}
_STYLE_NAMES = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
_KNOWN_DIRS = [Path("/usr/share/fonts/opentype/inter"), Path("/usr/share/fonts/truetype/inter")]
_DEJAVU = {False: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
           True: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"}


@lru_cache(maxsize=64)
def font_path(family: str = "Inter", weight: str = "bold") -> str:
    """Absolute path of an installed font file for family+weight, with fallbacks."""
    w = WEIGHTS.get(weight, 700)
    for fam in dict.fromkeys([family, "Inter"]):
        found = _fc_match(fam, _STYLE_NAMES[w])
        if found:
            return found
        for d in _KNOWN_DIRS:
            p = d / f"{fam.replace(' ', '')}-{_STYLE_NAMES[w]}.otf"
            if p.exists():
                return str(p)
    path = _DEJAVU[w >= 600]
    if Path(path).exists():
        return path
    raise FileNotFoundError("No usable font found (install fonts-inter or fonts-dejavu)")


def _fc_match(family: str, style: str) -> str | None:
    if not shutil.which("fc-match"):
        return None
    try:
        out = subprocess.run(["fc-match", "-f", "%{family}\t%{style}\t%{file}", f"{family}:style={style}"],
                             capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    fams, styles, path = (out.split("\t") + ["", "", ""])[:3]
    fam_ok = family.lower() in [f.strip().lower() for f in fams.split(",")]
    style_ok = style.lower() in [s.strip().lower() for s in styles.split(",")]
    return path if fam_ok and style_ok and Path(path).exists() else None


def family_name(path: str) -> str:
    """Family name for libass ('Inter', 'DejaVu Sans')."""
    try:
        return ImageFont.truetype(path, 10).getname()[0]
    except OSError:
        return "DejaVu Sans"


@lru_cache(maxsize=256)
def load(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- layout
@dataclass
class TextBlock:
    font: ImageFont.FreeTypeFont
    lines: list[str]
    line_height: int

    @property
    def height(self) -> int:
        return self.line_height * len(self.lines)

    def width(self) -> int:
        return max((int(self.font.getlength(l)) for l in self.lines), default=0)


def wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Greedy word wrap; over-long single words are broken by characters."""
    lines: list[str] = []
    for para in (text or "").split("\n"):
        line = ""
        for word in para.split():
            while font.getlength(word) > max_width and len(word) > 1:
                cut = max(1, next((i for i in range(len(word), 0, -1)
                                   if font.getlength(word[:i] + "-") <= max_width), 1))
                if line:
                    lines.append(line)
                    line = ""
                lines.append(word[:cut] + "-")
                word = word[cut:]
            trial = f"{line} {word}".strip()
            if font.getlength(trial) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return _balance_orphan(lines, font, max_width)


def _balance_orphan(lines: list[str], font, max_width: int) -> list[str]:
    """Avoid a lone last word when the previous line can spare one."""
    if len(lines) >= 2 and " " not in lines[-1] and " " in lines[-2]:
        head, last = lines[-2].rsplit(" ", 1)
        moved = f"{last} {lines[-1]}"
        if font.getlength(moved) <= max_width:
            lines[-2:] = [head, moved]
    return lines


def fit(text: str, path: str, max_width: int, max_height: int, max_size: int, min_size: int = 18,
        leading: float = 1.15, max_lines: int | None = None) -> TextBlock:
    """Largest font size (stepping down) whose wrapped text fits the box."""
    size = max_size
    while True:
        font = load(path, size)
        lines = wrap(text, font, max_width)
        lh = int(size * leading)
        words_fit = all(font.getlength(wd) <= max_width for wd in (text or "").split())
        ok = words_fit and lh * len(lines) <= max_height and (max_lines is None or len(lines) <= max_lines)
        if ok or size <= min_size:
            if not ok:
                lines = _truncate(lines, font, max_width, max(1, min(max_lines or 99, max_height // lh)))
            return TextBlock(font, lines, lh)
        size = max(min_size, int(size * 0.93))


def _truncate(lines: list[str], font, max_width: int, n: int) -> list[str]:
    if len(lines) <= n:
        return lines
    out = lines[:n]
    last = out[-1]
    while last and font.getlength(last + "…") > max_width:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    out[-1] = last.rstrip(",.;:") + "…"
    return out


def draw_block(img: Image.Image, block: TextBlock, xy: tuple[int, int], fill, *, align: str = "left",
               box_width: int | None = None, shadow: tuple[int, int, int, int] | None = None,
               shadow_radius: int = 10, stroke: int = 0, stroke_fill=None) -> int:
    """Draw a TextBlock at xy (top-left of the box). Returns the bottom y."""
    x0, y = xy
    if shadow:
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        _draw_lines(ImageDraw.Draw(layer), block, x0, y + max(2, shadow_radius // 3), shadow, align, box_width,
                    stroke, shadow)
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(shadow_radius)))
    _draw_lines(ImageDraw.Draw(img), block, x0, y, fill, align, box_width, stroke, stroke_fill)
    return y + block.height


def _draw_lines(draw, block: TextBlock, x0: int, y: int, fill, align: str, box_width: int | None,
                stroke: int, stroke_fill) -> None:
    # Use the cap-height offset so the first line sits exactly at y.
    top_pad = block.font.getbbox("H")[1]
    for line in block.lines:
        w = block.font.getlength(line)
        x = x0
        if align == "center" and box_width:
            x = x0 + (box_width - w) / 2
        elif align == "right" and box_width:
            x = x0 + box_width - w
        draw.text((x, y - top_pad), line, font=block.font, fill=fill,
                  stroke_width=stroke, stroke_fill=stroke_fill)
        y += block.line_height
