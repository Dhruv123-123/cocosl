"""Build the "Crédito sin Seguro Social" lead magnet from credito/guia.py, through impuestos/build_guia.py's renderer:

  launch/dinero-simple/GUIA_CREDITO_SIN_SS.md                 the guide (review copy)
  launch/dinero-simple/REVIEW_CHECKLIST_CREDITO_SIN_SS_GUIA.md   native-speaker, credit-expert and attorney sign-off
  sites/dinero-simple/content/pages/credito-sin-seguro-social.md the guide as a site page (/credito-sin-seguro-social/)
  credito/dist/guia-credito-sin-seguro-social.html            printable page; --pdf also writes the PDF and copies it
                                                              to sites/dinero-simple/static/downloads/

    python launch/dinero-simple/credito/build_credito.py [--pdf]
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
ROOT = DS.parents[1]
SITE = ROOT / "sites" / "dinero-simple"
DIST = HERE / "dist"
PDF_NAME = "credito-sin-seguro-social.pdf"
UPDATED = "2026-11-07"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def renderer():
    """impuestos/build_guia.py with this folder's guia.py in place of the tax guide's."""
    saved = sys.modules.get("guia")
    sys.modules["guia"] = _load("guia", HERE / "guia.py")
    try:
        return _load("build_guia_credito", DS / "impuestos" / "build_guia.py")
    finally:
        if saved is None:
            sys.modules.pop("guia", None)
        else:
            sys.modules["guia"] = saved


def review_doc(b) -> str:
    rows = [f"# Review checklist: {b.TITLE} (lead magnet)", "",
            "Nothing in `GUIA_CREDITO_SIN_SS.md`, its PDF or the `/credito-sin-seguro-social/` page is shared until every box "
            "is ticked. Until then, keep the page out of the build with `hold` in `sites/dinero-simple/site.json`. Edit "
            "`credito/guia.py`, never the outputs, then run `python3 launch/dinero-simple/credito/build_credito.py --pdf`.", "",
            "- [ ] **Native-speaker review** of the whole guide (machine-written Spanish).",
            "- [ ] **CREDIT EXPERT REVIEW:** a HUD-approved housing counselor, NFCC counselor or credit union lender checks every credit fact below.",
            f"- [ ] **ATTORNEY REVIEW:** a licensed immigration attorney or DOJ-accredited representative reads the {sum(map(b.needs_attorney, b.SECTIONS))} sections marked below (every section that mentions the ITIN).",
            "- [ ] **Ask two local credit unions** whether they open accounts, secured cards and credit-builder loans with an ITIN, and note what ID they take.", ""]
    for n, s in enumerate(b.SECTIONS, 1):
        rows.append(f"### {n}. {s['title']}" + (" · **ATTORNEY REVIEW**" if b.needs_attorney(s) else ""))
        rows += [f"- [ ] {c}" for c in s["check"] if c != "ATTORNEY REVIEW"]
        rows.append("")
    return "\n".join(rows)


def site_page(b) -> str:
    body = b.markdown_doc().split("\n\n", 2)[2]  # drop the H1 and subtitle: the page template has its own title
    head = (f"---\ntitle: \"{b.TITLE}\"\ndescription: \"{b.SUBTITLE}. Guía gratis en español, con lista para imprimir.\"\n"
            f"updated: {UPDATED}\n---\n")
    return head + f"**[Descarga la guía en PDF, gratis](/downloads/{PDF_NAME})**\n\n" + body


def main() -> None:
    b = renderer()
    (DS / "GUIA_CREDITO_SIN_SS.md").write_text(b.markdown_doc())
    (DS / "REVIEW_CHECKLIST_CREDITO_SIN_SS_GUIA.md").write_text(review_doc(b))
    (SITE / "content" / "pages" / "credito-sin-seguro-social.md").write_text(site_page(b))
    DIST.mkdir(exist_ok=True)
    page = DIST / "guia-credito-sin-seguro-social.html"
    page.write_text(b.html_doc())
    print("wrote GUIA_CREDITO_SIN_SS.md, its review checklist, the site page and " + str(page.relative_to(ROOT)))
    if "--pdf" in sys.argv:
        pdf = DIST / PDF_NAME
        js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
              "await p.goto('file://" + str(page) + "');await p.pdf({path:'" + str(pdf) + "',"
              "format:'Letter',printBackground:true,preferCSSPageSize:true});await b.close();})();")
        subprocess.run(["node", "-e", js], check=True, env={**__import__("os").environ,
                                                              "NODE_PATH": "/opt/node22/lib/node_modules"})
        shutil.copy(pdf, SITE / "static" / "downloads" / PDF_NAME)
        print(f"wrote {pdf.name} and copied it to the site's downloads")


if __name__ == "__main__":
    main()
