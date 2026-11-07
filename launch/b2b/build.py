#!/usr/bin/env python3
"""Build branded, white-label packs for the B2B newsletter products.

Each product is a folder with product.json (labels, CTA, formats), issues.json (the content) and
brands/ (a fictional sample brand + a placeholders brand). Real clients go in <product>/clients/
(gitignored).

    python3 build.py                                    # every product: sample + placeholder packs, sales docs
    python3 build.py credit-union-alert                 # one product
    python3 build.py credit-union-alert --brand credit-union-alert/clients/acme.json [--issue ID]
    python3 build.py --no-images                        # HTML/text only

Output per product: <product>/out/<brand slug>/<unit>-<n>-<issue id>/ with
    email.html, email.txt    member/employee/patron email (inline CSS, 600 px)
    social.png, social.txt   1080x1080 image + caption + alt text
    lobby.png                1920x1080 lobby, breakroom or library screen slide
    poster.pdf               US letter flyer
    handout.pdf              large-print, full-content handout (products that list it)
    brief.txt                staff / manager / group-leader notes (not in the "essentials" tier)
    sources.md               every claim's source
plus <product>/out/<brand slug>.zip, out/sales-sheet.pdf, out/roi.pdf (if roi.html exists) and out/COMPLIANCE_NOTE.pdf.

Every {{TOKEN}} in a client pack must be filled, or the build fails. PNG/PDF use render.mjs
(Node + Playwright); without them the HTML pages are kept and images are skipped.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
SIZES = {"social": (1080, 1080), "lobby": (1920, 1080), "poster": (816, 1056), "handout": (816, 1056)}


# ---------------------------------------------------------------- text helpers

def fill(text: str, brand: dict) -> str:
    text = text.replace("{{ORG_NAME}}", brand["name"])
    for k, v in brand.get("tokens", {}).items():
        text = text.replace("{{" + k + "}}", v)
    return text


def md_html(text: str, color: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                  lambda m: f'<a href="{m.group(2)}" style="color:{color};text-decoration:underline">{m.group(1)}</a>', out)


def md_text(text: str) -> str:
    out = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"\1 (\2)", out)


def plain(text: str) -> str:
    out = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"\1", out)


def logo_html(brand: dict, size: int) -> str:
    if brand.get("logo"):
        return (f'<img src="{html.escape(brand["logo"])}" alt="{html.escape(brand["name"])}" '
                f'height="{size}" style="display:block;height:{size}px;width:auto;border:0">')
    return (f'<span style="display:inline-block;min-width:{size}px;height:{size}px;line-height:{size}px;'
            f'border-radius:{size // 5}px;background:{brand["accent"]};color:#111;font-weight:800;'
            f'font-size:{size * 0.38:.0f}px;text-align:center;padding:0 {size // 6}px;'
            f'font-family:Arial,Helvetica,sans-serif">{html.escape(brand["initials"])}</span>')


# ---------------------------------------------------------------- email

def email_html(issue: dict, brand: dict, prod: dict) -> str:
    c, a, L = brand["color"], brand["accent"], prod["labels"]
    f = lambda s: md_html(fill(s, brand), c)
    big = prod.get("large_print", False)
    fs = 18 if big else 16
    p = f'style="margin:0 0 14px;font-size:{fs}px;line-height:1.55;color:#1d232a"'
    h2 = f'style="margin:26px 0 10px;font-size:{fs + 3}px;line-height:1.3;color:{c}"'
    li = f'style="margin:0 0 10px;font-size:{fs}px;line-height:1.55;color:#1d232a"'
    explain = "".join(f"<p {p}>{f(x)}</p>" for x in issue["explain"])
    steps = "".join(f"<li {li}>{f(s)}</li>" for s in issue["steps"])
    hits = "".join(f"<li {li}>{f(s)}</li>" for s in issue["quick_hits"])
    sources = "".join(f'<li style="margin:0 0 4px"><a href="{s["url"]}" style="color:#4a5561">{html.escape(s["name"])}</a></li>'
                      for s in issue["sources"])
    footer = "".join(f'<p style="margin:0 0 4px">{html.escape(fill(x, brand))}</p>' for x in brand["footer_lines"])
    credit = f'<p style="margin:8px 0 0">{html.escape(brand["credit_line"])}</p>' if brand.get("credit_line") else ""
    promise = fill(brand.get("promise", ""), brand)
    promise_box = ""
    if issue.get("promise") and promise:
        promise_box = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:6px 0 18px">'
                       f'<tr><td style="background:#fff7e0;border-left:5px solid {a};padding:14px 16px;font-size:{fs}px;'
                       f'line-height:1.5;color:#1d232a"><strong>{html.escape(L["promise"])}:</strong> {html.escape(promise)}</td></tr></table>')
    example = ""
    if issue.get("example"):
        example = (f'<p style="margin:0 0 6px;font-size:14px;color:#4a5561">{f(issue["example_label"])}:</p>'
                   f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 16px"><tr>'
                   f'<td style="background:#f3f5f7;border-radius:6px;padding:14px 16px;font-size:{fs}px;line-height:1.5;'
                   f'color:#1d232a;font-style:italic">{f(issue["example"])}</td></tr></table>')
    hits_block = f'<h2 {h2}>{L["hits"]}</h2><ul style="margin:0 0 6px;padding-left:22px">{hits}</ul>' if hits else ""
    promise_foot = f'<p style="margin:0 0 6px">{html.escape(promise)}</p>' if promise else ""
    return f"""<!doctype html>
<html lang="{prod.get("lang", "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(fill(issue["subject"], brand))}</title></head>
<body style="margin:0;padding:0;background:#eef1f4">
<div style="display:none;max-height:0;overflow:hidden">{html.escape(fill(issue["preheader"], brand))}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef1f4"><tr><td align="center" style="padding:20px 10px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#ffffff;border-radius:8px;overflow:hidden;font-family:Arial,Helvetica,sans-serif">
<tr><td style="background:{c};padding:18px 24px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
  <td width="60" valign="middle">{logo_html(brand, 44)}</td>
  <td valign="middle" style="color:#ffffff;font-size:15px;font-weight:bold;padding-left:12px">{html.escape(brand["name"])}<br>
  <span style="font-weight:normal;font-size:13px;opacity:.9">{html.escape(fill(prod["series"], brand))}</span></td></tr></table>
</td></tr>
<tr><td style="padding:26px 24px 8px">
  <p style="margin:0 0 6px;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:{c};font-weight:bold">{html.escape(L["eyebrow"])}</p>
  <h1 style="margin:0 0 16px;font-size:{fs + 10}px;line-height:1.25;color:#111820">{f(issue["headline"])}</h1>
  {example}{explain}
  <h2 {h2}>{L["tell"]}</h2>
  <p {p}><strong>{f(issue["tell"])}</strong></p>
  {promise_box}
  <h2 {h2}>{L["steps"]}</h2>
  <ol style="margin:0 0 6px;padding-left:22px">{steps}</ol>
  {hits_block}
  <h2 {h2}>{L["job"]}</h2>
  <p {p}>{f(issue["job"])}</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:18px 0 8px"><tr>
  <td style="background:{c};border-radius:6px;padding:16px;color:#ffffff;font-size:{fs}px;line-height:1.5;text-align:center">
  {md_html(fill(prod["cta"], brand), "#ffffff")}</td></tr></table>
</td></tr>
<tr><td style="padding:12px 24px 22px;font-size:12px;line-height:1.5;color:#4a5561;border-top:1px solid #e3e7eb">
  {promise_foot}
  <p style="margin:0 0 6px">{html.escape(prod["disclaimer"])}</p>
  <p style="margin:0 0 4px">{html.escape(L.get("sources", "Sources"))}:</p><ul style="margin:0 0 10px;padding-left:18px">{sources}</ul>
  {footer}
  <p style="margin:8px 0 0">{html.escape(fill(brand.get("unsubscribe", ""), brand))}</p>
  {credit}
</td></tr>
</table></td></tr></table></body></html>
"""


def email_text(issue: dict, brand: dict, prod: dict) -> str:
    L = prod["labels"]
    f = lambda s: md_text(fill(s, brand))
    lines = [f"Subject: {f(issue['subject'])}", f"Preview: {f(issue['preheader'])}", "",
             f"{brand['name']} · {fill(prod['series'], brand)}", "",
             f"{L['eyebrow'].upper()}: {f(issue['headline'])}", ""]
    if issue.get("example"):
        lines += [f"{f(issue['example_label'])}:", f(issue["example"]), ""]
    lines += [f(x) + "\n" for x in issue["explain"]]
    lines += [L["tell"].upper(), f(issue["tell"]), ""]
    promise = fill(brand.get("promise", ""), brand)
    if issue.get("promise") and promise:
        lines += [f"{L['promise']}: {promise}", ""]
    lines += [L["steps"].upper()] + [f"{i}. {f(s)}" for i, s in enumerate(issue["steps"], 1)] + [""]
    if issue["quick_hits"]:
        lines += [L["hits"].upper()] + [f"- {f(s)}" for s in issue["quick_hits"]] + [""]
    lines += [L["job"].upper(), f(issue["job"]), "", md_text(fill(prod["cta"], brand)), "", "--"]
    if promise:
        lines.append(promise)
    lines += [prod["disclaimer"], L.get("sources", "Sources") + ":"] + [f"- {s['name']}: {s['url']}" for s in issue["sources"]]
    lines += [""] + [fill(x, brand) for x in brand["footer_lines"]]
    if brand.get("unsubscribe"):
        lines.append(fill(brand["unsubscribe"], brand))
    if brand.get("credit_line"):
        lines.append(brand["credit_line"])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- visuals

def visual_html(issue: dict, brand: dict, prod: dict, kind: str) -> str:
    c, a, L = brand["color"], brand["accent"], prod["labels"]
    w, h = SIZES[kind]
    lob = issue["lobby"]
    foot = md_html(fill(prod["visual_footer"], brand), c).replace(f'style="color:{c};text-decoration:underline"', "")
    if brand.get("credit_line"):
        foot += f'<div style="margin-top:6px;font-size:.8em;font-weight:700">{html.escape(fill(brand["credit_line"], brand))}</div>'
    if kind == "handout":
        return handout_html(issue, brand, prod, foot)
    s = {"social": 1.0, "lobby": 1.05, "poster": None}[kind]
    head = 72 if kind == "poster" else 86 * s if kind == "social" else 92 * s
    bul = 32 if kind == "poster" else 44 * s if kind == "social" else 46 * s
    pad = {"social": 80, "lobby": 110, "poster": 56}[kind]
    bullets = "".join(f'<li><span class="dot"></span>{html.escape(fill(b, brand))}</li>' for b in lob["bullets"])
    extra = ""
    if kind == "poster":
        steps = "".join(f"<li>{html.escape(plain(fill(x, brand)))}</li>" for x in issue["steps"])
        extra = f'<div class="steps"><h3>{html.escape(L["steps"])}</h3><ol>{steps}</ol></div>'
    size_css = f"width:{w}px;height:{h}px;" if kind != "poster" else "width:8.5in;height:10.98in;"
    page_css = "@page{size:8.5in 11in;margin:0}" if kind == "poster" else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{page_css}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#fff}}
.card{{{size_css}display:flex;flex-direction:column;background:#ffffff;font-family:Arial,Helvetica,sans-serif;color:#111820;overflow:hidden}}
.top{{background:{c};color:#fff;padding:{pad*0.45:.0f}px {pad}px;display:flex;align-items:center;gap:{pad*0.3:.0f}px}}
.top .name{{font-size:{bul*0.8:.0f}px;font-weight:700}}
.body{{flex:1 1 auto;min-height:0;padding:{pad*0.8:.0f}px {pad}px;display:flex;flex-direction:column;justify-content:center}}
.kicker{{display:inline-block;align-self:flex-start;background:{a};color:#111;font-weight:800;text-transform:uppercase;letter-spacing:.06em;font-size:{bul*0.62:.0f}px;padding:{bul*0.18:.0f}px {bul*0.4:.0f}px;border-radius:6px;margin-bottom:{pad*0.4:.0f}px}}
h1{{font-size:{head:.0f}px;line-height:1.08;letter-spacing:-.01em;margin-bottom:{pad*0.5:.0f}px}}
ul{{list-style:none}}
li{{font-size:{bul:.0f}px;line-height:1.3;margin-bottom:{bul*0.45:.0f}px;display:flex;gap:{bul*0.4:.0f}px;align-items:baseline}}
.dot{{flex:none;width:{bul*0.42:.0f}px;height:{bul*0.42:.0f}px;border-radius:50%;background:{c};display:inline-block}}
.steps{{margin-top:22px;border-top:3px solid {a};padding-top:18px}}
.steps h3{{font-size:28px;color:{c};margin-bottom:10px}}
.steps ol{{padding-left:28px}}
.steps ol li{{display:list-item;font-size:22px;line-height:1.4;margin-bottom:10px}}
.foot{{flex:none;background:#f3f5f7;padding:{pad*0.4:.0f}px {pad}px;font-size:{bul*0.72:.0f}px;line-height:1.3;border-top:6px solid {a}}}
.foot strong{{color:{c}}}
.small{{font-size:{bul*0.42:.0f}px;color:#4a5561;margin-top:6px}}
</style></head><body><div class="card">
<div class="top">{logo_html(brand, int(bul*1.6))}<div class="name">{html.escape(brand["name"])}</div></div>
<div class="body"><span class="kicker">{html.escape(fill(lob["kicker"], brand))}</span>
<h1>{html.escape(fill(lob["headline"], brand))}</h1><ul>{bullets}</ul>{extra}</div>
<div class="foot">{foot}
{'<div class="small">' + html.escape(prod["disclaimer"]) + '</div>' if kind == 'poster' else ''}</div>
</div></body></html>"""


def handout_html(issue: dict, brand: dict, prod: dict, foot: str) -> str:
    """Large-print, full-content handout (18 pt body), US letter, may run to 2 pages."""
    c, a, L = brand["color"], brand["accent"], prod["labels"]
    f = lambda s: md_html(fill(s, brand), c)
    example = (f'<p class="lab">{f(issue["example_label"])}:</p><div class="ex">{f(issue["example"])}</div>'
               if issue.get("example") else "")
    explain = "".join(f"<p>{f(x)}</p>" for x in issue["explain"])
    steps = "".join(f"<li>{f(s)}</li>" for s in issue["steps"])
    hits = "".join(f"<li>{f(s)}</li>" for s in issue["quick_hits"])
    hits_block = f"<h2>{L['hits']}</h2><ul>{hits}</ul>" if hits else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:8.5in 11in;margin:.6in .7in}}
*{{box-sizing:border-box}}
body{{font-family:Arial,Helvetica,sans-serif;color:#111820;font-size:18pt;line-height:1.4;margin:0}}
.top{{display:flex;align-items:center;gap:14px;border-bottom:5px solid {a};padding-bottom:10px;margin-bottom:14px}}
.top .name{{font-size:15pt;font-weight:700;color:{c}}}
.top .series{{font-size:12pt;color:#4a5561}}
h1{{font-size:30pt;line-height:1.1;margin:6px 0 12px}}
.kicker{{display:inline-block;background:{a};color:#111;font-weight:800;text-transform:uppercase;letter-spacing:.06em;font-size:12pt;padding:4px 10px;border-radius:5px}}
h2{{font-size:21pt;color:{c};margin:18px 0 6px;page-break-after:avoid}}
p{{margin:0 0 10px}}
.lab{{font-size:13pt;color:#4a5561;margin:0 0 4px}}
.ex{{background:#f3f5f7;border-radius:6px;padding:10px 14px;font-style:italic;margin-bottom:12px}}
ol,ul{{margin:0 0 6px;padding-left:30px;break-inside:avoid}} li{{margin-bottom:8px;break-inside:avoid}}
.tell{{font-weight:700;border-left:6px solid {a};padding:6px 0 6px 14px;background:#fff7e0}}
.foot{{margin-top:18px;background:#f3f5f7;border-top:5px solid {a};padding:10px 14px;font-size:16pt}}
.foot strong{{color:{c}}}
.small{{font-size:10pt;color:#4a5561;margin-top:10px}}
a{{color:{c}}}
</style></head><body>
<div class="top">{logo_html(brand, 48)}<div><div class="name">{html.escape(brand["name"])}</div>
<div class="series">{html.escape(fill(prod["series"], brand))}</div></div></div>
<span class="kicker">{html.escape(fill(issue["lobby"]["kicker"], brand))}</span>
<h1>{f(issue["headline"])}</h1>
{example}{explain}
<h2>{L["tell"]}</h2><p class="tell">{f(issue["tell"])}</p>
<h2>{L["steps"]}</h2><ol>{steps}</ol>
{hits_block}
<h2>{L["job"]}</h2><p>{f(issue["job"])}</p>
<div class="foot">{foot}</div>
<p class="small">{html.escape(prod["disclaimer"])} {html.escape(prod["labels"].get("sources", "Sources"))}: {"; ".join(html.escape(s["name"]) for s in issue["sources"])}.</p>
</body></html>"""


# ---------------------------------------------------------------- rendering

def have_renderer() -> bool:
    if not shutil.which("node"):
        return False
    return subprocess.run(["node", "-e", "require('playwright')"], cwd=ROOT, capture_output=True).returncode == 0


def render_all(jobs: list[dict]) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(jobs, fh)
    try:
        subprocess.run(["node", str(ROOT / "render.mjs"), fh.name], cwd=ROOT, check=True, timeout=900)
    finally:
        Path(fh.name).unlink(missing_ok=True)


# ---------------------------------------------------------------- master markdown

def master_md(issue: dict, prod: dict) -> str:
    L, lob, soc = prod["labels"], issue["lobby"], issue["social"]
    toks = ", ".join(f"`{t}`" for t in prod["tokens"])
    out = [f"# {prod['unit'].capitalize()} {issue['n']}: {issue['topic']}", "",
           f"- Send date: **{issue['send_date']}** · delivered to the client by **{issue['deliver_by']}**",
           f"- Built from: {issue['source']}", f"- Brand slots: {toks}, plus logo and brand colors", "",
           "## Email version", "", f"**Subject:** {issue['subject']}  ", f"**Preview text:** {issue['preheader']}", "",
           f"**{L['eyebrow']}**", "", f"### {issue['headline']}", ""]
    if issue.get("example"):
        out += [f"*{issue['example_label']}:* {issue['example']}", ""]
    out += [x + "\n" for x in issue["explain"]]
    out += [f"**{L['tell']}**", "", f"**{issue['tell']}**", ""]
    if issue.get("promise"):
        out += [f"> **{L['promise']}:** {prod.get('promise_token', '')}", ""]
    out += [f"**{L['steps']}**", ""] + [f"{i}. {s}" for i, s in enumerate(issue["steps"], 1)] + [""]
    if issue["quick_hits"]:
        out += [f"**{L['hits']}**", ""] + [f"- {s}" for s in issue["quick_hits"]] + [""]
    out += [f"**{L['job']}**", "", issue["job"], "", f"> {prod['cta']}", "",
            f"*Footer:* {prod['disclaimer']} Sources (below), plus the client's footer lines.", "",
            f"## {L['screen']}", "", f"- Kicker: **{lob['kicker']}**", f"- Headline: **{lob['headline']}**"]
    out += [f"- {b}" for b in lob["bullets"]] + [f"- Footer: {prod['visual_footer']}", ""]
    if "handout" in prod["visuals"]:
        out += ["The large-print handout carries the full email text at 18 pt.", ""]
    out += [f"## {L['post']}", "", f"**Caption:** {soc['caption']}", "", f"**Image alt text:** {soc['alt']}", "",
            f"## {L['brief']}", ""] + [f"- **{k}:** {v}" for k, v in issue["brief"].items()]
    out += ["", "## Sources", ""] + [f"- [{s['name']}]({s['url']})" for s in issue["sources"]]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- build

def build(pdir: Path, prod: dict, brand_path: Path, issues: list[dict], allow_tokens: bool, images: bool) -> list[dict]:
    brand = json.loads(brand_path.read_text())
    out = pdir / "out"
    root = out / brand["slug"]
    if root.exists():
        shutil.rmtree(root)
    essentials = brand.get("tier", "").lower() == "essentials"
    L = prod["labels"]
    jobs: list[dict] = []
    for issue in issues:
        d = root / f"{prod['unit']}-{issue['n']}-{issue['id']}"
        d.mkdir(parents=True)
        (d / "email.html").write_text(email_html(issue, brand, prod))
        (d / "email.txt").write_text(email_text(issue, brand, prod))
        (d / "social.txt").write_text(
            f"CAPTION ({L['post']})\n{fill(issue['social']['caption'], brand)}\n\nIMAGE ALT TEXT\n"
            f"{fill(issue['social']['alt'], brand)}\n\nPost on or after {issue['send_date']}.\n")
        if not essentials:
            brief = "\n".join(f"{k}: {fill(v, brand)}" for k, v in issue["brief"].items())
            (d / "brief.txt").write_text(f"{L['brief'].upper()}: {issue['topic']} (goes out {issue['send_date']})\n\n"
                                         f"{brief}\n\nThe one thing to repeat: {plain(fill(issue['tell'], brand))}\n")
        (d / "sources.md").write_text(f"# Sources: {issue['topic']}\n\n"
                                      + "\n".join(f"- [{s['name']}]({s['url']})" for s in issue["sources"]) + "\n")
        kinds = [k for k in prod["visuals"] if not (essentials and k in prod.get("not_in_essentials", []))]
        for kind in kinds:
            page = d / f"{kind}.html"
            page.write_text(visual_html(issue, brand, prod, kind))
            if images:
                w, h = SIZES[kind]
                target = d / (f"{kind}.pdf" if kind in ("poster", "handout") else f"{kind}.png")
                jobs.append({"html": str(page), "out": str(target), "w": w, "h": h, "page": kind in ("poster", "handout")})
        if not allow_tokens:
            for p in d.iterdir():
                if p.suffix in {".html", ".txt", ".md"}:
                    left = TOKEN_RE.findall(p.read_text())
                    if left:
                        sys.exit(f"error: unfilled tokens {sorted(set(left))} in {p}")
    return [dict(j, _root=str(root), _out=str(out), _slug=brand["slug"]) for j in jobs] or \
        [{"_root": str(root), "_out": str(out), "_slug": brand["slug"], "skip": True}]


def finish(packs: list[list[dict]]) -> None:
    """Render all images in one browser session, delete the source HTML, zip each pack."""
    jobs = [j for pack in packs for j in pack if not j.get("skip")]
    if jobs:
        render_all([{k: j[k] for k in ("html", "out", "w", "h")} for j in jobs])
        for j in jobs:
            Path(j["html"]).unlink(missing_ok=True)
    for pack in packs:
        root, out, slug = Path(pack[0]["_root"]), Path(pack[0]["_out"]), pack[0]["_slug"]
        zpath = out / f"{slug}.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(root.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(out))
        print(f"built {root.relative_to(ROOT)} -> {zpath.relative_to(ROOT)}")


NOTE_CSS = ("<style>@page{size:Letter;margin:.7in}body{font-family:Arial,Helvetica,sans-serif;font-size:11pt;"
            "line-height:1.45;color:#17202a}h1{font-size:20pt;color:#1F5C8B}h2{font-size:14pt;color:#1F5C8B;"
            "margin-top:18pt}h3{font-size:12pt}table{border-collapse:collapse;width:100%}td,th{border:1px solid #dfe4e9;"
            "padding:5px;vertical-align:top;font-size:10pt}a{color:#1F5C8B}</style>")


FORM_CSS = "<style>th:nth-child(3),td:nth-child(3){width:42%}td{height:30px}</style>"


def md_to_pdf_job(md: Path, out_pdf: Path, extra_css: str = "") -> dict:
    body = subprocess.run(["pandoc", str(md), "-f", "gfm", "-t", "html"],
                          check=True, capture_output=True, text=True).stdout
    page = out_pdf.with_suffix(".html")
    page.write_text(f"<!doctype html><html><head><meta charset='utf-8'>{NOTE_CSS}{extra_css}</head><body>{body}</body></html>")
    return {"html": str(page), "out": str(out_pdf), "w": 816, "h": 1056}


def sales_doc_jobs(pdir: Path) -> list[dict]:
    """Sales and onboarding documents: <name>.html pages and a few Markdown files, rendered to out/ as PDFs."""
    out = pdir / "out"
    out.mkdir(exist_ok=True)
    jobs = []
    pages = [pdir / f"{n}.html" for n in ("sales-sheet", "roi")]
    pages += [p for sub in ("onboarding", "broker") for p in sorted((pdir / sub).glob("*.html"))]
    for page in pages:
        if page.exists():
            dest = out / page.relative_to(pdir).with_suffix(".pdf")
            dest.parent.mkdir(parents=True, exist_ok=True)
            jobs.append({"html": str(page), "out": str(dest), "w": 816, "h": 1056})
    if shutil.which("pandoc"):
        for md in [pdir / "COMPLIANCE_NOTE.md", pdir / "onboarding" / "BRAND_INTAKE.md"]:
            if md.exists():
                dest = out / md.relative_to(pdir).with_suffix(".pdf")
                dest.parent.mkdir(parents=True, exist_ok=True)
                jobs.append(md_to_pdf_job(md, dest, FORM_CSS if md.name == "BRAND_INTAKE.md" else ""))
    return jobs


def demo_packet(pdir: Path, count: int = 3) -> None:
    """A pitch attachment: the first 3 sample issues (email HTML + email PDF + print files) for the fictional
    example brand, plus the sales sheet, in out/demo-packet/, zipped, and one combined PDF (sales sheet + emails)."""
    out = pdir / "out"
    slug = json.loads((pdir / "brands/example.json").read_text())["slug"]
    issue_dirs = sorted((out / slug).iterdir(), key=lambda d: int(d.name.split("-")[1]))[:count]
    demo = out / "demo-packet"
    if demo.exists():
        shutil.rmtree(demo)
    demo.mkdir()
    jobs = []
    for d in issue_dirs:
        dest = demo / d.name
        dest.mkdir()
        for name in ("email.html", "email.txt", "social.png", "poster.pdf", "handout.pdf", "lobby.png"):
            if (d / name).exists():
                shutil.copy(d / name, dest / name)
        # the PDF keeps the email's 600 px layout, centred on a letter page
        page = dest / "_email_print.html"
        page.write_text((d / "email.html").read_text().replace(
            "</head>", "<style>@page{size:8.5in 11in;margin:.4in}body,table[role=presentation]{background:transparent!important}</style></head>", 1))
        jobs.append({"html": str(page), "out": str(dest / "email.pdf"), "w": 816, "h": 1056})
    render_all(jobs)
    for j in jobs:
        Path(j["html"]).unlink(missing_ok=True)
    for name in ("sales-sheet.pdf", "roi.pdf"):
        if (out / name).exists():
            shutil.copy(out / name, demo / name)
    pdfs = [str(demo / "sales-sheet.pdf")] if (demo / "sales-sheet.pdf").exists() else []
    pdfs += [str(demo / d.name / "email.pdf") for d in issue_dirs]
    if shutil.which("pdfunite") and len(pdfs) > 1:
        subprocess.run(["pdfunite", *pdfs, str(out / "demo-packet.pdf")], check=True)
    zpath = out / "demo-packet.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(demo.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(out))
    print(f"built {zpath.relative_to(ROOT)} and demo-packet.pdf ({len(issue_dirs)} issues)")


def products() -> list[Path]:
    """Each product folder, plus language editions in <product>/<lang>/ (e.g. credit-union-alert/es)."""
    return sorted(p.parent for p in [*ROOT.glob("*/product.json"), *ROOT.glob("*/[a-z][a-z]/product.json")])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("product", nargs="?", help="product folder name (default: all)")
    ap.add_argument("--brand", type=Path, help="client brand JSON (needs a product)")
    ap.add_argument("--issue", help="only this issue id")
    ap.add_argument("--placeholders", action="store_true", help="allow {{TOKENS}} in output")
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    pdirs = [ROOT / a.product] if a.product else products()
    if a.brand and not a.product:
        sys.exit("--brand needs a product, e.g. build.py credit-union-alert --brand ...")
    images = not a.no_images and have_renderer()
    if not a.no_images and not images:
        print("warning: node + playwright not found; skipping PNG/PDF (HTML pages kept)", file=sys.stderr)
    packs, extra, demos = [], [], []
    for pdir in pdirs:
        prod = json.loads((pdir / "product.json").read_text())
        issues = json.loads((pdir / "issues.json").read_text())["issues"]
        if a.issue:
            issues = [i for i in issues if i["id"] == a.issue]
            if not issues:
                sys.exit(f"no issue {a.issue} in {pdir.name}")
        (pdir / "samples").mkdir(exist_ok=True)
        for i in issues:
            (pdir / "samples" / f"{prod['unit']}-{i['n']}.md").write_text(master_md(i, prod))
        if a.brand:
            packs.append(build(pdir, prod, a.brand, issues, a.placeholders, images))
        else:
            packs.append(build(pdir, prod, pdir / "brands/example.json", issues, False, images))
            packs.append(build(pdir, prod, pdir / "brands/placeholders.json", issues, True, images))
            for other in sorted((pdir / "brands").glob("*.json")):
                if other.stem not in ("example", "placeholders"):
                    packs.append(build(pdir, prod, other, issues, False, images))
            if images:
                extra += sales_doc_jobs(pdir)
                demos.append(pdir)
    finish(packs)
    if extra:
        render_all(extra)
    for j in extra:
        print(f"built {Path(j['out']).relative_to(ROOT)}")
    for pdir in demos:
        demo_packet(pdir)


if __name__ == "__main__":
    main()
