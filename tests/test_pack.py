import json
from datetime import date
from pathlib import Path

from contentfactory.pack import caption_txt, plan, revenue_tags

ROOT = Path(__file__).resolve().parents[1]
MONTH = ROOT / "launch" / "money-made-simple" / "month-1" / "content.json"


def _items():
    return json.loads(MONTH.read_text())


def test_month_content_is_valid(factory):
    from contentfactory.schemas import Script
    items = _items()
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
