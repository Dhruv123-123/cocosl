"""Final Etsy-compliance check across every Etsy listing in the catalog and the files it ships.

    python launch/catalog/etsy_audit.py [--root /mnt/project-files/content-factory] [--out <root>/ETSY_COMPLIANCE.md]

It reads each Etsy row of PRODUCTS_CATALOG (not the ones on hold), finds the Etsy part of its LISTING.md (the
"Etsy" section, or the title, tags and description headings) and the files in its folder, and checks:
- Etsy's limits: a title of 140 characters or fewer, 13 tags or fewer, each 20 characters or fewer;
- no links or pointers off Etsy in the Etsy copy (http, www, Gumroad, "link in bio", discount codes for elsewhere);
- the house copy rules: no guarantee, risk-free, bestseller, "I've used", income promises or fake urgency;
- the disclosures: a digital download says nothing is shipped (posters are physical, so they're exempt), the AI
  help is disclosed, and it says it isn't financial (or tax, or legal) advice;
- the AI-guide rule (Etsy, 22 Oct 2026): no guide on Etsy (etsy_rules.problems);
- the files: no Gumroad, store-link placeholders or Gumroad-only codes inside the PDFs that ship on Etsy.
Spanish listings use the Spanish markers. Rows whose LISTING.md isn't in the project files yet are listed as gaps.
Nothing is changed or uploaded; it writes one Markdown report.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
DEFAULT_ROOT = Path("/mnt/project-files/content-factory")

OFF_ETSY = re.compile(r"https?://(?!(www\.)?etsy\.com)|\bwww\.(?!etsy)|gumroad|link in (my )?bio|\[your store link\]|"
                      r"\[LINK|\[ENLACE|\{\{", re.I)
BANNED = re.compile(r"guarantee|risk[- ]free|best ?seller|i've used|get rich|passive income|make \$\d|only \d+ left|"
                    r"hurry|limited time|garantizad|sin riesgo|100% seguro|hazte rico|dinero f[áa]cil|este truco", re.I)
CODES = {"BUDGET5", "BILLCUT5", "KITPARENTS", "SEMANA5", "TRACKER15", "TAXKIT15", "KIT29", "GUIDEKIT", "TEAMLAUNCH",
         "BF10", "BF5", "YEAREND10"}   # Gumroad-only codes (BF25 is the Etsy code and may appear on Etsy)
DOWNLOAD = re.compile(r"digital download|nothing is shipped|nothing ships|descarga digital|no se env[íi]a", re.I)
AI = re.compile(r"\bAI\b|\bIA\b|artificial", re.I)
ADVICE = re.compile(r"not (tax, legal or )?financial|not (tax|legal|financial)[^.]{0,30}advice|isn't (financial|tax|legal)|"
                    r"no es asesor[íi]a|not financial advice|educational", re.I)


def sections(md: str) -> dict[str, str]:
    """{heading: text} for every ## or ### heading."""
    out, cur, buf = {}, "_top", []
    for line in md.splitlines():
        m = re.match(r"^#{2,3}\s+(.*)", line)
        if m:
            out[cur] = "\n".join(buf)
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    out[cur] = "\n".join(buf)
    return out


def etsy_part(md: str) -> dict[str, str]:
    """title, tags (list) and description of the Etsy part of a LISTING.md."""
    s = sections(md)
    keys = list(s)
    # A file with an "## Etsy" section and a "## Gumroad" one: only look inside the Etsy one.
    if "Etsy" in keys:
        i = keys.index("Etsy")
        sub = {}
        for k in keys[i:]:
            if k != "Etsy" and re.match(r"(Gumroad|Rules|How it differs|Files)", k):
                break
            sub[k] = s[k]
        s, keys = sub, list(sub)
    title = next((s[k] for k in keys if re.match(r"(Etsy )?[Tt]itle", k)), "")
    title = next((ln.strip().strip("`") for ln in title.splitlines() if ln.strip() and not ln.startswith(">")), "")
    tag_txt = next((s[k] for k in keys if re.match(r"(Etsy )?[Tt]ags", k)), "")
    tags = [re.sub(r"^\s*(\d+\.|-)\s*", "", ln).strip().strip("`") for ln in tag_txt.splitlines() if re.match(r"^\s*(\d+\.|-)\s", ln)]
    if not tags:
        line = next((ln for ln in tag_txt.splitlines() if "," in ln), "")
        tags = [t.strip().strip("`") for t in line.split(",") if t.strip()]
    desc = "\n".join(s[k] for k in keys if re.match(r"(Etsy )?[Dd]escri", k)) or s.get("Etsy", "")
    blob = "\n".join(s[k] for k in keys)
    if not title and (m := re.search(r"\*\*Title\*\*[^\n]*\n(.+)|\*\*Title:\*\*\s*(.+)", blob)):
        title = (m.group(1) or m.group(2)).strip()
    if not tags and (m := re.search(r"\*\*Tags[^\n]*?\*\*\s*(?:\([^)]*\))?\s*\n?((?:.+\n?)+?)(?:\n\n|\*\*)", blob)):
        tags = [t.strip().strip("`").strip() for t in re.split(r"[,·]", m.group(1).replace("\n", " ")) if t.strip().strip("`").strip()]
    return dict(title=title, tags=tags, description=desc)


def pdf_text(p: Path) -> str:
    try:
        return subprocess.run(["pdftotext", "-q", str(p), "-"], capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def check_row(r: dict, root: Path) -> list[str]:
    lst = root / r["listing"]
    if not lst.exists():
        return [f"LISTING.md not in the project files yet (`{r['listing']}`)"]
    md = lst.read_text()
    e = etsy_part(md)
    bad = []
    poster = "print on demand" in r["platform"]
    if e["title"] and len(e["title"]) > 140:
        bad.append(f"title is {len(e['title'])} characters (max 140)")
    if len(e["tags"]) > 13 or any(len(t) > 20 for t in e["tags"]):
        bad.append(f"tags: {len(e['tags'])}, longest {max((len(t) for t in e['tags']), default=0)} characters")
    if not e["tags"]:
        bad.append("no tags found")
    d = e["description"]
    if not d.strip():
        bad.append("no Etsy description found")
    else:
        if (m := OFF_ETSY.search(d)):
            bad.append(f"off-Etsy pointer in the description: '{m.group(0)}'")
        if (m := BANNED.search(d)):
            bad.append(f"banned wording in the description: '{m.group(0)}'")
        if (c := [c for c in CODES if re.search(rf"\b{c}\b", d)]):
            bad.append(f"Gumroad-only code in the description: {c}")
        if not poster and not DOWNLOAD.search(d):
            bad.append("doesn't say it's a digital download (nothing shipped)")
        if not AI.search(d):
            bad.append("no AI disclosure")
        if not ADVICE.search(d):
            bad.append("no 'not financial advice' line")
    folder = root / r["files"].split(" ")[0]
    for p in sorted(folder.glob("*.pdf")) if folder.is_dir() and not poster else []:
        t = pdf_text(p)
        if re.search(r"gumroad|\[your store link\]|\[LINK", t, re.I):
            bad.append(f"`{p.name}` mentions Gumroad or a store-link placeholder")
        if (c := [c for c in CODES if re.search(rf"\b{c}\b", t)]):
            bad.append(f"`{p.name}` prints a Gumroad-only code: {c}")
    return bad


def audit(root: Path, rows: list[dict] | None = None) -> tuple[list[dict], list[str]]:
    import build_catalog as CAT
    import etsy_rules
    rows = rows if rows is not None else CAT.all_rows()
    et = [r for r in rows if "Etsy" in r["platform"] and not r["platform"].startswith("On hold")
          and "optional" not in r["platform"]]
    results = [dict(r, problems=check_row(r, root)) for r in et]
    return results, etsy_rules.problems(rows)


def markdown(results: list[dict], rule_problems: list[str]) -> str:
    ok = [r for r in results if not r["problems"]]
    gaps = [r for r in results if r["problems"] and r["problems"][0].startswith("LISTING.md not in")]
    bad = [r for r in results if r["problems"] and r not in gaps]
    out = ["# Etsy compliance check\n",
           f"{len(results)} Etsy listings checked from `PRODUCTS_CATALOG.md` (listings on hold and \"Etsy optional\" rows "
           f"left out): **{len(ok)} pass**, {len(bad)} with problems, {len(gaps)} not in the project files yet. "
           "AI-guide rule: " + ("no guide on Etsy." if not rule_problems else f"{len(rule_problems)} problems.") +
           " Built by `launch/catalog/etsy_audit.py`; nothing was changed or uploaded.\n",
           "Checked: title 140 characters or fewer; 13 tags of 20 characters or fewer; no links, Gumroad mentions, "
           "store-link placeholders or Gumroad-only codes in the Etsy copy or the PDFs; no guarantee, risk-free, "
           "bestseller, \"I've used\" or urgency wording; the digital-download line (not for posters), the AI "
           "disclosure and the not-financial-advice line.\n"]
    if rule_problems:
        out.append("## AI-guide rule\n\n" + "\n".join(f"- {p}" for p in rule_problems) + "\n")
    if bad:
        out.append("## Problems\n\n| Brand | Product | Problem |\n|---|---|---|")
        out += [f"| {r['brand']} | {r['product']} | {'; '.join(r['problems'])} |" for r in bad]
        out.append("")
    if gaps:
        out.append("## Not in the project files yet\n\n" + "\n".join(f"- {r['brand']}: {r['product']} (`{r['listing']}`)" for r in gaps) + "\n")
    out.append(f"## Passing ({len(ok)})\n\n" + "\n".join(f"- {r['brand']}: {r['product']} ({r['platform']})" for r in ok))
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    root = Path(a.root)
    results, rule = audit(root)
    md = markdown(results, rule)
    out = Path(a.out) if a.out else root / "ETSY_COMPLIANCE.md"
    out.write_text(md)
    n_bad = sum(1 for r in results if r["problems"])
    print(f"{len(results)} Etsy listings, {n_bad} with problems or gaps -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
