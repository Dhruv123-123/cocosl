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
        if href in affiliate_links():
            return f'<a href="{esc(href)}" rel="sponsored" class="{AFFILIATE_CLICK}">{m.group(1)}</a>'
        if href in store_links():
            return f'<a href="{esc(href)}" class="{PRODUCT_CLICK}">{m.group(1)}</a>'
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
<p><a href="{u('/parents/')}">Protect Your Parents</a> · <a href="{u('/teams/')}">Training for teams</a> · <a href="{u('/newsletter/')}">Weekly Scam Alert</a> · <a href="{u('/compare/')}">Tools compared</a></p>
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
    <p><a class="button {PRODUCT_CLICK}" href="{esc(buy)}">Get the kit for {price(p)}</a></p>
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
  <p><a class="button {PRODUCT_CLICK}" href="{esc(buy)}">Get the kit for {price(p)}</a></p>
  {checker_box()}
  <div class="product">
    <img src="{u('/img/parents-cover.png')}" alt="Cover of Protect Your Parents" width="170" height="220" loading="lazy">
    <div><h2>Helping a parent?</h2>
    <p><strong>Protect Your Parents</strong> is our 20-page setup guide: every setting to change on their phone, bank and credit, plus 10 word-for-word phone scripts. Kit buyers get $10 off.</p>
    <p><a href="{u('/parents/')}">See the guide →</a></p></div>
  </div>
</section>"""


def ladder(slug: str) -> dict:
    return next(x for x in CFG.get("ladder", []) if x["slug"] == slug)


def buy_link(p: dict) -> str:
    if "example." in p["buy_url"] or is_placeholder(p["buy_url"]):
        WARNINGS.append(f"{p['slug']} buy_url is still a placeholder: {p['buy_url']}")
    return p["buy_url"]


def product_ld(p: dict, description: str) -> str:
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "image": absu(p["cover"]),
          "description": description, "brand": {"@type": "Brand", "name": CFG["name"]},
          "offers": {"@type": "Offer", "price": str(p["price"]), "priceCurrency": "USD", "url": p["buy_url"],
                     "availability": "https://schema.org/InStock"}}
    return f'<script type="application/ld+json">{json.dumps(ld)}</script>'


def parents_page() -> str:
    p = ladder("parents")
    buy = buy_link(p)
    inside = [
        ("A three-visit plan", "The conversation, the setup, then practice. Fits a holiday or a weekend."),
        ("What to say, and what not to", "Openers that work, and answers to \"I'd never fall for that\"."),
        ("40+ setup checks", "Phone, email, bank, credit and computer, in plain English: silence unknown callers, carrier PIN, bank alerts, a trusted contact, credit freezes, remote-access apps."),
        ("10 phone scripts", "Word-for-word lines for the grandchild-in-trouble call, the \"bank fraud department\", Medicare, the IRS, tech support, utility shut-offs, prizes and online romance."),
        ("Scripts for you", "Calling their bank together, the sibling who isn't worried, and a parent still talking to a scammer."),
        ("Fill-in sheets", "Family Plan, Important Numbers (official numbers included), monthly check-in tracker, phone-side card."),
        ("If it happens", "Warning signs, the first hour, and how to spot the \"recovery\" scam that follows."),
    ]
    items = "".join(f"<li><strong>{esc(a)}.</strong> {esc(b)}</li>" for a, b in inside)
    code = (f'<p class="small">Bought the {esc(CFG["product"]["name"])}? Use code <strong>{esc(p["code"])}</strong> '
            f'for ${p["code_off"]:g} off.</p>') if p.get("code") else ""
    return f"""{product_ld(p, "A setup guide and phone scripts to protect older parents from scams.")}
<section class="hero"><div class="wrap grid">
  <div>
    <p class="kicker">Our own product · {price(p)}</p>
    <h1>{esc(p['name'])}</h1>
    <p class="lede">Your parents answer the phone. Scammers know it. This {p['pages']}-page guide walks you through three short visits that make them much harder to scam, without making them feel foolish.</p>
    <p><a class="button {PRODUCT_CLICK}" href="{esc(buy)}">Get the guide for {price(p)}</a></p>
    {code}
    <p class="small">Printable PDF, US Letter. {CFG['product']['refund_days']}-day refund.</p>
  </div>
  <img class="cover" src="{u(p['cover'])}" alt="Cover of {esc(p['name'])}" width="306" height="396">
</div></section>
<section class="wrap">
  <h2>What's inside</h2>
  <ul class="inside">{items}</ul>
  <h2>Kit or guide?</h2>
  <p>The <a href="{u('/kit/')}">{esc(CFG['product']['name'])}</a> ({price(CFG['product'])}) is a whole-family plan: kids' credit freezes, a family meeting, fridge and wallet cards. <strong>Protect Your Parents</strong> goes deep on one job: setting up and coaching a parent. Many families get both; guide buyers get the kit free.</p>
  <h2>Honest notes</h2>
  <ul><li>No guide can promise your parents will never be scammed. This one helps them slow down and check.</li>
  <li>Phone menus change with updates; the guide tells you what to look for, not just where to tap.</li>
  <li>General education, not legal or financial advice.</li></ul>
  <p><a class="button {PRODUCT_CLICK}" href="{esc(buy)}">Get the guide for {price(p)}</a></p>
</section>"""


def teams_page() -> str:
    p = ladder("teams")
    buy = buy_link(p)
    inside = [
        ("25 editable slides with speaker notes", "The 3 tells, phishing, the fake boss, invoice and bank-change fraud, payroll diversion, fake IT calls and code theft, AI voice clones, QR codes, the verify rule and reporting."),
        ("3 practice scenarios", "With model answers, for pairs or breakout rooms."),
        ("A 12-question quiz", "With answer key and explanations."),
        ("Certificates and an attendance log", "Editable PowerPoint and printable PDF."),
        ("A verification policy template", "One page on bank changes, new payees, gift cards, employee data and codes."),
        ("Follow-up emails and a poster", "\"Verify before you pay\", for the office or the finance desk."),
    ]
    items = "".join(f"<li><strong>{esc(a)}.</strong> {esc(b)}</li>" for a, b in inside)
    return f"""{product_ld(p, "A ready-to-run 45-minute scam awareness training session for small teams.")}
<section class="hero"><div class="wrap grid">
  <div>
    <p class="kicker">For small businesses · {price(p)}</p>
    <h1>Spot It, Stop It: scam awareness training for your team</h1>
    <p class="lede">Most scams that hit small businesses don't hack anything. They ask a person to pay an invoice, change bank details, buy gift cards or read out a code. Run a 45-minute session yourself, no security background needed.</p>
    <p><a class="button {PRODUCT_CLICK}" href="{esc(buy)}">Get the training pack for {price(p)}</a></p>
    <p class="small">One organization, any number of employees. Zip download: PPTX, PDF.</p>
  </div>
  <img class="cover" src="{u(p['cover'])}" alt="Title slide of the Spot It, Stop It training deck" width="400" height="225">
</div></section>
<section class="wrap">
  <h2>What's inside</h2>
  <ul class="inside">{items}</ul>
  <h2>Who it's for</h2>
  <p>Owners and office managers of teams of 3 to 100, HR and finance leads, and anyone who pays invoices or runs payroll. If you already pay for a security awareness platform, you probably don't need this.</p>
  <h2>Honest notes</h2>
  <ul><li>Training reduces risk; it can't remove it. The policy template and the verify rule do the heavy lifting.</li>
  <li>It doesn't make you "compliant" with any specific law, standard or insurer. The attendance log helps you keep records.</li>
  <li>General education, not legal, compliance or financial advice.</li></ul>
  <p><a class="button {PRODUCT_CLICK}" href="{esc(buy)}">Get the training pack for {price(p)}</a></p>
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


def aff(slug: str) -> dict:
    return next(a for a in CFG["affiliates"] if a["slug"] == slug)


def aff_button(slug: str, label: str) -> str:
    a = aff(slug)
    if is_placeholder(a["url"]):
        WARNINGS.append(f"affiliate {slug} url is still a placeholder: {a['url']}")
    return (f'<a class="button {AFFILIATE_CLICK}" rel="sponsored nofollow" href="{esc(a["url"])}">{esc(label)}</a>')


COMPARE_ROWS = {
    "identity": [
        ("What it is", "An all-in-one plan: identity and credit monitoring plus device and privacy tools.",
         "Identity and credit monitoring from Gen Digital, the company behind Norton."),
        ("Good fit if", "You want one app that also covers antivirus, a VPN and passwords for the family.",
         "You mainly want identity monitoring and restoration help, and may already use Norton."),
        ("Watch for", "Plans, features and insurance limits change; check what the family plan covers for kids.",
         "Cheaper tiers may monitor only one credit bureau; first-year prices often rise at renewal."),
        ("Free trial", "Check the site: trials and money-back terms change.",
         "Check the site: trials and money-back terms change."),
    ],
    "passwords": [
        ("What it is", "Open-source password manager with a free plan for unlimited passwords on all your devices.",
         "Polished paid password manager with family plans and a free trial."),
        ("Good fit if", "You want to start free today, or want the cheapest paid family plan.",
         "You want the smoothest setup for a family that isn't techy."),
        ("Watch for", "The free plan covers the basics; sharing with a whole family needs a paid plan.",
         "No free-forever plan; set a reminder before the trial ends."),
        ("Free option", "Yes, a free plan.", "No, a free trial."),
    ],
}


def compare_table(cat: str, a: str, b: str) -> str:
    head = f"<tr><th></th><th>{esc(aff(a)['name'])}</th><th>{esc(aff(b)['name'])}</th></tr>"
    rows = "".join(f"<tr><th>{esc(k)}</th><td>{esc(x)}</td><td>{esc(y)}</td></tr>" for k, x, y in COMPARE_ROWS[cat])
    btns = (f"<tr><th></th><td>{aff_button(a, 'See ' + aff(a)['name'] + ' plans')}</td>"
            f"<td>{aff_button(b, 'See ' + aff(b)['name'] + ' plans')}</td></tr>")
    return f'<div class="scroll"><table class="compare">{head}{rows}{btns}</table></div>'


def compare_page() -> str:
    reviewed = CFG.get("compare_reviewed", "")
    return f"""<section class="wrap narrow">
<p class="kicker">Plain-English comparison · reviewed {esc(reviewed)}</p>
<h1>Identity theft protection and password managers: Aura vs LifeLock, Bitwarden vs 1Password</h1>
<p class="disclosure"><strong>Affiliate disclosure:</strong> the "See plans" buttons on this page are affiliate links. If you sign up, we may earn a commission at no extra cost to you. Nobody paid to be on this page, and we put the free options first. <a href="{u('/disclosures/')}">How we make money</a>.</p>
<h2>First, the free stuff (do this even if you buy nothing)</h2>
<ol>
<li><strong>Freeze your credit at all three bureaus</strong> (Equifax, Experian, TransUnion). It's free by law, and it blocks most new-account fraud. You can do it for your kids too.</li>
<li><strong>Check your credit reports for free</strong> at <a href="https://www.annualcreditreport.com/">AnnualCreditReport.com</a>, the official site.</li>
<li><strong>Get an IRS Identity Protection PIN</strong> at <a href="https://www.irs.gov/identity-theft-fraud-scams/get-an-identity-protection-pin">IRS.gov</a> so nobody can file taxes in your name.</li>
<li><strong>Turn on two-step sign-in</strong> for your email and bank.</li>
<li>If it happens, <a href="https://www.identitytheft.gov/">IdentityTheft.gov</a> (from the FTC) gives you a free recovery plan.</li>
</ol>
<p>A paid service can't freeze your credit better than you can, and it can't stop every scam. What it adds is <strong>convenience</strong>: alerts in one place, help with the paperwork if your identity is stolen, and insurance for some recovery costs.</p>

<h2>Password managers: Bitwarden vs 1Password</h2>
<p>Most hacked accounts start with a reused password. A password manager makes a different strong password for every site and remembers them all. For most families this is the single best security purchase, and you can start for free.</p>
{compare_table("passwords", "bitwarden", "1password")}
<p><strong>Our take:</strong> start with Bitwarden's free plan today. If the family finds it fiddly, try the 1Password trial. Either is far better than reusing passwords.</p>

<h2>Identity theft protection: Aura vs LifeLock</h2>
<p>These services watch for your details in places they shouldn't be (new credit, data breaches, the dark web), alert you, and help you recover if your identity is stolen. Both advertise identity theft insurance; check the limit and what it covers on the plan you're looking at.</p>
{compare_table("identity", "aura", "lifelock")}
<p><strong>Our take:</strong> freeze your credit first. If you then want someone watching and a team to call if it goes wrong, compare the family plans side by side, and check the renewal price, not just the first-year deal.</p>

<h2>Honest notes</h2>
<ul>
<li>Prices, plans and insurance limits change often, so we don't list prices here. Check each company's site before you buy.</li>
<li>No service can stop every scam. The habits in our <a href="{u('/free/')}">free checklist</a> do more than any app.</li>
<li>We haven't been paid to rank anyone. If that ever changes, we'll say so on this page.</li>
</ul>
<p class="small">Last reviewed {esc(reviewed)}. Spotted something out of date? Email {esc(CFG['contact_email'])}.</p>
</section>"""


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
        ("/parents/", f"{ladder('parents')['name']} ({price(ladder('parents'))})",
         "A setup guide and 10 phone scripts to protect older parents from scams.", parents_page(), False),
        ("/teams/", "Scam awareness training for small teams ($99)",
         "A ready-to-run 45-minute scam awareness session: slides, quiz, certificates.", teams_page(), False),
        ("/compare/", "Aura vs LifeLock, Bitwarden vs 1Password: plain-English comparison",
         "Identity theft protection and password managers compared in plain English, with the free options first.",
         compare_page(), False),
        ("/checker/", "Is this a scam? Free checker", "Check a suspicious text or email.", checker_page(), False),
    ]
    for p in load_dir("pages"):
        pages.append((f"/{p['slug']}/", f"{p['title']} · {CFG['name']}", p["title"],
                      f'<section class="wrap narrow"><h1>{esc(p["title"])}</h1>{markdown(p["body_md"])}</section>', False))
    pages += newsletter()
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
