#!/usr/bin/env python3
"""Render the site's images and the lead-magnet PDF (only needed when you change them).

Needs Playwright with Chromium:  pip install playwright && playwright install chromium
    python3 site/tools/make_assets.py
Writes:
  site/static/downloads/the-7-day-money-reset.pdf   (from site/lead-magnet/the-7-day-money-reset.html)
  site/static/img/lead-magnet-cover.png             (page 1 of the PDF, 600x776)
  site/static/img/product-20-minute-budget.png      (1280x720 product cover)
  site/static/img/og-default.png                    (1200x630 social share image)
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parents[1]
STATIC = SITE / "static"
LOGO = (STATIC / "img" / "logo.png").as_uri()

CARD_CSS = """
*{box-sizing:border-box;margin:0}
body{font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;background:#0b1d13;color:#f4f1e8}
.c{width:var(--w);height:var(--h);position:relative;overflow:hidden;padding:64px 72px;
  background:radial-gradient(80% 120% at 90% 0%,#1d3d2a 0%,#0b1d13 60%)}
.k{color:#f2b134;font-weight:800;letter-spacing:.18em;text-transform:uppercase;font-size:20px}
h1{font-weight:900;letter-spacing:-.035em;line-height:.95;margin:22px 0 18px}
h1 em{font-style:normal;color:#2fbf71}
p{color:#cfd8cf;line-height:1.35}
.b{position:absolute;left:72px;bottom:52px;display:flex;align-items:center;gap:14px;font-weight:800;font-size:22px}
.b img{width:48px;height:48px;border-radius:50%}
"""

PRODUCT = f"""<div class="c" style="--w:1280px;--h:720px">
<div class="k">Guide + spreadsheet</div>
<h1 style="font-size:104px">The<br><em>20-Minute</em><br>Budget</h1>
<p style="font-size:30px;max-width:640px">One number per week. 20 minutes to run it.</p>
<svg viewBox="0 0 200 200" style="position:absolute;right:90px;top:150px;width:420px;height:420px">
<circle cx="100" cy="100" r="92" fill="none" stroke="#2fbf71" stroke-width="6"/>
<path d="M100 100 L100 8 A92 92 0 0 1 179.7 146 Z" fill="#2fbf71" opacity=".9"/>
<circle cx="100" cy="100" r="70" fill="#0b1d13"/>
<text x="100" y="98" text-anchor="middle" font-family="Inter,sans-serif" font-weight="900" font-size="44" fill="#f4f1e8">20</text>
<text x="100" y="124" text-anchor="middle" font-family="Inter,sans-serif" font-weight="700" font-size="13" letter-spacing="3" fill="#f2b134">MINUTES</text></svg>
<div class="b"><img src="{LOGO}">Money Made Simple</div></div>"""

OG = f"""<div class="c" style="--w:1200px;--h:630px">
<div class="k">Money Made Simple</div>
<h1 style="font-size:84px;max-width:900px">One money move<br>a week, <em>explained<br>simply.</em></h1>
<p style="font-size:28px">Budgeting · first-time investing · credit · money tools</p>
<img src="{LOGO}" style="position:absolute;right:70px;top:70px;width:180px;height:180px;border-radius:50%">
</div>"""


def shot(page, html: str, w: int, h: int, out: Path) -> None:
    page.set_viewport_size({"width": w, "height": h})
    page.set_content(f"<style>{CARD_CSS}</style>{html}")
    page.wait_for_timeout(200)
    page.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": w, "height": h})
    print("wrote", out.relative_to(SITE.parent))


def main() -> None:
    (STATIC / "downloads").mkdir(parents=True, exist_ok=True)
    src = (SITE / "lead-magnet" / "the-7-day-money-reset.html").as_uri()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page()
        page.goto(src)
        pdf = STATIC / "downloads" / "the-7-day-money-reset.pdf"
        page.pdf(path=str(pdf), format="Letter", print_background=True, prefer_css_page_size=True)
        print("wrote", pdf.relative_to(SITE.parent))
        # Cover thumbnail: page 1 at 8.5x11 ratio.
        cover = browser.new_page(viewport={"width": 816, "height": 1056})
        cover.goto(src)
        cover.emulate_media(media="print")
        cover.screenshot(path=str(STATIC / "img" / "lead-magnet-cover.png"),
                         clip={"x": 0, "y": 0, "width": 816, "height": 1056})
        from PIL import Image  # noqa: E402  (Pillow is already a project dependency)
        im = Image.open(STATIC / "img" / "lead-magnet-cover.png").convert("RGB")
        im.resize((600, 776), Image.LANCZOS).save(STATIC / "img" / "lead-magnet-cover.png", optimize=True)
        print("wrote site/static/img/lead-magnet-cover.png")
        shot(page, PRODUCT, 1280, 720, STATIC / "img" / "product-20-minute-budget.png")
        shot(page, OG, 1200, 630, STATIC / "img" / "og-default.png")
        browser.close()


if __name__ == "__main__":
    main()
