"""Text to speech, one audio file per script segment.

Providers (settings.tts_provider; "auto" tries them in this order):
  kokoro     - Kokoro-82M (Apache-2.0 open weights, free, natural voices). Either a
               Kokoro-FastAPI server at KOKORO_URL (OpenAI-compatible /v1/audio/speech;
               `docker compose --profile kokoro up`), or the local `kokoro` Python
               package (pip install "contentfactory[kokoro]"). Voice: brand.voice.tts_voice
               if it is a Kokoro id like af_heart, else KOKORO_VOICE (default af_heart)
  piper      - local `piper` CLI, model path in PIPER_MODEL (.onnx)
  espeak     - local `espeak-ng` / `espeak` (robotic, but free and offline)
  elevenlabs - REST API, ELEVENLABS_API_KEY; voice id from brand.voice.tts_voice or ELEVENLABS_VOICE_ID
  openai     - REST API, OPENAI_API_KEY; gpt-4o-mini-tts (falls back to tts-1)
  silent     - near-silent room tone sized to the words at brand.voice.words_per_minute

Voice rights: clone only your own voice or a voice you hold a licence for.
Never clone or imitate a real person without their written consent, and never
use a synthetic voice to fake a customer testimonial.

A whole post is voiced by a single provider so the voice never changes
mid-video; in auto mode a provider that fails on any segment is abandoned and
the next one re-voices every segment.
"""
from __future__ import annotations

import os
import random
import re
import shutil
import struct
import wave
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from ..config import BrandProfile, Settings
from .util import MediaError, ProviderError, ffmpeg, probe, seed_of, word_count

ORDER = ["kokoro", "piper", "espeak", "elevenlabs", "openai", "silent"]
SAMPLE_RATE = 44100
HTTP_TIMEOUT = httpx.Timeout(90.0, connect=10.0)


@dataclass
class TTSResult:
    provider: str
    tool: str
    paths: list[Path]
    durations: list[float]
    notes: list[str] = field(default_factory=list)


def synthesize_segments(settings: Settings, brand: BrandProfile, texts: list[str], out_dir: Path) -> TTSResult:
    """Voice every text into out_dir/seg-XX.wav with one provider."""
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = (settings.tts_provider or "auto").lower()
    if wanted != "auto" and wanted not in ORDER:
        raise MediaError(f"Unknown TTS provider '{wanted}'. Use one of: auto, {', '.join(ORDER)}")
    candidates = ORDER if wanted == "auto" else [wanted]
    notes: list[str] = []
    for name in candidates:
        provider = PROVIDERS[name](settings, brand)
        if wanted == "auto" and not provider.available():
            continue
        try:
            paths, durs = [], []
            for i, text in enumerate(texts):
                path = out_dir / f"seg-{i:02d}.wav"
                provider.speak(text, path)
                paths.append(path)
                durs.append(probe(path)["duration"])
            return TTSResult(name, provider.tool, paths, durs, notes)
        except (ProviderError, MediaError, httpx.HTTPError) as e:
            if wanted != "auto":
                raise ProviderError(f"TTS provider '{name}' failed: {e}") from e
            notes.append(f"tts {name} failed, fell through: {str(e)[:200]}")
    raise ProviderError("No TTS provider succeeded: " + "; ".join(notes))


def concat_narration(paths: list[Path], slots: list[float], out: Path) -> None:
    """Join segment WAVs into one track, padding each to its timeline slot."""
    args: list[str] = []
    for p in paths:
        args += ["-i", str(p)]
    chains = [f"[{i}:a]aresample={SAMPLE_RATE},aformat=sample_fmts=s16:channel_layouts=mono,"
              f"apad,atrim=0:{slot:.3f},asetpts=PTS-STARTPTS[a{i}]" for i, slot in enumerate(slots)]
    joined = "".join(f"[a{i}]" for i in range(len(paths)))
    graph = ";".join(chains) + f";{joined}concat=n={len(paths)}:v=0:a=1[out]"
    ffmpeg([*args, "-filter_complex", graph, "-map", "[out]", "-c:a", "pcm_s16le", str(out)])


# ---------------------------------------------------------------- providers
class Provider:
    tool = ""

    def __init__(self, settings: Settings, brand: BrandProfile):
        self.settings, self.brand = settings, brand

    def available(self) -> bool:
        return True

    def speak(self, text: str, out: Path) -> None:
        raise NotImplementedError


KOKORO_VOICE_RE = re.compile(r"^[abefhijpz][fm]_[a-z]+$")


class Kokoro(Provider):
    """Kokoro-82M via a Kokoro-FastAPI server (KOKORO_URL) or the local `kokoro` package."""
    tool = "kokoro"
    _pipelines: dict = {}

    def voice(self) -> str:
        v = (self.brand.voice.tts_voice or "").strip()
        return v if KOKORO_VOICE_RE.match(v) else os.environ.get("KOKORO_VOICE", "af_heart")

    def speed(self) -> float:
        try:
            return float(os.environ.get("KOKORO_SPEED", "") or 1.0)
        except ValueError:
            return 1.0

    @staticmethod
    def _url() -> str:
        return os.environ.get("KOKORO_URL", "").rstrip("/")

    @staticmethod
    def _local() -> bool:
        import importlib.util
        return importlib.util.find_spec("kokoro") is not None and os.environ.get("KOKORO_LOCAL", "1") != "0"

    def available(self) -> bool:
        return bool(self._url()) or self._local()

    def speak(self, text: str, out: Path) -> None:
        if self._url():
            return self._speak_http(text, out)
        if self._local():
            return self._speak_local(text, out)
        raise ProviderError("Kokoro needs KOKORO_URL (a Kokoro-FastAPI server) or the `kokoro` package installed")

    def _speak_http(self, text: str, out: Path) -> None:
        body = {"model": os.environ.get("KOKORO_MODEL", "kokoro"), "input": _clean(text), "voice": self.voice(),
                "response_format": "wav", "speed": self.speed()}
        headers = {"Authorization": f"Bearer {os.environ['KOKORO_API_KEY']}"} if os.environ.get("KOKORO_API_KEY") else {}
        try:
            resp = httpx.post(f"{self._url()}/v1/audio/speech", json=body, headers=headers, timeout=HTTP_TIMEOUT)
        except httpx.HTTPError as e:
            raise ProviderError(f"Kokoro server at {self._url()} unreachable: {e}") from e
        _raise_for(resp, "Kokoro")
        self.tool = f"kokoro:{self.voice()}"
        _to_wav(resp.content, ".wav", out)

    def _speak_local(self, text: str, out: Path) -> None:
        try:
            import numpy as np
            from kokoro import KPipeline
        except Exception as e:  # torch/espeak missing, etc.
            raise ProviderError(f"local kokoro failed to load: {e}") from e
        voice = self.voice()
        lang = voice[0]
        if lang not in self._pipelines:
            self._pipelines[lang] = KPipeline(lang_code=lang)
        chunks = [np.asarray(audio, dtype="float32") for _, _, audio in
                  self._pipelines[lang](_clean(text), voice=voice, speed=self.speed())]
        if not chunks:
            raise ProviderError("kokoro returned no audio")
        pcm = (np.clip(np.concatenate(chunks), -1, 1) * 32767).astype("<i2").tobytes()
        tmp = out.with_suffix(".k24.wav")
        with wave.open(str(tmp), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)  # noqa: E702
        try:
            _to_wav(tmp.read_bytes(), ".wav", out)
        finally:
            tmp.unlink(missing_ok=True)
        self.tool = f"kokoro-local:{voice}"


class Piper(Provider):
    tool = "piper"

    def available(self) -> bool:
        model = os.environ.get("PIPER_MODEL", "")
        return bool(shutil.which("piper") and model and Path(model).exists())

    def speak(self, text: str, out: Path) -> None:
        if not self.available():
            raise ProviderError("piper needs the `piper` CLI on PATH and PIPER_MODEL pointing to a .onnx voice")
        from .util import run
        run(["piper", "--model", os.environ["PIPER_MODEL"], "--output_file", str(out)],
            input_bytes=_clean(text).encode(), timeout=300)


class Espeak(Provider):
    def available(self) -> bool:
        return bool(self._binary())

    @staticmethod
    def _binary() -> str | None:
        return shutil.which("espeak-ng") or shutil.which("espeak")

    @property
    def tool(self) -> str:  # type: ignore[override]
        return Path(self._binary() or "espeak-ng").name

    def speak(self, text: str, out: Path) -> None:
        binary = self._binary()
        if not binary:
            raise ProviderError("espeak-ng/espeak not found on PATH")
        from .util import run
        voice = os.environ.get("ESPEAK_VOICE", "en-us")
        wpm = str(max(80, min(260, self.brand.voice.words_per_minute)))
        run([binary, "-v", voice, "-s", wpm, "-w", str(out), "--stdin"], input_bytes=_clean(text).encode(),
            timeout=120)


class ElevenLabs(Provider):
    tool = "elevenlabs"
    URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    def _creds(self) -> tuple[str, str]:
        return (os.environ.get("ELEVENLABS_API_KEY", ""),
                self.brand.voice.tts_voice or os.environ.get("ELEVENLABS_VOICE_ID", ""))

    def available(self) -> bool:
        return all(self._creds())

    def speak(self, text: str, out: Path) -> None:
        key, voice = self._creds()
        if not key or not voice:
            raise ProviderError("ElevenLabs needs ELEVENLABS_API_KEY and a voice id "
                                "(brand.voice.tts_voice or ELEVENLABS_VOICE_ID)")
        resp = httpx.post(self.URL.format(voice_id=voice), params={"output_format": "mp3_44100_128"},
                          headers={"xi-api-key": key, "accept": "audio/mpeg"},
                          json={"text": _clean(text),
                                "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")},
                          timeout=HTTP_TIMEOUT)
        _raise_for(resp, "ElevenLabs")
        _to_wav(resp.content, ".mp3", out)


class OpenAITTS(Provider):
    tool = "openai"
    URL = "https://api.openai.com/v1/audio/speech"

    def available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def speak(self, text: str, out: Path) -> None:
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise ProviderError("OpenAI TTS needs OPENAI_API_KEY")
        voice = os.environ.get("OPENAI_TTS_VOICE", "alloy")
        last = None
        for model in dict.fromkeys([os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"), "tts-1"]):
            body = {"model": model, "input": _clean(text), "voice": voice, "response_format": "wav"}
            if model.startswith("gpt-4o"):
                body["instructions"] = f"Tone: {self.brand.voice.tone}. Speak naturally, like {self.brand.voice.persona}."
            resp = httpx.post(self.URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=HTTP_TIMEOUT)
            if resp.status_code in (400, 404) and model != "tts-1":
                last = resp
                continue
            _raise_for(resp, "OpenAI TTS")
            self.tool = f"openai:{model}"
            _to_wav(resp.content, ".wav", out)
            return
        _raise_for(last, "OpenAI TTS")


class Silent(Provider):
    """Near-silent room tone, as long as the words would take to say."""
    tool = "silent"

    def speak(self, text: str, out: Path) -> None:
        wpm = max(60, self.brand.voice.words_per_minute or 160)
        seconds = max(0.6, word_count(text) / wpm * 60)
        write_room_tone(out, seconds, seed_of(text))


def write_room_tone(out: Path, seconds: float, seed: int = 0, level_db: float = -62.0) -> None:
    """Mono 16-bit WAV of very quiet, smoothed noise (sounds like silence, but
    keeps encoders and platforms from treating the track as empty)."""
    rng = random.Random(seed)
    amp = 32767 * 10 ** (level_db / 20)
    prev, loop = 0.0, []
    for _ in range(SAMPLE_RATE):  # one second of noise, tiled
        prev = 0.97 * prev + 0.03 * rng.uniform(-1, 1) * 6
        loop.append(int(max(-1.0, min(1.0, prev)) * amp))
    one = struct.pack(f"<{len(loop)}h", *loop)
    n_bytes = int(seconds * SAMPLE_RATE) * 2
    frames = (one * (n_bytes // len(one) + 1))[:n_bytes]
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(bytes(frames))


PROVIDERS = {"kokoro": Kokoro, "piper": Piper, "espeak": Espeak, "elevenlabs": ElevenLabs, "openai": OpenAITTS, "silent": Silent}


# ---------------------------------------------------------------- helpers
def _clean(text: str) -> str:
    return " ".join((text or "").split()) or "."


def _raise_for(resp: httpx.Response | None, name: str) -> None:
    if resp is None:
        raise ProviderError(f"{name}: no response")
    if resp.status_code >= 400:
        raise ProviderError(f"{name} HTTP {resp.status_code}: {resp.text[:300]}")


def _to_wav(data: bytes, suffix: str, out: Path) -> None:
    """Normalise any provider audio to mono 44.1 kHz s16 WAV."""
    if not data:
        raise ProviderError("empty audio response")
    tmp = out.with_suffix(".src" + suffix)
    tmp.write_bytes(data)
    try:
        ffmpeg(["-i", str(tmp), "-ar", str(SAMPLE_RATE), "-ac", "1", "-c:a", "pcm_s16le", str(out)])
    finally:
        tmp.unlink(missing_ok=True)
