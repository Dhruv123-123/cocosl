"""Build the Gumroad downloads for 1099 Money's multi-file products.

Etsy's 22 Oct 2026 rule bans AI-generated functional guides, so the kits and bundles (which include guides that AI
helped draft) are sold on Gumroad and the site only; the Etsy build (`../etsy/build_etsy.py`) makes the
spreadsheet-only tracker listing.

    python launch/1099-money/products/build_gumroad.py [OUT_DIR] [--edition 2027]

Writes OUT_DIR/freelancer-tax-kit/ (1-Start-Here.pdf + Freelancer-Tax-Kit.zip). Default OUT_DIR is
/mnt/project-files/content-factory/1099-money/gumroad.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent
ROOT = BRAND.parent.parent
sys.path.insert(0, str(ROOT / "src"))
from contentfactory.business.pdf import html_to_pdf  # noqa: E402

DOWNLOADS = ROOT / "apps" / "freelance-tax" / "downloads"
CALENDAR = DOWNLOADS / "freelancer-tax-calendar-2027.pdf"
CHECKLIST = DOWNLOADS / "freelancer-tax-checklist.pdf"
JAR = DOWNLOADS / "tax-jar-tracker.pdf"
TAXKIT = HERE / "tax-kit"


def tracker_dir(edition: int) -> Path:
    return BRAND / "product" if edition == 2026 else BRAND / "product" / f"edition-{edition}"


def zip_dir(src: Path, dest: Path, arc_root: str) -> Path:
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, f"{arc_root}/{p.relative_to(src)}")
    return dest


def tracker_files(edition: int) -> list[Path]:
    t = tracker_dir(edition)
    return [t / "Quarterly-Tax-Tracker.xlsx", t / "The-Quarterly-Tax-Tracker.pdf"]


def build_tax_kit(out_root: Path, edition: int = 2026) -> list[Path]:
    """The Freelancer Tax Kit: the tracker (spreadsheet + guide) plus the three free tax printables."""
    d = out_root / "freelancer-tax-kit"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as t:
        stage = Path(t) / "taxkit"
        for sub, srcs in (("2-Quarterly-Tax-Tracker", tracker_files(edition)), ("3-Tax-Calendar-2027", [CALENDAR]),
                          ("4-Tax-Checklist", [CHECKLIST]), ("5-Tax-Jar-Tracker", [JAR])):
            (stage / sub).mkdir(parents=True)
            for src in srcs:
                shutil.copy(src, stage / sub)
        start = d / "1-Start-Here.pdf"
        if not html_to_pdf(TAXKIT / "the-freelancer-tax-kit.html", start):
            raise SystemExit("tax kit: could not print the Start Here PDF")
        zip_dir(stage, d / "Freelancer-Tax-Kit.zip", "Freelancer-Tax-Kit")
    shutil.copy(TAXKIT / "LISTING.md", d / "LISTING.md")
    return sorted(d.iterdir())


BUILDERS = {"tax-kit": build_tax_kit}


def main(argv: list[str]) -> dict[str, list[Path]]:
    edition = 2026
    if "--edition" in argv:
        k = argv.index("--edition")
        edition = int(argv[k + 1])
        del argv[k:k + 2]
    out = Path(argv[0]) if argv else Path("/mnt/project-files/content-factory/1099-money/gumroad")
    made = {name: fn(out, edition) for name, fn in BUILDERS.items()}
    for name, fs in made.items():
        assert all(f.stat().st_size < 250 * 1024 * 1024 for f in fs), name
        print(name, [f.name for f in fs])
    return made


if __name__ == "__main__":
    main(sys.argv[1:])
