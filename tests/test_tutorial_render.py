"""factory tutorial-render: spec -> silent preview with captions, then final.mp4 once voice takes exist."""
import subprocess
from pathlib import Path

import pytest
import yaml
from PIL import Image

from contentfactory import tutorial_render as tr
from contentfactory.media.util import probe

ROOT = Path(__file__).resolve().parents[1]


def _ff(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, a)], check=True)


def _spec(tmp_path, ai_voice=False):
    foot = tmp_path / "footage"
    foot.mkdir()
    Image.new("RGB", (320, 180), (200, 120, 90)).save(foot / "card.png")
    _ff("-f", "lavfi", "-i", "testsrc=size=320x180:rate=30", "-t", "1", "-pix_fmt", "yuv420p", foot / "clip.mp4")
    spec = {"id": "t-demo", "title": "Demo", "size": [320, 180], "palette": ["#16181d", "#f6efe6", "#c8775a"],
            "ai_voice": ai_voice,
            "beats": [{"image": "card.png", "say": "Open the maker in your browser.", "seconds": 1.2},
                      {"footage": "clip.mp4", "say": "Add three photos and click make.", "seconds": 1.5}]}
    p = tmp_path / "demo.yaml"
    p.write_text(yaml.safe_dump(spec))
    return p, foot


def test_preview_then_final_with_voice(factory, tmp_path):
    spec, foot = _spec(tmp_path)
    info = tr.render(factory, spec, foot, fast=True)
    out = Path(info["file"])
    assert info["mode"] == "none" and out.name == "preview.mp4" and out.exists()
    assert abs(probe(out)["duration"] - 2.7) < 0.3
    prompt = (out.parent / "TELEPROMPTER.md").read_text()
    assert "Open the maker in your browser." in prompt and "| 2 |" in prompt
    assert "beat-02.wav" in (out.parent / "RECORD.md").read_text()
    vd = tr.voice_dir(factory.settings, tr.load_spec(spec, foot))
    vd.mkdir(parents=True)
    for i, secs in ((1, 0.5), (2, 2.4)):  # the second take is longer than its planned slot: the beat stretches
        _ff("-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000", "-t", secs, vd / f"beat-{i:02d}.wav")
    info = tr.render(factory, spec, foot, fast=True)
    final = Path(info["file"])
    assert info["mode"] == "beats" and final.name == "final.mp4"
    assert info["seconds"] >= 1.2 + 2.4 + tr.TAKE_PAD - 0.01
    assert "audio" in probe(final)["streams"]


def test_missing_footage_and_empty_lines(factory, tmp_path):
    spec, foot = _spec(tmp_path)
    (foot / "clip.mp4").unlink()
    with pytest.raises(FileNotFoundError):
        tr.render(factory, spec, foot, fast=True)
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump({"id": "x", "beats": [{"image": "card.png", "say": ""}]}))
    with pytest.raises(ValueError):
        tr.load_spec(bad, foot)


def test_ai_voice_spec_gets_a_label(factory, tmp_path):
    spec, foot = _spec(tmp_path, ai_voice=True)
    info = tr.render(factory, spec, foot, fast=True)
    assert Path(info["file"]).exists()


def test_kit_tutorial_specs_load():
    specs = sorted((ROOT / "launch" / "ugc-service" / "kits-tutorials").glob("*.yaml"))
    assert len(specs) == 5
    for p in specs:
        s = tr.load_spec(p)
        assert s.beats and not s.ai_voice and s.size == (1920, 1080)
        text = " ".join(b.say for b in s.beats).lower()
        for banned in ("boost your sales", "best-selling", "guaranteed", "human-written"):
            assert banned not in text
