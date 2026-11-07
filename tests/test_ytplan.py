import json

from contentfactory.ytplan import plan, run


def _item(fmt, title, pillar, words=""):
    return {"format": fmt, "pillar": pillar, "script": {"title": title, "hook": words, "segments": []}}


def test_plan_chains_end_screens_and_picks_related(factory):
    brand = factory.brand("money-made-simple")
    p0, p1 = brand.pillars[0], brand.pillars[1]
    items = [_item("long", "Build a budget in one evening", p0, "budget categories"),
             _item("long", "Sinking funds explained", p0, "sinking funds bills"),
             _item("long", "Index funds for beginners", p1, "index funds invest"),
             _item("short", "Name your sinking funds", p0, "sinking funds bills"),
             _item("short", "Your first index fund", p1, "index funds")]
    p = plan(brand, items)
    ends = {e["title"]: e["left_tile"] for e in p["end_screens"]}
    assert ends["Build a budget in one evening"] == "Sinking funds explained"
    assert ends["Sinking funds explained"].startswith("playlist:")
    rel = {s["title"]: s["related"] for s in p["shorts"]}
    assert rel == {"Name your sinking funds": "Sinking funds explained", "Your first index fund": "Index funds for beginners"}


def test_run_writes_plan_and_keeps_pack_formatting(factory):
    home = factory.settings.home
    pack = home / "launch" / "money-made-simple" / "content.json"
    pack.parent.mkdir(parents=True, exist_ok=True)
    brand = factory.brand("money-made-simple")
    items = [_item("long", "Sinking funds explained", brand.pillars[0], "sinking funds"),
             _item("short", "Name your sinking funds", brand.pillars[0], "sinking funds")]
    pack.write_text(json.dumps(items, indent=1) + "\n")
    out = run(home, brand, [pack], write=True)
    md = out[0].read_text()
    assert "| Name your sinking funds | Sinking funds explained |" in md and "End screen layout" in md
    text = pack.read_text()
    assert text.splitlines()[1] == " {" and json.loads(text)[1]["script"]["related_video"] == "Sinking funds explained"


def test_shorts_title_limit_in_launch_check(factory):
    from datetime import datetime, timedelta, timezone
    from contentfactory.launch_check import run as check
    pid = factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "scheduled",
                                      "title": "x" * 61, "caption": "Made with AI tools.", "script": {"title": "x" * 61},
                                      "hashtags": [], "disclosure": "", "meta": {}, "assets": {}})
    factory.db.insert("publications", {"post_id": pid, "platform": "youtube", "status": "queued",
                                       "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()})
    assert any("Shorts title 61 chars" in f.message for f in check(factory).findings)


def test_end_slate_image(tmp_path):
    from PIL import Image
    from contentfactory.media.endslate import render_end_slate
    from contentfactory.media.util import Palette
    pal = Palette(dark=(10, 20, 15), light=(245, 240, 230), accents=[(47, 191, 113)])
    out = render_end_slate((1920, 1080), pal, "Inter", "Money Made Simple", "@mms", None, tmp_path / "s.png")
    assert Image.open(out).size == (1920, 1080) and out.with_suffix(".jpg").exists()
