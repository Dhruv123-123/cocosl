import json
from datetime import date
from pathlib import Path

from contentfactory.pack import plan

ROOT = Path(__file__).resolve().parents[1]
LAUNCH = ROOT / "launch" / "1099-money"
SPEC = {"short": "mon,tue,wed,thu,fri,sat,sun", "carousel": "mon,wed,fri,sat", "long": "sun"}


def _items():
    return json.loads((LAUNCH / "content.json").read_text())


def test_brand_loads_with_placeholder_affiliates(factory):
    brand = factory.brand("1099-money")
    assert brand.name == "1099 Money"
    assert "not tax" in brand.ai_disclosure
    assert {a.slug for a in brand.affiliates} >= {"freshbooks", "quickbooks", "gusto", "novo", "taxact", "lively"}
    assert all(a.url.startswith("https://example.com/go/") for a in brand.affiliates)  # replace when approved


def test_launch_content_is_valid(factory):
    from contentfactory.schemas import Script
    brand = factory.brand("1099-money")
    items = _items()
    assert [sum(i["format"] == f for i in items) for f in ("short", "carousel", "long")] == [14, 8, 2]
    assert len({i["script"]["title"] for i in items}) == len(items)
    for it in items:
        sc = Script.model_validate(it["script"])
        assert it["pillar"] in brand.pillars
        assert sc.claims_to_verify and sc.sources
        text = " ".join(s.narration for s in sc.segments).lower()
        assert not any(b.lower() in text for b in brand.voice.banned_phrases)
        assert all(len(s.on_screen_text.split()) < 12 for s in sc.segments)
        if "affiliate" in sc.caption.lower():
            assert "commission" in sc.caption
        if it["format"] == "short":
            words = sum(len(s.narration.split()) for s in sc.segments)
            assert words <= 160, (sc.title, words)  # under ~60s at 160 wpm


def test_two_week_plan_fits_and_respects_cap(factory):
    brand = factory.brand("1099-money")
    items = _items()
    slots, leftover = plan(brand, items, date(2026, 11, 16), 14, SPEC)
    assert not leftover and len(slots) == len(items)
    per = {}
    for s in slots:
        for p in s.platforms:
            per[(s.day, p)] = per.get((s.day, p), 0) + 1
    assert max(per.values()) <= brand.cadence.max_posts_per_day_per_platform


def test_tracker_builds(tmp_path):
    import importlib.util
    import pytest
    load_workbook = pytest.importorskip("openpyxl").load_workbook
    spec = importlib.util.spec_from_file_location("build_tracker", LAUNCH / "product" / "build_tracker.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.build(tmp_path / "t.xlsx")
    wb = load_workbook(out)
    assert {"Start Here", "Setup", "Quarterly", "Income", "Expenses", "Mileage", "Deadlines", "Tax Tables"} <= set(wb.sheetnames)
    q = wb["Quarterly"]
    assert any(str(c.value).startswith("=MAX(0,") for row in q.iter_rows() for c in row if c.value)
