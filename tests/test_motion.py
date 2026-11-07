from pathlib import Path

import pytest

from contentfactory.media import motion

SEGS = [{"heading": "Hook", "narration": "You pay $1,200 a year", "on_screen_text": "$1,200 a year"},
        {"heading": "Why", "narration": "Fees add up", "on_screen_text": "Fees add up"},
        {"heading": "Rate", "narration": "Most banks pay 0.4%", "on_screen_text": "0.4% at big banks"},
        {"heading": "Next", "narration": "Online banks pay 4%", "on_screen_text": "4% online"},
        {"heading": "Chart", "narration": "Over 10 years", "on_screen_text": "10 years", "chart": {"kind": "bar"}},
        {"heading": "So", "narration": "Move $500 today", "on_screen_text": "Move $500 today"},
        {"heading": "Do", "narration": "Open one", "on_screen_text": "Open one"},
        {"heading": "End", "narration": "Follow", "on_screen_text": "Follow"}]


def test_pick_beats_rules():
    # 8 beats -> max 2; never the hook, never a chart, never adjacent
    assert motion.pick_beats(SEGS) == [2, 5]
    assert motion.the_number(SEGS[2]) == "0.4%"
    segs = [dict(s) for s in SEGS]
    segs[2]["broll"] = "footage/x.mp4"
    assert 2 not in motion.pick_beats(segs)


def test_composition_is_safe_html():
    page = motion.composition("$1,200", "$1,200 <a year>", ["#111111", "#ffffff", "#00ffaa"], portrait=True)
    assert 'data-width="1080"' in page and 'data-height="1920"' in page
    assert "&lt;a year&gt;" in page and "<a year>" not in page
    assert 'window.__timelines["main"]' in page and "Date.now" not in page and "fetch(" not in page


def test_apply_with_fake_render(factory, monkeypatch):
    monkeypatch.setenv("FACTORY_MOTION", "hyperframes")
    pid = factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "in_review",
                                      "title": "Fees", "caption": "c", "script": {"title": "Fees", "segments": SEGS},
                                      "hashtags": [], "disclosure": "", "meta": {}, "assets": {}})
    calls = []

    def fake_run(cmd, cwd, env, **kw):
        calls.append((cmd, env))
        (Path(cwd) / "card.mp4").write_bytes(b"mp4")
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
    res = motion.apply(factory, pid, run=fake_run, check_tools=False)
    assert res == {"added": [3, 6], "errors": []}
    cmd, env = calls[0]
    assert cmd[:3] == ["npx", "--yes", "hyperframes@0.9.19"] and "render" in cmd and "publish" not in cmd
    assert env["HYPERFRAMES_NO_TELEMETRY"] == "1"
    post = factory.db.get("posts", pid)
    seg = post["script"]["segments"][2]
    assert seg["motion"].endswith("card.mp4") and (factory.settings.home / seg["motion"]).is_file()
    assert post["meta"]["motion_cards"][0]["tool"] == "hyperframes@0.9.19"
    # nothing left to add the second time
    assert motion.apply(factory, pid, run=fake_run, check_tools=False)["added"] == []


def test_off_by_default_and_version_pinned(factory, monkeypatch):
    monkeypatch.delenv("FACTORY_MOTION", raising=False)
    with pytest.raises(motion.MotionError):
        motion.apply(factory, 1, check_tools=False)
    monkeypatch.setenv("HYPERFRAMES_VERSION", "latest")
    with pytest.raises(motion.MotionError):
        motion.version()
