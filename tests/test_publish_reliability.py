from datetime import datetime, timedelta, timezone

import httpx
import pytest

import contentfactory.publish as pubmod


class _Res:
    def __init__(self, n):
        self.remote_id, self.url, self.raw = f"r{n}", f"https://x/{n}", {}


@pytest.fixture
def scheduled(factory, fake_render):
    idea = factory.ideas("money-made-simple", n=2, online=False)[0]
    pid = factory.produce(idea)
    factory.approve(pid)
    pubs = factory.schedule(pid)
    return pid, pubs


def _use(monkeypatch, factory, fn):
    monkeypatch.setenv("MANUAL_PLATFORMS", "")  # these tests are about API publishers

    class P:
        def __init__(self, platform):
            self.platform = platform

        def publish(self, req):
            return fn(self.platform)
    factory.settings.dry_run = False
    monkeypatch.setattr(pubmod, "get_publisher", lambda platform, settings, dry_run=None: P(platform))
    monkeypatch.setattr("contentfactory.publish.tokens.refresh_long_lived", lambda s: None)
    monkeypatch.setattr("contentfactory.publish.tokens.refresh_tiktok_if_needed", lambda s: None)


def test_unexpected_error_never_leaves_publication_stuck(factory, scheduled, monkeypatch):
    pid, pubs = scheduled
    _use(monkeypatch, factory, lambda p: (_ for _ in ()).throw(KeyError("caption")))
    later = datetime.now(timezone.utc) + timedelta(days=30)
    res = factory.publish_due(later)
    assert res and all(r["status"] == "failed" and not r["retry"] for r in res)
    assert {p["status"] for p in factory.db.query("SELECT status FROM publications")} == {"failed"}


def test_network_error_retries_with_backoff(factory, scheduled, monkeypatch):
    pid, pubs = scheduled
    _use(monkeypatch, factory, lambda p: (_ for _ in ()).throw(httpx.ConnectError("down")))
    later = datetime.now(timezone.utc) + timedelta(days=30)
    assert all(r["retry"] for r in factory.publish_due(later))
    assert factory.publish_due(later) == []                      # backed off
    pub = factory.db.get("publications", pubs[0])
    assert pub["status"] == "queued" and pub["scheduled_at"] > later.isoformat()


def test_never_publishes_same_post_twice_on_a_platform(factory, scheduled, monkeypatch):
    pid, pubs = scheduled
    n = iter(range(100))
    _use(monkeypatch, factory, lambda p: _Res(next(n)))
    later = datetime.now(timezone.utc) + timedelta(days=30)
    first = factory.publish_due(later)
    assert first and all(r["status"] == "published" for r in first)
    dup = factory.db.get("publications", pubs[0])
    factory.db.insert("publications", {"post_id": pid, "platform": dup["platform"], "status": "queued",
                                       "scheduled_at": later.isoformat(), "created_at": later.isoformat()})
    assert factory.publish_due(later + timedelta(minutes=1)) == []
    assert factory.db.scalar("SELECT COUNT(*) FROM publications WHERE status='cancelled'") == 1


def test_interrupted_publish_is_flagged_not_retried(factory, scheduled):
    pid, pubs = scheduled
    factory.db.execute("UPDATE publications SET status='publishing', updated_at='2000-01-01T00:00:00+00:00' "
                       "WHERE id = ?", [pubs[0]])
    assert factory.flag_interrupted() == 1
    assert factory.db.get("publications", pubs[0])["status"] == "needs_check"



def test_needs_check_resolution_from_dashboard(factory, scheduled):
    from fastapi.testclient import TestClient

    from contentfactory.web.app import create_app
    pid, pubs = scheduled
    factory.db.execute("UPDATE publications SET status='needs_check' WHERE id = ?", [pubs[0]])
    factory.settings.dashboard_token = "t"
    c = TestClient(create_app(factory), client=("203.0.113.9", 4000), headers={"Authorization": "Bearer t"},
                   follow_redirects=False)
    page = c.get("/").text
    assert "interrupted mid-upload" in page and f"/publications/{pubs[0]}/resolve" in page
    r = c.post(f"/publications/{pubs[0]}/resolve", data={"action": "live", "url": "https://ig/p/1"},
               headers={"Origin": "http://testserver"})
    assert r.status_code in (302, 303)
    pub = factory.db.get("publications", pubs[0])
    assert pub["status"] == "published" and pub["url"] == "https://ig/p/1"
    with pytest.raises(ValueError):
        factory.resolve_publication(pubs[0], "requeue")


def test_requeue_failed_publication(factory, scheduled):
    pid, pubs = scheduled
    factory.db.execute("UPDATE publications SET status='failed', attempts=3 WHERE id = ?", [pubs[0]])
    factory.resolve_publication(pubs[0], "requeue")
    pub = factory.db.get("publications", pubs[0])
    assert pub["status"] == "queued" and pub["attempts"] == 0


def test_backlog_after_downtime_is_spread_out_not_dumped(factory, scheduled, monkeypatch):
    monkeypatch.setenv("PUBLISH_LATE_HOURS", "6")
    pid, pubs = scheduled
    sched = datetime.fromisoformat(factory.db.get("publications", pubs[0])["scheduled_at"])
    on_time = factory.publish_due(sched + timedelta(hours=1))
    assert on_time and on_time[0]["status"] == "dry_run"                 # an hour late is fine
    pid2 = factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "scheduled",
                                       "title": "late"})
    late = factory.db.insert("publications", {"post_id": pid2, "platform": "youtube", "status": "queued",
                                              "scheduled_at": sched.isoformat(), "created_at": "x"})
    res = factory.publish_due(sched + timedelta(days=2))
    assert [r["status"] for r in res if r["publication"] == late] == ["rescheduled"]
    assert factory.db.get("publications", late)["scheduled_at"] > (sched + timedelta(days=2)).isoformat()
