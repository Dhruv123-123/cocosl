# January 2027 pricing check: our budget and tax templates against Etsy and Gumroad

Written 2026-11-07, for prices that should be set before the January peak. **Docs only.** No price has been
changed. The Etsy figures come from RankHero's public keyword pages, which sample 50-70 USD listings per
keyword. Etsy's own listing data isn't public without an API key, and we don't scrape. Gumroad publishes no
price statistics, and its Discover search only renders in a browser, so the Gumroad side covers fees and
positioning, not a market median. Our prices come from `PRODUCTS_CATALOG.csv` (121 rows).

## TL;DR

| Keyword (Etsy) | Median | Average | Under $10 | Our matching products | Verdict |
|---|---:|---:|---:|---|---|
| budget planner | $6.99 | $8.94 | 76% | Monthly Budget Planner **$6**; 30+ one-page sheets **$3** | Planner fine. One-page sheets are cheap but right as entry items |
| budget spreadsheet | $7.49 | $9.44 | 61% | Monthly Budget Sheet $9, 2027 Budget Sheet $12 (Gumroad) | Fine, slightly above median |
| budget binder | $7 | $12.07 | 61% | Budget Binder (10) **$12**, Mega Bundle (40) **$19** | Fine: bundles should sit above the median |
| savings challenge | $4 | $7.20 | 86% | 15 challenges **$3**, pack of 12 **$8** | **Raise singles to $4** (the median) |
| debt payoff tracker | $8.67 | $9.86 | 64% | Coloring tracker $4, Debt-Free Date Planner **$17** | $17 is double the median. Keep it only if the listing leads with "guide + spreadsheet", otherwise $12 |
| 2027 planner | $12.25 | $19.88 | 47% | 2027 Budget Planner **$12**, 2027 Money HQ (Notion) $24 | On the median. Fine |
| tax tracker | **$17** | $19.57 | 37% | Quarterly Tax Tracker **$15** | **Raise to $17** before 1 Jan (people pay more for tax tools) |
| small business bookkeeping | $10 | $13.24 | 50% | Freelancer Money Bundle **$49**, Rate & Contract Kit $29 | $49 is at the top of the range ($50). Show the bundle comparison; consider $39 |
| presupuesto (Spanish) | no price data ("not enough data") | — | — | Dinero Simple $5-29 | Too few listings to compare. Keep parity with the English prices |
| notion budget template | no price data | — | — | Notion range $5-24 | No benchmark. Searches fell 33% year on year (1,900 a month) |

**Timing:** "budget planner" searches peak in **January**, about 22% above Nov-Dec (74K vs 60.5K, RankHero).
"quarterly tax" peaks in **January and April** (8,100 each, the estimated-payment months). So January is
full-price season. Holiday codes (`bfcm-plan-2026.md`) should end by 31 Dec, with new prices from 1 Jan, and
no January discounts on tax products.

## 1. What a sale nets at our prices

| Price | Etsy net (listing $0.20 + 6.5% transaction + 3% + $0.25 processing) | Gumroad direct (10% + $0.50) | Gumroad Discover (30%) |
|---:|---:|---:|---:|
| $3 | ~$2.27 (24% in fees) | $2.20 | $2.10 |
| $4 | ~$3.17 | $3.10 | $2.80 |
| $5 | ~$4.08 | $4.00 | $3.50 |
| $12 | ~$10.41 | $10.30 | $8.40 |
| $17 | ~$14.94 | $14.80 | $11.90 |

Etsy Offsite Ads take another 15% on sales they bring in (12% for shops over $10K a year), and US rates vary
slightly. Gumroad fees are from [gumroad.com/pricing](https://gumroad.com/pricing), read today.
**Moving $3 items to $4 adds about $0.90 a sale (+40% net)** for a price that's still at the savings-challenge
median.

## 2. Recommended price changes (for the products thread)

| Product | Now | Suggested from 1 Jan 2027 | Why |
|---|---:|---:|---|
| Single savings challenges and one-page trackers (Etsy, ~35 listings) | $3 | **$4** | Median for "savings challenge" is $4; 86% of listings are under $10 anyway |
| Quarterly Tax Tracker (Etsy + Gumroad) | $15 | **$17** (2027 edition) | "tax tracker" median $17; it's being re-dated for 2027 anyway (`etsy-seo-playbook.md`) |
| Debt-Free Date Planner | $17 | $17 if the listing shows the guide + spreadsheet; else **$12** | Twice the tracker median |
| Freelancer Money Bundle | $49 | **$39** or keep $49 with a "worth $59 separately" line | Bookkeeping median $10, top of range $50 |
| Savings Challenge Pack (12) | $8 | **$10** | Keeps the pack under 12 × $4 = $48 while the singles go up |
| Everything else | — | No change | Within the market range |

Same price on Etsy and Gumroad, as the catalog already does, so neither channel undercuts the other.

## 3. Caveats

- RankHero's samples are small (51-72 listings per keyword) and include physical planners in some
  keywords ("2027 planner"), which pushes averages up. Medians are the safer guide.
- Its pages were updated between Jul and Oct 2026; re-check "tax tracker" and "budget planner" in late
  December, by hand.
- Prices are one of three levers. `etsy-seo-playbook.md` found that photos and first lines are the bigger
  problems, so fix those first. A higher price on a listing nobody sees changes nothing.

## Sources

RankHero keyword pages, read 2026-11-07: [budget planner](https://www.rankhero.com/keywords/budget-planner) (28 Oct 2026),
[budget spreadsheet](https://www.rankhero.com/keywords/budget-spreadsheet) (15 Sep), [budget binder](https://www.rankhero.com/keywords/budget-binder) (20 Oct),
[savings challenge](https://www.rankhero.com/keywords/savings-challenge) (9 Sep), [debt payoff tracker](https://www.rankhero.com/keywords/debt-payoff-tracker) (13 Oct),
[2027 planner](https://www.rankhero.com/keywords/2027-planner) (29 Sep), [tax tracker](https://www.rankhero.com/keywords/tax-tracker) (25 Jul),
[small business bookkeeping](https://www.rankhero.com/keywords/small-business-bookkeeping) (11 Sep), [quarterly tax](https://www.rankhero.com/keywords/quarterly-tax),
[presupuesto](https://www.rankhero.com/keywords/presupuesto), [notion budget template](https://www.rankhero.com/keywords/notion-budget-template).
[Gumroad pricing](https://gumroad.com/pricing). Our prices: `/mnt/project-files/content-factory/PRODUCTS_CATALOG.csv`.
