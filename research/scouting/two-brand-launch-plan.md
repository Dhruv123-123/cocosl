# Two-brand launch: Money Made Simple and Scam Decoded first

Written 2026-11-07. **Docs only.** A plan in `docs/GO_LIVE.md` stage terms (that file is on the go-live
branch). It **replaces the brand order in `launch-playbook.md`**, which put 1099 Money and MMS in week 1.
Why the change: the risk memo's top risk is burnout (`risk-memo.md`), MMS is the brand with the most
finished material (months 1-4, the six Gumroad products, the site batches), and Scam Decoded has the
strongest spring moment we can prepare for in time (NCPW, 28 Feb-6 Mar 2027,
`seasonal-demand-feb-jun-2027.md`). 1099 Money's best moment, the 15 Jan quarterly payment, comes too soon
after launch to do well on a third brand. Its tax season (Feb to 15 Apr) is still open if the brand-3
gates pass at week 8.

Dates assume Stage 0 (the merges) happens on Mon 9 Nov 2026. If it slips, slide every row by the same
amount. Week 1 is the first week MMS posts.

## TL;DR

- **Weeks 0-1:** Stages 0-8 for MMS, plus Stage 2 (ad studio) from Tue 10 Nov. About 13-16 hours of setup.
- **Weeks 2-3:** Stage 9b (Scam Decoded) and 9a (free web apps). Scam posts from week 3 at half cadence.
- **Weeks 4-8:** both brands at full cadence. No new brand. About **9-10 hours a week** for Dhruv.
- **End of week 8 (around 10 Jan 2027):** check the brand-3 gates. If they pass, brand 3 is **1099 Money**
  (Stage 9d). Dinero Simple stays paused until a Spanish reviewer is booked.
- **Still running the whole time:** the ad studio, the MMS Gumroad products, the Scam kit, the free apps,
  and the email funnel. B2B stays parked until Dhruv OKs cold email; its pitch is timed to NCPW.

## Weeks 1-8

| Week (Mon) | GO_LIVE stages | What goes live | Dhruv's hours |
|---|---|---|---|
| **0** (9 Nov) | 0 merges; 1 identity and payouts; 2 ad studio (15 emails a day from Tue 10 Nov); 3 six MMS products on Gumroad; 5 MMS site and email; 6 voice and writing keys | Gumroad products, the MMS site and its welcome sequence, the first ad-studio emails | ≈ 9-10 h |
| **1** (16 Nov) | 4 MMS accounts and first posts; R7 launch day; 8 automation and server; R6 starts | MMS at **half cadence** (`launch-playbook.md`). Month 1 of the MMS calendar starts Sat 21 Nov | ≈ 6-7 h |
| **2** (23 Nov) | R6 day 7: "if MMS is steady, start the next brand". **9b Scam Decoded** accounts, $9 kit on Gumroad, site and 7-email sequence. **9a free apps** (the scam checker is the Scam site's lead tool) | Scam site, kit and apps. MMS moves to full cadence if R8's week-1 scorecard is clean | ≈ 8-9 h |
| **3** (30 Nov) | 9b first posts (R7 again, for Scam). Day 10 of MMS: **Stage 7** affiliate applications | Scam Decoded at half cadence. Only long videos with their original element (see below) | ≈ 7-8 h |
| **4** (7 Dec) | Both brands in R6. 3b **Etsy** once the ~15 AI-guide listings are moved or rewritten (`ai-disclosure-rules-nov-2026.md`) | Etsy shop. Scam to full cadence if its week-1 scorecard is clean | ≈ 9 h |
| **5** (14 Dec) | Steady state. MMS day 30: swap the model's assumptions for real numbers (`docs/FINANCIAL_MODEL.md`) | Holiday-scam posts on Scam Decoded | ≈ 8 h |
| **6** (21 Dec) | Steady state. Batch two weeks of reviews before the holidays so the queue covers them | Nothing new | ≈ 7 h |
| **7** (28 Dec) | Steady state. Scam day 30 numbers | MMS "new year money reset" posts | ≈ 8 h |
| **8** (4 Jan) | **Brand-3 check** (below). Start the NCPW build (daily alerts, due 1 Feb) | Nothing new until the check passes | ≈ 8 h |

### Scam Decoded's long videos

`youtube-policy-review-nov-2026.md` found 23 long videos with no original element, which is the biggest
YouTube risk we have. The Scam thread's `LONG_VIDEO_RECORDINGS.md` shot list adds one (first recording due
22 Nov). **Rule for week 3 onward:** a long video uploads only once its recording is done. Shorts can start
without them.

## Dhruv's weekly hours (steady state, weeks 4-8)

| Item | Per week |
|---|---|
| R6 daily routine: 15 min a brand a day (triage, review 2 posts, TikTok by hand, replies) × 2 brands × 7 days | 3.5 h |
| Ad studio: 15 first emails plus follow-ups, Mon-Fri (+45 min a day) | 3.75 h |
| Monday `factory report`, `factory launch-check`, `check_thresholds.py` | 0.5 h |
| Saturday recording session (R5), both brands' originals in one sitting | 1-1.5 h |
| **Total** | **≈ 9-10 h** |

Weeks 0-3 add the setup time in the table above. If a week runs over 12 hours twice in a row, cut the
ad-studio follow-ups to every other day before cutting a brand's replies (replies are what new accounts
are judged on, `first-100-followers-2026.md`).

## Criteria for adding brand 3

All five, checked at the end of week 8 and then every two weeks:

1. **Time:** both brands together took **under an hour a day for four straight weeks** (the risk memo's rule).
   Keep a rough log; the R6 routine is timed to 15 minutes a brand.
2. **Clean accounts:** no warnings, strikes or "not recommended" notices on either brand for four weeks
   (YouTube Account Status, Instagram Account Status, TikTok notifications).
3. **Thresholds:** `check_thresholds.py` against `launch_thresholds.json` shows **no open "change" rule** on
   either brand for two weeks running. "Watch" rules are fine.
4. **A queue:** at least two weeks of approved posts scheduled for both brands, so a third brand's setup
   week doesn't empty them.
5. **Owned audience:** the email list is growing every week on both brands (any growth counts; we judge
   the rate at months 3 and 6, not now).

**Which brand is third:** **1099 Money** (Stage 9d, about 2 hours). It needs no reviewer, it has months 5-6
and the tax-season pack ready, and Feb to 15 Apr is its season. Before posting, re-check the 2027 figures
against irs.gov (GO_LIVE 9d). **Dinero Simple** (9c) goes fourth, and only once a paid Spanish reviewer has
done the two-hour test and the lean set (about $200-500, `spanish-and-legal-review-options.md`). That
spend is Dhruv's call. Tiny Histories (4b) stays off.

If the gates fail at week 8, fix the failing one and check again in two weeks. Don't add a brand to
"get momentum".

## What else keeps running

| Asset | Stage | Status in this plan |
|---|---|---|
| **Ad studio** (326 leads) | 2 | **Runs from Tue 10 Nov, every weekday.** It's the fastest money and needs no audience. Dhruv sends every email |
| **MMS products**, six on Gumroad | 3 | Live from week 0. Featured in the welcome emails |
| **MMS Etsy shop** | 3b | Week 4, after the AI-guide listings are fixed |
| **Scam Decoded kit**, $9 | 9b | Live from week 2 |
| **Free web apps** (calculators, scam checker, budget app with $3 Pro) | 9a | Week 2. Search traffic with no audience needed. The Chrome extension ($5 developer fee) waits: it's spend |
| **1099 Money tracker** ($15) and **freelance tax app** | 9d | Wait for brand 3. The calculator could go up with 9a if Dhruv wants search traffic early, with no posting |
| **Affiliates** | 7 | MMS applies on day 10; Scam's (Aura, 1Password, NordVPN) once it has posts |
| **B2B newsletters** (PR #13) | — | **Parked.** Cold email needs Dhruv's OK. If Dhruv gives it, the pitch goes out in late Jan, timed to NCPW (28 Feb-6 Mar), using Scam Decoded's posts as samples |
| **Dinero Simple** (PR #11) | 9c | Paused. Content stays in the repo |
| **Email funnel** | 5 | MMS from week 0, Scam from week 2. Double opt-in and the CAN-SPAM footer with a real postal address (`sender-setup-guide.md`) |

## Changes to fold into GO_LIVE

1. Stage 9's order becomes **9b Scam Decoded, then 9a apps (same week), then 9d 1099 Money, then 9c Dinero**.
2. Stage 9's intro gets the brand-3 gates above, in place of "after Money Made Simple is posting".
3. R6's "Day 7" row names Scam Decoded as the next brand.
4. 9b gets a line: long videos upload only after their `LONG_VIDEO_RECORDINGS.md` recording.
5. 9d's "posting plan starts Nov 16" becomes "starts when the brand-3 gates pass (week 8 at the earliest)".

## Sources

`docs/GO_LIVE.md` (go-live branch, read 2026-11-07); `launch-playbook.md`; `risk-memo.md`;
`seasonal-demand-feb-jun-2027.md` ([FTC NCPW](https://consumer.ftc.gov/ncpw), 28 Feb-6 Mar 2027);
`launch_thresholds.json`; `youtube-policy-review-nov-2026.md`; `spanish-and-legal-review-options.md`;
`first-100-followers-2026.md`. Hours are our estimates from GO_LIVE's own per-step timings.
