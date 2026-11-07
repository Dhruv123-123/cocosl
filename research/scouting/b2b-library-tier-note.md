# Note for PR #13: a new price for Community Scam Watch's library system tier

Written 2026-11-07 for `launch/b2b/community-scam-watch/` on PR #13. **Docs only.** Nothing in PR #13 was
changed.

**Now:** $19 a month for one location; **$59 a month for a system** (up to 10 branches, or every center in an
Area Agency on Aging region). Annual plans get 2 months free.

## Recommendation

| Tier | Now | **Proposed** | Per year (annual, 2 months free) |
|---|---|---|---|
| Single location (branch, senior center) | $19 a month | **$19 a month** (no change) | $190 |
| Small system (2-4 locations) | $59 | **$49 a month** | $490 |
| System (5-20 locations) | $59 (up to 10) | **$12 per location a month** (10 = $120, 20 = $240) | 10 locations: $1,200 |
| Large system (21+) or a whole Area Agency on Aging | $59 | **Quote; start at $250 a month** | from $2,500 |
| **New:** credit-union-sponsored | — | **$99 a month**, paid by a local credit union, for up to 5 locations, with "brought to you by [credit union]" | $990 |

## Why

1. **Systems spend far more than $59 on single e-resources.** One California system's committee (SJVLS,
   Aug 2024) weighed Brainfuse at $231,700 a year, LinkedIn Learning at $145,110, LearningExpress at
   $97,915, Udemy via Gale at $75,000 and a Gale package at $33,000-63,389. At $59 a month ($708 a year),
   our system tier is under 1% of the cheapest of those. Charging per location keeps the price tied to how
   much use a system gets.
2. **Single branches and tiny libraries have very small budgets, so $19 should stay.** IMLS's Public
   Libraries Survey (FY2018) puts the median electronic-materials spend at **$0.20 per person a year for
   libraries serving under 2,500 people**, and $0.27 for 2,500-9,999. A library serving 2,500 people spends
   about **$500 a year on all e-resources**. Our $228 a year is close to half of that. Treat it as
   programming or outreach spend, not the e-resource budget, and **sell to the programming librarian or
   the senior center director**.
3. **That's why the sponsored tier matters.** Banzai is free to schools because "a local financial
   institution" pays, and it's "used by over 2,500 partners". A credit union paying $99 a month to put its
   name on scam alerts at 5 local libraries or senior centers removes the budget problem. It also gives
   the credit-union alert sales a second product to offer.
4. **Prices in this market are hidden.** Vendors quote on request (`b2b-pricing-benchmarks.md`), so a clear
   public per-location price is easy for a library board to approve.

## What would change in PR #13

- `community-scam-watch/product.json` and `README.md`: the tier table above.
- `sales-sheet.html`: replace the "$59 a system" line with "From $49 for 2-4 locations; $12 a location
  for larger systems".
- `credit-union-alert/README.md` and its sales sheet: add the sponsored option.
- `revenue_model.py` (PR #2) prices Scam Watch at $35 + $12.50. Re-run it if these tiers are adopted.

## Sources

[SJVLS Electronic Resources Committee minutes, 15 Aug 2024](https://www.sjvls.org/sites/default/files/2024-10/ERC_minutes_240815.pdf);
[IMLS PLS FY2018 research brief](https://imls.gov/sites/default/files/2021-02/pls_fy18_research_brief.pdf) (Table A3);
[banzai.org](https://banzai.org/); `b2b-pricing-benchmarks.md`.
