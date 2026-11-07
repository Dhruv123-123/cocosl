import math
import shutil
import wave
from array import array

import pytest

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg required")


def _take(path, parts=(1.0, 1.4, 0.8), gap=0.5, rate=44100):
    data = array("h")
    for i, secs in enumerate(parts):
        data += array("h", [int(7000 * math.sin(2 * math.pi * (200 + 40 * i) * n / rate)) for n in range(int(secs * rate))])
        data += array("h", [0] * int(gap * rate))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)  # noqa: E702
        w.writeframes(data.tobytes())
    return path


def test_single_take_split_at_pauses(home, tmp_path):
    from contentfactory.config import Settings, load_brand
    from contentfactory.media.tts import human_voice
    settings = Settings.load(home)
    brand = load_brand(settings.brands_dir, "money-made-simple")
    texts = ["one two three", "four five six seven", "eight nine"]
    assert human_voice(settings, brand, 5, texts, tmp_path / "v") is None
    slot = settings.home / "voice" / brand.slug
    slot.mkdir(parents=True)
    _take(slot / "post-5.wav")
    res = human_voice(settings, brand, 5, texts, tmp_path / "v")
    assert res.provider == "human" and len(res.paths) == 3
    # cut in the pauses, so each piece is about its spoken part (trimmed of silence)
    for got, want in zip(res.durations, (1.0, 1.4, 0.8)):
        assert abs(got - want) < 0.35, res.durations


def test_factory_voice_command_queues_rerender(factory, tmp_path):
    from contentfactory.renderq import use_own_voice
    pid = factory.db.insert("posts", {"brand": "money-made-simple", "format": "short", "status": "in_review",
                                      "title": "t", "script": {}})
    take = _take(tmp_path / "take.wav")
    job = use_own_voice(factory, pid, [str(take)])
    assert job and (factory.settings.home / "voice" / "money-made-simple" / f"post-{pid}.wav").is_file()
    a, b = _take(tmp_path / "a.wav"), _take(tmp_path / "b.wav")
    factory.db.execute("UPDATE render_jobs SET status='done'")
    use_own_voice(factory, pid, [str(a), str(b)])
    slot = factory.settings.home / "voice" / "money-made-simple" / f"post-{pid}"
    assert slot.is_dir() and len(list(slot.iterdir())) == 2 and not slot.with_suffix(".wav").exists()
    with pytest.raises(ValueError):
        use_own_voice(factory, pid, [str(tmp_path / "nope.txt")])


def test_render_uses_own_voice(home):
    from contentfactory.config import Settings, load_brand
    from contentfactory.media import render_post
    from tests.test_media import make_post
    settings = Settings.load(home)
    settings.extra.update(video_fps=12, x264_preset="ultrafast", render_workers=4)
    brand = load_brand(settings.brands_dir, "money-made-simple")
    slot = settings.home / "voice" / brand.slug
    slot.mkdir(parents=True)
    _take(slot / "post-30.wav")
    assets = render_post(settings, brand, make_post(30, "short", 2))
    audio = next(p for p in assets["provenance"] if p["path"].endswith("audio.wav"))
    assert audio["source"] == "own" and audio["provider"] == "human"
