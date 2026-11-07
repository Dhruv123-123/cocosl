# Scouting: what's working in AI content income (Nov 2026)

Researched 2026-11-07 for the Money Made Simple brand. Scope: which Instagram formats and faceless
accounts are actually growing, and which open-source GitHub repos could plug into the `contentfactory`
pipeline. Competitor and affiliate research lives elsewhere in `research/`; this folder doesn't repeat it.

**How this was gathered.** Public reporting and platform docs via web search, and GitHub's search API
for repo metadata (stars, forks, licence, commit and issue counts over the last 90 days). Nothing was
scraped from Instagram, and no account was logged into. Follower counts quoted here come from the
third-party sites cited, not from our own collection. To track accounts ourselves we can use Instagram's
official Business Discovery API (see `watchlist.py`).

## The short version

1. **Instagram now rewards original, saveable explainers, and quietly punishes everything "slop" relies on.**
   Since 30 Apr 2026 accounts that are mostly reposts are classed as aggregators and dropped from Explore
   and recommendations (rolling 30-day check). Since 31 Aug 2026 profiles that feature an AI-generated
   person must carry an "AI-generated profile" label or lose reach. Meta's Facebook payout program demotes
   and demonetizes unoriginal pages. Our model (original scripts, illustrated carousels, faceless voice-over
   reels, no AI persona) is on the right side of all three.
2. **Carousels are our best format on Instagram right now.** In Socialinsider's 2026 benchmark (67.5M posts,
   579K business accounts) carousels lead engagement (0.50% vs 0.48% for Reels) and, for 100K-1M accounts,
   average more views per post than Reels (35.4K vs 16.0K). Our carousel renderer is already the strongest
   part of the pipeline; post more of them.
3. **The biggest "slop" wins are real but don't transfer to finance.** Fruit Love Island hit 3M+ TikTok
   followers in 9 days (Mar 2026), then TikTok removed episodes and it ended in 15 days. Huge reach, no
   monetization story, high removal risk. In finance, trust is the product; absurdist AI and fake AI
   "advisors" work against affiliate and product sales.
4. **Free local voice unblocks the 16 videos waiting on a voice.** Kokoro-FastAPI (Apache-2.0, actively
   maintained) is now wired in as the `kokoro` TTS provider on main. Kokoro voices are Apache-2.0 licensed, so they're safe to monetize.
5. **Correction to our earlier stack note:** F5-TTS's code is MIT but its released model weights are
   non-commercial (CC-BY-NC). Don't use F5-TTS for monetized content. Use Kokoro, Chatterbox (MIT, adds an
   inaudible watermark) or Qwen3-TTS (Apache-2.0).
6. **Don't plug in any of the "MoneyPrinter"-style all-in-one bots wholesale.** The popular ones either
   upload through browser automation (against platform terms), are AGPL (would force us to open-source the
   whole factory if we ran a modified copy as a service), or produce stock-footage-plus-TTS videos that
   Meta's and YouTube's originality rules now demote. Borrow their ideas and individual components instead.

## Files

| File | What it is |
|---|---|
| [`instagram-formats.md`](instagram-formats.md) | Platform rule changes, format data, account types that are growing, and what to make for Money Made Simple |
| [`github-repos.md`](github-repos.md) | 56 repos scored for licence, health and fit, plus 16 more in round 2 (captions, B-roll, thumbnails, scheduling, clipping) |
| [`integration-plan.md`](integration-plan.md) | Ranked changes to cocosl, each with the file it touches and effort |
| [`creators.md`](creators.md) | 20 finance and scam-awareness creators: hooks, formats, cadence, how they make money |
| [`software-ideas.md`](software-ideas.md) | 10 small software products ranked, with demand evidence, competitors, pricing, build effort and how each makes money |
| [`distribution.md`](distribution.md), [`distribution-drafts.md`](distribution-drafts.md) | Where each brand's audience gathers off the big platforms, the self-promotion rules, a 30-day plan, and draft posts (nothing posted) |
| [`newsletter.md`](newsletter.md) | beehiiv vs Kit vs MailerLite (cost at 0-10k, ad network, paid recommendations, payout per subscriber); a free-plan comparison with Sender and Brevo after Kit Free dropped sequences (recommendation now Sender Free, Dhruv's call); exact setup and automations for the existing sequences, and 20 swap partners |
| [`youtube-monetization.md`](youtube-monetization.md) | YouTube money beyond AdSense: sponsors that fit 1k-10k finance channels and their rates, the inauthentic-content and AI-label rules audited against our pipeline (with fixes), and Shopping/Amazon eligibility |
| [`tiktok-instagram-monetization.md`](tiktok-instagram-monetization.md) | TikTok Creator Rewards (1-minute rule), Subscriptions and Shop; Instagram bonuses, Subscriptions, Gifts and Facebook Content Monetization; both platforms' AI and originality rules audited against our formats, with fixes |
| [`pinterest-seo.md`](pinterest-seo.md) | Pinterest for finance (fresh pins, standard vs video, cadence, AI labels), Google's scaled-content, thin-affiliate and AI rules, and an audit of the Money Made Simple site (PR #4) with measured duplication per section and fixes |
| [`domains-and-names.md`](domains-and-names.md) | .com availability (RDAP) for all four brands with 5 unregistered options each, the handle plan, and name conflicts (Scam Shield is a live T-Mobile trademark; use Scam Decoded) |
| [`paid-acquisition.md`](paid-acquisition.md) | Paid ads math: net and break-even CPA per product, value per subscriber, Meta/Pinterest/Reddit finance CPCs, the gate before spending anything, and a $100 Meta test with kill rules (docs only, nothing spent) |
| [`thank-you-offers.md`](thank-you-offers.md) | Paid recommendations compared (Kit Creator Network, SparkLoop Partner Network, beehiiv): pay per subscriber, minimum list size, fees, setup. Thank-you page rules, the offer per brand, and ready copy for all four (Spanish needs review). Corrects `newsletter.md`: Kit paid recommendations need the Creator plan |
| [`launch-playbook.md`](launch-playbook.md) | First 30 days for all brands: staggered launch order, which accounts to make first (domain → email → site → accounts → API audits), new-account hygiene, day-by-day week 1 and cadence ramps per platform, a 15-minute daily engagement routine, and stop rules, citing each platform's own guidance |
| [`api-applications.md`](api-applications.md) | TikTok and YouTube API access. TikTok: don't apply (its guidelines rule out tools that upload to accounts "you or your team manages"); post by hand instead. YouTube: no audit or Google verification needed for personal use since Nov 2026; setup checklist, plus use-case text, scope justification and demo script kept on file. Privacy policy section and terms page drafts |
| [`meta-pinterest-api.md`](meta-pinterest-api.md) | Instagram, Facebook and Pinterest APIs for our own accounts: Meta Standard Access works for app-role users with no App Review; rate limits; setup. Pinterest: Trial access is sandbox-only (Standard needs an OAuth demo video), each scheduled pin must be chosen by a person, and API data may not be stored |
| [`faceless-teardown.md`](faceless-teardown.md) | Teardown of 5 faceless money accounts (Economics Explained, How Money Works, WhiteBoard Finance, The Swedish Investor, Personal Finance Club): cadence, formats, title hooks, sponsors and products, what not to copy, and 10 concrete changes for our brands. Added to `watchlist.csv` |
| [`sponsor-kit.md`](sponsor-kit.md) | Sponsor readiness: the 7-point gate before any pitch, a CPM rate card formula with worked prices, a media kit template with per-brand lines, 40 finance-adjacent brands seen sponsoring faceless channels (plus a do-not-pitch list), and 6 email drafts. Nothing sent |
| [`hooks.md`](hooks.md) | 30 hook templates, now used by the writer (`src/contentfactory/hooks_library.json`) |
| [`repos.csv`](repos.csv) | Raw repo metadata pulled 2026-11-07 |
| [`watchlist.csv`](watchlist.csv), [`watchlist.py`](watchlist.py) | Accounts to watch, and a script that snapshots their public follower and engagement numbers through the official Business Discovery API |

## Top 5 actions, in order

1. Voice the 16 waiting videos with Kokoro (the `kokoro` TTS provider on main: `docker compose --profile kokoro up`, set `KOKORO_URL`).
2. Turn on Trial Reels (`IG_TRIAL_REELS=SS_PERFORMANCE`, added in this PR) so new Reels go to non-followers first as Trial Reels and only graduate if they perform. Ideal for a new account testing hooks.
3. Replace estimated caption timing with word-level timestamps from faster-whisper or stable-ts (both MIT).
4. Shift the weekly mix towards carousels (5 per week instead of 3), keeping Reels for hooks and reach.
5. Start the Business Discovery watchlist weekly so we measure which accounts in our niche are growing, rather than trusting listicle numbers.
