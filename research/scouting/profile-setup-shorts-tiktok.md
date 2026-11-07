# YouTube and TikTok profile setup: Money Made Simple and Scam Decoded

Written 2026-11-07. **Docs only. Dhruv creates the accounts himself; nothing has been registered.** This
sheet is what to type into each profile screen. Handles couldn't be checked from here (that needs a login),
so each has fallbacks. The order follows `domains-and-names.md` and `two-brand-launch-plan.md`: MMS in
week 0, Scam Decoded in week 2.

## The platform rules that shape the profile

| Rule | YouTube | TikTok | Source |
|---|---|---|---|
| Handle length and characters | 3-30 characters: letters, numbers, `_`, `-`, `.`. It can't look like a URL or phone number | Up to 24 characters: letters, numbers, `_`, `.` | YouTube: [Tasty Edits, updated Jan 2026](https://www.tastyedits.com/all-about-youtube-handles/). TikTok: [HandleGrab](https://www.handlegrab.com/zh-CN/blog/tiktok-username-character-limit) (secondary; check in the app) |
| Changing the name or handle later | Twice in 14 days for each | The username is commonly reported as once every 30 days | [YouTube Help](https://support.google.com/youtube/answer/2657964); TikTok is secondary ([MakeTechEasier](https://maketecheasier.com/change-tiktok-usernames/)) |
| Bio length | The channel description shows in the header. Commonly cited at 1,000 characters | 80 characters | YouTube: check in Studio. TikTok: [Replug](https://replug.io/blog/tiktok-bio-character-limit) (secondary) |
| Clickable links | **Up to 14 channel links**, with the first shown beside Subscribe. **Links in Shorts descriptions and comments are not clickable** (since 31 Aug 2023). Instead, each Short can carry one "related video" link to a long video | **A personal account needs 1,000 followers for the website link.** A Business account gets it at once but loses part of the music library and Creator Rewards eligibility | YouTube: [Help](https://support.google.com/youtube/answer/2657964), [Lindsey Gamble](https://lindseygamble.com/blog/youtubes-link-changes-what-it-means-for-creators). TikTok: [Stan, updated 16 Sep 2026](https://stan.store/blog/tiktok-link-bio-requirements-2026-guide/) |
| Pinned posts | One channel trailer for non-subscribers and one featured video for returning viewers. Shorts can't be pinned to the top of the Shorts tab, so use a playlist | **Up to 3 pinned videos** at the top of the grid | TikTok: [Metricool](https://metricool.com/how-to-pin-videos-on-tiktok/) (secondary) |

**What this means for us:**

1. **Keep TikTok personal, not Business** (`tiktok-instagram-monetization.md`). So there's **no clickable
   link until 1,000 followers**. Until then the bio says the site in words ("moneymadesimple.com", typed
   out), and the pinned videos do the selling.
2. **On YouTube, the link lives in the channel links and in each Short's related-video link.** Point every
   Short at the matching long video, or at the "start here" long video when there's no match.

## Money Made Simple

| Field | YouTube | TikTok |
|---|---|---|
| Name | Money Made Simple | Money Made Simple |
| Handle, in order | `@moneymadesimple` → `@mymoneymadesimple` → `@moneymadesimplehq` | `moneymadesimple` → `mymoneymadesimple` → `moneymadesimplehq` (use the same one as YouTube if possible) |
| Bio | See below | `One money move a week, with the math shown. No hype, no stock picks.` (68 characters) |
| Link | 1: the site's `/start/` page. 2: the free tools hub. 3: the newsletter signup. 4: Instagram. 5: TikTok | None until 1,000 followers. Then the site's `/start/` page with `?utm_source=tiktok` (use `docs/UTM.md` from PR #8) |
| Profile picture | The brand mark from `visual` in `brands/money-made-simple.yaml`, not a face. It's cropped to a circle, so keep it centred | Same image |
| Banner | Brand colours, plus "One money move a week" in the safe middle strip | — |

**YouTube channel description (about 520 characters):**

> Money Made Simple is personal finance for people in their 20s who feel behind on money. Each week:
> one money move you can make that week, with the numbers shown. Budgeting systems that stick, credit
> scores, debt payoff, high-yield savings, and first-time investing with index funds and retirement
> accounts. No crypto pumps, no stock picks, no get-rich-quick.
>
> Scripts are drafted with AI help and fact-checked by a person. This is general education, not
> financial advice. Free calculators and the newsletter are in the links above.

The AI line matches `brands/money-made-simple.yaml` after the a57f479 fix. Keep it word for word.

**Pinned and featured posts (picked from `launch/money-made-simple/content.json`):**

| Slot | Post | Why this one |
|---|---|---|
| YouTube channel trailer (for non-subscribers) | #23 "Feel behind on money? A 30-day reset plan" | It's the brand promise in one video, and it speaks directly to the audience |
| YouTube featured video (for subscribers) | #22 "How to start investing with $100 a month" | Highest search demand among the long videos (`keywords-mms-first-30.md`) |
| YouTube playlist "Start here: 60-second money moves" | The first 5 Shorts | Shorts can't be pinned, so this playlist is the shelf |
| TikTok pin 1 | #6 "Freeze your credit for free tonight" | A free, do-it-tonight action, so it's the most likely to be saved and sent |
| TikTok pin 2 | #4 "The fee that eats $18,000" | A single shocking number that shows how the brand works (the maths shown) |
| TikTok pin 3 | #13 "Find your forgotten subscriptions in 10 minutes" | It leads to the free subscription-audit tool once the link unlocks |

**Rule:** swap a pin after week 4 for whichever post has the best watch time or saves in its first 72 hours
(`launch-metrics-30-days.md`).

## Scam Decoded

| Field | YouTube | TikTok |
|---|---|---|
| Name | Scam Decoded | Scam Decoded |
| Handle, in order | `@scamdecoded` → `@getscamdecoded` → `@scamdecodedhq` | `scamdecoded` → `getscamdecoded` → `scamdecodedhq` |
| Bio | See below | `One scam, decoded in 60 seconds. Send it to someone who'd fall for it.` (70 characters) |
| Link | 1: the free "Is this a scam?" checker. 2: the family scam-proofing checklist. 3: the newsletter (weekly scam alert). 4: Instagram | None until 1,000 followers. Then the checker |
| Profile picture | The teal shield mascot from `brands/scam-decoded.yaml` | Same |
| Banner | Navy and cream, plus "One scam, decoded in 60 seconds" | — |

**Name check:** never "Scam Shield" anywhere on these profiles, because of T-Mobile's SCAMSHIELD mark
(`domains-and-names.md`). Make sure the site URL in the links is the renamed one, not
`scamshield.netlify.app`.

**YouTube channel description (about 560 characters):**

> Scam Decoded explains one scam at a time, in plain language, so you spot it first. Text and email
> scams, fake bank calls, AI voice clones, investment and crypto scams, identity theft and credit freezes,
> and how to protect older parents. Every video ends with what to do and where to report it (FTC, your
> bank, 7726 for scam texts).
>
> We never ask you to send money, codes or personal details. Anyone claiming to be us and asking for
> those is a scammer. Scripts are drafted with AI help and fact-checked by a person. Free scam checker
> in the links above.

The "we never ask" line matters: impersonation is the first thing that happens to a scam-awareness account
once it grows. Check that the Scam Decoded brand file uses the same AI-disclosure wording as MMS when PR #9
merges (`risk-memo.md`, decision 2).

**Pinned and featured posts (picked from `launch/scam-decoded/content.json` on PR #9):**

| Slot | Post | Why this one |
|---|---|---|
| YouTube channel trailer | #0 "3 ways to pay that only scammers insist on" | One rule that covers most scams. It's the brand promise |
| YouTube featured video | The first long video from `LONG_VIDEO_RECORDINGS.md` (due 22 Nov) | An original long video is our protection against YouTube's reused-content rule |
| YouTube playlist "Start here: 60-second scam checks" | Shorts #0-#6 | The shelf for Shorts |
| TikTok pin 1 | #3 "1 family safe word beats an AI voice clone" | The most shareable to family, and it fits the bio's ask |
| TikTok pin 2 | #2 "That $3.95 'unpaid toll' text is a trap" | The scam people receive most often right now (FTC and BBB alerts in `keywords-scam-decoded-first-20.md`) |
| TikTok pin 3 | #5 "7726: the free number to forward scam texts to" | A one-number action, and an easy save |

## Setup order (about 40 minutes per brand)

1. Make the brand Google account, then the YouTube channel, from the brand email (`launch-playbook.md`).
2. Claim the handle. If the first choice is taken on either platform, use the **same fallback on both**.
3. Upload the picture and banner, paste the description, and add the channel links in order.
4. On TikTok: sign up with the brand email, **keep the personal account type**, set the name, username and
   bio, and add the picture. Leave the website field empty.
5. Turn on 2-step verification on both (TikTok: Settings → Security; Google: the account's security page).
6. Don't post on day 1. Watch and follow 10-20 accounts in the niche from the account for a day or two, so
   the For You feed learns what the account is about. This is our judgment, not a platform rule.
7. Post the first three pinned candidates in week 1, then pin them.

## Sources

Read 2026-11-07:
[YouTube Help: manage your channel's profile](https://support.google.com/youtube/answer/2657964);
[Tasty Edits: YouTube handles](https://www.tastyedits.com/all-about-youtube-handles/) (updated 6 Jan 2026);
[Lindsey Gamble: YouTube link changes](https://lindseygamble.com/blog/youtubes-link-changes-what-it-means-for-creators);
[Stan: TikTok link in bio requirements](https://stan.store/blog/tiktok-link-bio-requirements-2026-guide/) (updated 16 Sep 2026);
[Replug: TikTok bio character limit](https://replug.io/blog/tiktok-bio-character-limit);
[Metricool: pinning TikTok videos](https://metricool.com/how-to-pin-videos-on-tiktok/);
[HandleGrab: TikTok username limit](https://www.handlegrab.com/zh-CN/blog/tiktok-username-character-limit).
TikTok's own help pages didn't load from here, so the TikTok limits marked "secondary" should be confirmed
on the sign-up screen.
