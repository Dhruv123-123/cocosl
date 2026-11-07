import json
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
    from contentfactory.pack import build_pack
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
