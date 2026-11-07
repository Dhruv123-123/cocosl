"""Data charts for money content: exact numbers drawn from the script, not an AI picture of a chart.

A segment can carry a `chart` (schemas.ChartSpec): bars or a line with labels and values.
`render_chart` draws it in the brand palette at the beat's size. With FACTORY_CHARTS=manim and
Manim installed (MIT), `render_chart_clip` also renders a short animated version (bars growing,
line drawing on) that the video uses in place of the still.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

from . import fonts
from .util import Palette


def _fmt(v: float, prefix: str, suffix: str) -> str:
    if abs(v) >= 1_000_000:
        s = f"{v / 1_000_000:.1f}M"
    elif abs(v) >= 10_000:
        s = f"{v / 1000:.0f}k"
    elif v == int(v):
        s = f"{int(v):,}"
    else:
        s = f"{v:,.2f}"
    return f"{prefix}{s}{suffix}"


def render_chart(spec, size: tuple[int, int], palette: Palette, family: str, out: Path) -> Path:
    w, h = size
    img = Image.new("RGB", size, palette.dark)
    d = ImageDraw.Draw(img)
    accent = palette.accent_on(palette.dark, 3.0)
    muted = tuple(int(c * 0.6 + d_ * 0.4) for c, d_ in zip(palette.light, palette.dark))
    m = int(min(w, h) * 0.08)
    title = fonts.fit(spec.title or " ", fonts.font_path(family, "black"), w - 2 * m, int(h * 0.16),
                      int(min(w, h) * 0.075), 28, leading=1.05, max_lines=2)
    fonts.draw_block(img, title, (m, m), (*palette.light, 255))
    top = m + title.height + int(h * 0.05)
    bottom = h - m - int(h * 0.07)
    left, right = m, w - m
    vals = [float(v) for v in spec.values] or [0.0]
    labels = list(spec.labels) + [""] * (len(vals) - len(spec.labels))
    vmax = max(max(vals), 1e-9)
    label_font = fonts.load(fonts.font_path(family, "bold"), max(18, int(min(w, h) * 0.032)))
    value_font = fonts.load(fonts.font_path(family, "black"), max(20, int(min(w, h) * 0.04)))
    d.line([(left, bottom), (right, bottom)], fill=muted, width=3)
    n = len(vals)
    if spec.kind == "line" and n > 1:
        pts = [(left + i * (right - left) / (n - 1), bottom - (v / vmax) * (bottom - top - 60)) for i, v in enumerate(vals)]
        d.line(pts, fill=accent, width=max(6, w // 160), joint="curve")
        for i, (x, y) in enumerate(pts):
            r = max(7, w // 140)
            d.ellipse([x - r, y - r, x + r, y + r], fill=accent)
            if i in (0, n - 1) or n <= 6:
                txt = _fmt(vals[i], spec.unit_prefix, spec.unit_suffix)
                tw = d.textlength(txt, font=value_font)
                d.text((min(max(x - tw / 2, left), right - tw), y - value_font.size - 14), txt, font=value_font,
                       fill=palette.light)
            if labels[i] and (n <= 8 or i % max(1, n // 6) == 0 or i == n - 1):
                tw = d.textlength(labels[i], font=label_font)
                d.text((min(max(x - tw / 2, left), right - tw), bottom + 12), labels[i], font=label_font, fill=muted)
    else:
        gap = (right - left) / n
        bw = gap * 0.62
        for i, v in enumerate(vals):
            x0 = left + i * gap + (gap - bw) / 2
            y0 = bottom - (v / vmax) * (bottom - top - 60)
            d.rounded_rectangle([x0, y0, x0 + bw, bottom - 2], radius=int(bw * 0.12),
                                fill=accent if i == n - 1 else palette.light)
            txt = _fmt(v, spec.unit_prefix, spec.unit_suffix)
            tw = d.textlength(txt, font=value_font)
            d.text((x0 + (bw - tw) / 2, y0 - value_font.size - 12), txt, font=value_font, fill=palette.light)
            lab = textwrap.shorten(labels[i], 18, placeholder="…")
            tw = d.textlength(lab, font=label_font)
            d.text((x0 + (bw - tw) / 2, bottom + 12), lab, font=label_font, fill=muted)
    if spec.note:
        note_font = fonts.load(fonts.font_path(family, "regular"), max(16, int(min(w, h) * 0.024)))
        d.text((m, h - m + 4 - note_font.size), textwrap.shorten(spec.note, 90, placeholder="…"), font=note_font,
               fill=muted)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


MANIM_SCENE = '''
from manim import *
SPEC = {spec!r}
class ChartScene(Scene):
    def construct(self):
        self.camera.background_color = "{bg}"
        vals, labels = SPEC["values"], SPEC["labels"]
        title = Text(SPEC["title"], color="{fg}", weight=BOLD).scale(0.7).to_edge(UP)
        self.play(FadeIn(title), run_time=0.4)
        ymax = max(vals) * 1.15 or 1
        ax = Axes(x_range=[0, len(vals) + 1, 1], y_range=[0, ymax, ymax / 4], x_length=10, y_length=5,
                  tips=False, axis_config={{"color": "{fg}", "include_ticks": False}}).shift(DOWN * 0.4)
        self.add(ax)
        if SPEC["kind"] == "line" and len(vals) > 1:
            g = ax.plot_line_graph(list(range(1, len(vals) + 1)), vals, line_color="{accent}",
                                   vertex_dot_style={{"fill_color": "{accent}"}})
            self.play(Create(g), run_time=SPEC.get("seconds", 3) - 0.6)
        else:
            bars = VGroup(*[Rectangle(width=0.6, height=max(0.01, v / ymax * 5), fill_color="{accent}",
                            fill_opacity=1, stroke_width=0).move_to(ax.c2p(i + 1, 0), aligned_edge=DOWN)
                            for i, v in enumerate(vals)])
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2),
                      run_time=SPEC.get("seconds", 3) - 0.6)
        last = Text(SPEC["last_label"], color="{accent}").scale(0.6).next_to(title, DOWN)
        self.play(FadeIn(last), run_time=0.2)
        self.wait(0.0001)
'''


def render_chart_clip(spec, size: tuple[int, int], palette: Palette, out: Path, seconds: float = 3.0) -> Path | None:
    """Animated chart via Manim (FACTORY_CHARTS=manim and `manim` on PATH). Returns None if unavailable."""
    if os.environ.get("FACTORY_CHARTS", "").lower() != "manim" or not shutil.which("manim"):
        return None
    hexc = lambda c: "#%02x%02x%02x" % c  # noqa: E731
    data = {"kind": spec.kind, "title": spec.title, "values": [float(v) for v in spec.values],
            "labels": list(spec.labels), "seconds": max(1.5, seconds),
            "last_label": _fmt(float(spec.values[-1]), spec.unit_prefix, spec.unit_suffix) if spec.values else ""}
    with tempfile.TemporaryDirectory() as tmp:
        scene = Path(tmp) / "chart.py"
        scene.write_text(MANIM_SCENE.format(spec=data, bg=hexc(palette.dark), fg=hexc(palette.light),
                                            accent=hexc(palette.accent_on(palette.dark, 3.0))))
        w, h = size
        try:
            subprocess.run(["manim", "-q", "m", "--disable_caching", "-r", f"{w},{h}", "--media_dir", tmp,
                            "-o", "chart.mp4", str(scene), "ChartScene"], check=True, capture_output=True,
                           timeout=300)
        except (subprocess.SubprocessError, OSError):
            return None
        found = next(Path(tmp).rglob("chart.mp4"), None)
        if not found:
            return None
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(found, out)
    return out
