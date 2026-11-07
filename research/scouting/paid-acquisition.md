# Paid ads: when they'd pay for our products, and a $100 test plan

Written 2026-11-07. **Docs only. Nothing has been spent and no ad account has been touched.** Ad
benchmarks come from public reports (linked); our own numbers come from the financial model
(`docs/FINANCIAL_MODEL.md`, PR #3), the shop prices on the PR #4 site, and the newsletter research
(`newsletter.md`). Anything marked *assumption* is a planning number to replace with our own data.

## TL;DR

1. **Ads sending cold traffic straight to a $5-39 product lose money on every platform.** At a typical
   1-2% purchase rate, a $12 product can only afford about $0.10-0.19 a click, and the cheapest finance
   clicks cost $0.60-1.50.
2. **Ads to the free lead magnet get close but don't break even yet.** A subscriber costs about $2-5 on
   Meta or Pinterest, and is worth an estimated $0.80-2.40 in the first 90 days *once* the thank-you-page
   offer and paid recommendations are switched on. Today, with neither live, a subscriber is worth less.
3. **When ads start to make sense:** after 30 days of organic data shows what a subscriber is actually worth,
   with a self-liquidating offer on the thank-you page, and with creative that has already won organically.
   Then boost the winner.
4. **If you run the $100 test, use Meta**: the cheapest finance clicks ($0.86 median for traffic), the best
   published lead conversion, and it can boost a Reel that already did well. Pinterest second. Reddit not yet:
   finance clicks there run $1.50-4.00.

## 1. What a sale and a subscriber are worth to us

### Net per sale

Gumroad direct sale fee, from `docs/FINANCIAL_MODEL.md`: **10% + $0.50, plus card processing about
2.9% + $0.30**. So net ≈ price × 0.871 − $0.80.

| Product (brand) | Price | Net per sale |
|---|---|---|
| Printables (Money Made Simple shop, most items) | $3 | $1.81 |
| Bill Cut Kit | $5 | $3.56 |
| Family Scam-Proofing Kit (Scam Decoded); Credit Report Audit Kit; budget sheet | $9 | $7.04 |
| The 20-Minute Budget (MMS main offer) | $12 | $9.65 |
| Quarterly Tax Tracker (1099 Money) | $15 | $12.26 |
| Investing Starter Kit; Money Sheets Bundle | $19 | $15.75 |
| Rate & Contract Kit (1099 Money) | $29 | $24.46 |
| Money Toolkit Bundle (MMS) | $39 | $33.17 |
| Freelancer Money Bundle (1099 Money) | $49 | $41.88 |

**Break-even cost per sale (CPA) = net per sale.** It's the most an ad can pay to get one purchase and
still not lose money, before counting anything else the buyer brings in (email, affiliates, a second sale).

### Break-even cost per click, straight to a product page

Break-even CPC = net × purchase rate. Purchase rate from a cold ad click to a low-priced digital
product is the big unknown. **1-4% is the assumption here**; replace it with our own Plausible numbers
once there's organic traffic.

| Price | at 1% | at 2% | at 4% |
|---|---|---|---|
| $9 | $0.07 | $0.14 | $0.28 |
| $12 | $0.10 | $0.19 | $0.39 |
| $15 | $0.12 | $0.25 | $0.49 |
| $19 | $0.16 | $0.31 | $0.63 |
| $29 | $0.24 | $0.49 | $0.98 |
| $39 | $0.33 | $0.66 | $1.33 |
| $49 | $0.42 | $0.84 | $1.68 |

Against real click prices (section 2), only the **$39-49 bundles at 4%** come near break-even, and 4%
from cold traffic is optimistic. **Selling a product straight from an ad doesn't work for us at these
prices.**

### What a subscriber is worth (first 90 days)

| Source | Per new subscriber | Basis |
|---|---|---|
| Paid recommendations on the thank-you step (Kit Creator Network / SparkLoop) | $0.30-0.70 | `newsletter.md` estimate: $2-3 per referral × 20-30% pick one × ~76% after fees × ~80% verified |
| Welcome sequence sale of the main product ($12-15) | $0.10-0.37 | *assumption*: 1-3% of subscribers buy within 21 days |
| Thank-you-page offer, $5-9 (not built yet) | $0.20-0.70 | *assumption*: 5-10% take a small offer right after signing up |
| Affiliate clicks from emails | $0.20-0.60 | *assumption*, using the PR #3 model's 2-3% affiliate conversion |
| **Total, with everything switched on** | **about $0.80-2.40** | |
| **Total today** (no thank-you offer, no paid recommendations) | **about $0.30-1.00** | |

**Break-even cost per subscriber (CPL) is therefore about $0.80-2.40**, and only once both the
thank-you-page offer and paid recommendations are live. Long-term value (people who stay a year and buy
twice) is higher, but don't spend against it until the data shows it.

1099 Money is the exception to watch: tax buyers have a deadline, the tracker is $15, and the checkout
upsell to the $49 bundle raises the average order. If 20% take the $34 upgrade, the average net per buyer
is about $18 rather than $12. It's the best candidate for paid ads in **January, March-April, June and
September**, the weeks before quarterly payments are due.

## 2. What clicks and leads cost (public benchmarks)

| Platform | Finance CPC | Other numbers | Source |
|---|---|---|---|
| **Meta** (Facebook + Instagram) | **$0.86** traffic, finance & insurance (median) | All industries: traffic CPC $0.60, lead CPC $1.80, lead conversion 8.54%, **cost per lead $27.39**. Education: lead CPC $1.72, conversion 15.87%, CPL $26.31 | WordStream/LocaliQ, 14 Sep 2026, via [Digital Applied](https://digitalapplied.com/blog/facebook-ads-benchmarks-2026-cpc-cpm-ctr-industry) |
| **Pinterest** | **$0.80-1.50** finance | Finance CPA ~$12-15, CTR 0.3-0.5%, conversion ~0.5-1.0%: the costliest category on Pinterest. **No minimum budget**; $100-500 a month suggested to start | AdBacklog 2025 and a WebFX survey, via [Cropink, 20 Aug 2026](https://cropink.com/pinterest-ads-cost) |
| **Reddit** | **$1.50-4.00** finance subreddits (avg $2.50) | Financial services CPL $60-150. Broad interest CPC ~$0.75. **$5/day minimum**; $20-50/day suggested for a real test | [Benly, Mar 2026](https://benly.ai/learn/reddit-ads/reddit-ads-cost-benchmarks) (no sample size given) |

The $26-27 "cost per lead" figures are for businesses buying sales leads (quotes, consultations).
A free checklist converts far better than a sales form, so our cost per subscriber should be much lower.
**Our estimate: $2-5 per subscriber** on Meta or Pinterest, from $0.60-1.50 clicks and a 30% sign-up rate
on the landing page (*assumption*; the site's sign-up rate from organic traffic will tell us the real one).

**$2-5 per subscriber against a $0.80-2.40 value means paid ads lose money until two things change:**
the value per subscriber goes up (thank-you offer and paid recommendations live), and the cost goes down
(creative that already won organically, so clicks are cheaper).

### Rules that affect finance ads

- **Meta's "Financial products and services" special ad category** (required in the US since early
  2025) covers credit, loans, insurance, bank accounts, investment and payment services. Ads in it can't
  target by age, gender or ZIP code, and can't use lookalike audiences
  ([Jon Loomer](https://www.jonloomer.com/qvt/financial-products-and-services/)). **An ad for a free
  budgeting checklist probably isn't in that category, but an ad that names a credit card, a savings
  account or a broker is.** Keep paid creative about the checklist, not about any affiliate product.
- **No affiliate links in ads.** Send ads to our own page. Most affiliate programs (bank and card ones in
  particular) forbid paid traffic straight to their links, and it's the fastest way to lose an approval.
- **Same guardrails as organic:** no income claims, no "guaranteed", the AI label where the creative is
  AI-made, and the disclosure line where anything is affiliate.

## 3. When paid ads make sense: the gate

Spend nothing until **all five** are true:

1. **30+ days of organic sign-ups**, with at least 300 subscribers on one list, so we know that list's real
   sign-up rate, welcome-sequence purchase rate and unsubscribe rate.
2. **The thank-you page carries an offer** ($5-9, one click, no countdowns) and **paid recommendations
   are on** (Kit Creator Network + SparkLoop). Together these are most of the value in the table above.
3. **Measured value per subscriber ≥ $1.50** from (1) and (2).
4. **A creative that already won organically**: a Reel or pin in the top 10% for saves or link clicks.
   Boosting proven creative is far cheaper than testing cold ads.
5. **Tracking that works without guessing**: a Meta lead-form ad feeding Kit (through Zapier), or the
   Meta pixel on the landing page with the privacy page updated to say so. Plausible alone can't tell
   Meta who signed up.

## 4. The $100 test (only once the gate is passed)

**Platform:** Meta. **Brand:** whichever list has the highest measured value per subscriber; 1099
Money if it's within six weeks of a quarterly tax deadline, otherwise Money Made Simple.

| Setting | Choice |
|---|---|
| Objective | Leads (instant form → Kit with double opt-in), or Traffic to the landing page if the pixel is set up |
| Budget | $10 a day for 10 days, one campaign, one ad set |
| Audience | US, 18+, broad (Advantage+ audience). No interest stacking at this budget |
| Creative | 3 ads: the top organic Reel as-is, the same Reel with a new first 2 seconds, and one static checklist image |
| Landing | The lead magnet page, not a product page |
| Offer after sign-up | The $5-9 thank-you-page offer, plus paid recommendations |

**Kill rules** (check daily; each applies on its own):

| When | Rule | Action |
|---|---|---|
| After $15 on an ad | Link CTR under 0.8% | Turn that ad off |
| After $30 total | Cost per subscriber over $5 | Stop the campaign |
| After $50 total | Cost per subscriber over $3 | Stop the campaign |
| Any time | A comment or complaint suggesting the ad is misleading, or an ad rejection | Pause and fix before spending more |
| Any time | Unsubscribe rate from ad sign-ups over 2× the organic rate | Stop: the audience is wrong |
| After $100 | Cost per subscriber at or under the measured value per subscriber, and at least one thank-you-page sale | **Continue** at $10/day for 2 more weeks, then judge on 30-day value |
| After $100 | Anything else | Stop and write down what was learned |

**What $100 can and can't tell us:** at $0.60-1.00 a click, $100 buys about 100-165 clicks, or about
30-50 subscribers at a 30% sign-up rate. That's enough to measure **cost per subscriber** roughly. It's not
enough to measure the **purchase rate** reliably (one or two sales either way). So the decision at $100
is about cost per subscriber; the purchase rate is judged over the following 30 days.

## 5. Platform by platform

- **Meta:** the best first test. Cheapest finance clicks, it can boost proven organic Reels, and lead-form
  ads skip the landing page. Watch the special ad category if the creative mentions any financial product.
- **Pinterest:** second. No minimum budget, and promoted pins keep working after the spend stops because
  saves continue. But finance clicks are $0.80-1.50, with ~0.5-1% conversion. Only promote a pin that's
  already in the top 10% organically, to a lead magnet. Never promote the $3 printables: at $1.81 net,
  no click price can pay for them.
- **Reddit:** not yet. Finance clicks cost $1.50-4.00, and r/personalfinance-style communities react
  badly to ads from unknown brands. Revisit for 1099 Money (r/freelance-type audiences) once there's a
  proven offer, and test with Reddit's $5/day minimum.
- **Paid newsletter recommendations (the reverse direction):** paying other newsletters $1.50-3 a
  subscriber through SparkLoop or Kit is often cheaper than social ads for email growth, and the
  subscribers already read newsletters. Price it the same way: only when value per subscriber ≥ cost.

## Open questions for Dhruv

- Is there a monthly ad budget at all for the first 90 days, or is it organic only? The plan above
  assumes organic only until the gate in section 3 is passed.
- Which list should get the first test? The recommendation is 1099 Money around the 15 Jan 2027 quarterly
  payment, if its list is ready by mid-December.
