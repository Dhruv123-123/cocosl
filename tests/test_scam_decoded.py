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
