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
    e = {**os.environ, "SITE_OUT": str(out), "SITE_URL": url, **env}
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
