# 1099 Money LinkedIn growth kit

Everything here is posted and sent by hand. Nothing is automated.

| File | What it is |
|---|---|
| `README.md` (this file) | Page profile, personal profile, the 30-day plan, how it fits with the other LinkedIn posts |
| `POSTS.md`, `posts.json` | 30 posts for freelancers and solo consultants, Nov 16 to Dec 15, 2026 (built by `build_linkedin.py`) |
| `COMMENTS.md` | 24 comment templates for engaging with other people's posts |
| `images/` | Page cover (1128x191), personal banner (1584x396), page logo (400x400), from `render_banner.mjs` |

## Where to post from

Post from **Dhruv's personal profile**, then reshare each post to the 1099 Money page later the same day.
On LinkedIn, posts from people usually reach far more people than posts from company pages, and comments
(see `COMMENTS.md`) can only build a following when they come from a person. The page is the place the
profile points to, and it carries the Q4 and tax-season posts.

## The 1099 Money page

Set these at linkedin.com → For Business → Create a Company Page → Company.

- **Name:** 1099 Money
- **LinkedIn public URL:** linkedin.com/company/1099money (or the closest free one)
- **Website:** https://1099money.netlify.app
- **Industry:** Financial Services
- **Company size:** 0-1 employees
- **Company type:** Self-employed
- **Logo:** `images/page-logo.png`
- **Cover image:** `images/page-cover.png` (Page → Edit → Header)
- **Custom button:** "Visit website", pointing to https://1099money.netlify.app/rate-calculator/
- **Tagline** (LinkedIn allows 120 characters; this is 103):

  > Free rate, tax and deduction calculators for US freelancers and consultants. Plain numbers, 2026 rules.

- **Overview** (about 1,000 of the 2,000 characters allowed):

  > 1099 Money helps US freelancers, consultants and contractors with the money side of working for
  > yourself: what to charge, what to set aside, and what to pay the IRS and when.
  >
  > Everything on the site is free and runs in your browser. Nothing you type is sent anywhere.
  >
  > - Rate calculator: work back from the take-home pay you want to the hourly and day rate you need
  > - Quarterly tax calculator: what to pay each quarter and what to set aside from every payment
  > - January 15 calculator: the Q4 payment and the file-early alternative
  > - Deduction finder: 18 yes/no questions, a list of the deductions that apply to you
  > - Mileage calculator for delivery and rideshare drivers
  >
  > Posts here cover pricing, clients, contracts, invoicing and taxes, worked out with real numbers.
  >
  > Educational, not tax, legal or financial advice. Figures use 2026 federal rules; check irs.gov
  > before acting.

- **Specialties** (up to 20): freelance taxes, quarterly estimated taxes, self-employment tax, freelance
  pricing, consulting rates, freelance contracts, invoicing, 1099-NEC, deductions for the self-employed,
  solo 401(k)

## Dhruv's personal profile

Only change what's true for you. Suggested lines:

- **Headline** (220 characters max): `Building 1099 Money: free rate and tax calculators for freelancers and consultants`
  (add your own role first if you have one, e.g. `[Your role] · Building 1099 Money: ...`)
- **Banner:** `images/profile-banner.png`. The text sits on the right because the photo covers the bottom left.
- **Featured section:** add the rate calculator (https://1099money.netlify.app/rate-calculator/) and the
  quarterly calculator (https://1099money.netlify.app/) as links.
- **Experience:** add 1099 Money as a position so it links to the page. Description: the page tagline.
- **About section:** one line on what 1099 Money is, plus the hashtags #freelancing, #consulting, #pricing, #taxes.

## The 30-day plan

One post a day from Nov 16 (the site's launch day) to Dec 15, 2026. Weekdays carry the longer posts
(worked numbers, checklists, scripts); weekends are short questions and myth-vs-fact posts. Seven formats
rotate and none runs two days in a row: numbers (6), checklist (5), question (5), myth-fact (4),
script (4), compare (3), mistake (3).

**Topics:** rates and pricing (13), tax (5), clients (4), invoicing (4), contracts (3), pipeline (1).
The rate posts lead to the free rate calculator; the tax posts lead to the quarterly calculator.

**Daily routine (about 30 minutes):**
1. Post that day's text from `POSTS.md` around 8 to 9 a.m. your time.
2. If it has a **first comment**, post it as a comment straight away. That's where the link goes.
3. Reply to every comment on your post during the day.
4. Leave 5 to 10 comments on other people's posts using `COMMENTS.md` (written fresh each time).
5. Reshare to the 1099 Money page.

**Fitting with the other LinkedIn posts:** the Q4 pack (`../q4/POSTS.md`) has LinkedIn versions dated
Nov 20 to Jan 14, and the tax-season pack (`../tax-season/POSTS.md`) runs Jan 19 to Apr 14, 2027.
During these 30 days, post the Q4 ones **on the 1099 Money page** on their dates (Nov 20, 24, 27, Dec 1,
4, 8, 11, 15), not on the personal profile, so the profile has one post a day. From Dec 16, the personal
profile picks up the Q4 posts on their dates, then the tax-season pack, so it never goes quiet.

**What to watch:** followers, profile views and visits to the site from LinkedIn each week (in your
site analytics, if you've turned it on). After two weeks, look at which formats got the most comments and write more of those.

## Rebuild

```
python3 launch/1099-money/linkedin/build_linkedin.py     # posts.json + POSTS.md
node launch/1099-money/linkedin/render_banner.mjs         # images/ (needs Playwright)
```
