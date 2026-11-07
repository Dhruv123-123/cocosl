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


def test_kokoro_captioned_speech_returns_word_timings(factory, brand, monkeypatch, tmp_path):
    import base64
    calls = []

    def fake_post(url, json=None, headers=None, timeout=None):
        calls.append(url)
        if url.endswith("/dev/captioned_speech"):
            body = {"audio": base64.b64encode(_wav_bytes(1.0)).decode(),
                    "timestamps": [{"word": "Hello", "start_time": 0.05, "end_time": 0.4},
                                   {"word": "there.", "start_time": 0.45, "end_time": 0.9}]}
            return httpx.Response(200, json=body, request=httpx.Request("POST", url))
        raise AssertionError("plain endpoint should not be needed")

    monkeypatch.setenv("KOKORO_URL", "http://kokoro:8880")
    monkeypatch.setattr(tts.httpx, "post", fake_post)
    monkeypatch.setattr(factory.settings, "tts_provider", "kokoro")
    res = tts.synthesize_segments(factory.settings, brand, ["Hello there."], tmp_path)
    assert res.timing == "kokoro" and res.words[0] == [("Hello", 0.05, 0.4), ("there.", 0.45, 0.9)]


def test_word_timed_captions_follow_the_voice():
    from contentfactory.media.captions import time_segment, time_segment_words
    text = "Your savings account is probably paying you almost nothing."
    words = [(w, 0.3 * i + 1.0, 0.3 * i + 1.25) for i, w in enumerate(text.split())]  # speech starts at 1.0s
    cues = time_segment_words(text, 10.0, 5.0, words)
    assert cues[0].start == 11.0                                   # first word, not the segment start
    assert abs(cues[-1].end - (10.0 + words[-1][2])) < 1e-6
    assert " ".join(c.text for c in cues) == text
    # timestamps that don't match the script fall back to the estimate
    assert [c.text for c in time_segment_words(text, 0, 5, [("nope", 0, 1)])] == \
           [c.text for c in time_segment(text, 0, 5)]


def test_whisper_alignment_is_optional(monkeypatch, tmp_path):
    monkeypatch.setenv("FACTORY_ALIGN", "whisper")
    import builtins
    real = builtins.__import__

    def no_whisper(name, *a, **k):
        if name == "faster_whisper":
            raise ImportError("no")
        return real(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", no_whisper)
    res = tts.TTSResult("espeak", "espeak", [], [])
    tts.align_with_whisper(res)
    assert res.timing == "estimated" and "faster-whisper" in res.notes[0]
