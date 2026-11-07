# 1099 Money Threads/X growth kit

The short-form partner to `../linkedin/`. Everything is posted and replied to by hand. Nothing is automated
(X charges for API posting).

| File | What it is |
|---|---|
| `README.md` (this file) | Profiles, the 30-day plan, the daily routine, how it fits with the other packs |
| `POSTS.md`, `posts.json` | 30 days of posts for freelancers, Nov 16 to Dec 15, 2026 (built by `build_threads_x.py`) |
| `REPLIES.md` | 24 reply templates for joining other people's conversations |
| `images/x-header.png` | X header, 1500x500 (from `render_header.mjs`). Profile picture: `../linkedin/images/page-logo.png` |

## Profiles

Run both as the **1099 Money** brand (Threads uses the Instagram account @1099money; X is @1099money or the
closest free handle). The LinkedIn kit is the one posted from Dhruv's personal profile; these are brand accounts.

**X**
- **Name:** 1099 Money
- **Bio** (160 max; this is 134):
  > Freelance money in plain numbers: rates, invoices, contracts and quarterly taxes. Free calculators below. Educational, not tax advice.
- **Website:** https://1099money.netlify.app
- **Header:** `images/x-header.png`. **Photo:** `../linkedin/images/page-logo.png`
- **Pinned post:** the Threads/X version in `../distribution/PINNED_POSTS.md` ("How 1099 Money makes money").

**Threads**
- **Bio** (150 max; this is 125):
  > Rates, invoices and taxes for freelancers, worked out with real numbers. Free tools in the link. Educational, not tax advice.
- **Link:** https://1099money.netlify.app
- **Pinned post:** same as X.
- Threads and Instagram share the photo and name; keep them identical to X.

## The 30-day plan

One post or short thread a day, Nov 16 (launch day) to Dec 15, 2026, the **same text on both platforms**.
Every part fits X's 280-character count (emoji and symbols count double there), so it fits Threads too.

- **Seven formats rotate**, never the same two days running: numbers (5), thread (5), question (5),
  hot take (4), myth-fact (4), one-liner (4), checklist (3).
- **Topics:** tax (10), rates (9), invoicing (6), clients (3), contracts (1), pipeline (1) — weighted toward
  pricing and getting paid, which the LinkedIn kit and the site's rate calculator and invoice template support.
- **No links in posts.** Both platforms show link posts to fewer people. Where a free tool helps, the
  **link reply** goes in as the first reply to your own post.
- **No first-person stories.** It's a brand account: advice and arithmetic, not anecdotes.

**Fitting with the other packs.** The Q4 pack (`../q4/POSTS.md`) has a Threads/X version for Nov 20, 24, 27,
Dec 1, 4, 8, 11 and 15. On those days post both: this plan in the morning, the Q4 post in the afternoon.
Two a day is normal on both platforms. From Dec 16, the Q4 posts carry on alone, then the tax-season pack
(`../tax-season/`) from Jan 19.

## Daily routine (about 20 minutes)

1. Post the day's text on X and on Threads (for a thread, reply to yourself on X; use "Add to thread" on Threads).
2. Post the link reply if there is one.
3. Reply to every reply on your posts within a few hours. Replies are most of the reach on both platforms.
4. Leave 5 to 10 replies on other people's posts using `REPLIES.md`, rewritten for each one.
5. Once a week, note followers and link clicks, and which formats got replies. Write more of those.

## Rebuild

```
python3 launch/1099-money/threads-x/build_threads_x.py
node launch/1099-money/threads-x/render_header.mjs     # needs Playwright
```
