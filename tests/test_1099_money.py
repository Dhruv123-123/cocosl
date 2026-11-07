import json
import re
from datetime import date, timedelta
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
MONTH5 = "month-5/content.json"
MONTH6 = "month-6/content.json"
MONTH7 = "month-7/content.json"
COUPLES = "couples/content.json"
DRIVERS = "drivers/content.json"
YT6 = "youtube-6wk/content.json"
JAR = "jar-challenge/content.json"
MONTH8 = "month-8/content.json"


def test_brand_loads_with_placeholder_affiliates(factory):
    brand = factory.brand("1099-money")
    assert brand.name == "1099 Money"
    assert "not tax" in brand.ai_disclosure
    assert {a.slug for a in brand.affiliates} >= {"freshbooks", "quickbooks", "gusto", "novo", "taxact", "lively"}
    assert all(a.url.startswith("https://example.com/go/") for a in brand.affiliates)  # replace when approved


import pytest


@pytest.mark.parametrize("name,counts", [("content.json", [14, 8, 2]), (MONTH1, [22, 13, 4]), (MONTH2, [22, 14, 4]), (MONTH3, [22, 13, 5]), (MONTH4, [22, 13, 4]), (MONTH5, [22, 13, 5]), (MONTH6, [22, 14, 4]), (MONTH7, [23, 13, 0]), (COUPLES, [6, 3, 1]), (DRIVERS, [10, 0, 0]), (YT6, [0, 0, 6]), (JAR, [10, 1, 0]), (MONTH8, [22, 14, 4])])
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


def test_month_5_has_no_repeat_titles_and_fills_31_days(factory):
    earlier = {i["script"]["title"].lower() for n in ("content.json", MONTH1, MONTH2, MONTH3, MONTH4) for i in _items(n)}
    month = _items(MONTH5)
    assert not earlier & {i["script"]["title"].lower() for i in month}
    slots, leftover = plan(factory.brand("1099-money"), month, date(2027, 4, 2), 31)
    assert not leftover
    assert {s.day for s in slots} == set(range(1, 32))
    tax_day = [s for s in slots if s.when.date() == date(2027, 4, 15) and s.fmt == "short"]
    assert tax_day and month[tax_day[0].index]["script"]["title"].startswith("Tax day")


def test_month_6_has_no_repeat_titles_rotates_formats_and_fills_31_days(factory):
    earlier = {i["script"]["title"].lower() for n in ("content.json", MONTH1, MONTH2, MONTH3, MONTH4, MONTH5, DRIVERS) for i in _items(n)}
    month = _items(MONTH6)
    assert not earlier & {i["script"]["title"].lower() for i in month}
    slots, leftover = plan(factory.brand("1099-money"), month, date(2027, 5, 3), 31)
    assert not leftover
    assert {s.day for s in slots} == set(range(1, 32))
    shorts = [i for i in month if i["format"] == "short"]
    assert all(a["format_style"] != b["format_style"] for a, b in zip(shorts, shorts[1:]))  # no style twice in a row
    assert len({i["format_style"] for i in shorts}) >= 8
    assert all(i.get("original_element") for i in month if i["format"] == "long")
    june = [s for s in slots if s.fmt == "short" and month[s.index]["script"]["title"].startswith("June 15")]
    assert june and date(2027, 5, 31) <= june[0].when.date() <= date(2027, 6, 2)
    text = " ".join(seg["narration"] for i in month for seg in i["script"]["segments"])
    assert "seventy-five dollars an hour" in text and "seventy-two and a half cents" in text


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


def test_driver_series_is_new_and_matches_the_mileage_calculator():
    earlier = {i["script"]["title"].lower() for n in ("content.json", MONTH1, MONTH2, MONTH3, MONTH4, MONTH5) for i in _items(n)}
    drivers = _items(DRIVERS)
    assert not earlier & {i["script"]["title"].lower() for i in drivers}
    text = " ".join(i["script"]["caption"] for i in drivers)
    assert "72.5¢" in text and "$2,000" in text and "$20,000" in text
    assert "$600" not in text  # old 1099-NEC threshold
    assert all("http" not in i["script"]["caption"] for i in drivers)
    guide = (LAUNCH / "drivers" / "README.md").read_text()
    for i in drivers:
        assert i["script"]["title"] in guide


def test_answer_bank_has_30_drafts_and_no_links():
    text = (LAUNCH / "distribution" / "ANSWER_BANK.md").read_text()
    assert len(re.findall(r"^### Q\d+\.", text, re.M)) == 18
    assert len(re.findall(r"^### R\d+\.", text, re.M)) == 12
    assert "http" not in text and "DM me" not in text.replace('No "DM me"', "")
    assert "$2,000" in text and "72.5" in text and "$184,500" in text


def test_q4_year_end_pack_is_ready_to_post():
    posts = json.loads((LAUNCH / "q4" / "posts.json").read_text())
    assert len(posts) == 15
    dates = [p["date"] for p in posts]
    assert dates == sorted(dates) and len(set(dates)) == 15
    assert dates[0] >= "2026-11-20" and dates[-1] <= "2027-01-15"
    for p in posts:
        assert len(p["short"]) <= 280, (p["n"], len(p["short"]))  # fits X as one post
        assert "http" not in p["facebook"] and "1099 Money" not in p["facebook"]  # groups: no links, no brand
        assert "not tax advice" in p["linkedin"].lower() and p["sources"] and p["claims"]
        assert (LAUNCH / "q4" / p["card_file"]).exists()
        assert len(p["card"]) == 3
    text = " ".join(p["linkedin"] + p["short"] for p in posts)
    for fact in ("$2,000", "$20,000", "72.5", "February 1, 2027", "tax year 2026", "December 15"):
        assert fact.lower() in text.lower(), fact
    assert "$600 or more" not in text
    topics = {p["topic"] for p in posts}
    assert topics == {"jan15", "equipment", "yearend", "retirement", "1099"}
    emails = sorted((ROOT / "apps" / "freelance-tax" / "emails" / "year-end").glob("0*.md"))
    assert len(emails) == 2
    for e in emails:
        body = e.read_text()
        assert re.search(r"^send_on: 2026-12-\d\d$", body, re.M) and "{{q4_url}}" in body
        assert "not tax, legal or financial advice" in body and "tracker" not in body.lower()


def test_tax_season_posts_rotate_formats_and_are_ready():
    posts = json.loads((LAUNCH / "tax-season" / "posts.json").read_text())
    assert len(posts) == 20
    dates = [p["date"] for p in posts]
    assert dates == sorted(dates) and dates[0] >= "2027-01-16" and dates[-1] <= "2027-04-15"
    assert all(a["format"] != b["format"] for a, b in zip(posts, posts[1:]))  # never the same structure twice in a row
    assert len({p["format"] for p in posts}) == 6
    assert {p["topic"] for p in posts} == {"filing", "schedulec", "deductions", "homeoffice", "mileage", "q1"}
    q4_titles = {p["title"] for p in json.loads((LAUNCH / "q4" / "posts.json").read_text())}
    assert not q4_titles & {p["title"] for p in posts}
    for p in posts:
        assert len(p["short"]) <= 280, (p["n"], len(p["short"]))
        assert "http" not in p["facebook"] and "1099 Money" not in p["facebook"]
        assert (LAUNCH / "tax-season" / p["card_file"]).exists() and p["sources"] and p["claims"]
        if p["format"] == "myth-vs-fact":
            assert p["linkedin"].count("Myth:") >= 3 and p["linkedin"].count("Fact:") >= 3
        if p["format"] == "common-question":
            assert p["linkedin"].startswith("A common question")
    text = " ".join(p["linkedin"] for p in posts)
    for fact in ("$12,037", "72.5", "$16,100", "January 18, 2028", "October 15", "$2,000"):
        assert fact in text, fact


def test_linkedin_kit_is_complete_and_ready_to_post():
    kit = LAUNCH / "linkedin"
    posts = json.loads((kit / "posts.json").read_text())
    assert len(posts) == 30
    days = [date.fromisoformat(p["date"]) for p in posts]
    assert days[0] == date(2026, 11, 16) and all((b - a).days == 1 for a, b in zip(days, days[1:]))  # 30 days in a row
    assert all(a["format"] != b["format"] for a, b in zip(posts, posts[1:]))
    assert len({p["format"] for p in posts}) == 7
    for p in posts:
        assert p["chars"] == len(p["text"]) <= 1300, p["n"]  # well under LinkedIn's 3,000
        assert len(p["hook"]) <= 120 and p["text"].startswith(p["hook"])  # shown before "see more"
        assert "http" not in p["text"] and ".app" not in p["text"]  # links only in the first comment
        outside_quotes = re.sub(r'"[^"]*"', "", p["text"])  # scripts quote what the reader would say
        assert not re.search(r"\b(I|my|me|I've|I'm)\b", outside_quotes), p["n"]  # no invented first-person stories
        if p["first_comment"]:
            assert "1099money.netlify.app" in p["first_comment"]
        if p["topic"] == "tax":
            assert "not tax advice" in p["text"]
    text = " ".join(p["text"] for p in posts)
    for fact in ("$75 an hour", "$84,000", "$90,000", "1,200 hours", "15.3% on 92.35%", "January 15, 2027", "$2,000 or more"):
        assert fact in text, fact  # same figures as apps/freelance-tax/test/rate.test.js and the 2026 tax model
    comments = (kit / "COMMENTS.md").read_text()
    assert len(re.findall(r"^\*\*\d+\.", comments, re.M)) >= 20
    assert "http" not in comments and "1099money" not in comments
    readme = (kit / "README.md").read_text()
    tagline = re.search(r"> (Free rate, tax.+)", readme).group(1)
    assert len(tagline) <= 120
    for img in ("page-cover.png", "profile-banner.png", "page-logo.png"):
        assert (kit / "images" / img).exists(), img


def test_threads_x_kit_fits_both_platforms_and_is_ready():
    import importlib.util
    kit = LAUNCH / "threads-x"
    spec = importlib.util.spec_from_file_location("build_threads_x", kit / "build_threads_x.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    days = json.loads((kit / "posts.json").read_text())
    assert len(days) == 30
    dates = [date.fromisoformat(d["date"]) for d in days]
    assert dates[0] == date(2026, 11, 16) and all((b - a).days == 1 for a, b in zip(dates, dates[1:]))
    assert all(a["format"] != b["format"] for a, b in zip(days, days[1:]))
    assert len({d["format"] for d in days}) == 7
    for d in days:
        assert (len(d["posts"]) > 1) == (d["format"] == "thread"), d["n"]
        for t in d["posts"]:
            assert mod.xlen(t) <= 280, (d["n"], mod.xlen(t))  # X's weighted count; Threads allows 500
            assert "http" not in t and ".app" not in t  # links go in the link reply only
            assert not re.search(r"\b(I|my|me|I've|I'm)\b", re.sub(r'"[^"]*"', "", t)), d["n"]
        if d["link_reply"]:
            assert "1099money.netlify.app" in d["link_reply"]
    assert mod.xlen("☐ → 🧵") == 8 and mod.xlen("abc") == 3
    text = " ".join(t for d in days for t in d["posts"])
    for fact in ("$75/hour", "15.3%", "92.35%", "$91,800", "Jan 15"):
        assert fact in text, fact
    replies = (kit / "REPLIES.md").read_text()
    assert len(re.findall(r"^\*\*\d+\.", replies, re.M)) >= 20 and "http" not in replies
    readme = (kit / "README.md").read_text()
    x_bio, threads_bio = re.findall(r"^  > (.+)$", readme, re.M)[:2]
    assert len(x_bio) <= 160 and len(threads_bio) <= 150
    assert (kit / "images" / "x-header.png").exists()


def test_short_titles_fit_in_60_characters():
    # Shorts titles get cut off in the feed past ~60 characters; YouTube's hard limit is 100 for any video.
    files = ["content.json", MONTH1, MONTH2, MONTH3, MONTH4, MONTH5, MONTH6, DRIVERS, YT6, JAR, MONTH7, COUPLES]
    for name in files:
        for it in _items(name):
            title = it["script"]["title"]
            limit = 60 if it["format"] == "short" else 100
            assert len(title) <= limit, (name, it["format"], len(title), title)


def test_tax_checklist_lead_magnet_is_built_and_dated():
    html = (LAUNCH / "lead-magnets" / "tax-checklist" / "checklist.html").read_text()
    for fact in ("Fri Jan 15, 2027", "Thu Apr 15, 2027", "Tue Jun 15, 2027", "Wed Sep 15, 2027", "Tue Jan 18, 2028",
                 "Feb 1, 2027", "72.5¢", "$16,100", "110%", "$2,000 or more"):
        assert fact in html, fact
    assert html.count('class="page') == 5 and "not tax" in html.lower()
    pdf = ROOT / "apps" / "freelance-tax" / "downloads" / "freelancer-tax-checklist.pdf"
    assert pdf.exists() and pdf.read_bytes()[:4] == b"%PDF" and pdf.stat().st_size > 20000


def test_six_week_youtube_plan_has_charts_end_slates_and_new_titles(factory):
    plan_items = _items(YT6)
    earlier = {i["script"]["title"].lower() for n in ["content.json", MONTH1, MONTH2, MONTH3, MONTH4, MONTH5, MONTH6, DRIVERS]
               for i in _items(n)}
    assert not earlier & {i["script"]["title"].lower() for i in plan_items}
    for it in plan_items:
        segs = it["script"]["segments"]
        # A real chart drawn from the video's own numbers, so the pack's original-element check passes.
        charts = [s for s in segs if s.get("chart")]
        assert charts and all(len(c["chart"]["labels"]) == len(c["chart"]["values"]) >= 2 for c in charts)
        assert all(v > 0 for c in charts for v in c["chart"]["values"])  # the chart renderer draws bars up from zero
        # 20-second end slate: the last beat, ~20s of narration at 160 wpm, with end-screen cards planned.
        end = segs[-1]
        seconds = len(end["narration"].split()) / 160 * 60 + 1
        assert end["heading"] == "End slate" and 19 <= seconds <= 21, (it["script"]["title"], seconds)
        assert it["end_slate"]["seconds"] == 20 and len(it["end_slate"]["cards"]) >= 2
        assert segs[-2]["heading"] == "Recap"
    # Each end slate points at the next week's video; the last one points back to the first.
    titles = [i["script"]["title"] for i in plan_items]
    assert [i["end_slate"]["watch_next"] for i in plan_items] == titles[1:] + titles[:1]
    slots, leftover = plan(factory.brand("1099-money"), plan_items, date(2027, 6, 6), 36)
    assert not leftover
    assert sorted(s.when.date() for s in slots) == [date(2027, 6, 6) + timedelta(weeks=k) for k in range(6)]


def test_tax_jar_challenge_runs_weekly_to_jan_15_and_stays_honest():
    items = _items(JAR)
    earlier = {i["script"]["title"].lower() for n in ["content.json", MONTH1, MONTH2, MONTH3, MONTH4, MONTH5, MONTH6, DRIVERS, YT6]
               for i in _items(n)}
    assert not earlier & {i["script"]["title"].lower() for i in items}
    shorts = [i for i in items if i["format"] == "short"]
    days = [date.fromisoformat(i["post_on"]) for i in shorts]
    assert days[0] == date(2026, 11, 16) and days[-1] == date(2027, 1, 15)
    assert days[1:-1] == [date(2026, 11, 23) + timedelta(weeks=k) for k in range(8)]  # every Monday
    assert [i["series"] for i in shorts] == [f"Tax Jar Challenge {k}/10" for k in range(1, 11)]
    assert len({i["format_style"] for i in shorts}) == 10  # each check-in built differently
    for it in items:
        text = " ".join(s["narration"] for s in it["script"]["segments"]) + it["script"]["caption"]
        assert not re.search(r"\byou will save\b|\bI saved\b|\bcomment [A-Z]{3,}\b", text), it["script"]["title"]
        if re.search(r"\bSam\b", text):
            assert "fictional" in text.lower()
    for it in shorts[1:-1]:
        assert "pinned" in " ".join(s["narration"] for s in it["script"]["segments"])  # points back to day 1
    pdf = ROOT / "apps" / "freelance-tax" / "downloads" / "tax-jar-tracker.pdf"
    assert pdf.exists() and pdf.read_bytes()[:4] == b"%PDF"
    assert "tax-jar-tracker.pdf" in (ROOT / "apps" / "freelance-tax" / "free" / "thanks" / "index.html").read_text()


def test_month_7_fills_jun_3_to_jul_3_with_the_youtube_plan_on_sundays(factory):
    earlier = {i["script"]["title"].lower() for n in ("content.json", MONTH1, MONTH2, MONTH3, MONTH4, MONTH5, MONTH6, DRIVERS, YT6, JAR)
               for i in _items(n)}
    month = _items(MONTH7)
    assert not earlier & {i["script"]["title"].lower() for i in month}
    brand = factory.brand("1099-money")
    slots, leftover = plan(brand, month, date(2027, 6, 3), 31)
    assert not leftover
    sundays = {s.when.date() for s in plan(brand, _items(YT6), date(2027, 6, 6), 36)[0]}
    covered = {s.when.date() for s in slots} | sundays
    assert {date(2027, 6, 3) + timedelta(days=k) for k in range(31)} <= covered
    shorts = [i for i in month if i["format"] == "short"]
    assert all(a["format_style"] != b["format_style"] for a, b in zip(shorts, shorts[1:]))
    assert len({i["format_style"] for i in shorts}) >= 8
    by_day = {s.when.date(): month[s.index]["script"]["title"] for s in slots if s.fmt == "short"}
    assert by_day[date(2027, 6, 14)].startswith("Tomorrow")  # the day before the Jun 15 payment


def test_couples_pack_fits_its_week_and_matches_the_tax_model(factory):
    items = _items(COUPLES)
    earlier = {i["script"]["title"].lower() for n in ("content.json", MONTH1, MONTH2, MONTH3, MONTH4, MONTH5, MONTH6, MONTH7, DRIVERS, YT6, JAR)
               for i in _items(n)}
    assert not earlier & {i["script"]["title"].lower() for i in items}
    spec = {"short": "mon,tue,wed,thu,fri,sat", "carousel": "mon,wed,fri", "long": "sun"}
    slots, leftover = plan(factory.brand("1099-money"), items, date(2027, 7, 12), 7, spec)
    assert not leftover and {s.when.date() for s in slots} == {date(2027, 7, 12) + timedelta(days=k) for k in range(7)}
    long = next(i for i in items if i["format"] == "long")
    assert any(s.get("chart") for s in long["script"]["segments"])
    # The numbers in the scripts come from the site's tax model (run: node -e with lib/tax.js, status mfj).
    text = " ".join(s["narration"] for i in items for s in i["script"]["segments"]) + " ".join(i["script"]["caption"] for i in items)
    for figure in ("$13,261", "$9,221", "$7,427", "$355", "$5,623", "$13,992"):
        assert figure in text, figure
    readme = (LAUNCH / "couples" / "README.md").read_text()
    assert "irs.gov" in readme and "$67,539" in readme


def test_recordings_list_covers_every_long_waiting_on_footage_in_date_order():
    text = (LAUNCH / "RECORDINGS.md").read_text()
    files = ["content.json"] + [f"month-{n}/content.json" for n in range(1, 7)]
    waiting = [i["script"]["title"] for f in files for i in _items(f)
               if i["format"] == "long" and i["original_element"]["type"] != "worked-example-chart"]
    assert len(waiting) == 14
    shots = text.split("## Shot lists, by posting date")[1].split("## Also worth")[0]
    headed = re.findall(r"^### (\w{3} \w{3} \d{1,2}, \d{4}) · (.+)$", shots, re.M)
    assert sorted(t for _, t in headed) == sorted(waiting)
    dates = [date(int(d[-4:]), "JanFebMarAprMayJunJulAugSepOctNovDec".index(d[4:7]) // 3 + 1, int(d[8:-6])) for d, _ in headed]
    assert dates == sorted(dates)
    assert shots.count("- **Footage path:**") == 14
    assert "nothing submitted" in shots.lower()


def test_month_8_runs_jul_19_to_aug_18_after_the_couples_week(factory):
    earlier = {i["script"]["title"].lower() for n in ("content.json", MONTH1, MONTH2, MONTH3, MONTH4, MONTH5, MONTH6, MONTH7, COUPLES, DRIVERS, YT6, JAR)
               for i in _items(n)}
    month = _items(MONTH8)
    assert not earlier & {i["script"]["title"].lower() for i in month}
    slots, leftover = plan(factory.brand("1099-money"), month, date(2027, 7, 19), 31)
    assert not leftover
    assert {s.when.date() for s in slots} == {date(2027, 7, 19) + timedelta(days=k) for k in range(31)}
    longs = {s.when.date(): month[s.index] for s in slots if s.fmt == "long"}
    assert sorted(longs) == [date(2027, 7, 25), date(2027, 8, 1), date(2027, 8, 8), date(2027, 8, 15)]
    for it in longs.values():  # every long passes the original-element check with its chart
        assert it["original_element"]["type"] == "worked-example-chart"
        assert any(s.get("chart") and s["heading"] == it["original_element"]["chapter"] for s in it["script"]["segments"])
    assert "September 15" in longs[date(2027, 8, 15)]["script"]["title"]
    shorts = [i for i in month if i["format"] == "short"]
    assert all(a["format_style"] != b["format_style"] for a, b in zip(shorts, shorts[1:]))
    text = " ".join(s["narration"] + " " + s["on_screen_text"] for i in month for s in i["script"]["segments"])
    for figure in ("$3,874", "$1,857", "$7,115", "$12,037", "$8,478", "$615", "$720", "$1,320", "$55,000"):
        assert figure in text or figure in " ".join(i["script"]["caption"] for i in month), figure
    assert "Jan 15, 2028" not in text and "Jan 18, 2028" in text  # Jan 15, 2028 is a Saturday; Jan 17 is MLK Day


def test_freelancer_tax_kit_listing_bundles_only_existing_products_honestly():
    etsy = (LAUNCH / "etsy" / "freelancer-tax-kit.md").read_text()
    gum = (LAUNCH / "products" / "tax-kit" / "LISTING.md").read_text()
    for text in (etsy, gum):
        assert "[PRICE]" in text  # placeholder until Dhruv picks the price
        assert "free" in text and "not tax, legal or financial advice" in text
        assert not re.search(r"\bworth \$|\$\d+ value", text.replace('"worth $X"', "").replace('"a $60 value"', ""))
    tags = re.search(r"\*\*Tags\*\*.*?\n(.+)\n", etsy).group(1).split(" · ")
    assert len(tags) == 13 and all(len(t.strip("`")) <= 20 for t in tags)
    assert len(re.search(r"\*\*Title\*\*.*\n(.+)\n", etsy).group(1)) <= 140
    for f in ("freelancer-tax-calendar-2027.pdf", "freelancer-tax-checklist.pdf", "tax-jar-tracker.pdf"):
        assert (ROOT / "apps" / "freelance-tax" / "downloads" / f).exists()
    assert (LAUNCH / "product" / "Quarterly-Tax-Tracker.xlsx").exists()
    start = (LAUNCH / "products" / "tax-kit" / "the-freelancer-tax-kit.html").read_text()
    assert "Jan 18, 2028" in start and "also free" in start
