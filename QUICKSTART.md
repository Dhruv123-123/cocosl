# Quickstart: install, connect, check, schedule

Ten commands, about 20 minutes. You need Python 3.11+, ffmpeg and git. Nothing posts until you set
`FACTORY_DRY_RUN=0`, so every step below is safe to try.

```bash
# 1. Install (Mac: brew install ffmpeg · Linux: sudo apt install ffmpeg)
git clone https://github.com/Dhruv123-123/cocosl && cd cocosl && python -m venv .venv && source .venv/bin/activate && pip install -e ".[claude]"

# 2. Create .env, brands/ and the database, then put your keys in .env
#    (ANTHROPIC_API_KEY, KOKORO_URL or a voice key, YT_CLIENT_ID/SECRET, TIKTOK_CLIENT_KEY/SECRET)
factory init

# 3. Connect the platforms (each opens a browser once; add --brand <slug> for a brand's own accounts)
factory auth youtube
factory auth meta --token <short-lived-token>     # Instagram, Facebook Page, Threads
factory auth tiktok

# 4. Check the install: ffmpeg, voice, keys, media URL, worker
factory doctor

# 5. Load the scripted month and render it
factory import launch/money-made-simple/content.json --brand money-made-simple

# 6. Review and approve in the dashboard (http://127.0.0.1:8000 → Review), then schedule everything approved
factory serve
factory schedule --all

# 7. One last look before anything goes out: red / yellow / green
factory launch-check
```

## What each colour means

- **Green:** go live: set `FACTORY_DRY_RUN=0` in `.env` and start the worker (`docker compose up -d`, see `docs/DEPLOY.md`).
- **Yellow:** fine in dry run. Usually it's placeholder links (example.com, example.gumroad.com) in the brand
  file. Put your real Gumroad, Stripe and affiliate links in `brands/<slug>.yaml`, then run the check again.
- **Red:** fix before anything posts: a `REPLACE_ME` in a post going out within 14 days, an affiliate post
  without a disclosure, or a broken UTM tag. The report names the post.

## Handy afterwards

| You want to | Run |
|---|---|
| See every brand's schedule in your calendar app | `factory calendar --export output/calendar` (open `calendar.ics`) |
| See calendar, review queue, recordings and launch check on one page | `factory ui` (opens http://127.0.0.1:8000/today, this computer only) |
| Add another brand in 5 minutes | `factory brand new rent-smart --name "Rent Smart" --niche "money for renters" --import` |
| Know what's waiting on you (voice, screen recordings) | `factory recordings` |
| Use your own narration on a video | `factory voice <post id> take.m4a` |
| Check that every real link answers | `factory launch-check --online` |

More detail: `docs/QUICKSTART.md` (daily routine), `docs/CREDENTIALS.md` (each account step by step),
`launch/VERIFY_BEFORE_POSTING.md` (facts only you can confirm).
