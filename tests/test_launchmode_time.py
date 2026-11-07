from datetime import date, datetime, timedelta, timezone

from contentfactory import launchmode, scorecard, timelog


def test_time_log_and_streak(factory):
    today = date(2026, 12, 30)
    mon = timelog.week_start(today)
    for k in range(1, 5):
        for d in range(7):
            timelog.log(factory, 50, "routine", day=mon - timedelta(weeks=k) + timedelta(days=d))
        timelog.log(factory, 200, "ad-studio", day=mon - timedelta(weeks=k))  # not counted against the brands
    ok, why = timelog.streak_ok(factory, 4, today)
    assert ok, why
    timelog.log(factory, 400, "recording", day=mon - timedelta(weeks=2))
    ok, why = timelog.streak_ok(factory, 4, today)
    assert not ok and "limit 420" in why
    text = timelog.to_text(timelog.weeks(factory, 3, today))
    assert "OVER" in text and "ad-studio" in text
    import pytest
    with pytest.raises(ValueError):
        timelog.log(factory, 10, "napping")


def test_launch_mode_filters(factory, capsys):
    from contentfactory.cli import main
    assert launchmode.active_brands(factory) is None
    data = launchmode.set_mode(factory, "two-brand")
    assert data["brands"] == ["money-made-simple", "scam-decoded"]
    missing = [b for b in data["brands"] if b not in factory.brands()]
    assert ("note" in data) == bool(missing) and all(b in data.get("note", "") for b in missing)
    assert launchmode.in_play(factory, "money-made-simple") and not launchmode.in_play(factory, "tiny-histories")
    main(["--home", str(factory.settings.home), "launch-mode"])
    assert "Left out" in capsys.readouterr().out
    main(["--home", str(factory.settings.home), "scorecard"])
    out = capsys.readouterr().out
    assert "money-made-simple" in out and "tiny-histories" not in out
    # today leaves the paused brand's review items out
    pid = factory.db.insert("posts", {"brand": "tiny-histories", "format": "short", "status": "in_review", "title": "Paused",
                                      "caption": "", "script": {}, "hashtags": [], "disclosure": "", "meta": {}, "assets": {}})
    from contentfactory.routine import collect, to_text
    r = collect(factory, date.today(), cap=False)
    assert all(i.brand != "tiny-histories" for i in r["review"]) and "launch mode" in to_text(r)
    launchmode.set_mode(factory, "all")
    r = collect(factory, date.today(), cap=False)
    assert any(f"#{pid}" in i.what for i in r["review"])


def test_gate(factory, monkeypatch):
    monkeypatch.setenv("FACTORY_LAUNCH_DATE", "2026-11-16")
    day = date(2027, 1, 13)  # day 58
    mon = day - timedelta(days=day.weekday())
    for k in range(1, 5):
        for d in range(7):
            timelog.log(factory, 40, day=mon - timedelta(weeks=k) + timedelta(days=d))
    gates = scorecard.gate(factory, ["money-made-simple"], day)
    names = {g["gate"].split(":")[0]: g for g in gates}
    assert names["time"]["ok"]
    assert not names["clean accounts"]["ok"]       # no weekly warning answers recorded
    assert not names["a queue"]["ok"] and not names["owned audience"]["ok"]
    text = scorecard.gate_text(gates, ["money-made-simple"], 58)
    assert "[PASS] time" in text and "Not yet" in text and "Too early" not in text
    assert (factory.settings.home / "data" / "scorecard-history" / f"{mon}-money-made-simple.json").is_file()
