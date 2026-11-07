import json
from datetime import UTC, datetime, timedelta

from contentfactory import batch_record as br


def _post(f, fmt, title, segs, meta=None, days=None, **script_extra):
    script = {"title": title, "hook": "Opening line here.", "cta": "Follow for more.",
              "segments": segs, **script_extra}
    pid = f.db.insert("posts", {"brand": "money-made-simple", "format": fmt, "status": "approved", "title": title,
                                "caption": "", "script": script, "hashtags": [], "disclosure": "",
                                "meta": meta or {}, "assets": {}})
    if days is not None:
        at = (datetime.now(UTC) + timedelta(days=days)).isoformat()
        f.db.insert("publications", {"post_id": pid, "platform": "youtube", "status": "queued", "scheduled_at": at})
    return pid


def _seg(heading, narration, **kw):
    return {"heading": heading, "narration": narration, "on_screen_text": heading, "visual_prompt": "x", **kw}


def test_plan_sessions_and_attach(factory, tmp_path):
    words = " ".join(["word"] * 150)
    v = _post(factory, "short", "Voice short", [_seg("One", "Opening line here. Then more."), _seg("Two", words)],
              meta={"own_voice": True}, days=2)
    long = _post(factory, "long", "Budget app walkthrough",
                 [_seg("Intro", "Hello there."), _seg("Set up the budget app", "Open the budget app and add rent."),
                  _seg("Wrap", "That is it.")], days=5,
                 original_element="Screen recording: set up the budget app and add rent")
    later = _post(factory, "long", "Far future", [_seg("A", "x"), _seg("B", "y")], days=60,
                  original_element="Screen recording of the savings calculator")
    items = br.tasks(factory)
    kinds = {(t["post_id"], t["kind"]) for t in items}
    assert (v, "voice") in kinds and (long, "screen") in kinds and (later, "screen") in kinds
    voice = next(t for t in items if t["kind"] == "voice")
    assert voice["save_as"] == f"voice/money-made-simple/post-{v}.wav"
    assert voice["lines"][0] == "Opening line here. Then more."  # hook not read twice
    screen = next(t for t in items if t["post_id"] == long)
    assert screen["beat"] == 1 and screen["save_as"].endswith(f"post-{long}-beat2.mp4")
    assert all(t["post_id"] != later for t in br.tasks(factory, days=30))

    plan = br.sessions(items, minutes=45)
    assert [s["kind"] for s in plan][:2] == ["voice", "screen"]  # soonest first
    assert all(s["brand"] == "money-made-simple" for s in plan)
    small = br.sessions(items, minutes=1)  # splits when over the budget
    assert len([s for s in small if s["kind"] == "screen"]) == 2

    root = br.write(factory, plan)
    d = next(root.glob("session-02-*"))
    shot = (d / "SHOT_LIST.md").read_text()
    assert "Budget app walkthrough" in shot and "batch-record attach" in shot
    page = (d / "teleprompter.html").read_text()
    assert "Open the budget app and add rent." in page and "Mirror" in page
    assert (root / "README.md").read_text().count("| [") == len(plan)
    assert json.loads((d / "session.json").read_text())["tasks"]

    assert br.attach(factory, d) == []  # nothing recorded yet
    target = factory.settings.home / screen["save_as"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"fake")
    assert br.attach(factory, d) == [f"#{long} beat 2 ← {screen['save_as']}"]
    seg = factory.db.get("posts", long)["script"]["segments"][1]
    assert seg["footage"] == screen["save_as"]
    assert all(t["post_id"] != long for t in br.tasks(factory))  # no longer waiting


def test_cli_nothing(factory, capsys):
    from contentfactory.cli import main
    main(["batch-record"])
    assert "Nothing waiting" in capsys.readouterr().out
