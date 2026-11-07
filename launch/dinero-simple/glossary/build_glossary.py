"""Write the Dinero Simple glossary page (sites/dinero-simple/content/pages/glosario.md) and its review checklist
(launch/dinero-simple/GLOSSARY_REVIEW.md) from terms.py.

Refuses a duplicate term, a link to a page that doesn't exist, an ITIN entry without the attorney line, or a
blog post that no entry links to (every article gets at least one internal link from the glossary).
The page carries schema.org DefinedTermSet data so search engines can read each term.

    python launch/dinero-simple/glossary/build_glossary.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SITE = ROOT / "sites" / "dinero-simple"
sys.path.insert(0, str(HERE))
from terms import ATTORNEY_LINE, GROUPS, T  # noqa: E402

PAGE = SITE / "content" / "pages" / "glosario.md"
REVIEW = HERE.parent / "GLOSSARY_REVIEW.md"
URL = json.loads((SITE / "site.json").read_text())["url"]


def slug_id(text: str) -> str:
    import unicodedata
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def exists(path: str) -> bool:
    """True when an internal path is a page this site builds."""
    p = path.strip("/")
    if p in ("free", "links", "products", "blog", ""):
        return True
    kind, _, slug = p.partition("/")
    if kind == "blog":
        return (SITE / "content" / "blog" / f"{slug}.md").exists()
    if kind == "products":
        return (SITE / "content" / "products" / f"{slug}.md").exists()
    return not slug and (SITE / "content" / "pages" / f"{kind}.md").exists()


def plain(md: str) -> str:
    return re.sub(r"[*_`]", "", md)


def check() -> None:
    names = [t[0] for t in T]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise SystemExit(f"duplicate terms: {sorted(dupes)}")
    groups = {g for g, _ in GROUPS}
    for term, _, group, text, links, _ in T:
        if group not in groups:
            raise SystemExit(f"{term}: unknown group {group}")
        if re.search(r"https?://", text):
            raise SystemExit(f"{term}: put links in the links list, not the definition")
        for _, path in links:
            if not exists(path):
                raise SystemExit(f"{term}: link to a page that doesn't exist: {path}")
        if "ITIN" in term and ATTORNEY_LINE not in text:
            raise SystemExit(f"{term}: an ITIN entry needs the attorney line")
    linked = {p for *_, links, _ in T for _, p in links}
    for post in sorted((SITE / "content" / "blog").glob("*.md")):
        if f"/blog/{post.stem}/" not in linked:
            raise SystemExit(f"no glossary entry links to /blog/{post.stem}/")


def page() -> str:
    check()
    jump = " · ".join(f"[{label}](#{slug_id(label)})" for _, label in GROUPS)
    out = [f"""---
title: Glosario de dinero en EE. UU.
description: "{len(T)} palabras de dinero de Estados Unidos explicadas en español sencillo: crédito, APR, W-2, ITIN, 401(k), remesas y más, con enlaces a guías gratis."
updated: 2026-11-07
---
En Estados Unidos tu banco, tu trabajo y el IRS te hablan en inglés y con siglas: APR, W-2, FICO, 401(k). Aquí están las {len(T)} que más vas a ver, explicadas en español sencillo y en dos o tres líneas. Cada una tiene un enlace a una guía gratis por si quieres saber más.

**Ir a:** {jump}

Información general, no asesoría financiera, fiscal ni legal. Las cifras son de 2026 y cambian cada año: revisa la fuente oficial antes de decidir."""]
    ld_terms = []
    for g, label in GROUPS:
        out.append(f"## {label}")
        for term, english, group, text, links, _ in T:
            if group != g:
                continue
            tid = slug_id(term)
            entry = [f"### {term}"]
            if english:
                entry.append(f"*En inglés: {english}.*")
            entry.append(text)
            if links:
                entry.append("**Lee más:** " + " · ".join(f"[{t}]({p})" for t, p in links))
            out.append("\n\n".join(entry))
            ld_terms.append({"@type": "DefinedTerm", "name": term, "description": plain(text),
                             "url": f"{URL}/glosario/#{tid}", **({"alternateName": english} if english else {})})
    out.append("## ¿Falta una palabra?\n\nSi viste una palabra de dinero que no entiendes y no está aquí, respóndenos a cualquier correo y la agregamos. Todo el sitio es gratis: mira [cómo ganamos dinero](/como-ganamos-dinero/).")
    ld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Glosario de dinero en EE. UU.",
          "inLanguage": "es", "url": f"{URL}/glosario/", "hasDefinedTerm": ld_terms}
    out.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    return "\n\n".join(out) + "\n"


def review() -> str:
    rows = ["# Glossary review checklist", "",
            f"`sites/dinero-simple/content/pages/glosario.md` is built from `launch/dinero-simple/glossary/terms.py` ({len(T)} terms). "
            "Edit `terms.py`, never the page, then run `python3 launch/dinero-simple/glossary/build_glossary.py`.", "",
            "- [ ] **Native-speaker review:** a fluent Spanish speaker reads every entry (machine-written).",
            "- [ ] **ATTORNEY REVIEW:** the ITIN and notario entries are read by a licensed immigration attorney or DOJ-accredited representative.",
            "- [ ] **Yearly update:** the 2026 figures (standard deduction, Child Tax Credit) are updated each January, with the paycheck calculator.",
            "", "## Facts to confirm", "", "| Term | Check |", "|---|---|"]
    for term, _, _, _, _, chk in T:
        for c in chk:
            rows.append(f"| {term} | {'**ATTORNEY REVIEW**' if c == 'ATTORNEY REVIEW' else c} |")
    return "\n".join(rows) + "\n"


def main() -> None:
    PAGE.write_text(page())
    REVIEW.write_text(review())
    print(f"wrote {PAGE.relative_to(ROOT)} ({len(T)} terms) and {REVIEW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
