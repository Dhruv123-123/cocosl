# Dhruv's decisions: every open call, in the order that unblocks launch

Written 2026-11-07 from every open PR's start-here and checklist docs: `docs/GO_LIVE.md` (PR #7),
`launch/b2b/B2B_START_HERE.md` and `LAUNCH_CHECKLIST.md` (PR #13), `launch/dinero-simple/DINERO_START_HERE.md`
(PR #11), the ad studio kit `PRICING.md` (project files), the product and KDP notes (PR #6, #9, #10), and the
scouting research on this PR. **Nothing here has been bought, sent or submitted.** Each row gives a
recommendation, what it costs, and what waits on it. Say "yes to all recommendations" and the threads
can carry on; change any row you disagree with.

**Total spend if you take every recommendation in sections 1 and 2:** about **$30-45 up front**, plus a
mailbox (price depends on where you live), plus about **$10 every 4 months** in Etsy listing fees. Section 3
adds about **$300-600 in Jan-Mar 2027**, and only if the gates pass.

## 1. This weekend: these block everything else

| # | Decision | Recommendation | Cost | What waits on it |
|---|---|---|---|---|
| 1 | **Merge the PRs** | Merge in this order: **#1, #3, #2, #4, #5, #6, #8, #12, #11, #7**, then #9 and #10 once GitHub shows them green (`GO_LIVE.md` → PR merge order) | $0, 15 min | Everything. Until then the work isn't on `main` |
| 2 | **How many brands at launch** | **Two:** Money Made Simple now, Scam Decoded in week 2. Skip Tiny Histories (Stage 4b) for now. 1099 Money is brand 3 at the week-8 gate, and Dinero Simple is brand 4 (`two-brand-launch-plan.md`) | $0 | The launch calendar, and your time (about 9-10 h a week) |
| 2b | **Launch dates** | **Money Made Simple: Mon 16 Nov 2026. Scam Decoded: around Mon 30 Nov** (two weeks after MMS). Both dates are relative: if the merges, domain or accounts (rows 1, 4, 5) slip, both dates move by the same amount, and Scam Decoded always stays two weeks behind MMS. Pick a Monday, so week 1 lines up with the posting plans and the Monday report | $0 | The first-week posting plans, the 30-day metrics calendar (`launch-metrics-30-days.md`) and the 90-day plan (`growth-90-days-two-brands.md`) |
| 3 | **Final brand names** | **Scam Decoded**, never "Scam Shield" (a live T-Mobile trademark). Keep **Money Made Simple** as a content brand, but don't file a trademark on it (`domains-and-names.md`) | $0 | Domains, handles, email |
| 4 | **Domains** | Buy **two now**: MMS and Scam Decoded (for example `mymoneymadesimple.com` and `getscamdecoded.com`, both free on 7 Nov; check again first). Buy 1099 Money's and Dinero's when they pass their gates. Use Cloudflare or Porkbun (`domain-plan.md`) | About **$23 a year** now, $45 a year for all four | Email authentication, Search Console, the Pinterest claim, the site URLs in every bio |
| 5 | **A postal address you're OK publishing** | A PO box or virtual mailbox. US virtual mailboxes need USPS Form 1583 and take a few days, so order it first (`GO_LIVE.md` Stage 1) | Varies by location; check the USPS PO box page or a virtual mailbox's price page | **Every newsletter and every cold email** (CAN-SPAM). Until then: Instagram DMs only |
| 6 | **Second inbox for B2B** | **No.** Share the one inbox with the ad studio: from 1 Dec, 4 of the 10 daily sends are B2B (`OUTREACH_DATES.md`). The second-inbox plan is kept only for comparison | Saves about $6-7 a month | Nothing, if you say no |
| 7 | **Newsletter tool** | **Sender Free Forever**, one account with a group and sender identity per brand (`newsletter-tool-decision.md`, `sender-setup-guide.md`). Kit's free plan no longer runs welcome sequences | $0 up to 2,500 subscribers | The welcome sequences, with the day-7 product pitch |
| 8 | **Writing key** | Yes: an Anthropic API key with a **$5 prepay**. The launch packs are already written, so this only matters for new drafts | $5-10 | New drafts. Without it, new drafts come out as placeholders |
| 9 | **Your voice and recording time** | Yes: one **Saturday recording session of 1-2 hours**, starting with the first Scam Decoded long video (`LONG_VIDEO_RECORDINGS.md`, first due **22 Nov**), then the 1099 Money pen-and-paper clips (8 clips, about 45 min) and the Actual Budget screen recordings | $0 | YouTube's reused-content risk on long videos, and TikTok's AI-only risk |
| 10 | **Ads** | **Organic only** until the 5-point gate in `paid-acquisition.md` passes | $0 | Nothing. It stops early spending |

## 2. Weeks 1-4: these block the first revenue

| # | Decision | Recommendation | Cost | What waits on it |
|---|---|---|---|---|
| 11 | **Ad studio prices** | Keep **$249 / $449 / $799** for the first 3 clients, then move to the $300 / $900 / retainer the coordinator suggested once you have case studies. A first yes is worth more than $50 | $0 | Outreach, from Tue 10 Nov |
| 12 | **Ad studio retainer** | Keep the **$99 Shop Retainer as 4 template videos**, not custom ads, so it doesn't undercut the $249 Starter (already agreed with the coordinator) | $0 | The retainer page |
| 13 | **Self-serve kit prices** | Approve `PRICING.md`: Listing Video Kit $19, Pin Maker $15, Seasonal Sale Kit $15, **Shop Refresh Kit $15** (not $12: at $12 a Discover sale keeps only $8.40), Cover Kit $15, bundle $35, Lite free | $0 | The kit listings (they still say [PRICE]) |
| 14 | **Upwork's $179 tier** | **Hold.** Do direct outreach first. Upwork bids cost Connects, and the first two clients will come from the 326 leads already written | $0 now | Nothing urgent |
| 15 | **Product prices still marked [PRICE]** | Take the suggestions: the 1099 Money tax kit at **$19** (between the $15 tracker and the $49 bundle), the Scam Decoded parents' printable kit at **$7**, the 45-tool Money Toolkit at **$9**. From 1 Jan, the scheduled bumps ($3 Etsy singles to $4, the challenge pack to $10; `template-pricing-jan-2027.md`) | $0 | Those listings |
| 16 | **Ebook and KDP author name** | **"Money Made Simple"**, as the files already use. It matches the planner and journals, and it keeps your own name off Amazon. Change `AUTHOR` in `build_ebook.py` if you'd rather use your name | $0 | The KDP upload |
| 17 | **The site's editor name** | Your **first name**, or a consistent pen name. `site.json` → `editor` is a placeholder, and a named editor helps trust on money pages | $0 | The site's About and article bylines |
| 18 | **Etsy listings** | Open the shop in week 4 with about **15 of the best listings**, not all 74. **Don't list the ~15 AI-written guide listings** (Etsy's 22 Oct 2026 rule); move them to Gumroad (`ai-disclosure-rules-nov-2026.md`) | $0.20 a listing, about **$3** for 15; about $10 every 4 months for 50. Etsy may show a one-time setup fee at sign-up | Etsy sales |
| 19 | **Browser extension stores** | **Edge Add-ons first** ("no registration fee"), then Chrome after the first 100 users (`free-tool-listings.md`) | $0 for Edge; **$5** one time for Chrome | Store listings for the scam extension |
| 20 | **Netlify rebuilds** | Change the site's **daily rebuild to weekly**, or move it to Cloudflare Pages. The daily cron uses about 450 of the free 300 credits a month, so deploys would stop around day 20 (`free-tool-limits.md`) | $0 | Every site deploy after about day 20 |
| 21 | **Affiliate applications** | Apply to **Impact and CJ** this week (Stage 7). First fix the untrue Dinero line in PR #5's kit ("every post is reviewed by a native Spanish speaker"; the fix has been sent to the thread that owns it). Use `affiliate-answers-five-programs.md` for Aura, NordVPN, Keeper and Wise. Hold Remitly until Dinero resumes | $0 | Every affiliate link on the sites |
| 22 | **B2B cold email** | **Yes, from Tue 1 Dec**, by hand, 4 a day, accounting firms first (they must hear from you before mid-January). Conditions: the postal address (#5) is in place, and before the **first signed deal** a lawyer reads the services agreement once | $0 to send. About **$35** for a 30-minute bar referral consult before the first contract | All five B2B offers (PR #13) |

## 3. January to March 2027: only if the gates pass

| # | Decision | Recommendation | Cost | What waits on it |
|---|---|---|---|---|
| 23 | **Brand 3 at week 8 (about 10 Jan)** | **1099 Money**, if all five gates pass (time, clean accounts, `launch_thresholds.json`, a queue, list growth). Otherwise fix the failing gate and look again in two weeks | About $12 for its domain | 1099 Money's tax-season content (the 15 Jan and 15 Apr dates) |
| 24 | **Spanish reviewer test** | **Yes, in January:** post the job, send the paid two-hour test, and hire at 70+ on the rubric (`DINERO_START_HERE.md` step 4) | **$45** | Everything Dinero Simple publishes |
| 25 | **Dinero lean review** | Decide after the test score. About 10-14 hours of review, plus a Spanish-reading immigration attorney for about 1.2 hours | About **$200-350, capped at $500, plus $35** | The April Dinero launch |
| 26 | **A server** | **Wait** until manual posting is tedious, probably week 4 or later (`GO_LIVE.md` Stage 8) | $5-10 a month | Automatic posting, webhooks, backups |
| 27 | **Sponsor floor** | Keep **$75** as the minimum per placement until the 7-point gate in `sponsor-kit.md` passes | $0 | Sponsor pitches, which come later |

## Already decided (no action needed)

- **The AI-disclosure line** is fixed on `main` (a57f479): "drafted with AI help and fact-checked by a person".
- **TikTok accounts stay personal**, not Business, for Creator Rewards. So no bio link until 1,000 followers
  (`profile-setup-shorts-tiktok.md`).
- **Salary and debt pages:** the site thread has already rewritten them (8 salary bands with hand-written
  examples, one debt-payoff calculator page).
- **One shared inbox** for the ad studio and B2B (coordinator plan, 7 Nov). Row 6 only asks you to confirm it.
