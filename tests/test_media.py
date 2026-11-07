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
    for key in ("OPENAI_API_KEY", "ELEVENLABS_API_KEY", "REPLICATE_API_TOKEN", "COMFYUI_URL", "PIPER_MODEL",
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


@pytest.mark.parametrize("fmt,size", [("short", (1080, 1920)), ("mid", (1080, 1920)), ("long", (1920, 1080))])
def test_render_video(media_env, tmp_path, fmt, size):
    settings, brand = media_env
    assets = render_post(settings, brand, make_post(1, fmt, 3))
    _check_provenance(assets, settings)
    info = probe(settings.output_dir / assets["video"])
    assert (info["width"], info["height"]) == size
    assert set(info["streams"]) == {"video", "audio"}
    # 3 lines + CTA at 160 wpm, each beat >= 1.5s plus gaps
    slate = assets.get("end_slate_seconds") or 0
    assert slate == (20 if fmt == "long" else 0)  # long videos close on a slate for the Studio end screen
    assert 8 < info["duration"] - slate < 25
    assert abs(info["duration"] - assets["duration"]) < 0.5
    assert len(assets["images"]) == 3 and assets["slides"] == []
    assert probe(settings.output_dir / assets["thumbnail"])["width"] == 1280
    if fmt == "long":
        variants = assets["thumbnail_variants"]
        assert len(variants) == 3 and variants[0] == assets["thumbnail"]
        assert all((settings.output_dir / v).is_file() and (settings.output_dir / v[:-4]).with_suffix(".jpg").is_file()
                   for v in variants)
        tc = assets["test_compare"]  # A/B/C for YouTube Test & compare
        assert [p.rsplit("/", 1)[1] for p in tc] == ["A.jpg", "B.jpg", "C.jpg"]
        assert all((settings.output_dir / p).stat().st_size < 2 * 1024 * 1024 for p in tc)
        from PIL import Image as _I
        a, b = (_I.open(settings.output_dir / tc[i]).convert("L").resize((64, 36)) for i in (0, 1))
        assert sum(abs(x - y) for x, y in zip(a.getdata(), b.getdata())) / (64 * 36) > 8  # visibly different
    srt = (settings.output_dir / assets["captions_srt"]).read_text()
    assert "Follow for one" in srt and "-->" in srt
    if slate:  # no captions run into the end slate
        import re as _re
        ends = [sum(float(x) * m for x, m in zip(_re.split("[:,]", t)[:3], (3600, 60, 1))) for t in
                _re.findall(r"--> (\d+:\d+:\d+),", srt)]
        assert max(ends) <= info["duration"] - slate + 1
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


def _chart_post(post_id: int, fmt: str, n: int) -> dict:
    post = make_post(post_id, fmt, n)
    post["script"]["segments"][1]["chart"] = dict(kind="bars", title="Interest on $10,000 for a year",
                                                  labels=["Big bank", "High yield"], values=[10, 420],
                                                  unit_prefix="$", note="Example rates; check yours")
    return post


def test_chart_segment_is_drawn_not_generated(media_env, monkeypatch):
    settings, brand = media_env
    import contentfactory.media.render as r
    prompts = []
    real = r.generate_images
    monkeypatch.setattr(r, "generate_images", lambda s, b, ps, *a, **k: prompts.extend(ps) or real(s, b, ps, *a, **k))
    assets = render_post(settings, brand, _chart_post(5, "carousel", 3))
    _check_provenance(assets, settings)
    assert "coins growing like plants" not in prompts and len(prompts) == 2
    chart = next(p for p in assets["provenance"] if p.get("provider") == "chart")
    assert chart["source"] == "rendered" and "420" in chart["prompt"]
    from PIL import Image
    assert Image.open(settings.output_dir / assets["slides"][1]).size == (1080, 1350)


def test_chart_clip_used_in_video_when_available(media_env, monkeypatch):
    settings, brand = media_env
    import contentfactory.media.charts as charts
    calls = []

    def fake_clip(spec, size, palette, out, seconds=3.0):
        calls.append((spec.title, size))
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=red:s={size[0]}x{size[1]}:d=1",
                        "-pix_fmt", "yuv420p", str(out)], check=True)
        return out
    monkeypatch.setattr(charts, "render_chart_clip", fake_clip)
    assets = render_post(settings, brand, _chart_post(6, "short", 3))
    assert calls == [("Interest on $10,000 for a year", (1080, 1920))]
    assert probe(settings.output_dir / assets["video"])["duration"] > 5


def test_render_chart_sizes_and_line(media_env, tmp_path):
    from PIL import Image, ImageStat

    from contentfactory.media.charts import _fmt, render_chart, render_chart_clip
    from contentfactory.media.util import Palette
    from contentfactory.schemas import ChartSpec
    _, brand = media_env
    pal = Palette.from_brand(brand)
    spec = ChartSpec(kind="line", title="$1,000 at 7% for 10 years", labels=[f"Y{i}" for i in range(11)],
                     values=[round(1000 * 1.07 ** i, 2) for i in range(11)], unit_prefix="$")
    for size in [(1080, 1920), (1920, 1080), (1080, 1350)]:
        out = render_chart(spec, size, pal, brand.visual.font, tmp_path / f"c{size[0]}x{size[1]}.png")
        img = Image.open(out)
        assert img.size == size and ImageStat.Stat(img.convert("L")).stddev[0] > 5
    assert _fmt(12_345, "$", "") == "$12k" and _fmt(1.5, "", "%") == "1.50%" and _fmt(2_500_000, "", "") == "2.5M"
    assert render_chart_clip(spec, (1080, 1920), pal, tmp_path / "x.mp4") is None  # FACTORY_CHARTS unset


def test_own_footage_beat(media_env, monkeypatch):
    settings, brand = media_env
    clip = settings.home / "footage" / "irs.mp4"
    clip.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=1280x720:d=3",
                    "-pix_fmt", "yuv420p", str(clip)], check=True)
    post = make_post(7, "long", 3)
    post["script"]["segments"][1]["footage"] = "footage/irs.mp4"
    assets = render_post(settings, brand, post)
    own = [p for p in assets["provenance"] if p["source"] == "own"]
    assert own and own[0]["tool"] == "footage"
    post["script"]["segments"][1]["footage"] = "footage/missing.mp4"
    from contentfactory.media.util import MediaError
    with pytest.raises(MediaError, match="footage not found"):
        render_post(settings, brand, post)


def test_long_video_needs_original_element():
    from contentfactory.guardrails import check_original_element
    seg = {"heading": "h", "narration": "n", "on_screen_text": "o", "visual_prompt": "v"}
    long = {"format": "long", "script": {"segments": [dict(seg)] * 3}}
    assert check_original_element(long).level == "block"
    long["script"]["original_element"] = "Record the IRS payment page"
    c = check_original_element(long)
    assert c.level == "block" and "not in the video yet" in c.message
    long["script"]["segments"] = [dict(seg, footage="footage/irs.mp4"), seg]
    assert check_original_element(long).level == "ok"
    assert check_original_element({"format": "short", "script": {}}) is None


def test_whisper_model_follows_brand_language(monkeypatch):
    from contentfactory.media.tts import TTSResult, align_with_whisper, whisper_model_name
    monkeypatch.delenv("WHISPER_MODEL", raising=False)
    assert whisper_model_name("en") == "base.en" and whisper_model_name("es") == "base"
    monkeypatch.setenv("WHISPER_MODEL", "small")
    assert whisper_model_name("es") == "small"
    import sys
    import types
    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=object))
    monkeypatch.setenv("FACTORY_ALIGN", "whisper")
    monkeypatch.setenv("WHISPER_MODEL", "base.en")
    res = TTSResult("x", "x", [], [], [], [])
    align_with_whisper(res, "es")
    assert "English-only" in res.notes[0]


def test_stock_broll_beat(media_env):
    import json as _json
    settings, brand = media_env
    clip = settings.home / "footage" / "money-made-simple" / "stock" / "b.mp4"
    clip.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=720x1280:d=3",
                    "-pix_fmt", "yuv420p", str(clip)], check=True)
    clip.with_suffix(".json").write_text(_json.dumps({"provider": "pexels", "author": "Ana", "license": "Pexels License",
                                                      "page": "https://pexels.com/v/1", "query": "groceries"}))
    post = make_post(8, "short", 3)
    post["script"]["segments"][1]["broll"] = "footage/money-made-simple/stock/b.mp4"
    assets = render_post(settings, brand, post)
    lic = [p for p in assets["provenance"] if p["source"] == "licensed" and p["tool"] == "pexels"]
    assert lic and "Ana" in str(lic[0])
