import io
import wave

import httpx
import pytest

from contentfactory.media import tts


def _wav_bytes(seconds=0.5, rate=24000):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)  # noqa: E702
        w.writeframes(b"\x00\x01" * int(seconds * rate))
    return buf.getvalue()


@pytest.fixture
def brand(factory):
    return next(iter(factory.brands().values()))


def test_kokoro_unavailable_without_config(factory, brand, monkeypatch):
    monkeypatch.delenv("KOKORO_URL", raising=False)
    monkeypatch.setenv("KOKORO_LOCAL", "0")
    assert not tts.Kokoro(factory.settings, brand).available()


def test_kokoro_http_voices_and_normalises(factory, brand, monkeypatch, tmp_path):
    seen = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        seen.update(url=url, body=json)
        return httpx.Response(200, content=_wav_bytes(), request=httpx.Request("POST", url))

    monkeypatch.setenv("KOKORO_URL", "http://kokoro:8880/")
    monkeypatch.setenv("KOKORO_VOICE", "bf_emma")
    monkeypatch.setattr(tts.httpx, "post", fake_post)
    monkeypatch.setattr(factory.settings, "tts_provider", "kokoro")
    res = tts.synthesize_segments(factory.settings, brand, ["Hello there.", "Second line."], tmp_path)
    assert res.provider == "kokoro" and len(res.paths) == 2
    assert seen["url"] == "http://kokoro:8880/v1/audio/speech"
    assert seen["body"]["voice"] == "bf_emma" and seen["body"]["response_format"] == "wav"
    with wave.open(str(res.paths[0])) as w:
        assert w.getframerate() == tts.SAMPLE_RATE and w.getnchannels() == 1


def test_kokoro_brand_voice_wins_only_if_kokoro_id(factory, brand, monkeypatch):
    k = tts.Kokoro(factory.settings, brand)
    monkeypatch.setenv("KOKORO_VOICE", "am_michael")
    monkeypatch.setattr(brand.voice, "tts_voice", "21m00Tcm4TlvDq8ikWAM")  # an ElevenLabs id
    assert k.voice() == "am_michael"
    monkeypatch.setattr(brand.voice, "tts_voice", "af_bella")
    assert k.voice() == "af_bella"


def test_auto_falls_back_when_kokoro_server_down(factory, brand, monkeypatch, tmp_path):
    def boom(*a, **k):
        raise httpx.ConnectError("refused")

    monkeypatch.setenv("KOKORO_URL", "http://kokoro:8880")
    monkeypatch.setattr(tts.httpx, "post", boom)
    for var in ("PIPER_MODEL", "ELEVENLABS_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(tts.Espeak, "available", lambda self: False)
    monkeypatch.setattr(factory.settings, "tts_provider", "auto")
    res = tts.synthesize_segments(factory.settings, brand, ["Hi."], tmp_path)
    assert res.provider == "silent" and any("kokoro" in n.lower() for n in res.notes)
