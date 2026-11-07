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

New here? **`docs/QUICKSTART.md`** gets you from clone to first scheduled post in 15 minutes. Then read **`launch/LAUNCH_DAY.md`** (the plan for day one) and **`docs/CREDENTIALS.md`** (the steps
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

Ready-made launch material lives in `launch/`: two weeks of scripts for the example finance brand,
a sellable product (guide PDF + spreadsheet), the ad studio's website, rate card, pitch templates,
contract template and the launch-day plan.

## Everyday commands

```bash
factory daily --brand money-made-simple     # ideas + 2 drafts into the review queue (never auto-approves)
factory review                              # what's waiting
factory approve 12 --yes-i-checked --schedule
factory publish                             # post what's due (dry run until FACTORY_DRY_RUN=0)
factory insights --brand money-made-simple --rescore
factory repurpose 15                        # long video → Shorts + carousel
factory import launch/money-made-simple/content.json --brand money-made-simple
factory clients import --file leads.csv && factory pitch draft && factory pitch export
factory order create --client 3 --package starter && factory order invoice --id 1
factory revenue report
factory auth youtube | tiktok | meta        # connect accounts
factory renderq revoice                     # re-voice silent renders once KOKORO_URL (or another voice) is set
factory status                              # credentials, queues, worker heartbeat, anything needing you
factory doctor [--online]                   # is this install ready to make and post content?
factory preflight --scheduled               # check queued media against each platform's limits (runs automatically too)
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
