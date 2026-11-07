"""Per-video looks, so a channel doesn't read as one template with the words swapped.

YouTube's inauthentic-content review looks at a whole channel and names
"slideshows that all have the same narration" as its example. Every video
gets a look: a layout, a motion style, a caption style and a headline style.
The look is picked to differ as much as possible from the brand's recent
videos (newest count most), so no two videos in a row look the same with the
sound off. The chosen look is stored in assets["look"].
"""
from __future__ import annotations

import itertools

from PIL import Image, ImageDraw

LAYOUTS = ("full", "framed", "split")       # full-bleed art | art inset on the brand colour | art beside a panel
MOTIONS = ("kenburns", "gentle", "cuts")      # varied pans/zooms | one slow push | no movement, hard cuts
CAPTIONS = ("pop", "plain", "box")            # pop-in words | steady words | words on a solid box, higher up
HEADLINES = ("card", "bar")                   # rounded card | full-width strip
DIMENSIONS = {"layout": LAYOUTS, "motion": MOTIONS, "captions": CAPTIONS, "headline": HEADLINES}


def choose(recent: list[dict], seed: int = 0) -> dict:
    """The combination that shares the fewest traits with recent looks (newest first, weighted higher)."""
    recent = [r for r in recent if isinstance(r, dict)][:8]
    combos = [dict(zip(DIMENSIONS, c)) for c in itertools.product(*DIMENSIONS.values())]

    def cost(c: dict) -> float:
        total = 0.0
        for age, r in enumerate(recent):
            w = 1.0 / (1 + age)
            total += w * sum(c[k] == r.get(k) for k in DIMENSIONS)
            if all(c[k] == r.get(k) for k in DIMENSIONS):
                total += 10 * w  # never repeat a whole recent look
        return total

    best = min(cost(c) for c in combos)
    ties = [c for c in combos if cost(c) == best]
    return ties[seed % len(ties)]


def compose(art_path, size: tuple[int, int], layout: str, palette, out) -> object:
    """Bake the layout into the beat's still. 'full' returns the art unchanged."""
    if layout == "full":
        return art_path
    w, h = size
    art = Image.open(art_path).convert("RGB")
    canvas = Image.new("RGB", size, palette.dark)
    vertical = h > w
    if layout == "framed":
        box_w = int(w * 0.84)
        box_h = int(h * (0.56 if vertical else 0.78))
        top = int(h * (0.24 if vertical else 0.14))
        box = (int((w - box_w) / 2), top, int((w - box_w) / 2) + box_w, top + box_h)
    else:  # split
        box = (0, 0, w, int(h * 0.58)) if vertical else (int(w * 0.42), 0, w, h)
    bw, bh = box[2] - box[0], box[3] - box[1]
    scale = max(bw / art.width, bh / art.height)
    fitted = art.resize((max(bw, int(art.width * scale)), max(bh, int(art.height * scale))), Image.LANCZOS)
    cx, cy = (fitted.width - bw) // 2, (fitted.height - bh) // 2
    fitted = fitted.crop((cx, cy, cx + bw, cy + bh))
    mask = Image.new("L", (bw, bh), 255)
    if layout == "framed":
        mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw, bh), radius=int(min(w, h) * 0.03), fill=255)
    canvas.paste(fitted, box[:2], mask)
    accent = palette.accent_on(palette.dark)
    d = ImageDraw.Draw(canvas)
    if layout == "split":  # a thin accent rule where the art meets the panel
        if vertical:
            d.rectangle((0, box[3], w, box[3] + 8), fill=accent)
        else:
            d.rectangle((box[0] - 8, 0, box[0], h), fill=accent)
    from pathlib import Path
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    return out
