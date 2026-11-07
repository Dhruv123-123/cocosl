"""Build the free family tax-season guide from guia.py:
  launch/dinero-simple/GUIA_IMPUESTOS_2027.md          the guide, for review and for pasting into the site or a doc
  launch/dinero-simple/REVIEW_CHECKLIST_IMPUESTOS_2027.md  native-speaker, tax-pro and attorney sign-off per section
  launch/dinero-simple/impuestos/dist/guia-impuestos-2027.html  printable page (Letter); --pdf also writes the PDF

Every section that mentions the ITIN is marked ATTORNEY REVIEW in the checklist (like flag_attorney for posts).
Refuses an attorney=True section without the attorney note or an ATTORNEY REVIEW check, a section with no facts
to check, and any bare outside link (only irs.gov/es style mentions and our own site paths).

    python launch/dinero-simple/impuestos/build_guia.py [--pdf]
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
ROOT = DS.parents[1]
sys.path.insert(0, str(HERE))
import guia as G  # noqa: E402
from guia import ATTORNEY_NOTE, CHECKLIST_1PAGE, DEADLINE, INTRO, SECTIONS, SUBTITLE, TITLE  # noqa: E402

# credito/build_credito.py renders another guide of the same shape through these functions; its FOOTER replaces this one.
FOOTER = getattr(G, "FOOTER", "*Dinero Simple · Información general, no es asesoría fiscal ni legal. Hecho con ayuda de IA y "
                 "revisado por personas. Cifras para el año fiscal 2026; confírmalas en irs.gov/es antes de declarar.*")

SITE_URL = json.loads((ROOT / "sites" / "dinero-simple" / "site.json").read_text())["url"]
DIST = HERE / "dist"


def check() -> None:
    ids = [s["id"] for s in SECTIONS]
    assert len(ids) == len(set(ids)), "duplicate section ids"
    for s in SECTIONS:
        if s["attorney"] and ATTORNEY_NOTE not in s["body"]:
            raise SystemExit(f"{s['id']}: attorney section without the attorney note")
        if s["attorney"] and not any(c.startswith("ATTORNEY REVIEW") for c in s["check"]):
            raise SystemExit(f"{s['id']}: attorney section without an ATTORNEY REVIEW check")
        if re.search(r"https?://", s["body"]):
            raise SystemExit(f"{s['id']}: no bare links in the guide body")
        if not s["check"]:
            raise SystemExit(f"{s['id']}: list the facts to check")


def needs_attorney(s: dict) -> bool:
    return s["attorney"] or "ITIN" in s["title"] + s["body"]


def anchor(text: str) -> str:
    import unicodedata
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def markdown_doc() -> str:
    check()
    heads = [f"{n}. {s['title']}" for n, s in enumerate(SECTIONS, 1)]
    parts = [f"# {TITLE}", f"*{SUBTITLE}*", INTRO, "**Contenido:** " + " · ".join(f"[{h}](#{anchor(h)})" for h in heads)]
    for h, s in zip(heads, SECTIONS):
        parts.append(f"## {h}\n\n" + s["body"].strip())
    parts.append("## Tu lista de una página\n\n" + "\n".join(f"- [ ] {c}" for c in CHECKLIST_1PAGE))
    parts.append("---\n" + FOOTER)
    return "\n\n".join(parts) + "\n"


def review_doc() -> str:
    rows = [f"# Review checklist: {TITLE}", "",
            "Nothing in `GUIA_IMPUESTOS_2027.md` or its PDF is shared, posted or linked until every box below is ticked. "
            "Edit `impuestos/guia.py`, never the outputs, then run `python3 launch/dinero-simple/impuestos/build_guia.py --pdf`.", "",
            "- [ ] **Native-speaker review** of the whole guide (machine-written Spanish).",
            "- [ ] **Tax professional** (enrolled agent, CPA or VITA site coordinator) checks every figure and rule for tax year 2026.",
            f"- [ ] **ATTORNEY REVIEW:** a licensed immigration attorney or DOJ-accredited representative reads the {sum(map(needs_attorney, SECTIONS))} sections marked below (every section that mentions the ITIN), the week the guide goes out.",
            "- [ ] **Re-check in January 2027:** IRS opening day, the VITA income limit and any 2026-year guidance on the 2025 law.", ""]
    for n, s in enumerate(SECTIONS, 1):
        rows.append(f"### {n}. {s['title']}" + (" · **ATTORNEY REVIEW**" if needs_attorney(s) else ""))
        rows += [f"- [ ] {c}" for c in s["check"] if c != "ATTORNEY REVIEW"]
        rows.append("")
    return "\n".join(rows)


def html_doc() -> str:
    sys.path.insert(0, str(ROOT / "sites" / "dinero-simple"))
    import build as site  # the Dinero Simple site's Markdown subset
    site.CFG.setdefault("url", SITE_URL)
    site.CFG.setdefault("base_path", "")
    site.CFG["_absolute_links"] = False
    body = markdown_doc().replace("](/", f"]({SITE_URL}/")
    out, _ = site.markdown(body)
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>{html.escape(TITLE)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
@page {{ size: Letter; margin: 0.7in 0.75in; }}
:root {{ --ink:#14213d; --green:#11706a; --coral:#ff7a59; --line:#e2d8c4; --paper:#fffdf8; --tint:#e2f4f1; }}
body {{ font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; color: var(--ink);
       background: var(--paper); font-size: 10.5pt; line-height: 1.5; max-width: 7.2in; margin: 0 auto; padding: 16px; }}
h1 {{ font-size: 24pt; line-height: 1.1; margin: 0 0 4px; }}
h1 + p em {{ color: #4a5468; font-size: 12pt; }}
h2 {{ font-size: 15pt; margin: 22px 0 6px; padding-top: 8px; border-top: 3px solid var(--coral); break-after: avoid; }}
table {{ border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9.5pt; break-inside: avoid; }}
th, td {{ border: 1px solid var(--line); padding: 5px 7px; text-align: left; vertical-align: top; }}
th {{ background: var(--tint); }}
ul.checks {{ list-style: none; padding-left: 0; }}
ul.checks li::before {{ content: "☐ "; color: var(--green); font-weight: 700; }}
a {{ color: var(--green); }}
hr {{ border: 0; border-top: 1px solid var(--line); margin: 18px 0 8px; }}
.table {{ overflow-x: auto; }}
</style></head><body>
{out}
</body></html>
"""


def main() -> None:
    (DS / "GUIA_IMPUESTOS_2027.md").write_text(markdown_doc())
    (DS / "REVIEW_CHECKLIST_IMPUESTOS_2027.md").write_text(review_doc())
    DIST.mkdir(exist_ok=True)
    page = DIST / "guia-impuestos-2027.html"
    page.write_text(html_doc())
    print(f"wrote GUIA_IMPUESTOS_2027.md, REVIEW_CHECKLIST_IMPUESTOS_2027.md and {page.relative_to(ROOT)}")
    if "--pdf" in sys.argv:
        pdf = DIST / "Guia-Temporada-de-Impuestos-2027.pdf"
        js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
              "await p.goto('file://" + str(page) + "');await p.pdf({path:'" + str(pdf) + "',"
              "format:'Letter',printBackground:true,preferCSSPageSize:true});await b.close();})();")
        subprocess.run(["node", "-e", js], check=True, env={**__import__("os").environ,
                                                              "NODE_PATH": "/opt/node22/lib/node_modules"})
        print("wrote dist/Guia-Temporada-de-Impuestos-2027.pdf")


if __name__ == "__main__":
    main()
