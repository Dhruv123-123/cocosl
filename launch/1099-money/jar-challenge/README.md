# 1099 Money: the Tax Jar Challenge (Nov 16, 2026 – Jan 15, 2027)

**Why:** scouting found that savings-challenge hooks get about 6× the reach of other finance hooks
(`research/scouting/finance-formats-nov-2026.md`, PR #2: Draper's May 2026 study of finance TikToks). Our packs had none.

**The challenge:** from every client payment, move 25% (then your own percentage) into a separate tax account the
same day, until the last 2026 estimated payment on **Fri Jan 15, 2027**. One small step every Monday.

`content.json` holds 10 Shorts and 1 carousel. Every item has `series` ("Tax Jar Challenge 3/10") and `post_on`.

| Post on | # | Format | Title | Style |
|---|---|---|---|---|
| Mon Nov 16 | 1 | Short | The Tax Jar Challenge: 25% of every payment until Jan 15 | challenge-day-1 |
| Thu Nov 19 | – | Carousel | The Tax Jar Challenge: all 8 weeks on one page | checklist |
| Mon Nov 23 | 2 | Short | Your tax money needs its own account (Tax Jar, week 1) | how-to |
| Mon Nov 30 | 3 | Short | Is 25% right for you? Tax Jar week 2 | real-numbers |
| Mon Dec 7 | 4 | Short | Backfill since September 1: Tax Jar week 3 | myth-vs-fact |
| Mon Dec 14 | 5 | Short | 25% of the payment or the profit? Tax Jar week 4 | question-reply |
| Mon Dec 21 | 6 | Short | 3 ways to fill your tax jar on autopilot (week 5) | countdown |
| Mon Dec 28 | 7 | Short | Is your tax jar enough for Jan 15? Week 6 check | on-screen-calculation |
| Mon Jan 4 | 8 | Short | Set up your IRS payment now: Tax Jar week 7 | walkthrough |
| Mon Jan 11 | 9 | Short | Why your tax jar holds more than the payment (week 8) | explainer |
| Fri Jan 15 | 10 | Short | Payment day: pay from the tax jar, then start again | deadline-alert |

**Pin day 1** on TikTok, Instagram and YouTube for the whole challenge. Every check-in stands alone and says
"day 1 is pinned". On YouTube, set day 1 as each Short's related video.

## Swap plan: replace, don't add (the brand caps at 2 posts a day per platform)

Each challenge Short takes that day's 12:30 Short slot. Where the bumped Short is timely, it moves into the slot of a
weaker or overlapping Short that week, and that one goes to the evergreen backlog.

| Date | Challenge post | Bumped pack post | What to do with it |
|---|---|---|---|
| Nov 16 | Day 1 | Your first 1099 has no tax taken out (launch) | Move to Sat Nov 21; drop "The tax deadline after New Year's" (the challenge covers Jan 15) |
| Nov 19 | Carousel | none (Thursday has no carousel) | Add; still 2 posts on Instagram that day |
| Nov 23 | Week 1 | The rule that kills the underpayment penalty | Move to Sat Nov 28; "Your phone bill isn't 100% deductible" goes to the backlog |
| Nov 30 | Week 2 | Freelancers: Dec 15 is your health insurance deadline (month 1) | Move to Sat Dec 5; "It's not too late to cut your 2026 tax" goes to the backlog (Dec 3 covers year-end moves) |
| Dec 7 | Week 3 | Your 1099 might be wrong. Here's what to do. | Backlog: it works better in late January |
| Dec 14 | Week 4 | An LLC won't lower your taxes | Backlog (evergreen) |
| Dec 21 | Week 5 | Getting paid on payment apps? Read this first | Backlog: repost in January with 1099-K season |
| Dec 28 | Week 6 | Freelancers can still open an IRA | Move to Tue Dec 29; "The upside of self-employment tax" goes to the backlog |
| Jan 4 | Week 7 | Jan 15: the tax payment for last year (month 2) | Drop: the challenge covers it |
| Jan 11 | Week 8 | 1099 season starts now: what's coming by Feb 1 | Move to Thu Jan 14; drop "The Jan 15 tax payment is tomorrow" (week 8 and payment day cover it) |
| Jan 15 | Payment day | Due today: pay something | Drop: the challenge's payment-day post replaces it |

## Tracker

`apps/freelance-tax/downloads/tax-jar-tracker.pdf` (2 pages): the jar to colour in, the 10 steps with dates, the
2026 set-aside table and a payments log. It's a third bonus on the calendar thank-you page (`free/thanks/`), so the
"free jar tracker in the link in bio" captions lead there. Source: `launch/1099-money/lead-magnets/tax-jar-tracker/`
(`node .../build_pdf.mjs` rebuilds it).

## Rules kept (from the scouting note)

- Numbers are examples, never promises. Sam is labelled "Example, fictional" every time.
- No invented personal progress and no comment-for-something bait.
- 2026 set-aside numbers come from the site's tax model (`apps/freelance-tax/lib/tax.js`); the Jan 15 example
  ($6,500 − $4,875 = $1,625) matches the free q4 page.
- Check `claims_to_verify` before posting. Nothing here posts automatically.
