# Free tools round 4: caption styles, B-roll sources, animated charts, Remotion alternatives

Written 2026-11-07. **Docs only. Nothing installed or vendored.** Licence, stars and last push come from
the GitHub search API (read today). Media licences come from each provider's own page. Rounds 1-3 are in
`github-repos.md` (Remotion, Manim, pycaps, MoneyPrinterTurbo) and `pipeline-tools-round3.md` (Motion
Canvas, editly, MoviePy, ffsubsync), so this round covers what's new and re-checks those picks.

**Where the factory is today:** captions are hand-written `.ass` styles (`media/captions.py`). Charts are
static images from the script's numbers, with optional Manim clips (`FACTORY_CHARTS=manim`,
`media/charts.py`). There's **no stock B-roll source** (`grep pexels src/` finds nothing). Visuals are
cards, images and charts.

## TL;DR: the picks

| Need | Pick | Licence | Why |
|---|---|---|---|
| Remotion alternative | **HyperFrames** (`heygen-com/hyperframes`) | **Apache-2.0** | HTML/CSS/GSAP/Lottie to MP4 through headless Chrome and FFmpeg. "No per-render fees or commercial-use thresholds", unlike Remotion's 3-person limit. 80K stars, pushed today. Ships caption, chart-race and `data-chart` blocks. Node 22+ and FFmpeg |
| Remotion alternative (backup) | **Revideo** (`midrender/revideo`) | MIT | Code-to-video with a headless `renderVideo()` API. Turn off its PostHog telemetry with `DISABLE_TELEMETRY=true` |
| Caption styles | **pycaps** (`francozanardi/pycaps`), re-checked | MIT | CSS-styled word-by-word captions, with a `.word-being-narrated` state, templates, and pops, slides and typewriter effects. Takes our existing timestamps (SRT/VTT/Whisper JSON), so it needs no new transcription. Alpha, not on PyPI; its CSS renderer needs Playwright Chromium |
| Caption timing | **WhisperX** (`m-bain/whisperX`) | BSD-2 | Word-level timestamps; pushed Oct 2026. Already listed as the upgrade in round 3 |
| Animated charts | **Manim CE**, keep | MIT | Already wired into `charts.py` |
| Animated charts (web) | **Vizzu** (`vizzuhq/vizzu-lib`) | Apache-2.0 | Animates *between* chart types (bars to stacked to pie), which suits "where your paycheck goes". JavaScript only, with no video export of its own, so render it inside HyperFrames |
| B-roll | **Pexels API** | Pexels licence (free, commercial OK) | Photos and **video**. 200 requests an hour, 20,000 a month. Must show "a prominent link to Pexels" and credit photographers where possible |
| B-roll | **Pixabay** | Pixabay Content Licence | Free and commercial, no attribution needed. **Not allowed:** selling unaltered copies "on a Standalone basis", using recognisable trademarks commercially, or deceptive use |
| B-roll (public domain) | **US federal agency media** (FTC, CFPB, IRS, NASA) | Usually public domain (works of the US government) | Best for Scam Decoded and 1099 Money. Check each item: some agency pages carry third-party material |

## 1. Remotion alternatives

| Repo | Licence | Stars | Last push | Notes |
|---|---|---:|---|---|
| remotion-dev/remotion | Custom (free up to 3 people, then a company licence) | 71K | today | The reference; the limit is why we look elsewhere |
| **heygen-com/hyperframes** | **Apache-2.0** | 80K | today | Local or Docker; AWS Lambda optional. The Studio app's paid Pro tier only adds HeyGen's AI models, and the framework doesn't need it |
| midrender/revideo | MIT | 4.2K | Jul 2026 | Headless render API; telemetry on by default |
| motion-canvas/motion-canvas | MIT | 19.7K | Jul 2026 | Round 3 pick; editor-first, rendering is less headless |
| nexu-io/html-video | Apache-2.0 | 4.8K | Jun 2026 | Same idea as HyperFrames, smaller |
| Zulko/moviepy | MIT | 15K | Aug 2026 | Python compositing. Overlaps with `media/video.py` |
| mifi/editly | MIT | 5.6K | May 2025 | JSON-to-video, slowing down |
| etro-js/etro | **GPL-3.0** | 1.2K | Nov 2026 | **Avoid** (copyleft) |
| diffusionstudio/core | MPL-2.0 | 1.3K | Nov 2025 | Browser-only (WebCodecs); file-level copyleft |
| ncounterspecialist/twick | No SPDX | 546 | Jun 2026 | **Avoid** until the licence is clear |

**Recommendation:** don't replace the FFmpeg pipeline. Add **HyperFrames as an optional renderer for
motion-graphic beats** (a chart, a "fee eats $18,000" counter, a scam-text mock-up), the same way Manim is
optional today. A beat would render to a short MP4 that `render.py` drops in like a Manim clip
(`Beat.clip`).

## 2. Caption styles

| Repo | Licence | Stars | Notes |
|---|---|---:|---|
| **francozanardi/pycaps** | MIT | 231 | Pick (above). Its `browser` install option uses Google Cloud Speech; don't use that one |
| veedstudio/open-edit | Apache-2.0 | 1.8K | An agent skill that designs captions as HTML. It can transcribe locally with WhisperX, but VEED transcription and AI generation are paid options. An idea source, not a dependency |
| unconv/captacity | MIT | 141 | Shorts captions; last push Jun 2024, so stale |
| tkarabela/pysubs2 | MIT | 447 | A clean way to write `.ass` files, if we keep our own styles |
| smacke/ffsubsync | MIT | 7.9K | Already noted in round 3 |
| ColinGPT9/clips-studio | **AGPL-3.0** | 214 | **Avoid** |

**Cheapest win:** keep `.ass`, and add 2-3 styles pycaps popularised (the current word highlighted in the
brand accent, a one-word "pop" for numbers, and a lower-third for sources) through pysubs2. That needs no
browser in the render path. Try pycaps itself only if those aren't enough.

## 3. B-roll and stock media

| Source | Licence and terms | Fit |
|---|---|---|
| **Pexels API** | Free, commercial use OK. Show "a prominent link to Pexels"; credit photographers where possible; 200/hour, 20,000/month (higher on request); don't build a Pexels clone. Video endpoints are moving to `/v1/videos/` | Generic money B-roll (cards, receipts, laptops). Put the credit in the description |
| **Pixabay** | Free, commercial OK, no attribution. No standalone resale; no commercial use of recognisable trademarks; no deceptive use. "Only the full Content License is legally binding" | Same. **Reject any clip showing a bank or card brand logo** |
| US federal agency media | Usually public domain | FTC and CFPB scam explainers and IRS footage, used with our commentary (Stitch or Remix style, `first-100-followers-2026.md`) |
| Openverse (`WordPress/openverse`, MIT code) | Mixed CC licences per item | Filter to commercial-and-modification licences only, and keep the attribution. The API page didn't load here, so check the limits before using it |

**Rules for us:**
- Stock clips are at most **one beat in three**. YouTube's inauthentic-content rules and Instagram's
  originality rules reward our own visuals (`youtube-policy-review-nov-2026.md`), and MoneyPrinterTurbo-style
  all-stock videos are what those rules target.
- Never use stock people as "our expert".
- Keep a `credits.json` per video listing each clip's source URL and licence.

## 4. Animated charts

| Repo | Licence | Notes |
|---|---|---|
| ManimCommunity/manim | MIT | Keep (in `charts.py`) |
| vizzuhq/vizzu-lib | Apache-2.0 | Morphing charts, rendered via HyperFrames |
| juliangarnier/anime | MIT | 74K stars, pushed this week. Counters and number tickers in HyperFrames |
| airbnb/lottie-web | MIT | Lottie icons. **The animation files have their own licences**, so use only ones we make or that are clearly licensed |
| dexplo/bar_chart_race | MIT | Last push Jun 2024. Bar races in matplotlib, so it's Python and easy, but stale |
| thomasp85/gganimate | No SPDX here (it's MIT on CRAN) | R; not our stack |
| Samsung/rlottie | No SPDX (mixed licences) | **Avoid** |

## 5. What to send to the main thread (in order)

1. **Pexels and Pixabay as an optional B-roll source**, capped at 1 beat in 3, with logo-free clips only,
   a `credits.json`, and a Pexels credit line in the description.
2. **2-3 new `.ass` caption styles** modelled on pycaps (current-word highlight, number pop, source
   lower-third) via pysubs2 (MIT).
3. **HyperFrames (Apache-2.0) as an optional motion-graphics renderer** for chart, counter and scam-text
   beats, beside Manim. Needs Node 22+ in the Docker image.
4. **Avoid list:** etro (GPL-3.0), clips-studio (AGPL-3.0), twick (unclear licence), rlottie (mixed),
   pycaps' Google Cloud option, and Remotion above 3 people without a licence.

## Sources

GitHub search API (licence SPDX, stars, last push), read 2026-11-07;
[HyperFrames README](https://github.com/heygen-com/hyperframes);
[OpenEdit README](https://github.com/veedstudio/open-edit);
[pycaps README](https://github.com/francozanardi/pycaps);
[Revideo README](https://github.com/midrender/revideo);
[Vizzu README](https://github.com/vizzuhq/vizzu-lib);
[Pexels API documentation](https://www.pexels.com/api/documentation/);
[Pixabay licence summary](https://pixabay.com/service/license-summary/).
