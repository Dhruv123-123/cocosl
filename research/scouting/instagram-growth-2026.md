# Instagram growth for faceless finance accounts, late 2026

Researched 2026-11-07 from Instagram's own posts (creators.instagram.com, about.fb.com) and dated trade press
(linked, with dates). **Docs only. Organic only. Nothing has been posted.** Where sources disagree, both
are given and the check is "look in the app". This adds to `tiktok-instagram-monetization.md`,
`launch-playbook.md` and `meta-pinterest-api.md`.

## TL;DR: what changes for our four brands

1. **Originality is now enforced on carousels and photos, not just Reels** (Instagram, 30 Apr 2026). Accounts
   that mostly repost others' work stop being recommended. Our factory makes its own carousels and Reels, so
   we're fine, **as long as we never repost other creators' clips or screenshots**, even with credit.
2. **5 hashtags maximum per post** (Instagram, Dec 2025). Mosseri says hashtags don't add reach anyway.
   **The factory still allows 30 for Instagram and asks for 5-10.** That's a one-line fix (see section 6).
3. **Sends per reach is the growth number.** Mosseri's top three ranking signals are watch time, likes and
   sends. Sends matter most for reaching new people. Finance is a "send this to your partner" niche, so
   design every carousel to be sent, not just liked.
4. **Trial Reels** test a Reel on non-followers first. They need a minimum follower count (sources disagree:
   200 or 1,000 for professional accounts), so **they won't work in week 1.** Use them from the threshold
   on, for hook tests.
5. **Collabs are the strongest free growth lever left:** up to 5 co-authors, one post on every grid. Our four
   brands can collab with **each other** (MMS × 1099 Money, MMS × Scam Decoded), and with small
   finance creators once we have something to offer.
6. **Broadcast channels come later.** Older help text set a 10,000-follower minimum. Treat it as a month 3+
   feature, check eligibility in the app, and use it for the weekly "one number" check-in and launch
   announcements.

## 1. What Instagram ranks on (official statements)

| Fact | Source |
|---|---|
| "The top three signals that matter most for ranking are watch time, likes and sends." Track average watch time, likes per reach and sends per reach. Likes count more with followers; sends count more with new people | Mosseri, reported by [Social Media Today, 22 Jan 2025](https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/) |
| Accounts that "regularly repost content they didn't create" are "no longer eligible for recommendations", now including photos and carousels. Followers still see their posts | [Instagram, 30 Apr 2026](https://creators.instagram.com/blog/rewarding-original-creators-on-instagram); [TechCrunch, 30 Apr 2026](https://techcrunch.com/2026/04/30/instagram-restricts-reach-of-content-aggregators-in-new-crackdown/) |
| Original = made by you, or third-party content you "materially edited", with additions that "add real value beyond just simply restating or referencing" it. **Not** original: "just adding a border, watermark, subtitles, or a credit in the captions" | same |
| Recovery: regain eligibility when "a significant share" of recent posts are original, on a **rolling 30 days**. Check **Settings → Account Status** | same |
| Hashtags capped at **5** per post or Reel, rolling out from Dec 2025. Mosseri: hashtags "don't work" for reach, but help say what a post is about | [Social Media Today, 18 Dec 2025](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/) |
| Reels can be created up to 20 minutes, but **recommendations to non-followers stop at 3 minutes** | [SocialPilot, Sep 2026](https://www.socialpilot.co/?p=563048), citing a Mosseri post (secondary) |
| "Comment GUIDE to get the link" isn't banned. Instagram said there "haven't been changes to our recommendation guidelines" and tools like ManyChat are fine. Asking for a specific comment *only to inflate engagement* can limit reach | Instagram, reported by [Social Media Today, 5 Jun 2024](https://www.socialmediatoday.com/news/instagram-clarifies-advice-on-single-word-ctas-and-longer-reels/718151/) |
| Viewers can now tune topics ("Your Algorithm") in Reels, Explore and, since mid-2026, Feed. Clear topic signals (on-screen text, caption keywords) help us land in the right interest | [SocialPilot](https://www.socialpilot.co/?p=563048) (secondary) |

## 2. Trial Reels

| Item | Detail | Source |
|---|---|---|
| What | Toggle **Trial** before sharing. The Reel goes to non-followers first, and doesn't show on the grid or to followers, except through DMs or audio, location or filter pages | [Instagram creators blog](https://creators.instagram.com/blog/instagram-trial-reels), launched 10 Dec 2024 |
| Results | After about 24 hours: views, likes, comments and shares, compared with your earlier trials | same |
| Auto-share | Optional: Instagram shares it with followers if it does well, based on views in the first **72 hours**. Or share it by hand in one tap | same |
| Eligibility | Public account, eligible for recommendations. **Minimum followers disputed:** [Planoly, 23 Oct 2026](https://www.planoly.com/blog/how-to-post-a-trial-reel-on-instagram.md) cites the Help Center as 200 for professional accounts and 1,000 for personal ones. [PostFast, Sep 2026](https://postfa.st/blog/instagram-trial-reels) and SocialPilot say 1,000. **Check the toggle in the app** | as linked |
| Losing access | "If your public account is ineligible to appear in recommendations, you will also lose access to trial reels". One more reason never to repost | Planoly, quoting the Help Center |
| Limits | No collab partners on a Trial Reel. Duplicate uploads are detected, so each trial needs a genuinely different hook, audio or visual | PostFast |
| API | `trial_params` with `MANUAL` or `SS_PERFORMANCE` (our `publish/instagram.py` supports both). Eligibility is checked when it publishes, so open the app first to confirm the toggle appears | `meta-pinterest-api.md`; Planoly |

**How we use them (from the threshold on):**
- **Hook tests.** For each week's best script, make 2 versions with different first lines and on-screen
  text, both as Trial Reels with manual sharing. After 24 hours, share the winner to everyone and archive
  the other. Never run the same video twice with a new caption only.
- **New formats** (Spanish on Dinero Simple, own-voice vs Kokoro, a new carousel-to-Reel style) go out as
  trials first, so a flop doesn't teach followers to scroll past us.
- **Count trials inside the 2-a-day cap** in `launch-playbook.md`. The cap is about not looking like a spam
  account, and trials are still posts.
- Record each trial's 24-hour views, shares and sends against the regular Reel in `factory metrics`, so
  `factory report` can show which hook styles win.

## 3. Collabs

| Item | Detail | Source |
|---|---|---|
| How | Tag people → **Invite collaborator**, up to **5** accounts. The invitee accepts in DMs, then the post shows on their grid and to their followers too. Works for feed posts, carousels and Reels, not Stories | [Sked Social, Aug 2026](https://skedsocial.com/blog/instagram-collaboration-feature.md), citing the Help Center as of Oct 2026 |
| Shared | One post: one like count, one comment thread. Only the creator can delete it | same |
| Ranking | Mosseri (2024): ranking "biases more towards the original collaborator than the person who accepts". **The account that posts gets more of the lift** | same |
| Officially recommended | Instagram lists collabs, remix and the paid-partnership label as the right way to share others' content | [Instagram, 30 Apr 2026](https://creators.instagram.com/blog/rewarding-original-creators-on-instagram) |

**Collab plan for us (free, organic):**
1. **Between our own brands, from week 2.** One collab carousel a week where the topics overlap. Rotate
   which brand posts it, because the poster gets more of the lift.
   - MMS × 1099 Money: "The budget that works with irregular income".
   - MMS × Scam Decoded: "The 3 bank texts that are always scams".
   - Dinero Simple × MMS: Spanish and English versions as separate posts, not one collab, so each reaches its
     own language audience.

   Each brand account must be its own real account that Dhruv runs, which it already is. Don't create extra
   accounts just to collab.
2. **With small finance creators, from about 1,000 followers.** Pitch a carousel we design with their tip and
   their name on it, posted by them, with us as collaborator. Target creators of a similar size
   (`watchlist.csv` has candidates).
   - Dhruv sends every invite and DM himself.
   - No money changes hands. If anything of value is exchanged (a free product, a shout-out deal), use the
     paid-partnership label.
3. **Never collab with:** trading or crypto "signals" accounts, "get rich" accounts, or any account on the
   do-not-pitch list in `sponsor-kit.md`. Our name ends up on their grid.

## 4. Broadcast channels

| Item | Detail | Source |
|---|---|---|
| Eligibility | Professional account. Older Help Center text, quoted by [Buffer, Oct 2024](https://buffer.com/resources/instagram-broadcast-channels/): "Broadcast channels can be started by a public account with more than 10,000 followers." [Sendible, Jun 2026](https://www.sendible.com/insights/instagram-broadcast-channels?hsLang=en) gives no minimum. **Check in the app** (Profile → + → Broadcast channel, or in the inbox) | as linked |
| Joining | The first message sends "all your followers... a notification inviting them to join". After that: join button in the DM chat, invite link, Story share. Only members get messages | Buffer |
| Content | Text, photos, videos, voice notes, polls, 24-hour question prompts. Members react with emoji. Replies are an optional setting on some accounts | Sendible |
| Scheduling | **No API.** Posted live in the app only | Sendible |

**When and how we use it:**
- **From the eligibility threshold, for MMS first.** Use the one-time join notification on a strong day,
  for example launch week of the Actual Budget series (`actual-budget-tutorials.md`).
- **Content:**
  - One message a week, the "Sunday 20-minute check": a poll ("Did you stay under your weekly number?") and
    a one-line tip.
  - Product and lead-magnet links at most 1 in 5 messages, matching Sendible's 80/20.
  - Never sell in the first message.
- **Don't** repost the feed into the channel. Channel-only content gives people a reason to join.
- It's a second funnel next to email, but **email stays the owned list**. The channel can be switched off or
  changed by Instagram, so always point channel members to the free lead magnet too.

## 5. Faceless finance: format rules that follow from the above

1. **Carousels built to be sent.** One idea, 6-10 slides. The last slide says why to send it ("Send this to
   whoever pays the bills in your house"). Sends are the new-audience signal, so write for that action,
   not "double tap".
2. **Reels: the hook is on screen in the first second**, with a clear topic in the caption's first line
   (helps "Your Algorithm" topic matching and search). 30-55 seconds for most, at most 3 minutes for
   anything we want recommended.
3. **Original elements in every post:** our own charts of our own numbers, worked examples (fictional,
   labelled), and Dhruv's own voice or screen recordings where possible. It's what Instagram counts as
   original, and what keeps us out of the aggregator bucket.
4. **Never repost:** no stitched viral clips, no screenshots of other creators' posts, no "credit:
   @someone" reposts. To spotlight someone, share to Story or use Instagram's own repost button, which keeps
   attribution with them.
5. **Comment-for-link is OK if it's real.** "Comment BUDGET and I'll DM you the free sheet" is fine when we
   really send it. Automating that DM needs Instagram's messaging API through a tool (ManyChat or similar,
   check its free plan) or replying by hand. Don't use comment bait on posts with nothing to send.
6. **Hashtags: 3-5, descriptive** ("#budgeting #sinkingfunds #personalfinance"). They describe the topic, they
   don't add reach.
7. **AI label:** keep `is_ai_generated` on for posts with AI voice or AI visuals, as `publish/instagram.py`
   already does.
8. **Check Account Status weekly** in the 15-minute engagement routine. A recommendation-eligibility warning
   is the earliest sign something's wrong, and it also turns off Trial Reels.

## 6. Changes for the factory (not made here, docs only)

| # | Change | Why |
|---|---|---|
| 1 | `publish/instagram.py`: `HASHTAG_MAX = 30` → **5**. `launch_check.py`: `CAPTION_LIMITS["instagram"]` → `(2200, 5)` | Instagram's cap is 5 since Dec 2025. `fit_caption` already drops trailing hashtags, so it's a constant change plus a test |
| 2 | `schemas.py` line 53: "5-10 relevant hashtags" → "3-5" | The writer asks for more than Instagram allows |
| 3 | `publish/instagram.py` notes: carousel children ≤10 → 20 | Already flagged in `meta-pinterest-api.md` |
| 4 | Trial Reels: an option on `factory approve` (e.g. `--trial manual`) and a 24-hour reminder in Today to share the winner | Hook tests become a routine, not a manual chore |
| 5 | `factory metrics`: store sends (`shares`) and reach for Instagram, and report **sends per reach** and **likes per reach** | They're the numbers Mosseri says to track |

## 7. Week-by-week, for a new brand account

| When | Do |
|---|---|
| Weeks 1-2 | Original carousels and Reels at half cadence (`launch-playbook.md`). 3-5 hashtags. Collab carousel between our own brands from week 2. Check Account Status weekly |
| At the Trial Reels threshold (200 or 1,000 followers, check the app) | Start hook tests on the best script each week |
| About 1,000 followers | First outside collab pitches (Dhruv sends), 1-2 a month |
| At broadcast-channel eligibility | Open an MMS channel, then the other brands. Weekly check-in poll |
| Every month | Compare sends per reach across formats in `factory report`, and drop the weakest format |

## Open questions for Dhruv

1. Should the factory thread make the hashtag fix (change 1-2 above)? It's small and stops captions being
   cut by Instagram.
2. Are you OK running collab carousels between our own brands from week 2? Each post appears on both
   grids.
