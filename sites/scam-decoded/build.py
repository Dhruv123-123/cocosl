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
def email_form(source: str, button: str = "Send me the free checklist", thanks_path: str = "/free/thanks/") -> str:
    e = CFG["email"]
    provider = e.get("provider", "netlify")
    thanks = u(thanks_path)
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


OG_IMAGES: dict[str, str] = {}  # page path -> its own share image (default: the lead magnet cover)


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
<meta property="og:image" content="{absu(OG_IMAGES.get(path, '/img/lead-magnet-cover.png'))}">
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
<p><a href="{u('/parents/')}">Protect Your Parents</a> · <a href="{u('/teams/')}">Training for teams</a> · <a href="{u('/newsletter/')}">Weekly Scam Alert</a> · <a href="{u('/alerts/')}">Scam alerts</a> · <a href="{u('/quiz/')}">Could you spot it? Quiz</a> · <a href="{u('/compare/')}">Tools compared</a> · <a href="{u('/scams/')}">Scam explainers</a> · <a href="{u('/breached/')}">Data breach checklist</a> · <a href="{u('/how-we-make-money/')}">How we make money</a></p>
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
SHORTCODES = {"checker_box", "checker_cta", "checker_tool", "scam_index", "download", "buy", "signup", "aff",
              "money_products", "money_affiliates", "quiz_tool"}


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


def quiz_data() -> dict:
    return json.loads((CONTENT / "quiz.json").read_text())


def quiz_tool() -> str:
    """The 'Could you spot it?' quiz: questions in content/quiz.json, logic in static/quiz.js. No network, nothing stored."""
    q = quiz_data()
    data = json.dumps({"questions": q["questions"], "tiers": q["tiers"], "site": absu("/").rstrip("/")}).replace("</", "<\\/")
    n = len(q["questions"])
    sources = "".join(f'<li><a href="{esc(h)}">{esc(t)}</a></li>' for t, h in q["sources"])
    answers = "".join(f'<li><strong>{esc(x["answer"].capitalize())}.</strong> {esc(x["channel"])} from {esc(x["sender"])}: '
                      f'{esc(x["tell"])}.</li>' for x in q["questions"])
    return f"""<div id="sd-quiz" class="quiz-tool" tabindex="-1" aria-live="polite">
  <p class="quiz-progress">{n} questions · about 3 minutes</p>
  <p>{esc(q["intro"])}</p>
  <p><button type="button" id="sd-quiz-start">Start the quiz</button></p>
  <p class="form-note">Runs on your device. Your answers aren't sent anywhere or saved.</p>
</div>
<noscript><p>The quiz needs JavaScript. The answers are listed below.</p></noscript>
<div id="sd-quiz-after" hidden>
<h2>Get one scam a week, explained</h2>
<p>Every Thursday: one real scam, its tells and the fix, in a 3-minute read.</p>
{email_form("quiz", "Send me the weekly scam")}
<p>Want the people you love to score 12/12? The <a href="{u('/kit/')}">Family kit</a> walks through these with them.</p>
</div>
<details class="quiz-answers"><summary>See all {n} answers</summary><ol>{answers}</ol></details>
<h2>Sources</h2><ul class="small">{sources}</ul>
<script>window.SD_QUIZ = {data};</script>
<script src="{u('/quiz.js')}" defer></script>"""


def quiz_pages() -> list[tuple]:
    """/quiz/score/N/: what a shared result link opens. Each has its own share image (static/img/quiz/score-N.png,
    made by make_quiz_cards.py) so the preview shows the score. Not indexed."""
    q, pages = quiz_data(), []
    n = len(q["questions"])
    for s in range(n + 1):
        tier = next(t for t in q["tiers"] if s >= t["min"])
        path = f"/quiz/score/{s}/"
        OG_IMAGES[path] = f"/img/quiz/score-{s}.png"
        pages.append((path, f"I got {s}/{n} on Could you spot it? · {CFG['name']}",
                      f"{s}/{n}: {tier['name']}. 12 messages, scam or legit? Take the free quiz and see if you can beat it.",
                      f'<section class="wrap narrow"><p class="kicker">Could you spot it?</p><h1>Someone scored {s}/{n}: '
                      f'{esc(tier["name"])}</h1><img class="quiz-card" src="{u(OG_IMAGES[path])}" alt="Result card: {s} out of {n}" '
                      f'width="1200" height="630"><p class="lede">12 real-looking messages. Scam or legit? It takes about 3 minutes, '
                      f'and you see the tell after every answer.</p><p><a class="button" href="{u("/quiz/")}">Take the quiz</a></p></section>',
                      True))
    return pages


def money_products() -> str:
    """Every product we sell, with its price, straight from site.json (for /how-we-make-money/)."""
    rows = "".join(f'<li><a href="{u("/" + p["slug"] + "/")}">{esc(p["name"])}</a>, {esc(price(p))}</li>'
                   for p in [CFG["product"], *CFG["ladder"]])
    return f'<ul class="reads">{rows}</ul>'


def money_affiliates() -> str:
    """Every affiliate partner in site.json, by category, linking to the comparison page."""
    names = {"identity": "identity protection", "passwords": "password manager", "vpn": "VPN"}
    rows = "".join(f'<li>{esc(a["name"])} ({esc(names.get(a["category"], a["category"]))})</li>' for a in CFG["affiliates"])
    return f'<ul class="reads">{rows}</ul>'


def shortcode(name: str, args: list[str], ctx: dict) -> str | None:
    """HTML-producing {{name:arg|arg}} shortcodes for content files."""
    if name == "checker_box":
        return checker_box()
    if name == "checker_tool":
        return checker_tool()
    if name == "scam_index":
        return scam_index()
    if name == "money_products":
        return money_products()
    if name == "quiz_tool":
        return quiz_tool()
    if name == "money_affiliates":
        return money_affiliates()
    if name == "checker_cta":
        return checker_cta()
    if name == "signup":
        return email_form(*[a.strip() for a in args]) if args else None
    if name == "aff":
        return aff_button(args[0].strip(), args[1].strip())
    if name == "download":
        lm = CFG[args[0].strip()] if args else CFG["lead_magnet"]  # {{download}} or {{download:holiday_guide}}
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


# --------------------------------------------------------------- scam of the week alerts
SEVERITY = {"watch": ("Watch for this", "#2ec4b6", "#0d1b2a"),
            "warning": ("Scam warning", "#ff9f1c", "#0d1b2a"),
            "urgent": ("Urgent scam alert", "#d7263d", "#ffffff")}
ALERT_FIELDS = ("alert_date", "severity", "scam", "channel", "subject", "preheader", "example", "sender",
                "tell_1", "tell_2", "tell_3", "do_1", "do_2", "do_3", "if_already", "source_title", "source_url")


def alert_items() -> list[dict]:
    """content/alerts/NN-slug.md: one 'scam of the week' alert, all fields in the front matter.
    _TEMPLATE.md has no alert_date and isn't published. Missing fields fail the build loudly."""
    out = []
    for a in load_dir("alerts"):
        if not a.get("alert_date"):
            continue
        missing = [f for f in ALERT_FIELDS if not str(a.get(f, "")).strip()]
        if missing:
            raise SystemExit(f"alert {a['slug']}: missing {', '.join(missing)}")
        todo = [f for f in (*ALERT_FIELDS, "explainer", "body_md") if str(a.get(f, "")).lstrip().startswith("[")]
        if todo or a["source_url"].strip() == "https://":
            raise SystemExit(f"alert {a['slug']}: still has template text in {', '.join(todo) or 'source_url'}")
        if a["severity"] not in SEVERITY:
            raise SystemExit(f"alert {a['slug']}: severity must be one of {', '.join(SEVERITY)}")
        out.append(a)
    return sorted(out, key=lambda a: str(a["alert_date"]))


def alert_links(a: dict, link) -> list[tuple[str, str]]:
    links = [("Paste a message into our free scam checker", link("/checker/"))]
    if a.get("explainer") and a["explainer"] in article_map():
        links.insert(0, (f"How it works: {article_map()[a['explainer']]['title']}", link(f"/scams/{a['explainer']}/")))
    return links


def alert_email_html(a: dict) -> str:
    label, bg, fg = SEVERITY[a["severity"]]
    tells = "".join(f'<li style="margin:0 0 8px">{esc(a[f"tell_{n}"])}</li>' for n in (1, 2, 3))
    dos = "".join(f'<li style="margin:0 0 8px">{esc(a[f"do_{n}"])}</li>' for n in (1, 2, 3))
    extra = markdown(expand(a["body_md"])) if a["body_md"].strip() else ""
    links = "".join(f'<p style="margin:0 0 8px"><a style="color:#178a80;font-weight:600" href="{esc(h)}">{esc(t)}</a></p>'
                    for t, h in alert_links(a, absu))
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(a['subject'])}</title></head>
<body style="margin:0;background:#f4f1ea">
<span style="display:none;max-height:0;overflow:hidden">{esc(a['preheader'])}</span>
<div style="max-width:560px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:#0d1b2a;background:#ffffff">
<div style="background:{bg};color:{fg};padding:14px 20px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:13px">{esc(label)} · Scam of the week · {esc(str(a['alert_date']))}</div>
<div style="padding:20px">
<h1 style="font-size:24px;line-height:1.25;margin:0 0 12px">{esc(a['scam'])}</h1>
<p style="margin:0 0 8px;font-size:13px;color:#4a5868">Arrives by: {esc(a['channel'])} · From: {esc(a['sender'])} (fictional example)</p>
<div style="background:#eef2f4;border-radius:16px;padding:14px 16px;margin:0 0 20px;font-style:italic">{esc(a['example'])}</div>
<h2 style="font-size:18px;margin:0 0 8px">3 tells</h2><ol style="margin:0 0 16px;padding-left:22px">{tells}</ol>
<h2 style="font-size:18px;margin:0 0 8px">Do this</h2><ol style="margin:0 0 16px;padding-left:22px">{dos}</ol>
<p style="margin:0 0 16px;background:#fff4e0;border-left:4px solid #ff9f1c;padding:10px 12px"><strong>Already clicked, paid or shared?</strong> {esc(a['if_already'])}</p>
{extra}
{links}
<p style="margin:16px 0 0;font-size:13px;color:#4a5868">Source: <a style="color:#178a80" href="{esc(a['source_url'])}">{esc(a['source_title'])}</a>. Forward this to someone who'd get this message.</p>
<p style="margin:16px 0 0;font-size:12px;color:#4a5868">{esc(CFG['disclaimer'])}</p>
</div></div></body></html>
"""


def alert_email_text(a: dict) -> str:
    label = SEVERITY[a["severity"]][0]
    lines = [f"{label.upper()} · SCAM OF THE WEEK · {a['alert_date']}", "", a["scam"], "",
             f"Arrives by: {a['channel']} · From: {a['sender']} (fictional example)", f"\"{a['example']}\"", "",
             "3 TELLS", *[f"{n}. {a[f'tell_{n}']}" for n in (1, 2, 3)], "",
             "DO THIS", *[f"{n}. {a[f'do_{n}']}" for n in (1, 2, 3)], "",
             f"Already clicked, paid or shared? {a['if_already']}", ""]
    if a["body_md"].strip():
        lines += [email_text(markdown(expand(a["body_md"]))).rsplit("\n\n", 1)[0], ""]
    lines += [f"{t}: {h}" for t, h in alert_links(a, absu)]
    lines += ["", f"Source: {a['source_title']} ({a['source_url']})", "Forward this to someone who'd get this message.",
              "", CFG["disclaimer"]]
    return "\n".join(lines) + "\n"


def alerts() -> list[tuple]:
    """Scam of the week alerts: fill the fields in content/alerts/_TEMPLATE.md, get a ready-to-send email (HTML +
    text) and a public page. Separate from the Thursday newsletter: send one when a scam spikes."""
    items, pages = [], []
    for a in alert_items():
        CFG["_absolute_links"] = True
        try:
            html_doc, text = alert_email_html(a), alert_email_text(a)
        finally:
            CFG["_absolute_links"] = False
        write(f"/alerts/{a['slug']}/email.html", html_doc)
        (OUT / "alerts" / a["slug"] / "email.txt").write_text(text)
        items.append({"slug": a["slug"], "alert_date": str(a["alert_date"]), "severity": a["severity"],
                      "subject": a["subject"], "preheader": a["preheader"], "html": html_doc, "text": text})
        label, bg, fg = SEVERITY[a["severity"]]
        tells = "".join(f"<li>{esc(a[f'tell_{n}'])}</li>" for n in (1, 2, 3))
        dos = "".join(f"<li>{esc(a[f'do_{n}'])}</li>" for n in (1, 2, 3))
        links = "".join(f'<li><a href="{esc(h)}">{esc(t)}</a></li>' for t, h in alert_links(a, u))
        extra = markdown(expand(a["body_md"])) if a["body_md"].strip() else ""
        pages.append((f"/alerts/{a['slug']}/", f"{a['scam']} · {CFG['name']}", a["preheader"],
                      f'<section class="wrap narrow"><p class="alert-badge" style="background:{bg};color:{fg}">{esc(label)} · '
                      f'{esc(str(a["alert_date"]))}</p><h1>{esc(a["scam"])}</h1>'
                      f'<p class="small">Arrives by: {esc(a["channel"])} · From: {esc(a["sender"])} (fictional example)</p>'
                      f'<blockquote class="alert-example">{esc(a["example"])}</blockquote>'
                      f'<h2>3 tells</h2><ol>{tells}</ol><h2>Do this</h2><ol>{dos}</ol>'
                      f'<p class="alert-already"><strong>Already clicked, paid or shared?</strong> {esc(a["if_already"])}</p>'
                      f'{extra}<ul>{links}</ul><p class="small">Source: <a href="{esc(a["source_url"])}">{esc(a["source_title"])}</a></p>'
                      f'<h2>Get alerts like this</h2>{email_form("alert-" + a["slug"], "Send me scam alerts")}</section>', False))
    (OUT / "alerts").mkdir(parents=True, exist_ok=True)
    (OUT / "alerts" / "alerts.json").write_text(json.dumps(items, indent=2))
    rows = "".join(f'<li><a href="{u("/alerts/" + x["slug"] + "/")}">{esc(x["subject"])}</a> '
                   f'<span class="small">{esc(x["alert_date"])}</span></li>' for x in reversed(items))
    pages.insert(0, ("/alerts/", f"Scam alerts · {CFG['name']}", "Short alerts when a scam is spiking: the message, 3 tells, and what to do.",
                     f'<section class="wrap narrow"><h1>Scam alerts</h1><p class="lede">When a scam spikes, we send a short alert: '
                     f'the message, 3 tells, and what to do. The full weekly read is the <a href="{u("/newsletter/")}">Thursday newsletter</a>.</p>'
                     f'{email_form("alerts-archive", "Send me scam alerts")}<h2>Recent alerts</h2><ul>{rows}</ul></section>', False))
    return pages


def build() -> list[str]:
    global CFG
    CFG = load_config()
    WARNINGS.clear()
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(STATIC, OUT)
    pages = content_pages()
    pages += newsletter()
    pages += alerts()
    pages += quiz_pages()
    for path, title, desc, body, noindex in pages:
        write(path, layout(title=title, description=desc, path=path, body=body, noindex=noindex))
    write("/404.html", layout(title="Not found", description="Page not found.", path="/404.html", noindex=True,
                              body=f'<section class="wrap narrow"><h1>Page not found</h1><p><a href="{u("/")}">Get the free checklist</a></p></section>'))
    emails()
    indexed = [p for p, *_ , noindex in pages if not noindex and p != "/free/"]  # /free/ duplicates /
    sm = "".join(f"<url><loc>{absu(p)}</loc></url>" for p in indexed)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: {u('/emails/')}\nDisallow: {u('/free/thanks/')}\nDisallow: {u('/holiday/thanks/')}\n"
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
