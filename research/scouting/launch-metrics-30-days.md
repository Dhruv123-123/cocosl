# The first 30 days after launch: what to watch, and when to change something

Written 2026-11-07. **Docs only.** It turns the stop rules in `launch-playbook.md` and the benchmarks in
this folder into numbers that can be checked each week. The thresholds are in
[`launch_thresholds.json`](launch_thresholds.json). [`check_thresholds.py`](check_thresholds.py) checks a
`factory stats` scorecard (plus a small file of numbers typed in by hand) against them and prints what to
change.

## TL;DR

- **One review a week per brand, on Mondays, about 20 minutes.**
  1. Download the exports and run `factory stats import`.
  2. Type 15-20 numbers into `manual.json`.
  3. Run `check_thresholds.py --day <days since launch>`.
  4. Make **one change per platform per week**, never several at once, or you can't tell what worked.
- **Judge each platform on its own clock.** Instagram and TikTok posts at **72 hours** (about 70% of
  Instagram views come in the first 3 days). Etsy listings at **14 days**. YouTube CTR after **1,000
  impressions**. Pinterest at **30 days**, because it's slow.
- **Every threshold needs a minimum sample** (the `min` in each rule). Below it, the rule stays silent. 50
  visits is noise, not a result.
- **Three severities:**
  - **stop:** pause and fix today. A platform warning, email bounces over 2%, spam complaints over 0.1%.
  - **change:** one fix this week.
  - **watch:** note it, and act if it holds for 2 weeks.

## 1. What to watch, platform by platform

| Platform | The numbers that matter in month 1 | Where to get them | Threshold (rule id) | Benchmark behind it |
|---|---|---|---|---|
| **YouTube** | Impressions, impressions CTR, watch hours, subscribers per video | Studio export → `factory stats import` | CTR < 2% after 1,000 impressions, from day 14 (`yt-ctr-low`). Under 500 impressions by day 21 (`yt-no-impressions`). Under 50 watch hours by day 30 (`yt-watch-pace`, watch) | YouTube: "Half of all channels and videos on YouTube have an impressions CTR... between 2% and 10%". New videos vary more, so don't judge in week 1 ([YouTube Help](https://support.google.com/youtube/answer/7628154)). YPP needs 8,000 hours a year (`revenue-model-2027.md`) |
| **TikTok** | Views per video, average watch time, shares | TikTok Studio export → `factory stats import` | Average under 200 views after 10+ posts, from day 21 (`tt-views-low`) | Our judgment. A new account's videos go to a small test audience first, so a 10-post average is the first fair read |
| **Instagram** | Reach, **sends per 1,000 reach**, non-follower share of reach, saves | Professional dashboard, typed into `manual.json` | Sends under 2 per 1,000 reach after 2,000 reach (`ig-sends-per-reach`). Non-followers under 30% of reach (`ig-nonfollower-reach`, watch) | Mosseri: sends drive reach to new people; judge at 72 hours (`instagram-growth-2026.md`, `finance-formats-nov-2026.md`). The 2-per-1,000 bar is ours, to calibrate after month 1 |
| **Pinterest** | Impressions, saves, outbound clicks | Pinterest Analytics, typed in | Under 10 saves after 20+ pins at day 30 (`pin-saves`). Under 20 outbound clicks per 5,000 impressions (`pin-outbound`) | Pinterest's distribution is slow and keyword-driven (`pinterest-playbook-2026.md`). Thresholds are ours |
| **Site** | Visitors by UTM campaign, sign-ups, outbound clicks | Plausible export → `factory stats import` | Sign-ups under 2% after 200 visitors, from day 14 (`site-signup-rate`). Under 100 visitors by day 30 (`site-no-traffic`, watch) | Our judgment for a free-lead-magnet page. Calibrate after month 1 |
| **Etsy** | Visits per listing, shop conversion rate, favourites | Shop Manager → Stats, typed in | Over half the listings under 20 visits in 14 days (`etsy-no-visits`). Conversion under 0.5% after 300 visits, from day 21 (`etsy-conversion`) | New shops typically convert 0.5-2%, and established ones 2-3% ([ListingView, Jun 2026](https://listingview.io/blogs/what-is-a-good-conversion-rate-on-etsy-in-2026); no dataset named, so a rough guide). Few visits means SEO; visits without sales means photos, copy or price (`etsy-seo-playbook.md`) |
| **Gumroad** | Product page views, conversion | Gumroad analytics, typed in | Under 1% after 150 views, from day 21 (`gumroad-conversion`) | Our judgment. Traffic is mostly warm (bio and email), so 1% is a low bar |
| **Email** | Welcome open rate, click rate, unsubscribes, bounces, complaints | The email tool's report, typed in | Welcome opens under 30% (`email-open`). Clicks under 2% (`email-click`). Unsubscribes over 0.5% per send (`email-unsub`). **Bounces over 2% (`email-bounce`, stop). Complaints over 0.1% (`spam-complaints`, stop)** | [Mailchimp benchmarks](https://mailchimp.com/resources/email-marketing-benchmarks/), Business & Finance: 31.35% open, 2.78% click, 0.15% unsubscribe (data to Dec 2023; opens inflated by Apple Mail Privacy). Google's bulk-sender rules: keep spam complaints under 0.1%, never 0.3% |
| **All** | Any strike, warning, "reduced distribution" or monetization notice | The platform's own notices | Any at all (`platform-warning`, stop) | `launch-playbook.md` stop rules |

**Money numbers** (orders, revenue, affiliate clicks) are in `factory report`. In month 1 they're too small
to judge, so they're tracked but don't trigger changes. They feed the month-3 re-run of
`revenue_model.py`.

## 2. How to run it each week

```bash
# 1. Import what factory stats already reads (YouTube, TikTok, Plausible exports)
factory stats import --brand money-made-simple "Table data.csv" tiktok.csv plausible/*.csv

# 2. Save the scorecard as JSON
python3 -c "import json; from contentfactory.config import Settings; from contentfactory.pipeline import Factory; \
from contentfactory import stats; f = Factory.create(Settings.load(None)); \
print(json.dumps(stats.scorecard(f, 'money-made-simple'), default=str))" > card.json

# 3. Check it, with this week's hand-typed numbers
python3 research/scouting/check_thresholds.py --day 14 --scorecard card.json --manual manual.json
```

**`manual.json` template** (leave out anything you don't have; rules without data stay silent):

```json
{
  "instagram": {"reach": 0, "sends_per_1000_reach": 0, "nonfollower_reach_share": 0},
  "pinterest": {"pins": 0, "impressions": 0, "saves": 0, "outbound_clicks": 0},
  "etsy": {"visits": 0, "conversion_rate": 0, "listings_under_20_visits_share": 0},
  "gumroad": {"views": 0, "conversion_rate": 0},
  "email": {"welcome_sends": 0, "welcome_open_rate": 0, "sends": 0, "click_rate": 0,
            "unsubscribe_rate": 0, "bounce_rate": 0, "complaint_rate": 0},
  "any": {"platform_warnings": 0}
}
```

Rates are fractions (0.31, not 31). YouTube CTR comes from `factory stats` as a percentage (2.0), which
matches YouTube Studio.

**Tested:** a sample scorecard and manual file fire the expected 8 rules on day 30 and none on day 3, and
a scorecard from an empty factory home fires nothing.

## 3. Calendar for the first 30 days

| Day | What to look at | Typical change |
|---|---|---|
| **1-3** | Stop rules only: warnings, bounces, complaints, broken links, and posts that didn't go live | Fix and resend. Don't judge content yet |
| **7** | First Monday review. Instagram and TikTok posts older than 72 hours. Email unsubscribes | Drop the weakest hook mechanic; keep posting at half cadence (`launch-playbook.md`) |
| **14** | YouTube CTR (if over 1,000 impressions), site sign-up rate, Etsy visits per listing, welcome opens | One title or thumbnail change; Etsy SEO fixes; form placement |
| **21** | TikTok after 10+ posts, Etsy and Gumroad conversion, email clicks, Instagram non-follower share | Hooks; first photos and copy; one email CTA |
| **30** | Everything, including Pinterest and watch-hour pace. Re-run `revenue_model.py` with real numbers | Pick 2 formats to double and 1 to drop for month 2 |

## 4. Making it part of `factory stats` later (optional, for the factory thread)

These thresholds are research, so they live here, not in `src/`. To make them a real command later:
1. Add Instagram, Pinterest, Etsy, Gumroad and email-tool CSV parsers to `stats.py`. Each of these
   platforms has an export, so `manual.json` would go away.
2. Add `factory stats check --day N`. It would run `check_thresholds.evaluate()` on `stats.scorecard()`,
   reading rules from the brand yaml (`thresholds:`) with this JSON as the default.
3. Show fired rules on the `/today` page and in the weekly HTML report (`weekly_html.py`).

## Open questions for Dhruv

1. Are you happy with one weekly review on Mondays (about 20 minutes per brand at first, less once the
   exports are automated)?
2. The thresholds marked "our judgment" (TikTok 200 views, sign-up 2%, Pinterest saves) should be reset after
   month 1 using our own medians. Agree?
