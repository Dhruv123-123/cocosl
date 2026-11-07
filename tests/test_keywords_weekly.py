from datetime import date, datetime, timedelta, timezone

from contentfactory import keywords, weekly_review

SHEET = ("plan_day,source,format,current_title,target_phrase,second_phrase,title_fit,suggested_title,confirmed_in_autocomplete\n"
         "D1,c#0,short,The two-account trick that stops overdrafts,how to avoid overdraft fees,x,partial,"
         "Stop overdraft fees: the two-account trick,\n"
         "D2,c#6,short,Freeze your credit for free tonight,how to freeze your credit,credit freeze,match,keep,yes\n"
         "D3,c#1,short,\"Budget weekly, not monthly\",weekly budget,how to budget weekly,match,keep,\n"
         "D4,c#2,short,Not scheduled yet,sinking funds,x,match,keep,\n")


def _post(f, title, status="scheduled", when=None):
    pid = f.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": status, "title": title,
                                "caption": "Cap. Made with AI tools.", "script": {"title": title}, "hashtags": [],
                                "disclosure": "", "meta": {}, "assets": {}})
    if when:
        f.db.insert("publications", {"post_id": pid, "platform": "youtube", "status": "queued", "scheduled_at": when})
    return pid


def _sheet(f):
    d = f.settings.home / "research" / "scouting"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "keywords-mms-first-30.csv"
    p.write_text(SHEET)
    return p


def test_keyword_check(factory, capsys, monkeypatch):
    from contentfactory.cli import main
    p = _sheet(factory)
    soon = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    later = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    a = _post(factory, "The two-account trick that stops overdrafts", when=later)
    _post(factory, "Freeze your credit for free tonight", when=soon)
    b = _post(factory, "Budget weekly, not monthly!", when=soon)
    rows = keywords.load(factory)
    assert {r.brand for r in rows} == {"money-made-simple"} and len(rows) == 4
    todo = keywords.todo(rows)
    assert [r.ref for r in todo] == ["mms:3", "mms:1"]  # ticked and unscheduled rows left out, soonest first
    assert todo[0].posts[0]["id"] == b and todo[1].posts[0]["id"] == a
    assert len(keywords.todo(rows, everything=True)) == 3
    text = keywords.to_text(todo, rows)
    assert "title not updated yet" in text and 'type "how to avoid"' in text
    main(["--home", str(factory.settings.home), "keyword-check", "mark", "mms:1", "no", "--use", "avoid overdraft fee"])
    assert "no; use: avoid overdraft fee" in p.read_text()
    monkeypatch.setattr("builtins.input", lambda _: "y")
    main(["--home", str(factory.settings.home), "keyword-check", "go"])
    assert "1 marked" in capsys.readouterr().out
    assert keywords.todo(keywords.load(factory)) == []
    assert p.read_text().splitlines()[0].endswith("confirmed_in_autocomplete")


def test_keyword_check_no_sheets(factory, capsys):
    from contentfactory.cli import main
    main(["--home", str(factory.settings.home), "keyword-check"])
    assert "No keyword sheets" in capsys.readouterr().out


def test_weekly_review(factory, capsys, monkeypatch):
    from contentfactory import timelog
    from contentfactory.cli import main
    from contentfactory.worker import Worker
    _sheet(factory)
    day = date.today()
    when = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    _post(factory, "Budget weekly, not monthly", when=when)
    _post(factory, "Waiting", status="in_review")
    timelog.log(factory, 30, "routine", day=day)
    r = weekly_review.collect(factory, day)
    md = weekly_review.to_markdown(r)
    for part in ("1. Scorecard", "2. Time used", "3. Brand-3 gates", "4. Queued", "5. Blocked on you"):
        assert part in md
    assert "search-box check" in md and "under 2 weeks left" in md and "30 min on the brands" in md
    main(["--home", str(factory.settings.home), "weekly-review", "--save"])
    out = factory.settings.output_dir / "weekly-review"
    assert list(out.glob("*.md")) and "<h2>" in next(out.glob("*.html")).read_text()
    assert "Saved" in capsys.readouterr().out
    # the worker writes it on Sunday evening, once
    w = Worker(factory)
    sunday = datetime(2026, 11, 8, 23, 30, tzinfo=timezone.utc)
    assert w.weekly_review_due(sunday)
    w._mark("worker.weekly_review", "", sunday)
    assert not w.weekly_review_due(sunday + timedelta(minutes=5))
    assert not w.weekly_review_due(datetime(2026, 11, 9, 23, 30, tzinfo=timezone.utc))


def test_commands_doc_is_current():
    import subprocess
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run([sys.executable, str(root / "scripts" / "gen_commands.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
