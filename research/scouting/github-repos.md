# GitHub repos for AI content income: what to use, borrow or avoid

Pulled 2026-11-07 from GitHub's search API. "90d" columns count commits and new issues since 2026-08-07.
Raw numbers are in [`repos.csv`](repos.csv).

## How to read the verdicts

- **Use**: safe licence, healthy project, fits a gap in cocosl. Run it as a separate service or call its CLI.
- **Borrow**: good ideas or a component worth copying (with credit), but don't depend on the whole thing.
- **Avoid**: breaks platform terms, licence problem, abandoned, or makes the kind of content that's now demoted.

**Licence rules for us.** cocosl is MIT and we may sell services built on it.
MIT / BSD / Apache / Unlicense: fine to use and modify.
GPL: fine to call as a separate program (CLI or HTTP); don't copy its code into cocosl.
AGPL: fine to run unmodified as its own service; if we modify it and expose it over a network we must publish
our changes, so never vendor AGPL code into cocosl.
**Model weights have their own licences**, often stricter than the code. Check them separately.

**Star counts are not quality.** Several repos below gained tens of thousands of stars in a few months with
one or two committers. Where stars, commits and contributors don't match, it's flagged.

## 1. All-in-one "faceless video" generators

| Repo | Stars | Licence | 90d commits / issues | What it does | Verdict |
|---|---|---|---|---|---|
| harry0703/MoneyPrinterTurbo | 140K | MIT | 552 / 76, 19 authors | Topic → LLM script → stock clips (Pexels/Pixabay) → TTS → subtitles → MP4. Web UI and API. | **Borrow.** Healthy and permissively licensed, but its output is stock footage plus TTS, the format Meta now demotes as unoriginal. Its stock-clip search and subtitle styling are worth borrowing as a B-roll layer. |
| FujiwaraChoki/MoneyPrinterV2 | 32K | AGPL-3.0 | 1 / 0 | YouTube Shorts plus a Twitter bot, Amazon affiliate posting and cold outreach, driven through browser automation. | **Avoid.** Browser-automated posting breaks platform terms, AGPL, and effectively unmaintained. |
| FujiwaraChoki/MoneyPrinter | 14K | MIT | low | The original MoviePy Shorts generator. | **Avoid.** Superseded by MoneyPrinterTurbo. |
| ddean2009/MoneyPrinterPlus | 7.3K | GPL-3.0 | none since Mar 2025 | Batch remix videos and auto-post to Douyin, Kuaishou and others. | **Avoid.** Built for mass remixing; stale. |
| RayVentura/ShortGPT | 8.1K | MIT | none since Feb 2025 | Early Shorts automation framework. | **Avoid.** Stale. |
| ATH-MaaS/Pixelle-Video | 30K | Apache-2.0 | 0 / 16 | ComfyUI-based fully automatic short-video engine. | **Borrow.** Good ComfyUI workflow ideas; no commits in 90 days. |
| calesthio/OpenMontage | 78K | AGPL-3.0 | 153 / 58, 15 authors | Agentic production system: 12 pipelines, Remotion, Flux, ElevenLabs, skills files. | **Borrow ideas only.** Active and real, but AGPL, so don't vendor it. Its pipeline/skill breakdown is a useful reference for our writer prompts. |
| gyoridavid/short-video-maker | 1.5K | MIT | 0 / 3 | MCP server: script → Kokoro TTS → Pexels → Remotion → Short. | **Borrow.** Clean, small, MIT. Shows Kokoro + Remotion + Pexels wiring. Inactive since Jun 2025. |
| rushindrasinha/youtube-shorts-pipeline | 2.4K | MIT | 0 / 1 | News → script → AI visuals → voice → captions → upload. | **Borrow.** Readable reference; inactive. |
| Hao0321/video-autopilot-kit | 2.3K | MIT | 63 / 4, 2 authors | CapCut JSON templates + ffmpeg tools + onboarding questionnaire. | **Borrow.** CapCut project export is interesting if Dhruv wants to hand-polish in CapCut. |
| Vincentwei1021/anything2explainer | 3.1K | no SPDX licence | 28 / 10 | Claude Code skill: topic → motion-graphics explainer (Remotion + Kokoro/edge-tts). | **Borrow ideas only** until the licence is clear. The black-canvas motion-graphics explainer style suits finance. |
| kaomei/stickman-video-director | 4.6K | MIT | 137 / 4, **1 author** | Script → animated stickman video for faceless YouTube. | **Try with caution.** Shows strong demand for the format. 4.6K stars in 3 months from a single author with few issues is unusual; review the code before running it. |
| SaarD00/AI-Youtube-Shorts-Generator, Dark2C/Viral-Faceless-Shorts-Generator, purffle-shorts, yumcut | <1K | mixed | low | More of the same. | **Skip.** Nothing cocosl doesn't already do. |

**Takeaway:** cocosl already has the parts these repos have (script, voice, visuals, captions, render), plus
guardrails and official-API publishing they mostly lack. The gaps worth filling are better voice, real
caption timing, and nicer motion graphics, not another generator.

## 2. Voice (TTS)

| Repo | Stars | Licence (code / weights) | 90d | Verdict |
|---|---|---|---|---|
| remsky/Kokoro-FastAPI | 5.6K | Apache-2.0 / Kokoro-82M weights Apache-2.0 | 151 commits, 10 authors | **Use.** Docker, CPU or GPU, **OpenAI-compatible `/v1/audio/speech`**, also returns word timestamps. Plugs into our existing `openai` TTS provider once its URL is configurable. Best free option. |
| hexgrad/kokoro | 9.9K | Apache-2.0 | | The model behind it. |
| resemble-ai/chatterbox | 28K | MIT | 1 commit / 20 issues | **Use (option 2).** More expressive than Kokoro, zero-shot voice cloning (own voice only). Adds an inaudible "Perth" watermark, which is fine and arguably good for disclosure. Slower; needs a GPU for comfort. |
| QwenLM/Qwen3-TTS | 14K | Apache-2.0 | quiet | **Use (option 3).** Voice design from a text description and cloning; Apache weights. |
| OHF-Voice/piper1-gpl | 6.2K | GPL-3.0 | 72 commits | **Keep as is.** The maintained Piper (rhasspy/piper is archived). We call the CLI, so GPL is fine. Check each voice's own licence. |
| SWivid/F5-TTS | 16K | MIT code / **CC-BY-NC weights** | 7 | **Avoid for monetized content.** The released checkpoints are non-commercial. This corrects our 2026-11-05 stack note. |
| debpalash/VoiceStudio | 103K | AGPL-3.0 | **5,345 commits, 2 authors** / 907 issues | **Avoid for now.** "Local ElevenLabs alternative" with star and commit counts that don't fit a 7-month-old, 2-person project. AGPL either way. |
| abus-aikorea/voice-pro | 13K | GPL-3.0 | | Skip; a GUI over the same models. |

## 3. Captions and editing

| Repo | Stars | Licence | 90d | Verdict |
|---|---|---|---|---|
| SYSTRAN/faster-whisper | 27K | MIT | 13 commits | **Use.** Word-level timestamps on our own TTS audio, so burned captions land exactly on each word instead of the current estimate (`media/captions.py`). CPU is fine for Short-length audio. |
| jianfch/stable-ts | 2.3K | MIT | 0 | **Use (alternative).** Forced alignment: we already have the exact script, so aligning text to audio is more accurate than transcribing. Quiet but stable. |
| m-bain/whisperX | 25K | BSD-2-Clause | 9 | Use if we need diarization (we don't). |
| WyattBlue/auto-editor | 5.8K | Unlicense | 172 | **Use** for any human-recorded audio or screen recordings: cuts silences automatically. CLI. |
| buxuku/SmartSub | 6K | MIT | active | Desktop app; not for the pipeline. |
| nicolaigaina/ai-video-captions | 70 | MIT | | Borrow its animated caption style presets (e.g. word-pop) for our `.ass` templates. |

## 4. Visuals and motion

| Repo | Stars | Licence | 90d | Verdict |
|---|---|---|---|---|
| Comfy-Org/ComfyUI | 145K | GPL-3.0 | 570 | **Already integrated** (HTTP API). Keep. |
| remotion-dev/remotion | 71K | Custom: free for individuals and companies of up to 3 people; paid company licence above that | 5,717 commits | **Use for motion-graphic explainers and animated charts**, which suit finance (compound-interest curves, debt payoff bars). Run as a separate Node render step. Fine under the free tier while it's Dhruv alone. |
| Wan-Video/Wan2.2 | 18K | Apache-2.0 (weights Apache) | 2 | **Use sparingly** for short B-roll clips via ComfyUI. Needs a 24GB+ GPU or a rented one. |
| Lightricks/LTX-2 | 10K | Apache-2.0 code; check weight licence | 15 | Faster than Wan; check the model weights' licence terms before commercial use. |
| Tencent-Hunyuan/HunyuanVideo | 13K | Tencent licence (excludes EU, UK, South Korea) | | **Avoid**: territory restrictions. |
| Kosinkadink/ComfyUI-VideoHelperSuite | 1.9K | GPL-3.0 | | Use inside ComfyUI if we do video there. |
| bytedance/LatentSync, Rudrabha/Wav2Lip | 6K / 13K | Apache / none | stale | **Avoid.** Lip-sync talking heads lead to the AI-persona label and likeness risk. |

## 5. Music

| Repo | Stars | Licence | Verdict |
|---|---|---|---|
| ace-step/ACE-Step-1.5 | 14K | MIT | **Use** for short background beds we generate ourselves (no copyright-claim risk). Keep music under the voice and check the output on YouTube's Content ID before relying on it. |
| facebookresearch/audiocraft (MusicGen) | 24K | MIT code / **CC-BY-NC weights** | **Avoid** for monetized content. |

## 6. Scheduling and publishing

| Repo | Stars | Licence | 90d | Verdict |
|---|---|---|---|---|
| gitroomhq/postiz-app | 41K | AGPL-3.0 | 735 commits | **Already integrated** (`publish/postiz.py`), run unmodified as its own service, which is fine under AGPL. |
| gitroomhq/postiz-agent | 565 | unclear | 53 | Skip; we already call Postiz directly. |
| inovector/mixpost | 3.9K | MIT | **0** | Was in our 2026-11-05 stack note; no commits in 90 days. Prefer Postiz. |
| eat-pray-ai/yutu | 715 | Apache-2.0 | 82 | **Borrow.** Go CLI/MCP for the official YouTube Data API: handy for Dhruv to manage the channel from Claude. |
| langchain-ai/social-media-agent | 3K | MIT | 95 | Borrow its human-in-the-loop review pattern; we already have one. |
| brightbeanxyz/brightbean-studio | 2.6K | AGPL-3.0 | 137 | Skip; Postiz covers it. |
| wanghaisheng/easy-uploader | 386 | MIT | | **Avoid.** Bulk auto-upload through unofficial routes. |

## 7. AI UGC ads (for the ad studio line)

| Repo | Stars | Licence | Verdict |
|---|---|---|---|
| Anil-matcha/Open-AI-UGC | 418 | MIT | Borrow ideas only. It's a front end for a paid API (muapi) generating "AI actor" ads. Our business module deliberately does spokesperson/demo ads, never fake customers; keep it that way. |
| xixihhhh/clipforge | 1.2K | AGPL-3.0 | Product-image → selling video for Douyin shops. Interesting idea (product image kept unchanged, AI does the rest); AGPL, so ideas only. |
| Clipcat-ai/clipcat-skill | 458 | none | **Avoid.** "Replicate winning videos" is the copying Meta now demotes. |

## 8. Instagram scrapers we deliberately skipped

`instaloader/instaloader` (14K, MIT) and similar tools download other people's posts and profiles. That
breaks Instagram's terms and our own compliance rules (no scrapers or downloaders), so none were used for
this research and none should be added to cocosl. Use the official Business Discovery API instead
(`watchlist.py`).
