# Posting times and frequency for new accounts in 2026: TikTok, Shorts, Reels, Pinterest

Written 2026-11-07. **Docs only. Nothing in `brands/*.yaml` was changed.** This compares the large 2026
studies (Buffer, Sprout Social, PostFast, Tailwind) with what our packs actually schedule. Our schedules:
Money Made Simple and 1099 Money post at **12:30 and 19:00 America/New_York**, Scam Decoded at **12:00 and
19:30**, Tiny Histories at **17:00**. Each short goes to TikTok, YouTube Shorts and Instagram Reels at the
midday slot, carousels go to Instagram in the evening, and the long video goes to YouTube on Sunday evening
(`launch/money-made-simple/POSTING_PLAN.md`). Cadence is 5 shorts, 3 carousels and 1 long a week, with at
most 2 posts per platform per day.

## TL;DR

- **For a brand-new account, timing matters less than the studies suggest.** Every study measures
  accounts that already have followers. With almost no followers, TikTok, Shorts and Reels hand a video to
  people by interest, not by who's online at the time. (That's our reasoning, not a finding from these
  studies.) Posting on a steady schedule and ramping up slowly matter more, and `launch-playbook.md`
  already does both.
- **The studies disagree with each other on TikTok.** Buffer (7.1M posts) finds that **afternoons
  (12-5 p.m.) are the weakest** and evenings (6-11 p.m.) the strongest. Sprout (about 2 billion
  engagements) finds **weekday afternoons, 1-8 p.m., the best**. Our 12:30 TikTok slot is in Buffer's
  weak window. **Moving TikTok to 18:00** fits both: it's an evening slot for Buffer and inside Sprout's
  Tuesday-Wednesday windows.
- **Our 12:30 slot is right for Shorts.** PostFast's controlled data (6,175 posts, mostly Shorts) peaks at
  **1 p.m. local time (1.28× a channel's normal)**. 6 p.m. is below normal (0.80×).
- **Reels at 12:30 and carousels at 19:00 are both fine.** Buffer's best Instagram slots are Wednesday
  12 p.m., Thursday 9 a.m. and Wednesday 6 p.m., with evenings strong on most days.
- **Pinterest at 19:00 is outside every window.** Sprout puts Pinterest at **weekday mornings to early
  afternoon (about 10 a.m.-1 p.m.)**. Give Pinterest its own time, 11:00.
- **Frequency: we're within the guidance everywhere except Instagram.** Sending all 5 shorts to Reels plus
  3 carousels is **8 Instagram posts a week**. Buffer says 3-5. Our own steady state in `launch-playbook.md`
  is 3 carousels and 2-3 Reels. Cut Reels to the **3 shorts that did best on TikTok** in their first 48
  hours.

## 1. What the 2026 studies say

| Platform | Study | Data | Best times (local) | Frequency |
|---|---|---|---|---|
| **TikTok** | Buffer, 14 Sep 2026 | 7.1M posts, median engagement rate | Best single slots: Sun 9 a.m., Mon 1 p.m., Sun 1 p.m. Best day Saturday. **Evenings 6-11 p.m. peak; 12-5 p.m. lowest** on most days | "Posting consistently matters more than posting every single day" |
| | Sprout Social, 31 Mar 2026 | ~2B engagements, 307K profiles, 27 Nov 2025-27 Feb 2026 | Mon 3-5 p.m., Tue 2-6 p.m., **Wed 1-8 p.m.**, Thu 1-5 p.m., Fri 3-5 p.m. Weekends and early mornings worst | "You don't necessarily need to post more" |
| | Buffer, 8 Oct 2025 (frequency) | 11.4M posts, 150K accounts | — | **Median** views per post barely move with frequency (489 at 1 a week, 506 at 2-5, 487 at 6-10, 459 at 11+). Buffer's regression estimates +17% (2-5), +29% (6-10), +34% (11+) per post. Read it as: **2-5 a week is the safe range, and more doesn't hurt per-post reach much** |
| **YouTube Shorts** | PostFast, updated 20 Sep 2026 | 6,175 posts from 97 workspaces, each scored against its channel's normal | **1 p.m. (1.25-1.28×)**, then 9 p.m. (1.19×) and 10 a.m. (1.18×). **6 p.m. weak (0.80×).** Sat 1.13× and Sun 1.12×; Wed weakest (0.89×). Rankings only partly repeat across samples (0.59) | Guidance, not measured: daily beats weekly for Shorts; long videos 1-2 a week |
| | Sprout Social | — | No YouTube times; says to use YouTube Studio | — |
| **Instagram (Reels and carousels)** | Buffer, 2026 | 9.6M posts, Jan 2024-Dec 2025 | Thu 9 a.m., **Wed 12 p.m.**, Wed 6 p.m. Best day Wednesday. **Evenings (6-11 p.m.) strong except Thursday.** Fri and Sat weakest. Reels and carousels weren't measured separately | **3-5 feed posts a week**, 1-2 Stories a day |
| | Sprout Social | as above | Mon 2-4 p.m., Tue 1-7 p.m., **Wed 12-9 p.m.**, Thu 12-2 p.m. Mon-Thu best; weekends worst | — |
| **Pinterest** | Sprout Social | as above | Mon 10 a.m.-12 p.m., Tue 7 a.m. and 10 a.m.-1 p.m., Wed 8 a.m.-1 p.m., Thu 10-11 a.m., Fri 10-11 a.m. Summary: **Tue-Thu 10 a.m.-1 p.m.** | — |
| | Tailwind help | — | — | **New accounts: 3-5 fresh pins a week.** Creators: 1-3 fresh pins a day |

**What "local time" means for us:** every study gives the viewer's local time. Our audiences are spread
across the US, and our times are Eastern, so 12:30 ET is 9:30 a.m. in California and 19:00 ET is 4 p.m.
there. Midday and early evening Eastern are a reasonable compromise across time zones. The real answer for
each account comes from its own analytics after about 30 posts (TikTok Analytics > Followers, YouTube
Studio "When your viewers are on YouTube", Instagram Insights).

## 2. Our schedules against the studies

| Platform | Our slot (MMS, 1099) | Fits? | Suggestion |
|---|---|---|---|
| TikTok | 12:30 ET, 5 a week | **Mixed.** In Buffer's weakest window; inside Sprout's only on Wednesday | **18:00 ET** on all days (one slot a day is enough for 5 a week) |
| YouTube Shorts | 12:30 ET, 5 a week | **Yes.** PostFast's best hour is 1 p.m. | Keep |
| YouTube long | Sunday 19:00 ET, 1 a week | Not measured well (PostFast had too few long videos); industry guidance is weekday afternoons | Keep Sunday for now, since it's the habit slot in our packs. Check YouTube Studio after 8 uploads |
| Instagram Reels | 12:30 ET, 5 a week | Time **yes** (Buffer Wed 12 p.m.; Sprout Mon-Thu afternoons). Count **too high** | Keep 12:30. Post only **3 a week**: the shorts that did best on TikTok after 48 hours |
| Instagram carousels | 19:00 ET, 3 a week | **Yes.** Buffer's evening peak | Keep. Prefer Mon-Thu; avoid Saturday (Buffer's and Sprout's weakest) |
| Pinterest | Uses the brand's 12:30 and 19:00 | 12:30 **yes**; 19:00 **no** | **11:00 ET**, one slot. Week 1-2: 3-5 pins a week (Tailwind), then 1 a day as `launch-playbook.md` already plans |
| Scam Decoded | 12:00 and 19:30 ET | Same as above | Same platform changes. Its audience includes older relatives, who may use Facebook and earlier hours more; that's untested, so check Insights after a month |
| Tiny Histories | 17:00 ET only | TikTok fine (Sprout's weekday windows); Shorts 5 p.m. is near PostFast's weak 6 p.m. | Shorts at 13:00 if the brand runs again |

**The weekend question has no clear answer.** Buffer finds Saturday the best TikTok day, and PostFast
finds weekends best for Shorts. Sprout finds weekends the worst for TikTok and Instagram. Our packs post
every day, which suits a new account building a habit. Don't skip weekends because of these studies.

## 3. The change, if the main thread wants it

The factory already supports per-platform times (`cadence.platform_times` in each brand yaml, used by
`scheduler.next_slot`). For Money Made Simple and 1099 Money:

```yaml
cadence:
  post_times: ["12:30", "19:00"]
  platform_times:
    tiktok: ["18:00"]
    pinterest: ["11:00"]
```

Scam Decoded: the same, with its own `post_times` left at 12:00 and 19:30. Instagram and YouTube keep the
brand's two times. The Reels count is a pack decision, not a config one. The POSTING_PLAN files would need
the TikTok column moved to 18:00 and two of the five Reels a week dropped.

**Test it rather than trust it:** run TikTok at 18:00 for 4 weeks, then compare median views per post with
the first 2 weeks at 12:30. Keep whichever wins. With a new account the difference may be noise, so only
switch for a clear gap (say 25% or more).

## Sources

Read 2026-11-07:
[Buffer: best time to post on TikTok](https://buffer.com/resources/best-time-to-post-on-tiktok) (14 Sep 2026);
[Buffer: how often to post on TikTok](https://buffer.com/resources/how-often-should-you-post-on-tiktok/) (8 Oct 2025);
[Buffer: best time to post on Instagram](https://buffer.com/resources/when-is-the-best-time-to-post-on-instagram/);
[Sprout Social: best times to post on social media](https://sproutsocial.com/insights/best-times-to-post-on-social-media/) (31 Mar 2026, modified 13 Oct 2026);
[PostFast: best time to post on YouTube](https://postfa.st/blog/best-time-to-post-on-youtube) (updated 20 Sep 2026);
[Tailwind: how many pins to post per day](https://support.tailwindapp.com/en/articles/15621722-how-many-pins-should-you-post-per-day-on-pinterest).
Our schedules: `brands/*.yaml` `cadence` blocks (this branch and the brand threads' branches) and
`launch/money-made-simple/POSTING_PLAN.md`.
