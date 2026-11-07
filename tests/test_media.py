"""Offline media rendering: silent TTS + Pillow 'cards' art + ffmpeg."""
from __future__ import annotations

import shutil
import subprocess

import pytest

from contentfactory.config import Settings, load_brand
from contentfactory.media import render_post
from contentfactory.media.captions import chunk_words, time_segment
from contentfactory.media.util import probe

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
                                reason="ffmpeg/ffprobe required")

SEGMENTS = [
    ("Hook", "Your savings account is probably paying you almost nothing.", "Your bank is underpaying you",
     "a piggy bank on a sunny shelf"),
    ("Why", "High yield accounts often pay far more, with the same deposit insurance.", "Same safety, better rate",
     "coins growing like plants"),
    ("Do it", "Compare three banks tonight and move your emergency fund.", "Move it tonight",
     "a calendar and a checklist"),
    ("Watch out", "Rates change, so check yours every few months.", "Rates move. Check them.",
     "a small boat on calm water"),
    ("Recap", "Better rate, same safety, ten minutes of work.", "Ten minutes, real money", "a sunrise over hills"),
]


def make_post(post_id: int, fmt: str, n: int) -> dict:
    segs = [dict(heading=h, narration=t, on_screen_text=o, visual_prompt=v) for h, t, o, v in SEGMENTS[:n]]
    script = dict(title="Stop letting your bank underpay you", hook=segs[0]["narration"], segments=segs,
                  cta="Follow for one money move a week.", caption="cap", hashtags=["money"], description="d",
                  thumbnail_text="Your bank underpays you", sources=[], claims_to_verify=[])
    return {"id": post_id, "format": fmt, "title": script["title"], "script": script}


@pytest.fixture
def media_env(home, monkeypatch):
    for key in ("OPENAI_API_KEY", "ELEVENLABS_API_KEY", "REPLICATE_API_TOKEN", "COMFYUI_URL", "PIPER_MODEL", "KOKORO_URL",
                "OPENAI_TTS_BASE_URL",
                "FACTORY_MUSIC_DIR"):
        monkeypatch.delenv(key, raising=False)
    settings = Settings.load(home)
    settings.extra.update(video_fps=12, x264_preset="ultrafast", render_workers=4)
    return settings, load_brand(settings.brands_dir, "money-made-simple")


def _check_provenance(assets: dict, settings) -> None:
    files = [assets[k] for k in ("video", "audio", "captions_srt", "thumbnail") if assets.get(k)]
    files += assets["images"] + assets["slides"]
    covered = {p["path"] for p in assets["provenance"]}
    for rel in files:
        assert not rel.startswith("/"), rel
        assert (settings.output_dir / rel).is_file(), rel
        assert rel in covered, f"no provenance for {rel}"
    for rel in assets["slides"] + ([assets["thumbnail"]] if assets.get("thumbnail") else []):
        jpg = rel[:-4] + ".jpg"
        assert (settings.output_dir / jpg).is_file() and jpg in covered, f"missing JPEG twin for {rel}"
    assert all(p["source"] in ("generated", "rendered", "own", "licensed") for p in assets["provenance"])


@pytest.mark.parametrize("fmt,size", [("short", (1080, 1920)), ("long", (1920, 1080))])
def test_render_video(media_env, tmp_path, fmt, size):
    settings, brand = media_env
    assets = render_post(settings, brand, make_post(1, fmt, 3))
    _check_provenance(assets, settings)
    info = probe(settings.output_dir / assets["video"])
    assert (info["width"], info["height"]) == size
    assert set(info["streams"]) == {"video", "audio"}
    # 3 lines + CTA at 160 wpm, each beat >= 1.5s plus gaps
    assert 8 < info["duration"] < 25
    assert abs(info["duration"] - assets["duration"]) < 0.5
    assert len(assets["images"]) == 3 and assets["slides"] == []
    assert probe(settings.output_dir / assets["thumbnail"])["width"] == 1280
    srt = (settings.output_dir / assets["captions_srt"]).read_text()
    assert "Follow for one" in srt and "-->" in srt
    video_prov = next(p for p in assets["provenance"] if p["path"] == assets["video"])
    assert video_prov["tool"] == "ffmpeg"
    assert not (settings.output_dir / brand.slug / "post-1" / "_work").exists()
    frame = tmp_path / "frame.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", str(settings.output_dir / assets["video"]),
                    "-frames:v", "1", str(frame)], check=True)
    from PIL import Image, ImageStat
    assert ImageStat.Stat(Image.open(frame).convert("L")).stddev[0] > 10  # real picture, not a flat colour


def test_render_carousel(media_env):
    settings, brand = media_env
    assets = render_post(settings, brand, make_post(3, "carousel", 5))
    _check_provenance(assets, settings)
    assert len(assets["slides"]) == 5 and len(assets["images"]) == 5
    assert assets["video"] is None and assets["duration"] == 0.0
    from PIL import Image
    for rel in assets["slides"]:
        assert Image.open(settings.output_dir / rel).size == (1080, 1350)


def test_render_image_post(media_env):
    settings, brand = media_env
    assets = render_post(settings, brand, make_post(4, "image", 1))
    _check_provenance(assets, settings)
    assert len(assets["slides"]) == 1
    from PIL import Image
    assert Image.open(settings.output_dir / assets["slides"][0]).size == (1080, 1350)


def test_auto_falls_through_and_is_deterministic(media_env, monkeypatch):
    settings, brand = media_env
    settings.image_provider = "auto"
    monkeypatch.setenv("COMFYUI_URL", "http://127.0.0.1:9")  # nothing listens here
    a = render_post(settings, brand, make_post(5, "image", 1))
    img = next(p for p in a["provenance"] if p["path"] == a["images"][0])
    assert img["provider"] == "cards" and "comfyui failed" in img["note"]
    first = (settings.output_dir / a["images"][0]).read_bytes()
    b = render_post(settings, brand, make_post(5, "image", 1))  # re-render replaces the folder
    assert (settings.output_dir / b["images"][0]).read_bytes() == first


def test_caption_chunking():
    chunks = chunk_words("Compare three banks tonight, and move your emergency fund before Friday.")
    assert all(2 <= len(c) <= 5 for c in chunks)
    cues = time_segment("one two three four five six seven", 2.0, 3.5)
    assert cues[0].start == 2.0 and abs(cues[-1].end - 5.5) < 1e-6


def test_string_id_and_output_subdir(media_env):
    settings, brand = media_env
    post = make_post("order3-v1", "image", 1)
    a = render_post(settings, brand, post)
    assert a["slides"][0].startswith(f"{brand.slug}/post-order3-v1/")
    post["meta"] = {"output_subdir": "clients/acme/order3-v1"}
    b = render_post(settings, brand, post)
    assert b["slides"][0].startswith("clients/acme/order3-v1/")
    _check_provenance(b, settings)
    post["meta"] = {"output_subdir": "../escape"}
    with pytest.raises(Exception):
        render_post(settings, brand, post)


# --------------------------------------------------------------------------- Kokoro / OpenAI-compatible TTS
def _fake_speech(calls):
    import io
    import wave

    def handler(url, headers=None, json=None, timeout=None):
        calls.append({"url": url, "headers": headers or {}, "json": json})
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(b"\x00\x00" * 12000)
        import httpx
        return httpx.Response(200, content=buf.getvalue())
    return handler


def test_openai_tts_base_url_override(media_env, monkeypatch, tmp_path):
    from contentfactory.media import tts
    settings, brand = media_env
    settings.tts_provider = "openai"
    calls = []
    monkeypatch.setenv("OPENAI_TTS_BASE_URL", "http://tts.local:9000/v1")
    monkeypatch.setenv("OPENAI_TTS_MODEL", "tts-1")
    monkeypatch.setattr(tts.httpx, "post", _fake_speech(calls))
    res = tts.synthesize_segments(settings, brand, ["Hello there."], tmp_path / "b")
    assert calls[0]["url"] == "http://tts.local:9000/v1/audio/speech" and res.tool == "openai:tts-1"
    assert "Authorization" not in calls[0]["headers"]  # local server, no key needed
    monkeypatch.delenv("OPENAI_TTS_BASE_URL")
    with pytest.raises(tts.ProviderError):  # the real OpenAI endpoint still needs a key
        tts.OpenAITTS(settings, brand).speak("hi", tmp_path / "c.wav")
