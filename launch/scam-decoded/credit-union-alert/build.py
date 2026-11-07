#!/usr/bin/env python3
"""Build a branded Weekly Scam Alert pack for one credit union.

    python3 build.py                                   # sample pack (fictional CU) + placeholder master
    python3 build.py --brand clients/acme-cu.json      # one client, all issues
    python3 build.py --brand clients/acme-cu.json --issue 2027-01-a
    python3 build.py --no-images                       # HTML/text only (no Chromium needed)

Output: out/<brand slug>/<week>-<issue id>/ with
    email.html        paste into the CU's email platform (inline CSS, 600 px, table layout)
    email.txt         plain-text part
    social.png        1080x1080 post image   + social.txt (caption + alt text)
    lobby.png         1920x1080 lobby screen / digital signage slide
    poster.pdf        US letter poster for the branch
    staff-brief.txt   5-minute front-line huddle note (Standard and Plus tiers)
Brand files may set "tier": "essentials" to leave out poster.pdf and staff-brief.txt.
    sources.md        every claim's source, for the CU's compliance review
and out/<brand slug>.zip with all of it.

Also writes samples/week-N.md, the master copy with every brand slot visible as a token.

Only the Python standard library is needed. PNG/PDF images use render.mjs (Node + Playwright);
without them the build keeps the HTML pages and skips images with a warning.
The build fails if any {{TOKEN}} is left unfilled in a client pack.
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

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")

DISCLAIMER = ("This alert is general information to help you spot scams. It isn't legal, tax or "
              "financial advice.")


# ---------------------------------------------------------------- helpers

def fill(text: str, brand: dict) -> str:
    return (text.replace("{{CU_NAME}}", brand["name"])
                .replace("{{CU_SHORT}}", brand["short"])
                .replace("{{CU_PHONE}}", brand["phone"])
                .replace("{{CU_WEBSITE}}", brand["website"]))


def md_inline_html(text: str, color: str) -> str:
    """**bold** and [text](url) to HTML, everything else escaped."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                 lambda m: f'<a href="{m.group(2)}" style="color:{color};text-decoration:underline">{m.group(1)}</a>',
                 out)
    return out


def md_inline_text(text: str) -> str:
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

def email_html(issue: dict, brand: dict) -> str:
    c, a = brand["color"], brand["accent"]
    f = lambda s: md_inline_html(fill(s, brand), c)
    p = 'style="margin:0 0 14px;font-size:16px;line-height:1.55;color:#1d232a"'
    h2 = f'style="margin:26px 0 10px;font-size:19px;line-height:1.3;color:{c}"'
    explain = "".join(f"<p {p}>{f(x)}</p>" for x in issue["explain"])
    steps = "".join(f'<li style="margin:0 0 10px;font-size:16px;line-height:1.55;color:#1d232a">{f(s)}</li>'
                    for s in issue["steps"])
    hits = "".join(f'<li style="margin:0 0 10px;font-size:16px;line-height:1.55;color:#1d232a">{f(s)}</li>'
                   for s in issue["quick_hits"])
    sources = "".join(f'<li style="margin:0 0 4px"><a href="{s["url"]}" style="color:#4a5561">{html.escape(s["name"])}</a></li>'
                      for s in issue["sources"])
    footer = "".join(f'<p style="margin:0 0 4px">{html.escape(fill(x, brand))}</p>' for x in brand["footer_lines"])
    credit = (f'<p style="margin:8px 0 0">{html.escape(brand["credit_line"])}</p>' if brand.get("credit_line") else "")
    never = html.escape(fill(brand["never_ask"], brand))
    never_box = ""
    if issue.get("never_ask"):
        never_box = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:6px 0 18px">'
                     f'<tr><td style="background:#fff7e0;border-left:5px solid {a};padding:14px 16px;font-size:16px;'
                     f'line-height:1.5;color:#1d232a"><strong>Our promise:</strong> {never}</td></tr></table>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(fill(issue["subject"], brand))}</title></head>
<body style="margin:0;padding:0;background:#eef1f4">
<div style="display:none;max-height:0;overflow:hidden">{html.escape(fill(issue["preheader"], brand))}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef1f4"><tr><td align="center" style="padding:20px 10px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#ffffff;border-radius:8px;overflow:hidden;font-family:Arial,Helvetica,sans-serif">
<tr><td style="background:{c};padding:18px 24px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
  <td width="60" valign="middle">{logo_html(brand, 44)}</td>
  <td valign="middle" style="color:#ffffff;font-size:15px;font-weight:bold;padding-left:12px">{html.escape(brand["name"])}<br>
  <span style="font-weight:normal;font-size:13px;opacity:.9">Weekly Scam Alert</span></td></tr></table>
</td></tr>
<tr><td style="padding:26px 24px 8px">
  <p style="margin:0 0 6px;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:{c};font-weight:bold">This week's scam</p>
  <h1 style="margin:0 0 16px;font-size:26px;line-height:1.25;color:#111820">{f(issue["headline"])}</h1>
  <p style="margin:0 0 6px;font-size:14px;color:#4a5561">{f(issue["example_label"])}:</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 16px"><tr>
  <td style="background:#f3f5f7;border-radius:6px;padding:14px 16px;font-size:16px;line-height:1.5;color:#1d232a;font-style:italic">{f(issue["example"])}</td></tr></table>
  {explain}
  <h2 {h2}>The tell</h2>
  <p {p}><strong>{f(issue["tell"])}</strong></p>
  {never_box}
  <h2 {h2}>What to do</h2>
  <ol style="margin:0 0 6px;padding-left:22px">{steps}</ol>
  <h2 {h2}>Quick hits</h2>
  <ul style="margin:0 0 6px;padding-left:22px">{hits}</ul>
  <h2 {h2}>Your 5-minute job this week</h2>
  <p {p}>{f(issue["five_minute_job"])}</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:18px 0 8px"><tr>
  <td style="background:{c};border-radius:6px;padding:16px;color:#ffffff;font-size:16px;line-height:1.5;text-align:center">
  Not sure about a call, text or email? Call us at <strong style="color:#ffffff">{html.escape(brand["phone"])}</strong>
  or the number on the back of your card.</td></tr></table>
</td></tr>
<tr><td style="padding:12px 24px 22px;font-size:12px;line-height:1.5;color:#4a5561;border-top:1px solid #e3e7eb">
  <p style="margin:0 0 6px">{never}</p>
  <p style="margin:0 0 6px">{DISCLAIMER}</p>
  <p style="margin:0 0 4px">Sources:</p><ul style="margin:0 0 10px;padding-left:18px">{sources}</ul>
  {footer}
  <p style="margin:8px 0 0">{html.escape(brand["unsubscribe"])}</p>
  {credit}
</td></tr>
</table></td></tr></table></body></html>
"""


def email_text(issue: dict, brand: dict) -> str:
    f = lambda s: md_inline_text(fill(s, brand))
    lines = [f"Subject: {f(issue['subject'])}", f"Preview: {f(issue['preheader'])}", "",
             f"{brand['name']} · Weekly Scam Alert", "",
             f"THIS WEEK'S SCAM: {f(issue['headline'])}", "",
             f"{f(issue['example_label'])}:", f(issue["example"]), ""]
    lines += [f(x) + "\n" for x in issue["explain"]]
    lines += ["THE TELL", f(issue["tell"]), ""]
    if issue.get("never_ask"):
        lines += [f"Our promise: {fill(brand['never_ask'], brand)}", ""]
    lines += ["WHAT TO DO"] + [f"{i}. {f(s)}" for i, s in enumerate(issue["steps"], 1)] + [""]
    lines += ["QUICK HITS"] + [f"- {f(s)}" for s in issue["quick_hits"]] + [""]
    lines += ["YOUR 5-MINUTE JOB THIS WEEK", f(issue["five_minute_job"]), ""]
    lines += [f"Not sure about a call, text or email? Call us at {brand['phone']} or the number on the back of your card.", "",
              "--", fill(brand["never_ask"], brand), DISCLAIMER, "Sources:"]
    lines += [f"- {s['name']}: {s['url']}" for s in issue["sources"]]
    lines += [""] + [fill(x, brand) for x in brand["footer_lines"]] + [brand["unsubscribe"]]
    if brand.get("credit_line"):
        lines.append(brand["credit_line"])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- visuals

def visual_html(issue: dict, brand: dict, w: int, h: int, kind: str) -> str:
    c, a = brand["color"], brand["accent"]
    lob = issue["lobby"]
    s = w / 1080 if kind != "poster" else 1.0
    if kind == "lobby":
        s = h / 1080 * 1.05
    head_size = {"social": 86, "lobby": 92, "poster": 72}[kind] * (s if kind != "poster" else 1)
    bullet_size = {"social": 44, "lobby": 46, "poster": 32}[kind] * (s if kind != "poster" else 1)
    pad = {"social": 80, "lobby": 110, "poster": 56}[kind]
    bullets = "".join(f'<li><span class="dot"></span>{html.escape(fill(b, brand))}</li>' for b in lob["bullets"])
    extra = ""
    if kind == "poster":
        steps = "".join(f"<li>{html.escape(plain(fill(x, brand)))}</li>" for x in issue["steps"])
        extra = f'<div class="steps"><h3>What to do</h3><ol>{steps}</ol></div>'
    size_css = f"width:{w}px;height:{h}px;" if kind != "poster" else "width:8.5in;height:11in;"
    page_css = "@page{size:8.5in 11in;margin:0}" if kind == "poster" else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{page_css}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#fff}}
.card{{{size_css}display:flex;flex-direction:column;background:#ffffff;font-family:Arial,Helvetica,sans-serif;color:#111820;overflow:hidden}}
.top{{background:{c};color:#fff;padding:{pad*0.45:.0f}px {pad}px;display:flex;align-items:center;gap:{pad*0.3:.0f}px}}
.top .name{{font-size:{bullet_size*0.8:.0f}px;font-weight:700}}
.body{{flex:1;padding:{pad*0.8:.0f}px {pad}px;display:flex;flex-direction:column;justify-content:center}}
.kicker{{display:inline-block;align-self:flex-start;background:{a};color:#111;font-weight:800;text-transform:uppercase;letter-spacing:.06em;font-size:{bullet_size*0.62:.0f}px;padding:{bullet_size*0.18:.0f}px {bullet_size*0.4:.0f}px;border-radius:6px;margin-bottom:{pad*0.4:.0f}px}}
h1{{font-size:{head_size:.0f}px;line-height:1.08;letter-spacing:-.01em;margin-bottom:{pad*0.5:.0f}px}}
ul{{list-style:none}}
li{{font-size:{bullet_size:.0f}px;line-height:1.3;margin-bottom:{bullet_size*0.45:.0f}px;display:flex;gap:{bullet_size*0.4:.0f}px;align-items:baseline}}
.dot{{flex:none;width:{bullet_size*0.42:.0f}px;height:{bullet_size*0.42:.0f}px;border-radius:50%;background:{c};display:inline-block}}
.steps{{margin-top:22px;border-top:3px solid {a};padding-top:18px}}
.steps h3{{font-size:28px;color:{c};margin-bottom:10px}}
.steps ol{{padding-left:28px}}
.steps ol li{{display:list-item;font-size:22px;line-height:1.4;margin-bottom:10px}}
.foot{{background:#f3f5f7;padding:{pad*0.4:.0f}px {pad}px;font-size:{bullet_size*0.72:.0f}px;line-height:1.3;border-top:6px solid {a}}}
.foot strong{{color:{c}}}
.small{{font-size:{bullet_size*0.42:.0f}px;color:#4a5561;margin-top:6px}}
</style></head><body><div class="card">
<div class="top">{logo_html(brand, int(bullet_size*1.6))}<div class="name">{html.escape(brand["name"])}</div></div>
<div class="body"><span class="kicker">{html.escape(fill(lob["kicker"], brand))}</span>
<h1>{html.escape(fill(lob["headline"], brand))}</h1><ul>{bullets}</ul>{extra}</div>
<div class="foot">Not sure? Call us at <strong>{html.escape(brand["phone"])}</strong> or the number on your card.
{'<div class="small">' + html.escape(DISCLAIMER) + '</div>' if kind == 'poster' else ''}</div>
</div></body></html>"""


def have_renderer() -> bool:
    if not shutil.which("node"):
        return False
    r = subprocess.run(["node", "-e", "require('playwright')"], cwd=HERE, capture_output=True)
    return r.returncode == 0


def render_all(jobs: list[dict]) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(jobs, fh)
    try:
        subprocess.run(["node", str(HERE / "render.mjs"), fh.name], cwd=HERE, check=True, timeout=600)
    finally:
        Path(fh.name).unlink(missing_ok=True)


# ---------------------------------------------------------------- master markdown

def master_md(issue: dict) -> str:
    lob, soc, sb = issue["lobby"], issue["social"], issue["staff_brief"]
    L = [f"# Week {issue['week']}: {issue['topic']}", "",
         f"- Member send date: **{issue['member_send_date']}** · delivered to the credit union by **{issue['deliver_to_cu_by']}** (7-day review window)",
         f"- Built from: {issue['source_issue']}",
         "- Brand slots: `{{CU_NAME}}`, `{{CU_SHORT}}`, `{{CU_PHONE}}`, `{{CU_NEVER_ASK}}`, `{{CU_ADDRESS}}`, `{{CU_INSURANCE_STATEMENT}}`, `{{UNSUBSCRIBE_LINK}}`, plus logo and brand colour",
         "", "## Email version", "",
         f"**Subject:** {issue['subject']}  ", f"**Preview text:** {issue['preheader']}", "",
         "**This week's scam**", "", f"### {issue['headline']}", "",
         f"*{issue['example_label']}:* {issue['example']}", ""]
    L += [x + "\n" for x in issue["explain"]]
    L += ["**The tell**", "", f"**{issue['tell']}**", ""]
    if issue.get("never_ask"):
        L += ["> **Our promise:** {{CU_NEVER_ASK}}", ""]
    L += ["**What to do**", ""] + [f"{i}. {s}" for i, s in enumerate(issue["steps"], 1)] + [""]
    L += ["**Quick hits**", ""] + [f"- {s}" for s in issue["quick_hits"]] + [""]
    L += ["**Your 5-minute job this week**", "", issue["five_minute_job"], "",
          "> Not sure about a call, text or email? Call us at {{CU_PHONE}} or the number on the back of your card.", "",
          "*Footer:* {{CU_NEVER_ASK}} " + DISCLAIMER + " Sources (below). {{CU_ADDRESS}} · {{CU_INSURANCE_STATEMENT}} · {{UNSUBSCRIBE_LINK}}", "",
          "## Lobby screen and poster", "",
          f"- Kicker: **{lob['kicker']}**", f"- Headline: **{lob['headline']}**"]
    L += [f"- {b}" for b in lob["bullets"]]
    L += ["- Footer: Not sure? Call us at {{CU_PHONE}} or the number on your card.",
          "- Poster adds the three \"What to do\" steps and the disclaimer.", "",
          "## Social post (Facebook, Instagram, LinkedIn, Nextdoor)", "",
          f"**Caption:** {soc['caption']}", "", f"**Image alt text:** {soc['alt']}", "",
          "## Staff huddle brief (Standard and Plus)", "",
          f"- **Members may ask:** {sb['members_may_ask']}", f"- **What to say:** {sb['say']}",
          f"- **Escalate:** {sb['escalate']}", "",
          "## Sources", ""]
    L += [f"- [{s['name']}]({s['url']})" for s in issue["sources"]]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- main

def build(brand_path: Path, issues: list[dict], placeholders: bool, images: bool) -> Path:
    brand = json.loads(brand_path.read_text())
    root = OUT / brand["slug"]
    if root.exists():
        shutil.rmtree(root)
    render = images and have_renderer()
    if images and not render:
        print("warning: node + playwright not found; skipping PNG/PDF (HTML pages kept)", file=sys.stderr)
    jobs: list[dict] = []
    for issue in issues:
        d = root / f"week-{issue['week']}-{issue['id']}"
        d.mkdir(parents=True)
        (d / "email.html").write_text(email_html(issue, brand))
        (d / "email.txt").write_text(email_text(issue, brand))
        (d / "social.txt").write_text(
            f"CAPTION\n{fill(issue['social']['caption'], brand)}\n\nIMAGE ALT TEXT\n{fill(issue['social']['alt'], brand)}\n"
            f"\nPost on or after {issue['member_send_date']}. Don't add links to anything but your own site or a .gov page.\n")
        essentials = brand.get("tier", "standard").lower() == "essentials"
        sb = issue["staff_brief"]
        if not essentials:
            (d / "staff-brief.txt").write_text(
            f"STAFF HUDDLE: {issue['topic']} (members get this alert {issue['member_send_date']})\n\n"
            f"Members may ask: {fill(sb['members_may_ask'], brand)}\nWhat to say: {fill(sb['say'], brand)}\n"
            f"Escalate: {fill(sb['escalate'], brand)}\n\nThe rule to repeat: {plain(fill(issue['tell'], brand))}\n"
            f"\nThis follows your own procedures; it doesn't replace them.\n")
        (d / "sources.md").write_text(f"# Sources: {issue['topic']}\n\nContent reviewed against these on the date in issues.json.\n\n"
                                      + "\n".join(f"- [{s['name']}]({s['url']})" for s in issue["sources"]) + "\n")
        kinds = [("social", 1080, 1080), ("lobby", 1920, 1080)] + ([] if essentials else [("poster", 816, 1056)])
        for kind, w, h in kinds:
            page = d / f"{kind}.html"
            page.write_text(visual_html(issue, brand, w, h, kind))
            if render:
                target = d / ("poster.pdf" if kind == "poster" else f"{kind}.png")
                jobs.append({"html": str(page), "out": str(target), "w": w, "h": h})
        if not placeholders:
            for p in d.iterdir():
                if p.suffix in {".html", ".txt", ".md"}:
                    left = TOKEN_RE.findall(p.read_text())
                    if left:
                        sys.exit(f"error: unfilled tokens {sorted(set(left))} in {p}")
    if jobs:
        render_all(jobs)
        for j in jobs:
            Path(j["html"]).unlink()
    zpath = OUT / f"{brand['slug']}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(OUT))
    print(f"built {root.relative_to(HERE)} ({len(issues)} issues) -> {zpath.relative_to(HERE)}")
    return root


NOTE_CSS = ("<style>@page{size:Letter;margin:.7in}body{font-family:Arial,Helvetica,sans-serif;font-size:11pt;"
            "line-height:1.45;color:#17202a}h1{font-size:20pt;color:#1F5C8B}h2{font-size:14pt;color:#1F5C8B;"
            "margin-top:18pt}h3{font-size:12pt}table{border-collapse:collapse;width:100%}td,th{border:1px solid #dfe4e9;"
            "padding:5px;vertical-align:top;font-size:10pt}a{color:#1F5C8B}</style>")


def build_sales_docs() -> None:
    """out/sales-sheet.pdf, and out/COMPLIANCE_NOTE.pdf when pandoc is installed."""
    if not have_renderer():
        return
    OUT.mkdir(exist_ok=True)
    jobs = [{"html": str(HERE / "sales-sheet.html"), "out": str(OUT / "sales-sheet.pdf"), "w": 816, "h": 1056}]
    if shutil.which("pandoc"):
        body = subprocess.run(["pandoc", str(HERE / "COMPLIANCE_NOTE.md"), "-f", "gfm", "-t", "html"],
                              check=True, capture_output=True, text=True).stdout
        note = OUT / "COMPLIANCE_NOTE.html"
        note.write_text(f"<!doctype html><html><head><meta charset='utf-8'>{NOTE_CSS}</head><body>{body}</body></html>")
        jobs.append({"html": str(note), "out": str(OUT / "COMPLIANCE_NOTE.pdf"), "w": 816, "h": 1056})
    render_all(jobs)
    print("built out/sales-sheet.pdf" + (" and out/COMPLIANCE_NOTE.pdf" if len(jobs) > 1 else ""))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand", type=Path, help="brand JSON (default: sample pack + placeholder master)")
    ap.add_argument("--issue", help="only this issue id")
    ap.add_argument("--placeholders", action="store_true", help="allow {{TOKENS}} in output")
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    issues = json.loads((HERE / "issues.json").read_text())["issues"]
    if a.issue:
        issues = [i for i in issues if i["id"] == a.issue]
        if not issues:
            sys.exit(f"no issue {a.issue}")
    samples = HERE / "samples"
    samples.mkdir(exist_ok=True)
    for i in issues:
        (samples / f"week-{i['week']}.md").write_text(master_md(i))
    if a.brand:
        build(a.brand, issues, a.placeholders, not a.no_images)
    else:
        build(HERE / "brands/example.json", issues, False, not a.no_images)
        build(HERE / "brands/placeholders.json", issues, True, not a.no_images)
        if not a.no_images:
            build_sales_docs()


if __name__ == "__main__":
    main()
