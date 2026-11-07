# Pipeline tools, round 3: free voices, captions, thumbnails and ffmpeg tools, licences checked

Written 2026-11-07. **Docs only.** Nothing was installed. It adds to `github-repos.md` (rounds 1-2, which
already cover Kokoro, Chatterbox, Piper, faster-whisper, stable-ts, whisperX, auto-editor, rembg, BiRefNet,
satori, Remotion and MoviePy). Licences were read on each repo's GitHub page (SPDX field) and, for models,
on the model card. "Weights" means the downloadable model, which often has a different licence from the code.

## TL;DR: the picks, in order

1. **Dinero Simple can get a free Spanish voice today with no code change.** Kokoro (already our default,
   Apache-2.0 weights) ships Spanish voices `ef_dora` (female), `em_alex` and `em_santa` (male). Our
   `KOKORO_VOICE_RE` already accepts the `e` prefix, and the local pipeline picks `lang_code` from it. Set
   `voice.tts_voice: em_alex` in `brands/dinero-simple.yaml`, which is empty now and points at ElevenLabs
   (paid). Kokoro has no quality grade for Spanish and warns non-English "may be thin", so a fluent listener
   should check 3 clips first (it fits the existing `review-language` step).
2. **If Kokoro Spanish isn't good enough: Chatterbox Multilingual (MIT)**, which has dedicated
   **Latin American Spanish** (`Chatterbox-Multilingual-es-mx-latam`) and Spain Spanish finetunes. Every
   clip carries Resemble's inaudible PerTh watermark, which is fine for us (we label AI voice anyway).
   Second choice: **VoxCPM2** (Apache-2.0 code and weights, "commercial-ready", 30 languages including
   Spanish), but it wants about 8 GB of GPU memory.
3. **Fix Spanish caption timing (bug-sized). Fixed on `main` the same day** ("Use a multilingual whisper model and the brand language for caption alignment"). `align_with_whisper()` in `media/tts.py` defaults to
   `WHISPER_MODEL=base.en`, an English-only model. On a Spanish brand that gives wrong words and timings.
   Fix: default to `base` (multilingual) and pass `language=brand.language` to `transcribe()`.
4. **Exact captions: ctc-forced-aligner (BSD-2).** Whisper *transcribes*, so a misheard word ends up in
   the caption. A forced aligner takes our script text and only finds the timings, so captions always match
   the script word for word. It supports Spanish, and it works on any TTS output, including Piper and
   ElevenLabs, which give no timestamps. **Caveat:** its usual model, `mms-300m-1130-forced-aligner`, is
   CC-BY-NC-4.0 (non-commercial). Load a permissively licensed Wav2Vec2 CTC model instead, for example a
   Spanish XLSR model whose card says Apache-2.0, and check the card at install.
5. **ffsubsync (MIT)** to re-sync an .srt to a video after an edit (for example after auto-editor cuts).
   Small, one command, and fine as an optional step.
6. **PyAV (BSD-3)** if the factory ever outgrows calling the `ffmpeg` binary: frame-level access and no
   shell quoting. Not needed now. Our direct `ffmpeg` calls are simpler than any wrapper, and
   **ffmpeg-python** (Apache-2.0) hasn't been updated since Aug 2024, so skip it.
7. **Motion Canvas (MIT)** as the code-driven animation tool for chart and explainer scenes. Unlike
   Remotion, it has no company licence above 3 people.

**Avoid for commercial use:** XTTS-v2 weights (Coqui Public Model Licence, non-commercial), Fish Speech
(weights historically CC-BY-NC-SA, repo licence unclear), F5-TTS weights (CC-BY-NC), ChatTTS (AGPL, plus
non-commercial weights), aeneas (AGPL), VibeVoice (Microsoft removed the TTS code in Sep 2025 and calls the
model "for research and development purposes only").

## 1. Text to speech (voices)

| Tool | Code / weights licence | Spanish | Needs | Verdict |
|---|---|---|---|---|
| **Kokoro-82M** (in use) | Apache-2.0 / Apache-2.0 | `ef_dora`, `em_alex`, `em_santa`; G2P falls back to espeak-ng `es` | CPU | **Use for Dinero Simple first.** Zero code change |
| **Chatterbox Multilingual V3** (resemble-ai) | MIT / MIT (model card tag) | 23 languages; LatAm and Spain Spanish finetunes | GPU helps; 0.5B | **Best upgrade** for Spanish and for a cloned own voice. PerTh watermark on every clip |
| **VoxCPM2** (OpenBMB, 41K stars, active) | Apache-2.0 / Apache-2.0 ("free for commercial use") | 30 languages incl. Spanish | ~8 GB VRAM; llama.cpp build for CPU/Mac | Strong second choice; forbids impersonation and fraud uses |
| **CosyVoice 3** (FunAudioLLM) | Apache-2.0 / Apache-2.0 (card tag) | 9 languages incl. Spanish | GPU | OK, but the card says its content is "for academic purposes only", so weaker than the two above |
| **Supertonic 3** (Supertone) | MIT code / **OpenRAIL-M** weights | 31 languages incl. Spanish | Very fast, ONNX, CPU | Usable (OpenRAIL-M allows commercial use with use restrictions), but **archived**: no fixes. Not a long-term base |
| **sherpa-onnx** (k2-fsa) | Apache-2.0 / per model | Runs Piper, Kokoro and other voices | CPU, phones | Only useful if we leave Python |
| Dia, Orpheus, Higgs Audio | Apache-2.0 | English-first | GPU | Skip for now; English is covered by Kokoro |
| MeloTTS (MyShell) | MIT / MIT | Yes | CPU | Stale since Dec 2024. Skip |
| Piper (in use) | GPL-3 tool; voice licences vary per voice | `es_MX` and `es_ES` voices | CPU | Check each voice's model card before commercial use |
| VibeVoice (Microsoft) | MIT repo, **TTS code removed** | Realtime model only, "experimental" | — | **Avoid** ("research and development purposes only") |
| XTTS-v2 (Coqui), Fish Speech, F5-TTS, ChatTTS | Non-commercial or unclear weights | — | — | **Avoid** |

## 2. Captions and subtitles

| Tool | Licence | What it adds | Verdict |
|---|---|---|---|
| **ctc-forced-aligner** (MahmoudAshraf97) | BSD-2 code. Its MMS-300M aligner model is **CC-BY-NC-4.0**, so load a Wav2Vec2 CTC model with a permissive licence | Script text + audio → word timings. Captions match the script exactly | **Pick**, with the model licence checked at install |
| Montreal Forced Aligner | MIT | The academic standard, many languages | Heavier (conda, acoustic models). Fallback |
| **whisper.cpp** (ggml-org, 55K stars) | MIT, OpenAI Whisper weights MIT | Fast CPU and Mac transcription, word timestamps | Only if faster-whisper is too slow on Dhruv's machine |
| **ffsubsync** | MIT | Re-syncs an .srt to the audio | **Pick** as an optional repair step |
| subaligner | MIT | Similar, neural | ffsubsync is simpler |
| FunClip (modelscope) | MIT | LLM-picked highlight clips from long videos | Interesting for long-to-Shorts later; Chinese-first |
| aeneas | AGPL-3.0 | Forced alignment | **Avoid** (AGPL) |

Whisper weights are MIT, so faster-whisper and whisper.cpp are clean for commercial use.

## 3. Thumbnails

Nothing new beats what rounds 1-2 found: **rembg** (MIT) or **BiRefNet** (MIT) to cut out a subject,
**satori** (MPL-2.0) or Pillow to lay out text, and FLUX.1-schnell (Apache-2.0) for backgrounds. The gaps
are in process, not tools. YouTube's "Test & compare" (built into Studio, free) tests 3 thumbnails per
video, and the 30-day metrics plan (`launch-metrics-30-days.md`, rule `yt-ctr-low`) says when to use it.
**Never** use FLUX.1-dev weights (non-commercial) for thumbnails.

## 4. Video editing and ffmpeg tools

| Tool | Licence | Verdict |
|---|---|---|
| **PyAV** | BSD-3 (bundles LGPL ffmpeg) | Best Python ffmpeg binding if we ever need frames. Not now |
| ffmpeg-python | Apache-2.0 | Stale (Aug 2024). Skip |
| **Motion Canvas** | MIT | **Pick** for animated charts and explainers (TypeScript). No company licence, unlike Remotion |
| editly (mifi) | MIT | JSON-to-video in Node. Overlaps with what `media/` already does |
| ffmpeg-skill (kajisho5) | MIT | 42 ffmpeg recipes for agents. Useful as a reference for filter strings, not a dependency |
| backgroundremover | MIT | Video background removal. rembg covers images |

**ffmpeg licence note:** the `ffmpeg` binary is LGPL or GPL depending on the build. We call it as a
separate program and don't ship it, so neither affects our content.

## Suggested order for the factory thread

1. Set `em_alex` (or `ef_dora`) for Dinero Simple and render 3 test clips for a fluent listener (an hour).
2. ~~Fix the whisper default for non-English brands~~ (done on `main`).
3. Optional `FACTORY_ALIGN=ctc` using ctc-forced-aligner, falling back to whisper (half a day).
4. Only if (1) sounds wrong: add a `chatterbox` provider with the LatAm Spanish finetune (a day).

## Sources

GitHub repo pages and SPDX licence fields (via the GitHub search API) for every repo above, read
2026-11-07; model cards on Hugging Face for Kokoro-82M (VOICES.md), ResembleAI/chatterbox,
Fun-CosyVoice3-0.5B; READMEs for VoxCPM, supertonic, VibeVoice (removal notice dated 2025-09-05) and
ffsubsync.
