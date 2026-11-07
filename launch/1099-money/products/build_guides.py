"""Build the kit and bundle guides (HTML -> PDF) with the tracker guide's styles.

    python launch/1099-money/products/build_guides.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
from contentfactory.business.pdf import html_to_pdf  # noqa: E402

TRACKER_HTML = HERE.parent / "product" / "the-quarterly-tax-tracker.html"
GUIDES = [
    (HERE / "rate-contract-kit", "The Rate & Contract Kit", "the-rate-and-contract-kit.html", "The-Rate-and-Contract-Kit.pdf"),
    (HERE / "bundle", "The Freelancer Money Bundle", "the-freelancer-money-bundle.html", "Start-Here-Freelancer-Money-Bundle.pdf"),
]


def head(title: str) -> str:
    h = TRACKER_HTML.read_text().split("<body", 1)[0]
    return h.replace("<title>The Quarterly Tax Tracker</title>", f"<title>{title}</title>")


def build() -> list[Path]:
    out = []
    for folder, title, html_name, pdf_name in GUIDES:
        html = folder / html_name
        html.write_text(head(title) + (folder / "guide-body.html").read_text())
        pdf = folder / pdf_name
        if html_to_pdf(html, pdf):
            out.append(pdf)
        out.append(html)
    return out


if __name__ == "__main__":
    for p in build():
        print(p.relative_to(HERE))
