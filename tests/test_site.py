"""The static website in site/ builds, and every internal link and asset resolves."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest

SITE = Path(__file__).resolve().parents[1] / "site"


def _build(tmp_path, url, **env):
    out = tmp_path / "public"
    e = {**os.environ, "SITE_OUT": str(out), "SITE_URL": url, "BLOG_SHOW_SCHEDULED": "1", **env}
    e.pop("URL", None)
    subprocess.run([sys.executable, str(SITE / "build.py")], check=True, env=e, capture_output=True)
    return out


@pytest.mark.parametrize("url", ["https://example.org", "https://someone.github.io/cocosl"])
def test_site_builds_and_links_resolve(tmp_path, url):
    out = _build(tmp_path, url)
    base = urlparse(url).path.rstrip("/")
    pages = list(out.rglob("*.html"))
    assert len(pages) > 30
    broken = []
    for page in pages:
        html = page.read_text()
        for ref in re.findall(r'(?:href|src)="([^"#]+)', html):
            if ref.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            assert ref.startswith(base + "/"), f"{page}: link {ref} misses base path {base!r}"
            target = out / ref[len(base) + 1:]
            if not (target.is_file() or (target / "index.html").is_file()):
                broken.append(f"{page.relative_to(out)} -> {ref}")
    assert not broken, broken


def test_seo_and_funnel_basics(tmp_path):
    out = _build(tmp_path, "https://example.org")
    home = (out / "index.html").read_text()
    assert 'rel="canonical" href="https://example.org/"' in home
    assert 'data-netlify="true"' in home  # default provider captures emails on Netlify
    art = (out / "blog" / "debt-avalanche-vs-snowball" / "index.html").read_text()
    assert '"@type": "Article"' in art and '"@type": "FAQPage"' in art
    sitemap = (out / "sitemap.xml").read_text()
    assert "/emails/" not in sitemap and "/free/thanks/" not in sitemap
    assert (out / "downloads" / "the-7-day-money-reset.pdf").stat().st_size > 50_000
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert [e["order"] for e in seq] == list(range(1, 11))
    assert all("https://example.org/" in e["html"] for e in seq)  # absolute links in emails


def test_email_provider_switch(tmp_path):
    out = _build(tmp_path, "https://example.org", EMAIL_PROVIDER="kit",
                 EMAIL_FORM_ACTION="https://app.kit.com/forms/123/subscriptions")
    home = (out / "index.html").read_text()
    assert 'action="https://app.kit.com/forms/123/subscriptions"' in home
    assert 'name="email_address"' in home and "data-netlify" not in home


def test_plausible_analytics(tmp_path):
    out = _build(tmp_path, "https://example.org", PLAUSIBLE_DOMAIN="mms.example")
    for page in out.rglob("index.html"):
        if 'http-equiv="refresh"' in page.read_text():
            continue  # redirect stubs
        assert 'data-domain="mms.example"' in page.read_text(), page
    assert "script.outbound-links.tagged-events.js" in (out / "index.html").read_text()
    prod = (out / "products" / "the-20-minute-budget" / "index.html").read_text()
    assert "plausible-event-name=Product+Click" in prod
    off = _build(tmp_path / "off", "https://example.org", PLAUSIBLE_DOMAIN="")
    assert "plausible.io" not in (off / "index.html").read_text()


def test_comparison_pages_affiliate_placeholders(tmp_path):
    out = _build(tmp_path, "https://example.org")
    pages = sorted(p.parent.name for p in (out / "compare").glob("*/index.html"))
    assert len(pages) == 8
    hysa = (out / "compare" / "best-high-yield-savings-accounts" / "index.html").read_text()
    assert "Checked as of" in hysa and "Disclosure:" in hysa
    # No affiliate URL configured yet: plain official link, no sponsored label, and the notice says so.
    assert 'href="https://www.sofi.com/" rel="noopener nofollow"' in hysa
    assert "earn anything from the companies" in hysa and 'rel="sponsored' not in hysa


def test_comparison_page_names_paying_programs(tmp_path):
    cfg = json.loads((SITE / "site.json").read_text())
    cfg["programs"]["sofi"]["affiliate_url"] = "https://aff.example/sofi"
    alt = tmp_path / "site"
    import shutil
    shutil.copytree(SITE, alt, ignore=shutil.ignore_patterns("public"))
    (alt / "site.json").write_text(json.dumps(cfg))
    out = tmp_path / "pub"
    env = {**os.environ, "SITE_OUT": str(out), "SITE_URL": "https://example.org"}
    env.pop("URL", None)
    subprocess.run([sys.executable, str(alt / "build.py")], check=True, env=env, capture_output=True)
    hysa = (out / "compare" / "best-high-yield-savings-accounts" / "index.html").read_text()
    assert 'href="https://aff.example/sofi" rel="sponsored noopener" class="plausible-event-name=Affiliate+Click"' in hysa
    assert "through links to: SoFi" in hysa


def test_hub_resources_quiz_and_rich_pins(tmp_path):
    out = _build(tmp_path, "https://example.org")
    sitemap = (out / "sitemap.xml").read_text()
    for p in ("/start/", "/resources/", "/quiz/", "/compare/"):
        assert f"https://example.org{p}" in sitemap
    assert "Sitemap: https://example.org/sitemap.xml" in (out / "robots.txt").read_text()
    res = (out / "resources" / "index.html").read_text()
    assert 'data-program="sofi"' in res and "no affiliation" in res
    quiz = (out / "quiz" / "index.html").read_text()
    assert quiz.count('class="q"') == 6 and "window.MMS_QUIZ" in quiz and 'value="quiz"' in quiz
    # Every article and comparison: Article + FAQ JSON-LD and article rich-pin tags.
    for page in list((out / "blog").glob("*/index.html")) + list((out / "compare").glob("*/index.html")):
        html = page.read_text()
        if 'property="og:type" content="article"' not in html:
            continue  # topic index pages
        assert '"@type": "Article"' in html and '"@type": "FAQPage"' in html, page
        assert 'property="article:published_time"' in html, page
    for page in out.rglob("index.html"):
        html = page.read_text()
        if 'http-equiv="refresh"' in html:
            continue  # redirect stubs
        assert 'property="og:image"' in html and 'name="pinterest-rich-pin"' in html, page
    prod = (out / "products" / "the-20-minute-budget" / "index.html").read_text()
    assert 'property="product:price:amount" content="12"' in prod


@pytest.mark.parametrize("url", ["https://example.org", "https://someone.github.io/cocosl"])
def test_deploy_check_passes(tmp_path, url):
    sys.path.insert(0, str(SITE / "tools"))
    import check_site
    out = _build(tmp_path, url)
    errors, _, report = check_site.check(out, urlparse(url).path.rstrip("/"))
    assert not errors, errors
    assert len(report) > 60


def test_deploy_check_catches_problems(tmp_path):
    sys.path.insert(0, str(SITE / "tools"))
    import check_site
    out = _build(tmp_path, "https://example.org")
    page = out / "about" / "index.html"
    page.write_text(page.read_text().replace("</main>", '<a href="/nope/">x</a><a href="#missing">y</a></main>'))
    (out / "img" / "huge.png").write_bytes(b"0" * 300_000)
    home = out / "index.html"
    home.write_text(home.read_text().replace("</main>", '<img src="/img/huge.png" alt=""></main>'))
    errors, _, _ = check_site.check(out, "")
    text = "\n".join(errors)
    assert "broken a -> /nope/" in text and "anchor #missing" in text and "huge.png" in text


def test_affiliate_articles_merged_without_duplicates(tmp_path):
    out = _build(tmp_path, "https://example.org")
    cfg = json.loads((SITE / "site.json").read_text())
    # Retired duplicate slugs redirect to the comparison page and never appear in the sitemap.
    sitemap = (out / "sitemap.xml").read_text()
    for old, new in cfg["blog_redirects"].items():
        assert f"/blog/{old}/" not in sitemap
        assert f"url={new}" in (out / "blog" / old / "index.html").read_text()
        assert f"/blog/{old}/ {new} 301" in (out / "_redirects").read_text()
    # Reviews link to their comparison page, and the comparison page links back.
    sofi = (out / "blog" / "sofi-review" / "index.html").read_text()
    assert "Compare your options" in sofi and "/compare/best-high-yield-savings-accounts/" in sofi
    assert 'href="/go/sofi/"' in sofi and (out / "go" / "sofi" / "index.html").is_file()
    hysa = (out / "compare" / "best-high-yield-savings-accounts" / "index.html").read_text()
    assert "/blog/sofi-review/" in hysa
    # No article links to a retired slug (links are rewritten to the comparison page).
    for page in (out / "blog").glob("*/index.html"):
        if page.parent.name in cfg["blog_redirects"]:
            continue
        for old in cfg["blog_redirects"]:
            assert f'href="/blog/{old}/"' not in page.read_text(), page


def test_newsletter_archive_hides_scheduled_issues(tmp_path):
    out = _build(tmp_path, "https://example.org", BUILD_DATE="2026-11-01")
    archive = (out / "newsletter" / "index.html").read_text()
    assert "No issues yet. The first one goes out on November 12, 2026." in archive
    assert not (out / "newsletter" / "holiday-spending-number").exists()
    assert "/newsletter/holiday-spending-number/" not in (out / "sitemap.xml").read_text()
    feed = (out / "newsletter" / "feed.xml").read_text()
    assert "<item>" not in feed
    # paste-ready email copies exist for every issue, with absolute links
    mail = (out / "emails" / "newsletter" / "raise-401k-one-percent" / "email.html").read_text()
    assert 'href="https://example.org/blog/401k-match-explained/"' in mail
    assert "/newsletter/" in (out / "index.html").read_text()  # footer link


def test_newsletter_archive_and_feed_after_send_date(tmp_path):
    import xml.etree.ElementTree as ET
    out = _build(tmp_path, "https://example.org/sub", BUILD_DATE="2026-11-20")
    archive = (out / "newsletter" / "index.html").read_text()
    assert "Pick your holiday number" in archive and "Raise your retirement contribution" in archive
    assert "Read your credit reports" not in archive  # Nov 26 issue not out yet
    issue = (out / "newsletter" / "raise-401k-one-percent" / "index.html").read_text()
    assert 'href="/sub/newsletter/holiday-spending-number/"' in issue  # pager to the older issue
    assert '"@type": "Article"' in issue and 'application/rss+xml' in issue
    root = ET.parse(out / "newsletter" / "feed.xml").getroot()
    items = root.findall("./channel/item")
    assert [i.findtext("link") for i in items] == [
        "https://example.org/sub/newsletter/raise-401k-one-percent/",
        "https://example.org/sub/newsletter/holiday-spending-number/"]
    enc = items[0].find("{http://purl.org/rss/1.0/modules/content/}encoded").text
    assert "401(k)" in enc
    assert "https://example.org/sub/newsletter/raise-401k-one-percent/" in (out / "sitemap.xml").read_text()
    r = subprocess.run([sys.executable, str(SITE / "tools" / "check_site.py"), "--dir", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_salary_and_city_pages(tmp_path):
    import json
    import re
    sys.path.insert(0, str(SITE))
    import pseo
    rules, cdata = pseo.load()
    # Federal maths matches the take-home pay calculator (lib/tax2026.js), checked against its takeHomePay().
    for salary, net in [(25000, 22197.5), (50000, 42355), (100000, 79180), (175000, 130878.5), (250000, 183182)]:
        assert round(pseo.take_home(rules, salary)["net"], 2) == net
    assert round(pseo.take_home(rules, 100000, pretax401k=5000)["net"], 2) == 75280
    # NYC city tax on $80k (taxable $72k) = $2,665.89; Texas has none; Philadelphia's wage tax is on wages.
    assert round(pseo.take_home(rules, 80000, "NY", "nyc")["local"], 2) == 2665.89
    assert pseo.take_home(rules, 80000, "TX")["state"] == 0
    assert round(pseo.take_home(rules, 60000, "PA", "philadelphia")["local"], 2) == round(60000 * 0.03735, 2)
    assert len(cdata["cities"]) == 25 and len(pseo.SALARIES) == 8

    out = _build(tmp_path, "https://example.org")
    sitemap = (out / "sitemap.xml").read_text()
    pages = [out / "budget" / f"{s}-salary" / "index.html" for s in pseo.SALARIES]
    pages += [out / "cost-of-living" / c["slug"] / "index.html" for c in cdata["cities"]]
    bodies = []
    for p in pages:
        h = p.read_text()
        assert "/calculators/take-home-pay/?salary=" in h, p
        assert '"@type": "FAQPage"' in h and 'id="common-questions"' in h
        assert p.parent.relative_to(out).as_posix() in sitemap
        main = re.sub(r"<[^>]+>", " ", h[h.index("<h1"):h.index('class="disclaimer"')])
        assert len(main.split()) > 600, f"{p} is thin"
        bodies.append(set(main.split()))
    # No two pages are near-duplicates: compare word sets pairwise within each family.
    for fam in (bodies[:8], bodies[8:]):
        for i in range(len(fam)):
            for j in range(i + 1, len(fam)):
                assert len(fam[i] & fam[j]) / len(fam[i] | fam[j]) < 0.9
    austin = (out / "cost-of-living" / "austin" / "index.html").read_text()
    assert "$1,530" in austin and "no state income tax" in austin
    sf = (out / "cost-of-living" / "san-francisco" / "index.html").read_text()
    assert "the highest of the 25 largest US cities" in sf
    # Each salary page has its own hand-written example; each city its own sourced local fact.
    for s in pseo.SALARIES:
        h = (out / "budget" / f"{s}-salary" / "index.html").read_text()
        assert 'id="example"' in h
        th = pseo.take_home(rules, s)["month"]
        ex = pseo.load_examples()[s]
        assert pseo.money(th) in ex, f"worked example for {s} doesn't match the take-home maths ({pseo.money(th)})"
    for c in cdata["cities"]:
        h = (out / "cost-of-living" / c["slug"] / "index.html").read_text()
        assert c["local_fact"]["source"].replace("&", "&amp;") in h and 'id="getting-around"' in h
    # Retired salary URLs redirect to the nearest band, with a real 301 on Netlify.
    rd = (out / "_redirects").read_text()
    for old, new in pseo.SALARY_REDIRECTS.items():
        assert f"/budget/{old}-salary/ /budget/{new}-salary/ 301!" in rd
        assert f"/budget/{old}-salary/" not in sitemap
    assert (out / "budget" / "index.html").exists() and (out / "cost-of-living" / "index.html").exists()


def test_shop_and_debt_pages(tmp_path):
    import json
    import re
    sys.path.insert(0, str(SITE))
    import pseo
    # The debt maths is a port of debtPayoff() in the calculators' lib/calc.js; values checked against it.
    d = pseo.debts_for(15000)
    assert [(x["balance"], x["minPayment"]) for x in d] == [(4500, 135), (3000, 90), (750, 25), (6750, 181)]
    a, s = pseo.payoff(d, 300, "avalanche"), pseo.payoff(d, 300, "snowball")
    assert (a["months"], round(a["interest"], 2)) == (25, 2931.49)
    assert (s["months"], round(s["interest"], 2)) == (25, 3005.23)
    assert pseo.payoff(d, pseo.extra_for_months(d, 36))["months"] <= 36

    out = _build(tmp_path, "https://example.org")
    shop = (out / "shop" / "index.html").read_text()
    items = json.loads((SITE / "content" / "shop.json").read_text())["items"]
    assert len(items) >= 50
    for it in items:
        assert f'plausible-event-product={it["slug"]}' in shop, it["slug"]
    assert shop.count("plausible-event-name=Product+Click") >= len(items)
    assert 'id="bundles"' in shop and "$62 separately, save $23" in shop
    assert "https://example.gumroad.com/l/bill-cut-kit" in shop  # placeholder until real links are pasted
    assert '"@type": "ItemList"' in shop
    assert 'href="/shop/"' in (out / "index.html").read_text()  # nav

    sitemap = (out / "sitemap.xml").read_text()
    h = (out / "debt-payoff" / "index.html").read_text()
    assert 'id="debt-calc"' in h and "/debt-calc.js" in h and '"@type": "FAQPage"' in h
    for t in pseo.EXAMPLES:
        assert f'id="example-{t}"' in h
    assert "$2,931" in h and "$3,005" in h  # the $15k example, same numbers as payoff()
    rd = (out / "_redirects").read_text()
    for t in pseo.DEBT_LEVELS:
        assert f"/debt-payoff/{t}-debt/ /debt-payoff/ 301!" in rd and f"/debt-payoff/{t}-debt/" not in sitemap
    # The in-page calculator (static/debt-calc.js) gives the same answer as pseo.payoff().
    js = (SITE / "static" / "debt-calc.js").read_text()
    assert "function payoff(" in js and "b.apr - a.apr" in js


def test_scheduled_articles_stay_hidden_until_their_date(tmp_path):
    out = _build(tmp_path, "https://example.org", BUILD_DATE="2026-11-07", BLOG_SHOW_SCHEDULED="0")
    assert (out / "blog" / "debt-avalanche-vs-snowball" / "index.html").exists()
    assert not (out / "blog" / "ynab-review" / "index.html").exists()  # dated 2026-11-13
    sitemap = (out / "sitemap.xml").read_text()
    assert "/blog/ynab-review/" not in sitemap
    # Links to a scheduled article render as plain text, so nothing 404s in between.
    for page in out.rglob("*.html"):
        assert 'href="/blog/ynab-review/"' not in page.read_text(), page
    later = _build(tmp_path / "later", "https://example.org", BUILD_DATE="2026-12-31", BLOG_SHOW_SCHEDULED="0")
    assert (later / "blog" / "ynab-review" / "index.html").exists()
    dates = [build_meta_date(f) for f in (SITE / "content" / "blog").glob("*.md")]
    assert len(set(dates)) >= 15  # not all on one day


def build_meta_date(f):
    import re as _re
    return _re.search(r"^date: (.+)$", f.read_text(), _re.M).group(1)


def test_editor_byline_and_overviews(tmp_path):
    out = _build(tmp_path, "https://example.org")
    art = (out / "blog" / "ynab-review" / "index.html").read_text()
    assert 'href="/about/editor/"' in art and (out / "about" / "editor" / "index.html").exists()
    for f in (SITE / "content" / "blog").glob("*-review.md"):
        title = re.search(r"^title: (.+)$", f.read_text(), re.M).group(1)
        assert "review" not in title.lower(), f"{f.name}: untested products are overviews, not reviews"


def test_email_capture_ab_test(tmp_path):
    import json
    out = _build(tmp_path, "https://example.org")
    cfg = json.loads((SITE / "site.json").read_text())["ab_test"]
    home = (out / "index.html").read_text()
    assert "mms_ab=" in home and "max-age=7776000" in home and "window.mmsAB" in home
    assert f'<span class="ab-hero-a">{cfg["hero"]["a"]["headline"]}' in home
    assert f'<span class="ab-hero-b">{cfg["hero"]["b"]["headline"]}' in home
    assert '<span class="ab-magnet-b">' in home
    assert '<span class="ab-magnet-b">' in (out / "free" / "index.html").read_text()
    js = (out / "site.js").read_text()
    assert '"AB Exposure"' in js and "abProps(" in js and "p.variant" in js
    assert "mms_ab" in (out / "privacy" / "index.html").read_text()
    # Switched off: one plain version, no cookie script.
    import shutil
    site2 = tmp_path / "site2" / "site"
    shutil.copytree(SITE, site2, ignore=shutil.ignore_patterns("public"))
    c = json.loads((site2 / "site.json").read_text())
    c["ab_test"]["active"] = False
    (site2 / "site.json").write_text(json.dumps(c))
    out2 = tmp_path / "out2"
    e = {**os.environ, "SITE_OUT": str(out2), "SITE_URL": "https://example.org"}
    e.pop("URL", None)
    subprocess.run([sys.executable, str(site2 / "build.py")], check=True, env=e, capture_output=True)
    h2 = (out2 / "index.html").read_text()
    assert "mms_ab=" not in h2 and "ab-hero-b" not in h2 and cfg["hero"]["a"]["headline"] in h2


def _contrast(a: str, b: str) -> float:
    def lum(h):
        h = h.lstrip("#")
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_colour_tokens_meet_wcag_aa():
    import re
    css = (SITE / "static" / "style.css").read_text()
    tok = dict(re.findall(r"--([\w-]+):(#[0-9a-fA-F]{6})", css.split("}", 1)[0]))
    text_pairs = [  # (text, background) combinations the stylesheet uses for body-size text
        ("ink", "paper"), ("ink", "card"), ("ink", "tint"), ("ink", "gold-t"), ("ink", "gold"),
        ("muted", "paper"), ("muted", "card"), ("muted", "tint"),
        ("green-d", "paper"), ("green-d", "card"), ("green-d", "tint"),
        ("paper", "ink"), ("paper", "ink2"), ("gold", "ink"), ("gold", "ink2"), ("paper", "green-d")]
    for fg, bg in text_pairs:
        assert _contrast(tok[fg], tok[bg]) >= 4.5, f"{fg} on {bg}: {_contrast(tok[fg], tok[bg]):.2f}"
    assert _contrast("#c9cdc4", tok["ink"]) >= 4.5  # footer text
    # Focus rings and borders of controls are non-text UI: 3:1 against what's next to them.
    assert _contrast(tok["green-d"], tok["paper"]) >= 3 and _contrast(tok["gold"], tok["ink"]) >= 3
    assert ":focus-visible" in css and "outline:none" not in css


def test_deploy_check_catches_accessibility_problems(tmp_path):
    import shutil
    out = _build(tmp_path, "https://example.org")
    page = out / "about" / "index.html"
    h = page.read_text()
    h = h.replace('<html lang="en">', "<html>", 1)
    h = h.replace("</main>", '<img src="/img/logo.png"><a href="/blog/"></a><button></button>'
                  '<input type="email" name="x2"><span id="dup"></span><span id="dup"></span></main>', 1)
    page.write_text(h)
    r = subprocess.run([sys.executable, str(SITE / "tools" / "check_site.py"), "--dir", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 1
    for msg in ("no lang attribute", "image(s) without alt", "form field", "<a> with no text",
                "<button> with no text", "id 'dup' used 2 times"):
        assert msg in r.stdout, msg


STOP = set("a an and the to of for on in is it my i do does how what should can i'm your you or with when if much many by be at from".split())


def _words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower().replace("401(k)", "401k")) if w not in STOP}


def test_ask_page_answers_30_new_questions_with_schema(tmp_path):
    out = _build(tmp_path, "https://example.org")
    page = (out / "ask" / "index.html").read_text()
    ld = [json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page)]
    faq = next(x for x in ld if x["@type"] == "FAQPage")["mainEntity"]
    assert len(faq) == 30
    visible = re.findall(r'<div class="ask-q" id="[^"]+"><h3>(.*?)</h3>', page)
    assert [html_unescape(q) for q in visible] == [q["name"] for q in faq]
    assert all(len(q["acceptedAnswer"]["text"]) > 150 and "{" not in q["acceptedAnswer"]["text"] for q in faq)
    # every answer links a tool, and every shop link points at a real card
    assert page.count('class="ask-tools"') == 30
    for slug in re.findall(r'href="/shop/#item-([a-z0-9-]+)"', page):
        assert f'id="item-{slug}"' in (out / "shop" / "index.html").read_text(), slug
    assert "/ask/" in (out / "sitemap.xml").read_text()
    assert 'href="/ask/"' in (out / "index.html").read_text()
    # No overlap with what the site already answers: article/compare/newsletter titles and their FAQ questions.
    sys.path.insert(0, str(SITE))
    import build
    existing = []
    for d in ("blog", "compare", "newsletter", "pages"):
        for f in (SITE / "content" / d).glob("*.md"):
            meta, body = build.parse_front_matter(f.read_text())
            existing.append(meta.get("title", ""))
            existing += [q for q, _ in build.extract_faq(body)]
    for q in faq:
        qa = _words(q["name"])
        for e in existing:
            eb = _words(e)
            sim = len(qa & eb) / len(qa | eb) if qa | eb else 0
            assert sim < 0.5, f"Ask question overlaps existing content: {q['name']!r} ~ {e!r}"


def html_unescape(s):
    import html
    return html.unescape(s)


def test_pin_specs_match_pages():
    sys.path.insert(0, str(SITE / "tools"))
    import make_pins
    pins = make_pins.pins()
    assert len(pins) == 10
    for p in pins:
        assert "utm_campaign=pin-" + p["slug"] in p["link"] and p["title"] and p["alt"] and p["board"]
        assert (SITE / "content").exists() and len(p["desc"]) <= 500 and len(p["title"]) <= 100
    assert "$3,530" in pins[6]["html"]  # $50k take-home, same maths as /budget/50000-salary/
