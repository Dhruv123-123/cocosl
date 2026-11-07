# Scam Decoded: originality pass (Nov 7 2026)

Why this exists: the scouting notes on PR #2 (`research/scouting/youtube-monetization.md`,
`research/scouting/tiktok-instagram-monetization.md`) found two rules that our pipeline was walking into.

- **YouTube "inauthentic content"** (YPP, renamed from "repetitious content" in Jul 2025). It names
  "slideshows that all have the same narration" and is judged per **channel**, not per video. Our
  default render (`media/video.py`) is a still image per beat with a Ken Burns move and a narration
  track: exactly that pattern.
- **TikTok Creator Rewards** pays only for original videos **over 1 minute**. The scouting also notes
  (unverified) that fully AI-made videos, AI visuals plus AI voice, may be excluded. Our TikTok cuts so
  far were 60–90 s by word count, often just over the line, with AI voice and AI stills.

Nothing in this pass has been posted. All outputs are files for Dhruv to record and post by hand.

## 1. What this pass adds

| Format | Files | What makes it original |
|---|---|---|
| **Scam text walkthroughs** (6 vertical videos, 42–57 s, 1080×1920) | `originality/out/walkthroughs/<id>/<id>.mp4`, `cover.png`, `voiceover.txt` | A phone-screen recording: messages arrive, each red flag lights up and gets numbered in time with the narration, then a "what to do" card. Every scene is drawn from that scam's own text, so no two look alike. Fictional numbers (555-01xx), masked links |
| **"Spot the red flags" quizzes** (6 Instagram carousels, 7–8 slides, 1080×1350) | `originality/out/quizzes/<id>/slide-NN.png` | Interactive: the message first, a "count them" slide, one reveal per flag, then the fix and "how many did you get?". Saves and shares, not a narrated slideshow |
| **Real FTC data charts** (4 slides, 1080×1350) | `originality/out/charts/<id>.png` | Drawn from published FTC Consumer Sentinel numbers, source on the image (see §5) |
| **10 TikTok minute cuts** (69–76 s of narration plus pause beats) | `tiktok-minute-cuts.json` | Rebuilt versions of the 10 strongest Shorts: each has a walkthrough or quiz beat, a "pause" card, an FTC number where one fits, and an `original_element` that says what Dhruv records |

Rebuild everything with `python3 originality/build.py` (about 3 minutes; needs Node, Playwright's Chromium
and ffmpeg) and `python3 originality/minute_cuts.py`. Content lives in `originality/formats.py`.

## 2. Rules from now on

1. **Human voice on every TikTok and every long video.** Dhruv reads the narration (phone mic in a quiet
   room is fine). AI voice stays on Shorts drafts only, until he's recorded them. This is the cheapest
   fix for both platforms.
2. **No two videos in a row in the same format.** Rotate through: walkthrough, face cam + text, quiz
   pause, data chart, illustrated explainer. On a given day, the Short and the TikTok cut shouldn't use
   the same format either.
3. **Every long video needs an `original_element`.** Something that only exists because a person made
   it: a screen recording of a real tool, a real (redacted) scam message he got, his face on camera, a
   chart from real data. The table in §3 fills this in for weeks 22–26.
4. **TikTok cuts run at least 65 s of narration** (about 165+ words at 150 wpm) plus a pause beat, so
   they clear the 1-minute line with room to spare. The minute cuts here run 69–76 s before pauses.
5. **Sameness check before posting a week.** Run the pairwise Jaccard check already in the tests; nothing
   above 0.25 against anything in the last 90 days. Today's ten cuts top out at 0.09 against each other
   and 0.19 against the Shorts they came from.
6. **Rotate hooks.** No more than two hooks a week that open with "Zero …" or a dollar amount. The
   minute cuts open with pauses, step-by-steps and "watch how", on purpose.
7. **Accounts:** keep the TikTok account **personal**, not Business. Creator Rewards is for personal
   accounts, and Business accounts are limited to the commercial music library. Cross-post Reels to a Facebook Page
   for the extra reach the scouting found; it costs nothing.
8. **One YouTube community post a week**, using a chart or a quiz slide from this pass.

## 3. `original_element` for the weeks 22–26 long videos

| # | Date | Long video | Original element |
|---|---|---|---|
| 40 | Sun Apr 4 | After the storm: home repair scams | 20 s screen recording of looking up a contractor's licence on his state's licensing site, plus the c3 total-losses chart |
| 41 | Sun Apr 11 | After Tax Day: the scams that follow you | Screen recording of IRS.gov "Your Online Account" sign-in page and IRS Direct Pay (no personal data) to show where real notices and payments live; walkthrough-style mockup of a fake IRS text |
| 42 | Sun Apr 18 | How 1 hacked email unlocks everything | Screen recording of turning on two-step sign-in and checking "devices signed in" on his own email account (addresses blurred) |
| 43 | Sun Apr 25 | Rental listing and moving company scams | Screen recording of a reverse image search on a rental photo, plus the FMCSA mover lookup page |
| 44 | Sun May 2 | Older Americans Month: the 7 scams | Face cam intro and outro, the c4 age chart, and two quiz pauses using q5-medicare and q4-utility |

### Screen-recording shot list for Dhruv (about 1 hour, once)

Record on a computer at 1080p or a phone screen-record. Blur or crop anything personal. Each clip is
10–20 s and can be reused across videos.

1. **Credit freeze:** one bureau's freeze page, from the landing page to the "freeze" button (stop before
   entering details). Used by the credit freeze minute cut.
2. **IRS Direct Pay:** the landing page and the "make a payment" choices. Used by #41.
3. **IRS Online Account:** the sign-in page only. Used by #41.
4. **Bank alerts:** the alert settings screen in his own banking app (balances hidden). Used by the
   bank-call minute cut and any future bank video.
5. **Sign out of all devices:** where it lives in his email or main account. Used by the code minute cut
   and #42.
6. **Force quit:** a harmless full-screen page closed with Task Manager or Force Quit. Used by the pop-up
   minute cut.
7. **Report spam text:** forwarding a spam text to 7726 on his own phone. Used by the toll cut.
8. **Contractor licence lookup** and **reverse image search**. Used by #40 and #43.

## 4. Where the new pieces go in weeks 22–26

The weeks 22–26 plan leaves TikTok empty on Tuesdays and Thursdays and posts nothing on Saturdays.

| Date | 18:00 TikTok (minute cut) | Saturday 12:00 Reel + Short (walkthrough) | Saturday 19:30 Instagram (quiz) |
|---|---|---|---|
| Tue Apr 6 | Pause on this toll text: count the 4 red flags | | |
| Thu Apr 8 | The fraud alert that ends with a code, played out | | |
| Sat Apr 10 | | w1-toll | q1-refund |
| Tue Apr 13 | Freezing your credit, start to finish, in 3 stops | | |
| Thu Apr 15 | Quiz: 4 red flags in a $499 order email | | |
| Sat Apr 17 | | w3-bank-code | q3-invoice |
| Tue Apr 20 | 'Move it to a safe account': the bank call, step by step | | |
| Thu Apr 22 | The task job text, followed all the way to the top-up | | |
| Sat Apr 24 | | w5-job | q6-account |
| Tue Apr 27 | Fake virus pop-up: 3 tricks and the 1 key combo that ends it | | |
| Thu Apr 29 | 'New number, can you pay a bill?': the whole text thread | | |
| Sat May 1 | | w4-new-number | q4-utility |
| Tue May 4 | A cloned voice call, played out: 1 word ends it | | |
| Thu May 6 | Dating app to WhatsApp in 1 day: the pattern, hour by hour | | |
| Sat May 8 | | w6-wrong-number | q5-medicare |

Spare: walkthrough w2-delivery and quiz q2-marketplace go into week 27. Charts: one per Sunday as the
YouTube community post (c1 Apr 4, c2 Apr 11, c3 Apr 18, c4 Apr 25) and as an Instagram story the same day.

Walkthrough videos are silent on purpose. Record `voiceover.txt` (one numbered line per on-screen step,
at an easy pace) and lay it under the video in CapCut; the timing was built at 150 words a minute.

## 5. Data used, and what to check before posting

All numbers are from reports to the FTC's Consumer Sentinel, which undercounts (most fraud is never
reported). Re-check each against the source the week it posts.

- Social media losses: $261M (2020), $789M (2021), $1.2B (2022), $1.5B (2023), $1.9B (2024), $2.1B (2025);
  share of 2025 loss reports by contact method (website or app 31%, social 28%, phone 11%, email 10%,
  text 7%); share starting on social by age (18–29 40% … 80+ 14%). FTC Data Spotlight, Apr 2026:
  https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2026/04/reported-losses-scams-social-media-eight-times-higher-2020
- Imposter scams $3.5B in 2025; business impersonators nearly $1B; government impersonators about $920M.
  FTC, Jun 2026: https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025
- $12.5B total in 2024; job scams $501M. FTC, Mar 2025:
  https://www.ftc.gov/news-events/news/press-releases/2025/03/new-ftc-data-show-big-jump-reported-losses-fraud-125-billion-2024
- The FTC didn't collect reports during the 2025 government shutdown; the c1 chart says so on the image.

Still unverified: whether TikTok actually excludes AI-voiced videos from Creator Rewards. The human-voice
rule above makes it not matter.
