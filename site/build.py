#!/usr/bin/env python3
"""Build the Money Made Simple static site (or another brand's, with SITE_ROOT; see sites/).

Standard library only, so it runs anywhere Python 3.9+ exists (your laptop,
Netlify's build image, GitHub Actions) with no installs.

    python3 site/build.py                     # writes site/public/
    SITE_URL=https://example.com python3 site/build.py
    python3 site/build.py --serve             # build, then preview on http://localhost:8080
    SITE_ROOT=sites/dinero-simple python3 site/build.py   # build another brand's site (its own
                                              # site.json, content/ and static/; UI text from site.json "ui")

Content lives in site/content/ as Markdown with a small front-matter block:
  blog/*.md      articles   (title, description, date, pillar, keyword, read_minutes)
  products/*.md  products   (title, price, buy_url, ... see the existing file)
  pages/*.md     plain pages (about, privacy, disclosures, terms)
  emails/*.md    the welcome / nurture sequence (rendered to public/emails/ for preview)
Settings (site URL, email provider, social links) are in site/site.json.
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(os.environ.get("SITE_ROOT") or Path(__file__).resolve().parent).resolve()
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
SHARED_STATIC = Path(__file__).resolve().parent / "static"  # style.css and site.js live here for every site
OUT = Path(os.environ.get("SITE_OUT") or ROOT / "public")


# --------------------------------------------------------------------- config
def load_config() -> dict:
    cfg = json.loads((ROOT / "site.json").read_text())
    # Deploy targets tell us the public URL: SITE_URL wins, then Netlify's URL.
    url = os.environ.get("SITE_URL") or os.environ.get("URL") or cfg["url"]
    cfg["url"] = url.rstrip("/")
    cfg["base_path"] = urlparse(cfg["url"]).path.rstrip("/")  # "/cocosl" on a GitHub project page
    provider = os.environ.get("EMAIL_PROVIDER")
    if provider:
        cfg["email"]["provider"] = provider
    if os.environ.get("EMAIL_FORM_ACTION"):
        cfg["email"]["action"] = os.environ["EMAIL_FORM_ACTION"]
    return cfg


CFG: dict = {}

# Every piece of interface text the generator writes itself. A site.json "ui" block overrides any key,
# which is how a site in another language (sites/dinero-simple) reuses this generator unchanged.
UI_EN: dict = {
    "lang": "en", "theme_color": "#0b1d13",
    "months": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
               "October", "November", "December"],
    "date_format": "{month} {day}, {year}",
    "nav_articles": "Articles", "nav_products": "Products", "nav_free": "Free reset", "nav_about": "About",
    "skip": "Skip to content", "home": "Home", "articles": "Articles", "guide": "Guide",
    "privacy": "Privacy", "disclosures": "Disclosures", "terms": "Terms", "links": "Links",
    "form_button": "Send me the free reset", "form_button_short": "Send it", "honeypot": "Leave this empty",
    "email_label": "Email address", "email_placeholder": "you@example.com",
    "privacy_note": "One useful email a week. Unsubscribe in one click.",
    "free_download": "Free download", "cover_of": "Cover of {title}",
    "coming_soon": "Coming soon", "launch_price": "launch price",
    "on_this_page": "On this page", "sources": "Sources", "updated": "Updated", "min_read": "min read",
    "reviewed": "Reviewed by a human editor",
    "aff_note": "This article contains affiliate links. If you sign up through them we may earn a commission at "
                "no extra cost to you.",
    "aff_how": "How we handle this", "tool_for_this": "Tool for this", "read_next": "Read next",
    "blog_title": "Articles: budgeting, investing basics, credit and money tools",
    "blog_description": "Plain-English guides for students and early-career workers: budgeting that sticks, "
                        "first-time investing, credit scores, debt payoff and money apps, with the maths shown.",
    "blog_h1": "Articles", "blog_dek": "One idea per article, explained properly, with the numbers shown. Pick a topic:",
    "pillar_title": "{label}: articles", "pillar_description": "Every {site} article on {label_lower}.",
    "products": "Products", "preview_alt": "{title} preview",
    "not_on_sale": "Not on sale yet. Join the free email and you'll hear the day it opens.",
    "waitlist_button": "Tell me when it opens", "buy_label": "Get instant access",
    "products_title": "Guides and templates",
    "products_description": "Low-cost, no-subscription money tools from {site}: guides and spreadsheets you keep.",
    "products_dek": "Small, specific tools. One payment, no subscription, files you keep. Each one has a no-hoops refund.",
    "free_title": "Free: {title}", "free_kicker": "Free PDF + checklist",
    "free_days_h": "What you'll do, one 15-minute task a day", "day": "Day {n}",
    "free_else_h": "What else you get",
    "free_else": "After the reset, one short email a week: a single money move, explained with the numbers. No hype, "
                 "no stock picks, no \"get rich\" anything. You can unsubscribe in one click from any email.",
    "thanks_title": "You're in", "thanks_description": "Your free download.",
    "thanks_h1": "You're in. Here's your reset.",
    "thanks_note": "Check your inbox too: your first email is on its way (look in Promotions or Spam if you do not see it).",
    "download": "Download {title} (PDF)",
    "thanks_start": "Start with Day 1 today. It takes about 15 minutes and you'll need your banking app.",
    "thanks_more": "Want the full system?",
    "links_title": "Links", "links_free": "Free: {title}", "links_products": "Guides and templates",
    "links_articles": "Popular articles", "links_tools": "Tools we recommend", "affiliate": "affiliate",
    "links_aff_note": "Affiliate links: we may earn a commission at no extra cost to you.",
    "home_title": "{site}: one money move a week, explained simply",
    "home_kicker": "For students and early-career workers",
    "home_h1": "Feel behind on money? Start with one move this week.",
    "home_offer": "Get <strong>{title}</strong> free: seven 15-minute tasks that get your money organised in a week.",
    "home_topics": "Start with a topic", "home_latest": "Latest articles", "home_all": "All articles",
    "home_tools": "The tools", "home_how": "How we make this", "n_articles": "{n} articles",
    "home_promise": [
        ["Specific, not hype", "Every article and email is one idea you can use this week, with the maths shown. "
                               "No stock picks, no crypto pumps, no income claims."],
        ["Checked by a human", "We use AI tools for visuals and drafts. A human picks every topic, checks every "
                               "number against primary sources (IRS, CFPB, FDIC, Investor.gov) and approves every post."],
        ["Honest about money", "Some links are affiliate links and they're always labelled. Products have a no-hoops "
                               "refund. Testimonials only ever come from real buyers, quoted word for word."]],
    "nf_title": "Page not found", "nf_h1": "That page wandered off.",
    "nf_dek": "Try the <a href=\"{blog}\">articles</a> or grab the <a href=\"{free}\">free reset</a>.",
}


def T(key: str, **kw) -> str:
    """Interface text: site.json "ui" first, English default second."""
    val = (CFG.get("ui") or {}).get(key, UI_EN[key])
    return val.format(**kw) if kw and isinstance(val, str) else val


def u(path: str) -> str:
    """Site-relative link that also works under a GitHub Pages sub-path."""
    if path.startswith(("http://", "https://", "mailto:", "#")):
        return path
    if CFG.get("_absolute_links"):
        return absu(path)
    return CFG["base_path"] + "/" + path.lstrip("/")


def absu(path: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    return CFG["url"] + "/" + path.lstrip("/")


esc = html.escape


# ------------------------------------------------------------------ markdown
def parse_front_matter(text: str) -> tuple[dict, str]:
    meta: dict = {}
    if text.startswith("---\n"):
        end = text.index("\n---", 4)
        for line in text[4:end].splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            k, _, v = line.partition(":")
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                meta[k.strip()] = [x.strip().strip('"') for x in v[1:-1].split(",") if x.strip()]
            else:
                meta[k.strip()] = v.strip('"')
        text = text[end + 4:].lstrip("\n")
    return meta, text


def inline(s: str) -> str:
    codes: list[str] = []

    def keep_code(m):
        codes.append(f"<code>{esc(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", keep_code, s)
    s = esc(s, quote=False)

    def link(m):
        text, href = m.group(1), m.group(2)
        ext = href.startswith("http") and urlparse(href).netloc not in CFG["url"]
        rel = ' rel="noopener"' if ext else ""
        if "sponsored" in href or "/go/" in href:
            rel = ' rel="sponsored noopener"'
        return f'<a href="{esc(u(href))}"{rel}>{text}</a>'

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)
    return s


def slug_id(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-")


def markdown(text: str, shortcodes=None) -> tuple[str, list[tuple[str, str]]]:
    """Small Markdown subset: headings, paragraphs, lists, quotes, tables, hr, raw HTML,
    and {{shortcode}} lines. Returns (html, [(id, h2 text)])."""
    lines = text.splitlines()
    out: list[str] = []
    toc: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        st = line.strip()
        if not st:
            i += 1
            continue
        m = re.fullmatch(r"\{\{\s*([\w:-]+)\s*\}\}", st)
        if m:
            out.append(shortcodes(m.group(1)) if shortcodes else "")
            i += 1
            continue
        if st.startswith("<"):
            block = []
            while i < len(lines) and lines[i].strip():
                block.append(lines[i])
                i += 1
            out.append("\n".join(block))
            continue
        m = re.match(r"(#{1,4})\s+(.*)", st)
        if m:
            level = len(m.group(1))
            body = inline(m.group(2))
            hid = slug_id(m.group(2))
            if level == 2:
                toc.append((hid, body))
            out.append(f'<h{level} id="{hid}">{body}</h{level}>')
            i += 1
            continue
        if re.fullmatch(r"-{3,}|\*{3,}", st):
            out.append("<hr>")
            i += 1
            continue
        if st.startswith(">"):
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip()[1:].strip())
                i += 1
            inner, _ = markdown("\n".join(block), shortcodes)
            out.append(f"<blockquote>{inner}</blockquote>")
            continue
        if st.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r":?-+:?", c) for c in r)]
            t = ["<div class=\"table\"><table><thead><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in body:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        lm = re.match(r"([-*]|\d+[.)])\s+", st)
        if lm:
            ordered = lm.group(1)[0].isdigit()
            items: list[str] = []
            while i < len(lines):
                s2 = lines[i].strip()
                m2 = re.match(r"([-*]|\d+[.)])\s+(.*)", s2)
                if m2 and (m2.group(1)[0].isdigit()) == ordered:
                    items.append(m2.group(2))
                elif s2 and items and lines[i].startswith(("  ", "\t")):
                    items[-1] += " " + s2
                else:
                    break
                i += 1
            tag = "ol" if ordered else "ul"
            cls = ' class="checks"' if not ordered and all(x.startswith("[ ]") for x in items) else ""
            lis = "".join(f"<li>{inline(x[3:].strip() if cls else x)}</li>" for x in items)
            out.append(f"<{tag}{cls}>{lis}</{tag}>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r"(#{1,4}\s|[-*]\s|\d+[.)]\s|>|\||<|\{\{)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        joined = ""
        for k, ln in enumerate(para):  # keep short sign-off lines ("Talk soon,") on their own line
            sep = "" if k == 0 else ("<br>" if para[k - 1].endswith(",") and len(para[k - 1]) < 30 else " ")
            joined += sep + inline(ln)
        out.append(f"<p>{joined}</p>")
    return "\n".join(out), toc


def extract_faq(md: str) -> list[tuple[str, str]]:
    """Pull '### Question' + answer pairs from a '## ...FAQ...' or '## Common questions' section."""
    m = re.search(r"^## (?:FAQ|Frequently asked questions|Common questions|Preguntas frecuentes|Dudas comunes)[^\n]*\n(.*?)(?=^## |\Z)", md,
                  re.S | re.M | re.I)
    if not m:
        return []
    pairs = re.findall(r"^### (.+?)\n(.*?)(?=^### |\Z)", m.group(1), re.S | re.M)
    clean = lambda s: re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"\*\*?|`", "", s)).strip()
    return [(clean(q), " ".join(clean(a).split())) for q, a in pairs]


# ------------------------------------------------------------------- content
def load_dir(name: str) -> list[dict]:
    items = []
    for p in sorted((CONTENT / name).glob("*.md")):
        meta, body = parse_front_matter(p.read_text())
        meta.setdefault("slug", re.sub(r"^\d+-", "", p.stem))
        meta["body"] = body
        meta["file"] = p.name
        items.append(meta)
    return items


# ----------------------------------------------------------------- templates
def email_form(source: str, button: str = "", compact: bool = False) -> str:
    button = button or T("form_button")
    e = CFG["email"]
    provider = e.get("provider", "netlify")
    thanks = u("/free/thanks/")
    field = e.get("email_field") or {
        "kit": "email_address", "mailerlite": "fields[email]", "buttondown": "email",
        "factory": "email", "netlify": "email"}.get(provider, "email")
    extra = ""
    attrs = ""
    if provider == "netlify":
        action = thanks
        attrs = ' name="lead-magnet" data-netlify="true" netlify-honeypot="website"'
        extra = '<input type="hidden" name="form-name" value="lead-magnet">'
    elif provider == "factory":
        action = e.get("action") or f"http://localhost:8000/subscribe/{CFG.get('slug', 'money-made-simple')}"
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
    note = esc(e.get("privacy_note", T("privacy_note")))
    return f"""<form class="signup-form{' compact' if compact else ''}" method="post" action="{esc(action)}"{attrs} data-thanks="{thanks}">
  {extra}
  <label class="hp" aria-hidden="true">{esc(T("honeypot"))} <input type="text" name="website" tabindex="-1" autocomplete="off"></label>
  <label class="sr" for="em-{esc(source)}">{esc(T("email_label"))}</label>
  <input id="em-{esc(source)}" type="email" name="{esc(field)}" required autocomplete="email" inputmode="email" placeholder="{esc(T("email_placeholder"))}">
  <button type="submit">{esc(button)}</button>
</form>
<p class="form-note">{note} <a href="{u('/privacy/')}">{esc(T("privacy"))}</a>.</p>"""


def magnet_box(source: str) -> str:
    lm = CFG["lead_magnet"]
    return f"""<aside class="magnet" aria-label="{esc(T('free_download'))}">
  <img src="{u('/img/lead-magnet-cover.png')}" alt="{esc(T('cover_of', title=lm['title']))}" width="150" height="194" loading="lazy">
  <div>
    <p class="kicker">{esc(T('free_download'))}</p>
    <h2 class="magnet-title">{esc(lm['title'])}</h2>
    <p>{esc(lm['pitch'])}</p>
    {email_form(source)}
  </div>
</aside>"""


def product_card(p: dict) -> str:
    price = price_html(p)
    return f"""<a class="product-card" href="{u(f"/products/{p['slug']}/")}">
  <img src="{u(p['image'])}" alt="" width="640" height="360" loading="lazy">
  <span class="pc-body"><span class="pc-title">{esc(p['title'])}</span>
  <span class="pc-short">{esc(p['short'])}</span>{price}</span>
</a>"""


def price_html(p: dict) -> str:
    if p.get("status") == "coming-soon":
        return f'<span class="price soon">{esc(T("coming_soon"))}</span>'
    if p.get("sale_price"):
        return (f'<span class="price"><s>${esc(p["price"])}</s> ${esc(p["sale_price"])} '
                f'<small>{esc(p.get("sale_label", T("launch_price")))}</small></span>')
    return f'<span class="price">${esc(p["price"])}</span>'


def shortcode_factory(products: dict, source: str):
    def sc(name: str) -> str:
        if name == "signup":
            return magnet_box(source)
        if name.startswith("product:"):
            p = products.get(name.split(":", 1)[1])
            return f'<div class="inline-product">{product_card(p)}</div>' if p else ""
        if name == "disclaimer":
            return f'<p class="disclaimer">{esc(CFG["disclaimer"])}</p>'
        return ""
    return sc


def layout(*, title: str, description: str, path: str, body: str, og_type: str = "website",
           jsonld: list | None = None, image: str = "/img/og-default.png", noindex: bool = False,
           extra_head: str = "") -> str:
    full_title = title if CFG["name"] in title else f"{title} · {CFG['name']}"
    nav = "".join(
        f'<a href="{u(href)}"{" aria-current=page" if path.startswith(href) and href != "/" else ""}>{esc(t)}</a>'
        for t, href in [(T("nav_articles"), "/blog/"), (T("nav_products"), "/products/"),
                        (T("nav_free"), "/free/"), (T("nav_about"), "/about/")])
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
                 for x in (jsonld or []))
    soc = " · ".join(f'<a href="{esc(h)}" rel="me noopener">{esc(n)}</a>' for n, h in CFG["socials"].items())
    analytics = CFG.get("analytics_snippet", "")
    return f"""<!doctype html>
<html lang="{esc(T('lang'))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(absu(path))}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<meta property="og:site_name" content="{esc(CFG['name'])}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(absu(path))}">
<meta property="og:image" content="{esc(absu(image))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{esc(T('theme_color'))}">
<link rel="icon" type="image/png" href="{u('/img/favicon.png')}">
<link rel="apple-touch-icon" href="{u('/img/apple-touch-icon.png')}">
<link rel="alternate" type="application/rss+xml" title="{esc(CFG['name'])}" href="{u('/feed.xml')}">
<link rel="stylesheet" href="{u('/style.css')}">{theme_css()}
{ld}{extra_head}{analytics}
</head>
<body>
<a class="skip" href="#main">{esc(T('skip'))}</a>
<header class="site-head">
  <div class="wrap head-inner">
    <a class="brand" href="{u('/')}"><img src="{u('/img/logo.png')}" alt="" width="36" height="36">{esc(CFG['name'])}</a>
    <nav aria-label="Main">{nav}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
  <div class="wrap">
    <p class="foot-brand"><strong>{esc(CFG['name'])}</strong> · {esc(CFG['tagline'])}</p>
    <p>{soc}</p>
    <p><a href="{u('/privacy/')}">{esc(T('privacy'))}</a> · <a href="{u('/disclosures/')}">{esc(T('disclosures'))}</a> · <a href="{u('/terms/')}">{esc(T('terms'))}</a> · <a href="{u('/links/')}">{esc(T('links'))}</a> · <a href="{u('/feed.xml')}">RSS</a></p>
    <p class="small">{esc(CFG['disclaimer'])}</p>
    <p class="small">{esc(CFG['ai_disclosure'])}</p>
    <p class="small">&copy; {date.today().year} {esc(CFG['name'])}</p>
  </div>
</footer>
<script src="{u('/site.js')}" defer></script>
</body>
</html>
"""


def org_ld() -> dict:
    return {"@context": "https://schema.org", "@type": "Organization", "name": CFG["name"],
            "url": CFG["url"] + "/", "logo": absu("/img/logo.png"), "sameAs": list(CFG["socials"].values())}


def fmt_date(d: str) -> str:
    dt = datetime.strptime(d, "%Y-%m-%d")
    return T("date_format", month=T("months")[dt.month - 1], day=dt.day, year=dt.year)


# --------------------------------------------------------------------- pages
def write(path: str, text: str) -> None:
    dest = OUT / path.lstrip("/")
    if path.endswith("/"):
        dest = dest / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)


def build() -> list[str]:
    global CFG
    CFG = load_config()
    if OUT.exists():
        shutil.rmtree(OUT)
    if STATIC != SHARED_STATIC:  # another brand's site: shared CSS/JS first, its own images and downloads on top
        OUT.mkdir(parents=True)
        for name in ("style.css", "site.js"):
            shutil.copy2(SHARED_STATIC / name, OUT / name)
    shutil.copytree(STATIC, OUT, dirs_exist_ok=True)
    urls: list[tuple[str, str]] = []

    posts = sorted(load_dir("blog"), key=lambda p: p["date"], reverse=True)
    products_list = [p for p in load_dir("products") if p.get("status") != "draft"]
    products_list.sort(key=lambda p: int(p.get("order", 99)))
    products = {p["slug"]: p for p in products_list}
    pages = load_dir("pages")
    pillars = CFG["pillars"]

    # ---- articles
    for p in posts:
        path = f"/blog/{p['slug']}/"
        body_html, toc = markdown(p["body"], shortcode_factory(products, f"blog-{p['slug']}"))
        faq = extract_faq(p["body"])
        related = [x for x in posts if x is not p and x.get("pillar") == p.get("pillar")][:2]
        related += [x for x in posts if x is not p and x not in related][: 3 - len(related)]
        prod = products.get(p.get("product", "")) or (products_list[0] if products_list else None)
        toc_html = ""
        if len(toc) >= 3:
            toc_html = f'<nav class="toc" aria-label="{esc(T("on_this_page"))}"><p>{esc(T("on_this_page"))}</p><ol>' + "".join(
                f'<li><a href="#{i}">{t}</a></li>' for i, t in toc) + "</ol></nav>"
        ld = [{
            "@context": "https://schema.org", "@type": "Article", "headline": p["title"],
            "description": p["description"], "datePublished": p["date"],
            "dateModified": p.get("updated", p["date"]), "mainEntityOfPage": absu(path),
            "image": absu(p.get("image", "/img/og-default.png")),
            "author": {"@type": "Organization", "name": CFG["name"], "url": CFG["url"] + "/"},
            "publisher": org_ld(), "keywords": p.get("keyword", "")},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": T("home"), "item": CFG["url"] + "/"},
                {"@type": "ListItem", "position": 2, "name": T("articles"), "item": absu("/blog/")},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": absu(path)}]}]
        if faq:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq]})
        rel_html = "".join(
            f'<li><a href="{u(f"/blog/{x["slug"]}/")}">{esc(x["title"])}</a></li>' for x in related)
        sources = ""
        if p.get("sources"):
            sources = f'<section class="sources"><h2>{esc(T("sources"))}</h2><ul>' + "".join(
                f'<li><a href="{esc(s)}" rel="noopener">{esc(urlparse(s).netloc + urlparse(s).path)}</a></li>'
                for s in p["sources"]) + "</ul></section>"
        updated = f' · {esc(T("updated"))} {fmt_date(p["updated"])}' if p.get("updated") else ""
        aff = (f'<p class="aff-note">{esc(T("aff_note"))} <a href="{u("/disclosures/")}">{esc(T("aff_how"))}</a>.</p>'
               if p.get("affiliate") == "yes" else "")
        body = f"""<article class="wrap article">
  <p class="crumbs"><a href="{u('/')}">{esc(T('home'))}</a> / <a href="{u('/blog/')}">{esc(T('articles'))}</a> / <span>{esc(pillars.get(p.get('pillar', ''), T('guide')))}</span></p>
  <h1>{esc(p['title'])}</h1>
  <p class="dek">{esc(p['description'])}</p>
  <p class="meta">{fmt_date(p['date'])}{updated} · {esc(p.get('read_minutes', '6'))} {esc(T('min_read'))} · {esc(T('reviewed'))}</p>
  {aff}
  {toc_html}
  <div class="prose">
{body_html}
  </div>
  {sources}
  <p class="disclaimer">{esc(CFG['disclaimer'])}</p>
  {magnet_box(f"blog-{p['slug']}-end")}
  {f'<section class="next"><h2>{esc(T("tool_for_this"))}</h2>{product_card(prod)}</section>' if prod else ''}
  <section class="next"><h2>{esc(T('read_next'))}</h2><ul class="related">{rel_html}</ul></section>
</article>"""
        write(path, layout(title=p.get("seo_title", p["title"]), description=p["description"], path=path,
                           body=body, og_type="article", jsonld=ld, image=p.get("image", "/img/og-default.png")))
        urls.append((path, p.get("updated", p["date"])))

    # ---- blog index (+ one page per pillar)
    def post_list(items):
        return "".join(f"""<li class="post">
  <p class="post-pillar">{esc(pillars.get(x.get('pillar', ''), ''))}</p>
  <h2><a href="{u(f"/blog/{x['slug']}/")}">{esc(x['title'])}</a></h2>
  <p>{esc(x['description'])}</p>
  <p class="meta">{fmt_date(x['date'])} · {esc(x.get('read_minutes', '6'))} {esc(T('min_read'))}</p>
</li>""" for x in items)

    chips = "".join(f'<a class="chip" href="{u(f"/blog/{k}/")}">{esc(v)}</a>' for k, v in pillars.items())
    write("/blog/", layout(
        title=T("blog_title"), description=T("blog_description"),
        path="/blog/", jsonld=[org_ld()], body=f"""<section class="wrap">
  <h1>{esc(T('blog_h1'))}</h1>
  <p class="dek">{esc(T('blog_dek'))}</p>
  <p class="chips">{chips}</p>
  <ul class="posts">{post_list(posts)}</ul>
</section>"""))
    urls.append(("/blog/", posts[0]["date"]))
    for key, label in pillars.items():
        items = [x for x in posts if x.get("pillar") == key]
        path = f"/blog/{key}/"
        write(path, layout(title=T("pillar_title", label=label),
                           description=T("pillar_description", site=CFG["name"], label_lower=label.lower()),
                           path=path, body=f"""<section class="wrap">
  <p class="crumbs"><a href="{u('/blog/')}">{esc(T('articles'))}</a></p>
  <h1>{esc(label)}</h1>
  <p class="chips">{chips}</p>
  <ul class="posts">{post_list(items)}</ul>
</section>"""))
        urls.append((path, items[0]["date"] if items else posts[0]["date"]))

    # ---- products
    for p in products_list:
        path = f"/products/{p['slug']}/"
        body_html, _ = markdown(p["body"], shortcode_factory(products, f"product-{p['slug']}"))
        faq = extract_faq(p["body"])
        if p.get("status") == "coming-soon":
            buy = (f'<p class="buy-note">{esc(T("not_on_sale"))}</p>'
                   f'{email_form(f"waitlist-{p["slug"]}", T("waitlist_button"))}')
        else:
            buy = (f'<a class="btn big" href="{esc(p["buy_url"])}" rel="noopener" data-buy="{esc(p["slug"])}">'
                   f'{esc(p.get("buy_label", T("buy_label")))}</a>'
                   f'<p class="buy-note">{esc(p.get("guarantee", ""))}</p>')
        ld = [{"@context": "https://schema.org", "@type": "Product", "name": p["title"],
               "description": p["short"], "image": absu(p["image"]), "brand": {"@type": "Brand", "name": CFG["name"]},
               **({"offers": {"@type": "Offer", "price": p.get("sale_price") or p["price"], "priceCurrency": "USD",
                              "availability": "https://schema.org/InStock", "url": p["buy_url"]}}
                  if p.get("status") != "coming-soon" else {})}]
        if faq:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
        includes = "".join(f"<li>{inline(x)}</li>" for x in p.get("includes", []))
        body = f"""<article class="wrap product">
  <p class="crumbs"><a href="{u('/products/')}">{esc(T('products'))}</a></p>
  <div class="product-hero">
    <img src="{u(p['image'])}" alt="{esc(T('preview_alt', title=p['title']))}" width="640" height="360">
    <div>
      <h1>{esc(p['title'])}</h1>
      <p class="dek">{esc(p['short'])}</p>
      {price_html(p)}
      <ul class="checks">{includes}</ul>
      {buy}
    </div>
  </div>
  <div class="prose">
{body_html}
  </div>
  <div class="buy-again">{price_html(p)}{buy}</div>
  <p class="disclaimer">{esc(CFG['disclaimer'])}</p>
</article>"""
        write(path, layout(title=p.get("seo_title", p["title"]), description=p["short"], path=path, body=body,
                           og_type="product", jsonld=ld, image=p["image"]))
        urls.append((path, p.get("updated", date.today().isoformat())))
    write("/products/", layout(
        title=T("products_title"), path="/products/",
        description=T("products_description", site=CFG["name"]),
        body=f"""<section class="wrap">
  <h1>{esc(T('products_title'))}</h1>
  <p class="dek">{esc(T('products_dek'))}</p>
  <div class="product-grid">{''.join(product_card(p) for p in products_list)}</div>
  {magnet_box('products-index')}
</section>"""))
    urls.append(("/products/", date.today().isoformat()))

    # ---- static pages
    for pg in pages:
        path = f"/{pg['slug']}/"
        body_html, _ = markdown(pg["body"], shortcode_factory(products, f"page-{pg['slug']}"))
        write(path, layout(title=pg["title"], description=pg.get("description", pg["title"]), path=path,
                           body=f'<article class="wrap article"><h1>{esc(pg["title"])}</h1><div class="prose">{body_html}</div></article>'))
        urls.append((path, pg.get("updated", date.today().isoformat())))

    # ---- lead magnet landing + thanks
    lm = CFG["lead_magnet"]
    days = "".join(f"<li><strong>{esc(T('day', n=i))}:</strong> {esc(d)}</li>" for i, d in enumerate(lm["days"], 1))
    write("/free/", layout(
        title=T("free_title", title=lm["title"]), path="/free/", description=lm["pitch"],
        body=f"""<section class="wrap landing">
  <div class="landing-grid">
    <div>
      <p class="kicker">{esc(T('free_kicker'))}</p>
      <h1>{esc(lm['headline'])}</h1>
      <p class="dek">{esc(lm['pitch'])}</p>
      {email_form('free-page')}
    </div>
    <img class="cover" src="{u('/img/lead-magnet-cover.png')}" alt="{esc(T('cover_of', title=lm['title']))}" width="300" height="388">
  </div>
  <h2>{esc(T('free_days_h'))}</h2>
  <ol class="days">{days}</ol>
  <h2>{esc(T('free_else_h'))}</h2>
  <p>{esc(T('free_else'))}</p>
  {magnet_box('free-page-bottom')}
</section>"""))
    urls.append(("/free/", date.today().isoformat()))
    write("/free/thanks/", layout(
        title=T("thanks_title"), path="/free/thanks/", noindex=True, description=T("thanks_description"),
        body=f"""<section class="wrap landing thanks">
  <h1>{esc(T('thanks_h1'))}</h1>
  <p class="dek">{esc(CFG['email'].get('thanks_note', T('thanks_note')))}</p>
  <p><a class="btn big" href="{u('/downloads/' + lm['file'])}" download>{esc(T('download', title=lm['title']))}</a></p>
  <p>{esc(T('thanks_start'))}</p>
  <h2>{esc(T('thanks_more'))}</h2>
  <div class="product-grid">{''.join(product_card(p) for p in products_list[:2])}</div>
</section>"""))

    # ---- link in bio (site.json "links_featured": article slugs to pin; default is the 4 newest)
    by_slug = {p["slug"]: p for p in posts}
    featured = [by_slug[x] for x in CFG.get("links_featured", []) if x in by_slug] or posts[:4]
    links = "".join(f'<a class="lb-link" href="{u(f"/products/{p["slug"]}/")}"><span>{esc(p["title"])}</span>{price_html(p)}</a>'
                    for p in products_list)
    links += f'<h2 class="lb-h">{esc(T("links_articles"))}</h2>' + "".join(f'<a class="lb-link" href="{u(f"/blog/{p["slug"]}/")}"><span>{esc(p["title"])}</span></a>'
                     for p in featured)
    aff = "".join(f'<a class="lb-link" href="{esc(a["url"])}" rel="sponsored noopener"><span>{esc(a["name"])}</span><small>{esc(T("affiliate"))}</small></a>'
                  for a in CFG.get("affiliates", []))
    write("/links/", layout(
        title=T("links_title"), path="/links/", description=CFG["tagline"],
        body=f"""<section class="linkbio">
  <img class="avatar" src="{u('/img/avatar.jpg')}" alt="" width="104" height="104">
  <h1>{esc(CFG['name'])}</h1>
  <p class="dek">{esc(CFG['tagline'])}</p>
  <div class="lb-signup"><h2>{esc(T('links_free', title=lm['title']))}</h2><p>{esc(lm['short'])}</p>{email_form('link-in-bio', T('form_button_short'), compact=True)}</div>
  <h2 class="lb-h">{esc(T('links_products'))}</h2>{links}
  {f'<h2 class="lb-h">{esc(T("links_tools"))}</h2>{aff}<p class="small">{esc(T("links_aff_note"))}</p>' if aff else ''}
</section>"""))
    urls.append(("/links/", date.today().isoformat()))

    # ---- home
    latest = "".join(f"""<li class="post"><p class="post-pillar">{esc(pillars.get(x.get('pillar',''),''))}</p>
<h3><a href="{u(f"/blog/{x['slug']}/")}">{esc(x['title'])}</a></h3><p>{esc(x['description'])}</p></li>""" for x in posts[:6])
    pillar_cards = "".join(
        f'<a class="pillar" href="{u(f"/blog/{k}/")}"><span class="pillar-n">{esc(T("n_articles", n=len([x for x in posts if x.get("pillar") == k])))}</span><strong>{esc(v)}</strong></a>'
        for k, v in pillars.items())
    home_ld = [org_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": CFG["name"],
                          "url": CFG["url"] + "/"}]
    write("/", layout(
        title=T("home_title", site=CFG["name"]), path="/", jsonld=home_ld,
        description=CFG["description"],
        body=f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="kicker">{esc(T('home_kicker'))}</p>
      <h1>{esc(T('home_h1'))}</h1>
      <p class="dek">{esc(CFG['description'])}</p>
      <div class="hero-form"><p class="hero-offer">{T('home_offer', title=esc(lm['title']))}</p>{email_form('home-hero')}</div>
    </div>
    <img class="cover" src="{u('/img/lead-magnet-cover.png')}" alt="{esc(T('cover_of', title=lm['title']))}" width="300" height="388">
  </div>
</section>
<section class="wrap">
  <h2 class="section-h">{esc(T('home_topics'))}</h2>
  <div class="pillars">{pillar_cards}</div>
</section>
<section class="wrap">
  <h2 class="section-h">{esc(T('home_latest'))}</h2>
  <ul class="posts grid">{latest}</ul>
  <p><a class="btn ghost" href="{u('/blog/')}">{esc(T('home_all'))}</a></p>
</section>
<section class="band">
  <div class="wrap">
    <h2 class="section-h">{esc(T('home_tools'))}</h2>
    <div class="product-grid">{''.join(product_card(p) for p in products_list)}</div>
  </div>
</section>
<section class="wrap promise">
  <h2 class="section-h">{esc(T('home_how'))}</h2>
  <div class="three">
    {''.join(f'<div><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in T('home_promise'))}
  </div>
</section>"""))
    urls.append(("/", posts[0]["date"]))

    # ---- 404
    (OUT / "404.html").write_text(layout(
        title=T("nf_title"), path="/404.html", noindex=True, description=T("nf_title"),
        body=f'<section class="wrap landing"><h1>{esc(T("nf_h1"))}</h1><p class="dek">{T("nf_dek", blog=u("/blog/"), free=u("/free/"))}</p></section>'))

    # ---- email sequence preview (noindex, for you to proofread)
    emails = load_dir("emails")
    rows = []
    for e in emails:
        body_html, _ = markdown(e["body"])
        path = f"/emails/{e['slug']}/"
        write(path, layout(title=f"Email {e['order']}: {e['subject']}", path=path, noindex=True,
                           description="Email preview",
                           body=f"""<article class="wrap article email-preview">
  <p class="crumbs"><a href="{u('/emails/')}">Email sequence</a> · send on day {esc(e['day'])}</p>
  <p class="meta"><strong>Subject:</strong> {esc(e['subject'])}<br><strong>Preview text:</strong> {esc(e.get('preheader', ''))}</p>
  <div class="email-body prose">{body_html}</div>
</article>"""))
        rows.append(f"<tr><td>{esc(e['order'])}</td><td>Day {esc(e['day'])}</td><td><a href=\"{u(path)}\">{esc(e['subject'])}</a></td><td>{esc(e.get('goal', ''))}</td></tr>")
    export = []
    CFG["_absolute_links"] = True
    for e in emails:
        body_abs, _ = markdown(e["body"])
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f"{m.group(1)} ({absu(m.group(2))})", e["body"])
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text).strip() + "\n"
        export.append({"order": int(e["order"]), "send_on_day": int(e["day"]), "subject": e["subject"],
                       "preheader": e.get("preheader", ""), "goal": e.get("goal", ""), "html": body_abs,
                       "text": text})
        (OUT / "emails" / e["slug"] / "email.html").write_text(email_html(e, body_abs))
        (OUT / "emails" / e["slug"] / "email.txt").write_text(text)
    CFG["_absolute_links"] = False
    (OUT / "emails" / "sequence.json").write_text(json.dumps(export, indent=2, ensure_ascii=False))
    write("/emails/", layout(title="Email sequence preview", path="/emails/", noindex=True, description="Preview",
                             body=f'<section class="wrap"><h1>Welcome and nurture sequence</h1><p class="dek">Preview only (not linked, not indexed). Copy these into your email provider; see site/README.md.</p><div class="table"><table><thead><tr><th>#</th><th>Send</th><th>Subject</th><th>Job</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>'))

    # ---- sitemap, robots, feed
    sm = "".join(f"<url><loc>{esc(absu(p))}</loc><lastmod>{d}</lastmod></url>" for p, d in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: {u('/emails/')}\nDisallow: {u('/free/thanks/')}\n"
                                    f"Sitemap: {absu('/sitemap.xml')}\n")
    items = "".join(f"""<item><title>{esc(p['title'])}</title><link>{absu(f"/blog/{p['slug']}/")}</link>
<guid>{absu(f"/blog/{p['slug']}/")}</guid><pubDate>{datetime.strptime(p['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc).strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>
<description>{esc(p['description'])}</description></item>""" for p in posts)
    (OUT / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{esc(CFG['name'])}</title><link>{CFG['url']}/</link>
<description>{esc(CFG['description'])}</description>{items}</channel></rss>
""")
    # Netlify Forms needs a static copy of the form to detect it at deploy time (the pages above have it).
    return [p for p, _ in urls]


EMAIL_COLORS = {"ink": "#0b1d13", "paper": "#f4f1e8", "line": "#d9d3c3", "tint": "#eaf6ef", "gold": "#f2b134",
                "gold-t": "#fdf3dd", "green-d": "#1a7a45", "muted": "#4b5a51"}


def theme_css() -> str:
    """site.json "colors" overrides the stylesheet's :root variables (ink, paper, green, green-d, gold...)."""
    colors = CFG.get("colors") or {}
    if not colors:
        return ""
    return "<style>:root{" + "".join(f"--{k}:{v};" for k, v in colors.items()) + "}</style>"


def email_html(e: dict, body: str) -> str:
    """A plain, inline-styled email body that survives every email client. Paste into your provider's
    HTML editor; the provider adds the unsubscribe link and postal address footer."""
    c = {**EMAIL_COLORS, **(CFG.get("colors") or {})}
    body = re.sub(r"<h(\d)[^>]*>", r'<h\1 style="font-size:20px;margin:24px 0 8px">', body)
    body = body.replace("<p>", '<p style="margin:0 0 16px">')
    body = body.replace("<table>", '<table style="border-collapse:collapse;width:100%;font-size:15px;margin:0 0 16px">')
    body = body.replace("<th>", f'<th style="border:1px solid {c["line"]};padding:6px 8px;text-align:left;background:{c["tint"]}">')
    body = body.replace("<td>", f'<td style="border:1px solid {c["line"]};padding:6px 8px">')
    body = body.replace("<blockquote>", f'<blockquote style="margin:0 0 16px;padding:8px 14px;border-left:4px solid {c["gold"]};background:{c["gold-t"]}">')
    body = body.replace("<a ", f'<a style="color:{c["green-d"]};font-weight:600" ')
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(e['subject'])}</title></head>
<body style="margin:0;background:{c["paper"]}">
<span style="display:none;max-height:0;overflow:hidden">{esc(e.get('preheader', ''))}</span>
<div style="max-width:560px;margin:0 auto;padding:24px 20px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:{c["ink"]};background:#ffffff">
{body}
<p style="margin:24px 0 0;font-size:12px;color:{c["muted"]}">{esc(CFG['disclaimer'])}</p>
</div></body></html>
"""


def serve(port: int = 8080) -> None:
    import functools
    import http.server
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print(f"Serving {OUT} on http://localhost:{port}{CFG['base_path'] or ''}/")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    pages = build()
    if CFG["email"]["provider"] == "netlify" and os.environ.get("GITHUB_ACTIONS"):
        print("WARNING: email provider is 'netlify', but this build is for GitHub Pages, where Netlify Forms "
              "don't exist. Set the EMAIL_PROVIDER and EMAIL_FORM_ACTION repository variables (see site/README.md).")
    print(f"Built {len(pages)} indexed pages into {OUT} for {CFG['url']}"
          f" (email provider: {CFG['email']['provider']})")
    if "--serve" in sys.argv:
        serve()
