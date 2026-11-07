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
MONTH2 = "month-2/content.json"
MONTH3 = "month-3/content.json"
MONTH4 = "month-4/content.json"


def test_brand_loads_with_placeholder_affiliates(factory):
    brand = factory.brand("1099-money")
    assert brand.name == "1099 Money"
    assert "not tax" in brand.ai_disclosure
    assert {a.slug for a in brand.affiliates} >= {"freshbooks", "quickbooks", "gusto", "novo", "taxact", "lively"}
    assert all(a.url.startswith("https://example.com/go/") for a in brand.affiliates)  # replace when approved


import pytest


@pytest.mark.parametrize("name,counts", [("content.json", [14, 8, 2]), (MONTH1, [22, 13, 4]), (MONTH2, [22, 14, 4]), (MONTH3, [22, 13, 5]), (MONTH4, [22, 13, 4])])
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
        if it["format"] == "long":
            words = sum(len(s.narration.split()) for s in sc.segments)
            seconds = words / 160 * 60 + len(sc.segments)  # 160 wpm + a beat per chapter (as in the chapter maker)
            assert seconds >= 485, (sc.title, seconds)  # 8+ minutes, so YouTube allows mid-roll ads


def test_month_1_has_no_repeat_titles_and_fills_30_days(factory):
    launch = {i["script"]["title"].lower() for i in _items()}
    month = _items(MONTH1)
    assert not launch & {i["script"]["title"].lower() for i in month}
    slots, leftover = plan(factory.brand("1099-money"), month, date(2026, 11, 30), 30)
    assert not leftover
    assert {s.day for s in slots} == set(range(1, 31))


def test_month_2_has_no_repeat_titles_and_fills_31_days(factory):
    earlier = {i["script"]["title"].lower() for i in _items() + _items(MONTH1)}
    month = _items(MONTH2)
    assert not earlier & {i["script"]["title"].lower() for i in month}
    slots, leftover = plan(factory.brand("1099-money"), month, date(2026, 12, 30), 31)
    assert not leftover
    assert {s.day for s in slots} == set(range(1, 32))


def test_month_3_has_no_repeat_titles_and_fills_31_days(factory):
    earlier = {i["script"]["title"].lower() for i in _items() + _items(MONTH1) + _items(MONTH2)}
    month = _items(MONTH3)
    assert not earlier & {i["script"]["title"].lower() for i in month}
    slots, leftover = plan(factory.brand("1099-money"), month, date(2027, 1, 30), 31)
    assert not leftover
    assert {s.day for s in slots} == set(range(1, 32))


def test_month_4_has_no_repeat_titles_and_fills_31_days(factory):
    earlier = {i["script"]["title"].lower() for i in _items() + _items(MONTH1) + _items(MONTH2) + _items(MONTH3)}
    month = _items(MONTH4)
    assert not earlier & {i["script"]["title"].lower() for i in month}
    slots, leftover = plan(factory.brand("1099-money"), month, date(2027, 3, 2), 31)
    assert not leftover
    assert {s.day for s in slots} == set(range(1, 32))


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


def test_product_ladder_builds(tmp_path):
    pytest.importorskip("openpyxl")
    pytest.importorskip("docx")
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_kit", LAUNCH / "products" / "build_kit.py")
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    files = kit.build_all(tmp_path)
    assert len(files) == 6 and all(f.stat().st_size > 5000 for f in files)
    from openpyxl import load_workbook
    wb = load_workbook(files[0])
    assert wb.sheetnames[:5] == ["Start Here", "Rate Calculator", "Project Pricer", "Invoice", "Invoice Log"]
    assert wb["Grossup"].sheet_state == "hidden"
    assert wb["Rate Calculator"]["C6"].value == 55000  # matches the rate video's example
    # The prices in the brand file, listings and upsell path agree.
    text = (LAUNCH / "products" / "UPSELL_PATH.md").read_text()
    assert "$15" in text and "$29" in text and "$49" in text and "TRACKER15" in text and "KIT29" in text
    assert "$29" in (LAUNCH / "products" / "rate-contract-kit" / "LISTING.md").read_text()
    assert "$49" in (LAUNCH / "products" / "bundle" / "LISTING.md").read_text()


def test_spring_channels_point_at_etsy_calculator_and_compare_pages(factory, tmp_path):
    from contentfactory import channels
    res = channels.export(factory, "1099-money", LAUNCH / "channels" / "spring.json", tmp_path, render=False)
    assert res["block"] == 0 and res["warn"] == 0 and res["issues"] == 8 and res["pins"] >= 36
    pins = json.loads((tmp_path / "pinterest" / "pins.json").read_text())
    targets = [p["target"] for p in pins]
    for listing in ("quarterly-tax-tracker", "rate-contract-kit", "freelancer-money-bundle"):
        assert sum(t == f"product:etsy-{listing}".replace("rate-contract", "rate-and-contract") for t in targets) == 2
    assert sum(t == "article:calculator" for t in targets) >= 4
    assert any(t.startswith("article:") and "calculator" not in t for t in targets)
    assert not {p["title"] for p in pins} & {"Six weeks to April 15: the freelancer countdown", "Your 1099s are due Monday: check these 3 things"}
    for p in pins:
        if "etsy.com" in p["link"]:
            assert "utm_" not in p["link"]
        else:
            assert "utm_source=pinterest" in p["link"]


def test_b2b_kit_builds_with_verified_leads_and_a_clean_schedule(tmp_path):
    import csv as _csv
    import datetime as _dt
    import importlib.util
    import re as _re

    spec = importlib.util.spec_from_file_location("build_b2b", LAUNCH / "b2b" / "build_b2b.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tracker = mod.build(tmp_path)

    n = len(tracker)
    assert 70 <= n <= 80
    rows = list(_csv.DictReader(open(tmp_path / "leads_research.csv")))
    assert len({r["email"].lower() for r in rows}) == n
    for r in rows:
        assert _re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", r["email"], _re.I), r["email"]
        assert r["email_source_url"].startswith("http"), r["name"]
        assert r["opener"], r["name"]

    holidays = {"2026-11-26", "2026-11-27", "2026-12-24", "2026-12-25"}
    days = sorted({t["email1_planned"] for t in tracker})
    assert days[0] == "2026-11-11"
    for t in tracker:
        for k in ("email1_planned", "fu1_planned", "fu2_planned"):
            d = _dt.date.fromisoformat(t[k])
            assert d.weekday() < 5 and t[k] not in holidays, (t["name"], k, t[k])
        assert t["email1_planned"] < t["fu1_planned"] < t["fu2_planned"]
    from collections import Counter
    per_day = Counter(t["email1_planned"] for t in tracker)
    assert max(per_day.values()) == 8 and all(v == 8 for d, v in per_day.items() if d != days[-1])

    pitches = sorted((tmp_path / "pitches").glob("*.md"))
    assert len(pitches) == n
    allowed = {"{Your Name}", "{Bundle link}", "{Street address or PO box / registered mailbox}",
               "{City, Postcode}", "{Country}"}
    for p in pitches:
        text = p.read_text()
        assert text.count('Not interested? Reply "no thanks"') == 3, p.name
        assert set(_re.findall(r"\{[^{}]+\}", text)) <= allowed, p.name
        assert "Jan 15, 2027" in text and "$49" in text
        sent = "".join(_re.findall(r"```\n(.*?)```", text, _re.S))
        assert "affiliate" not in sent.lower()
        assert "$600" not in text  # the 2026 1099-NEC threshold is $2,000
