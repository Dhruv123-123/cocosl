"""Dinero Simple website (sites/dinero-simple/build.py)."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest

DS = Path(__file__).resolve().parents[1] / "sites" / "dinero-simple"


def _build(tmp_path, url, **env):
    out = tmp_path / "public"
    e = {**os.environ, "SITE_OUT": str(out), "SITE_URL": url, **env}
    e.pop("URL", None)
    subprocess.run([sys.executable, str(DS / "build.py")], check=True, env=e, capture_output=True)
    return out


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
    assert "REPLACE_ME" not in html and "apps.example.org" not in html and "scam-checker" not in html
    # a tool that is a page of the site itself (base "site") is always live
    assert 'href="/calculadora-de-envios/"' in (out / "links" / "index.html").read_text()

    site = tmp_path / "ds"
    shutil.copytree(DS, site, ignore=shutil.ignore_patterns("public"))
    cfg = json.loads((site / "site.json").read_text())
    cfg["tool_urls"] = {"calculators": "https://apps.example.org/money-calculators/es",
                        "scam_checker": "https://apps.example.org/scam-checker/es",
                        "apps_es": "https://apps.example.org/es"}
    (site / "site.json").write_text(json.dumps(cfg, ensure_ascii=False))
    out = _build(tmp_path / "b", "https://example.org", SITE_ROOT=str(site))
    links = (out / "links" / "index.html").read_text()
    assert "Herramientas gratis" in links and 'href="https://apps.example.org/scam-checker/es/"' in links
    assert 'href="https://apps.example.org/es/"' in links  # the apps site's Spanish hub
    art = (out / "blog" / "avalancha-o-bola-de-nieve" / "index.html").read_text()
    assert 'href="https://apps.example.org/money-calculators/es/debt-payoff/"' in art
    assert (out / "products" / "el-paquete-dinero-simple" / "index.html").is_file()


def test_plausible_events_and_email_utm(tmp_path):
    out = _build(tmp_path, "https://example.org", SITE_ROOT=str(DS))
    pages = [p for p in out.rglob("*.html") if p.name != "email.html" and "go" not in p.relative_to(out).parts]
    snippet = 'data-domain="dinerosimple.netlify.app" src="https://plausible.io/js/script.outbound-links.tagged-events.js"'
    assert pages and all(snippet in p.read_text() for p in pages)
    buy = (out / "products" / "tu-fecha-sin-deudas" / "index.html").read_text()
    assert "plausible-event-name=Product+Click" in buy and "plausible-event-link=tu-fecha-sin-deudas" in buy
    mail = (out / "emails" / "avalancha-bola-de-nieve" / "email.txt").read_text()
    assert "/products/el-presupuesto-de-20-minutos/?utm_source=newsletter&utm_medium=email&utm_campaign=welcome-d" in mail
    assert ".pdf?utm" not in " ".join(p.read_text() for p in (out / "emails").rglob("email.*"))


def test_dinero_youtube_descriptions_carry_utm_links():
    items = json.loads((DS.parents[1] / "launch" / "dinero-simple" / "content-month-1.json").read_text())
    longs = [i for i in items if i["format"] == "long"]
    assert longs and all(f"utm_source=youtube&utm_medium=social&utm_campaign={i['key']}" in i["script"]["description"]
                         for i in longs)
    assert all("utm_" not in i["script"]["description"] for i in items if i["format"] != "long")


def test_go_links_redirect_home_until_the_affiliate_url_is_set(tmp_path):
    out = _build(tmp_path, "https://example.org", SITE_ROOT=str(DS))
    redirects = (out / "_redirects").read_text()
    assert "/go/remitly/ https://www.remitly.com/ 302!" in redirects and "REPLACE_ME" not in redirects
    assert "Disallow: /go/" in (out / "robots.txt").read_text()
    art = (out / "blog" / "remitly-wise-o-xoom" / "index.html").read_text()
    assert 'href="/go/wise/" rel="sponsored noopener"' in art and "Divulgación" in art
    # ITIN partner boxes stay hidden until a real, checked partner is configured
    assert 'class="partner"' not in (out / "blog" / "cuenta-y-tarjeta-con-itin" / "index.html").read_text()
    assert not (out / "go" / "cuenta-itin").exists()

    site = tmp_path / "ds"
    shutil.copytree(DS, site, ignore=shutil.ignore_patterns("public"))
    cfg = json.loads((site / "site.json").read_text())
    cfg["go_links"]["tarjeta-itin"] = {"name": "Tarjeta X", "home": "", "url": "https://aff.example/x",
                                       "card": {"text": "Acepta ITIN.", "button": "Ver tarjeta"}}
    (site / "site.json").write_text(json.dumps(cfg, ensure_ascii=False))
    out = _build(tmp_path / "b", "https://example.org", SITE_ROOT=str(site))
    art = (out / "blog" / "cuenta-y-tarjeta-con-itin" / "index.html").read_text()
    assert 'class="partner"' in art and 'href="/go/tarjeta-itin/"' in art
    assert "/go/tarjeta-itin/ https://aff.example/x 302!" in (out / "_redirects").read_text()


def test_hold_keeps_unreviewed_pages_off_without_breaking_links(tmp_path):
    site = tmp_path / "ds"
    shutil.copytree(DS, site, ignore=shutil.ignore_patterns("public"))
    cfg = json.loads((site / "site.json").read_text())
    assert cfg["hold"]["enabled"] is False  # off until Dhruv chooses the lean launch
    cfg["hold"]["enabled"] = True
    (site / "site.json").write_text(json.dumps(cfg, ensure_ascii=False))
    out = _build(tmp_path / "b", "https://example.org", SITE_ROOT=str(site))
    assert (out / "products" / "el-presupuesto-de-20-minutos" / "index.html").is_file()
    for slug in cfg["hold"]["products"]:
        assert not (out / "products" / slug).exists()
    assert not any((out / "blog" / f.stem).exists() for f in (DS / "content" / "blog").glob("*.md"))
    assert "Muy pronto" in (out / "blog" / "index.html").read_text()
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert [e["order"] for e in seq] == [1, 2, 3]
    broken = []
    for page in out.rglob("*.html"):
        for ref in re.findall(r'(?:href|src)="([^"#]+)', page.read_text()):
            if ref.startswith("https://example.org/"):
                ref = ref[len("https://example.org"):]
            if ref.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            target = out / ref.lstrip("/")
            if not (target.is_file() or (target / "index.html").is_file()):
                broken.append(f"{page.relative_to(out)} -> {ref}")
    assert not broken, broken
    for e in seq:
        for ref in re.findall(r'href="https://example\.org(/[^"#?]*)', e["html"]):
            assert (out / ref.lstrip("/")).is_file() or (out / ref.lstrip("/") / "index.html").is_file(), ref
