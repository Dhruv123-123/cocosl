#!/usr/bin/env python3
"""Assemble the B2B landing page into dist/, ready to drop on Netlify.

    cd launch/b2b && python3 build.py && python3 site/build_site.py

Copies index.html, config.js and netlify.toml, four sample images, each offer's 3-issue demo pack, sales
sheet, ROI sheet and compliance note into dist/, and writes one live sample issue page per offer at
dist/samples/<offer>/. Fails if a download is missing (run ../build.py first).
"""
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
B2B = SITE.parent
DIST = SITE / "dist"

FILES = {
    "downloads/credit-union-sample-pack.zip": "credit-union-alert/out/demo-packet.zip",
    "downloads/credit-union-sales-sheet.pdf": "credit-union-alert/out/sales-sheet.pdf",
    "downloads/credit-union-roi.pdf": "credit-union-alert/out/roi.pdf",
    "downloads/credit-union-compliance-note.pdf": "credit-union-alert/out/COMPLIANCE_NOTE.pdf",
    "downloads/employer-sample-pack.zip": "employer-wellness/out/demo-packet.zip",
    "downloads/employer-sales-sheet.pdf": "employer-wellness/out/sales-sheet.pdf",
    "downloads/employer-compliance-note.pdf": "employer-wellness/out/COMPLIANCE_NOTE.pdf",
    "downloads/scam-watch-sample-pack.zip": "community-scam-watch/out/demo-packet.zip",
    "downloads/scam-watch-sales-sheet.pdf": "community-scam-watch/out/sales-sheet.pdf",
    "downloads/scam-watch-compliance-note.pdf": "community-scam-watch/out/COMPLIANCE_NOTE.pdf",
    "downloads/accounting-firm-sample-pack.zip": "freelancer-client-letter/out/demo-packet.zip",
    "downloads/accounting-firm-sales-sheet.pdf": "freelancer-client-letter/out/sales-sheet.pdf",
    "downloads/schools-sample-pack.zip": "schools/out/demo-packet.zip",
    "downloads/schools-sales-sheet.pdf": "schools/out/sales-sheet.pdf",
    "img/fc-social.png": "freelancer-client-letter/out/sample-ledger/month-1-2027-01/social.png",
    "img/cu-social.png": "credit-union-alert/out/sample-community-cu/week-1-2027-01-a/social.png",
    "img/hr-lobby.png": "employer-wellness/out/sample-outfitters/month-4-2027-04/lobby.png",
    "img/sw-lobby.png": "community-scam-watch/out/sample-county-library/month-1-2027-01/lobby.png",
}

# One live sample issue per offer, served at /samples/<slug>/ (the email exactly as a client's readers get it,
# with a banner saying it's a sample for a fictional organization). Link these in follow-ups.
SAMPLE_PAGES = {
    "credit-union": ("credit-union-alert/out/sample-community-cu/week-1-2027-01-a/email.html",
                     "credit unions", "Sample Community Credit Union", "cu"),
    "employer": ("employer-wellness/out/sample-outfitters/month-1-2027-01/email.html",
                 "employers", "Sample Outfitters Co.", "hr"),
    "scam-watch": ("community-scam-watch/out/sample-county-library/month-1-2027-01/email.html",
                   "libraries and senior centers", "Sample County Library", "sw"),
    "accounting-firm": ("freelancer-client-letter/out/sample-ledger/month-1-2027-01/email.html",
                        "accounting firms", "Sample Ledger & Tax Co.", "fc"),
    "schools": ("schools/out/sample-valley-high/week-1-2027-w02/email.html",
                "high schools and colleges", "Sample Valley High School", "sc"),
}
BANNER = (
    '<div style="background:#111827;color:#fff;font:15px/1.5 -apple-system,Segoe UI,Roboto,Arial,sans-serif;'
    'padding:14px 16px;text-align:center">'
    '<strong>Sample issue for {who}.</strong> It\'s made for a fictional organization, {org}, so that name and its '
    'phone number and website are made up. The sources are real. Your version carries your own name, logo and contact details. '
    '<a href="../../#request" data-offer="{key}" style="color:#fde68a;font-weight:700">Get a free sample pack</a>'
    ' · <a href="../../" style="color:#fde68a">All offers</a></div>'
)


def sample_page(src: Path, who: str, org: str, key: str) -> str:
    html = src.read_text()
    html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex">\n'
                        '<meta name="viewport" content="width=device-width, initial-scale=1">', 1)
    i = html.index("<body")
    j = html.index(">", i) + 1
    return html[:j] + BANNER.format(who=who, org=org, key=key) + html[j:]


def main() -> None:
    missing = [src for src in list(FILES.values()) + [v[0] for v in SAMPLE_PAGES.values()]
               if not (B2B / src).exists()]
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
    for slug, (src, who, org, key) in SAMPLE_PAGES.items():
        out = DIST / "samples" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(sample_page(B2B / src, who, org, key))
    if "REPLACE_ME" in (SITE / "config.js").read_text():
        print("note: config.js still has the REPLACE_ME email; the request button won't reach anyone yet")
    size = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file()) / 1e6
    print(f"built {DIST.relative_to(B2B)} ({size:.1f} MB)")


if __name__ == "__main__":
    main()
