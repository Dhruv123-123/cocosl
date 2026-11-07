import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "sites" / "scam-decoded"


def build(tmp_path, monkeypatch, **env):
    monkeypatch.setenv("SITE_OUT", str(tmp_path / "public"))
    for k in ("SITE_URL", "URL", "EMAIL_PROVIDER", "EMAIL_FORM_ACTION", "SCAM_CHECKER_URL"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    spec = importlib.util.spec_from_file_location("scam_site_build", ROOT / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build()
    return mod, tmp_path / "public"


def test_pages_and_internal_links_resolve(tmp_path, monkeypatch):
    mod, out = build(tmp_path, monkeypatch)
    for page in ["index.html", "free/index.html", "free/thanks/index.html", "kit/index.html", "checker/index.html",
                 "privacy/index.html", "disclosures/index.html", "404.html", "sitemap.xml", "robots.txt",
                 "downloads/the-scam-proof-checklist.pdf"]:
        assert (out / page).exists(), page
    for html in out.rglob("*.html"):
        text = html.read_text()
        assert "{{" not in text, html
        for href in re.findall(r'(?:href|src)="(/[^"#]*)"', text):
            target = out / href.lstrip("/")
            assert target.exists() or (target / "index.html").exists(), f"{html}: {href}"
    # placeholder checker link is hidden and reported
    assert "REPLACE_ME" not in (out / "index.html").read_text()
    assert any("scam_checker" in w for w in mod.WARNINGS)


def test_seven_email_sequence_sells_the_kit(tmp_path, monkeypatch):
    _, out = build(tmp_path, monkeypatch)
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert [e["order"] for e in seq] == list(range(1, 8))
    assert [e["send_on_day"] for e in seq] == sorted(e["send_on_day"] for e in seq)
    assert all(e["subject"] and e["text"] and e["html"] for e in seq)
    assert sum("/kit/" in e["html"] for e in seq) >= 3
    assert "the-scam-proof-checklist.pdf" in seq[0]["html"]
    for e in seq:
        assert "{{" not in e["html"] and "{{" not in e["text"]
        assert not re.search(r'href="/', e["html"]), "email links must be absolute"
        assert not re.search(r"\bguarantee", e["text"], re.I)
    assert "noindex" in (out / "emails" / "index.html").read_text()


def test_provider_switch_and_checker_url(tmp_path, monkeypatch):
    _, out = build(tmp_path, monkeypatch, EMAIL_PROVIDER="kit", EMAIL_FORM_ACTION="https://app.kit.com/forms/1/subscriptions",
                   SCAM_CHECKER_URL="https://checker.example.org/", SITE_URL="https://example.org/scam")
    home = (out / "index.html").read_text()
    assert 'action="https://app.kit.com/forms/1/subscriptions"' in home
    assert 'name="email_address"' in home and "data-netlify" not in home
    assert 'href="https://checker.example.org/"' in home
    assert 'href="/scam/kit/"' in home
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert "https://checker.example.org/" in "".join(e["html"] for e in seq)


def test_product_ladder_pages_and_upsells(tmp_path, monkeypatch):
    mod, out = build(tmp_path, monkeypatch)
    parents = (out / "parents" / "index.html").read_text()
    teams = (out / "teams" / "index.html").read_text()
    assert "$29" in parents and "KITPARENTS" in parents
    assert "$99" in teams and "One organization" in teams
    assert 'href="/parents/"' in (out / "kit" / "index.html").read_text()
    assert any("parents buy_url" in w for w in mod.WARNINGS)
    seq = json.loads((out / "emails" / "sequence.json").read_text())
    assert "/parents/" in seq[-1]["html"] and "/teams/" in seq[-1]["html"]
    sitemap = (out / "sitemap.xml").read_text()
    assert "/parents/" in sitemap and "/teams/" in sitemap
