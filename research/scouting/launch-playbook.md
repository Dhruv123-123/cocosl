# First 30 days: launch playbook for all four brands

Written 2026-11-07. **Docs only. No account has been made and nothing has been posted.** Each rule cites
the platform's own page where one exists. Where a platform publishes no number (most don't say how often to
post), the figure comes from a large third-party study and is marked as such. Anything marked **practice**
is common creator advice with no official source. It's here because it's cheap and safe, not because a
platform requires it.

It builds on the other files in this folder: `domains-and-names.md` (names, handles), `newsletter.md`
(the email tool, which is still Dhruv's call), `distribution.md` (the 30-day community plan),
`youtube-monetization.md` and `tiktok-instagram-monetization.md` (the AI and originality rules), and
`thank-you-offers.md`.

## TL;DR

1. **Stagger the brands.** Launch Money Made Simple and 1099 Money in week 1. 1099 Money goes first
   because the 15 Jan 2027 quarterly tax payment is its best moment. Scam Decoded follows in week 2, and
   Dinero Simple in week 3, once a native speaker has checked the Spanish. Four new brands on the same day
   means four times the setup mistakes, and nobody can keep up with replies to all of them.
2. **Order of operations: domain → email → site → accounts → API apps.** Everything downstream (the email
   sending domain, the Pinterest claim, Search Console, the bio links) needs the final domain.
3. **Two API gates take the longest, so apply in week 1:**
   - Until TikTok approves our app, every post it publishes is **private** (`publish/tiktok.py`).
   - YouTube API projects that haven't been verified upload as **private** too.

   Post by hand in the apps until both clear.
4. **Ramp, don't flood.** Week 1 is about half the eventual cadence. YouTube's spam policy bans using
   automation "to flood our platform with repetitive content", and TikTok bans accounts run "in bulk" or
   "through unauthorized automation". Our steady state is the cap we already set: at most 1 long video and
   1 Short a day per channel.
5. **Every brand needs about 15 minutes a day of a real person replying.** Comments are where new accounts
   build trust. They're also the one thing the factory can't do for us, and shouldn't.

## 1. The rules that shape the plan

| Platform | What the platform says | What it means for the launch | Source |
|---|---|---|---|
| **YouTube** | Standard features come with a new channel. **Phone verification** unlocks intermediate features: videos over 15 minutes, custom thumbnails, live on desktop. **Channel history or ID/video verification** unlocks advanced features: clickable links in long-form descriptions, **pinned comments**, chapters, monetization | Verify the phone on day 1, or the 6-10 minute explainers and custom thumbnails fail. Pinned comments and description links come later, so put the link in the channel banner and the "about" section until then | [YouTube Help: feature access](https://support.google.com/youtube/answer/9890437) |
| **YouTube** | Spam policy: no automation "to flood our platform with repetitive content" ("a few variations of a video is ok"); no "identical or similar 'check out my channel' messages across hundreds of videos"; "It's okay to ask viewers to like, comment, or subscribe." 3 strikes in 90 days can end a channel | Never comment-promote on other channels. Ramp the upload count. Vary the structure from video to video (`youtube-monetization.md`) | [YouTube Help: spam, deceptive practices and scams](https://support.google.com/youtube/answer/2801973) |
| **YouTube API** | Uploads through `videos.insert` from **unverified API projects** are restricted to private | Apply for the API audit in week 1. Until it clears, the factory uploads as private and a person publishes in Studio, which `YT_PRIVACY=private` already does | YouTube Data API revision history, linked in `publish/youtube.py` |
| **TikTok** | Not allowed: accounts operated "in bulk" or "through unauthorized automation"; using "multiple accounts to intentionally bypass our rules" (several accounts are fine "for authentic creative expression"). Not eligible for For You: "unoriginal or reproduced content… without any new or creative changes", "extremely short clips", content containing QR codes | One account per brand is fine. Never post the same video on two brand accounts. No QR codes in end cards | [TikTok Community Guidelines: integrity and authenticity](https://www.tiktok.com/community-guidelines/en/integrity-authenticity) |
| **TikTok API** | An app that hasn't passed TikTok's audit can only post as `SELF_ONLY` (private) | Submit the app for audit in week 1. Post by hand from the TikTok app until then | `publish/tiktok.py` (cites TikTok's Content Posting API docs) |
| **Instagram API** | 100 API-published posts per rolling 24 hours (a carousel counts as 1) | Not a constraint at our volume. The account must be a professional (Creator or Business) account | `publish/instagram.py` (cites Meta's content-publishing docs) |
| **Email (Gmail)** | "A consistent sending volume is particularly important for new domains." "Increasing your sending volume too quickly can result in delivery issues"; after a deferral, increase "with a common daily increase of 25% to 100%". Keep the Postmaster spam rate "below 0.1%". Set up SPF and DKIM, then DMARC. Use one-click unsubscribe | Authenticate the domain before the first send. Send the weekly issue on the same day and time every week. Double opt-in only, so the list stays clean | [Gmail: top sender issues](https://support.google.com/mail/answer/15256272) |

**How often to post:** Instagram, TikTok and Pinterest publish no official numbers, so these are the
best available:
- **Instagram:** "3-5 times per week" is the sweet spot, from 2.1M posts across about 102k accounts
  ([Buffer, Aug 2025](https://buffer.com/resources/how-often-to-post-on-instagram/)).
- **TikTok:** "2 to 5 posts per week" gives the biggest gain per extra post, from 11.4M posts
  ([Buffer, Oct 2025](https://buffer.com/resources/how-often-should-you-post-on-tiktok/)). Median views stay
  flat whatever the frequency. Posting more mostly raises the odds of one breakout.
- **Pinterest:** new accounts "3-5 a week", then 1-3 fresh pins a day (Tailwind, in `pinterest-seo.md`).

## 2. Which accounts to make, in order

Do this per brand, in this order. Each step needs the one before it.

| # | Step | Why this order | Notes |
|---|---|---|---|
| 1 | **Register the domain** (`domains-and-names.md` has the free options) | Everything else points at it | Cloudflare Registrar, auto-renew, WHOIS privacy |
| 2 | **Brand inbox** (`hello@<domain>`) | Every sign-up below uses it, so the brand doesn't depend on a personal Gmail | Turn on 2-step verification with an authenticator app, not SMS |
| 3 | **Email tool** (Sender or Kit, Dhruv's call) + SPF, DKIM, DMARC on the domain | Mail sent before authentication goes to spam, and that history sticks to the domain | `newsletter.md` section 2 |
| 4 | **Point the site at the domain** (Netlify) + **Google Search Console** + submit the sitemap | Search history builds on the domain from day one | `pinterest-seo.md`: no migration later |
| 5 | **YouTube**: a **Brand Account** channel under the brand inbox, then **phone verification** | Unlocks videos over 15 minutes and custom thumbnails | Turn on the altered/synthetic content disclosure habit from the first upload |
| 6 | **Instagram** (professional account, **Creator**) + **Threads** with the same handle | Instagram and Threads share a handle, so take them together | Connect to a Facebook Page (step 7) for the Graph API |
| 7 | **Facebook Page** | Needed for the Instagram API and for Content Monetization interest | Cross-post Reels here from week 2 |
| 8 | **TikTok**: a **personal** account, not Business | Business accounts can never join Creator Rewards (`tiktok-instagram-monetization.md`) | 18+, the brand's own phone number or inbox |
| 9 | **Pinterest** business account + **claim the domain** | Rich pins and analytics need the claimed domain | One board per topic, 5-8 boards to start |
| 10 | **Gumroad** product pages live, with the real prices | The thank-you page and bio links point at them | `thank-you-offers.md` |
| 11 | **API apps**: Google Cloud project for the YouTube Data API (submit the audit), TikTok developer app (submit the audit), Meta app for Instagram | The audits take time. Start them while posting by hand | Keys go in `.env` only |

**One handle everywhere** (`domains-and-names.md`). Take all of them on the same day, even if a platform
won't be used until week 3, so nobody else takes the handle. Fill in the profile right away (picture, bio,
link). An empty profile looks like a bot.

**Account hygiene that keeps new accounts out of spam filters** (practice, unless a source is cited):
- Sign up on a phone in the platform's own app, and verify the phone and email right away.
- Fill in every profile field before the first post: name, bio, link, picture, banner.
- **Don't follow, like or comment in bulk.** Follow 10-20 accounts in the niche over the first few days,
  by hand. TikTok and YouTube both name artificial engagement as a violation.
- **No follow-for-follow, engagement pods, bought followers or "growth services"** (TikTok bans their
  trade outright).
- **Post by hand in the app for the first week,** then move to the factory's API publishing. This also
  fits the API gates above, which force it on YouTube and TikTok anyway.
- **One login per device per brand** for the first week. Switching four new accounts back and forth on
  one phone all day looks like an account farm (practice). After week 1, the apps' account switchers are fine.
- **Never DM strangers.** In finance and scams, "DM me" is the scammer's move (`distribution.md`).

## 3. The 30 days, day by day

**Day 0 is setup, not launch.** "Brand A" is the brand launching that week:
- Week 1: 1099 Money, then Money Made Simple.
- Week 2: Scam Decoded.
- Week 3: Dinero Simple.

Each brand runs its own copy of days 1-14 from its launch day.

### Before day 1 (one sitting per brand, about 2 hours)

- Accounts 1-11 above for 1099 Money and Money Made Simple. For Scam Decoded and Dinero Simple, steps 1-9
  only, to reserve the handles.
- Bank 10 finished videos and 6 carousels per launching brand, all reviewed by a person: the factory makes
  them, Dhruv approves them. Launch week shouldn't depend on that day's render.
- Write a short "about" line on each profile that says the content is AI-assisted and checked by a
  person. That's the same honesty line the site's About page uses.

### Week 1: launch two brands, half cadence

| Day | YouTube | Instagram / Threads | TikTok | Pinterest | Email and site | Engagement (15 min per brand) |
|---|---|---|---|---|---|---|
| **1** | Upload a channel trailer (Short) and 1 long video, by hand in Studio. Add the link to the banner | 1 carousel (the lead magnet's best tip), plus 1 Story with a link sticker to `/free/` | Nothing yet. Watch and comment on 10 videos in the niche | 2 pins to the lead magnet | Test the sign-up form end to end: form, confirm, thank-you page, day-0 email. Send yourself one | Follow 10 accounts in the niche. Reply to every comment |
| **2** | 1 Short | Nothing in the feed; 1 Story | First video, posted by hand in the app (the 65-90 second cut if it's ready) | 1 pin | Check that the Sender/Kit report shows the test email as delivered and authenticated | Leave 5 real comments on others' posts (no links). Reply to everything |
| **3** | 1 Short | 1 Reel (the best Short, re-cut 9:16, no other platform's watermark) | 1 video | Nothing | Nothing | Same as day 2. Answer any DM with help in public where possible |
| **4** | Nothing (rest day) | 1 carousel | Nothing | 1 pin | Nothing | Same |
| **5** | 1 Short | 1 Story | 1 video | Nothing | Nothing | Same |
| **6** | 1 long video | 1 Reel | Nothing | 1 pin | Day 7 email pitch goes to the first sign-ups (automatic) | Same |
| **7** | Nothing | Nothing | 1 video | Nothing | **Review** (below) | **Review** |

Week 1 totals per brand: YouTube 2 long + 3 Shorts; Instagram 2 carousels + 2 Reels + Stories; TikTok 4;
Pinterest 5. That's about half the steady state and inside every source above.

**Day 7 review (30 minutes per brand):** for each platform, write down:
- Views per post, saves and shares, profile visits, and link clicks (UTM-tagged).
- Email: sign-ups, confirm rate, thank-you offer clicks (the Plausible event from `thank-you-offers.md`).
- Any warning: a removed post, an "unoriginal" notice, a "try again later" block, a spam folder hit.

**Any warning means hold that platform's cadence at week 1 levels for another week.**

### Week 2: Scam Decoded launches (its days 1-7 as above); week-1 brands step up

Week-1 brands, per week:

| Platform | Week 2 | Notes |
|---|---|---|
| YouTube | 1 long + 5 Shorts | Turn on factory publishing if the API audit has cleared. Otherwise keep uploading through Studio |
| Instagram | 3 carousels + 2 Reels, Stories most days | Start **Trial Reels** (`IG_TRIAL_REELS`) for one Reel a week: it shows to non-followers first |
| TikTok | 5 videos | Still by hand, until the app audit clears |
| Pinterest | 5-7 pins | Each one a fresh design for an existing URL |
| Facebook Page | Cross-post every original Reel | Original Reels only, never anyone else's clips |
| Email | **First weekly issue**, same day and time every week from now on | Goes to everyone who finished the welcome sequence, excluding those still in it |
| Communities | `distribution.md` days 1-10: read the rules, comment only | Dhruv's own account, no links |

Engagement for week-1 brands stays at 15 minutes a day:
- Reply to every comment within 24 hours. Pin the best question once pinned comments unlock.
- Turn the best questions into next week's video titles (`factory ideas`).

### Week 3: Dinero Simple launches (its days 1-7 as above, Spanish reviewed); first brands reach steady state

Week-1 brands, from day 15:

| Platform | Steady state per brand | Cap |
|---|---|---|
| YouTube | 1-2 long + 1 Short a day | At most 1 long and 1 Short a day (`youtube-monetization.md`) |
| Instagram | 3 carousels + 2-3 Reels a week | 3-5 feed posts a week (Buffer) |
| TikTok | 5-7 a week | 2 a day at most (`max_posts_per_day_per_platform`) |
| Pinterest | 1 fresh pin a day | Tailwind's 1-3 a day for creators with a content system |
| Email | 1 weekly issue | Same day, same time |

Set the factory's per-brand `cadence` block (`brands/<brand>.yaml`) to these numbers on day 15, not
before. Today it's already at `shorts_per_week: 5, long_per_week: 1, carousels_per_week: 3`, with a cap of 2
a day. Week 1's lower numbers come from posting by hand, so nothing in the config has to change for them.

### Days 22-30: measure, cut, double down

| Days | What to do |
|---|---|
| 22-24 | Scam Decoded steps up to the week-2 numbers. Dinero Simple stays at week-1 levels. For each week-1 brand, pick the **top 3 posts by saves and link clicks** and make one new variation of each. That's a new design or a new hook, not a repost |
| 25-27 | Communities: `distribution.md` days 18-24 (first links, only where allowed). If the funnel analytics show a platform sending nobody to the email list after 3 weeks, cut its cadence in half and move the time to the platform that does |
| 28 | **Value per subscriber check** for each launched brand: sales on the thank-you page + day-7 pitch, divided by new subscribers. This is the number the paid-ads gate needs (`paid-acquisition.md`) |
| 29 | Write next month's plan per brand: keep, cut and grow, platform by platform. Note anything that needs Dhruv: narration for the TikTok cut, a sponsor reply, an ad budget |
| 30 | Make sure every account has 2-step verification, the inbox password is in a password manager, and API keys are only in `.env` |

## 4. Engagement routine (15 minutes a day per brand, from day 1)

Do these in order, and stop when the 15 minutes are up:
1. **Reply to every comment on our own posts,** newest first. Use real answers, not "Thanks!". If a
   question needs a full answer, say "I'll make a video on this" and add it to the idea list.
2. **Answer DMs in public where possible** ("Good question, I answered it here: <post>"). Never ask anyone
   for account details, and never offer one-to-one money help.
3. **Leave 5 comments on posts by creators in the niche** (`creators.md` has 20). Each one should add
   something: a number, a source, a caveat. No links and no "check out my page". YouTube's spam policy
   names exactly that.
4. **One Story or community post** asking the audience a question: a poll, or "what bill went up this
   month?". YouTube says asking for engagement is fine, but forcing it through Polls isn't.
5. **Log one thing that worked** in the day's notes: a comment that got replies, a hook that held people.

Four brands × 15 minutes is an hour a day. If that's too much, launch fewer brands. Don't cut the
engagement.

## 5. Stop rules

| Signal | Action |
|---|---|
| Any removed post, strike, or "unoriginal" or "reused content" notice | Stop automated posting on that platform for 7 days. Read the notice and fix the cause (`youtube-monetization.md` lists the fixes). Appeal only if it's wrong |
| An action block ("try again later", follow or comment limits) | Stop all likes, follows and comments on that account for 48 hours. Then go back to half the previous activity |
| Email spam rate over 0.1% in Postmaster Tools, or bounces over 2% | Pause the weekly issue. Check the sign-up source and the confirm step. Resend to engaged readers only |
| A post's comments say it's wrong or misleading | Correct it in a pinned comment the same day. If the error is material, take the post down |
| An account gets suspended | Appeal once through the official form. Never make a replacement account (TikTok calls that bypassing enforcement) |

## Open questions for Dhruv

1. Is the launch order right: 1099 Money and Money Made Simple first, then Scam Decoded, then Dinero
   Simple?
2. Can you give about 15 minutes per brand per day to replies? If not, launch two brands this month,
   not four.
3. The domain and email tool decisions (`domains-and-names.md`, `newsletter.md`) block steps 1-4, so
   nothing launches until those are settled.
