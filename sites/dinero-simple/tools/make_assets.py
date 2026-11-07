#!/usr/bin/env python3
"""Render the Dinero Simple site's images and the Spanish lead-magnet PDF (only needed when you change them).

Needs Playwright with Chromium:  pip install playwright && playwright install chromium
    python3 sites/dinero-simple/tools/make_assets.py
Writes:
  static/downloads/tu-dinero-en-orden-en-7-dias.pdf   (from lead-magnet/tu-dinero-en-orden-en-7-dias.html)
  static/img/lead-magnet-cover.png                    (page 1 of the PDF, 600x776)
  static/img/producto-presupuesto-20-minutos.png      (1280x720 product cover)
  static/img/og-default.png                           (1200x630 social share image)
logo.png, avatar.jpg, favicon.png and apple-touch-icon.png come from the brand kit (`factory brandkit dinero-simple`).
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parents[1]
STATIC = SITE / "static"
LOGO = (STATIC / "img" / "logo.png").as_uri()
LEAD = "tu-dinero-en-orden-en-7-dias"

CARD_CSS = """
*{box-sizing:border-box;margin:0}
body{font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;background:#14213d;color:#fbf5e9}
.c{width:var(--w);height:var(--h);position:relative;overflow:hidden;padding:64px 72px;
  background:radial-gradient(80% 120% at 90% 0%,#2b3f6b 0%,#14213d 60%)}
.k{color:#ff7a59;font-weight:800;letter-spacing:.18em;text-transform:uppercase;font-size:20px}
h1{font-weight:900;letter-spacing:-.035em;line-height:.95;margin:22px 0 18px}
h1 em{font-style:normal;color:#2ab7a9}
p{color:#d5dbe8;line-height:1.35}
.b{position:absolute;left:72px;bottom:52px;display:flex;align-items:center;gap:14px;font-weight:800;font-size:22px}
.b img{width:48px;height:48px;border-radius:50%}
"""

PRODUCT = f"""<div class="c" style="--w:1280px;--h:720px">
<div class="k">Guía + hoja de cálculo</div>
<h1 style="font-size:96px">El Presupuesto<br>de <em>20 Minutos</em></h1>
<p style="font-size:30px;max-width:640px">Un solo número por semana. 20 minutos para manejarlo.</p>
<svg viewBox="0 0 200 200" style="position:absolute;right:80px;top:200px;width:360px;height:360px">
<circle cx="100" cy="100" r="92" fill="none" stroke="#2ab7a9" stroke-width="6"/>
<path d="M100 100 L100 8 A92 92 0 0 1 179.7 146 Z" fill="#2ab7a9" opacity=".9"/>
<circle cx="100" cy="100" r="70" fill="#14213d"/>
<text x="100" y="98" text-anchor="middle" font-family="Inter,sans-serif" font-weight="900" font-size="44" fill="#fbf5e9">20</text>
<text x="100" y="124" text-anchor="middle" font-family="Inter,sans-serif" font-weight="700" font-size="13" letter-spacing="3" fill="#ff7a59">MINUTOS</text></svg>
<div class="b"><img src="{LOGO}">Dinero Simple</div></div>"""

OG = f"""<div class="c" style="--w:1200px;--h:630px">
<div class="k">Dinero Simple</div>
<h1 style="font-size:80px;max-width:900px">Un paso con tu dinero<br>cada semana, <em>explicado<br>fácil.</em></h1>
<p style="font-size:28px">Presupuesto · invertir · crédito · herramientas</p>
<img src="{LOGO}" style="position:absolute;right:70px;top:70px;width:170px;height:170px;border-radius:50%">
</div>"""


def shot(page, html: str, w: int, h: int, out: Path) -> None:
    page.set_viewport_size({"width": w, "height": h})
    page.set_content(f"<style>{CARD_CSS}</style>{html}")
    page.wait_for_timeout(200)
    page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": w, "height": h})
    print("wrote", out.relative_to(SITE))


def main() -> None:
    (STATIC / "downloads").mkdir(parents=True, exist_ok=True)
    src = (SITE / "lead-magnet" / f"{LEAD}.html").as_uri()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page()
        page.goto(src)
        pdf = STATIC / "downloads" / f"{LEAD}.pdf"
        page.pdf(path=str(pdf), format="Letter", print_background=True, prefer_css_page_size=True)
        print("wrote", pdf.relative_to(SITE))
        cover = browser.new_page(viewport={"width": 816, "height": 1056})
        cover.goto(src)
        cover.emulate_media(media="print")
        out = STATIC / "img" / "lead-magnet-cover.png"
        cover.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": 816, "height": 1056})
        from PIL import Image  # Pillow is already a project dependency
        Image.open(out).convert("RGB").resize((600, 776), Image.LANCZOS).save(out, optimize=True)
        print("wrote", out.relative_to(SITE))
        shot(page, PRODUCT, 1280, 720, STATIC / "img" / "producto-presupuesto-20-minutos.png")
        shot(page, OG, 1200, 630, STATIC / "img" / "og-default.png")
        browser.close()


if __name__ == "__main__":
    main()
