import json
import re
from datetime import date
from pathlib import Path

from contentfactory.pack import plan

ROOT = Path(__file__).resolve().parents[1]
LAUNCH = ROOT / "launch" / "1099-money"
SPEC = {"short": "mon,tue,wed,thu,fri,sat,sun", "carousel": "mon,wed,fri,sat", "long": "sun"}


def _items(name="content.json"):
    return json.loads((LAUNCH / name).read_text())


MONTH1 = "month-1/content.json"


def test_brand_loads_with_placeholder_affiliates(factory):
    brand = factory.brand("1099-money")
    assert brand.name == "1099 Money"
    assert "not tax" in brand.ai_disclosure
    assert {a.slug for a in brand.affiliates} >= {"freshbooks", "quickbooks", "gusto", "novo", "taxact", "lively"}
    assert all(a.url.startswith("https://example.com/go/") for a in brand.affiliates)  # replace when approved


import pytest


@pytest.mark.parametrize("name,counts", [("content.json", [14, 8, 2]), (MONTH1, [22, 13, 4])])
def test_content_is_valid(factory, name, counts):
    from contentfactory.schemas import Script
    brand = factory.brand("1099-money")
    items = _items(name)
    assert [sum(i["format"] == f for i in items) for f in ("short", "carousel", "long")] == counts
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


def test_month_1_has_no_repeat_titles_and_fills_30_days(factory):
    launch = {i["script"]["title"].lower() for i in _items()}
    month = _items(MONTH1)
    assert not launch & {i["script"]["title"].lower() for i in month}
    slots, leftover = plan(factory.brand("1099-money"), month, date(2026, 11, 30), 30)
    assert not leftover
    assert {s.day for s in slots} == set(range(1, 31))


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
    load_workbook = pytest.importorskip("openpyxl").load_workbook
    spec = importlib.util.spec_from_file_location("build_tracker", LAUNCH / "product" / "build_tracker.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.build(tmp_path / "t.xlsx")
    wb = load_workbook(out)
    assert {"Start Here", "Setup", "Quarterly", "Income", "Expenses", "Mileage", "Deadlines", "Tax Tables"} <= set(wb.sheetnames)
    q = wb["Quarterly"]
    assert any(str(c.value).startswith("=MAX(0,") for row in q.iter_rows() for c in row if c.value)


def test_funnel_emails_and_lead_magnet():
    app = ROOT / "apps" / "freelance-tax"
    emails = sorted((app / "emails").glob("[0-9][0-9]-*.md"))
    assert len(emails) == 7
    days = []
    for i, path in enumerate(emails, 1):
        text = path.read_text()
        head = text.split("---")[1]
        meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
        assert set(meta) == {"order", "day", "subject", "preheader", "goal"}
        assert int(meta["order"]) == i
        days.append(int(meta["day"]))
        assert "not tax, legal or financial advice" in text
        assert not re.search(r"guarantee|risk-free|last chance|expires", text, re.I)
    assert days == sorted(days) and days[0] == 0
    assert (app / "downloads" / "freelancer-tax-calendar-2027.pdf").stat().st_size > 10_000
    assert "tax-calendar" in (app / "free" / "index.html").read_text()
