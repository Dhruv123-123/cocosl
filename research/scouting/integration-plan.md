# Integration plan: what to plug into cocosl, in order

Each item names the file it touches, the repo it uses, and rough effort. None of these change the
compliance guardrails in `docs/COMPLIANCE.md`; several strengthen them.

## 1. Free local voice via Kokoro-FastAPI (unblocks the 16 videos waiting on a voice) — done

**Shipped on main:** `kokoro` TTS provider (Kokoro-FastAPI at `KOKORO_URL`, or the local `kokoro`
package), first in auto order, with `docker compose --profile kokoro up`. See `media/tts.py`.

- **Repo:** remsky/Kokoro-FastAPI (Apache-2.0; Kokoro-82M weights Apache-2.0).
- **Why:** The launch pack has 16 scripts in `videos-need-voice/`. ElevenLabs costs money and needs a
  key; espeak sounds robotic; Piper voices vary in quality and licence. Kokoro is free, runs on CPU,
  and sounds natural.
- **Effort:** about 1 hour including a test. **Licence risk:** none.

## 2. Trial Reels in the Instagram publisher — done

**Shipped:** set `IG_TRIAL_REELS=SS_PERFORMANCE` (or `MANUAL`) and every Reel goes out as a Trial Reel;
the publish result records `trial_reel: true`.

- **API:** `trial_params={"graduation_strategy": "SS_PERFORMANCE"}` on a `REELS` container
  ([docs](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media)).
- **Why:** Trial Reels are shown to non-followers first and only reach followers if they perform. For a
  new account that's free, official hook testing, and weak posts never dent engagement with followers.
- **Change:** `publish/instagram.py` Reels branch: add `trial_params` when the post or brand YAML sets
  `instagram.trial_reels: true`. Show "trial" on the dashboard. Record the graduation result in metrics.
- **Effort:** 1-2 hours. **Risk:** none; it's an official parameter.

## 3. Word-accurate captions

- **Repos:** SYSTRAN/faster-whisper (MIT) or jianfch/stable-ts (MIT, forced alignment). Kokoro-FastAPI
  also returns word timestamps directly, which may make this free once #1 is in.
- **Why:** `media/captions.py` spreads words across each segment by length. Word-pop captions only
  feel right when each word lands on time.
- **Change:** new `media/align.py` with `align(text, wav) -> list[Cue]`: use timestamps from the TTS
  provider if it gave them, else stable-ts alignment if installed, else today's estimate. Optional
  dependency extra `[align]`.
- **Effort:** half a day. **Licence risk:** none.

## 4. Motion-graphic finance explainers with Remotion

- **Repo:** remotion-dev/remotion (free for individuals and companies of up to 3 people).
- **Why:** Animated charts (compound growth, debt avalanche vs snowball, fee drag) are original, clearly
  useful, and hard for stock-footage generators to copy. Fits the carousel topics we already have.
- **Change:** a small `integrations/remotion/` Node project with 3 templates (line chart grows, bar race,
  number counter) that takes JSON props from the script; `media/video.py` calls `npx remotion render`
  when `brand.video.style == "motion"`. Borrow layout ideas from anything2explainer (no licence yet, so
  ideas only).
- **Effort:** 1-2 days. **Licence risk:** buy a company licence if the business grows past 3 people.

## 5. Competitor watchlist through the official API

- **API:** Instagram Business Discovery (`business_discovery.username(x){followers_count,media_count,media{...}}`),
  available to our own Business/Creator account token.
- **Why:** We have no honest data on which faceless finance accounts are growing. Listicles estimate.
  A weekly snapshot gives us real follower deltas and per-post engagement for accounts in our niche.
- **Change:** done as a standalone script in this folder (`watchlist.py`). If it proves useful, move it
  into `insights.py` and show deltas on the dashboard.
- **Effort:** done; needs Dhruv's Instagram token from `factory auth meta`.

## 6. Silence-cut for human-recorded audio and screen demos

- **Repo:** WyattBlue/auto-editor (Unlicense).
- **Why:** For the screen-recorded template-demo format and if Dhruv ever records his own voice.
- **Change:** optional pre-step in `media/video.py` when an asset's provenance is `own` and it's a
  recording: `auto-editor in.mp4 --margin 0.15s -o out.mp4`.
- **Effort:** 1 hour.

## 7. Generated background music

- **Repo:** ace-step/ACE-Step-1.5 (MIT).
- **Why:** Licensed-music costs and copyright claims. A quiet generated bed under the voice is ours.
- **Change:** `media/music.py` provider that calls a local ACE-Step server; provenance `generated`.
  Keep it at -24 dB under the voice. Test one upload against YouTube Content ID first.
- **Effort:** half a day plus a GPU.

## 8. Stock B-roll as a supporting layer (optional)

- **Borrow from:** harry0703/MoneyPrinterTurbo (MIT) Pexels search code.
- **Why:** Some Reels benefit from a real-world clip behind the text. As the main visual it reads as
  unoriginal; as one layer under an original script and our own graphics it's fine.
- **Change:** `media/stock.py` using the Pexels API (free key; follow Pexels' attribution guideline),
  provenance `licensed` with the source URL stored, so `guardrails.check_assets_licensed` still passes.
- **Effort:** half a day.

## Not doing, and why

- **MoneyPrinterV2, easy-uploader, MoneyPrinterPlus auto-posting:** browser-automated or unofficial
  uploads break platform terms.
- **AI presenters and lip-sync (LatentSync, Wav2Lip, Open-AI-UGC actors):** triggers Instagram's AI-profile
  label rule and FTC fake-testimonial risk in a finance niche.
- **F5-TTS and MusicGen weights:** non-commercial licences.
- **HunyuanVideo:** licence excludes the EU, UK and South Korea.
- **Instaloader or any scraper:** breaks Instagram's terms; use Business Discovery.
- **VoiceStudio:** AGPL, and its activity numbers look inflated; revisit if it proves out.
