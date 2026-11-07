"""Build a brand's visual kit: profile picture, YouTube banner + watermark,
Instagram highlight covers, a style sheet (PNG + HTML) and a bio pack.

Everything is original artwork drawn from the brand palette and initials;
no third-party logos or characters.
"""
from __future__ import annotations

import base64
import html
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw

from ..config import BrandProfile, Settings
from ..llm import LLM
from . import bios as bio_mod
from .draw import (FILLER_ICONS, Palette, draw_icon, fit_font, font, font_family_name, gradient, initials,
                   logo_mark, mix, pick_icon, rgb_to_hex, wrap, _soft_glow)

PROFILE = (1080, 1080)
BANNER = (2560, 1440)
BANNER_SAFE = (1546, 423)
WATERMARK = (150, 150)
HIGHLIGHT = (1080, 1920)


def kit_dir(settings: Settings, brand: BrandProfile) -> Path:
    return settings.output_dir / brand.slug / "brand-kit"


def handle_of(brand: BrandProfile) -> str:
    h = brand.visual.watermark or next((a.handle for a in brand.accounts if a.handle), "")
    return h if not h or h.startswith("@") else f"@{h}"


# ---------------------------------------------------------------- images
def profile_picture(pal: Palette, letters: str) -> Image.Image:
    """1080x1080 mark on the dark brand colour; all detail sits inside the
    inscribed circle so a circular crop loses nothing."""
    bg = gradient(PROFILE, mix(pal.dark, pal.accent, 0.10), pal.dark).convert("RGBA")
    mark = logo_mark(int(PROFILE[0] * 0.82), pal, letters, background=None)
    _soft_glow(bg, (PROFILE[0] / 2, PROFILE[1] / 2), PROFILE[0] * 0.36, pal.accent, 60)
    off = (PROFILE[0] - mark.width) // 2
    bg.alpha_composite(mark, (off, off))
    return bg.convert("RGB")


def watermark(pal: Palette, letters: str) -> Image.Image:
    """150x150 transparent PNG for YouTube's branding watermark."""
    return logo_mark(WATERMARK[0], pal, letters, background=None, ring=False)


def banner(pal: Palette, brand: BrandProfile, letters: str, guides: bool = False) -> Image.Image:
    """2560x1440 channel art. Text and mark stay inside the 1546x423 area that
    every device shows; the rest is decoration that may be cropped."""
    W, H = BANNER
    img = gradient(BANNER, pal.dark, mix(pal.dark, pal.accent, 0.18)).convert("RGBA")
    # decorative shapes outside the safe area (visible on TV/desktop only)
    deco = Image.new("RGBA", BANNER, (0, 0, 0, 0))
    d = ImageDraw.Draw(deco)
    d.ellipse([-420, -520, 760, 660], fill=(*pal.accent, 26))
    for r in (520, 640):
        d.ellipse([170 - r, 70 - r, 170 + r, 70 + r], outline=(*pal.accent, 40), width=6)
    d.ellipse([W - 640, H - 700, W + 360, H + 300], fill=(*pal.accent2, 26))
    for r in (600, 720):
        d.ellipse([W - 140 - r, H - 200 - r, W - 140 + r, H - 200 + r], outline=(*pal.accent2, 40), width=6)
    d.ellipse([W - 360, 140, W - 140, 360], fill=(*pal.accent, 60))
    img.alpha_composite(deco)
    sx, sy = (W - BANNER_SAFE[0]) // 2, (H - BANNER_SAFE[1]) // 2
    sw, sh = BANNER_SAFE
    d = ImageDraw.Draw(img)
    mark_size = sh - 40
    img.alpha_composite(logo_mark(mark_size, pal, letters), (sx + 10, sy + 20))
    tx = sx + mark_size + 70
    tw = sx + sw - tx - 10
    name_f = fit_font(brand.name, tw, 150, 60, weight="Black")
    tagline = brand.promise or brand.niche
    tagline = tagline[:1].upper() + tagline[1:]
    tag_f = font(52, "Medium", display=False)
    tag_lines = wrap(tagline, tag_f, tw)
    while len(tag_lines) > 2 and tag_f.size > 30:
        tag_f = font(tag_f.size - 4, "Medium", display=False)
        tag_lines = wrap(tagline, tag_f, tw)
    tag_lines = tag_lines[:2]
    meta = "  ·  ".join(x for x in [handle_of(brand), _cadence_line(brand)] if x)
    meta_f = font(36, "SemiBold", display=False)
    name_h = name_f.getbbox("Hg")[3]
    line_h = int(tag_f.size * 1.3)
    total = name_h + 18 + line_h * len(tag_lines) + (26 + 44 if meta else 0)
    y = sy + (sh - total) // 2
    d.text((tx, y), brand.name, font=name_f, fill=pal.light)
    y += name_h + 18
    for line in tag_lines:
        d.text((tx, y), line, font=tag_f, fill=mix(pal.light, pal.dark, 0.18))
        y += line_h
    if meta:
        y += 26
        d.rounded_rectangle([tx, y + 4, tx + 8, y + 40], radius=4, fill=pal.accent)
        d.text((tx + 24, y), meta, font=meta_f, fill=mix(pal.light, pal.dark, 0.3))
    if guides:
        d.rectangle([sx, sy, sx + sw, sy + sh], outline=(255, 0, 80), width=4)
    return img.convert("RGB")


def _cadence_line(brand: BrandProfile) -> str:
    c = brand.cadence
    if c.long_per_week and "long" in brand.formats:
        return "New videos every week"
    if c.shorts_per_week >= 5:
        return "New shorts most days"
    return "New videos every week"


def highlight_cover(pal: Palette, icon: str, variant: int) -> Image.Image:
    """1080x1920 cover; Instagram shows the centre circle, so the icon sits
    there on a solid disc. Backgrounds alternate dark/accent for variety."""
    W, H = HIGHLIGHT
    img = gradient(HIGHLIGHT, mix(pal.dark, pal.accent, 0.08), pal.dark, vertical=True).convert("RGBA")
    d = ImageDraw.Draw(img)
    disc = pal.accent if variant % 2 == 0 else pal.accent2
    r = 420
    cx, cy = W // 2, H // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=disc)
    ink = pal.ink_on(disc)
    ic = draw_icon(icon, 440, ink, disc)
    img.alpha_composite(ic, (cx - 220, cy - 220))
    return img.convert("RGB")


def pillar_labels(brand: BrandProfile, n: int = 5) -> list[tuple[str, str]]:
    """(label, icon) for n highlights: the brand pillars first, then fillers."""
    out: list[tuple[str, str]] = []
    used: set[str] = set()
    for p in brand.pillars[:n]:
        icon = pick_icon(p, used)
        used.add(icon)
        out.append((p, icon))
    for icon, label in FILLER_ICONS:
        if len(out) >= n:
            break
        if icon in used:
            continue
        used.add(icon)
        out.append((label, icon))
    return out[:n]


def short_label(text: str, limit: int = 15) -> str:
    """Highlight titles are cut at ~15 chars by Instagram."""
    words = [w for w in text.replace("(", " ").replace(")", " ").split() if w.lower() not in
             {"the", "a", "an", "of", "and", "that", "actually", "for", "to", "why", "they", "exist"}]
    out = ""
    for w in words:
        trial = f"{out} {w}".strip()
        if len(trial) > limit:
            break
        out = trial
    return (out or text[:limit]).title()


# ---------------------------------------------------------------- style sheet
def do_dont(brand: BrandProfile) -> tuple[list[str], list[str]]:
    dos = [f"Sound like {brand.voice.persona}: {brand.voice.tone}.",
           f"Deliver the promise: {brand.promise or brand.niche}.",
           "Lead with a specific hook; one idea per post.",
           f"Close with the CTA: “{brand.cta}”",
           "Label AI-assisted content and disclose affiliate links (#ad / “I may earn a commission”)."]
    donts = [f"Use banned phrases: {', '.join(repr(p) for p in brand.voice.banned_phrases)}."
             if brand.voice.banned_phrases else "Use hype, clickbait or guaranteed-result language.",
             "Let an AI voice or avatar give first-person testimonials.",
             "Use other creators' clips, logos, or real people's likeness.",
             "Use more than two accent colours in one graphic."]
    if brand.avoid_topics:
        donts.insert(1, f"Cover off-limits topics: {', '.join(brand.avoid_topics)}.")
    return dos, donts


def style_sheet_png(pal: Palette, brand: BrandProfile, letters: str) -> Image.Image:
    W, H = 1600, 2200
    img = Image.new("RGBA", (W, H), (*pal.light, 255))
    d = ImageDraw.Draw(img)
    ink, soft = pal.dark, mix(pal.dark, pal.light, 0.45)
    m = 100
    # header band
    d.rectangle([0, 0, W, 360], fill=pal.dark)
    img.alpha_composite(logo_mark(220, pal, letters), (m, 70))
    d.text((m + 260, 104), brand.name, font=fit_font(brand.name, W - m * 2 - 260, 86, 40, "Black"), fill=pal.light)
    d.text((m + 262, 214), "Brand style sheet", font=font(40, "Medium", False), fill=mix(pal.light, pal.dark, 0.3))
    y = 430
    d.text((m, y), "PALETTE", font=font(28, "Bold", False), fill=soft)
    y += 56
    sw = (W - m * 2 - 3 * 40) // 4
    for i, (role, col, _use) in enumerate(pal.roles()):
        x = m + i * (sw + 40)
        d.rounded_rectangle([x, y, x + sw, y + 240], radius=28, fill=col,
                            outline=mix(pal.dark, pal.light, 0.8) if col == pal.light else None, width=3)
        d.text((x, y + 262), rgb_to_hex(col).upper(), font=font(38, "Bold", False), fill=ink)
        d.text((x, y + 312), role, font=font(26, "Medium", False), fill=soft)
    y += 420
    d.text((m, y), "TYPE", font=font(28, "Bold", False), fill=soft)
    y += 56
    fam = font_family_name()
    d.text((m, y), f"{fam} Display Black", font=font(72, "Black"), fill=ink)
    d.text((m, y + 96), f"Headlines, thumbnails, on-screen text", font=font(30, "Regular", False), fill=soft)
    d.text((m + 760, y + 14), f"{fam} Medium", font=font(52, "Medium", False), fill=ink)
    d.text((m + 760, y + 96), "Captions, body copy, subtitles", font=font(30, "Regular", False), fill=soft)
    y += 200
    d.text((m, y), "VOICE", font=font(28, "Bold", False), fill=soft)
    y += 56
    voice = f"{brand.voice.persona.capitalize()}. Tone: {brand.voice.tone}."
    for line in wrap(voice, font(40, "SemiBold", False), W - m * 2)[:3]:
        d.text((m, y), line, font=font(40, "SemiBold", False), fill=ink)
        y += 54
    y += 50
    dos, donts = do_dont(brand)
    colw = (W - m * 2 - 60) // 2
    for col_i, (title, items, mark_col) in enumerate((("DO", dos, pal.accent), ("DON'T", donts, (200, 64, 64)))):
        x = m + col_i * (colw + 60)
        yy = y
        d.text((x, yy), title, font=font(28, "Bold", False), fill=soft)
        yy += 56
        f = font(28, "Regular", False)
        for item in items:
            lines = wrap(item, f, colw - 50)
            d.ellipse([x, yy + 8, x + 20, yy + 28], fill=mark_col)
            for line in lines[:4]:
                d.text((x + 40, yy), line, font=f, fill=ink)
                yy += 38
            yy += 18
    d.line([m, H - 170, W - m, H - 170], fill=mix(pal.dark, pal.light, 0.8), width=2)
    ff = font(24, "Regular", False)
    fy = H - 140
    for line in wrap(f"{handle_of(brand)}  ·  {brand.ai_disclosure}", ff, W - m * 2)[:3]:
        d.text((m, fy), line, font=ff, fill=soft)
        fy += 34
    return img.convert("RGB")


def style_sheet_html(pal: Palette, brand: BrandProfile, logo_png: bytes) -> str:
    e = html.escape
    dos, donts = do_dont(brand)
    swatches = "".join(
        f'<div class="sw"><div class="chip" style="background:{rgb_to_hex(c)}"></div>'
        f'<b>{rgb_to_hex(c).upper()}</b><span>{e(role)}</span><small>{e(use)}</small></div>'
        for role, c, use in pal.roles())
    logo = base64.b64encode(logo_png).decode()
    li = lambda xs: "".join(f"<li>{e(x)}</li>" for x in xs)  # noqa: E731
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(brand.name)} brand style sheet</title>
<style>
:root{{--ink:{rgb_to_hex(pal.dark)};--paper:{rgb_to_hex(pal.light)};--a:{rgb_to_hex(pal.accent)};--a2:{rgb_to_hex(pal.accent2)}}}
*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,system-ui,sans-serif;background:var(--paper);color:var(--ink)}}
header{{background:var(--ink);color:var(--paper);padding:40px 24px;display:flex;gap:24px;align-items:center}}
header img{{width:96px;height:96px}}h1{{margin:0;font-size:40px;font-weight:900}}header p{{margin:4px 0 0;color:var(--a2)}}
main{{max-width:960px;margin:0 auto;padding:24px}}h2{{font-size:13px;letter-spacing:.12em;opacity:.6;margin:40px 0 12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}}
.sw{{display:flex;flex-direction:column;gap:4px}}.chip{{height:120px;border-radius:16px;border:1px solid rgba(0,0,0,.08)}}
.sw small{{opacity:.6}}ul{{padding-left:20px;line-height:1.6}}.cols{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}
@media(max-width:640px){{.cols{{grid-template-columns:1fr}}}}footer{{padding:24px;opacity:.6;font-size:13px;text-align:center}}
</style></head><body>
<header><img src="data:image/png;base64,{logo}" alt="{e(brand.name)} logo mark"><div><h1>{e(brand.name)}</h1>
<p>Brand style sheet · {e(handle_of(brand))}</p></div></header>
<main>
<h2>PALETTE</h2><div class="grid">{swatches}</div>
<h2>TYPE</h2><p><b style="font-size:32px;font-weight:900">Inter Display Black</b> headlines, thumbnails, on-screen text<br>
<span style="font-size:22px;font-weight:500">Inter Medium</span> captions, body copy, subtitles</p>
<h2>VOICE</h2><p><b>{e(brand.voice.persona.capitalize())}.</b> Tone: {e(brand.voice.tone)}.</p>
<p><b>Promise:</b> {e(brand.promise or brand.niche)}<br><b>Audience:</b> {e(brand.audience)}<br>
<b>Pillars:</b> {e(', '.join(brand.pillars))}</p>
<div class="cols"><div><h2>DO</h2><ul>{li(dos)}</ul></div><div><h2>DON'T</h2><ul>{li(donts)}</ul></div></div>
<h2>IMAGE STYLE</h2><p>{e(brand.visual.image_style)}</p>
{f'<p><b>Mascot:</b> {e(brand.visual.mascot)}</p>' if brand.visual.mascot else ''}
</main><footer>{e(brand.ai_disclosure)}</footer></body></html>
"""


# ---------------------------------------------------------------- build
def _png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def build_brand_kit(settings: Settings, brand: BrandProfile, llm: LLM | None = None) -> dict[str, Path]:
    """Write the full kit to output_dir/<slug>/brand-kit/ and return {name: path}.

    `llm` writes the bios; by default one is built from settings (offline
    when no API key), so this always works without network."""
    out = kit_dir(settings, brand)
    (out / "highlights").mkdir(parents=True, exist_ok=True)
    pal = Palette.from_hex(brand.visual.palette)
    letters = initials(brand.name)
    paths: dict[str, Path] = {}

    def save(name: str, img: Image.Image, rel: str) -> None:
        p = out / rel
        img.save(p, "PNG", optimize=True)
        paths[name] = p

    save("profile_picture", profile_picture(pal, letters), "profile-picture.png")
    save("youtube_banner", banner(pal, brand, letters), "youtube-banner.png")
    save("youtube_banner_guides", banner(pal, brand, letters, guides=True), "youtube-banner-safe-area-guide.png")
    save("youtube_watermark", watermark(pal, letters), "youtube-watermark.png")
    logo = logo_mark(1024, pal, letters)
    save("logo_mark", logo, "logo-mark.png")
    labels = []
    for i, (label, icon) in enumerate(pillar_labels(brand)):
        save(f"highlight_{i + 1}", highlight_cover(pal, icon, i), f"highlights/{i + 1:02d}-{icon}.png")
        labels.append({"file": f"highlights/{i + 1:02d}-{icon}.png", "title": short_label(label), "pillar": label})
    save("style_sheet_png", style_sheet_png(pal, brand, letters), "style-sheet.png")
    html_path = out / "style-sheet.html"
    html_path.write_text(style_sheet_html(pal, brand, _png_bytes(logo_mark(192, pal, letters))))
    paths["style_sheet_html"] = html_path

    llm = llm or LLM(settings.llm_provider, settings.anthropic_model, settings.anthropic_effort)
    pack = bio_mod.write_bios(llm, brand)
    bio_path = out / "bio-pack.txt"
    bio_path.write_text(bio_mod.render_text(brand, pack))
    paths["bio_pack"] = bio_path
    manifest = {
        "brand": brand.slug, "palette": {r: rgb_to_hex(c) for r, c, _ in pal.roles()}, "initials": letters,
        "highlights": labels, "bios": pack.model_dump(),
        "files": {k: str(v.relative_to(out)) for k, v in paths.items()},
        "notes": {"youtube_banner": "2560x1440; text inside the centred 1546x423 safe area",
                  "youtube_watermark": "150x150 transparent PNG (YouTube Studio > Customisation > Branding)",
                  "highlights": "1080x1920; Instagram crops the centre circle"},
    }
    man_path = out / "manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2))
    paths["manifest"] = man_path
    return paths
