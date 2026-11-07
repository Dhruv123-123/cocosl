# 90 days of organic growth: Money Made Simple and Scam Decoded

Written 2026-11-07. **Docs only. Organic only, no paid ads.** Day 1 is MMS's launch, by default **Mon 16 Nov
2026**. Scam Decoded starts on day 15, around **Mon 30 Nov**. Both are Dhruv's call (`DHRUV_DECISIONS.md`
row 2b), and every date here moves with them. Day 90 is Sat 13 Feb 2027.

This pulls together the earlier plans and doesn't repeat them: posting volume from `two-brand-launch-plan.md`,
platform rules from `first-100-followers-2026.md`, `instagram-first-30-days.md` and
`youtube-first-1000-subscribers.md`, Pinterest from `pinterest-launch-mms.md`, email from
`email-list-from-zero.md`, and thresholds from `launch_thresholds.json`.

**Targets are our estimates, not benchmarks.** Each has a **floor**: below it, change something. Each also
has a **goal**: at it, things are working. The goals sit below the base case in `revenue-model-2027.md`
(MMS: about 2,500 email subscribers by month 12), because the first three months are the slowest.

## The time budget: 1 hour a day for both brands

| Block | Minutes a day | What |
|---|---|---|
| Replies, MMS | 15 | Comments in the first hour after each post, plus DMs |
| Replies, Scam Decoded (from day 15) | 15 | The same |
| Posting by hand | 10-15 | TikTok (about 2 minutes a post) and anything the scheduler can't do |
| Review queue | 10-15 | Approve the next day's posts in `factory serve` |
| **Total** | **about 50-60** | |

Weekly extras, outside the hour: the Saturday recording session (1-2 hours, `LONG_VIDEO_RECORDINGS.md`) and the
Monday 20-minute numbers check (`check_thresholds.py`).

## Weekly targets

### Money Made Simple (day 1 = Mon 16 Nov)

| Week | Dates | Posting | Floor / goal at the end of the week |
|---|---|---|---|
| 1-2 | 16-29 Nov | 5 Shorts and Reels, 3 carousels, 1 long video, 4 pins a week. TikTok gets each Short | YouTube 10 / 40 subscribers. Instagram 30 / 100 followers. TikTok 50 / 200. Email 10 / 40. **No change before day 14** unless a stop rule fires |
| 3-4 | 30 Nov-13 Dec | The same, plus 7 pins a week. **Cross-promotion starts** (below) | YouTube 30 / 100. Instagram 80 / 250. TikTok 150 / 500. Email 40 / 120 |
| 5-8 | 14 Dec-10 Jan | The same, plus 10-14 pins a week. Year-end and "money reset" topics. **Day-30 review** on 15 Dec | YouTube 60 / 200. Instagram 150 / 450. TikTok 300 / 900. Email 100 / 250. Pinterest 3K / 10K monthly impressions |
| 9-13 | 11 Jan-14 Feb | Steady. January is peak season for budgeting searches and products. **Day-60 review** on 14 Jan. **Day-90 review** on 13 Feb | **Day 90:** YouTube 100 / 300. Instagram 200 / 600. TikTok 400 / 1,200 (the bio link unlocks at 1,000). Email 150 / 400. Pinterest 5K / 20K impressions a month |

### Scam Decoded (day 1 = about Mon 30 Nov)

| Week | Dates | Posting | Floor / goal |
|---|---|---|---|
| 1-2 | 30 Nov-13 Dec | 5 Shorts and Reels, 3 carousels, 1 long video a week (from the recorded originals) | YouTube 10 / 40. Instagram 20 / 80. TikTok 50 / 200. Email 10 / 30 |
| 3-6 | 14 Dec-10 Jan | The same. Holiday-shopping and delivery scams are in season. Day-30 review on 29 Dec | YouTube 40 / 120. Instagram 80 / 250. TikTok 200 / 600. Email 50 / 150 |
| 7-11 | 11 Jan-14 Feb | Steady. Tax-season and IRS impostor scams from mid-January. Plan the NCPW week (28 Feb-6 Mar) | **Day 76:** YouTube 80 / 250. Instagram 150 / 450. TikTok 350 / 1,000. Email 100 / 300 |

Scam Decoded's day 90 falls around 27 Feb, the eve of NCPW, which is a good day to review it.

**Why these numbers:** the only big 30-day dataset found a median of 346 Instagram followers, but that was a
growth vendor's paying customers (`instagram-first-30-days.md`). Organic accounts with one post a day usually
grow slower, so our Instagram goal for day 30 is about 250. YouTube subscribers trail views on a new
channel, and long videos earn most subscribers (`youtube-first-1000-subscribers.md`). Email follows from about
2% of site visitors (`email-list-from-zero.md`).

## Cross-promotion between the two brands

The audiences overlap where money meets safety: credit freezes, fake bank calls, account security, protecting
parents. The rule is to cross-promote **only where the topic is genuinely shared**. Each brand keeps its own
voice, and neither turns into an ad for the other.

| When | What | Where |
|---|---|---|
| Week 3 (Scam Decoded's week 1) | MMS posts one Story (and a YouTube Community post once Community is available on the channel): "We started a sister channel that decodes one scam a minute" | MMS Instagram Story; YouTube Community (check availability in Studio) |
| Every 2 weeks from week 3 | **One collab carousel**, posted by both accounts as an Instagram Collab: "Freeze your credit in 10 minutes" (both packs have it), "5 locks every account should have", "Is your savings app actually insured?" | Instagram Collab, so it counts once and shows on both grids |
| Every long video | An end screen and a description line pointing at the sister channel's matching video. MMS "Freeze your credit" ↔ Scam Decoded "Credit freeze walkthrough" | YouTube end screens (set by hand) |
| Every Short where it fits | A related-video link to the other channel's long video, when that's the best next video | YouTube Shorts related link |
| Email | One line in each brand's welcome email 4 or 5: "Our sister newsletter, a weekly scam alert." Never add people to the other list automatically. They click and confirm themselves | Sender, separate groups (`sender-setup-guide.md`) |
| Free tools | The MMS tools hub links the scam checker, and the scam checker's results page links the budget tools | PR #8 apps |
| Never | Reposting the other brand's video, follow-for-follow between them, or tagging the other account on unrelated posts | — |

A cross-promotion is working if the sister account gets **5% or more of its new followers** in the 48 hours
after a collab. Check Insights → Followers. Below 2% three times running, cut collabs to monthly.

## If the time goes over an hour a day: what to cut, in order

Cut from the top. Stop when the hour fits again. Keep the order the same for both brands.

| Order | Cut | What it saves | Why it's first |
|---|---|---|---|
| 1 | **Facebook Reels** (MMS only; Scam Decoded's brand file has no Facebook account) | About 10 min a day. Each post needs the AI-info toggle set by hand | MMS's audience is in their 20s and mostly elsewhere, and this is the most manual work per post. If Scam Decoded ever adds Facebook, keep it: its 35-70 audience is there |
| 2 | **X and Threads threads** | About 5-10 min a day | Low reach for new accounts, and no commerce |
| 3 | **TikTok-only long cuts** (the 60-90 second versions) | About 5 min a day | Post the same Short instead; still post TikTok by hand |
| 4 | **Instagram Stories** beyond one a day | About 5 min | Stories mostly reach existing followers |
| 5 | **Pinterest down to 4 fresh pins a week** | About 10 min a week | The native scheduler holds 10, so batch them on Mondays |
| 6 | **Scam Decoded long video from weekly to every two weeks** | About 1 hour of recording a fortnight | Shorts keep going. Only do this after cuts 1-5 |
| 7 | **Replies down to 10 minutes a brand**, answering questions only | About 10 min a day | Last, because replying is the one free lever with data behind it (+21% engagement on Instagram) |

**Never cut:** the review queue (nothing posts unchecked), the weekly MMS long video (YouTube's main
subscriber source), the welcome emails (they're automated), and the Monday numbers check.

**If it's still over an hour after cut 7,** pause Scam Decoded's posting for two weeks rather than doing
both brands badly. The launch playbook's stop rules say the same ("launch fewer brands", `launch-playbook.md`).

## The three reviews

| Day | Date (MMS) | Look at | Decide |
|---|---|---|---|
| 30 | Tue 15 Dec | `check_thresholds.py` on day-30 numbers; the top 3 posts by sends and saves | Formats: more of what's sent and saved, less of what isn't. No brand changes |
| 60 | Thu 14 Jan | The same, plus email growth and the first product sales | Whether brand 3 (1099 Money) can start (the week-8 gates are checked about 10 Jan) |
| 90 | Sat 13 Feb | Every floor above | Under the floor on 3 or more platforms: fix hooks and topics first, then drop the weakest platform. Don't restart accounts (`instagram-first-30-days.md`) |

## Sources

This plan uses the dated sources already cited in the files named above. It adds no new outside numbers.
All targets are our estimates.
