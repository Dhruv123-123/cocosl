from datetime import datetime, timezone

from contentfactory.worker import Worker, read_heartbeat


def _worker(factory, **kw):
    w = Worker(factory, **kw)
    calls = {"daily": [], "publish": 0}
    factory.daily = lambda slug, n_ideas=8, n_produce=2, online=True: calls["daily"].append((slug, n_produce)) or {}
    factory.publish_due = lambda now: calls.__setitem__("publish", calls["publish"] + 1) or []
    factory.collect_metrics = lambda: 0
    w.run_sequences = lambda now: None
    w.collect_comments = lambda: None
    return w, calls


def test_each_brand_runs_daily_once_on_its_own_clock(factory):
    brands = factory.brands()
    assert len(brands) >= 2
    slugs = list(brands)[:2]
    brands = {s: brands[s] for s in slugs}  # the test is about two clocks; ignore any other brands
    brands[slugs[0]].cadence.timezone = "America/New_York"
    brands[slugs[1]].cadence.timezone = "Europe/London"
    brands[slugs[1]].cadence.daily_drafts = 1
    factory.brands = lambda: brands
    factory.brand = lambda s: brands[s]
    w, calls = _worker(factory)
    # 08:00 UTC Tuesday: 08:00 London (due), 03:00 New York (not yet)
    t1 = datetime(2026, 11, 10, 8, 0, tzinfo=timezone.utc)
    assert w.tick(t1)["daily"] == [slugs[1]]
    assert calls["daily"] == [(slugs[1], 1)]
    assert "daily" not in w.tick(t1.replace(minute=30))               # not twice the same day
    t2 = datetime(2026, 11, 10, 12, 30, tzinfo=timezone.utc)          # 07:30 New York
    assert w.tick(t2)["daily"] == [slugs[0]]
    # a restarted worker remembers (audit log), so no rerun
    w2, calls2 = _worker(factory)
    assert "daily" not in w2.tick(t2)
    assert read_heartbeat(factory)["at"] == t2.isoformat()


def test_paused_brand_is_skipped_and_failures_are_isolated(factory):
    brands = factory.brands()
    slugs = list(brands)
    for b in brands.values():
        b.cadence.timezone = "UTC"
    brands[slugs[0]].cadence.paused = True
    factory.brands = lambda: brands
    factory.brand = lambda s: brands[s]
    w, calls = _worker(factory)

    def broken(now):
        raise RuntimeError("platform down")
    factory.publish_due = broken
    ran = w.tick(datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc))
    assert ran["daily"] == slugs[1:]                                    # paused brand skipped, rest still ran
    assert "platform down" in w.errors["publish"]
    assert "platform down" in read_heartbeat(factory)["errors"]["publish"]


def test_weekly_report_on_monday_once(factory):
    brands = factory.brands()
    for b in brands.values():
        b.cadence.timezone = "UTC"
    factory.brands = lambda: brands
    factory.brand = lambda s: brands[s]
    w, _ = _worker(factory)
    monday = datetime(2026, 11, 9, 8, 0, tzinfo=timezone.utc)
    assert "report" in w.tick(monday)
    assert "report" not in w.tick(monday.replace(hour=9))
    assert "report" not in w.tick(datetime(2026, 11, 10, 8, 0, tzinfo=timezone.utc))


def test_status_reports_alerts(factory):
    from fastapi.testclient import TestClient

    from contentfactory.health import system_status
    from contentfactory.web.app import create_app
    st = system_status(factory)
    assert any("never run" in a for a in st["alerts"])
    w, _ = _worker(factory)
    w.tick(datetime.now(timezone.utc))
    assert not any("never run" in a for a in system_status(factory)["alerts"])
    factory.settings.dashboard_token = "t"
    c = TestClient(create_app(factory), client=("203.0.113.9", 4000), headers={"Authorization": "Bearer t"})
    body = c.get("/api/status").json()
    assert "render_queue" in body and "publications" in body


def test_status_flags_missing_media_and_disconnected_platform(factory, fake_render):
    from contentfactory.health import system_status
    idea = factory.ideas("money-made-simple", n=2, online=False)[0]
    pid = factory.produce(idea)
    factory.approve(pid)
    factory.schedule(pid)
    assert not any("media files are missing" in a for a in system_status(factory)["alerts"])
    post = factory.db.get("posts", pid)
    f = post["assets"].get("video") or post["assets"]["slides"][0]
    (factory.settings.output_dir / f).unlink()
    assert any("media files are missing" in a for a in system_status(factory)["alerts"])
    factory.settings.dry_run = False
    assert any("isn't connected" in a for a in system_status(factory)["alerts"])
