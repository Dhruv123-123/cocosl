import shutil
import subprocess

import pytest

from contentfactory.media.looks import DIMENSIONS, choose


def test_choose_avoids_recent_looks():
    seen = []
    for i in range(6):
        look = choose(list(reversed(seen)), seed=i)
        if seen:
            assert sum(look[k] == seen[-1][k] for k in DIMENSIONS) == 0  # nothing shared with the last video
        assert look not in seen[-5:]
        seen.append(look)
    assert len({l["layout"] for l in seen[:3]}) == 3 and len({l["motion"] for l in seen[:3]}) == 3


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg required")
@pytest.mark.parametrize("look", [
    {"layout": "framed", "motion": "gentle", "captions": "box", "headline": "bar"},
    {"layout": "split", "motion": "cuts", "captions": "plain", "headline": "card"},
])
def test_render_with_each_layout(home, monkeypatch, tmp_path, look):
    from contentfactory.config import Settings, load_brand
    from contentfactory.media import render_post
    from contentfactory.media.util import probe
    from tests.test_media import make_post
    settings = Settings.load(home)
    settings.extra.update(video_fps=12, x264_preset="ultrafast", render_workers=4)
    brand = load_brand(settings.brands_dir, "money-made-simple")
    for fmt in ("short", "long"):
        post = make_post(20 if fmt == "short" else 21, fmt, 2)
        post["look"] = look
        assets = render_post(settings, brand, post)
        assert assets["look"] == look and probe(settings.output_dir / assets["video"])["duration"] > 3


def test_sameness_warns_on_template_channel(factory):
    from contentfactory.guardrails import check_sameness
    db = factory.db
    seg = {"heading": "h", "narration": "n", "on_screen_text": "o", "visual_prompt": "v"}

    def add(i, title, hook, beats=6):
        return db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "published",
                                   "title": title, "script": {"title": title, "hook": hook, "segments": [seg] * beats},
                                   "assets": {"look": {"layout": "full", "motion": "kenburns"}}})
    for i in range(8):
        add(i, f"{i + 3} ways to save on groceries", f"Stop wasting {i * 10} dollars a week")
    new = {"id": 999, "format": "short", "script": {"title": "5 ways to cut your phone bill",
           "hook": "Stop wasting 40 dollars a month", "segments": [seg] * 6},
           "assets": {"look": {"layout": "full", "motion": "kenburns"}}}
    c = check_sameness(db, "money-made-simple", new)
    assert c.level == "warn" and "title" in c.message
    different = {"id": 998, "format": "short", "script": {"title": "Why your bank pays you nothing",
                 "hook": "Your savings account has a secret", "segments": [seg] * 9},
                 "assets": {"look": {"layout": "split", "motion": "cuts"}}}
    assert check_sameness(db, "money-made-simple", different).level == "ok"
