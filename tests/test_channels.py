import json
from pathlib import Path

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
