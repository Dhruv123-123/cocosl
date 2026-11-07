import pytest

from contentfactory.media.images import ComfyUI, check_model_licence
from contentfactory.media.util import ProviderError


def test_flux_schnell_workflow_and_dev_refused(monkeypatch):
    monkeypatch.setenv("COMFYUI_CHECKPOINT", "flux1-schnell-fp8.safetensors")
    wf = ComfyUI.__new__(ComfyUI).workflow("a piggy bank", "9:16")
    assert wf["3"]["inputs"]["steps"] == 4 and wf["3"]["inputs"]["cfg"] == 1.0 and wf["7"]["inputs"]["text"] == ""
    with pytest.raises(ProviderError):
        check_model_licence("flux1-dev-fp8.safetensors")
    check_model_licence("sd_xl_base_1.0.safetensors")


def _tone_wav(path, rate=44100, lead=0.6, speech=0.5, tail=0.9):
    import math
    import wave
    from array import array
    data = array("h", [0] * int(lead * rate))
    data += array("h", [int(8000 * math.sin(2 * math.pi * 220 * i / rate)) for i in range(int(speech * rate))])
    data += array("h", [0] * int(tail * rate))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)  # noqa: E702
        w.writeframes(data.tobytes())


def test_trim_silence_cuts_dead_air_and_reports_lead(tmp_path, monkeypatch):
    import wave

    from contentfactory.media.tts import trim_silence
    p = tmp_path / "seg.wav"
    _tone_wav(p)
    lead = trim_silence(p)
    assert abs(lead - 0.52) < 0.03                      # 0.6 s of silence minus 0.08 s padding
    with wave.open(str(p)) as w:
        assert abs(w.getnframes() / w.getframerate() - 0.66) < 0.04
    monkeypatch.setenv("FACTORY_TRIM_SILENCE", "0")
    _tone_wav(p)
    assert trim_silence(p) == 0.0
