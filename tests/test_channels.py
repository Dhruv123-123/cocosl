import json
from pathlib import Path

import pytest

from contentfactory import channels

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "launch" / "money-made-simple" / "channels" / "config.json"


def test_channels_export(factory, tmp_path):
    res = channels.export(factory, "money-made-simple", CONFIG, tmp_path, render=False)
    assert res["pins"] == 60 and res["issues"] == 12 and res["threads"] >= 90
    assert res["block"] == 0 and res["warn"] == 0

    pins = json.loads((tmp_path / "pinterest" / "pins.json").read_text())
    assert len({p["title"] for p in pins}) == 60
    assert len({p["publish_at"] for p in pins}) == 60
    for p in pins:
        assert len(p["title"]) <= 100 and len(p["description"]) <= 500
        assert "AI tools" in p["description"]
        assert p["link"].startswith("https://")
        if p["target"].startswith("article:"):
            assert "/blog/" in p["link"] and "utm_source=pinterest" in p["link"]
    carousel_pins = [p for p in pins if p["source"] != "hand-written"]
    assert not any(channels.YEAR.search(p["title"] + p["description"]) for p in carousel_pins)
    assert sum(p["target"] == "free" for p in carousel_pins) <= 10
    targets = {p["target"] for p in pins}
    assert sum(t.startswith("article:") for t in targets) == 13  # every article gets traffic

    threads = json.loads((tmp_path / "threads" / "threads.json").read_text())
    for t in threads:
        assert all(channels.x_len(p) <= 280 for p in t["x"])
        assert all(len(p) <= 500 for p in t["threads"])
        assert "AI tools" in t["x"][-1] and "AI tools" in t["threads"][-1]
        assert len(t["threads"]) <= len(t["x"])

    issues = json.loads((tmp_path / "newsletter" / "issues.json").read_text())
    assert [i["date"] for i in issues][:2] == ["2026-11-22", "2026-11-29"]
    for i in issues:
        assert "{{unsubscribe_url}}" in i["text"] and "{{business_address}}" in i["text"]
        assert "utm_medium=email" in i["read_url"]
        assert len(i["subject"]) <= 60
    html = next((tmp_path / "newsletter").glob("01-*.html")).read_text()
    assert "Issue 1" in html and "{{unsubscribe_url}}" in html


def test_weak_match_falls_back_to_lead_magnet():
    links = channels.Links("https://x.test", {"a": {"title": "A", "keywords": ["budget"]}}, {})
    item = {"script": {"title": "Date ideas", "caption": "one budget", "segments": [{"narration": "cheap"}]}}
    assert links.match(item)[0] == "free"
    item["script"]["title"] = "A budget for dates"
    assert links.match(item)[0] == "article:a"


def test_split_keeps_sentences_under_limit():
    text = "One short sentence. " * 30
    parts = channels._split(text.strip(), 100)
    assert all(len(p) <= 100 for p in parts) and " ".join(parts) == text.strip()


@pytest.mark.parametrize("brand", ["scam-decoded", "1099-money"])
def test_other_brand_configs(factory, tmp_path, brand):
    """Runs once those brands' packs and brand files are on the branch (they live in their own PRs)."""
    cfg_path = ROOT / "launch" / brand / "channels" / "config.json"
    cfg = channels.load_config(cfg_path)
    if not all(p.exists() for p, _ in cfg["_sources"]) or brand not in factory.brands():
        pytest.skip(f"{brand} packs not merged yet")
    res = channels.export(factory, brand, cfg_path, tmp_path, render=False)
    assert res["pins"] == 60 and res["issues"] == 12 and res["block"] == 0 and res["warn"] == 0


def test_store_links_tagged():
    from contentfactory.channels import tag_url
    site = "https://moneymadesimple.netlify.app"
    g = tag_url("https://me.gumroad.com/l/budget", "pinterest", "social", "pin-budget-1", site)
    assert g == "https://me.gumroad.com/l/budget?utm_source=pinterest&utm_medium=social&utm_campaign=pin-budget-1"
    s = tag_url("https://buy.stripe.com/abc?prefilled_email=x#top", "newsletter", "email", "newsletter-03", site)
    assert s == ("https://buy.stripe.com/abc?prefilled_email=x&utm_source=newsletter&utm_medium=email"
                 "&utm_campaign=newsletter-03&client_reference_id=newsletter__email__newsletter-03#top")
    assert tag_url(site + "/blog/x/", "x", "social", "t", site).endswith("?utm_source=x&utm_medium=social&utm_campaign=t")
    aff = "https://sofi.sjv.io/abc123"
    assert tag_url(aff, "pinterest", "social", "p", site) == aff  # affiliate links stay untouched
    tagged = g
    assert tag_url(tagged, "x", "social", "other", site) == tagged  # never override existing UTM


def test_export_has_no_untagged_links(factory, tmp_path):
    import re
    from contentfactory.channels import is_store_link
    out = tmp_path / "out"
    channels.export(factory, "money-made-simple", CONFIG, out, render=False)
    untagged = []
    for f in out.rglob("*"):
        if f.suffix in {".csv", ".txt", ".html", ".md", ".json"}:
            for url in re.findall(r"https?://[^\s\"'<>(),\]\\]+", f.read_text()):
                if (is_store_link(url) or "moneymadesimple.netlify.app" in url) and "utm_source=" not in url:
                    untagged.append(f"{f.name}: {url}")
    assert not untagged, untagged[:5]
