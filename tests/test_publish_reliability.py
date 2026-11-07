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

