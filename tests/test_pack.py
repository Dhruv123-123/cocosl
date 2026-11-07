import json
from datetime import date
from pathlib import Path

import pytest

from contentfactory.pack import caption_txt, est_seconds, plan, platforms_for, revenue_tags, tiktok_segments

ROOT = Path(__file__).resolve().parents[1]
MONTHS = sorted((ROOT / "launch" / "money-made-simple").glob("month-*/content.json"))
MONTH = MONTHS[0]
EVERGREEN = ROOT / "launch" / "money-made-simple" / "evergreen" / "content.json"
SERIES = ROOT / "launch" / "money-made-simple" / "youtube-series" / "content.json"


def _items(path=MONTH):
    return json.loads(path.read_text())


@pytest.mark.parametrize("path", MONTHS + [EVERGREEN, SERIES], ids=lambda p: p.parent.name)
def test_month_content_is_valid(factory, path):
    from contentfactory.schemas import Script
    items = _items(path)
    titles = [i["script"]["title"] for i in items]
    assert len(titles) == len(set(titles))
    brand = factory.brand("money-made-simple")
    for it in items:
        sc = Script.model_validate(it["script"])
        assert it["format"] in ("short", "carousel", "long")
        assert it["pillar"] in brand.pillars
        assert sc.claims_to_verify and sc.sources
        text = " ".join(s.narration for s in sc.segments).lower()
        assert not any(b.lower() in text for b in brand.voice.banned_phrases)
        if "affiliate" in sc.caption.lower():
            assert "commission" in sc.caption


def test_plan_respects_cadence_and_cap(factory):
    brand = factory.brand("money-made-simple")
    items = _items()
    slots, leftover = plan(brand, items, date(2026, 11, 21), 30)
    assert len(slots) + len(leftover) == len(items)
    assert {s.day for s in slots} == set(range(1, 31))  # every day has a post
    per = {}
    for s in slots:
        for p in s.platforms:
            per[(s.day, p)] = per.get((s.day, p), 0) + 1
    assert max(per.values()) <= brand.cadence.max_posts_per_day_per_platform
    longs = [s for s in slots if s.fmt == "long"]
    assert all(s.when.weekday() == 6 and "youtube" in s.platforms
               and set(s.platforms) <= set(platforms_for(brand, "long")) for s in longs)
    assert all("instagram" in s.platforms and set(s.platforms) <= set(platforms_for(brand, "carousel"))
               for s in slots if s.fmt == "carousel")
    assert [s.index for s in slots if s.fmt == "short"] == sorted(s.index for s in slots if s.fmt == "short")


def test_caption_txt_has_disclosures(factory):
    brand = factory.brand("money-made-simple")
    items = _items()
    slots, _ = plan(brand, items, date(2026, 11, 21), 30)
    aff = next(s for s in slots if "affiliate" in s.tags)
    txt = caption_txt(brand, items[aff.index], aff)
    assert brand.ai_disclosure in txt and "affiliate link" in txt and "CHECK BEFORE POSTING" in txt
    assert revenue_tags(brand, "nothing to see") == []


def test_export_writes_pack(factory, tmp_path):
    from contentfactory.pack import export
    items = [i for i in _items() if i["format"] == "carousel"][:1] + [i for i in _items() if i["format"] == "short" and not i.get("tiktok_extra")][:1]
    res = export(factory, "money-made-simple", items, tmp_path / "pack", date(2026, 11, 21), 3)
    out = tmp_path / "pack"
    assert res["posts"] == 2 and res["block"] == 0
    for name in ("POSTING_PLAN.md", "calendar.csv", "calendar.ics", "CHECKS.md", "content.json"):
        assert (out / name).exists()
    car = next((out / "carousels").iterdir())
    assert sorted(p.name for p in car.glob("slide-*"))[0].startswith("slide-01")
    vid = next((out / "videos-need-voice").iterdir())
    assert (vid / "thumbnail.jpg").exists() or (vid / "thumbnail.png").exists()
    assert "NARRATION SCRIPT" in (vid / "caption.txt").read_text()


@pytest.mark.parametrize("month,start,days", [("month-2", date(2026, 12, 21), 31), ("month-3", date(2027, 1, 21), 31),
                                              ("month-4", date(2027, 2, 21), 28),
                                              ("month-5", date(2027, 3, 21), 31),
                                              ("month-6", date(2027, 4, 21), 30),
                                              ("month-7", date(2027, 5, 21), 31),
                                              ("month-8", date(2027, 6, 21), 30),
                                              ("month-9", date(2027, 7, 21), 31),
                                              ("month-10", date(2027, 8, 21), 31),
                                              ("month-11", date(2027, 9, 21), 30)])
def test_tiktok_cuts_and_series(factory, month, start, days):
    items = _items(ROOT / "launch" / "money-made-simple" / month / "content.json")
    shorts = [i for i in items if i["format"] == "short"]
    assert shorts and all(i.get("tiktok_extra") for i in shorts)
    for it in shorts:
        base = [s["narration"] for s in it["script"]["segments"]]
        cut = [s["narration"] for s in tiktok_segments(it)]
        assert est_seconds(base) <= 50          # Reels/Shorts cut stays short
        assert 55 <= est_seconds(cut) <= 90     # TikTok cut lands in the 60-90s band once pauses are added
        assert cut[-1] == base[-1]
        assert any(ch.isdigit() for ch in it["script"]["hook"])  # number-first hooks
    rmb = [i for i in items if i.get("series") == "Rate My Budget"]
    assert len(rmb) >= 4
    assert all("Fictional example" in i["script"]["caption"] for i in rmb)
    brand = factory.brand("money-made-simple")
    slots, leftover = plan(brand, items, start, days,
                           {"carousel": "mon,tue,wed,thu,fri"})
    assert len(leftover) <= 1  # a spare is fine when the window ends on a weekend
    txt = caption_txt(brand, rmb[0], None)
    assert "TikTok cut" in txt and "Reels / Shorts cut" in txt


def test_evergreen_library_is_undated_and_unique():
    import re
    items = _items(EVERGREEN)
    assert len(items) == 50
    assert sum(i["format"] == "short" for i in items) == 25
    for it in items:
        blob = json.dumps(it["script"])
        assert not re.search(r"\b20[2-3]\d\b", blob), it["script"]["title"]  # no years: works any month
        if it["format"] == "short":
            assert est_seconds(s["narration"] for s in it["script"]["segments"]) <= 20
    seen = {i["script"]["title"].lower() for m in MONTHS for i in _items(m)}
    assert not seen & {i["script"]["title"].lower() for i in items}


def test_no_title_reused_across_months():
    titles = [i["script"]["title"].lower() for m in MONTHS for i in _items(m)]
    assert len(titles) == len(set(titles)), sorted(t for t in titles if titles.count(t) > 1)


# Ids from the hook library (src/contentfactory/hooks_library.json, scouting PR). Kept here so this
# test runs on branches that don't have the library file yet.
HOOK_TEMPLATE_IDS = {
    "fine-print", "cost-of-mistake", "if-i-started-today", "visualize-the-number", "x-vs-y-real-math",
    "stop-doing", "myth-check", "tonight-in-minutes", "three-signs", "pov-your-age", "nobody-explains",
    "word-on-statement", "free-money-left", "same-income-different-result", "the-one-question",
    "paid-off-but", "app-honest-review", "calendar-surprise", "percent-fee-eats", "checklist-save",
    "what-you-own", "scam-script-reveal", "scam-one-tell", "scam-real-or-fake", "scam-what-happens-next",
    "scam-too-good", "scam-protect-parents", "small-change-big-year", "question-you-asked", "boring-wins",
}


def test_rewritten_hooks_use_library_templates():
    import re
    from contentfactory.guardrails import HYPE_PATTERNS, TESTIMONIAL_PATTERNS
    lib = ROOT / "src" / "contentfactory" / "hooks_library.json"
    ids = HOOK_TEMPLATE_IDS
    if lib.exists():
        data = json.loads(lib.read_text())
        ids = {t["id"] for t in (data["templates"] if isinstance(data, dict) else data)}
    rewritten = [it for p in MONTHS for it in _items(p) if it.get("hook_template")]
    assert len(rewritten) >= 20
    for it in rewritten:
        sc = it["script"]
        assert it["hook_template"] in ids
        assert any(ch.isdigit() for ch in sc["hook"])           # number-first, like the newer months
        assert sc["segments"][0]["narration"] == sc["hook"]     # the spoken open matches the hook
        assert len(sc["hook"].split()) <= 24
        for pat in HYPE_PATTERNS + TESTIMONIAL_PATTERNS:
            assert not re.search(pat, sc["hook"], re.I), (sc["title"], pat)


def test_youtube_series_is_long_form_and_tagged():
    import re
    from urllib.parse import parse_qs, urlparse
    from contentfactory.guardrails import HYPE_PATTERNS, TESTIMONIAL_PATTERNS
    items = _items(SERIES)
    assert len(items) == 12 and all(i["format"] == "long" for i in items)
    assert [i["series_part"] for i in items] == list(range(1, 13))
    others = {i["script"]["title"].lower() for m in MONTHS + [EVERGREEN] for i in _items(m)}
    for it in items:
        sc = it["script"]
        words = sum(len(s["narration"].split()) for s in sc["segments"])
        assert 1200 <= words <= 1800, (sc["title"], words)      # 8-12 minutes at ~150 words a minute
        assert sc["title"].lower() not in others
        assert it["search_terms"] and sc["thumbnail_text"] and len(sc["thumbnail_text"].split()) <= 6
        assert any(ch.isdigit() for ch in sc["hook"])
        chapters = re.findall(r"^(\d+):(\d\d) (.+)$", sc["description"], re.M)
        assert len(chapters) == len(sc["segments"]) and chapters[0][:2] == ("0", "00")  # YouTube needs 0:00
        secs = [int(m) * 60 + int(s) for m, s, _ in chapters]
        assert secs == sorted(secs) and all(b - a >= 10 for a, b in zip(secs, secs[1:]))
        links = re.findall(r"https://moneymadesimple\.netlify\.app\S+", sc["description"])
        assert len(links) >= 3
        for url in links:
            q = parse_qs(urlparse(url).query)
            assert q["utm_source"] == ["youtube"] and q["utm_medium"] == ["social"]
            assert q["utm_campaign"] == [it["content_id"]]
        assert "AI tools" in sc["description"]
        if "/compare/" in sc["description"]:
            assert "commission" in sc["description"]
        text = " ".join([sc["hook"], sc["caption"], sc["description"]] + [s["narration"] for s in sc["segments"]])
        for pat in HYPE_PATTERNS + TESTIMONIAL_PATTERNS:
            assert not re.search(pat, text, re.I), (sc["title"], pat)


HOLIDAY = ROOT / "launch" / "money-made-simple" / "holiday-2026"
# (part, start, days): part 1 covers Nov 20 – Dec 19, part 2 Dec 21 – Dec 31 (Dec 20 is full in month 1).
HOLIDAY_PARTS = [("part-1", date(2026, 11, 20), 30), ("part-2", date(2026, 12, 21), 11)]
HOLIDAY_DAYS = {"short": "wed,sun", "carousel": "sun"}


def test_holiday_addon_fills_open_days_only(factory):
    """The holiday add-on posts only where months 1–2 leave room under the per-platform daily cap."""
    brand = factory.brand("money-made-simple")
    others = {i["script"]["title"].lower() for p in MONTHS + [EVERGREEN, SERIES] for i in _items(p)}
    busy = {}

    def count(slots):
        for s in slots:
            for p in s.platforms:
                busy[(s.when.date(), p)] = busy.get((s.when.date(), p), 0) + 1

    count(plan(brand, _items(MONTHS[0]), date(2026, 11, 21), 30)[0])
    count(plan(brand, _items(ROOT / "launch" / "money-made-simple" / "month-2" / "content.json"),
               date(2026, 12, 21), 31, {"carousel": "mon,tue,wed,thu,fri"})[0])
    titles = []
    for part, start, days in HOLIDAY_PARTS:
        items = _items(HOLIDAY / part / "content.json")
        titles += [i["script"]["title"].lower() for i in items]
        for it in (i for i in items if i["format"] == "short"):
            assert it["format_style"]
            assert est_seconds([s["narration"] for s in it["script"]["segments"]]) <= 50
            assert 55 <= est_seconds([s["narration"] for s in tiktok_segments(it)]) <= 90
            assert any(ch.isdigit() for ch in it["script"]["hook"])
            if "fictional" in it["idea_angle"].lower():
                assert "Fictional example" in it["script"]["caption"]
        slots, leftover = plan(brand, items, start, days, HOLIDAY_DAYS)
        assert not leftover
        count(slots)
        styles = [items[s.index]["format_style"] for s in slots if s.fmt == "short"]
        assert all(a != b for a, b in zip(styles, styles[1:]))
    assert len(titles) == len(set(titles)) and not others & set(titles)
    assert max(busy.values()) <= brand.cadence.max_posts_per_day_per_platform


def test_month1_tiktok_long_cuts():
    shorts = [i for i in _items(MONTHS[0]) if i["format"] == "short" and i.get("tiktok_extra")]
    assert len(shorts) >= 11
    for it in shorts:
        cut = [s["narration"] for s in tiktok_segments(it)]
        assert 65 <= est_seconds(cut) <= 90
        assert cut[-1] == it["script"]["segments"][-1]["narration"]


BASICS = ROOT / "launch" / "money-made-simple" / "youtube-money-basics" / "content.json"


def test_money_basics_series_parts_are_long_form_and_tagged():
    import re
    from urllib.parse import parse_qs, urlparse
    from contentfactory.guardrails import HYPE_PATTERNS, TESTIMONIAL_PATTERNS
    items = _items(BASICS)
    others = {i["script"]["title"].lower() for p in MONTHS + [EVERGREEN, SERIES] for i in _items(p)}
    assert [i["series_part"] for i in items] == list(range(1, len(items) + 1)) and len(items) >= 4
    for it in items:
        sc = it["script"]
        words = sum(len(s["narration"].split()) for s in sc["segments"])
        assert 1200 <= words <= 1800, (sc["title"], words)
        assert sc["title"].lower() not in others
        assert sc["segments"][0]["narration"].split()[0] == sc["hook"].split()[0]  # the spoken open is the hook
        assert any(ch.isdigit() for ch in sc["hook"])
        links = re.findall(r"https://\S+", sc["description"])
        assert len(links) >= 3
        for u in links:
            q = parse_qs(urlparse(u).query)
            assert q["utm_campaign"] == [it["content_id"]] and it["content_id"].startswith("yt-basics-")
        assert "AI tools" in sc["description"]
        if "/compare/" in sc["description"]:
            assert "commission" in sc["description"]
        text = " ".join([sc["hook"], sc["caption"], sc["description"]] + [s["narration"] for s in sc["segments"]])
        for pat in HYPE_PATTERNS + TESTIMONIAL_PATTERNS:
            assert not re.search(pat, text, re.I), (sc["title"], pat)


FIRST_1000 = ROOT / "launch" / "money-made-simple" / "youtube-first-1000" / "content.json"


def test_first_1000_investing_series_is_compliance_ready():
    import re
    from contentfactory.guardrails import HYPE_PATTERNS, TESTIMONIAL_PATTERNS
    from contentfactory.schemas import ChartSpec
    items = _items(FIRST_1000)
    others = {i["script"]["title"].lower() for p in MONTHS + [EVERGREEN, SERIES, BASICS] for i in _items(p)}
    assert [i["series_part"] for i in items] == list(range(1, 7))
    assert len({i["format_style"] for i in items}) == 6
    for it in items:
        sc = it["script"]
        words = sum(len(s["narration"].split()) for s in sc["segments"])
        assert 1200 <= words <= 1800, (sc["title"], words)
        assert sc["title"].lower() not in others and len(sc["title"]) <= 70
        assert sc["segments"][0]["narration"].split()[0] == sc["hook"].split()[0]
        assert it["content_id"].startswith("yt-invest-") and f"utm_campaign={it['content_id']}" in sc["description"]
        assert "possible loss of money" in sc["description"] and "hypothetical" in sc["description"]
        assert "don't recommend specific securities" in sc["description"]
        if "/compare/" in sc["description"]:
            assert "commission" in sc["description"]
        assert len(it["compliance_review"]) >= 3
        seg = next(s for s in sc["segments"] if s["heading"] == it["original_element"]["chapter"])
        assert re.search(r"hypothetical|illustrat|example", ChartSpec(**seg["chart"]).note, re.I)
        text = " ".join([sc["hook"], sc["caption"], sc["description"]] + [s["narration"] for s in sc["segments"]])
        for pat in HYPE_PATTERNS + TESTIMONIAL_PATTERNS:
            assert not re.search(pat, text, re.I), (sc["title"], pat)


MONEY_BY_AGE = ROOT / "launch" / "money-made-simple" / "youtube-money-by-age" / "content.json"


def test_money_by_age_series_is_compliance_ready():
    import re
    from contentfactory.guardrails import HYPE_PATTERNS, TESTIMONIAL_PATTERNS
    from contentfactory.schemas import ChartSpec
    items = _items(MONEY_BY_AGE)
    others = {i["script"]["title"].lower() for p in MONTHS + [EVERGREEN, SERIES, BASICS, FIRST_1000] for i in _items(p)}
    assert [i["series_part"] for i in items] == list(range(1, 6))
    assert len({i["format_style"] for i in items}) == 5
    for decade, it in zip(("20s", "30s", "40s", "50s", "60s"), items):
        sc = it["script"]
        words = sum(len(s["narration"].split()) for s in sc["segments"])
        assert 1200 <= words <= 1800, (sc["title"], words)
        assert decade in sc["title"] and sc["title"].lower() not in others and len(sc["title"]) <= 70
        assert sc["segments"][0]["narration"].split()[0] == sc["hook"].split()[0]
        assert it["content_id"].startswith("yt-age-") and f"utm_campaign={it['content_id']}" in sc["description"]
        assert "possible loss of money" in sc["description"] and "fact-checked by a person" in sc["description"]
        assert "fictional" in " ".join(s["narration"] for s in sc["segments"][:3]).lower()
        assert len(it["compliance_review"]) >= 3
        seg = next(s for s in sc["segments"] if s["heading"] == it["original_element"]["chapter"])
        assert re.search(r"hypothetical|fictional|example", ChartSpec(**seg["chart"]).note, re.I)
        text = " ".join([sc["hook"], sc["caption"], sc["description"]] + [s["narration"] for s in sc["segments"]])
        for pat in HYPE_PATTERNS + TESTIMONIAL_PATTERNS:
            assert not re.search(pat, text, re.I), (sc["title"], pat)


MYTH_VS_MATH = ROOT / "launch" / "money-made-simple" / "myth-vs-math" / "content.json"


def test_myth_vs_math_saturdays_fit_under_the_cap(factory):
    """12 weekly Myth vs Math carousels on Saturdays (Nov 21, 2026 – Feb 6, 2027), on top of every other pack."""
    brand = factory.brand("money-made-simple")
    items = _items(MYTH_VS_MATH)
    assert len(items) == 12 and all(i["format"] == "carousel" and i["series"] == "Myth vs Math" for i in items)
    others = {i["script"]["title"].lower() for p in MONTHS + [EVERGREEN, SERIES, BASICS] for i in _items(p)}
    for part, _, _ in HOLIDAY_PARTS:
        others |= {i["script"]["title"].lower() for i in _items(HOLIDAY / part / "content.json")}
    assert not others & {i["script"]["title"].lower() for i in items}
    assert all(i["script"]["hook"].startswith(f"Myth vs Math #{n}:") for n, i in enumerate(items, 1))
    busy = {}

    def count(slots):
        for s in slots:
            for p in s.platforms:
                busy[(s.when.date(), p)] = busy.get((s.when.date(), p), 0) + 1

    starts = {"month-1": (date(2026, 11, 21), 30, None)}
    for m, st, d in [("month-2", date(2026, 12, 21), 31), ("month-3", date(2027, 1, 21), 31),
                     ("month-4", date(2027, 2, 21), 28)]:
        starts[m] = (st, d, {"carousel": "mon,tue,wed,thu,fri"})
    for m, (st, d, spec) in starts.items():
        count(plan(brand, _items(ROOT / "launch" / "money-made-simple" / m / "content.json"), st, d, spec)[0])
    for part, st, d in HOLIDAY_PARTS:
        count(plan(brand, _items(HOLIDAY / part / "content.json"), st, d, HOLIDAY_DAYS)[0])
    slots, leftover = plan(brand, items, date(2026, 11, 21), 78, {"carousel": "sat"})
    assert not leftover and all(s.when.weekday() == 5 for s in slots)
    count(slots)
    assert max(busy.values()) <= brand.cadence.max_posts_per_day_per_platform


CHALLENGE = ROOT / "launch" / "money-made-simple" / "savings-challenge" / "content.json"


def test_savings_challenge_is_tiktok_only_weekly_and_labelled(factory):
    brand = factory.brand("money-made-simple")
    items = _items(CHALLENGE)
    assert [i["series_part"] for i in items] == list(range(1, 9))
    for it in items:
        sc = it["script"]
        assert it["format"] == "mid" and 65 <= est_seconds([s["narration"] for s in sc["segments"]]) <= 90
        assert "not a promise" in sc["caption"] and any(ch.isdigit() for ch in sc["hook"])
        assert all(len(s["on_screen_text"].split()) < 12 for s in sc["segments"])
    assert "$300 of $300" in items[-1]["script"]["caption"]
    slots, leftover = plan(brand, items[:7], date(2026, 11, 15), 43, {"mid": "sun"})
    assert not leftover and all(s.when.weekday() == 6 and s.platforms == ["tiktok"] for s in slots)
    slots, leftover = plan(brand, items[7:], date(2026, 12, 31), 1, {"mid": "thu"})
    assert not leftover and slots[0].platforms == ["tiktok"]


def test_chart_element_videos_carry_a_real_chart():
    from contentfactory.schemas import ChartSpec
    files = MONTHS + [SERIES, BASICS, FIRST_1000, MONEY_BY_AGE]
    longs = [i for p in files for i in _items(p) if i["format"] == "long"]
    charted = [i for i in longs if i["original_element"]["type"] == "worked-example-chart"]
    assert len(charted) >= 20
    for it in charted:
        seg = next(s for s in it["script"]["segments"] if s["heading"] == it["original_element"]["chapter"])
        ChartSpec(**seg["chart"])
    assert all(i["script"].get("original_element") for i in longs)


def test_no_spend_january_challenge_runs_on_january_sundays(factory):
    brand = factory.brand("money-made-simple")
    items = _items(ROOT / "launch" / "money-made-simple" / "no-spend-january" / "content.json")
    assert [i["series_part"] for i in items] == list(range(1, 6))
    for it in items:
        sc = it["script"]
        assert it["format"] == "mid" and 65 <= est_seconds([s["narration"] for s in sc["segments"]]) <= 90
        assert "not a promise" in sc["caption"] and any(ch.isdigit() for ch in sc["hook"])
    slots, leftover = plan(brand, items, date(2027, 1, 3), 29, {"mid": "sun"})
    assert not leftover and [s.when.day for s in slots] == [3, 10, 17, 24, 31]
    assert all(s.platforms == ["tiktok"] for s in slots)


def test_rate_my_budget_items_are_labelled():
    """launch/money-made-simple/community/RATE_MY_BUDGET_SUBMISSIONS.md: every Rate My Budget is either
    labelled fictional, or carries the viewer-submission label plus a consent record (no personal data)."""
    real_label = "Based on a viewer's budget, shared with permission."
    items = [i for p in (ROOT / "launch" / "money-made-simple").rglob("content.json") for i in _items(p)
             if i.get("series") == "Rate My Budget"]
    assert len(items) >= 40
    for it in items:
        cap = it["script"]["caption"]
        sub = it.get("submission")
        if sub:
            assert real_label in cap and "ictional" not in cap, it["script"]["title"]
            assert sub["consent_version"].startswith("rmb-consent-") and sub["consented_on"] and sub["confirmed_on"]
            assert set(sub) <= {"id", "consent_version", "consented_on", "confirmed_on"}
        else:
            assert "Fictional" in cap and real_label not in cap, it["script"]["title"]
