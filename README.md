# Content Factory

A one-person AI content studio that runs the whole loop: pick a niche, generate ideas from what people
search for, write and fact-check scripts with Claude, voice and illustrate them, render captioned
vertical videos and Instagram carousels, put everything through a human review queue, publish through
the official Instagram, YouTube, TikTok, Facebook, Threads (or Postiz) APIs, and track what it earns.

It's built around the two income lines that actually pay in 2026 (see `docs/PLAYBOOK.md`):

1. **Niche channels** that turn views into affiliate commissions, product sales and newsletter subscribers.
2. **An AI video ad studio** that sells short spokesperson/demo ads to small brands, with a CRM, pitch
   drafts, invoices and bookkeeping built in.

It's also built to stay monetizable: originality checks, AI disclosures, cadence caps, no fake
testimonials, official APIs only, and nothing posts without your approval (`docs/COMPLIANCE.md`).

## Start here

```bash
pip install -e ".[claude]"        # Python 3.11+, ffmpeg on PATH
factory init                      # creates .env, brands/, data/
factory demo                      # renders sample posts offline, no keys needed
factory serve                     # dashboard at http://127.0.0.1:8000
```

New here? **`QUICKSTART.md`** is the one-page version (ten commands). **`docs/QUICKSTART.md`** gets you from clone to first scheduled post in 15 minutes. Then read **`launch/LAUNCH_DAY.md`** (the plan for day one) and **`docs/CREDENTIALS.md`** (the steps
only you can do: payouts, accounts, API keys).

## What's in the box

| Area | What it does | Code |
|---|---|---|
| Niche & brand | Score niches by ad value, demand, risk, saturation; generate a brand profile; brand kit (logo, banners, bios) | `niche.py`, `brandkit/` |
| Ideas | Trend signals (YouTube autocomplete, Reddit questions), Claude pitches, scoring, de-duplication, learned re-scoring from performance | `ideas.py`, `insights.py` |
| Writing | Research grounding, draft → editor critique → revision, claims to verify, sources | `writer.py`, `research.py` |
| Media | TTS (Kokoro, Piper, espeak, ElevenLabs, OpenAI), images (ComfyUI, OpenAI, Replicate, built-in art), 9:16 and 16:9 video with burned captions, carousels, thumbnails | `media/` |
| Repurposing | One long video → 3 standalone Shorts + a carousel | `repurpose.py` |
| Guardrails | Originality, fake testimonials, disclosures, risky claims, engagement bait, asset rights, cadence | `guardrails.py` |
| Review | Dashboard queue with video/slide preview, caption editing, fact-check gate, approve & schedule | `web/` |
| Publishing | Official APIs with AI labels (`is_aigc`, `containsSyntheticMedia`, `is_ai_generated`), token refresh, retries | `publish/` |
| Analytics | Metrics collection, rollups by format/pillar/platform/hour, feedback into idea scores | `insights.py` |
| Funnel | Link-in-bio page, double opt-in email capture, weekly digest, Stripe/Gumroad sale webhooks | `funnel/` |
| Business | UGC clients CRM, packages & quotes, ad scripts (no fake testimonials), pitch drafts, invoices (PDF), digital products (PDF), affiliate link tracking, P&L, goal tracking | `business/` |
| Ops | CLI, Docker Compose (app, worker, renderer, media host, optional Kokoro voice), multi-brand worker on per-brand clocks, render queue, `factory status` / `/api/status` health, n8n workflow, CI | `cli.py`, `worker.py`, `renderq.py`, `health.py`, `integrations/` |
| Languages | Per-brand `language`/`region` (Spanish built in): writer and idea prompts, on-slide labels, bios, banner, highlights, TTS voice, trend locale, Spanish guardrail patterns, and a native-speaker sign-off (`factory review-gate pass <id> native_review`) | `i18n.py` |
| Hand-off packs | `factory handoff-pack content.json --brand X --out DIR`: slides, thumbnails and caption.txt files with facts to check | `launchpack.py` |
| Spanish brand | Dinero Simple: content plans in `launch/dinero-simple/` (pending native-speaker review) and its own static site with free calculators and a glossary (`sites/dinero-simple/build.py`) | `launch/dinero-simple/`, `sites/dinero-simple/` |

Ready-made launch material lives in `launch/`: two weeks of scripts for the example finance brand,
a sellable product (guide PDF + spreadsheet), the ad studio's website, rate card, pitch templates,
contract template and the launch-day plan. `launch/scam-decoded/` is a second brand (scam and identity-theft
explainers) with Shorts, 60–90s TikTok cuts routed by platform, carousels and a printable product; turn any of
its content files into a postable folder with
`factory launch-pack launch/scam-decoded/content.json --brand scam-decoded --out dist/scam-decoded`.

## Website and email funnel

`site/` is the brand's static website: home, 32 SEO articles, 8 comparison pages, product pages, a quiz,
a newsletter archive with RSS, a free lead magnet (The 7-Day Money Reset PDF), a link-in-bio page and a
10-email welcome sequence that sells the products. It deploys free to Netlify (`netlify.toml`) or GitHub
Pages (`.github/workflows/pages.yml`). See **`site/README.md`**. **`docs/SITES.md`** is the plan for running
every brand's site from this one builder, with per-brand Netlify, domain and Plausible steps.

## Everyday commands

All 81 commands, grouped, are in [docs/COMMANDS.md](docs/COMMANDS.md) (generated from the CLI, so it's always
current). The ones you'll use most:

```bash
# Your routine (about an hour a day, two brands)
factory today --15min                         # the daily routine with today's real items
factory ui                                    # local dashboard (127.0.0.1): Today, review queue, /review/fast keyboard review
factory time log 20 --what review             # log your minutes; `factory time` shows the week vs the one-hour limit
factory weekly-review --save                  # Sunday one-pager: scorecard, time, brand-3 gates, next week's queue, what's blocked on you
factory keyword-check go                      # one sitting: confirm each scheduled title's search phrase in the search box
factory launch-mode two-brand                 # today / reslot / scorecard show only MMS + Scam Decoded
factory triage                                # everything waiting on you, most urgent first

# Make and review content
factory import launch/money-made-simple/content.json --brand money-made-simple
factory pack export --brand money-made-simple --file launch/money-made-simple/month-1/content.json \
  --start 2026-11-21 --days 30 --out month-1/   # content.json → per-platform posting calendar + ready-to-post folders
factory daily --brand money-made-simple       # ideas + 2 drafts into review (never auto-approves)
factory review-gate [list|pass|require|send-back]   # draft → native_review → legal_review → approved
factory approve 12 --yes-i-checked --schedule
factory batch-record                          # recordings grouped into sessions: shot list + teleprompter
factory voice 12 take.m4a                     # your own narration for post 12
factory broll 12 [--apply]                    # optional Pexels/Pixabay B-roll (free keys), max 1 beat in 3, credited
factory motion 12 [--write|--apply]           # optional HyperFrames motion cards for number beats (FACTORY_MOTION=hyperframes)
factory audit-originality --packs             # YouTube inauthentic-content risk per channel
factory launch-check                          # red/yellow/green: links, placeholders, disclosures, caption limits

# Schedule and post
factory reslot [--yes]                        # queued posts onto the current slots, zero collisions
factory export-week <brand> --weeks 4         # one zip per week, posting order, captions ready to paste
factory manual [build|copy <pub>|done <pub> --url]   # TikTok + Pinterest post-by-hand packages
factory publish                               # post what's due (dry run until FACTORY_DRY_RUN=0)

# Measure
factory stats import --brand <slug> *.csv     # YouTube Studio / TikTok / Plausible exports
factory scorecard [--save] [--gate]           # weekly scorecard with stop/change flags; --gate: the five brand-3 gates
factory report --html                         # weekly business report + one-page HTML per brand

# Email
factory sequence-export <brand> --for sender  # welcome emails as a Sender automation
factory subscribers-export <brand> --for sender
factory newsletter --brand <slug> --for kit|sender   # a week of posts as a draft email (never sent)

# Setup and upkeep
factory doctor [--online | --offline]         # is this install ready?
factory backup --archive [--with-media]       # one dated zip; `factory restore <zip>` lists first
scripts/smoke_fresh_clone.sh                  # fresh clone → install → render one post per brand → launch-check
```

`factory --help` lists everything. Run it in production with `docker compose up -d`.

## Tests

```bash
FACTORY_LLM=offline python -m pytest
```

Everything runs offline: an offline LLM provider, silent TTS and built-in art make the whole pipeline
testable without keys.

## Licence

MIT for this code. Content you make is yours; keep licences for any music or stock you add.
