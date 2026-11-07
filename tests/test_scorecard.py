from datetime import date

import yaml

from contentfactory import scorecard as sc


def _yt(f, impressions, ctr, views=100, n=3):
    from contentfactory.stats import ensure_schema
    ensure_schema(f.db)
    for k in range(n):
        f.db.insert("analytics_rows", {"brand": "money-made-simple", "platform": "youtube", "import_id": "2026-12-01",
                                       "title": f"v{k}", "views": views, "watch_hours": 5.0, "impressions": impressions // n,
                                       "ctr": ctr, "subscribers": 2, "imported_at": "2026-12-01T00:00:00"})
    for k in range(12):
        f.db.insert("analytics_rows", {"brand": "money-made-simple", "platform": "tiktok", "import_id": "2026-12-01",
                                       "title": f"t{k}", "views": 150, "imported_at": "2026-12-01T00:00:00"})
    f.db.insert("site_stats", {"brand": "money-made-simple", "import_id": "2026-12-01", "kind": "visitors", "value": 300,
                               "imported_at": "2026-12-01T00:00:00"})
    f.db.insert("site_stats", {"brand": "money-made-simple", "import_id": "2026-12-01", "kind": "goal", "name": "Signup",
                               "value": 3, "imported_at": "2026-12-01T00:00:00"})


def test_scorecard_flags(factory, monkeypatch):
    monkeypatch.setenv("FACTORY_LAUNCH_DATE", "2026-11-10")
    _yt(factory, 3000, 1.5)
    early = sc.collect(factory, "money-made-simple", date(2026, 11, 12))  # day 2: only stop rules
    assert not [f for f in early["flags"] if f.status == "flag"]
    c = sc.collect(factory, "money-made-simple", date(2026, 12, 2))  # day 22
    hit = {f.rule for f in c["flags"] if f.status == "flag"}
    assert "YouTube CTR < 2% (after 1,000 impressions)" in hit
    assert "site sign-ups < 2% (after 200 visitors)" in hit  # 1%
    assert "TikTok avg < 200 views (after 10+ posts)" in hit
    assert "YouTube < 50 watch hours" in hit
    text = sc.to_text(c)
    assert "impressions 3,000" in text and "CTR 1.5%" in text and "Day since launch: 22" in text
    assert "[CHANGE (one fix this week)] YouTube CTR" in text and "Not yet" in text

    p = sc.template(factory)
    data = yaml.safe_load(p.read_text())
    assert "email" in data["money-made-simple"]
    data["money-made-simple"]["email"]["bounces_pct"] = 3
    data["money-made-simple"]["warnings"]["any_warning"] = False
    data["money-made-simple"]["notes"]["one_change"] = "Shorter hooks"
    p.write_text(yaml.safe_dump(data))
    c = sc.collect(factory, "money-made-simple", date(2026, 12, 12))  # day 32
    stop = [f for f in c["flags"] if f.status == "flag" and f.severity == "stop"]
    assert [f.rule for f in stop] == ["email bounces > 2%"]
    assert any(f.severity == "go" for f in c["flags"])
    text = sc.to_text(c)
    assert "Shorter hooks" in text and "N\n" in text.replace("  N", " N")


def test_cli_blank(factory, capsys):
    from contentfactory.cli import main
    main(["scorecard", "--brand", "money-made-simple"])
    out = capsys.readouterr().out
    assert "YouTube    impressions ____" in out and "No flags" in out
