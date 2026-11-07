#!/usr/bin/env python3
"""Import the products thread's catalog into site/content/shop.json and make small card images.

    python3 site/tools/import_shop.py /mnt/project-files/content-factory

Reads (from PR #6's folders, copied to project files):
  products/<slug>/LISTING.md + cover-square.png   guide + spreadsheet kits (Gumroad)
  templates/templates.csv + <slug>/cover-square.png Google Sheets and Notion templates (Gumroad)
  etsy/listings.csv + <slug>/LISTING.md           printables (Etsy)
Store links are placeholders built from site.json > stores; paste real ones into shop.json > items[].url
(an item's own url always wins, and re-running this tool keeps urls you've set).
Needs Pillow for the card images.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
OUT = SITE / "content" / "shop.json"
IMG = SITE / "static" / "img" / "shop"

KITS = [  # ladder order from products/UPSELL_PATH.md
    ("bill-cut-kit", "The Bill Cut Kit"), ("the-20-minute-budget", "The 20-Minute Budget"),
    ("credit-report-audit-kit", "The Credit Report Audit Kit"),
    ("debt-free-date-planner", "The Debt-Free Date Planner"),
    ("investing-starter-kit", "Start Investing With $100 a Month"),
    ("money-toolkit-bundle", "The Money Made Simple Toolkit")]
KIT_PRICES = {"bill-cut-kit": 5, "the-20-minute-budget": 12, "credit-report-audit-kit": 9,
              "debt-free-date-planner": 17, "investing-starter-kit": 19, "money-toolkit-bundle": 39}
# Etsy slugs that are the same product as a kit (listed once, with both store buttons).
ETSY_SAME = {"20-minute-budget": "the-20-minute-budget", "bill-cut-kit": "bill-cut-kit",
             "credit-report-audit-kit": "credit-report-audit-kit", "debt-free-date-planner": "debt-free-date-planner",
             "investing-starter-kit": "investing-starter-kit", "money-toolkit-bundle": "money-toolkit-bundle"}
ETSY_BUNDLES = {"budget-binder-bundle", "savings-challenge-pack", "mega-budget-bundle"}


def group(slug: str) -> str:
    if re.search(r"challenge|bingo|envelope-challenge|jar|roll-and-save", slug):
        return "savings"
    if re.search(r"debt|loan|credit-card", slug):
        return "debt"
    if re.search(r"budget|paycheck|50-30-20|zero-based|cash-envelope|irregular", slug):
        return "budget"
    return "trackers"


def section(md: str, name: str) -> str:
    m = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1).strip() if m else ""


def first_desc_line(md: str) -> str:
    body = section(md, "Description")
    lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not ln.startswith("```")]
    return lines[0] if lines else ""


def separately(md: str) -> int | None:
    m = re.search(r"(?:Bought separately: \$|\(\$)(\d+)(?: separately)?", md)
    return int(m.group(1)) if m else None


def card_image(src: Path, slug: str) -> str:
    from PIL import Image
    im = Image.open(src).convert("RGB")
    im.thumbnail((360, 360), Image.LANCZOS)  # fit, don't crop: mockups carry text near the edges
    canvas = Image.new("RGB", (360, 360), im.getpixel((2, 2)))
    canvas.paste(im, ((360 - im.width) // 2, (360 - im.height) // 2))
    im = canvas
    IMG.mkdir(parents=True, exist_ok=True)
    out = IMG / f"{slug}.jpg"
    im.save(out, "JPEG", quality=72, optimize=True, progressive=True)
    return f"/img/shop/{slug}.jpg"


def main(src: Path) -> None:
    old = {}
    if OUT.exists():
        old = {i["slug"]: i for i in json.loads(OUT.read_text()).get("items", [])}
    items = []

    # ---- kits
    etsy_rows = {r["slug"]: r for r in csv.DictReader((src / "etsy" / "listings.csv").open())}
    for slug, name in KITS:
        folder = "20-minute-budget" if slug == "the-20-minute-budget" else slug
        md = (src / "products" / folder / "LISTING.md")
        md = md.read_text() if md.exists() else (src / "etsy" / folder / "LISTING.md").read_text()
        blurb = section(md, "Short description").splitlines()[0] if section(md, "Short description") else first_desc_line(md)
        blurb = re.sub(r"\s*\$\d+\.?$", "", blurb).strip()
        if not blurb and slug == "the-20-minute-budget":  # the site's own product file has it
            blurb = re.search(r"^short: (.+)$", (SITE / "content" / "products" / "the-20-minute-budget.md").read_text(), re.M).group(1)
        cover = src / "products" / folder / "cover-square.png"
        if not cover.exists():
            cover = src / "etsy" / folder / "mockup-01-hero.png"
        etsy_slug = next((e for e, k in ETSY_SAME.items() if k == slug), None)
        items.append({"slug": slug, "name": name, "kind": "kit", "price": KIT_PRICES[slug],
                      "blurb": blurb, "image": card_image(cover, slug),
                      "bundle": slug == "money-toolkit-bundle",
                      "separately": (separately(md) or 62) if slug == "money-toolkit-bundle" else None,
                      "stores": ["gumroad"] + (["etsy"] if etsy_slug in etsy_rows else []),
                      "page": "/products/the-20-minute-budget/" if slug == "the-20-minute-budget" else ""})

    # ---- templates
    for r in csv.DictReader((src / "templates" / "templates.csv").open()):
        md_p = src / "templates" / r["slug"] / "LISTING.md"
        md = md_p.read_text() if md_p.exists() else ""
        is_bundle = r["kind"].endswith("bundle")
        it = {"slug": r["slug"], "name": r["name"], "kind": "notion" if r["kind"].startswith("notion") or
              r["slug"].startswith("notion") else "sheets", "price": float(r["price"]),
              "blurb": r["tagline"], "bundle": is_bundle, "separately": separately(md) if is_bundle else None,
              "stores": ["gumroad"]}
        cover = src / "templates" / r["slug"] / "cover-square.png"
        if is_bundle and cover.exists():
            it["image"] = card_image(cover, r["slug"])
        items.append(it)

    # ---- Etsy printables
    for slug, r in etsy_rows.items():
        if slug in ETSY_SAME:
            continue
        md = (src / "etsy" / slug / "LISTING.md").read_text()
        name = r["title"].split(",")[0].replace(" Printable", "").strip()
        it = {"slug": slug, "name": name, "kind": "printable", "group": group(slug), "price": float(r["price"]),
              "blurb": first_desc_line(md), "bundle": slug in ETSY_BUNDLES,
              "separately": separately(md) if slug in ETSY_BUNDLES else None, "stores": ["etsy"]}
        if slug in ETSY_BUNDLES:
            it["image"] = card_image(src / "etsy" / slug / "mockup-01-hero.png", slug)
        items.append(it)

    for it in items:  # keep links already pasted in
        if old.get(it["slug"], {}).get("url"):
            it["url"] = old[it["slug"]]["url"]
        if old.get(it["slug"], {}).get("etsy_url"):
            it["etsy_url"] = old[it["slug"]]["etsy_url"]
        it = {k: v for k, v in it.items() if v not in (None, "")}
    items = [{k: v for k, v in it.items() if v not in (None, "")} for it in items]
    OUT.write_text(json.dumps({"_about": __doc__.strip().splitlines()[0] + " Generated by tools/import_shop.py; "
                               "edit url/etsy_url here, everything else in the products thread's files.",
                               "items": items}, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(items)} items -> {OUT.relative_to(SITE)}; images in {IMG.relative_to(SITE)}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/content-factory"))
