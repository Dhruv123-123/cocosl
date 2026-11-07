"""Build the Scam Decoded funnel site: landing page with the free checklist, thanks/download page,
kit sales page, legal pages, and the 7-email sequence.

Same conventions as the Money Made Simple site (site/ in PR #4): Python standard library only,
settings in site.json, emails as Markdown with front matter in content/emails/, the email provider
switch (netlify | mailerlite | kit | buttondown | factory) with EMAIL_PROVIDER / EMAIL_FORM_ACTION /
SITE_URL env overrides, and a build of public/ that is committed for drag-and-drop deploys.

    python3 sites/scam-decoded/build.py            # writes sites/scam-decoded/public/
    python3 sites/scam-decoded/build.py --serve    # preview on http://localhost:8080/

Placeholders: links containing REPLACE_ME (the scam checker URL until PR #8's app is deployed) are
hidden on the site and reported by the build; emails fall back to the site's /checker/ page.
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
OUT = Path(os.environ.get("SITE_OUT") or ROOT / "public")
esc = html.escape
CFG: dict = {}
WARNINGS: list[str] = []


# --------------------------------------------------------------------- config
def load_config() -> dict:
    cfg = json.loads((ROOT / "site.json").read_text())
    url = os.environ.get("SITE_URL") or os.environ.get("URL") or cfg["url"]
    cfg["url"] = url.rstrip("/")
    cfg["base_path"] = urlparse(cfg["url"]).path.rstrip("/")
    if os.environ.get("EMAIL_PROVIDER"):
        cfg["email"]["provider"] = os.environ["EMAIL_PROVIDER"]
    if os.environ.get("EMAIL_FORM_ACTION"):
        cfg["email"]["action"] = os.environ["EMAIL_FORM_ACTION"]
    if os.environ.get("SCAM_CHECKER_URL"):
        cfg["scam_checker"]["url"] = os.environ["SCAM_CHECKER_URL"]
    an = cfg.setdefault("analytics", {})
    if "PLAUSIBLE_DOMAIN" in os.environ:  # set it to "" to build without analytics
        an["plausible_domain"] = os.environ["PLAUSIBLE_DOMAIN"]
    if os.environ.get("PLAUSIBLE_SRC"):
        an["plausible_src"] = os.environ["PLAUSIBLE_SRC"]
    if an.get("plausible_domain"):
        src = an.get("plausible_src") or "https://plausible.io/js/script.outbound-links.tagged-events.js"
        cfg["analytics_snippet"] = (f'<script defer data-domain="{html.escape(an["plausible_domain"])}" '
                                    f'src="{html.escape(src)}"></script>')
    return cfg


PRODUCT_CLICK = "plausible-event-name=Product+Click"
AFFILIATE_CLICK = "plausible-event-name=Affiliate+Click"


def store_links() -> set[str]:
    links = {CFG["product"]["buy_url"]}
    links |= {p.get("buy_url", "") for p in CFG.get("ladder", [])}
    return {x for x in links if x}


def affiliate_links() -> set[str]:
    return {a.get("url", "") for a in CFG.get("affiliates", []) if isinstance(a, dict) and a.get("url")}


def is_placeholder(link: str) -> bool:
    return not link or "REPLACE_ME" in link


def u(path: str) -> str:
    if path.startswith(("http://", "https://", "mailto:", "#")):
        return path
    if CFG.get("_absolute_links"):
        return absu(path)
    return CFG["base_path"] + "/" + path.lstrip("/")


def absu(path: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    return CFG["url"] + "/" + path.lstrip("/")


def checker_url() -> str:
    link = CFG["scam_checker"]["url"]
    return u("/checker/") if is_placeholder(link) else link


# ------------------------------------------------------------------ markdown
def parse_front_matter(text: str) -> tuple[dict, str]:
    meta: dict = {}
    if text.startswith("---"):
        head, body = text[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            k, _, v = line.partition(":")
            v = v.strip()
            meta[k.strip()] = int(v) if v.isdigit() else v
        text = body.lstrip("\n")
    return meta, text


def values(extra: dict | None = None) -> dict:
    """Plain-text {{name}} values available to every content file (escaped later like any text)."""
    lm, kit = CFG["lead_magnet"], CFG["product"]
    v = {"checker": checker_url(), "magnet": u(f"/downloads/{lm['file']}"),
         "buy": kit["buy_url"], "contact": CFG["contact_email"],
         "ai": CFG["ai_disclosure"], "disclaimer": CFG["disclaimer"],
         "site_name": CFG["name"], "tagline": CFG["tagline"], "lm_title": lm["title"],
         "lm_headline": lm["headline"], "lm_pitch": lm["pitch"], "thanks_note": CFG["email"]["thanks_note"],
         "kit_name": kit["name"], "kit_price": price(kit), "kit_pages": str(kit["pages"]),
         "kit_refund_days": str(kit["refund_days"]), "reviewed": CFG.get("compare_reviewed", "")}
    v.update(extra or {})
    return v


def expand(text: str, extra: dict | None = None) -> str:
    """{{checker}}, {{magnet}}, {{buy}}, {{contact}}, {{ai}}, {{disclaimer}} and the other values() placeholders."""
    subs = values(extra)
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(subs.get(m.group(1), m.group(0))), text)


def inline(s: str) -> str:
    s = esc(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)\*(?!\w)", r"<em>\1</em>", s)

    def link(m):
        href = m.group(2)
        if href in affiliate_links():
            return f'<a href="{esc(href)}" rel="sponsored" class="{AFFILIATE_CLICK}">{m.group(1)}</a>'
        if href in store_links():
            return f'<a href="{esc(href)}" class="{PRODUCT_CLICK}">{m.group(1)}</a>'
        return f'<a href="{esc(u(href))}">{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


TOKEN = "\x00{}\x00"


def markdown(text: str, ctx: dict | None = None) -> str:
    """Markdown subset: #/##/### headings, lists, paragraphs, pipe tables, bold/italic/links, raw HTML lines
    (starting with "<"), `::: class [args]` ... `:::` blocks and {{shortcode:arg|arg}} HTML shortcodes."""
    ctx = ctx or {}
    tokens: list[str] = []

    def tokenize(m):
        html_out = shortcode(m.group(1), (m.group(2) or "").split("|") if m.group(2) is not None else [], ctx)
        if html_out is None:
            return m.group(0)
        tokens.append(html_out)
        return TOKEN.format(len(tokens) - 1)
    text = re.sub(r"\{\{(\w+)(?::([^}]*))?\}\}", lambda m: tokenize(m) if (m.group(2) is not None or m.group(1) in SHORTCODES) else m.group(0), text)
    text = expand(text, ctx.get("values"))
    out, para, lst, table, closers = [], [], None, [], []
    list_class = ""

    def flush():
        nonlocal para, lst, table, list_class
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []
        if lst:
            tag = lst[0]
            attr = f' class="{list_class}"' if list_class else ""
            list_class = ""
            out.append(f"<{tag}{attr}>" + "".join(f"<li>{inline(i)}</li>" for i in lst[1]) + f"</{tag}>")
            lst = None
        if table:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table
                    if not re.fullmatch(r"\|?[\s:|-]+\|?", r.strip())]
            head = "<tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr>"
            body = "".join("<tr>" + "".join(f"<{'th' if k == 0 else 'td'}>{inline(c)}</{'th' if k == 0 else 'td'}>"
                                            for k, c in enumerate(r)) + "</tr>" for r in rows[1:])
            out.append(f'<div class="scroll"><table class="compare">{head}{body}</table></div>')
            table = []

    for line in text.splitlines():
        s = line.strip()
        if not s:
            flush()
            continue
        if m := re.fullmatch(r":::\s*([\w-]*)\s*(.*)", s):
            flush()
            cls, arg = m.group(1), m.group(2).strip()
            if not cls:
                out.append(closers.pop() if closers else "")
            elif cls == "product":
                src, _, alt = (x.strip() for x in arg.partition("|"))
                out.append(f'<div class="product"><img src="{esc(u(src))}" alt="{esc(alt)}" width="170" height="220" loading="lazy"><div>')
                closers.append("</div></div>")
            elif cls == "inside":  # class on the list itself
                list_class = "inside"
                closers.append("")
            elif cls == "card":
                out.append("<div>")
                closers.append("</div>")
            else:
                out.append(f'<div class="{esc(cls)}">')
                closers.append("</div>")
            continue
        if re.fullmatch(TOKEN.format(r"\d+"), s) or s.startswith("<"):
            flush()
            out.append(s)
            continue
        if s.startswith("|"):
            if para or lst:
                flush()
            table.append(s)
            continue
        if m := re.match(r"(#{1,3})\s+(.*)", s):
            flush()
            out.append(f"<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>")
        elif m := re.match(r"[-*]\s+(.*)", s):
            if para:
                flush()
            if not lst or lst[0] != "ul":
                flush()
                lst = ["ul", []]
            lst[1].append(m.group(1))
        elif m := re.match(r"\d+\.\s+(.*)", s):
            if para:
                flush()
            if not lst or lst[0] != "ol":
                flush()
                lst = ["ol", []]
            lst[1].append(m.group(1))
        else:
            if lst or table:
                flush()
            para.append(s)
    flush()
    out.extend(reversed(closers))
    html_out = "\n".join(out)
    return re.sub(TOKEN.format(r"(\d+)"), lambda m: tokens[int(m.group(1))], html_out)


def load_dir(name: str) -> list[dict]:
    items = []
    for p in sorted((CONTENT / name).glob("*.md")):
        meta, body = parse_front_matter(p.read_text())
        meta["slug"] = re.sub(r"^\d+-", "", p.stem)
        meta["body_md"] = body
        items.append(meta)
    return items


# --------------------------------------------------------------------- parts
def email_form(source: str, button: str = "Send me the free checklist") -> str:
    e = CFG["email"]
    provider = e.get("provider", "netlify")
    thanks = u("/free/thanks/")
    field = e.get("email_field") or {"kit": "email_address", "mailerlite": "fields[email]"}.get(provider, "email")
    extra, attrs = "", ""
    if provider == "netlify":
        action = thanks
        attrs = ' name="lead-magnet" data-netlify="true" netlify-honeypot="website"'
        extra = '<input type="hidden" name="form-name" value="lead-magnet">'
    elif provider == "factory":
        action = e.get("action") or "http://localhost:8000/subscribe/scam-decoded"
    else:
        action = e.get("action") or "#configure-email-provider-in-site.json"
    if provider == "buttondown":
        extra += f'<input type="hidden" name="tag" value="{esc(source)}">'
    elif provider == "kit":
        extra += f'<input type="hidden" name="fields[source]" value="{esc(source)}">'
    elif provider == "mailerlite":
        extra += '<input type="hidden" name="ml-submit" value="1"><input type="hidden" name="anticsrf" value="true">'
        extra += f'<input type="hidden" name="fields[source]" value="{esc(source)}">'
    else:
        extra += f'<input type="hidden" name="source" value="{esc(source)}">'
    return f"""<form class="signup-form" method="post" action="{esc(action)}"{attrs}>
  {extra}
  <label class="hp" aria-hidden="true">Leave this empty <input type="text" name="website" tabindex="-1" autocomplete="off"></label>
  <label class="sr" for="em-{esc(source)}">Email address</label>
  <input id="em-{esc(source)}" type="email" name="{esc(field)}" required autocomplete="email" inputmode="email" placeholder="you@example.com">
  <button type="submit">{esc(button)}</button>
</form>
<p class="form-note">{esc(e.get('privacy_note', ''))} <a href="{u('/privacy/')}">Privacy</a>.</p>"""


def checker_box() -> str:
    link = CFG["scam_checker"]["url"]
    if is_placeholder(link):
        msg = "scam_checker.url is a placeholder: linking to the built-in /checker/ instead"
        if msg not in WARNINGS:
            WARNINGS.append(msg)
        link = u("/checker/")
    return (f'<a class="checker" href="{esc(link)}"><span class="badge">Free tool</span>'
            f'<strong>{esc(CFG["scam_checker"]["label"])}</strong><span aria-hidden="true">→</span></a>')


def layout(*, title: str, description: str, path: str, body: str, noindex: bool = False) -> str:
    socials = " · ".join(f'<a href="{esc(v)}" rel="me">{esc(k)}</a>' for k, v in CFG["socials"].items())
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{absu(path)}">
{robots}
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{absu(path)}">
<meta property="og:image" content="{absu('/img/lead-magnet-cover.png')}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{u('/style.css')}">
{CFG.get('analytics_snippet', '')}
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="{u('/')}"><span class="shield" aria-hidden="true"></span>{esc(CFG['name'])}</a>
<nav><a href="{checker_url()}">Scam checker</a><a href="{u('/kit/')}">Family kit</a></nav></div></header>
<main>{body}</main>
<footer><div class="wrap">
<p>{socials}</p>
<p><a href="{u('/parents/')}">Protect Your Parents</a> · <a href="{u('/teams/')}">Training for teams</a> · <a href="{u('/newsletter/')}">Weekly Scam Alert</a> · <a href="{u('/compare/')}">Tools compared</a> · <a href="{u('/scams/')}">Scam explainers</a></p>
<p><a href="{u('/disclosures/')}">Disclosures</a> · <a href="{u('/privacy/')}">Privacy</a> · {esc(CFG['contact_email'])}</p>
<p class="small">{esc(CFG['disclaimer'])} {esc(CFG['ai_disclosure'])}</p>
</div></footer>
</body>
</html>
"""


def write(path: str, text: str) -> None:
    dest = OUT / path.lstrip("/")
    if path.endswith("/"):
        dest = dest / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)


def price(p: dict) -> str:
    return f"${p['price']:g}"


def email_html(e: dict, body: str) -> str:
    body = re.sub(r"<h(\d)>", r'<h\1 style="font-size:20px;margin:24px 0 8px">', body)
    body = body.replace("<p>", '<p style="margin:0 0 16px">')
    body = body.replace("<ul>", '<ul style="margin:0 0 16px;padding-left:22px">')
    body = body.replace("<ol>", '<ol style="margin:0 0 16px;padding-left:22px">')
    body = body.replace("<li>", '<li style="margin:0 0 6px">')
    body = body.replace("<a ", '<a style="color:#178a80;font-weight:600" ')
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(e['subject'])}</title></head>
<body style="margin:0;background:#f4f1ea">
<span style="display:none;max-height:0;overflow:hidden">{esc(e.get('preheader', ''))}</span>
<div style="max-width:560px;margin:0 auto;padding:24px 20px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:#0d1b2a;background:#ffffff">
{body}
<p style="margin:24px 0 0;font-size:12px;color:#4a5868">{esc(CFG['disclaimer'])}</p>
</div></body></html>
"""


def email_text(body: str) -> str:
    t = re.sub(r"<li[^>]*>", "- ", body)
    t = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"\2 (\1)", t)
    t = re.sub(r"</(p|h\d|li|ul|ol)>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"\n{3,}", "\n\n", t).strip() + f"\n\n{CFG['disclaimer']}\n"


def emails() -> list[dict]:
    seq = []
    CFG["_absolute_links"] = True          # email links must be absolute
    try:
        for e in load_dir("emails"):
            body = markdown(e["body_md"])
            html_doc, text = email_html(e, body), email_text(body)
            write(f"/emails/{e['slug']}/email.html", html_doc)
            write(f"/emails/{e['slug']}/email.txt", text)
            seq.append({"order": e["order"], "send_on_day": e["day"], "slug": e["slug"], "subject": e["subject"],
                        "preheader": e.get("preheader", ""), "goal": e.get("goal", ""), "html": html_doc,
                        "text": text})
    finally:
        CFG["_absolute_links"] = False
    seq.sort(key=lambda x: x["order"])
    (OUT / "emails").mkdir(parents=True, exist_ok=True)
    (OUT / "emails" / "sequence.json").write_text(json.dumps(seq, indent=2))
    rows = "".join(f"<tr><td>{s['order']}</td><td>{s['send_on_day']}</td><td><a href=\"{u('/emails/' + s['slug'] + '/email.html')}\">"
                   f"{esc(s['subject'])}</a></td><td>{esc(s['goal'])}</td></tr>" for s in seq)
    write("/emails/", layout(title="Email sequence preview", description="Private preview.", path="/emails/",
                             noindex=True, body=f'<section class="wrap"><h1>Email sequence preview</h1>'
                             f'<table><tr><th>#</th><th>Day</th><th>Subject</th><th>Job</th></tr>{rows}</table></section>'))
    return seq


def newsletter_issues() -> list[dict]:
    """content/newsletter/NN-slug.md (TEMPLATE.md is the blank format and isn't published)."""
    return sorted((i for i in load_dir("newsletter") if i.get("issue")), key=lambda i: i["issue"])


def newsletter() -> list[tuple]:
    """Weekly Scam Alert: ready-to-paste email files plus a public archive."""
    issues, pages = [], []
    for i in newsletter_issues():
        CFG["_absolute_links"] = True
        try:
            body = markdown(expand(i["body_md"]))
            html_doc, text = email_html(i, body), email_text(body)
        finally:
            CFG["_absolute_links"] = False
        write(f"/newsletter/{i['slug']}/email.html", html_doc)
        (OUT / "newsletter" / i["slug"] / "email.txt").write_text(text)
        issues.append({"issue": i["issue"], "send_date": i["send_date"], "slug": i["slug"], "subject": i["subject"],
                       "preheader": i.get("preheader", ""), "html": html_doc, "text": text})
        web = markdown(expand(i["body_md"]))
        pages.append((f"/newsletter/{i['slug']}/", f"{i['subject']} · {CFG['name']}", i.get("preheader", ""),
                      f'<section class="wrap narrow"><p class="kicker">Scam Alert · issue {i["issue"]} · {esc(str(i["send_date"]))}</p>'
                      f'<h1>{esc(i["subject"].split(": ", 1)[-1])}</h1>{web}'
                      f'<h2>Get the next one</h2>{email_form("newsletter-" + i["slug"], "Send me the weekly Scam Alert")}</section>',
                      False))
    (OUT / "newsletter").mkdir(parents=True, exist_ok=True)
    (OUT / "newsletter" / "issues.json").write_text(json.dumps(issues, indent=2))
    rows = "".join(f'<li><a href="{u("/newsletter/" + x["slug"] + "/")}">{esc(x["subject"])}</a> '
                   f'<span class="small">{esc(str(x["send_date"]))}</span></li>' for x in reversed(issues))
    pages.insert(0, ("/newsletter/", f"Scam Alert: the weekly newsletter · {CFG['name']}",
                     "One scam a week, decoded in plain English: the tell, what to do, and one 5-minute job.",
                     f'<section class="wrap narrow"><h1>Scam Alert, every Thursday</h1>'
                     f'<p class="lede">One scam a week, decoded: the tell that gives it away, what to do, and one 5-minute job that makes you harder to scam.</p>'
                     f'{email_form("newsletter-archive", "Send me the weekly Scam Alert")}<h2>Past issues</h2><ul>{rows}</ul></section>',
                     False))
    return pages


# ------------------------------------------------------------------ products
def get_product(slug: str) -> dict:
    """The $9 kit is CFG["product"]; the other rungs are CFG["ladder"]."""
    if slug == CFG["product"]["slug"]:
        return CFG["product"]
    return next(x for x in CFG.get("ladder", []) if x["slug"] == slug)


def buy_link(p: dict) -> str:
    if "example." in p["buy_url"] or is_placeholder(p["buy_url"]):
        name = "product" if p is CFG["product"] else p["slug"]
        WARNINGS.append(f"{name} buy_url is still a placeholder: {p['buy_url']}")
    return p["buy_url"]


def product_ld(p: dict, image: str, description: str) -> str:
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "image": absu(image),
          "description": description, "brand": {"@type": "Brand", "name": CFG["name"]},
          "offers": {"@type": "Offer", "price": str(p["price"]), "priceCurrency": "USD", "url": p["buy_url"],
                     "availability": "https://schema.org/InStock"}}
    return f'<script type="application/ld+json">{json.dumps(ld)}</script>'


def aff(slug: str) -> dict:
    return next(a for a in CFG["affiliates"] if a["slug"] == slug)


def aff_button(slug: str, label: str) -> str:
    a = aff(slug)
    if is_placeholder(a["url"]):
        WARNINGS.append(f"affiliate {slug} url is still a placeholder: {a['url']}")
    return f'<a class="button {AFFILIATE_CLICK}" rel="sponsored nofollow" href="{esc(a["url"])}">{esc(label)}</a>'


def checker_cta() -> str:
    link = CFG["scam_checker"]["url"]
    if is_placeholder(link):
        WARNINGS.append("scam_checker.url is a placeholder: set it to the deployed PR #8 checker "
                        "(site.json or SCAM_CHECKER_URL)")
        return ("<p>Our free \"Is this a scam?\" checker is coming soon. Until then, use the three tells: rush, secrecy "
                "and a strange way to pay. See two, stop, and check on your own using a number or website you look up yourself.</p>")
    return f'<p><a class="button" href="{esc(link)}">Open the free scam checker</a></p>'


# ---------------------------------------------------------------- shortcodes
SHORTCODES = {"checker_box", "checker_cta", "checker_tool", "scam_index", "download", "buy", "signup", "aff"}


def articles() -> list[dict]:
    """content/articles/NN-slug.md -> /scams/<slug>/ (the explainers the checker links to)."""
    out = []
    for m in load_dir("articles"):
        m.setdefault("path", f"/scams/{m['slug']}/")
        out.append(m)
    return out


def article_map() -> dict:
    return {m["slug"]: {"title": m["title"], "url": u(m["path"])} for m in articles()}


def scam_index() -> str:
    rows = "".join(f'<li><a href="{esc(a["url"])}">{esc(a["title"])}</a></li>' for a in article_map().values())
    return f'<ul class="reads">{rows}</ul>'


def checker_tool() -> str:
    """The in-browser checker: rules in static/checker.js, no network calls, nothing stored."""
    data = json.dumps(article_map()).replace("</", "<\\/")
    return f"""<form id="sd-checker" class="checker-tool" autocomplete="off">
  <label for="sd-input"><strong>Paste the text, email or link</strong></label>
  <textarea id="sd-input" rows="7" maxlength="20000" spellcheck="false" placeholder="e.g. USPS: Your package is on hold. Update your address within 12 hours: usps-redelivery.com"></textarea>
  <div class="row"><button type="submit">Check it</button><button type="reset" class="ghost">Clear</button></div>
  <p class="form-note">Checked on your device. Nothing you paste is sent anywhere or saved, and links are never opened.</p>
</form>
<noscript><p>The checker needs JavaScript. Until then, use the three tells: rush, secrecy, and an unusual way to pay.</p></noscript>
<div id="sd-result" class="checker-result" tabindex="-1" aria-live="polite"></div>
<script>window.SD_ARTICLES = {data};</script>
<script src="{u('/checker.js')}" defer></script>"""


def shortcode(name: str, args: list[str], ctx: dict) -> str | None:
    """HTML-producing {{name:arg|arg}} shortcodes for content files."""
    if name == "checker_box":
        return checker_box()
    if name == "checker_tool":
        return checker_tool()
    if name == "scam_index":
        return scam_index()
    if name == "checker_cta":
        return checker_cta()
    if name == "signup":
        return email_form(*[a.strip() for a in args]) if args else None
    if name == "aff":
        return aff_button(args[0].strip(), args[1].strip())
    if name == "download":
        lm = CFG["lead_magnet"]
        return f'<p><a class="button" href="{u("/downloads/" + lm["file"])}" download>Download {esc(lm["title"])} (PDF)</a></p>'
    if name == "buy" and ctx.get("product"):
        p = ctx["product"]
        return f'<p><a class="button {PRODUCT_CLICK}" href="{esc(p["buy_url"])}">{esc(ctx["button"])}</a></p>'
    return None


# --------------------------------------------------------------------- pages
def product_values(p: dict) -> dict:
    v = {"name": p["name"], "price": price(p)}
    for k in ("pages", "refund_days", "code", "code_off"):
        if k in p:
            v[k] = f"{p[k]:g}" if isinstance(p[k], float) else str(p[k])
    return v


def render_page(meta: dict) -> tuple:
    """A content file -> (path, title, description, body, noindex). Layouts: page, narrow, lead-magnet, sales."""
    kind = meta.get("layout", "page")
    ctx: dict = {"values": {}}
    if meta.get("product"):
        p = get_product(meta["product"])
        buy_link(p)
        ctx = {"product": p, "values": product_values(p)}
    fm = {k: expand(str(v), ctx["values"]) for k, v in meta.items() if k != "body_md"}
    ctx["button"] = fm.get("button", "")
    body = markdown(meta["body_md"], ctx)
    path = fm.get("path") or f"/{meta['slug']}/"
    title, desc = fm.get("title", ""), fm.get("description") or fm.get("title", "")
    if kind == "page":
        title = f"{fm['title']} · {CFG['name']}"
        html_out = f'<section class="wrap narrow"><h1>{esc(fm["title"])}</h1>{body}</section>'
    elif kind == "narrow":
        html_out = f'<section class="wrap narrow">{body}</section>'
    elif kind == "lead-magnet":
        lm = CFG["lead_magnet"]
        html_out = f"""
<section class="hero"><div class="wrap grid">
  <div>
    <p class="kicker">{esc(CFG['tagline'])}</p>
    <h1>{esc(lm['headline'])}</h1>
    <p class="lede">{esc(lm['pitch'])}</p>
    {email_form(fm.get('signup', 'home-hero'))}
  </div>
  <img class="cover" src="{u('/img/lead-magnet-cover.png')}" alt="Cover of {esc(lm['title'])}" width="306" height="396">
</div></section>
<section class="wrap">{body}</section>"""
    elif kind == "sales":
        p = ctx["product"]
        cover = fm.get("cover") or p.get("cover", "")
        code = f'<p class="small">{inline(fm["code_note"])}</p>' if fm.get("code_note") and p.get("code") else ""
        html_out = f"""{product_ld(p, cover, fm.get('ld_description', desc))}
<section class="hero"><div class="wrap grid">
  <div>
    <p class="kicker">{esc(fm['kicker'])}</p>
    <h1>{esc(fm['headline'])}</h1>
    <p class="lede">{esc(fm['lede'])}</p>
    {shortcode('buy', [], ctx)}
    {code}
    <p class="small">{esc(fm['small'])}</p>
  </div>
  <img class="cover" src="{u(cover)}" alt="{esc(fm.get('cover_alt', ''))}" width="{fm.get('cover_w', 306)}" height="{fm.get('cover_h', 396)}">
</div></section>
<section class="wrap">{body}</section>"""
    else:
        raise SystemExit(f"{meta['slug']}: unknown layout {kind!r}")
    return path, title, desc, html_out, fm.get("noindex") == "true", fm


def content_pages() -> list[tuple]:
    items = [render_page(m) for m in load_dir("pages") + load_dir("products") + articles()]
    items.sort(key=lambda x: int(x[5].get("order", 99)))
    pages = []
    for path, title, desc, body, noindex, fm in items:
        pages.append((path, title, desc, body, noindex))
        if fm.get("alias"):
            pages.append((fm["alias"], fm.get("alias_title", title), desc, body, noindex))
    return pages


def build() -> list[str]:
    global CFG
    CFG = load_config()
    WARNINGS.clear()
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(STATIC, OUT)
    pages = content_pages()
    pages += newsletter()
    for path, title, desc, body, noindex in pages:
        write(path, layout(title=title, description=desc, path=path, body=body, noindex=noindex))
    write("/404.html", layout(title="Not found", description="Page not found.", path="/404.html", noindex=True,
                              body=f'<section class="wrap narrow"><h1>Page not found</h1><p><a href="{u("/")}">Get the free checklist</a></p></section>'))
    emails()
    indexed = [p for p, *_ , noindex in pages if not noindex and p != "/free/"]  # /free/ duplicates /
    sm = "".join(f"<url><loc>{absu(p)}</loc></url>" for p in indexed)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: {u('/emails/')}\nDisallow: {u('/free/thanks/')}\n"
                                    f"Sitemap: {absu('/sitemap.xml')}\n")
    return indexed


def serve(port: int = 8080) -> None:
    import functools
    import http.server
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print(f"Serving {OUT} on http://localhost:{port}{CFG['base_path'] or ''}/")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    built = build()
    print(f"Built {len(built)} indexed pages into {OUT} for {CFG['url']} (email provider: {CFG['email']['provider']})")
    for w in WARNINGS:
        print("WARNING:", w)
    if "--serve" in sys.argv:
        serve()
