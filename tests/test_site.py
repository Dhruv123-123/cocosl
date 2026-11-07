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
        assert 'data-domain="mms.example"' in page.read_text(), page
    assert "script.outbound-links.tagged-events.js" in (out / "index.html").read_text()
    prod = (out / "products" / "the-20-minute-budget" / "index.html").read_text()
    assert "plausible-event-name=Product+Click" in prod
    off = _build(tmp_path / "off", "https://example.org", PLAUSIBLE_DOMAIN="")
    assert "plausible.io" not in (off / "index.html").read_text()
