import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "launch" / "scam-decoded" / "content.json"


def _items():
    return json.loads(CONTENT.read_text())


def test_scam_decoded_content_is_valid_and_routed(factory):
    from contentfactory.schemas import Script
    brand = factory.brand("scam-decoded")
    items = _items()
    shorts = [i for i in items if i["format"] == "short"]
    assert len([i for i in items if i["format"] == "carousel"]) == 8
    assert len([i for i in shorts if i["platforms"] == ["tiktok"]]) == 14
    assert len([i for i in shorts if "tiktok" not in i["platforms"]]) == 14
    for item in items:
        sc = Script.model_validate(item["script"])
        assert any(ch.isdigit() for ch in sc.hook), sc.hook          # hooks open with a number
        assert sc.claims_to_verify and sc.sources
        for p in item.get("platforms", []):
            assert brand.account(p)
        words = sum(len(s.narration.split()) for s in sc.segments)
        if item.get("platforms") == ["tiktok"]:
            assert 150 <= words <= 230, sc.title                     # 60-90s TikTok cut
        elif item["format"] == "short":
            assert 60 <= words <= 120, sc.title                      # 30-45s Reel/Short


def test_platform_pinned_posts_only_schedule_to_their_platform(factory, fake_render):
    item = next(i for i in _items() if i.get("platforms") == ["tiktok"])
    pid = factory.import_script("scam-decoded", item["script"], "short", platforms=["tiktok"])
    assert factory.db.get("posts", pid)["meta"]["platforms"] == ["tiktok"]
    factory.approve(pid)
    pubs = [factory.db.get("publications", p) for p in factory.schedule(pid)]
    assert [p["platform"] for p in pubs] == ["tiktok"]

    other = next(i for i in _items() if i.get("platforms") == ["instagram", "youtube"])
    pid2 = factory.import_script("scam-decoded", other["script"], "short", platforms=other["platforms"])
    factory.approve(pid2)
    assert sorted(factory.db.get("publications", p)["platform"] for p in factory.schedule(pid2)) == \
        ["instagram", "youtube"]


def test_unknown_platform_is_rejected(factory):
    item = _items()[0]
    with pytest.raises(ValueError):
        factory.import_script("scam-decoded", item["script"], "short", render=False, platforms=["myspace"])


def test_build_pack_writes_postable_folders(factory, tmp_path):
    from contentfactory.launch_pack import build_pack
    items = _items()
    subset = [items[0], items[14], items[28]]           # a short, its TikTok cut, a carousel
    content = tmp_path / "content.json"
    content.write_text(json.dumps(subset))
    (tmp_path / "lead-magnet.json").write_text((CONTENT.parent / "lead-magnet.json").read_text())
    out = tmp_path / "pack"
    res = build_pack(factory, "scam-decoded", content, out)
    assert len(res["items"]) == 3
    short_dir = out / "videos-need-voice" / "01-3-ways-to-pay-that-only-scammers-insist-on"
    assert (short_dir / "thumbnail.jpg").exists()
    cap = (short_dir / "caption.txt").read_text()
    assert "Platforms: instagram, youtube" in cap and "CHECK BEFORE POSTING" in cap
    assert "All example messages, names and numbers are fictional" in cap
    tiktok = next((out / "videos-need-voice").glob("02-*-tiktok"))
    assert "Platforms: tiktok" in (tiktok / "caption.txt").read_text()
    slides = sorted((out / "carousels").glob("03-*/slide-*.jpg"))
    assert len(slides) == 9
    assert (out / "brand-kit" / "bio-pack.txt").exists()
    assert (out / "link-in-bio-page" / "index.html").exists()
    magnet = json.loads((out / "link-in-bio-page" / "lead-magnet.json").read_text())
    assert magnet["sections"][0]["heading"] == "Tonight (10 minutes)"
    assert "| 1 | short | tiktok |" in (out / "CONTENTS.md").read_text()


def test_weeks_3_6_content_is_valid_and_routed(factory):
    from contentfactory.schemas import Script
    brand = factory.brand("scam-decoded")
    items = json.loads((CONTENT.parent / "weeks-3-6.json").read_text())
    formats = [i["format"] for i in items]
    assert formats.count("carousel") == 8 and formats.count("long") == 4
    assert len([i for i in items if i.get("platforms") == ["tiktok"]]) == 12
    for item in items:
        sc = Script.model_validate(item["script"])
        assert any(ch.isdigit() for ch in sc.hook), sc.hook
        assert sc.claims_to_verify and sc.sources
        assert all(brand.account(p) for p in item.get("platforms", []))
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments), sc.title


def test_weeks_7_12_content_is_valid_and_routed(factory):
    from contentfactory.schemas import Script
    brand = factory.brand("scam-decoded")
    items = json.loads((CONTENT.parent / "weeks-7-12.json").read_text())
    formats = [i["format"] for i in items]
    assert formats.count("carousel") == 12 and formats.count("long") == 6
    tiktok = [i for i in items if i.get("platforms") == ["tiktok"]]
    shorts = [i for i in items if i.get("platforms") == ["instagram", "youtube"]]
    assert len(tiktok) == len(shorts) == 18
    words = lambda i: sum(len(s["narration"].split()) for s in i["script"]["segments"])
    assert all(60 <= words(i) <= 120 for i in shorts)
    assert all(150 <= words(i) <= 230 for i in tiktok)
    for item in items:
        sc = Script.model_validate(item["script"])
        assert any(ch.isdigit() for ch in sc.hook), sc.hook
        assert sc.claims_to_verify and sc.sources
        assert all(brand.account(p) for p in item.get("platforms", []))
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments), sc.title
        assert "guarantee" not in (sc.caption + " ".join(s.narration for s in sc.segments)).lower()


def test_weeks_13_21_content_is_valid_routed_and_new(factory):
    from contentfactory.schemas import Script
    brand = factory.brand("scam-decoded")
    items = json.loads((CONTENT.parent / "weeks-13-21.json").read_text())
    formats = [i["format"] for i in items]
    assert formats.count("carousel") == 16 and formats.count("long") == 8
    tiktok = [i for i in items if i.get("platforms") == ["tiktok"]]
    shorts = [i for i in items if i.get("platforms") == ["instagram", "youtube"]]
    assert len(tiktok) == len(shorts) == 24
    words = lambda i: sum(len(s["narration"].split()) for s in i["script"]["segments"])
    assert all(60 <= words(i) <= 120 for i in shorts)
    assert all(150 <= words(i) <= 230 for i in tiktok)
    earlier = set()
    for name in ("content.json", "weeks-3-6.json", "weeks-7-12.json"):
        earlier |= {i["script"]["title"] for i in json.loads((CONTENT.parent / name).read_text())}
    for item in items:
        sc = Script.model_validate(item["script"])
        assert sc.title not in earlier, sc.title
        assert any(ch.isdigit() for ch in sc.hook), sc.hook
        assert sc.claims_to_verify and sc.sources
        assert all(brand.account(p) for p in item.get("platforms", []))
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments), sc.title
        assert "guarantee" not in (sc.caption + " ".join(s.narration for s in sc.segments)).lower()
    sext = [i for i in items if "sextortion" in i["script"]["hashtags"]]
    assert sext and all("988" in (i["script"]["caption"] + i["script"]["description"] + " ".join(
        s["narration"] for s in i["script"]["segments"])) for i in sext)


def test_weeks_22_26_april_content_is_valid_and_new(factory):
    from contentfactory.schemas import Script
    brand = factory.brand("scam-decoded")
    items = json.loads((CONTENT.parent / "weeks-22-26.json").read_text())
    formats = [i["format"] for i in items]
    assert formats.count("carousel") == 10 and formats.count("long") == 5
    tiktok = [i for i in items if i.get("platforms") == ["tiktok"]]
    shorts = [i for i in items if i.get("platforms") == ["instagram", "youtube"]]
    assert len(tiktok) == len(shorts) == 15
    words = lambda i: sum(len(s["narration"].split()) for s in i["script"]["segments"])
    assert all(60 <= words(i) <= 120 for i in shorts)
    assert all(150 <= words(i) <= 230 for i in tiktok)
    earlier = set()
    for name in ("content.json", "weeks-3-6.json", "weeks-7-12.json", "weeks-13-21.json"):
        earlier |= {i["script"]["title"] for i in json.loads((CONTENT.parent / name).read_text())}
    for item in items:
        sc = Script.model_validate(item["script"])
        assert sc.title not in earlier, sc.title
        assert any(ch.isdigit() for ch in sc.hook), sc.hook
        assert sc.claims_to_verify and sc.sources
        assert all(brand.account(p) for p in item.get("platforms", []))
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments), sc.title
        assert "guarantee" not in (sc.caption + " ".join(s.narration for s in sc.segments)).lower()
    affiliate = [i for i in items if "comparison (link in bio)" in i["script"]["caption"]]
    assert affiliate and all("affiliate" in i["script"]["caption"] for i in affiliate)
    plan = (CONTENT.parent / "POSTING_PLAN_WEEKS_22-26.md").read_text()
    assert all(f"#{n} " in plan for n in range(len(items)))


def test_answer_bank_has_30_link_free_drafts():
    bank = (CONTENT.parent / "distribution" / "ANSWER_BANK.md").read_text()
    drafts = re.findall(r"^### ([QF]\d+)\.", bank, re.M)
    assert len(drafts) == 30 and len(set(drafts)) == 30
    assert sum(d.startswith("Q") for d in drafts) == 18
    assert not re.search(r"https?://|www\.", bank)
    assert "guarantee" not in bank.lower() and "Nothing has been posted" in bank
    assert "DM me" not in bank.replace('No "DM me"', "").replace('(No "DM me".', "")


def _load_originality(name):
    import importlib.util
    import sys
    d = CONTENT.parent / "originality"
    sys.path.insert(0, str(d))
    try:
        spec = importlib.util.spec_from_file_location(f"originality_{name}", d / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(str(d))


def test_originality_formats_render_to_html(tmp_path, monkeypatch):
    b = _load_originality("build")
    F = b.F
    assert len(F.WALKTHROUGHS) == len(F.QUIZZES) == 8 and len(F.CHARTS) == 4
    for w in F.WALKTHROUGHS:
        page, secs = b.walkthrough_html(w)
        assert 35 <= secs <= 75 and page.count('class="b ') == len(w["messages"])
        assert all(f'id="f{n}"' in page for n in range(1, len(w["flags"]) + 1)), w["id"]
        assert "555-01" in page or "●" in page
    for q in F.QUIZZES:
        slides = b.quiz_slides(q)
        assert len(slides) == len(q["flags"]) + 3
        assert all(f'data-i="{n}"' in slides[0] for n in range(1, len(q["flags"]) + 1)), q["id"]
    for c in F.CHARTS:
        assert len(c["labels"]) == len(c["values"]) == len(c["value_labels"])
        assert c["url"].startswith("https://www.ftc.gov/") and "Source:" in b.chart_slide(c)
    text = (CONTENT.parent / "originality" / "formats.py").read_text()
    assert "NORTON" not in text.upper()


def test_tiktok_minute_cuts_clear_one_minute_and_are_new():
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    items = json.loads((CONTENT.parent / "tiktok-minute-cuts.json").read_text())
    assert len(items) == 10 and all(i["platforms"] == ["tiktok"] for i in items)
    earlier = {}
    for name in ("content.json", "weeks-3-6.json", "weeks-7-12.json", "weeks-13-21.json", "weeks-22-26.json"):
        for i in json.loads((CONTENT.parent / name).read_text()):
            earlier[i["script"]["title"]] = G.shingles(G.script_text(i["script"]))
    for item in items:
        sc = Script.model_validate(item["script"])
        words = sum(len(s.narration.split()) for s in sc.segments)
        assert 165 <= words <= 230, (sc.title, words)  # 66-92 s at 150 wpm
        assert sc.title not in earlier and any(ch.isdigit() for ch in sc.hook)
        assert item["original_element"] and "No AI voice" in item["original_element"]
        assert any("pause" in s.heading.lower() or "quiz" in s.heading.lower() or "Pause" in s.narration
                   for s in sc.segments), sc.title
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments)
        assert sc.sources and sc.claims_to_verify and "guarantee" not in G.script_text(item["script"]).lower()
        mine = G.shingles(G.script_text(item["script"]))
        assert max(G.jaccard(mine, v) for v in earlier.values()) < 0.25, sc.title
    plan = (CONTENT.parent / "ORIGINALITY_PASS.md").read_text()
    assert all(i["script"]["title"] in plan for i in items)


def test_holiday_2026_pack_ten_posts_rotating_formats():
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    items = json.loads((CONTENT.parent / "holiday-2026.json").read_text())
    assert len(items) == 10
    kinds = [(i["format"], tuple(i["platforms"])) for i in items]
    assert all(a != b for a, b in zip(kinds, kinds[1:])), "two posts in a row share a format"
    topics = {i["topic"] for i in items}
    assert topics == {"delivery", "charity", "gift cards", "marketplace"}
    dates = [i["post_on"] for i in items]
    assert dates == sorted(dates) and dates[0] >= "2026-11-09" and dates[-1] <= "2026-12-31"
    earlier = set()
    for name in ("content.json", "weeks-3-6.json", "weeks-7-12.json", "weeks-13-21.json", "weeks-22-26.json",
                 "tiktok-minute-cuts.json"):
        earlier |= {i["script"]["title"] for i in json.loads((CONTENT.parent / name).read_text())}
    for item in items:
        sc = Script.model_validate(item["script"])
        words = sum(len(s.narration.split()) for s in sc.segments)
        if item["platforms"] == ["tiktok"]:
            assert 165 <= words <= 230, sc.title
        elif item["format"] == "short":
            assert 60 <= words <= 120, sc.title
        assert sc.title not in earlier and any(ch.isdigit() for ch in sc.hook)
        assert sc.sources and sc.claims_to_verify and item["original_element"]
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments)
        assert "checker" in sc.caption and "guarantee" not in G.script_text(item["script"]).lower()
        for pats in (G.HYPE_PATTERNS, G.TESTIMONIAL_PATTERNS, G.ENGAGEMENT_BAIT):
            assert G.check_patterns(G.script_text(item["script"]), pats, "x", "warn", "x").level == "ok", sc.title
    plan = (CONTENT.parent / "POSTING_PLAN_HOLIDAY_2026.md").read_text()
    assert all(f"#{n} " in plan for n in range(10))


def test_weeks_27_30_may_content_rotates_formats():
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    items = json.loads((CONTENT.parent / "weeks-27-30.json").read_text())
    fmt = lambda f, p=None: [i for i in items if i["format"] == f and (p is None or i["platforms"] == p)]
    assert len(fmt("long")) == 4 and len(fmt("carousel")) == 8
    assert len(fmt("short", ["tiktok"])) == len(fmt("short", ["instagram", "youtube"])) == 12
    dates = [i["post_on"] for i in items]
    assert dates == sorted(dates) and dates[0].startswith("2027-05-09") and dates[-1] < "2027-06-06"
    videos = [i for i in items if i["format"] != "carousel"]
    assert all(a["look"] != b["look"] for a, b in zip(videos, videos[1:])), "two videos in a row look alike"
    earlier = set()
    for name in ("content.json", "weeks-3-6.json", "weeks-7-12.json", "weeks-13-21.json", "weeks-22-26.json",
                 "tiktok-minute-cuts.json", "holiday-2026.json"):
        earlier |= {i["script"]["title"] for i in json.loads((CONTENT.parent / name).read_text())}
    for item in items:
        sc = Script.model_validate(item["script"])
        words = sum(len(s.narration.split()) for s in sc.segments)
        if item["platforms"] == ["tiktok"]:
            assert 165 <= words <= 230 and "No AI voice" in item["original_element"], sc.title
            assert any(s.heading == "Pause" for s in sc.segments), sc.title
        elif item["format"] == "short":
            assert 60 <= words <= 120, sc.title
        if item["format"] == "long":
            assert item["original_element"] and "Chapters" in sc.description
        assert sc.title not in earlier and any(ch.isdigit() for ch in sc.hook)
        assert sc.sources and sc.claims_to_verify
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments)
        text = G.script_text(item["script"])
        assert "guarantee" not in text.lower()
        for pats in (G.HYPE_PATTERNS, G.TESTIMONIAL_PATTERNS, G.ENGAGEMENT_BAIT):
            assert G.check_patterns(text, pats, "x", "warn", "x").level == "ok", sc.title
    plan = (CONTENT.parent / "POSTING_PLAN_WEEKS_27-30.md").read_text()
    assert all(f"#{n} " in plan for n in range(len(items)))


def test_tax_2027_pack_covers_tax_scams_on_free_saturdays():
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    items = json.loads((CONTENT.parent / "tax-2027.json").read_text())
    assert len(items) == 12
    assert {i["topic"] for i in items} == {"IRS impersonation", "fake preparers", "refund-theft texts", "IP PIN"}
    dates = [i["post_on"] for i in items]
    assert dates == sorted(dates) and dates[0] >= "2027-01-15" and dates[-1] <= "2027-04-15"
    import datetime as dt
    assert all(dt.date.fromisoformat(d[:10]).weekday() == 5 for d in dates)
    videos = [i for i in items if i["format"] != "carousel"]
    assert all(a["look"] != b["look"] for a, b in zip(videos, videos[1:])), "two videos in a row look alike"
    earlier, taken = set(), set()
    for name in ("content.json", "weeks-3-6.json", "weeks-7-12.json", "weeks-13-21.json", "weeks-22-26.json",
                 "tiktok-minute-cuts.json", "holiday-2026.json", "weeks-27-30.json"):
        for i in json.loads((CONTENT.parent / name).read_text()):
            earlier.add(i["script"]["title"])
            if i.get("post_on"):
                taken.add(i["post_on"][:10])
    assert not taken & {d[:10] for d in dates}, "a tax post lands on a day another plan already uses"
    for item in items:
        sc = Script.model_validate(item["script"])
        words = sum(len(s.narration.split()) for s in sc.segments)
        if item["platforms"] == ["tiktok"]:
            assert 165 <= words <= 230 and "No AI voice" in item["original_element"], sc.title
            assert any(s.heading == "Pause" for s in sc.segments), sc.title
        elif item["format"] == "short":
            assert 60 <= words <= 120, sc.title
        assert sc.title not in earlier and any(ch.isdigit() for ch in sc.hook)
        assert sc.sources and sc.claims_to_verify and item["original_element"]
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments)
        text = G.script_text(item["script"])
        assert "checker" in sc.caption and "guarantee" not in text.lower()
        for pats in (G.HYPE_PATTERNS, G.TESTIMONIAL_PATTERNS, G.ENGAGEMENT_BAIT):
            assert G.check_patterns(text, pats, "x", "warn", "x").level == "ok", sc.title
    plan = (CONTENT.parent / "POSTING_PLAN_TAX_2027.md").read_text()
    assert all(f"#{n} " in plan for n in range(12))


def test_holiday_season_pack_fills_free_tuesday_thursday_noon_slots():
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    import datetime as dt
    items = json.loads((CONTENT.parent / "holiday-season-2026.json").read_text())
    assert len(items) == 10
    dates = [i["post_on"] for i in items]
    assert dates == sorted(dates) and dates[0] >= "2026-11-23" and dates[-1] <= "2026-12-31 23:59"
    assert all(d.endswith("12:00") and dt.date.fromisoformat(d[:10]).weekday() in (1, 3) for d in dates)
    assert {i["format"] for i in items} == {"short", "carousel"}
    videos = [i for i in items if i["format"] != "carousel"]
    assert all(a["look"] != b["look"] for a, b in zip(videos, videos[1:])), "two videos in a row look alike"
    earlier, taken = set(), set()
    for f in CONTENT.parent.glob("*.json"):
        if f.name == "holiday-season-2026.json":
            continue
        data = json.loads(f.read_text())
        for i in data if isinstance(data, list) else []:
            if isinstance(i, dict) and "script" in i:
                earlier.add(i["script"]["title"])
                if i.get("post_on"):
                    taken.add(i["post_on"])
    assert not taken & set(dates), "a holiday post lands on a slot another plan already uses"
    for item in items:
        sc = Script.model_validate(item["script"])
        words = sum(len(s.narration.split()) for s in sc.segments)
        if item["format"] == "short":
            assert 60 <= words <= 120 and len(sc.title) <= 60, sc.title
        assert sc.title not in earlier and any(ch.isdigit() for ch in sc.hook.split(".")[0][:60])
        assert sc.sources and sc.claims_to_verify and item["original_element"]
        assert all(any(h in u for h in ("ftc.gov", "bbb.org", "fbi.gov", "ic3.gov")) for u in sc.sources), sc.title
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments) and len(sc.hashtags) <= 5
        text = G.script_text(item["script"])
        assert "checker" in sc.caption and "guarantee" not in text.lower()
        for pats in (G.HYPE_PATTERNS, G.TESTIMONIAL_PATTERNS, G.ENGAGEMENT_BAIT):
            assert G.check_patterns(text, pats, "x", "warn", "x").level == "ok", sc.title
    plan = (CONTENT.parent / "POSTING_PLAN_HOLIDAY_SEASON_2026.md").read_text()
    assert all(f"#{n} " in plan for n in range(10))


def test_weeks_31_34_june_content_rotates_formats():
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    items = json.loads((CONTENT.parent / "weeks-31-34.json").read_text())
    fmt = lambda f, p=None: [i for i in items if i["format"] == f and (p is None or i["platforms"] == p)]
    assert len(fmt("long")) == 4 and len(fmt("carousel")) == 8
    assert len(fmt("short", ["tiktok"])) == len(fmt("short", ["instagram", "youtube"])) == 12
    dates = [i["post_on"] for i in items]
    assert dates == sorted(dates) and dates[0].startswith("2027-06-06") and dates[-1] < "2027-07-04"
    videos = [i for i in items if i["format"] != "carousel"]
    assert all(a["look"] != b["look"] for a, b in zip(videos, videos[1:])), "two videos in a row look alike"
    earlier = set()
    for name in ("content.json", "weeks-3-6.json", "weeks-7-12.json", "weeks-13-21.json", "weeks-22-26.json",
                 "tiktok-minute-cuts.json", "holiday-2026.json", "weeks-27-30.json", "tax-2027.json"):
        earlier |= {i["script"]["title"] for i in json.loads((CONTENT.parent / name).read_text())}
    for item in items:
        sc = Script.model_validate(item["script"])
        words = sum(len(s.narration.split()) for s in sc.segments)
        if item["platforms"] == ["tiktok"]:
            assert 165 <= words <= 230 and "No AI voice" in item["original_element"], sc.title
            assert any(s.heading == "Pause" for s in sc.segments), sc.title
        elif item["format"] == "short":
            assert 60 <= words <= 120, sc.title
        if item["format"] == "long":
            assert item["original_element"] and "Chapters" in sc.description
        assert sc.title not in earlier and any(ch.isdigit() for ch in sc.hook)
        assert sc.sources and sc.claims_to_verify
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments)
        text = G.script_text(item["script"])
        assert "guarantee" not in text.lower()
        for pats in (G.HYPE_PATTERNS, G.TESTIMONIAL_PATTERNS, G.ENGAGEMENT_BAIT):
            assert G.check_patterns(text, pats, "x", "warn", "x").level == "ok", sc.title
    plan = (CONTENT.parent / "POSTING_PLAN_WEEKS_31-34.md").read_text()
    assert all(f"#{n} " in plan for n in range(len(items)))


def test_breach_shorts_promote_the_checklist_on_free_saturdays():
    import datetime as dt
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    items = json.loads((CONTENT.parent / "breach-shorts-2027.json").read_text())
    assert len(items) == 5 and all(a["look"] != b["look"] for a, b in zip(items, items[1:]))
    earlier, taken = set(), set()
    for name in ("content.json", "weeks-3-6.json", "weeks-7-12.json", "weeks-13-21.json", "weeks-22-26.json",
                 "tiktok-minute-cuts.json", "holiday-2026.json", "weeks-27-30.json", "tax-2027.json", "weeks-31-34.json"):
        for i in json.loads((CONTENT.parent / name).read_text()):
            earlier.add(i["script"]["title"])
            if i.get("post_on"):
                taken.add(i["post_on"][:10])
    for item in items:
        assert dt.date.fromisoformat(item["post_on"][:10]).weekday() == 5 and item["post_on"][:10] not in taken
        sc = Script.model_validate(item["script"])
        assert 60 <= sum(len(s.narration.split()) for s in sc.segments) <= 120, sc.title
        assert sc.title not in earlier and any(ch.isdigit() for ch in sc.hook)
        assert sc.sources and sc.claims_to_verify and item["original_element"]
        assert "/breached" in sc.caption and "checker" in sc.caption
        assert all(len(s.on_screen_text.split()) <= 12 for s in sc.segments)
        text = G.script_text(item["script"])
        for pats in (G.HYPE_PATTERNS, G.TESTIMONIAL_PATTERNS, G.ENGAGEMENT_BAIT):
            assert G.check_patterns(text, pats, "x", "warn", "x").level == "ok", sc.title


def test_how_the_scam_actually_worked_series():
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    root = CONTENT.parent
    import sys
    sys.path.insert(0, str(root / "how-it-worked"))
    from series import OUTLINE
    from parts_4_8 import PARTS_4_8
    from series import PARTS as P13
    PARTS = P13 + PARTS_4_8
    assert [o["part"] for o in OUTLINE] == list(range(1, 9))
    assert all(o["source"].startswith("https://") and ("justice.gov" in o["source"] or "ftc.gov" in o["source"]) for o in OUTLINE)
    items = json.loads((root / "how-it-worked.json").read_text())
    assert [i["part"] for i in items] == list(range(1, 9)) and all(i["format"] == "long" for i in items)
    taken = set()
    for name in ("weeks-22-26.json", "weeks-27-30.json", "weeks-31-34.json"):
        taken |= {i["post_on"][:10] for i in json.loads((root / name).read_text()) if i.get("post_on")}
    for item, part in zip(items, PARTS):
        assert item["post_on"][:10] not in taken
        sc = Script.model_validate(item["script"])
        assert 450 <= sum(len(s.narration.split()) for s in sc.segments) <= 900, sc.title
        assert sc.playlist == "How the scam actually worked" and any(ch.isdigit() for ch in sc.hook)
        assert "Chapters" in sc.description and sc.segments[-1].heading == "Three checks"
        assert "Case board" in item["original_element"] and "no AI voice" in item["original_element"]
        assert len(sc.sources) >= 2 and len(sc.claims_to_verify) >= 3
        assert (root / "how-it-worked" / "out" / f"{part['slug']}.html").exists()
        text = G.script_text(item["script"])
        for pats in (G.HYPE_PATTERNS, G.TESTIMONIAL_PATTERNS, G.ENGAGEMENT_BAIT):
            assert G.check_patterns(text, pats, "x", "warn", "x").level == "ok", sc.title
    for n in (0, 4, 5):  # parts with open charges say so
        assert "presumed innocent" in G.script_text(items[n]["script"]), n


def test_every_short_title_fits_60_characters():
    long = []
    for f in sorted(CONTENT.parent.glob("*.json")):
        data = json.loads(f.read_text())
        if not isinstance(data, list):
            continue
        long += [(f.name, i["script"]["title"]) for i in data
                 if isinstance(i, dict) and i.get("format") == "short" and len(i["script"]["title"]) > 60]
    assert not long, long


def test_every_post_uses_at_most_5_hashtags():
    over = []
    for f in sorted(CONTENT.parent.glob("*.json")):
        data = json.loads(f.read_text())
        if isinstance(data, list):
            over += [(f.name, i["script"]["title"]) for i in data
                     if isinstance(i, dict) and "script" in i and len(i["script"].get("hashtags", [])) > 5]
    assert not over, over[:5]


def test_newsletter_cut_pack():
    from contentfactory.schemas import Script
    from contentfactory import guardrails as G
    items = json.loads((CONTENT.parent / "newsletter-cuts.json").read_text())
    assert len(items) == 10 and all(a["look"] != b["look"] for a, b in zip(items, items[1:]))
    slots = set()
    for name in ("weeks-13-21.json", "weeks-22-26.json", "weeks-27-30.json", "weeks-31-34.json", "holiday-2026.json",
                 "tax-2027.json", "breach-shorts-2027.json"):
        slots |= {i["post_on"] for i in json.loads((CONTENT.parent / name).read_text()) if i.get("post_on")}
    news = CONTENT.parent.parent.parent / "sites" / "scam-decoded" / "content" / "newsletter"
    for item in items:
        sc = Script.model_validate(item["script"])
        issue = next(news.glob(f"{item['newsletter_issue']:02d}-*.md")).read_text()
        assert f"send_date: {item['post_on'][:10]}" in issue and item["post_on"] not in slots
        assert len(sc.hashtags) <= 5 and item["platforms"] == ["instagram", "tiktok"]
        assert "no AI voice" in item["original_element"] and sc.sources and sc.claims_to_verify
        assert 60 <= sum(len(s.narration.split()) for s in sc.segments) <= 120, sc.title
        assert any(ch.isdigit() for ch in sc.hook) and "Scam Alert" in sc.caption
        text = G.script_text(item["script"])
        for pats in (G.HYPE_PATTERNS, G.TESTIMONIAL_PATTERNS, G.ENGAGEMENT_BAIT):
            assert G.check_patterns(text, pats, "x", "warn", "x").level == "ok", sc.title


def test_every_long_video_has_an_original_element():
    """YouTube's inauthentic-content rule: each long video needs a chart of its own numbers or Dhruv's footage."""
    import glob
    import sys
    from contentfactory.guardrails import check_original_element
    from contentfactory.schemas import Script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "launch" / "scam-decoded"))
    import long_originals
    longs = []
    for f in sorted(glob.glob(str(Path(__file__).resolve().parents[1] / "launch" / "scam-decoded" / "*.json"))):
        data = json.loads(Path(f).read_text())
        if isinstance(data, list):
            longs += [i for i in data if isinstance(i, dict) and i.get("format") == "long"]
    assert len(longs) >= 39
    paths = []
    for it in longs:
        assert check_original_element(it).level == "ok", it["script"]["title"]
        Script(**it["script"])
        assert it["script"]["original_element"]
        paths += [s["footage"] for s in it["script"]["segments"] if s.get("footage")]
        if it["script"].get("playlist") == "How the scam actually worked":
            assert any(s.get("chart") for s in it["script"]["segments"])
    assert len(paths) == len(set(paths)) and all(p.startswith("footage/scam-decoded/") for p in paths)
    shots = (Path(long_originals.__file__).parent / "LONG_VIDEO_RECORDINGS.md").read_text()
    assert all(p in shots for p in paths)


def test_long_videos_follow_a_worked_example():
    """Originality audit: long videos under 800 words read as templated. Each one carries a worked example."""
    import glob
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "launch" / "scam-decoded"))
    from long_examples import examples
    table = examples()
    longs = []
    for f in sorted(glob.glob(str(Path(__file__).resolve().parents[1] / "launch" / "scam-decoded" / "*.json"))):
        data = json.loads(Path(f).read_text())
        if isinstance(data, list):
            longs += [i for i in data if isinstance(i, dict) and i.get("format") == "long"]
    for it in longs:
        sc = it["script"]
        words = sum(len(s["narration"].split()) for s in sc["segments"])
        assert words >= 800, (sc["title"], words)
        heads = [s["heading"] for s in sc["segments"]]
        assert len(heads) == len(set(heads)), sc["title"]
        chapters = [l.split(" ", 1)[1] for l in sc["description"].splitlines() if re.match(r"^\d+:\d\d ", l)]
        example = [v for k, v in table.items() if sc["title"].startswith(k)]
        assert example or words >= 900, sc["title"]
        for h, *_ in (example[0][1] if example else []):
            assert h in heads and (not chapters or h in chapters), (sc["title"], h)


def test_parents_printable_kit_and_listing(tmp_path, monkeypatch):
    import importlib.util
    import re
    kit = CONTENT.parent / "product" / "parents-printable-kit"
    spec = importlib.util.spec_from_file_location("parents_kit", kit / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "DIST", tmp_path)
    monkeypatch.setattr("sys.argv", ["build.py", "--no-pdf"])
    mod.main()
    html_text = (tmp_path / "Scam-Proof-Your-Parents-Kit.html").read_text()
    assert html_text.count('<section class="page') == 9
    assert len(mod.SCRIPTS) == 8 and sum(len(v) for v in mod.CHECKLIST.values()) == 15
    for word in ("code word", "Fridge", "checklist", "personal use only", "not legal or financial advice"):
        assert word.lower() in html_text.lower(), word
    assert all(any(h in u for h in ("ftc.gov", "fbi.gov", "ic3.gov", "ojp.gov", "justice.gov")) for _, u in mod.SOURCES)
    assert "guarantee" not in html_text.lower()
    listing = (kit / "LISTING.md").read_text()
    assert "[PRICE]" in listing and "## Etsy" in listing and "## Gumroad" in listing
    title = listing.split("**Title (13 words):**\n")[1].split("\n")[0]
    assert len(title.split()) == 13 and len(title) <= 140
    tags = re.findall(r"^\| \d+ \| ([a-z ]+) \| (\d+) \|$", listing, flags=re.M)
    assert len(tags) == 13 and len({t for t, _ in tags}) == 13
    assert all(len(t) <= 20 and len(t) == int(n) for t, n in tags)
    assert "How it's made" in listing and "Personal use only" in listing
