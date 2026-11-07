#!/usr/bin/env python3
"""Build the Money Made Simple static site.

Standard library only, so it runs anywhere Python 3.9+ exists (your laptop,
Netlify's build image, GitHub Actions) with no installs.

    python3 site/build.py                     # writes site/public/
    SITE_URL=https://example.com python3 site/build.py
    python3 site/build.py --serve             # build, then preview on http://localhost:8080

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
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
OUT = Path(os.environ.get("SITE_OUT") or ROOT / "public")


# --------------------------------------------------------------------- config
def load_config() -> dict:
    cfg = json.loads((ROOT / "site.json").read_text())
    # Deploy targets tell us the public URL: SITE_URL wins, then Netlify's URL.
    url = os.environ.get("SITE_URL") or os.environ.get("URL") or cfg["url"]
    cfg["url"] = url.rstrip("/")
    cfg["base_path"] = urlparse(cfg["url"]).path.rstrip("/")  # "/cocosl" on a GitHub project page
    # One place to paste approved affiliate links: site/go-links.json (also used by /go/<slug>/ redirects).
    go_file = ROOT / "go-links.json"
    cfg["go_links"] = json.loads(go_file.read_text())["links"] if go_file.exists() else {}
    for key, prog in cfg.get("programs", {}).items():
        go = cfg["go_links"].get(key.replace("_", "-"), {})
        if not prog.get("affiliate_url") and go.get("affiliate_url"):
            prog["affiliate_url"] = go["affiliate_url"]
    cfg.setdefault("analytics", {})
    if "PLAUSIBLE_DOMAIN" in os.environ:  # empty string turns analytics off
        cfg["analytics"]["plausible_domain"] = os.environ["PLAUSIBLE_DOMAIN"]
    provider = os.environ.get("EMAIL_PROVIDER")
    if provider:
        cfg["email"]["provider"] = provider
    if os.environ.get("EMAIL_FORM_ACTION"):
        cfg["email"]["action"] = os.environ["EMAIL_FORM_ACTION"]
    return cfg


CFG: dict = {}


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
        if href.startswith("aff:"):
            return aff_link(href[4:], text)
        href = CFG.get("blog_redirects", {}).get(href.rstrip("/").rsplit("/", 1)[-1], href) \
            if href.startswith("/blog/") else href
        if href.split("#")[0] in UNPUBLISHED:  # scheduled, not live yet: keep the words, drop the link
            return text
        ext = href.startswith("http") and urlparse(href).netloc not in CFG["url"]
        rel = ' rel="noopener"' if ext else ""
        if "sponsored" in href or "/go/" in href:
            rel = ' rel="sponsored noopener" class="plausible-event-name=Affiliate+Click"'
        return f'<a href="{esc(u(href))}"{rel}>{text}</a>'

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)
    return s


AFF_USED: list[str] = []
UNPUBLISHED: set[str] = set()  # paths of scheduled articles/comparisons not live at this build


def aff_link(key: str, text: str) -> str:
    """[text](aff:sofi) -> the program's affiliate URL from site.json once you're approved, otherwise its
    plain official site (no commission, no 'sponsored' label). Unknown keys fail the build."""
    progs = CFG.get("programs", {})
    if key not in progs:
        raise SystemExit(f"Unknown affiliate program 'aff:{key}'. Add it to site.json > programs.")
    p = progs[key]
    AFF_USED.append(key)
    if p.get("affiliate_url"):
        return (f'<a href="{esc(p["affiliate_url"])}" rel="sponsored noopener" '
                f'class="plausible-event-name=Affiliate+Click" data-program="{esc(key)}">{text}</a>')
    return f'<a href="{esc(p["site"])}" rel="noopener nofollow" data-program="{esc(key)}">{text}</a>'


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
            t = ["<div class=\"table\" tabindex=\"0\"><table><thead><tr>"]
            t += [f"<th>{inline(c)}</th>" if c else '<th><span class="visually-hidden">Item</span></th>' for c in head]
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
    m = re.search(r"^## (?:FAQ|Frequently asked questions|Common questions)[^\n]*\n(.*?)(?=^## |\Z)", md,
                  re.S | re.M | re.I)
    if not m:
        return []
    pairs = re.findall(r"^### (.+?)\n(.*?)(?=^### |\Z)", m.group(1), re.S | re.M)
    clean = lambda s: re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"\*\*?|`|\{\{[^}]*\}\}", "", s)).strip()
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
def email_form(source: str, button: str = "Send me the free reset", compact: bool = False,
               thanks_path: str = "/free/thanks/", field_id: str = "") -> str:
    """field_id: a distinct id for a second form with the same source on one page (ids must be unique)."""
    e = CFG["email"]
    fid = field_id or f"em-{source}"
    provider = e.get("provider", "netlify")
    thanks = u(thanks_path)
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
        action = e.get("action") or "http://localhost:8000/subscribe/money-made-simple"
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
    note = esc(e.get("privacy_note", "One useful email a week. Unsubscribe in one click."))
    return f"""<form class="signup-form{' compact' if compact else ''}" method="post" action="{esc(action)}"{attrs} data-thanks="{thanks}">
  {extra}
  <label class="hp" aria-hidden="true">Leave this empty <input type="text" name="website" tabindex="-1" autocomplete="off"></label>
  <label class="sr" for="{esc(fid)}">Email address</label>
  <input id="{esc(fid)}" type="email" name="{esc(field)}" required autocomplete="email" inputmode="email" placeholder="you@example.com">
  <button type="submit">{ab("magnet", button, CFG.get("ab_test", {}).get("magnet_button", {}).get("b", button)) if button == CFG.get("ab_test", {}).get("magnet_button", {}).get("a") else esc(button)}</button>
</form>
<p class="form-note">{note} <a href="{u('/privacy/')}">Privacy</a>.</p>"""


def ab_on() -> bool:
    return bool(CFG.get("ab_test", {}).get("active"))


def ab(kind: str, a: str, b: str) -> str:
    """Both variants in the HTML; CSS shows the one the visitor's cookie picked (A without JavaScript)."""
    if not ab_on() or a == b:
        return esc(a)
    return f'<span class="ab-{kind}-a">{esc(a)}</span><span class="ab-{kind}-b">{esc(b)}</span>'


def magnet_name() -> str:
    t = CFG.get("ab_test", {})
    m = t.get("magnet", {})
    return ab("magnet", m.get("a", CFG["lead_magnet"]["title"]), m.get("b", CFG["lead_magnet"]["title"]))


def ab_head() -> str:
    """Assigns the variant before first paint (no flicker) and remembers it for 90 days."""
    if not ab_on():
        return ""
    tid = json.dumps(CFG["ab_test"]["id"])
    return ("<script>(function(){var d=document,q=location.search.match(/[?&]ab=([ab])([ab])/),"
            "c=d.cookie.match(/(?:^|; )mms_ab=([ab])([ab])/),r=function(){return Math.random()<.5?'a':'b'},"
            "v=q?q[1]+q[2]:c?c[1]+c[2]:r()+r();if(!q)d.cookie='mms_ab='+v+'; path=/; max-age=7776000; SameSite=Lax';"
            "d.documentElement.className+=' ab-h-'+v[0]+' ab-m-'+v[1];"
            f"window.mmsAB={{test:{tid},hero:v[0].toUpperCase(),magnet:v[1].toUpperCase()}};}})();</script>"
            "<style>.ab-hero-b,.ab-magnet-b{display:none}.ab-h-b .ab-hero-a,.ab-m-b .ab-magnet-a{display:none}"
            ".ab-h-b .ab-hero-b,.ab-m-b .ab-magnet-b{display:inline}</style>")


def magnet_box(source: str) -> str:
    lm = CFG["lead_magnet"]
    return f"""<div class="magnet">
  <img src="{u('/img/lead-magnet-cover-sm.jpg')}" alt="Cover of {esc(lm['title'])}" width="150" height="194" loading="lazy">
  <div>
    <p class="kicker">Free download</p>
    <h2 class="magnet-title">{magnet_name()}</h2>
    <p>{esc(lm['pitch'])}</p>
    {email_form(source)}
  </div>
</div>"""


def compare_box(slug: str, comps: dict) -> str:
    target = comps.get(CFG.get("article_compare", {}).get(slug, ""))
    if not target:
        return ""
    return (f'<div class="callout cmp-box"><p class="kicker">Compare your options</p>'
            f'<p><a href="{u(f"/compare/{target["slug"]}/")}"><strong>{esc(target["title"])}</strong></a></p>'
            f'<p>{esc(target["description"])}</p></div>')


def reviews_box(compare_slug: str, posts: list[dict]) -> str:
    slugs = [s for s, c in CFG.get("article_compare", {}).items() if c == compare_slug]
    items = [p for p in posts if p["slug"] in slugs]
    if not items:
        return ""
    lis = "".join(f'<li><a href="{u(f"/blog/{p["slug"]}/")}">{esc(p["title"])}</a></li>' for p in items)
    return f'<section class="next"><h2>Go deeper</h2><ul class="related">{lis}</ul></section>'


def load_related() -> dict:
    f = ROOT / "content" / "data" / "related.json"
    return json.loads(f.read_text()) if f.exists() else {"tools": {}, "articles": {}}


def related_for(p: dict, posts: list[dict]) -> tuple[list[dict], dict | None]:
    """content/data/related.json: the first 3 published of an article's hand-picked related slugs, and its free tool.
    Falls back to same-pillar articles if fewer than 3 of the picks are live yet."""
    data = load_related()
    entry = data["articles"].get(p["slug"], {})
    live = {x["slug"]: x for x in posts}
    related = [live[s] for s in entry.get("related", []) if s in live][:3]
    for x in posts:
        if len(related) >= 3:
            break
        if x is not p and x not in related and x.get("pillar") == p.get("pillar"):
            related.append(x)
    for x in posts:
        if len(related) >= 3:
            break
        if x is not p and x not in related:
            related.append(x)
    return related, data["tools"].get(entry.get("tool", ""))


def howto_ld(p: dict, path: str) -> dict | None:
    """HowTo schema for step-by-step articles. Front matter `howto:` names the section whose numbered list or
    ### sub-headings are the steps, or `steps` for '## Step N: ...' headings across the article."""
    sec = p.get("howto")
    if not sec:
        return None
    md = re.sub(r"<!--.*?-->", "", p["body"], flags=re.S)
    clean = lambda s: " ".join(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"\*\*?|`", "", s)).split())
    steps: list[tuple[str, str]] = []
    if sec == "steps":
        for h, txt in re.findall(r"^## (Step \d+:[^\n]*)\n+(.*?)(?=^## |\Z)", md, re.S | re.M):
            first = next((b for b in txt.strip().split("\n\n") if not b.startswith(("#", "|"))), "")
            steps.append((clean(h.split(":", 1)[1]), clean(first)))
    else:
        m = re.search(rf"^## {re.escape(sec)}[^\n]*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
        if not m:
            raise SystemExit(f"{p['slug']}: howto section '{sec}' not found")
        part = m.group(1)
        subs = re.findall(r"^### (?:\d+\.\s*)?([^\n]+)\n+(.*?)(?=^### |\Z)", part, re.S | re.M)
        if subs:
            steps = [(clean(h), clean(t.strip().split("\n\n")[0])) for h, t in subs]
        else:
            for item in re.findall(r"^\d+\. (.+)$", part, re.M):
                lead = re.match(r"\*\*(.+?)\*\*[:.]?\s*(.*)", item)
                steps.append((clean(lead.group(1)).rstrip(":."), clean(lead.group(2)) or clean(lead.group(1)))
                             if lead else (clean(item)[:80], clean(item)))
    if len(steps) < 2:
        raise SystemExit(f"{p['slug']}: howto found {len(steps)} steps")
    ld = {"@context": "https://schema.org", "@type": "HowTo", "name": p["title"], "description": p["description"],
          "url": absu(path),
          "step": [{"@type": "HowToStep", "position": i + 1, "name": n, "text": t or n}
                   for i, (n, t) in enumerate(steps)]}
    if p.get("howto_time"):
        ld["totalTime"] = p["howto_time"]
    return ld


def apps_base() -> str:
    return (os.environ["APPS_URL"] if "APPS_URL" in os.environ else CFG.get("apps_url", "")).rstrip("/")


def load_apps() -> list[dict]:
    """content/data/apps.json: tools on the separate apps site. Empty when apps_url isn't set."""
    f = CONTENT / "data" / "apps.json"
    if not apps_base() or not f.exists():
        return []
    return json.loads(f.read_text())["tools"]


def apps_li(t: dict) -> str:
    return (f'<li><a href="{esc(apps_base() + t["path"])}"><strong>{esc(t["title"])}</strong></a>: '
            f'{esc(t["blurb"])}</li>')


def apps_tools_html(keys: list[str], heading: str = "More free tools") -> str:
    """A list of apps-site tools by key, for data pages (salary, city). Empty when apps_url isn't set."""
    by = {t["key"]: t for t in load_apps()}
    items = [by[k] for k in keys if k in by]
    if not items:
        return ""
    return f'<section class="next tool-box"><h2>{esc(heading)}</h2><ul class="related">{"".join(apps_li(t) for t in items)}</ul></section>'


def tool_box(t: dict | None, slug: str = "") -> str:
    """'Free tools for this': the article's site tool (related.json) plus up to 2 apps-site tools (apps.json)."""
    apps = [a for a in load_apps() if slug and slug in a.get("articles", [])][:2]
    items = []
    if t:
        items.append(f'<li><a href="{u(t["path"])}"><strong>{esc(t["title"])}</strong></a>: {esc(t["blurb"])}</li>')
    items += [apps_li(a) for a in apps]
    if not items:
        return ""
    head = "Free tools for this" if len(items) > 1 else "Free tool for this"
    return f'<section class="next tool-box"><h2>{head}</h2><ul class="related">{"".join(items)}</ul></section>'


def product_card(p: dict) -> str:
    price = price_html(p)
    return f"""<a class="product-card" href="{u(f"/products/{p['slug']}/")}">
  <img src="{u(p.get('thumb') or p['image'])}" alt="" width="640" height="360" loading="lazy">
  <span class="pc-body"><span class="pc-title">{esc(p['title'])}</span>
  <span class="pc-short">{esc(p['short'])}</span>{price}</span>
</a>"""


def price_html(p: dict) -> str:
    if p.get("status") == "coming-soon":
        return '<span class="price soon">Coming soon</span>'
    if p.get("sale_price"):
        return (f'<span class="price"><s>${esc(p["price"])}</s> ${esc(p["sale_price"])} '
                f'<small>{esc(p.get("sale_label", "launch price"))}</small></span>')
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
        if name == "money:shop":
            return money_shop_summary()
        if name == "money:partners":
            return money_partners()
        if name.startswith("embed:"):
            return embed_block(name.split(":", 1)[1])
        if name.startswith("template:"):
            it = shop_items().get(name.split(":", 1)[1])
            return template_card(it) if it else ""
        if name.startswith("start:"):
            return start_hub(name.split(":", 1)[1])
        if name.startswith("digest:"):
            return digest_list(name.split(":", 1)[1])
        return ""
    return sc


LIVE_POSTS: list[dict] = []  # published articles, newest first (set by build())


def load_placements() -> dict:
    f = CONTENT / "data" / "placements.json"
    return json.loads(f.read_text()) if f.exists() else {"articles": {}, "goals": []}


def shop_items() -> dict:
    f = CONTENT / "shop.json"
    return {i["slug"]: i for i in json.loads(f.read_text())["items"]} if f.exists() else {}


def template_card(it: dict) -> str:
    """A 'related template' card for articles: one of our own products, with its store buttons
    (placeholder store links until shop.json / site.json > stores have the real ones)."""
    img = (f'<img src="{u(it["image"])}" alt="" width="120" height="120" loading="lazy" decoding="async">'
           if it.get("image") else "")
    return f"""<aside class="template-card{' has-img' if img else ''}" aria-label="Template: {esc(it['name'])}">{img}<div>
  <p class="tc-label">Our template · {"Free" if not it["price"] else f"${it['price']:g}"}</p>
  <p class="tc-name"><a href="{u(product_path(it))}">{esc(it["name"])}</a></p>
  <p class="tc-blurb">{esc(it.get("blurb", ""))}</p>
  <p class="shop-buy">{shop_buttons(it)}</p></div></aside>"""


PILLAR_GOAL = {"credit-and-debt": "debt", "budgeting": "saving", "money-tools": "saving", "investing": "first-job"}


def article_goal(slug: str, pillar: str = "") -> dict | None:
    """The Start here goal an article belongs to: placements.json > article_goals, else the first goal in
    start.json that lists it, else one picked by pillar. Used for the article's /shop/<goal>/ link."""
    pl = load_placements()
    goals = {g["id"]: g for g in pl["goals"]}
    gid = pl.get("article_goals", {}).get(slug)
    if not gid:
        gid = next((g["id"] for g in load_start()["goals"] if slug in g["articles"]), None)
    return goals.get(gid or PILLAR_GOAL.get(pillar, "saving"))


def templates_section(slug: str, prod: dict | None, pillar: str = "") -> str:
    """End-of-article product block: the article's other related templates (or the default product), and a
    link to its goal's shop page so every article links one /shop/<goal>/ page."""
    items = shop_items()
    picks = [items[s] for s in load_placements()["articles"].get(slug, [])[1:] if s in items]
    g = article_goal(slug, pillar)
    goal_link = (f'<p class="goal-shop"><a href="{u(f"/shop/{g['id']}/")}">{esc(g["title"])}</a>'
                 f' · <a href="{u("/shop/")}">the whole shop</a></p>') if g else ""
    if picks:
        return ('<section class="next templates"><h2>More templates for this</h2>' + "".join(template_card(i) for i in picks)
                + (goal_link or f'<p><a href="{u("/shop/")}">See every template in the shop</a></p>') + '</section>')
    if prod or goal_link:
        return f'<section class="next"><h2>Template for this</h2>{product_card(prod) if prod else ""}{goal_link}</section>'
    return ""


def load_embeds() -> dict:
    f = CONTENT / "data" / "embeds.json"
    return json.loads(f.read_text()) if f.exists() else {"tools": {}, "articles": {}}


def embed_block(key: str) -> str:
    """An apps-site tool inside an article: a live calculator (the apps site's embed.js makes a self-sizing
    iframe) or a link card. Nothing while site.json > apps_url is empty."""
    t = load_embeds()["tools"].get(key)
    base = apps_base()
    if not t or not base:
        return ""
    full = esc(base + t["path"])
    head = (f'<p class="tc-label">Free tool</p><p class="tc-name"><a href="{full}">{esc(t["title"])}</a></p>'
            f'<p class="tc-blurb">{esc(t["blurb"])}</p>')
    if t["kind"] == "calc":
        return (f'<div class="tool-embed">{head}<div class="mms-calc" data-calc="{esc(t["calc"])}" data-title="{esc(t["title"])}"></div>'
                f'<script src="{esc(base)}/money-calculators/embed.js" async></script>'
                f'<p class="tool-open"><a href="{full}">Open the full calculator</a></p></div>')
    return (f'<div class="tool-embed">{head}<p class="shop-buy"><a class="btn" href="{full}">'
            f'{esc(t.get("button", "Open the tool"))}</a></p></div>')


def with_inline_template(body: str, slug: str) -> str:
    """Put the article's first related template right after its worked example section (or before
    'Common questions' if there's no worked example), as {{template:<slug>}}."""
    picks = load_placements()["articles"].get(slug, [])
    tool = load_embeds()["articles"].get(slug)
    if tool and f"{{{{embed:{tool}}}}}" in body:
        tool = None  # placed by hand
    if not picks and not tool:
        return body
    code = (f"\n{{{{embed:{tool}}}}}\n" if tool else "") + (f"\n{{{{template:{picks[0]}}}}}\n" if picks else "") + "\n"
    m = re.search(r"^## A worked example.*$", body, re.M)
    if m:
        nxt = re.search(r"^## ", body[m.end():], re.M)
        if nxt:
            i = m.end() + nxt.start()
            return body[:i] + code + body[i:]
    i = body.find("## Common questions")
    return body[:i] + code + body[i:] if i >= 0 else body
LIVE_COMPS: list[dict] = []  # published comparison pages, newest first (set by build())


def digest_picks(meta: dict) -> dict:
    """What the "best of" digest (content/digest.md) shows at this build: pinned articles first, then the newest
    published ones, up to 'count'; plus the newest published comparison page."""
    by_slug = {p["slug"]: p for p in LIVE_POSTS}
    pinned = [by_slug[s] for s in meta.get("pinned", []) if s in by_slug]
    rest = [p for p in LIVE_POSTS if p not in pinned]
    arts = (pinned + rest)[:int(meta.get("count", 5))]
    return {"articles": arts, "compare": LIVE_COMPS[:1]}


DIGEST_META: dict = {}


def digest_list(which: str) -> str:
    picks = digest_picks(DIGEST_META)
    if which == "latest":
        return "<ol>" + "".join(
            f'<li><p><a href="{u(f"/blog/{p["slug"]}/")}"><strong>{esc(p["title"])}</strong></a><br>'
            f'{esc(p["description"])}</p></li>' for p in picks["articles"]) + "</ol>"
    if which == "compare":
        return "".join(f'<p><a href="{u(f"/compare/{c["slug"]}/")}"><strong>{esc(c["title"])}</strong></a><br>'
                       f'{esc(c["description"])}</p>' for c in picks["compare"])
    raise SystemExit(f"Unknown digest shortcode 'digest:{which}' (use digest:latest or digest:compare).")


def digest_text(body: str) -> str:
    """Plain-text version of the digest: shortcodes become numbered lists with full URLs."""
    picks = digest_picks(DIGEST_META)
    lines = []
    for i, p in enumerate(picks["articles"], 1):
        lines.append(f"{i}. {p['title']}\n   {p['description']}\n   " + absu("/blog/" + p["slug"] + "/"))
    latest = "\n".join(lines)
    comp = "\n".join(f"{c['title']}\n{c['description']}\n" + absu("/compare/" + c["slug"] + "/")
                     for c in picks["compare"])
    text = body.replace("{{digest:latest}}", latest).replace("{{digest:compare}}", comp)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f"{m.group(1)} ({absu(m.group(2))})", text)
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text).strip() + "\n"


def build_digest() -> None:
    """content/digest.md -> /emails/digest/ (noindex preview), email.html, email.txt and digest.json, filled with
    the newest published articles at build time. Paste into your email provider when you send a digest."""
    f = CONTENT / "digest.md"
    if not f.exists():
        return
    meta, body = parse_front_matter(f.read_text())
    DIGEST_META.clear()
    DIGEST_META.update(meta)
    month = datetime.strptime(os.environ.get("BUILD_DATE") or date.today().isoformat(), "%Y-%m-%d").strftime("%B %Y")
    e = {"subject": meta["subject"].replace("{month}", month), "preheader": meta.get("preheader", "").replace("{month}", month)}
    sc = shortcode_factory({}, "digest")
    preview_html, _ = markdown(body, sc)
    write("/emails/digest/", layout(title=f"Digest: {e['subject']}", path="/emails/digest/", noindex=True,
                                    description="Email digest preview", body=f"""<article class="wrap article email-preview">
  <p class="crumbs"><a href="{u('/emails/')}">Emails</a> · best-of digest, filled at build time</p>
  <p class="meta"><strong>Subject:</strong> {esc(e['subject'])}<br><strong>Preview text:</strong> {esc(e['preheader'])}</p>
  <div class="email-body prose">{preview_html}</div>
</article>"""))
    CFG["_absolute_links"] = True
    html, _ = markdown(body, sc)
    CFG["_absolute_links"] = False
    text = digest_text(body)
    picks = digest_picks(meta)
    (OUT / "emails" / "digest" / "email.html").write_text(email_html(e, html))
    (OUT / "emails" / "digest" / "email.txt").write_text(text)
    (OUT / "emails" / "digest" / "digest.json").write_text(json.dumps({
        "subject": e["subject"], "preheader": e["preheader"], "html": html, "text": text,
        "articles": [absu(f"/blog/{p['slug']}/") for p in picks["articles"]],
        "compare": [absu(f"/compare/{c['slug']}/") for c in picks["compare"]]}, indent=2, ensure_ascii=False))


def load_start() -> dict:
    f = CONTENT / "data" / "start.json"
    return json.loads(f.read_text()) if f.exists() else {"goals": []}


def start_hub(which: str) -> str:
    """/start/ hub. {{start:goals}} = the goal picker (cards linking to each goal's section);
    {{start:<goal id>}} = that goal's reading list: the first published articles from content/data/start.json,
    so the hub fills in as scheduled articles go live, plus its tools and comparisons."""
    goals = load_start()["goals"]
    if which == "goals":
        cards = "".join(
            f'<li class="post goal"><p class="post-pillar">{esc(g["kicker"])}</p>'
            f'<h2><a href="#{slug_id(g["heading"])}">{esc(g["label"])}</a></h2><p>{esc(g["blurb"])}</p></li>'
            for g in goals)
        return f'<ul class="posts grid goals" aria-label="Pick your goal">{cards}</ul>'
    g = next((x for x in goals if x["id"] == which), None)
    if not g:
        raise SystemExit(f"Unknown Start here goal '{which}'. Add it to content/data/start.json.")
    by_slug = {p["slug"]: p for p in LIVE_POSTS}
    picks = [by_slug[s] for s in g["articles"] if s in by_slug][:int(g.get("show", 4))]
    items = "".join(f'<li><a href="{u(f"/blog/{p["slug"]}/")}">{esc(p["title"])}</a></li>' for p in picks)
    extras = [(t, h) for t, h in g.get("links", []) if h not in UNPUBLISHED][:3]
    more = "".join(f'<li><a href="{u(h)}">{esc(t)}</a></li>' for t, h in extras)
    shop = (f'<p class="start-shop"><a href="{u(f"/shop/{which}/")}">Templates for this goal</a></p>'
            if any(x["id"] == which for x in load_placements()["goals"]) else "")
    return (f'<div class="start-reading"><h3>Read next</h3><ul>{items}</ul>'
            + (f'<h3>Tools and comparisons</h3><ul>{more}</ul>' if more else "") + shop + "</div>")


def money_shop_summary() -> str:
    """/how-we-make-money/: what's in the shop right now, from content/shop.json."""
    f = CONTENT / "shop.json"
    if not f.exists():
        return ""
    items = json.loads(f.read_text())["items"]
    paid = [i["price"] for i in items if i["price"]]
    free = len(items) - len(paid)
    kinds = {"printable": "printables", "kit": "kits", "notion": "Notion templates", "sheets": "spreadsheets"}
    counts = {}
    for i in items:
        counts[kinds.get(i.get("kind"), "other tools")] = counts.get(kinds.get(i.get("kind"), "other tools"), 0) + 1
    mix = ", ".join(f"{n} {k}" for k, n in sorted(counts.items(), key=lambda x: -x[1]))
    rng = f"${min(paid):g} to ${max(paid):g}" if paid else ""
    return (f'<p class="money-facts">Right now: <strong>{len(items)} products</strong> ({esc(mix)})'
            + (f", priced {rng}" if rng else "") + (f", {free} of them free" if free else "") + ".</p>")


def money_partners() -> str:
    """/how-we-make-money/: affiliate programs that are actually live (an affiliate_url is set in site.json or
    go-links.json), so the page never claims a partnership we don't have."""
    live = sorted({p.get("name", k) for k, p in CFG.get("programs", {}).items() if p.get("affiliate_url")})
    if not live:
        return ('<p class="money-facts"><strong>Affiliate partners right now: none.</strong> '
                'Until an affiliate program approves us, links go straight to the company and pay us nothing. When that '
                'changes, the list appears here.</p>')
    return ('<p class="money-facts"><strong>Affiliate partners right now:</strong> ' + esc(", ".join(live))
            + '. This list updates automatically when a program is added or removed.</p>')


def plausible_tag() -> str:
    """Cookieless Plausible analytics (docs/UTM.md section 3). Outbound clicks are tracked automatically;
    elements with class plausible-event-name=... send custom events (Product Click, Affiliate Click)."""
    a = CFG.get("analytics", {})
    domain = a.get("plausible_domain", "")
    if not domain:
        return ""
    host = a.get("plausible_host", "https://plausible.io").rstrip("/")
    return (f'<script defer data-domain="{esc(domain)}" '
            f'src="{esc(host)}/js/script.outbound-links.tagged-events.js"></script>'
            '<script>window.plausible=window.plausible||function(){(window.plausible.q=window.plausible.q||[]).push(arguments)}</script>')


def img_dims(image: str) -> str:
    """og:image:width/height for local PNGs (read from the PNG header, no Pillow needed)."""
    f = STATIC / image.lstrip("/")
    if image.startswith("http") or f.suffix != ".png" or not f.is_file():
        return ""
    head = f.read_bytes()[16:24]
    w, h = int.from_bytes(head[:4], "big"), int.from_bytes(head[4:], "big")
    return f'<meta property="og:image:width" content="{w}">\n<meta property="og:image:height" content="{h}">\n'


def article_og(item: dict, section: str) -> dict:
    return {"article:published_time": item["date"], "article:modified_time": item.get("updated", item["date"]),
            "article:author": editor()["name"], "article:section": section}


def search_verification_tags() -> str:
    """Home-page meta tags that prove site ownership to Google Search Console and Bing Webmaster Tools
    (site.json > search_verification: {"google": "<content value>", "bing": "<content value>"}; env
    GOOGLE_SITE_VERIFICATION overrides google)."""
    v = dict(CFG.get("search_verification", {}))
    if os.environ.get("GOOGLE_SITE_VERIFICATION"):
        v["google"] = os.environ["GOOGLE_SITE_VERIFICATION"]
    names = {"google": "google-site-verification", "bing": "msvalidate.01"}
    return "".join(f'<meta name="{names[k]}" content="{esc(val)}">\n' for k, val in v.items() if k in names and val)


def auto_breadcrumbs(path: str, title: str, body: str, jsonld: list, noindex: bool) -> dict | None:
    """BreadcrumbList for every indexed page that doesn't define its own: built from the visible
    <p class="crumbs"> trail when there is one (Home is added if missing), else Home > the page's h1."""
    if noindex or path == "/" or any(isinstance(x, dict) and x.get("@type") == "BreadcrumbList" for x in jsonld):
        return None
    strip = lambda h: html.unescape(re.sub(r"<[^>]+>", "", h)).strip()
    origin = "{0.scheme}://{0.netloc}".format(urlparse(CFG["url"]))
    trail: list[tuple[str, str]] = []
    m = re.search(r'<p class="crumbs">(.*?)</p>', body, re.S)
    if m:
        trail = [(strip(t), origin + h if h.startswith("/") else h)
                 for h, t in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', m.group(1))]
    if not trail or trail[0][1] != CFG["url"] + "/":
        trail.insert(0, ("Home", CFG["url"] + "/"))
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    last = strip(h1.group(1)) if h1 else title
    if trail[-1][1] != absu(path):
        trail.append((last, absu(path)))
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url} for i, (n, url) in enumerate(trail)]}


def layout(*, title: str, description: str, path: str, body: str, og_type: str = "website",
           jsonld: list | None = None, image: str = "/img/og-default.png", noindex: bool = False,
           extra_head: str = "", og: dict | None = None) -> str:
    """og: extra Open Graph properties, e.g. article:published_time (article pins) or
    product:price:amount (product pins). Pinterest rich pins read these same tags."""
    # Brand suffix only when it still fits in what Google shows (~60 chars).
    full_title = title if CFG["name"] in title or len(title) > 40 else f"{title} · {CFG['name']}"
    nav = "".join(
        f'<a href="{u(href)}"{" aria-current=page" if path.startswith(href) and href != "/" else ""}>{esc(t)}</a>'
        for t, href in [("Start here", "/start/"), ("Articles", "/blog/"), ("Compare", "/compare/"),
                        ("Shop", "/shop/"), ("Free reset", "/free/")])
    jsonld = list(jsonld or [])
    crumbs = auto_breadcrumbs(path, title, body, jsonld, noindex)
    if crumbs:
        jsonld.append(crumbs)
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
                 for x in jsonld)
    soc = " · ".join(f'<a href="{esc(h)}" rel="me noopener">{esc(n)}</a>' for n, h in CFG["socials"].items())
    analytics = plausible_tag() + CFG.get("analytics_snippet", "")
    return f"""<!doctype html>
<html lang="en">
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
{img_dims(image)}<meta property="og:image:alt" content="{esc(title)}">
<meta property="og:locale" content="en_US">
{"".join(f'<meta property="{esc(k)}" content="{esc(str(v))}">' + chr(10) for k, v in (og or {}).items() if v not in (None, ""))}<meta name="pinterest-rich-pin" content="true">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(absu(image))}">
<meta name="theme-color" content="#0b1d13">
{search_verification_tags() if path == "/" else ""}
<link rel="icon" type="image/png" href="{u('/img/favicon.png')}">
<link rel="apple-touch-icon" href="{u('/img/apple-touch-icon.png')}">
<link rel="alternate" type="application/rss+xml" title="{esc(CFG['name'])}" href="{u('/feed.xml')}">
{ab_head()}<link rel="stylesheet" href="{u('/style.css')}">
{ld}{extra_head}{analytics}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap head-inner">
    <a class="brand" href="{u('/')}"><img src="{u('/img/logo-72.png')}" alt="" width="36" height="36">{esc(CFG['name'])}</a>
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
    <p><a href="{u('/about/')}">About</a> · <a href="{u('/tools/')}">Free tools</a> · <a href="{u('/resources/')}">Resources</a> · <a href="{u('/quiz/')}">Money quiz</a> · <a href="{u('/budget/')}">Budget by salary</a> · <a href="{u('/cost-of-living/')}">City budgets</a> · <a href="{u('/debt-payoff/')}">Debt payoff</a> · <a href="{u('/ask/')}">Money questions</a> · <a href="{u('/holiday/')}">Holiday money</a> · <a href="{u('/shop/')}">Shop</a> · <a href="{u('/privacy/')}">Privacy</a> · <a href="{u('/how-we-make-money/')}">How we make money</a> · <a href="{u('/disclosures/')}">Disclosures</a> · <a href="{u('/terms/')}">Terms</a> · <a href="{u('/links/')}">Links</a> · <a href="{u('/newsletter/')}">Newsletter</a> · <a href="{u('/feed.xml')}">RSS</a></p>
    <p class="small">{esc(CFG['disclaimer'])}</p>
    <p class="small">{esc(CFG['ai_disclosure'])}</p>
    <p class="small">&copy; {date.today().year} {esc(CFG['name'])}</p>
  </div>
</footer>
<script src="{u('/site.js')}" defer></script>
</body>
</html>
"""


def editor() -> dict:
    """site.json > editor: the person who edits and checks the site. placeholder: true until a real name is set."""
    e = CFG.get("editor", {})
    return {"name": e.get("name", f"The {CFG['name']} editor"), "placeholder": e.get("placeholder", True),
            "bio": e.get("bio", ""), "path": "/about/editor/"}


def author_ld() -> dict:
    """Article author: the named editor once there is one, the organisation while the name is a placeholder."""
    e = editor()
    if e["placeholder"]:
        return {"@type": "Organization", "name": CFG["name"], "url": CFG["url"] + "/"}
    return {"@type": "Person", "name": e["name"], "url": absu(e["path"]),
            "worksFor": {"@type": "Organization", "name": CFG["name"]}}


def byline() -> str:
    e = editor()
    return f'Edited and fact-checked by <a href="{u(e["path"])}">{esc(e["name"])}</a>'


def org_ld() -> dict:
    return {"@context": "https://schema.org", "@type": "Organization", "name": CFG["name"],
            "url": CFG["url"] + "/", "logo": absu("/img/logo.png"), "sameAs": list(CFG["socials"].values())}


def fmt_date(d: str) -> str:
    return datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")


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
    shutil.copytree(STATIC, OUT)
    urls: list[tuple[str, str]] = []

    redirects = CFG.get("blog_redirects", {})
    # Scheduled publishing: an article or comparison dated after the build date isn't built yet, and links to it
    # render as plain text until it is (BUILD_DATE overrides today; BLOG_SHOW_SCHEDULED=1 builds everything).
    build_day = os.environ.get("BUILD_DATE") or date.today().isoformat()
    show_sched = os.environ.get("BLOG_SHOW_SCHEDULED") == "1"
    live = lambda x: show_sched or str(x["date"]) <= build_day  # noqa: E731
    all_posts = [p for p in load_dir("blog") if p["slug"] not in redirects and p.get("status") != "draft"]
    all_comps = load_dir("compare")
    UNPUBLISHED.clear()
    UNPUBLISHED.update(f"/blog/{p['slug']}/" for p in all_posts if not live(p))
    UNPUBLISHED.update(f"/compare/{c['slug']}/" for c in all_comps if not live(c))
    if (CONTENT / "new-year.md").exists() and not new_year_live():
        UNPUBLISHED.add("/new-year/")
    posts = sorted((p for p in all_posts if live(p)), key=lambda p: (str(p["date"]), p.get("order", "")), reverse=True)
    LIVE_POSTS[:] = posts
    LIVE_COMPS[:] = sorted((c for c in all_comps if live(c)), key=lambda c: str(c["date"]), reverse=True)
    comps_by_slug = {c["slug"]: c for c in all_comps if live(c)}
    products_list = [p for p in load_dir("products") if p.get("status") != "draft"]
    products_list.sort(key=lambda p: int(p.get("order", 99)))
    products = {p["slug"]: p for p in products_list}
    pages = load_dir("pages")
    pillars = CFG["pillars"]

    # ---- articles
    for p in posts:
        path = f"/blog/{p['slug']}/"
        body_html, toc = markdown(with_inline_template(p["body"], p["slug"]),
                                  shortcode_factory(products, f"blog-{p['slug']}"))
        faq = extract_faq(p["body"])
        related, tool = related_for(p, posts)
        prod = products.get(p.get("product", "")) or (products_list[0] if products_list else None)
        toc_html = ""
        if len(toc) >= 3:
            toc_html = '<nav class="toc" aria-label="On this page"><p>On this page</p><ol>' + "".join(
                f'<li><a href="#{i}">{t}</a></li>' for i, t in toc) + "</ol></nav>"
        ld = [{
            "@context": "https://schema.org", "@type": "Article", "headline": p["title"],
            "description": p["description"], "datePublished": p["date"],
            "dateModified": p.get("updated", p["date"]), "mainEntityOfPage": absu(path),
            "image": absu(p.get("image", "/img/og-default.png")),
            "author": author_ld(),
            "publisher": org_ld(), "keywords": p.get("keyword", "")},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": CFG["url"] + "/"},
                {"@type": "ListItem", "position": 2, "name": "Articles", "item": absu("/blog/")},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": absu(path)}]}]
        if faq:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq]})
        how = howto_ld(p, path)
        if how:
            ld.append(how)
        rel_html = "".join(
            f'<li><a href="{u(f"/blog/{x["slug"]}/")}">{esc(x["title"])}</a></li>' for x in related)
        sources = ""
        if p.get("sources"):
            sources = '<section class="sources"><h2>Sources</h2><ul>' + "".join(
                f'<li><a href="{esc(s)}" rel="noopener">{esc(urlparse(s).netloc + urlparse(s).path)}</a></li>'
                for s in p["sources"]) + "</ul></section>"
        updated = f' · Updated {fmt_date(p["updated"])}' if p.get("updated") else ""
        aff = ('<p class="aff-note">This article contains affiliate links. If you sign up through them we may '
               f'earn a commission at no extra cost to you. <a href="{u("/disclosures/")}">How we handle this</a>.</p>'
               if p.get("affiliate") == "yes" else "")
        body = f"""<article class="wrap article">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <a href="{u('/blog/')}">Articles</a> / <span>{esc(pillars.get(p.get('pillar', ''), 'Guide'))}</span></p>
  <h1>{esc(p['title'])}</h1>
  <p class="dek">{esc(p['description'])}</p>
  <p class="meta">{fmt_date(p['date'])}{updated} · {esc(p.get('read_minutes', '6'))} min read · {byline()}</p>
  {aff}
  {toc_html}
  <div class="prose">
{body_html}
  </div>
  {sources}
  <p class="disclaimer">{esc(CFG['disclaimer'])}</p>
  {compare_box(p['slug'], comps_by_slug)}
  {magnet_box(f"blog-{p['slug']}-end")}
  {tool_box(tool, p['slug'])}
  {templates_section(p['slug'], prod, p.get('pillar', ''))}
  <section class="next"><h2>Read next</h2><ul class="related">{rel_html}</ul></section>
</article>"""
        write(path, layout(title=p.get("seo_title", p["title"]), description=p["description"], path=path,
                           body=body, og_type="article", jsonld=ld, image=p.get("image", "/img/og-default.png"),
                           og=article_og(p, pillars.get(p.get("pillar", ""), "Guide"))))
        urls.append((path, p.get("updated", p["date"])))

    # ---- comparison pages (affiliate)
    comps = sorted((c for c in all_comps if live(c)), key=lambda c: int(c.get("order", 99)))
    for c in comps:
        path = f"/compare/{c['slug']}/"
        AFF_USED.clear()
        body_html, toc = markdown(c["body"], shortcode_factory(products, f"compare-{c['slug']}"))
        used = list(dict.fromkeys(AFF_USED))
        earning = [CFG["programs"][k]["name"] for k in used if CFG["programs"][k].get("affiliate_url")]
        if earning and c.get("compliance_review") == "required":
            print(f"NOTE: /compare/{c['slug']}/ has paid adviser/broker links ({', '.join(earning)}). FINRA/SEC "
                  "rules apply: get the firm's sign-off on this page before publishing (research/02-affiliate-programs.md).")
        if earning:
            who = ("We may earn a commission if you sign up through links to: " + ", ".join(earning) +
                   ". Those links are marked as sponsored. It costs you nothing extra.")
        else:
            who = ("Right now we don't earn anything from the companies on this page. If we join their "
                   "affiliate programs, this notice will name them.")
        disclosure = f"""<div class="ftc"><p><strong>Disclosure:</strong> {esc(who)} Commissions never decide
  what we recommend, and we include options that don't pay us. <a href="{u('/disclosures/')}">How we make money</a>.</p></div>"""
        asof = f"""<p class="asof"><strong>Checked as of {esc(c['as_of'])}.</strong> Rates, fees and features change
  often, sometimes weekly. Confirm the current terms on the provider's own site before you sign up.</p>"""
        faq = extract_faq(c["body"])
        toc_html = ('<nav class="toc" aria-label="On this page"><p>On this page</p><ol>' + "".join(
            f'<li><a href="#{i}">{t}</a></li>' for i, t in toc) + "</ol></nav>") if len(toc) >= 3 else ""
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": c["title"],
               "description": c["description"], "datePublished": c["date"],
               "dateModified": c.get("updated", c["date"]), "mainEntityOfPage": absu(path),
               "image": absu("/img/og-default.png"),
               "author": author_ld(),
               "publisher": org_ld()}]
        if faq:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
        sources = ""
        if c.get("sources"):
            sources = '<section class="sources"><h2>Sources</h2><ul>' + "".join(
                f'<li><a href="{esc(s)}" rel="noopener">{esc(urlparse(s).netloc + urlparse(s).path)}</a></li>'
                for s in c["sources"]) + "</ul></section>"
        body = f"""<article class="wrap article compare">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <a href="{u('/compare/')}">Comparisons</a></p>
  <h1>{esc(c['title'])}</h1>
  <p class="dek">{esc(c['description'])}</p>
  {disclosure}
  {asof}
  <p class="meta">{fmt_date(c['date'])} · {byline()}</p>
  {toc_html}
  <div class="prose">
{body_html}
  </div>
  {sources}
  <p class="disclaimer">{esc(CFG['disclaimer'])}</p>
  {reviews_box(c['slug'], posts)}
  {magnet_box(f"compare-{c['slug']}-end")}
</article>"""
        write(path, layout(title=c.get("seo_title", c["title"]), description=c["description"], path=path,
                           body=body, og_type="article", jsonld=ld, og=article_og(c, "Comparisons")))
        urls.append((path, c.get("updated", c["date"])))
    if comps:
        cards = "".join(f"""<li class="post"><p class="post-pillar">Comparison · checked {esc(c['as_of'])}</p>
<h2><a href="{u(f"/compare/{c['slug']}/")}">{esc(c['title'])}</a></h2><p>{esc(c['description'])}</p></li>""" for c in comps)
        write("/compare/", layout(
            title="Honest comparisons: savings accounts, budgeting apps, cards and more", path="/compare/",
            description="Side-by-side comparisons of savings accounts, budgeting apps, credit-builder cards, robo-advisors "
                        "and more, with what each costs and who it's not for.",
            body=f"""<section class="wrap">
  <h1>Comparisons</h1>
  <p class="dek">Side-by-side tables, what each option costs, and who it's <em>not</em> for. Some links are affiliate links; every page says which.</p>
  <ul class="posts">{cards}</ul>
</section>"""))
        urls.append(("/compare/", comps[0]["date"]))

    # ---- blog index (+ one page per pillar)
    def post_list(items):
        return "".join(f"""<li class="post">
  <p class="post-pillar">{esc(pillars.get(x.get('pillar', ''), ''))}</p>
  <h2><a href="{u(f"/blog/{x['slug']}/")}">{esc(x['title'])}</a></h2>
  <p>{esc(x['description'])}</p>
  <p class="meta">{fmt_date(x['date'])} · {esc(x.get('read_minutes', '6'))} min read</p>
</li>""" for x in items)

    chips = "".join(f'<a class="chip" href="{u(f"/blog/{k}/")}">{esc(v)}</a>' for k, v in pillars.items())
    write("/blog/", layout(
        title="Articles: budgeting, investing basics, credit and money tools",
        description="Plain-English guides for students and early-career workers: budgeting that sticks, first-time "
                    "investing, credit scores, debt payoff and money apps, with the maths shown.",
        path="/blog/", jsonld=[org_ld()], body=f"""<section class="wrap">
  <h1>Articles</h1>
  <p class="dek">One idea per article, explained properly, with the numbers shown. Pick a topic:</p>
  <p class="chips">{chips}</p>
  <ul class="posts">{post_list(posts)}</ul>
</section>"""))
    urls.append(("/blog/", posts[0]["date"]))
    for key, label in pillars.items():
        items = [x for x in posts if x.get("pillar") == key]
        path = f"/blog/{key}/"
        write(path, layout(title=f"{label}: articles", description=f"Every Money Made Simple article on {label.lower()}.",
                           path=path, body=f"""<section class="wrap">
  <p class="crumbs"><a href="{u('/blog/')}">Articles</a></p>
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
            note = '<p class="buy-note">Not on sale yet. Join the free email and you\'ll hear the day it opens.</p>'
            buy = note + email_form(f"waitlist-{p['slug']}", "Tell me when it opens")
            # the bottom form keeps the same source tag but needs its own field id
            buy_bottom = note + email_form(f"waitlist-{p['slug']}", "Tell me when it opens",
                                           field_id=f"em-waitlist-{p['slug']}-bottom")
        else:
            buy = (f'<a class="btn big plausible-event-name=Product+Click" href="{esc(p["buy_url"])}" rel="noopener" data-buy="{esc(p["slug"])}">'
                   f'{esc(p.get("buy_label", "Get instant access"))}</a>'
                   f'<p class="buy-note">{esc(p.get("guarantee", ""))}</p>')
            buy_bottom = buy
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
  <p class="crumbs"><a href="{u('/products/')}">Products</a></p>
  <div class="product-hero">
    {product_hero_img(p)}
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
  <div class="buy-again">{price_html(p)}{buy_bottom}</div>
  <p class="disclaimer">{esc(CFG['disclaimer'])}</p>
</article>"""
        write(path, layout(title=p.get("seo_title", p["title"]), description=p["short"], path=path, body=body,
                           og_type="product", jsonld=ld, image=p["image"],
                           og={} if p.get("status") == "coming-soon" else {
                               "product:price:amount": p.get("sale_price") or p["price"],
                               "product:price:currency": "USD", "og:price:amount": p.get("sale_price") or p["price"],
                               "og:price:currency": "USD", "product:availability": "in stock",
                               "og:availability": "instock", "product:brand": CFG["name"]}))
        urls.append((path, p.get("updated", date.today().isoformat())))
    write("/products/", layout(
        title="Guides and templates", path="/products/",
        description="Low-cost, no-subscription money tools from Money Made Simple: guides and spreadsheets you keep.",
        body=f"""<section class="wrap">
  <h1>Guides and templates</h1>
  <p class="dek">Small, specific tools. One payment, no subscription, files you keep. Each one has a no-hoops refund.</p>
  <div class="product-grid">{''.join(product_card(p) for p in products_list)}</div>
  <p><a class="btn" href="{u('/shop/')}">See the whole shop: kits, templates, printables and bundles</a></p>
  {magnet_box('products-index')}
</section>"""))
    urls.append(("/products/", date.today().isoformat()))

    # ---- shop: every product from the products thread (content/shop.json, made by tools/import_shop.py)
    shop_file = CONTENT / "shop.json"
    if shop_file.exists():
        build_shop(json.loads(shop_file.read_text())["items"])
        urls.append(("/shop/", date.today().isoformat()))
        urls += build_shop_goals()
        urls += build_product_pages()

    # ---- static pages
    for pg in pages:
        path = f"/{pg['slug']}/"
        body_html, _ = markdown(pg["body"], shortcode_factory(products, f"page-{pg['slug']}"))
        write(path, layout(title=pg["title"], description=pg.get("description", pg["title"]), path=path,
                           body=f'<article class="wrap article"><h1>{esc(pg["title"])}</h1><div class="prose">{body_html}</div></article>'))
        urls.append((path, pg.get("updated", date.today().isoformat())))

    # ---- the editor: who checks the articles (site.json > editor). Placeholder until a real name is set.
    ed = editor()
    if ed["placeholder"]:
        print("warning: site.json > editor is a placeholder; set a real name and bio before launch", file=sys.stderr)
    ed_bio = markdown(ed["bio"])[0] if ed["bio"] else ""
    write(ed["path"], layout(
        title=f"About the editor · {CFG['name']}", description=f"Who edits and fact-checks {CFG['name']}, and how.",
        path=ed["path"], jsonld=[org_ld()] + ([] if ed["placeholder"] else [{
            "@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": author_ld()}]),
        body=f"""<article class="wrap article"><p class="crumbs"><a href="{u('/')}">Home</a> / <a href="{u('/about/')}">About</a> / <span>Editor</span></p>
<h1>{esc(ed["name"])}</h1>
<div class="prose">{ed_bio}
<h2>What the editor does</h2>
<ul><li>Chooses every topic and approves every article and comparison before it's published.</li>
<li>Checks every number, rate and fee against the source listed at the bottom of the page, and re-checks comparison pages on the date shown at the top.</li>
<li>Reads every page that was drafted with AI help line by line, including titles, descriptions and alt text, and rewrites what isn't right.</li>
<li>Decides which products we mention. Affiliate relationships never decide a recommendation (<a href="{u('/disclosures/')}">how we handle affiliate links</a>).</li></ul>
<p>Spotted a mistake? Email {esc(CFG.get("contact_email", ""))} and it'll be fixed, with the correction noted on the page.</p>
</div></article>"""))
    urls.append((ed["path"], date.today().isoformat()))

    # ---- resources: every tool, with its affiliate slot status
    cats: dict[str, list[str]] = {}
    for key, pr in CFG["programs"].items():
        paid = bool(pr.get("affiliate_url"))
        href = pr["affiliate_url"] if paid else pr["site"]
        rel = 'rel="sponsored noopener" class="plausible-event-name=Affiliate+Click"' if paid else 'rel="noopener nofollow"'
        tag = '<span class="tag aff">affiliate</span>' if paid else '<span class="tag">no affiliation</span>'
        cmp = (f' · <a href="{u(f"/compare/{pr["compare"]}/")}">compared here</a>'
               if pr.get("compare") and f"/compare/{pr['compare']}/" not in UNPUBLISHED else "")
        cats.setdefault(pr.get("category", "Other"), []).append(
            f'<li><a href="{esc(href)}" {rel} data-program="{esc(key)}"><strong>{esc(pr["name"])}</strong></a> {tag}'
            f'<br><span>{esc(pr.get("blurb", ""))}{cmp}</span></li>')
    for t in CFG.get("free_tools", []):
        cats.setdefault(t["category"], []).append(
            f'<li><a href="{esc(t["url"])}" rel="noopener"><strong>{esc(t["name"])}</strong></a> <span class="tag free">free</span>'
            f'<br><span>{esc(t["blurb"])}</span></li>')
    res_html = "".join(f'<h2 id="{slug_id(k)}">{esc(k)}</h2><ul class="resources">{"".join(v)}</ul>' for k, v in cats.items())
    ours = "".join(f'<li><a href="{u(f"/products/{p["slug"]}/")}"><strong>{esc(p["title"])}</strong></a> <span class="tag ours">ours</span><br><span>{esc(p["short"])}</span></li>'
                   for p in products_list)
    n_paid = sum(1 for pr in CFG["programs"].values() if pr.get("affiliate_url"))
    res_note = (f"{n_paid} of the companies below pay us a commission if you sign up through our link; they're labelled "
                "\"affiliate\". Everything labelled \"no affiliation\" or \"free\" pays us nothing.") if n_paid else (
                "None of the companies below pay us right now. If that changes, each paying link will be labelled \"affiliate\".")
    write("/resources/", layout(
        title="Resources: every money tool we mention", path="/resources/",
        description="Every bank, app, card and free government tool mentioned on Money Made Simple, what it's for, "
                    "and whether we earn anything from it.",
        body=f"""<article class="wrap article">
  <h1>Resources</h1>
  <p class="dek">Every tool we mention, what it's for, and where we compare it. Free government tools are included because they're often the best option.</p>
  <div class="ftc"><p><strong>Disclosure:</strong> {esc(res_note)} <a href="{u('/disclosures/')}">How we make money</a>.</p></div>
  <p class="asof">Listed as of {date.today().strftime('%B %-d, %Y')}. Check each provider's current terms before signing up.</p>
  <h2>Our own tools</h2><ul class="resources">{ours}<li><a href="{u('/free/')}"><strong>The 7-Day Money Reset</strong></a> <span class="tag free">free</span><br><span>Seven 15-minute tasks, printable checklist and worksheets.</span></li></ul>
  {res_html}
  {magnet_box('resources')}
</article>"""))
    urls.append(("/resources/", date.today().isoformat()))

    # ---- money personality quiz (static JS) -> 7-Day Money Reset signup
    quiz = json.loads((CONTENT / "quiz.json").read_text())
    for r in quiz["results"].values():
        r["moves"] = [[t, u(href)] for t, href in r["moves"]]
    qs = "".join(f"""<fieldset class="q" data-i="{i}"{' hidden' if i else ''}>
  <legend><span class="qn">Question {i + 1} of {len(quiz['questions'])}</span>{esc(q['q'])}</legend>
  {''.join(f'<button type="button" class="opt" data-v="{esc(k)}">{esc(v)}</button>' for k, v in q['a'].items())}
</fieldset>""" for i, q in enumerate(quiz["questions"]))
    write("/quiz/", layout(
        title=quiz["title"], path="/quiz/", description=quiz["intro"],
        body=f"""<section class="wrap landing quiz">
  <p class="kicker">1-minute quiz</p>
  <h1>{esc(quiz['title'])}</h1>
  <p class="dek">{esc(quiz['intro'])}</p>
  <div class="progress" aria-hidden="true"><span></span></div>
  <form id="quiz" onsubmit="return false">{qs}</form>
  <noscript><p>This quiz needs JavaScript. You can go straight to <a href="{u('/start/')}">Start here</a>.</p></noscript>
  <section id="result" hidden aria-live="polite">
    <p class="kicker">Your money personality</p>
    <h2 id="r-name"></h2>
    <p class="dek" id="r-summary"></p>
    <h3>Your next three moves</h3>
    <ol id="r-moves" class="days"></ol>
    <div class="magnet quiz-cta">
      <img src="{u('/img/lead-magnet-cover-sm.jpg')}" alt="" width="150" height="194" loading="lazy">
      <div><p class="kicker">Free</p><h2 class="magnet-title">Get the 7-Day Money Reset</h2>
      <p>Your three moves, plus four more, as seven 15-minute tasks with worksheets. Free PDF.</p>
      {email_form('quiz', 'Send me the free reset')}</div>
    </div>
    <p><button type="button" class="btn ghost" id="retake">Retake the quiz</button></p>
  </section>
  <p class="disclaimer">For fun and orientation only, not financial advice. Your answers stay in your browser.</p>
</section>
<script>window.MMS_QUIZ={json.dumps(quiz['results'], ensure_ascii=False)};</script>
<script src="{u('/quiz.js')}" defer></script>"""))
    urls.append(("/quiz/", date.today().isoformat()))

    # ---- lead magnet landing + thanks
    lm = CFG["lead_magnet"]
    days = "".join(f"<li><strong>Day {i}:</strong> {esc(d)}</li>" for i, d in enumerate(lm["days"], 1))
    write("/free/", layout(
        title=f"Free: {lm['title']}", path="/free/", description=lm["pitch"],
        body=f"""<section class="wrap landing">
  <div class="landing-grid">
    <div>
      <p class="kicker">Free PDF + checklist: {magnet_name()}</p>
      <h1>{esc(lm['headline'])}</h1>
      <p class="dek">{esc(lm['pitch'])}</p>
      {email_form('free-page', 'Send me the free reset')}
    </div>
    <img class="cover" src="{u('/img/lead-magnet-cover-sm.jpg')}" alt="Cover of {esc(lm['title'])}" width="300" height="388" fetchpriority="high">
  </div>
  <h2>What you'll do, one 15-minute task a day</h2>
  <ol class="days">{days}</ol>
  <h2>What else you get</h2>
  <p>After the reset, one short email a week: a single money move, explained with the numbers. No hype, no stock picks, no "get rich" anything. You can unsubscribe in one click from any email.</p>
  {magnet_box('free-page-bottom')}
</section>"""))
    urls.append(("/free/", date.today().isoformat()))
    write("/free/thanks/", layout(
        title="You're in", path="/free/thanks/", noindex=True, description="Your free download.",
        body=f"""<section class="wrap landing thanks">
  <h1>You're in. Here's your reset.</h1>
  <p class="dek">{esc(CFG['email'].get('thanks_note', 'Check your inbox too: your first email is on its way (look in Promotions or Spam if you do not see it).'))}</p>
  <p><a class="btn big" href="{u('/downloads/' + lm['file'])}" download>Download {esc(lm['title'])} (PDF)</a></p>
  <p>Start with Day 1 today. It takes about 15 minutes and you'll need your banking app.</p>
  <h2>Want the full system?</h2>
  <div class="product-grid">{''.join(product_card(p) for p in products_list[:2])}</div>
</section>"""))

    # ---- link in bio
    links = "".join(f'<a class="lb-link" href="{u(f"/products/{p["slug"]}/")}"><span>{esc(p["title"])}</span>{price_html(p)}</a>'
                    for p in products_list)
    links += '<h2 class="lb-h">Popular articles</h2>' + "".join(f'<a class="lb-link" href="{u(f"/blog/{p["slug"]}/")}"><span>{esc(p["title"])}</span></a>'
                     for p in posts[:4])
    aff = "".join(f'<a class="lb-link plausible-event-name=Affiliate+Click" href="{esc(a["url"])}" rel="sponsored noopener"><span>{esc(a["name"])}</span><small>affiliate</small></a>'
                  for a in CFG.get("affiliates", []))
    write("/links/", layout(
        title="Links", path="/links/", description=CFG["tagline"],
        body=f"""<section class="linkbio">
  <img class="avatar" src="{u('/img/avatar.jpg')}" alt="" width="104" height="104">
  <h1>{esc(CFG['name'])}</h1>
  <p class="dek">{esc(CFG['tagline'])}</p>
  <div class="lb-signup"><h2>Free: {esc(lm['title'])}</h2><p>{esc(lm['short'])}</p>{email_form('link-in-bio', 'Send it', compact=True)}</div>
  <a class="lb-link" href="{u('/quiz/')}"><span>What's your money personality? (1-minute quiz)</span></a>
  <a class="lb-link" href="{u('/start/')}"><span>New here? Start here</span></a>
  <h2 class="lb-h">Guides and templates</h2>{links}
  {f'<h2 class="lb-h">Tools we recommend</h2>{aff}<p class="small">Affiliate links: we may earn a commission at no extra cost to you.</p>' if aff else ''}
</section>"""))
    urls.append(("/links/", date.today().isoformat()))

    # ---- home
    latest = "".join(f"""<li class="post"><p class="post-pillar">{esc(pillars.get(x.get('pillar',''),''))}</p>
<h3><a href="{u(f"/blog/{x['slug']}/")}">{esc(x['title'])}</a></h3><p>{esc(x['description'])}</p></li>""" for x in posts[:6])
    pillar_cards = "".join(
        f'<a class="pillar" href="{u(f"/blog/{k}/")}"><span class="pillar-n">{len([x for x in posts if x.get("pillar") == k])} articles</span><strong>{esc(v)}</strong></a>'
        for k, v in pillars.items())
    compare_home = ""
    if comps:
        compare_home = ('<section class="wrap"><h2 class="section-h">Compare before you sign up</h2><p class="chips">' +
                        "".join(f'<a class="chip" href="{u(f"/compare/{c["slug"]}/")}">{esc(c.get("short", c["title"].split(":")[0]))}</a>'
                                for c in comps) + "</p></section>")
    _ab = CFG.get("ab_test", {}).get("hero", {})
    hero_a = _ab.get("a", {"headline": "Feel behind on money? Start with one move this week.",
                           "offer": "seven 15-minute tasks that get your money organised in a week."})
    hero_b = _ab.get("b", hero_a)
    home_ld = [org_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": CFG["name"],
                          "url": CFG["url"] + "/"}]
    write("/", layout(
        title=f"{CFG['name']}: one money move a week, explained simply", path="/", jsonld=home_ld,
        description=CFG["description"],
        body=f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="kicker">For students and early-career workers</p>
      <h1>{ab("hero", hero_a["headline"], hero_b["headline"])}</h1>
      <p class="dek">{esc(CFG['description'])}</p>
      <div class="hero-form"><p class="hero-offer">Get <strong>{magnet_name()}</strong> free: {ab("hero", hero_a["offer"], hero_b["offer"])}</p>{email_form('home-hero', 'Send me the free reset')}</div>
      <p class="quiz-link">Not sure where to start? <a href="{u('/quiz/')}">Take the 1-minute money personality quiz</a> or see <a href="{u('/start/')}">Start here</a>.</p>{holiday_note()}
    </div>
    <img class="cover" src="{u('/img/lead-magnet-cover-sm.jpg')}" alt="Cover of {esc(lm['title'])}" width="300" height="388" fetchpriority="high">
  </div>
</section>
<section class="wrap">
  <h2 class="section-h">Start with a topic</h2>
  <div class="pillars">{pillar_cards}</div>
</section>
<section class="wrap">
  <h2 class="section-h">Latest articles</h2>
  <ul class="posts grid">{latest}</ul>
  <p><a class="btn ghost" href="{u('/blog/')}">All articles</a></p>
</section>
{compare_home}
<section class="band">
  <div class="wrap">
    <h2 class="section-h">The tools</h2>
    <div class="product-grid">{''.join(product_card(p) for p in products_list)}</div>
  </div>
</section>
<section class="wrap promise">
  <h2 class="section-h">How we make this</h2>
  <div class="three">
    <div><h3>Specific, not hype</h3><p>Every article and email is one idea you can use this week, with the maths shown. No stock picks, no crypto pumps, no income claims.</p></div>
    <div><h3>Checked by a person</h3><p>Drafted with AI help, fact-checked by a person. A person picks every topic, checks every number against primary sources (IRS, CFPB, FDIC, Investor.gov) and approves every post.</p></div>
    <div><h3>Honest about money</h3><p>Some links are affiliate links and they're always labelled. Products have a no-hoops refund. Testimonials only ever come from real buyers, quoted word for word.</p></div>
  </div>
</section>"""))
    urls.append(("/", posts[0]["date"]))

    # ---- 404
    (OUT / "404.html").write_text(layout(
        title="Page not found", path="/404.html", noindex=True, description="Page not found",
        body=f'<section class="wrap landing"><h1>That page wandered off.</h1><p class="dek">Try the <a href="{u("/blog/")}">articles</a> or grab the <a href="{u("/free/")}">free reset</a>.</p></section>'))

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
                             body=f'<section class="wrap"><h1>Welcome and nurture sequence</h1><p class="dek">Preview only (not linked, not indexed). Copy these into your email provider; see site/README.md.</p><div class="table" tabindex="0"><table><thead><tr><th>#</th><th>Send</th><th>Subject</th><th>Job</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>'))

    build_digest()

    # ---- data-driven pages: budget by salary + cost of living by city (pseo.py)
    import pseo
    extra_redirects: list[tuple[str, str]] = []  # (old path, new path) from merged data pages
    urls += pseo.build_pseo({"CFG": CFG, "markdown": markdown, "author_ld": author_ld, "apps_tools": apps_tools_html, "redirects": extra_redirects, "u": u, "absu": absu, "layout": layout, "write": write, "org_ld": org_ld,
                             "magnet_box": magnet_box, "product_card": product_card,
                             "product": products_list[0] if products_list else None,
                             "today": os.environ.get("BUILD_DATE") or date.today().isoformat()})
    _shop = {i["slug"]: i for i in json.loads((CONTENT / "shop.json").read_text())["items"]} \
        if (CONTENT / "shop.json").exists() else {}
    urls += pseo.build_debt({"CFG": CFG, "markdown": markdown, "author_ld": author_ld, "apps_tools": apps_tools_html, "redirects": extra_redirects, "u": u, "absu": absu, "layout": layout, "write": write, "org_ld": org_ld,
                             "magnet_box": magnet_box, "product_card": product_card, "product": None, "shop": _shop,
                             "today": os.environ.get("BUILD_DATE") or date.today().isoformat(),
                             "as_of": fmt_date(os.environ.get("BUILD_DATE") or date.today().isoformat())})

    urls += build_ask(_shop, pseo)
    urls += build_holiday(_shop)
    urls += build_new_year()
    urls += build_money_basics()
    urls += build_tools()

    # ---- newsletter archive: content/newsletter/*.md, one page per issue that has gone out.
    # An issue dated in the future stays unpublished until a build on or after its date
    # (BUILD_DATE=YYYY-MM-DD overrides "today"; NEWSLETTER_SHOW_SCHEDULED=1 previews them locally).
    today = os.environ.get("BUILD_DATE") or date.today().isoformat()
    show_all = os.environ.get("NEWSLETTER_SHOW_SCHEDULED") == "1"
    all_issues = [n for n in load_dir("newsletter") if n.get("status") != "draft"]
    issues = sorted((n for n in all_issues if show_all or str(n["date"]) <= today),
                    key=lambda n: str(n["date"]), reverse=True)
    scheduled = sorted((n for n in all_issues if n not in issues), key=lambda n: str(n["date"]))
    nl_feed_link = f'<link rel="alternate" type="application/rss+xml" title="{esc(CFG["name"])} newsletter" href="{u("/newsletter/feed.xml")}">'
    nl_html: dict[str, str] = {}
    for i, n in enumerate(issues):
        path = f"/newsletter/{n['slug']}/"
        body_html, _ = markdown(n["body"], shortcode_factory(products, f"newsletter-{n['slug']}"))
        nl_html[n["slug"]] = body_html
        newer = issues[i - 1] if i > 0 else None
        older = issues[i + 1] if i + 1 < len(issues) else None
        pager = "".join(
            f'<a href="{u(f"/newsletter/{x["slug"]}/")}">{lbl}: {esc(x["title"])}</a>'
            for lbl, x in (("Older", older), ("Newer", newer)) if x)
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": n["title"],
               "description": n["description"], "datePublished": str(n["date"]), "mainEntityOfPage": absu(path),
               "image": absu("/img/og-default.png"),
               "author": author_ld(),
               "publisher": org_ld(), "isPartOf": {"@type": "Periodical", "name": f"{CFG['name']} newsletter",
                                                    "url": absu("/newsletter/")}},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": CFG["url"] + "/"},
                  {"@type": "ListItem", "position": 2, "name": "Newsletter", "item": absu("/newsletter/")},
                  {"@type": "ListItem", "position": 3, "name": n["title"], "item": absu(path)}]}]
        body = f"""<article class="wrap article">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <a href="{u('/newsletter/')}">Newsletter</a> / <span>Issue {esc(str(n.get('issue', '')))}</span></p>
  <h1>{esc(n['title'])}</h1>
  <p class="meta">Issue {esc(str(n.get('issue', '')))} · Sent {fmt_date(str(n['date']))}</p>
  <div class="prose">
{body_html}
  </div>
  <p class="disclaimer">{esc(CFG['disclaimer'])}</p>
  <nav class="pager" aria-label="More issues">{pager}</nav>
  {magnet_box(f"newsletter-{n['slug']}-end")}
</article>"""
        write(path, layout(title=n.get("seo_title", n["title"]), description=n["description"], path=path,
                           body=body, og_type="article", jsonld=ld, extra_head=nl_feed_link,
                           og={"article:published_time": str(n["date"]), "article:section": "Newsletter",
                               "article:author": editor()["name"]}))
        urls.append((path, str(n["date"])))
    if issues:
        listing = '<ul class="posts">' + "".join(f"""<li class="post">
  <p class="post-pillar">Issue {esc(str(n.get('issue', '')))} · {fmt_date(str(n['date']))}</p>
  <h2><a href="{u(f"/newsletter/{n['slug']}/")}">{esc(n['title'])}</a></h2>
  <p>{esc(n['description'])}</p>
</li>""" for n in issues) + "</ul>"
    else:
        first = f" The first one goes out on {fmt_date(str(scheduled[0]['date']))}." if scheduled else ""
        listing = (f'<p class="empty">No issues yet.{first} Sign up below and it lands in your inbox; '
                   'every issue is posted here afterwards.</p>')
    write("/newsletter/", layout(
        title="The newsletter: one money move a week",
        description=f"Every past issue of the {CFG['name']} newsletter: one specific, plain-English money move a "
                    "week. Read the archive or get the next one by email.",
        path="/newsletter/", extra_head=nl_feed_link, jsonld=[org_ld()], body=f"""<section class="wrap">
  <h1>The newsletter</h1>
  <p class="dek">One email a week, one specific money move, about five minutes to do. No hype, no stock picks. Subscribers also get the free 7-Day Money Reset. Prefer a feed reader? <a href="{u('/newsletter/feed.xml')}">RSS</a>.</p>
  {listing}
  {magnet_box("newsletter-archive")}
</section>"""))
    urls.append(("/newsletter/", str(issues[0]["date"]) if issues else today))
    nl_items = "".join(f"""<item><title>{esc(n['title'])}</title><link>{absu(f"/newsletter/{n['slug']}/")}</link>
<guid isPermaLink="true">{absu(f"/newsletter/{n['slug']}/")}</guid><pubDate>{datetime.strptime(str(n['date']), '%Y-%m-%d').replace(tzinfo=timezone.utc).strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>
<description>{esc(n['description'])}</description><content:encoded><![CDATA[{nl_html[n['slug']].replace(']]>', ']]]]><![CDATA[>')}]]></content:encoded></item>""" for n in issues)
    (OUT / "newsletter" / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>{esc(CFG['name'])} newsletter</title><link>{absu('/newsletter/')}</link>
<atom:link href="{absu('/newsletter/feed.xml')}" rel="self" type="application/rss+xml"/>
<description>One money move a week from {esc(CFG['name'])}.</description><language>en-us</language>{nl_items}</channel></rss>
""")
    # Paste-ready copies for the email provider (every issue, scheduled ones included).
    CFG["_absolute_links"] = True
    for n in all_issues:
        body_abs, _ = markdown(n["body"])
        d = OUT / "emails" / "newsletter" / n["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "email.html").write_text(email_html({"subject": n.get("subject", n["title"]),
                                                  "preheader": n.get("preheader", "")}, body_abs))
    CFG["_absolute_links"] = False

    # ---- redirects for retired blog slugs (stub page everywhere, real 301 on Netlify)
    rules = []
    for old, new in redirects.items():
        target = absu(new)
        write(f"/blog/{old}/", f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex"><link rel="canonical" href="{esc(target)}">
<meta http-equiv="refresh" content="0; url={esc(u(new))}"><title>Moved</title></head>
<body><p>This page moved to <a href="{esc(u(new))}">{esc(target)}</a>.</p></body></html>
""")
        rules.append(f"{u(f'/blog/{old}/')} {u(new)} 301!")
    for old, new in extra_redirects:
        target = absu(new)
        write(old, f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex"><link rel="canonical" href="{esc(target)}">
<meta http-equiv="refresh" content="0; url={esc(u(new))}"><title>Moved</title></head>
<body><p>This page moved to <a href="{esc(u(new))}">{esc(target)}</a>.</p></body></html>
""")
        rules.append(f"{u(old)} {u(new)} 301!")  # ! = redirect even though the stub file exists
    (OUT / "_redirects").write_text("\n".join(rules) + "\n")
    # Netlify cache headers. File names aren't fingerprinted, so images and downloads cache for a week and
    # CSS/JS for an hour (Netlify revalidates by ETag after that). Netlify gzips/brotlis text on its own.
    week, hour = "public, max-age=604800", "public, max-age=3600, stale-while-revalidate=86400"
    (OUT / "_headers").write_text("".join(f"{u(p)}\n  Cache-Control: {v}\n" for p, v in [
        ("/img/*", week), ("/downloads/*", week), ("/*.css", hour), ("/*.js", hour)]))

    # ---- sitemap, robots, feed
    sm = "".join(f"<url><loc>{esc(absu(p))}</loc><lastmod>{d}</lastmod></url>" for p, d in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: {u('/emails/')}\nDisallow: {u('/free/thanks/')}\nDisallow: {u('/holiday/thanks/')}\nDisallow: {u('/new-year/thanks/')}\nDisallow: {u('/money-basics/thanks/')}\n"
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


def build_ask(shop: dict, pseo) -> list[tuple[str, str]]:
    """/ask/: content/ask.md, '## Group' + '### Question' + answer. One page, a jump list, FAQPage schema."""
    src = CONTENT / "ask.md"
    if not src.exists():
        return []
    meta, md = parse_front_matter(src.read_text())
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    rules, _ = pseo.load()
    calc = CFG.get("calculators_url", CFG["url"] + "/calculators").rstrip("/")

    def token(m):
        kind, val = m.group(1), m.group(2)
        th = pseo.take_home(rules, int(val))
        return f"${th['month' if kind == 'month' else 'paycheck']:,.0f}"
    md = re.sub(r"\{(month|paycheck):(\d+)\}", token, md)

    def shop_link(m):
        if m.group(1) not in shop:
            raise SystemExit(f"content/ask.md: unknown shop item '{m.group(1)}'")
        return f"({product_path(shop[m.group(1)])})"
    md = re.sub(r"\(shop:([a-z0-9-]+)\)", shop_link, md)
    md = re.sub(r"\(calc:([a-z-]+)\)", lambda m: f"({calc}/{m.group(1)}/)", md)

    groups = []
    for g in re.split(r"^## ", md, flags=re.M)[1:]:
        name, rest = g.split("\n", 1)
        qs = [(q.strip(), a.strip()) for q, a in re.findall(r"^### (.+?)\n(.*?)(?=^### |\Z)", rest, re.S | re.M)]
        groups.append((name.strip(), qs))
    strip = lambda h: " ".join(re.sub(r"<[^>]+>", "", h).split())
    toc, sections, faq = [], [], []
    for name, qs in groups:
        items, links = [], []
        for q, a in qs:
            qid = slug_id(q)[:60].strip("-")
            ans, _ = markdown(a)
            ans = re.sub(r"<p><strong>([^<]+:)</strong>", r'<p class="ask-tools"><strong>\1</strong>', ans)
            items.append(f'<div class="ask-q" id="{qid}"><h3>{esc(q)}</h3>{ans}'
                         f'<p class="ask-link"><a href="#{qid}">Link to this answer</a> · <a href="#top">All questions</a></p></div>')
            links.append(f'<li><a href="#{qid}">{esc(q)}</a></li>')
            body_txt = strip(ans.split('<p class="ask-tools">')[0])
            faq.append({"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": body_txt}})
        gid = slug_id(name)
        toc.append(f'<h2 class="ask-toc-h"><a href="#{gid}">{esc(name)}</a></h2><ul>{"".join(links)}</ul>')
        sections.append(f'<section aria-labelledby="{gid}"><h2 id="{gid}">{esc(name)}</h2>{"".join(items)}</section>')
    updated = str(meta.get("updated", date.today().isoformat()))
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": absu("/")},
              {"@type": "ListItem", "position": 2, "name": "Money questions", "item": absu("/ask/")}]}, org_ld()]
    body = f"""<article class="wrap ask" id="top">
  <h1>Money questions, answered</h1>
  <p class="dek">{len(faq)} questions people ask about paychecks, rent, cars, credit card debt and saving on a tight budget. Each answer is short, says what it depends on, and links a free tool to work out your own numbers. Updated {fmt_date(updated)}.</p>
  <nav class="ask-toc" aria-label="All questions">{"".join(toc)}</nav>
  {"".join(sections)}
  <p class="disclaimer">General education, not financial, tax or legal advice. Tax figures are 2026 federal rules for a single filer unless an answer says otherwise; your state, deductions and situation change the numbers.</p>
  {magnet_box("ask")}
</article>"""
    write("/ask/", layout(title=meta.get("seo_title", meta["title"]), description=meta["description"], path="/ask/",
                          body=body, jsonld=ld))
    return [("/ask/", updated)]


def new_year_live() -> bool:
    src = CONTENT / "new-year.md"
    if not src.exists():
        return False
    meta, _ = parse_front_matter(src.read_text())
    day = os.environ.get("BUILD_DATE") or date.today().isoformat()
    return os.environ.get("BLOG_SHOW_SCHEDULED") == "1" or str(meta.get("live", "")) <= day


def build_new_year() -> list[tuple[str, str]]:
    """/new-year/: landing page for the 5-email New Year Money Reset mini-course (content/new-year.md). Built from
    its `live` date (links to it render as text before then). The form sends source=new-year-reset (or the
    page's course_source); the email provider starts the course from that source. Thanks page: /new-year/thanks/."""
    src = CONTENT / "new-year.md"
    if not src.exists():
        return []
    if not new_year_live():
        return []
    meta, md = parse_front_matter(src.read_text())
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    faq = extract_faq(md)
    days = re.findall(r"^### (Day \d+): (.+)$", md, re.M)
    body_html, _toc = markdown(md)
    source = meta.get("course_source", "new-year-reset")
    day_list = "".join(f"<li><strong>{esc(d)}:</strong> {esc(t)}</li>" for d, t in days)
    optin = f"""<div class="magnet no-img" id="signup">
  <div>
    <p class="kicker">Free 5-day email course</p>
    <h2 class="magnet-title">Start the New Year Money Reset</h2>
    <p>Five emails, January 1 to 5. One 15-minute task a day. By January 5, you'll have a money plan you can actually run in 2027.</p>
    <ol class="course-days">{day_list}</ol>
    {email_form(source, button="Start the reset (free)", thanks_path="/new-year/thanks/")}
  </div>
</div>"""
    updated = str(meta.get("updated", meta.get("live", date.today().isoformat())))
    ld = [{"@context": "https://schema.org", "@type": "Course", "name": meta["title"],
           "description": meta["description"], "provider": org_ld(), "isAccessibleForFree": True,
           "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online",
                                 "courseWorkload": "PT1H15M"},
           "offers": {"@type": "Offer", "price": 0, "priceCurrency": "USD", "category": "Free"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    body = f"""<article class="wrap article new-year">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <span>New Year money reset</span></p>
  <h1>{esc(meta['title'])}</h1>
  <p class="dek">{esc(meta['description'])}</p>
  <p class="meta">Updated {fmt_date(updated)} · {byline()}</p>
  {optin}
  <div class="prose">
{body_html}
  </div>
  <section class="next"><h2>Start before day 1</h2><ul class="related">
    <li><a href="{u('/budget/')}">Budget by salary</a>: a full monthly plan for your salary band.</li>
    <li><a href="{u('/debt-payoff/')}">Debt payoff calculator</a>: avalanche or snowball, month by month.</li>
    <li>{inline('[How to make a budget you will keep](/blog/how-to-make-a-budget-you-will-keep/)')}</li>
  </ul></section>
  <p class="disclaimer">{esc(CFG['disclaimer'])}</p>
</article>"""
    write("/new-year/", layout(title=meta.get("seo_title", meta["title"]), description=meta["description"],
                               path="/new-year/", body=body, og_type="article", jsonld=ld))
    write("/new-year/thanks/", layout(
        title="Your New Year Money Reset", path="/new-year/thanks/", noindex=True, description="You're signed up.",
        body=f"""<section class="wrap landing thanks">
  <h1>You're in.</h1>
  <p class="dek">Day 1 arrives on January 1 at 7am Eastern (or within a few minutes if that's already passed), and the other four follow one a day. Check the promotions tab if you don't see it.</p>
  <p>Before then, find a recent payslip and your bank and card balances: Day 1 starts with them.</p>
  <p><a href="{u('/new-year/')}">Back to the reset</a> · <a href="{u('/free/')}">Also free: the 7-Day Money Reset</a></p>
</section>"""))
    return [("/new-year/", updated)]


def build_money_basics() -> list[tuple[str, str]]:
    """/money-basics/: landing page for the free "Money Basics in 7 days" email course (content/money-basics.md),
    built from the best-of digest's format. Front matter `sender_form` holds the embed HTML from Sender; while it's
    REPLACE_ME (or empty) the page uses the normal signup form with source=course_source. Thanks: /money-basics/thanks/."""
    src = CONTENT / "money-basics.md"
    if not src.exists():
        return []
    meta, md = parse_front_matter(src.read_text())
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    faq = extract_faq(md)
    days = re.findall(r"^### (Day \d+): (.+)$", md, re.M)
    body_html, _toc = markdown(md)
    source = meta.get("course_source", "money-basics-7-days")
    sender = str(meta.get("sender_form", "") or "").strip()
    if sender and "REPLACE_ME" not in sender:
        form = f'<div class="sender-form">{sender}</div>'
    else:
        form = ('<!-- Sender form placeholder: paste Sender\'s embed into content/money-basics.md > sender_form -->'
                + email_form(source, button="Start the free course", thanks_path="/money-basics/thanks/"))
    day_list = "".join(f"<li><strong>{esc(d)}:</strong> {esc(t)}</li>" for d, t in days)
    optin = f"""<div class="magnet no-img" id="signup">
  <div>
    <p class="kicker">Free 7-day email course</p>
    <h2 class="magnet-title">Start Money Basics in 7 days</h2>
    <p>Seven emails, one a day from the day you sign up. One idea with the numbers shown, one task under 20 minutes.</p>
    <ol class="course-days">{day_list}</ol>
    {form}
  </div>
</div>"""
    updated = str(meta.get("updated", date.today().isoformat()))
    ld = [{"@context": "https://schema.org", "@type": "Course", "name": meta["title"],
           "description": meta["description"], "provider": org_ld(), "isAccessibleForFree": True,
           "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online", "courseWorkload": "PT2H20M"},
           "offers": {"@type": "Offer", "price": 0, "priceCurrency": "USD", "category": "Free"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    body = f"""<article class="wrap article money-basics">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <span>Money Basics in 7 days</span></p>
  <h1>{esc(meta['title'])}</h1>
  <p class="dek">{esc(meta['description'])}</p>
  <p class="meta">Updated {fmt_date(updated)} · {byline()}</p>
  {optin}
  <div class="prose">
{body_html}
  </div>
  <p class="disclaimer">{esc(CFG['disclaimer'])}</p>
</article>"""
    write("/money-basics/", layout(title=meta.get("seo_title", meta["title"]), description=meta["description"],
                                   path="/money-basics/", body=body, og_type="article", jsonld=ld))
    write("/money-basics/thanks/", layout(
        title="You're in: Money Basics in 7 days", path="/money-basics/thanks/", noindex=True,
        description="You're signed up.", body=f"""<section class="wrap landing thanks">
  <h1>You're in.</h1>
  <p class="dek">Day 1 is on its way. If you don't see it in a few minutes, check your promotions or spam folder, and confirm your email if we asked you to.</p>
  <p>Before Day 1, find one recent payslip: the first task starts with it.</p>
  <p><a href="{u('/money-basics/')}">Back to the course</a> · <a href="{u('/start/')}">Start here by goal</a></p>
</section>"""))
    return [("/money-basics/", updated)]


def build_tools() -> list[tuple[str, str]]:
    """/tools/: every free tool. Site tools (related.json > tools) first, then the apps site's tools by group
    (apps.json, shown only when apps_url is set)."""
    site_tools = load_related()["tools"]
    apps = load_apps()
    site_li = "".join(f'<li><a href="{u(t["path"])}"><strong>{esc(t["title"])}</strong></a>: {esc(t["blurb"])}</li>'
                      for t in site_tools.values())
    groups: dict[str, list[dict]] = {}
    for t in apps:
        groups.setdefault(t["group"], []).append(t)
    upcoming = []
    if apps and (CONTENT / "data" / "apps.json").exists():
        upcoming = json.loads((CONTENT / "data" / "apps.json").read_text()).get("upcoming", [])
    soon: dict[str, list[dict]] = {}
    for t in upcoming:
        soon.setdefault(t["group"], []).append(t)
        groups.setdefault(t["group"], [])
    soon_li = lambda t: f'<li class="soon"><strong>{esc(t["title"])}</strong> (coming soon): {esc(t["blurb"].replace(" Coming soon.", ""))}</li>'
    apps_html = "".join(f'<h2>{esc(g)}</h2><ul class="tool-list">{"".join(apps_li(t) for t in ts)}{"".join(soon_li(t) for t in soon.get(g, []))}</ul>'
                        for g, ts in groups.items())
    intro_apps = (f'<p>The calculators and trackers below run on our tools site, '
                  f'<a href="{esc(apps_base())}/">{esc(urlparse(apps_base()).netloc)}</a>. What you type stays in '
                  'your browser unless you choose to send it to us (for example, a budget for review).</p>' if apps else "")
    items = [(t["title"], absu(t["path"])) for t in site_tools.values()] + [(t["title"], apps_base() + t["path"]) for t in apps]
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": f"Free money tools from {CFG['name']}",
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "url": url}
                               for i, (n, url) in enumerate(items)]}, org_ld()]
    body = f"""<article class="wrap article tools-page">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <span>Free tools</span></p>
  <h1>{esc(CFG['name'])} tools</h1>
  <p class="dek">Every free calculator, planner, tracker and checklist we make, for budgets, bills, debt, saving, taxes, freelance income and scam safety. No sign-up.</p>
  <div class="prose">
  <h2>On this site</h2>
  <ul class="tool-list">{site_li}
  <li><a href="{u('/free/')}"><strong>The 7-Day Money Reset</strong></a>: a free printable plan for your first week.</li></ul>
  {intro_apps}
  {apps_html}
  <h2>Printables and templates</h2>
  <p>Planners, trackers and spreadsheets, some free, are in the <a href="{u('/shop/')}">Shop</a>.</p>
  </div>
</article>"""
    write("/tools/", layout(title=f"Free money tools and calculators · {CFG['name']}", path="/tools/", body=body,
                            description="Free budget, debt, savings and paycheck calculators and planners: budget by "
                                        "salary, debt payoff, take-home pay by state, emergency fund and more.",
                            jsonld=ld))
    return [("/tools/", date.today().isoformat())]


def build_holiday(shop: dict) -> list[tuple[str, str]]:
    """/holiday/: Black Friday traps, a holiday budget, BNPL rules and the year-end checklist (content/holiday.md),
    with the free printable Year-End Money Checklist as the email opt-in (thanks page: /holiday/thanks/)."""
    src = CONTENT / "holiday.md"
    if not src.exists():
        return []
    meta, md = parse_front_matter(src.read_text())
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    faq = extract_faq(md)
    body_html, toc = markdown(md)
    toc_html = '<nav class="toc" aria-label="On this page"><p>On this page</p><ol>' + "".join(
        f'<li><a href="#{i}">{t}</a></li>' for i, t in toc if i not in ("common-questions", "sources")) + "</ol></nav>"
    pdf = "year-end-money-checklist.pdf"
    optin = f"""<div class="magnet holiday-optin" id="checklist">
  <img src="{u('/img/year-end-checklist-cover.jpg')}" alt="Cover of the Year-End Money Checklist" width="150" height="194">
  <div>
    <p class="kicker">Free printable</p>
    <h2 class="magnet-title">The Year-End Money Checklist</h2>
    <p>Four pages: the 10 money moves to make before January 1 (with their deadlines), a one-page holiday plan in four numbers, and the Black Friday and pay-in-4 checks. Print it or fill it in on a tablet.</p>
    {email_form("holiday-checklist", button="Send me the checklist", thanks_path="/holiday/thanks/")}
  </div>
</div>"""
    tools = []
    planner = holiday_planner_url()
    if planner:
        tools.append(f'<li><a href="{esc(planner)}">Holiday spending planner</a> (free app): a gift list with a budget per '
                     'person, a total cap, extras like travel and food, and what pay-in-4 really costs. It saves in your '
                     'browser only.</li>')
    if new_year_live():
        tools.append(f'<li><a href="{u("/new-year/")}">The New Year Money Reset</a> (free): a 5-day email course '
                     'that turns January resolutions into a plan.</li>')
    for slug in ("holiday-savings-planner", "gift-budget-planner", "no-spend-challenge"):
        it = shop.get(slug)
        if it:
            price = "free" if not it["price"] else f"${it['price']:g}"
            tools.append(f'<li><a href="{u(product_path(it))}">{esc(it["name"])}</a> ({price}): '
                         f'{esc(it.get("blurb", ""))}</li>')
    tools_html = (f'<section class="next"><h2>Tools and printables for the season</h2><ul class="related">{"".join(tools)}</ul></section>'
                  if tools else "")
    updated = str(meta.get("updated", date.today().isoformat()))
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
           "description": meta["description"], "datePublished": updated, "dateModified": updated,
           "mainEntityOfPage": absu("/holiday/"), "image": absu("/img/og-default.png"),
           "author": author_ld(), "publisher": org_ld()},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    body = f"""<article class="wrap article holiday">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <span>Holiday money</span></p>
  <h1>{esc(meta['title'])}</h1>
  <p class="dek">A holiday budget in four numbers, the Black Friday and pay-later traps, and ten money moves to make before January 1.</p>
  <p class="meta">Updated {fmt_date(updated)} · {byline()}</p>
  {optin}
  {f'<p class="planner-link">Prefer to plan on screen? <a href="{esc(planner)}">Open the free holiday spending planner</a>: gift list, per-person budgets and the real cost of pay-in-4.</p>' if planner else ''}
  {toc_html}
  <div class="prose">
{body_html}
  </div>
  {tools_html}
  <p class="disclaimer">Examples are hypothetical. {esc(CFG['disclaimer'])}</p>
</article>"""
    write("/holiday/", layout(title=meta.get("seo_title", meta["title"]), description=meta["description"],
                              path="/holiday/", body=body, og_type="article", jsonld=ld))
    write("/holiday/thanks/", layout(
        title="Your year-end checklist", path="/holiday/thanks/", noindex=True, description="Your free download.",
        body=f"""<section class="wrap landing thanks">
  <h1>You're in. Here's your checklist.</h1>
  <p class="dek">{esc(CFG['email'].get('thanks_note', 'Check your inbox too: your first email is on its way.'))}</p>
  <p><a class="btn big" href="{u('/downloads/' + pdf)}" download>Download the Year-End Money Checklist (PDF)</a></p>
  <p>Start with the holiday plan on page 3: it takes about 30 minutes. Then tick off one year-end move a day.</p>
  <p><a href="{u('/holiday/')}">Back to holiday money</a> · <a href="{u('/free/')}">Also free: the 7-Day Money Reset</a></p>
</section>"""))
    return [("/holiday/", updated)]


SHOP_GROUPS = [("budget", "Budget planners"), ("savings", "Savings challenges"), ("debt", "Debt payoff"),
               ("trackers", "Trackers and records")]


def store_url(it: dict, store: str) -> str:
    """An item's own link wins; otherwise a placeholder built from site.json > stores."""
    stores = CFG.get("stores", {})
    if store == "etsy":
        if it.get("etsy_url"):
            return it["etsy_url"]
        return stores.get("etsy", "https://www.etsy.com/shop/REPLACE_ME") + "?search_query=" + quote(it["name"])
    if it.get("url"):
        return it["url"]
    return stores.get("gumroad", "https://example.gumroad.com").rstrip("/") + "/l/" + it["slug"]


def shop_buttons(it: dict) -> str:
    out = []
    for store in it["stores"]:
        label = {"gumroad": "Get it" if it["price"] else "Get it free", "etsy": "On Etsy"}[store]
        if store == "etsy" and "gumroad" in it["stores"]:
            cls = "btn ghost"
        else:
            cls = "btn"
        out.append(f'<a class="{cls} plausible-event-name=Product+Click plausible-event-product={esc(it["slug"])} '
                   f'plausible-event-store={store}" href="{esc(store_url(it, store))}" rel="noopener" '
                   f'data-buy="{esc(it["slug"])}">{label}</a>')
    if it.get("page"):
        out.insert(0, f'<a class="btn ghost" href="{u(it["page"])}">Details</a>')
    return "".join(out)


def product_hero_img(p: dict) -> str:
    """Product hero: the 640px card JPG at 1x and a 1280px JPG at 2x when they exist; the PNG stays for og:image."""
    big = p["image"].rsplit(".", 1)[0] + "-1280.jpg"
    if p.get("thumb") and (STATIC / big.lstrip("/")).is_file():
        src = f'src="{u(p["thumb"])}" srcset="{u(p["thumb"])} 640w, {u(big)} 1280w" sizes="(max-width: 700px) 100vw, 640px"'
    else:
        src = f'src="{u(p["image"])}"'
    return f'<img {src} alt="{esc(p["title"])} preview" width="640" height="360" fetchpriority="high">'


def holiday_planner_url() -> str:
    """The apps' holiday spending planner (apps/budget/holiday.html, PR #8). It deploys as its own Netlify site, so
    the link appears once site.json > apps_url is set to that site's address (or env APPS_URL)."""
    base = apps_base()
    return f"{base}/budget/holiday.html" if base else ""


def holiday_note() -> str:
    """Home-page pointer to /holiday/, shown only Nov 1 - Dec 31 of the build date (the daily build turns it on and off)."""
    day = os.environ.get("BUILD_DATE") or date.today().isoformat()
    if (day[5:7] == "12" and day[8:] >= "26" or day[5:7] == "01") and new_year_live():
        return (f'\n      <p class="quiz-link">New year: <a href="{u("/new-year/")}">take the free 5-day New Year '
                f'Money Reset</a>.</p>')
    if day[5:7] not in ("11", "12"):
        return ""
    return (f'\n      <p class="quiz-link">Holiday season: <a href="{u("/holiday/")}">plan it in four numbers and '
            f'get the free year-end checklist</a>.</p>')


def shop_price(it: dict) -> str:
    p = it["price"]
    txt = "Free" if not p else f"${p:g}"
    if it.get("separately"):
        save = it["separately"] - p
        txt += f' <span class="was">${it["separately"]:g} separately, save ${save:g}</span>'
    return f'<p class="price">{txt}</p>'


def shop_card(it: dict, image: bool = True, eager: bool = False) -> str:
    # The first card is the mobile LCP image, so it loads eagerly with high priority; the rest are lazy.
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    img = (f'<img src="{u(it["image"])}" alt="{esc(it["name"])} cover" width="360" height="360" {load}>'
           if image and it.get("image") else "")
    return f"""<div class="shop-card{' has-img' if img else ''}" id="item-{esc(it['slug'])}">{img}<div class="shop-body">
  <h3><a href="{u(product_path(it))}">{esc(it["name"])}</a></h3><p>{esc(it.get("blurb", ""))}</p>{shop_price(it)}
  <p class="shop-buy">{shop_buttons(it)}</p></div></div>"""


def build_shop(items: list[dict]) -> None:
    bundles = [i for i in items if i.get("bundle")]
    kits = [i for i in items if i["kind"] == "kit" and not i.get("bundle")]
    sheets = [i for i in items if i["kind"] == "sheets" and not i.get("bundle")]
    notion = [i for i in items if i["kind"] == "notion" and not i.get("bundle")]
    prints = [i for i in items if i["kind"] == "printable" and not i.get("bundle")]
    groups = "".join(
        f'<h3 class="shop-group" id="printables-{k}">{esc(label)}</h3><div class="shop-list">'
        + "".join(shop_card(i, image=False) for i in prints if i.get("group") == k) + "</div>"
        for k, label in SHOP_GROUPS if any(i.get("group") == k for i in prints))
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": f"{CFG['name']} shop",
           "itemListElement": [{"@type": "ListItem", "position": n + 1, "item": {
               "@type": "Product", "name": i["name"], "description": i.get("blurb", ""),
               "brand": {"@type": "Brand", "name": CFG["name"]},
               **({"image": absu(i["image"])} if i.get("image") else {}),
               "offers": {"@type": "Offer", "price": f'{i["price"]:.2f}', "priceCurrency": "USD",
                          "availability": "https://schema.org/InStock",
                          "url": store_url(i, i["stores"][0])}}} for n, i in enumerate(bundles + kits)]},
          org_ld()]
    count = len(items)
    body = f"""<section class="wrap shop">
  <h1>Shop</h1>
  <p class="dek">{count} money tools from {esc(CFG['name'])}: guide-and-spreadsheet kits, Google Sheets and Notion templates, and printables. One payment, no subscription, files you keep. Kits and templates are sold through Gumroad, printables through our Etsy shop.</p>
  <p class="chips">By goal: {"".join(f'<a class="chip" href="{u(f"/shop/{g['id']}/")}">{esc(g["h1"].split(":")[0])}</a>' for g in load_placements()["goals"])}</p>
  <p class="chips"><a class="chip" href="#bundles">Bundles</a><a class="chip" href="#kits">Guide kits</a><a class="chip" href="#templates">Sheets and Notion</a><a class="chip" href="#printables">Printables</a></p>
  <h2 id="bundles">Bundles</h2>
  <p>The best value if you want more than one. Savings are against buying the same items one by one.</p>
  <div class="shop-grid">{''.join(shop_card(i, eager=(n == 0)) for n, i in enumerate(bundles))}</div>
  <h2 id="kits">Guide and spreadsheet kits</h2>
  <p>Each kit is a short PDF guide plus a spreadsheet that does the maths (Excel, Google Sheets or Numbers). Start with the one that matches your problem: leaking subscriptions, no system, credit, debt or investing.</p>
  <div class="shop-grid">{''.join(shop_card(i) for i in kits)}</div>
  <h2 id="templates">Google Sheets and Notion templates</h2>
  <div class="shop-list">{''.join(shop_card(i, image=False) for i in sheets + notion)}</div>
  <h2 id="printables">Printables</h2>
  <p>Letter and A4 PDFs to print at home or fill in on a tablet.</p>
  {groups}
  <p class="disclaimer">Prices in US dollars; Etsy may show local currency and add sales tax. Our products are educational tools, not financial advice. Refunds: email {esc(CFG.get('contact_email', ''))} within 14 days.</p>
  {magnet_box('shop')}
</section>"""
    write("/shop/", layout(title="Shop: budget kits, templates and printables",
                           description=f"Every {CFG['name']} product: budget and debt payoff kits, Google Sheets and "
                                       "Notion templates, savings challenges and printables. Bundles save up to 85%.",
                           path="/shop/", body=body, jsonld=ld))


def product_path(it: dict) -> str:
    """Each product's own page: its landing page if it has one (shop.json > page), else /shop/<slug>/."""
    return it.get("page") or f"/shop/{it['slug']}/"


KIND_INFO = {
    "kit": ("Guide and spreadsheet kit", "A short PDF guide plus a spreadsheet that does the maths. The spreadsheet works in Excel, Google Sheets or Numbers."),
    "sheets": ("Google Sheets template", "A Google Sheets template. After checkout you get a link to make your own copy in your Google account."),
    "notion": ("Notion template", "A Notion template. After checkout you get a link to duplicate it into your own Notion workspace."),
    "printable": ("Printable PDF", "Letter and A4 PDFs to print at home or fill in on a tablet."),
}


def bundle_contains(bundle: dict, it: dict) -> bool:
    name = re.sub(r" (Kit|Pack|Printable)$", "", re.sub(r"^The ", "", it["name"]))
    return bundle is not it and bool(bundle.get("bundle")) and name.lower() in bundle.get("blurb", "").lower()


def build_product_pages() -> list[tuple[str, str]]:
    """/shop/<slug>/: one page per product, so pins and articles can link straight to it. Buy buttons use the
    same (placeholder) store links as the shop; Product schema carries the price and the store link."""
    items = list(shop_items().values())
    goals = load_placements()["goals"]
    goal_ids = {g["id"] for g in goals}
    arts = load_placements()["articles"]
    by_slug = {p["slug"]: p for p in LIVE_POSTS}
    out = []
    for it in items:
        if it.get("page"):
            continue  # has its own landing page already
        if it["slug"] in goal_ids:
            raise SystemExit(f"shop.json: item slug '{it['slug']}' clashes with a /shop/<goal>/ page")
        path = product_path(it)
        kind, how = KIND_INFO.get(it["kind"], ("Download", ""))
        if it.get("bundle"):
            kind = "Bundle"
        img = (f'<img src="{u(it["image"])}" alt="{esc(it["name"])} cover" width="360" height="360" fetchpriority="high">'
               if it.get("image") else "")
        guides = [by_slug[a] for a, picks in arts.items() if it["slug"] in picks and a in by_slug][:4]
        guides_html = ("<h2>Free guides that go with it</h2><ul class=\"related\">" + "".join(
            f'<li><a href="{u(f"/blog/{p["slug"]}/")}">{esc(p["title"])}</a></li>' for p in guides) + "</ul>") if guides else ""
        # Only bundles whose blurb names at least two of their items list contents (others say "every X" in prose).
        inside_of = {b["slug"]: [i for i in items if bundle_contains(b, i)] for b in items if b.get("bundle")}
        inside_of = {k: v for k, v in inside_of.items() if len(v) >= 2}
        in_bundles = [b for b in items if it in inside_of.get(b["slug"], [])]
        bundles_html = ("<p>Also included in " + ", ".join(
            f'<a href="{u(product_path(b))}">{esc(b["name"])}</a> (${b["price"]:g})' for b in in_bundles) + ".</p>") if in_bundles else ""
        inside = inside_of.get(it["slug"], [])
        inside_html = ("<h2>What's inside</h2><ul class=\"related\">" + "".join(
            f'<li><a href="{u(product_path(i))}">{esc(i["name"])}</a> (${i["price"]:g} on its own)</li>' for i in inside) + "</ul>") if inside else ""
        in_goals = [g for g in goals if it["slug"] in g["items"]]
        goals_html = ("<p class=\"chips\">For: " + "".join(
            f'<a class="chip" href="{u(f"/shop/{g["id"]}/")}">{esc(g["h1"].split(":")[0])}</a>' for g in in_goals) + "</p>") if in_goals else ""
        similar = [i for i in items if i is not it and (i.get("group") or i["kind"]) == (it.get("group") or it["kind"])][:4]
        similar_html = ("<h2>More like this</h2><ul class=\"related\">" + "".join(
            f'<li><a href="{u(product_path(i))}">{esc(i["name"])}</a> ({"free" if not i["price"] else f"${i['price']:g}"})</li>'
            for i in similar) + "</ul>") if similar else ""
        stores = " and ".join({"gumroad": "Gumroad", "etsy": "Etsy"}.get(x, x) for x in it["stores"])
        ld = [{"@context": "https://schema.org", "@type": "Product", "name": it["name"], "sku": it["slug"],
               "description": it.get("blurb", ""), "brand": {"@type": "Brand", "name": CFG["name"]},
               "url": absu(path), **({"image": absu(it["image"])} if it.get("image") else {}),
               "offers": {"@type": "Offer", "price": f'{it["price"]:.2f}', "priceCurrency": "USD",
                          "availability": "https://schema.org/InStock", "url": store_url(it, it["stores"][0])}},
              org_ld()]
        body = f"""<section class="wrap shop product-page">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <a href="{u('/shop/')}">Shop</a></p>
  <div class="product-head{' has-img' if img else ''}">{img}<div>
  <p class="tc-label">{esc(kind)}</p>
  <h1>{esc(it["name"])}</h1>
  <p class="dek">{esc(it.get("blurb", ""))}</p>
  {shop_price(it)}
  <p class="shop-buy">{shop_buttons(it)}</p>
  {goals_html}</div></div>
  <h2>What you get</h2>
  <p>{esc(how)} Sold through {stores}: one payment, no subscription, and the files are yours to keep.</p>
  {bundles_html}
  {inside_html}
  {guides_html}
  {similar_html}
  <p><a href="{u('/shop/')}">See the whole shop</a></p>
  <p class="disclaimer">This is our own product: we earn the full price when you buy it. Prices in US dollars; Etsy may show local currency and add sales tax. An educational tool, not financial advice. Refunds: email {esc(CFG.get('contact_email', ''))} within 14 days.</p>
  {magnet_box(f"product-{it['slug']}")}
</section>"""
        desc = it.get("blurb", "")
        if len(desc) > 155:
            desc = desc[:152].rsplit(" ", 1)[0].rstrip(",;:.") + "..."
        write(path, layout(title=f"{it['name']} ({kind.lower()})", description=desc, path=path, body=body, jsonld=ld))
        out.append((path, date.today().isoformat()))
    return out


def build_shop_goals() -> list[tuple[str, str]]:
    """/shop/<goal>/: one landing page per Start here goal (content/data/placements.json > goals), with that
    goal's templates and the free guides for it first."""
    items = shop_items()
    starts = {g["id"]: g for g in load_start()["goals"]}
    out = []
    for g in load_placements()["goals"]:
        path = f"/shop/{g['id']}/"
        picks = [items[s] for s in g["items"] if s in items]
        sg = starts.get(g["id"])
        by_slug = {p["slug"]: p for p in LIVE_POSTS}
        free = [by_slug[s] for s in (sg["articles"] if sg else []) if s in by_slug][:4]
        free_html = "".join(f'<li><a href="{u(f"/blog/{p["slug"]}/")}">{esc(p["title"])}</a></li>' for p in free)
        start_link = f'{u("/start/")}#{slug_id(sg["heading"])}' if sg else u("/start/")
        others = "".join(f'<a class="chip" href="{u(f"/shop/{o["id"]}/")}">{esc(o["title"].replace("Templates for ", "").capitalize())}</a>'
                         for o in load_placements()["goals"] if o["id"] != g["id"])
        ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": g["title"],
               "itemListElement": [{"@type": "ListItem", "position": n + 1, "url": store_url(i, i["stores"][0]),
                                    "name": i["name"]} for n, i in enumerate(picks)]}, org_ld()]
        body = f"""<section class="wrap shop">
  <p class="crumbs"><a href="{u('/')}">Home</a> / <a href="{u('/shop/')}">Shop</a></p>
  <h1>{esc(g["h1"])}</h1>
  <p class="dek">{esc(g["intro"])}</p>
  <div class="free-first"><h2>Free first</h2><p>Everything these templates do is explained for free in our guides. <a href="{start_link}">The steps for this goal</a>{" and these guides:" if free_html else "."}</p>{f"<ul>{free_html}</ul>" if free_html else ""}</div>
  <h2>{esc(g["title"])}</h2>
  <div class="shop-grid">{''.join(shop_card(i, eager=(n == 0)) for n, i in enumerate(x for x in picks if x.get("image")))}</div>
  <div class="shop-list">{''.join(shop_card(i, image=False) for i in picks if not i.get("image"))}</div>
  <p class="chips">Other goals: {others} <a class="chip" href="{u('/shop/')}">The whole shop</a></p>
  <p class="disclaimer">These are our own products: we earn the full price when you buy one. Prices in US dollars; Etsy may show local currency and add sales tax. Educational tools, not financial advice. Refunds: email {esc(CFG.get('contact_email', ''))} within 14 days.</p>
  {magnet_box(f"shop-{g['id']}")}
</section>"""
        write(path, layout(title=g["h1"], description=g["intro"][:155].rsplit(" ", 1)[0].rstrip(",;:") + ".",
                           path=path, body=body, jsonld=ld))
        out.append((path, date.today().isoformat()))
    return out


def email_html(e: dict, body: str) -> str:
    """A plain, inline-styled email body that survives every email client. Paste into your provider's
    HTML editor; the provider adds the unsubscribe link and postal address footer."""
    body = re.sub(r"<h(\d)[^>]*>", r'<h\1 style="font-size:20px;margin:24px 0 8px">', body)
    body = body.replace("<p>", '<p style="margin:0 0 16px">')
    body = body.replace("<table>", '<table style="border-collapse:collapse;width:100%;font-size:15px;margin:0 0 16px">')
    body = body.replace("<th>", '<th style="border:1px solid #d9d3c3;padding:6px 8px;text-align:left;background:#eaf6ef">')
    body = body.replace("<td>", '<td style="border:1px solid #d9d3c3;padding:6px 8px">')
    body = body.replace("<blockquote>", '<blockquote style="margin:0 0 16px;padding:8px 14px;border-left:4px solid #f2b134;background:#fdf3dd">')
    body = body.replace("<a ", '<a style="color:#1a7a45;font-weight:600" ')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(e['subject'])}</title></head>
<body style="margin:0;background:#f4f1e8">
<span style="display:none;max-height:0;overflow:hidden">{esc(e.get('preheader', ''))}</span>
<div style="max-width:560px;margin:0 auto;padding:24px 20px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:#0b1d13;background:#ffffff">
{body}
<p style="margin:24px 0 0;font-size:12px;color:#4b5a51">{esc(CFG['disclaimer'])}</p>
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
