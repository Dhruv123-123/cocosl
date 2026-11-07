from datetime import timedelta

import pytest

from contentfactory import renderq


def _silent_assets(post_id):
    return {"video": f"b/post-{post_id}/video.mp4", "slides": [],
            "provenance": [{"path": f"b/post-{post_id}/audio.wav", "provider": "silent", "tool": "silent"}]}


@pytest.fixture
def silent_post(factory, fake_render):
    idea = factory.ideas("money-made-simple", n=3, online=False)
    pid = factory.produce(next(i for i in idea if factory.db.get("ideas", i)["format"] != "carousel"), render=False)
    factory.db.update("posts", pid, {"assets": _silent_assets(pid), "status": "in_review"})
    return pid


def test_revoice_waits_for_a_voice_then_renders(factory, silent_post, monkeypatch):
    monkeypatch.setattr(renderq, "voice_ready", lambda f, b: False)
    jobs = renderq.enqueue_unvoiced(factory)
    assert len(jobs) == 1
    assert renderq.enqueue_unvoiced(factory) == []          # no duplicates
    assert renderq.run(factory) == []                         # waits: no voice yet
    with pytest.raises(PermissionError):
        factory.approve(silent_post)                          # can't approve while queued
    monkeypatch.setattr(renderq, "voice_ready", lambda f, b: True)
    res = renderq.run(factory)
    assert [r["status"] for r in res] == ["done"]
    assert factory.db.get("posts", silent_post)["status"] == "in_review"
    assert renderq.status(factory)["done"] == 1
    factory.approve(silent_post)


def test_failed_render_retries_with_backoff_then_fails(factory, silent_post, monkeypatch):
    def boom(post_id):
        raise RuntimeError("ffmpeg exploded")
    monkeypatch.setattr(factory, "render", boom)
    renderq.enqueue(factory, silent_post, reason="manual")
    now = renderq._now()
    assert renderq.run_one(factory, now)["status"] == "retry"
    assert renderq.run_one(factory, now) is None              # backoff
    assert renderq.run_one(factory, now + timedelta(minutes=6))["status"] == "retry"
    assert renderq.run_one(factory, now + timedelta(minutes=20))["status"] == "failed"
    st = renderq.status(factory)
    assert st["failed"] == 1 and "ffmpeg exploded" in st["recent_failures"][0]["error"]


def test_scheduled_posts_are_never_rerendered(factory, silent_post):
    factory.db.update("posts", silent_post, {"status": "scheduled"})
    assert renderq.enqueue(factory, silent_post) is None
    assert renderq.enqueue_unvoiced(factory) == []


def test_stale_running_job_is_recovered(factory, silent_post):
    job = renderq.enqueue(factory, silent_post, reason="manual")
    factory.db.update("render_jobs", job, {"status": "running", "started_at": "2000-01-01T00:00:00+00:00"})
    assert renderq.recover_stale(factory) == 1
    assert factory.db.get("render_jobs", job)["status"] == "queued"


def test_render_queue_mode_defers_rendering(factory, fake_render, monkeypatch):
    monkeypatch.setenv("RENDER_QUEUE", "1")
    idea = factory.ideas("money-made-simple", n=2, online=False)[0]
    pid = factory.produce(idea)
    assert not (factory.db.get("posts", pid)["assets"] or {}).get("video")
    assert factory.render_pending(pid)
    monkeypatch.setattr(renderq, "voice_ready", lambda f, b: True)
    assert renderq.run(factory)[0]["status"] == "done"
    assert not factory.render_pending(pid)


def test_voice_ready_reflects_tts_setting(factory, monkeypatch):
    monkeypatch.setattr(factory.settings, "tts_provider", "silent")
    assert not renderq.voice_ready(factory, "money-made-simple")
    monkeypatch.setattr(factory.settings, "tts_provider", "kokoro")
    monkeypatch.setenv("KOKORO_URL", "http://kokoro:8880")
    assert renderq.voice_ready(factory, "money-made-simple")


def test_two_renderers_never_take_the_same_job(factory, silent_post, monkeypatch):
    from contentfactory.config import Settings
    from contentfactory.pipeline import Factory
    other = Factory.create(Settings.load(factory.settings.home))          # second process, same database file
    renderq.enqueue(factory, silent_post, reason="manual")
    now = renderq._now()
    a = renderq._claim(factory, now)
    b = renderq._claim(other, now)
    assert a is not None and b is None
