"""Render the product HTML templates to HTML + PDF (and cover PNGs).

Usage:  python3 build_docs.py [name ...]      (default: all)
Needs node + playwright (global) for rendering; pdftoppm for previews.
Writes previews to $PREVIEW_DIR if set.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import jinja2

import figures

HERE = Path(__file__).resolve().parent
PRODUCTS = HERE.parent
BASE_CSS = (HERE / "base.css").read_text()
env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(HERE / "templates")), autoescape=False,
                         trim_blocks=False, lstrip_blocks=False)
env.filters["money"] = lambda v, d=0: f"${v:,.{d}f}"
env.filters["pct"] = lambda v, d=1: f"{v:.{d}f}%"

DAYS = [
    {"short": "Money snapshot", "mins": 20},
    {"short": "Cancel one subscription", "mins": 15},
    {"short": "Bill calendar + autopay", "mins": 20},
    {"short": "Three bank alerts", "mins": 10},
    {"short": "Start an emergency fund", "mins": 15},
    {"short": "List debts, pick an order", "mins": 20},
    {"short": "Your weekly number", "mins": 25},
]

DOCS = {
    # name: (template, output html, output pdf, context factory)
    "reset": ("money-reset.html.j2", "free-lead-magnet/the-7-day-money-reset.html",
              "free-lead-magnet/The-7-Day-Money-Reset.pdf", lambda: {"days": DAYS, "budget_price": 12}),
    "planner-guide": ("planner-guide.html.j2", "debt-payoff-planner/debt-payoff-planner-guide.html",
                      "debt-payoff-planner/Debt-Payoff-Planner-Guide.pdf", figures.planner_context),
    "invest": ("investing-kit.html.j2", "first-investing-account-kit/first-investing-account-kit.html",
               "first-investing-account-kit/Open-Your-First-Investing-Account.pdf", figures.investing_context),
}
COVERS = {
    # name: (template, output png, context)
    "cover-reset": ("cover.html.j2", "free-lead-magnet/cover-7-day-money-reset.png", "reset"),
    "cover-planner": ("cover.html.j2", "debt-payoff-planner/cover-debt-payoff-planner.png", "planner"),
    "cover-invest": ("cover.html.j2", "first-investing-account-kit/cover-first-investing-account-kit.png", "invest"),
    "cover-bundle": ("cover.html.j2", "bundle/cover-starter-bundle.png", "bundle"),
}


def node(*args):
    r = subprocess.run(["node", str(HERE / "render.js"), *args], capture_output=True, text=True,
                       env={**os.environ, "NODE_PATH": subprocess.run(["npm", "root", "-g"], capture_output=True,
                                                                       text=True).stdout.strip()})
    if r.returncode:
        raise SystemExit(r.stderr)
    return r.stdout.strip()


def preview(pdf: Path, name: str):
    d = os.environ.get("PREVIEW_DIR")
    if not d:
        return
    Path(d).mkdir(parents=True, exist_ok=True)
    for old in Path(d).glob(f"{name}-*.png"):
        old.unlink()
    subprocess.run(["pdftoppm", "-r", "70", "-png", str(pdf), str(Path(d) / name)], check=True)


def build_doc(name):
    tpl, html_out, pdf_out, ctx = DOCS[name]
    html = env.get_template(tpl).render(base_css=BASE_CSS, **ctx())
    hp, pp = PRODUCTS / html_out, PRODUCTS / pdf_out
    hp.write_text(html)
    msg = node("pdf", str(hp), str(pp))
    pages = subprocess.run(["pdfinfo", str(pp)], capture_output=True, text=True).stdout
    pages = next((ln.split()[-1] for ln in pages.splitlines() if ln.startswith("Pages")), "?")
    print(f"{name}: {pp.relative_to(PRODUCTS)} ({pages} pages) {msg}")
    preview(pp, name)


PAGE_IMAGES = {
    "img_planner_guide": ("debt-payoff-planner/Debt-Payoff-Planner-Guide.pdf", 1),
    "img_invest": ("first-investing-account-kit/Open-Your-First-Investing-Account.pdf", 1),
    "img_invest_ws": ("first-investing-account-kit/Open-Your-First-Investing-Account.pdf", 10),
    "img_budget": ("../product/The-20-Minute-Budget.pdf", 1),
}


def page_images(tmpdir: Path) -> dict:
    """Real page renders of the PDFs, so cover mockups only show what's actually in the product."""
    out = {}
    for key, (pdf, page) in PAGE_IMAGES.items():
        src = PRODUCTS / pdf
        if not src.exists():
            continue
        stem = tmpdir / key
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-singlefile", "-f", str(page), "-l", str(page),
                        str(src), str(stem)], check=True, capture_output=True)
        out[key] = "file://" + str(stem) + ".png"
    return out


def build_cover(name):
    import tempfile
    tpl, png_out, which = COVERS[name]
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        html = env.get_template(tpl).render(which=which, **page_images(tdp), **figures.cover_context(which))
        tmp = tdp / f"{name}.html"
        tmp.write_text(html)
        out = PRODUCTS / png_out
        node("png", str(tmp), str(out), "1600", "1200")
    print(f"{name}: {out.relative_to(PRODUCTS)}")


if __name__ == "__main__":
    names = sys.argv[1:] or [*DOCS, *COVERS]
    for n in names:
        (build_doc if n in DOCS else build_cover)(n)
