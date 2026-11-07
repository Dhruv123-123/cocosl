"""The static website in site/ builds, and every internal link and asset resolves."""
import json
import os
import re
import shutil
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


# ---- second brand / second language: sites/dinero-simple reuses build.py via SITE_ROOT
DS = Path(__file__).resolve().parents[1] / "sites" / "dinero-simple"


@pytest.mark.parametrize("url", ["https://example.org", "https://someone.github.io/dinero"])
def test_spanish_site_builds_and_links_resolve(tmp_path, url):
    out = _build(tmp_path, url, SITE_ROOT=str(DS))
    base = urlparse(url).path.rstrip("/")
    broken = []
    for page in out.rglob("*.html"):
        for ref in re.findall(r'(?:href|src)="([^"#]+)', page.read_text()):
            if ref.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            target = out / ref[len(base) + 1:]
            if not (target.is_file() or (target / "index.html").is_file()):
                broken.append(f"{page.relative_to(out)} -> {ref}")
    assert not broken, broken
    assert (out / "style.css").is_file() and (out / "downloads" / "tu-dinero-en-orden-en-7-dias.pdf").is_file()
    assert not (out / "downloads" / "the-7-day-money-reset.pdf").exists()  # no English assets leak in


def test_spanish_site_is_in_spanish(tmp_path):
    out = _build(tmp_path, "https://example.org", SITE_ROOT=str(DS))
    home = (out / "index.html").read_text()
    assert '<html lang="es-US">' in home and "Mándame la guía gratis" in home
    assert "--ink:#14213d" in home  # brand colours from site.json
    art = (out / "blog" / "avalancha-o-bola-de-nieve" / "index.html").read_text()
    assert '"@type": "FAQPage"' in art  # "Preguntas frecuentes" heading is recognised
    assert "de noviembre de 2026" in art and "min de lectura" in art
    text = " ".join(re.sub(r"<[^>]+>", " ", p.read_text()) for p in out.rglob("*.html") if "emails" not in p.parts)
    for english in ("Read next", "Free reset", "Money Made Simple", "Get instant access", "On this page"):
        assert english not in text, english
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert len(seq) == 10 and all("Dinero Simple" in e["text"] for e in seq)


def test_free_tools_hidden_until_their_url_is_set(tmp_path):
    out = _build(tmp_path, "https://example.org", SITE_ROOT=str(DS))
    html = " ".join(p.read_text() for p in out.rglob("*.html"))
    assert "REPLACE_ME" not in html and 'class="free-tool' not in html

    site = tmp_path / "ds"
    shutil.copytree(DS, site, ignore=shutil.ignore_patterns("public"))
    cfg = json.loads((site / "site.json").read_text())
    cfg["tool_urls"] = {"calculators": "https://apps.example.org/money-calculators/es",
                        "scam_checker": "https://apps.example.org/scam-checker/es"}
    (site / "site.json").write_text(json.dumps(cfg, ensure_ascii=False))
    out = _build(tmp_path / "b", "https://example.org", SITE_ROOT=str(site))
    links = (out / "links" / "index.html").read_text()
    assert "Herramientas gratis" in links and 'href="https://apps.example.org/scam-checker/es/"' in links
    art = (out / "blog" / "avalancha-o-bola-de-nieve" / "index.html").read_text()
    assert 'href="https://apps.example.org/money-calculators/es/debt-payoff/"' in art
    assert (out / "products" / "el-paquete-dinero-simple" / "index.html").is_file()


def test_plausible_events_and_email_utm(tmp_path):
    out = _build(tmp_path, "https://example.org", SITE_ROOT=str(DS))
    pages = [p for p in out.rglob("*.html") if p.name != "email.html"]
    snippet = 'data-domain="dinerosimple.netlify.app" src="https://plausible.io/js/script.outbound-links.tagged-events.js"'
    assert pages and all(snippet in p.read_text() for p in pages)
    buy = (out / "products" / "tu-fecha-sin-deudas" / "index.html").read_text()
    assert "plausible-event-name=Product+Click" in buy and "plausible-event-link=tu-fecha-sin-deudas" in buy
    mail = (out / "emails" / "avalancha-bola-de-nieve" / "email.txt").read_text()
    assert "/products/el-presupuesto-de-20-minutos/?utm_source=newsletter&utm_medium=email&utm_campaign=welcome-d" in mail
    assert ".pdf?utm" not in " ".join(p.read_text() for p in (out / "emails").rglob("email.*"))
    # The English site has no Plausible domain set, so no script and no event classes.
    en = _build(tmp_path / "en", "https://example.org")
    home = (en / "index.html").read_text()
    assert "plausible" not in home.lower() and "utm_" not in (en / "emails" / "sequence.json").read_text()


def test_dinero_youtube_descriptions_carry_utm_links():
    items = json.loads((DS.parents[1] / "launch" / "dinero-simple" / "content-month-1.json").read_text())
    longs = [i for i in items if i["format"] == "long"]
    assert longs and all(f"utm_source=youtube&utm_medium=social&utm_campaign={i['key']}" in i["script"]["description"]
                         for i in longs)
    assert all("utm_" not in i["script"]["description"] for i in items if i["format"] != "long")
