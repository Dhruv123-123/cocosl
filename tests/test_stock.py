import json

import httpx
import pytest

from contentfactory.media import stock


def _segs(n):
    return [{"heading": f"Beat {i} grocery shopping", "narration": "x", "on_screen_text": "", "visual_prompt":
             "Flat vector illustration of a shopping cart in a supermarket, no text"} for i in range(n)]


def test_pick_beats_rules():
    segs = _segs(9)
    picked = stock.pick_beats(segs)
    assert len(picked) == 3 and 0 not in picked and all(b - a > 1 for a, b in zip(picked, picked[1:]))
    segs[2]["chart"] = {"kind": "bar"}
    segs[4]["footage"] = "footage/x.mp4"
    assert 2 not in stock.pick_beats(segs) and 4 not in stock.pick_beats(segs)
    assert stock.pick_beats(_segs(2)) == []
    assert stock.query_for(segs[1]) == "beat grocery shopping shopping" or "grocery" in stock.query_for(segs[1])


def _client():
    def handler(req: httpx.Request):
        if "pexels.com/v1/videos/search" in str(req.url):
            assert req.headers["Authorization"] == "k"
            return httpx.Response(200, json={"videos": [
                {"id": 1, "url": "https://www.pexels.com/video/visa-card-logo-1/", "tags": [], "duration": 8,
                 "user": {"name": "Logo Person"}, "video_files": [{"file_type": "video/mp4", "width": 1080, "link": "https://cdn/1.mp4"}]},
                {"id": 2, "url": "https://www.pexels.com/video/groceries-2/", "tags": ["groceries"], "duration": 9,
                 "user": {"name": "Ana Lima", "url": "https://pexels.com/@ana"},
                 "video_files": [{"file_type": "video/mp4", "width": 1080, "link": "https://cdn/2.mp4"},
                                 {"file_type": "video/mp4", "width": 540, "link": "https://cdn/2-small.mp4"}]}]})
        if str(req.url).startswith("https://cdn/"):
            return httpx.Response(200, content=b"mp4:" + str(req.url).encode())
        return httpx.Response(404)
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_apply_downloads_credits_and_skips_logos(factory, monkeypatch):
    monkeypatch.setenv("PEXELS_API_KEY", "k")
    monkeypatch.delenv("PIXABAY_API_KEY", raising=False)
    pid = factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "in_review", "title": "t",
                                      "caption": "", "script": {"title": "t", "segments": _segs(6), "description": "About."},
                                      "hashtags": [], "disclosure": "", "meta": {}, "assets": {}})
    res = stock.apply(factory, pid, client=_client())
    assert res["added"] == [2, 4]
    post = factory.db.get("posts", pid)
    seg = post["script"]["segments"][1]
    clip = factory.settings.home / seg["broll"]
    assert clip.read_bytes() == b"mp4:https://cdn/2.mp4"  # logo clip skipped, smallest 720p+ file chosen
    side = json.loads(clip.with_suffix(".json").read_text())
    assert side["author"] == "Ana Lima" and "Pexels License" in side["license"]
    assert post["script"]["description"].endswith("B-roll: Pexels (pexels.com): Ana Lima")
    assert (factory.settings.output_dir / "money-made-simple" / f"post-{pid}" / "credits.json").is_file()
    # applying again doesn't stack credit lines or exceed 1 in 3
    stock.apply(factory, pid, client=_client())
    post = factory.db.get("posts", pid)
    assert post["script"]["description"].count("B-roll:") <= 1
    assert sum(1 for s in post["script"]["segments"] if s.get("broll")) == 2
    # stock never counts as an original element
    from contentfactory.originality import _element
    assert _element({**post["script"], "original_element": ""}, factory.settings.home) == "none"


def test_no_key(factory, monkeypatch):
    for k in ("PEXELS_API_KEY", "PIXABAY_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    pid = factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "in_review", "title": "t",
                                      "caption": "", "script": {"title": "t", "segments": _segs(6)}, "hashtags": [],
                                      "disclosure": "", "meta": {}, "assets": {}})
    with pytest.raises(stock.StockError):
        stock.apply(factory, pid)
