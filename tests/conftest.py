import os
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def home(tmp_path, monkeypatch):
    """An isolated factory home with the example brands and offline providers."""
    for key in list(os.environ):
        if key.startswith(("FACTORY_", "IG_", "YT_", "TIKTOK_", "FB_", "THREADS_", "POSTIZ_")):
            monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("FACTORY_LLM", "offline")
    monkeypatch.setenv("FACTORY_TTS", "silent")
    monkeypatch.setenv("FACTORY_IMAGES", "cards")
    monkeypatch.setenv("FACTORY_DRY_RUN", "1")
    monkeypatch.setenv("PUBLISH_LATE_HOURS", "0")  # tests jump the clock ahead; the late guard has its own test
    monkeypatch.setenv("FACTORY_PREFLIGHT", "0")  # fake media; tests/test_preflight.py turns it on
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    shutil.copytree(ROOT / "brands", tmp_path / "brands")
    return tmp_path


@pytest.fixture
def factory(home):
    from contentfactory.config import Settings
    from contentfactory.pipeline import Factory
    return Factory.create(Settings.load(home))


@pytest.fixture
def fake_render(monkeypatch):
    """Skip real media rendering: write tiny placeholder files instead."""
    def _render(settings, brand, post):
        d = settings.output_dir / brand.slug / f"post-{post['id']}"
        d.mkdir(parents=True, exist_ok=True)
        unique = f"\x00{brand.slug}:{post['id']}".encode()  # real renders differ per post (Instagram repost check)
        (d / "video.mp4").write_bytes(unique)
        carousel = post.get("format") == "carousel"
        if carousel:
            (d / "slide-01.png").write_bytes(unique)
        return {"video": None if carousel else f"{brand.slug}/post-{post['id']}/video.mp4", "images": [],
                "slides": [f"{brand.slug}/post-{post['id']}/slide-01.png"] if carousel else [],
                "thumbnail": None, "audio": None, "captions_srt": None, "duration": 30.0,
                "provenance": [{"path": "video.mp4", "source": "rendered", "tool": "test", "prompt": "", "license": ""}]}
    import contentfactory.media.render as r
    import contentfactory.media as m
    monkeypatch.setattr(r, "render_post", _render)
    monkeypatch.setattr(m, "render_post", _render)
    return _render
