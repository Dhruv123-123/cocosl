# Quickstart: from clone to first scheduled post

About 15 minutes on a laptop (macOS, Linux or WSL). You need Python 3.11+ and ffmpeg.

```bash
# 1. Install
git clone https://github.com/Dhruv123-123/cocosl && cd cocosl
python -m venv .venv && source .venv/bin/activate
pip install -e ".[claude]"
brew install ffmpeg            # or: sudo apt install ffmpeg

# 2. Set up a working folder (keeps your data out of the code)
factory init                   # creates .env, brands/, data/
factory demo                   # renders a few sample posts with no keys, so you can see the output

# 3. Add the two keys that matter most (edit .env)
#    ANTHROPIC_API_KEY=...      real scripts instead of placeholders
#    ELEVENLABS_API_KEY=... and ELEVENLABS_VOICE_ID=...   (your own cloned voice), or OPENAI_API_KEY
factory doctor                 # checks ffmpeg, voice, keys, media URL; says what to fix

# 4. Load the two weeks of finished scripts and render them with your voice
factory import launch/money-made-simple/content.json --brand money-made-simple

# 5. Review and approve in the dashboard
factory serve                  # http://127.0.0.1:8000 → Review
```

In the Review page, watch each video, tick every fact you've checked, then **Approve & schedule**.
Posting stays in dry-run until you connect platforms and set `FACTORY_DRY_RUN=0`
(`docs/CREDENTIALS.md`). Until then, download the files from the post page and post them by hand:
that's completely fine for the first weeks, and TikTok requires it until its API audit anyway.

## Daily routine (30 minutes)

| When | Do | Command / page |
|---|---|---|
| Morning | Let the factory fill the queue (or let the worker do it at 07:00) | `factory daily --brand money-made-simple` |
| Morning | Review, fix, approve & schedule 2 posts | Dashboard → Review |
| Midday | Send 5 personalised pitches and due follow-ups | Dashboard → Clients (or `factory pitch today`) |
| Evening | Reply to comments yourself; note questions as new ideas | Dashboard → Ideas |
| Monday | Read the weekly report and do its "Next actions" | Dashboard → Report (`factory report`) |

## Where things are

- `launch/LAUNCH_DAY.md` — the day-one plan (payments, product listing, first pitches, first posts).
- `launch/VERIFY_BEFORE_POSTING.md` — the facts only you can confirm on the day.
- `launch/product*/` — sellable products with listing copy.
- `launch/ugc-service/` — the ad studio's website, prices, pitches and contract.
- `docs/CREDENTIALS.md` — every account and key, in order of how fast it makes money.
- `docs/DEPLOY.md` — putting it on a $5 server so it runs without your laptop.
- `docs/COMPLIANCE.md` — the rules the code enforces and why.
