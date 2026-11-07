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
    return cfg


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


def expand(text: str) -> str:
    """{{checker}}, {{magnet}}, {{buy}}, {{contact}}, {{ai}}, {{disclaimer}} placeholders."""
    lm = CFG["lead_magnet"]
    subs = {"checker": checker_url(), "magnet": u(f"/downloads/{lm['file']}"),
            "buy": CFG["product"]["buy_url"], "contact": CFG["contact_email"],
            "ai": CFG["ai_disclosure"], "disclaimer": CFG["disclaimer"]}
    return re.sub(r"\{\{(\w+)\}\}", lambda m: subs.get(m.group(1), m.group(0)), text)


def inline(s: str) -> str:
    s = esc(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)\*(?!\w)", r"<em>\1</em>", s)

    def link(m):
        href = m.group(2)
        return f'<a href="{esc(u(href))}">{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def markdown(text: str) -> str:
    out, para, lst = [], [], None

    def flush():
        nonlocal para, lst
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []
        if lst:
            tag = lst[0]
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in lst[1]) + f"</{tag}>")
            lst = None

    for line in expand(text).splitlines():
        s = line.strip()
        if not s:
            flush()
            continue
        if m := re.match(r"(#{2,3})\s+(.*)", s):
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
            if lst:
                flush()
            para.append(s)
    flush()
    return "\n".join(out)


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
        return ""
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


# --------------------------------------------------------------------- pages
def home() -> str:
    lm = CFG["lead_magnet"]
    tonight = ["Freeze your credit at all three bureaus (free, 10 minutes)",
               "Pick a family safe word for panic calls about money",
               "Turn on alerts for every account and card"]
    return f"""
<section class="hero"><div class="wrap grid">
  <div>
    <p class="kicker">{esc(CFG['tagline'])}</p>
    <h1>{esc(lm['headline'])}</h1>
    <p class="lede">{esc(lm['pitch'])}</p>
    {email_form('home-hero')}
  </div>
  <img class="cover" src="{u('/img/lead-magnet-cover.png')}" alt="Cover of {esc(lm['title'])}" width="306" height="396">
</div></section>
<section class="wrap">
  {checker_box()}
  <h2>What's inside the free checklist</h2>
  <div class="cards">
    <div><h3>Tonight: 10 minutes, $0</h3><ul>{''.join(f'<li>{esc(t)}</li>' for t in tonight)}</ul></div>
    <div><h3>The three rules</h3><ul><li>Call back on a number you look up yourself</li><li>Never pay a stranger with gift cards, wires, crypto or apps</li><li>Never read a one-time code to anyone who contacted you</li></ul></div>
    <div><h3>If it happens</h3><ul><li>The first-hour plan, in order</li><li>Where to report (FTC, IdentityTheft.gov)</li><li>How to spot the "recovery" scam that follows</li></ul></div>
  </div>
  <h2>Then, one short email a week</h2>
  <p>The scam going around right now, the tell that gives it away, and exactly what to do. Calm, specific, no "you've been hacked" panic. Made for adults and their families, especially the person everyone calls about "a weird text".</p>
  <div class="cta-band">{email_form('home-bottom', 'Get the free checklist')}</div>
</section>"""


def thanks() -> str:
    lm, p = CFG["lead_magnet"], CFG["product"]
    return f"""
<section class="wrap narrow">
  <p class="kicker">You're in</p>
  <h1>Here's your checklist</h1>
  <p>{esc(CFG['email']['thanks_note'])}</p>
  <p><a class="button" href="{u('/downloads/' + lm['file'])}" download>Download {esc(lm['title'])} (PDF)</a></p>
  <p>Start with section 1 tonight. It takes about 10 minutes and costs nothing.</p>
  {checker_box()}
  <div class="product">
    <img src="{u('/img/kit-cover.png')}" alt="Cover of {esc(p['name'])}" width="170" height="220" loading="lazy">
    <div><h2>Want the whole family plan on paper?</h2>
    <p><strong>{esc(p['name'])}</strong> is our own {p['pages']}-page printable kit: a scripted family meeting, freeze trackers for every family member, the 12-scam decoder, and a fridge card and wallet cards for parents. {price(p)}, {p['refund_days']}-day refund.</p>
    <p><a href="{u('/kit/')}">See what's inside →</a></p></div>
  </div>
</section>"""


def kit() -> str:
    p = CFG["product"]
    buy = p["buy_url"]
    if "example." in buy or is_placeholder(buy):
        WARNINGS.append(f"product buy_url is still a placeholder: {buy}")
    inside = [
        ("The family meeting, scripted", "What to say, minute by minute, without making anyone feel foolish."),
        ("Family plan sheet", "Safe word, the call-back rule, the payment rule, and your trusted person."),
        ("Credit freeze tracker", "Every adult and child, all five agencies, with how-to steps."),
        ("Account lockdown checklist", "Five locks, one a night: email, passwords, passkeys, phone number, alerts."),
        ("The Scam Decoder", "12 common scams, the tell for each, and the move that beats it."),
        ("Fridge card + 4 wallet cards", "Big type, made for parents and grandparents."),
        ("\"It happened\" plan", "The first 60 minutes in order, plus an incident log banks and police will ask for."),
    ]
    items = "".join(f"<li><strong>{esc(a)}.</strong> {esc(b)}</li>" for a, b in inside)
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"],
          "image": absu("/img/kit-cover.png"), "description": "A printable family plan against scams.",
          "brand": {"@type": "Brand", "name": CFG["name"]},
          "offers": {"@type": "Offer", "price": str(p["price"]), "priceCurrency": "USD", "url": buy,
                     "availability": "https://schema.org/InStock"}}
    return f"""
<script type="application/ld+json">{json.dumps(ld)}</script>
<section class="hero"><div class="wrap grid">
  <div>
    <p class="kicker">Our own product · {price(p)}</p>
    <h1>{esc(p['name'])}</h1>
    <p class="lede">Scammers now clone voices, fake caller ID and know your parents' address from data breaches. This kit turns one 15-minute family conversation into a plan everyone follows when a scary call comes in.</p>
    <p><a class="button" href="{esc(buy)}">Get the kit for {price(p)}</a></p>
    <p class="small">Printable PDF, {p['pages']} pages, US Letter. {p['refund_days']}-day refund, no hoops.</p>
  </div>
  <img class="cover" src="{u('/img/kit-cover.png')}" alt="Cover of {esc(p['name'])}" width="306" height="396">
</div></section>
<section class="wrap">
  <h2>What's inside</h2>
  <ul class="inside">{items}</ul>
  <h2>Who it's for, and who it isn't</h2>
  <p><strong>For</strong> families: adult children worried about parents, grandparents who answer every call, parents who want their kids' credit frozen, and the person everyone calls about "a weird text".</p>
  <p><strong>Not for</strong> you if you live alone and don't help anyone else with money. The <a href="{u('/')}">free checklist</a> covers you.</p>
  <h2>Honest notes</h2>
  <ul><li>Most of the facts are free online, and we say so. The kit saves you turning them into a plan your family will follow.</li>
  <li>No product can promise you'll never be scammed. This one helps your family slow down and check.</li>
  <li>General education, not legal or financial advice.</li></ul>
  <p><a class="button" href="{esc(buy)}">Get the kit for {price(p)}</a></p>
  {checker_box()}
</section>"""


def checker_page() -> str:
    link = CFG["scam_checker"]["url"]
    if is_placeholder(link):
        WARNINGS.append("scam_checker.url is a placeholder: set it to the deployed PR #8 checker "
                        "(site.json or SCAM_CHECKER_URL)")
        body = """<p>Our free "Is this a scam?" checker is coming soon. Until then, use the three tells: rush, secrecy and a strange way to pay. See two, stop, and check on your own using a number or website you look up yourself.</p>"""
    else:
        body = f'<p><a class="button" href="{esc(link)}">Open the free scam checker</a></p>'
    return f"""<section class="wrap narrow"><p class="kicker">Free tool</p><h1>Is this a scam?</h1>{body}
<p>Get the free checklist so you know the patterns before the next message arrives:</p>{email_form('checker-page')}</section>"""


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


def build() -> list[str]:
    global CFG
    CFG = load_config()
    WARNINGS.clear()
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(STATIC, OUT)
    lm = CFG["lead_magnet"]
    pages = [
        ("/", f"{CFG['name']}: {lm['title']} (free)", lm["pitch"], home(), False),
        ("/free/", f"{lm['title']} (free PDF)", lm["pitch"], home(), False),
        ("/free/thanks/", "Your checklist", "Download your checklist.", thanks(), True),
        ("/kit/", f"{CFG['product']['name']} ({price(CFG['product'])})",
         "A printable family plan against scams: meeting script, freeze trackers, scam decoder, fridge card.", kit(), False),
        ("/checker/", "Is this a scam? Free checker", "Check a suspicious text or email.", checker_page(), False),
    ]
    for p in load_dir("pages"):
        pages.append((f"/{p['slug']}/", f"{p['title']} · {CFG['name']}", p["title"],
                      f'<section class="wrap narrow"><h1>{esc(p["title"])}</h1>{markdown(p["body_md"])}</section>', False))
    for path, title, desc, body, noindex in pages:
        write(path, layout(title=title, description=desc, path=path, body=body, noindex=noindex))
    write("/404.html", layout(title="Not found", description="Page not found.", path="/404.html", noindex=True,
                              body=f'<section class="wrap narrow"><h1>Page not found</h1><p><a href="{u("/")}">Get the free checklist</a></p></section>'))
    emails()
    indexed = [p for p, *_ , noindex in pages if not noindex and p != "/free/"]
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
