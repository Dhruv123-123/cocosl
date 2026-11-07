#!/usr/bin/env python3
"""Assemble the B2B landing page into dist/, ready to drop on Netlify.

    cd launch/b2b && python3 build.py && python3 site/build_site.py

Copies index.html, config.js and netlify.toml, four sample images and every sample pack, sales
sheet, ROI sheet and compliance note into dist/. Fails if a download is missing (run ../build.py first).
"""
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
B2B = SITE.parent
DIST = SITE / "dist"

FILES = {
    "downloads/credit-union-sample-pack.zip": "credit-union-alert/out/sample-community-cu.zip",
    "downloads/credit-union-sales-sheet.pdf": "credit-union-alert/out/sales-sheet.pdf",
    "downloads/credit-union-roi.pdf": "credit-union-alert/out/roi.pdf",
    "downloads/credit-union-compliance-note.pdf": "credit-union-alert/out/COMPLIANCE_NOTE.pdf",
    "downloads/employer-sample-pack.zip": "employer-wellness/out/sample-outfitters.zip",
    "downloads/employer-sales-sheet.pdf": "employer-wellness/out/sales-sheet.pdf",
    "downloads/employer-compliance-note.pdf": "employer-wellness/out/COMPLIANCE_NOTE.pdf",
    "downloads/scam-watch-sample-pack.zip": "community-scam-watch/out/sample-county-library.zip",
    "downloads/scam-watch-sales-sheet.pdf": "community-scam-watch/out/sales-sheet.pdf",
    "downloads/scam-watch-compliance-note.pdf": "community-scam-watch/out/COMPLIANCE_NOTE.pdf",
    "downloads/accounting-firm-sample-pack.zip": "freelancer-client-letter/out/sample-ledger.zip",
    "downloads/accounting-firm-sales-sheet.pdf": "freelancer-client-letter/out/sales-sheet.pdf",
    "img/fc-social.png": "freelancer-client-letter/out/sample-ledger/month-1-2027-01/social.png",
    "img/cu-social.png": "credit-union-alert/out/sample-community-cu/week-1-2027-01-a/social.png",
    "img/hr-lobby.png": "employer-wellness/out/sample-outfitters/month-4-2027-04/lobby.png",
    "img/sw-lobby.png": "community-scam-watch/out/sample-county-library/month-1-2027-01/lobby.png",
}


def main() -> None:
    missing = [src for src in FILES.values() if not (B2B / src).exists()]
    if missing:
        sys.exit("missing (run python3 build.py in launch/b2b first):\n  " + "\n  ".join(missing))
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for name in ("index.html", "config.js", "netlify.toml"):
        shutil.copy(SITE / name, DIST / name)
    for dest, src in FILES.items():
        (DIST / dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(B2B / src, DIST / dest)
    if "REPLACE_ME" in (SITE / "config.js").read_text():
        print("note: config.js still has the REPLACE_ME email; the request button won't reach anyone yet")
    size = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file()) / 1e6
    print(f"built {DIST.relative_to(B2B)} ({size:.1f} MB)")


if __name__ == "__main__":
    main()
