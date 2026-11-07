import json
from datetime import date
from pathlib import Path

import pytest

from contentfactory.pack import caption_txt, est_seconds, plan, revenue_tags, tiktok_segments

ROOT = Path(__file__).resolve().parents[1]
MONTHS = sorted((ROOT / "launch" / "money-made-simple").glob("month-*/content.json"))
MONTH = MONTHS[0]
EVERGREEN = ROOT / "launch" / "money-made-simple" / "evergreen" / "content.json"


def _items(path=MONTH):
    return json.loads(path.read_text())


@pytest.mark.parametrize("path", MONTHS + [EVERGREEN], ids=lambda p: p.parent.name)
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
    assert all(s.when.weekday() == 6 and s.platforms == ["youtube"] for s in longs)
    assert all(s.platforms == ["instagram"] for s in slots if s.fmt == "carousel")
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
    items = [i for i in _items() if i["format"] == "carousel"][:1] + [i for i in _items() if i["format"] == "short"][:1]
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
                                              ("month-4", date(2027, 2, 21), 28)])
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
