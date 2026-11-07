# Etsy SEO notes and seasonal calendar (November 2026)

Every listing's title, 13 tags and attributes now come from `seo.py`, and each `LISTING.md` shows them. This page explains
the choices and says when to push which listings. Everything here comes from public signals only: Etsy's own Seller
Handbook and the free keyword pages on rankhero.com. Those search numbers are third-party estimates, so use them to
rank keywords against each other, not as exact counts.

## What changed and why

| Before | After | Why |
|---|---|---|
| Long, comma-stuffed titles (18 to 22 words) ending in "Printable, Letter + A4 PDF" | Each title is under 15 words and names the item first | Etsy: "Consider using less than 15 words", and shoppers only see the first few words in search |
| Tags repeated title words and padded with "printable planner" / "undated planner" | Tags cover synonyms, long-tail phrases and who the item is for | Etsy: tags should be "multi-word phrases" a shopper would type. Size and file type now sit in attributes |
| No attributes | Each listing has a short attribute list (colours, file type, paper size, planner type, dated/undated, holiday) | Etsy: attributes "act like tags", and a phrase set as an attribute doesn't need its own tag |

Descriptions didn't change: their first sentence already names the item.

## Keyword signals used

| Keyword | Est. searches / month | Competing listings | Pattern | How we use it |
|---|---|---|---|---|
| budget planner | ~60,500 (74,000 in Jan) | ~250-290k | Peaks in January | A tag on the core planners and bundles; too crowded to lead most titles |
| savings challenge | ~9,900 (18,100 Dec, 27,100 Jan) | ~92-112k | **About 3x in January** | A tag on every challenge. Their titles name the specific challenge |
| debt snowball | ~27,100 | ~9,600 | Steady; highest in Jan and Mar | **Best ratio we found.** A tag on every debt listing, and it leads the Debt-Free Date Planner's title |
| bill tracker | ~5,400 (6,600 Jan) | ~28k | Small January bump | Leads the bill tracker's title; a tag on the bill-related listings |
| debt tracker / debt payoff | ~2,900 / ~2,400 | ~48k / ~28k | January, and again Aug-Sep | Tags on the debt listings |
| money saving challenge | ~1,600 (3,600 Jan) | ~30k | January | Covered by "money challenge" plus "savings challenge" |
| budget printable | ~1,300 | ~107k | Flat | Used only as a filler tag (crowded and small) |
| 52 weeks savings | ~20 | ~4k | Tiny | Dropped. Shoppers type "52 week challenge" / "52 week savings" instead |
| 2027 planner | rose from 320 (Oct 2025) to 33,100 (Sep 2026) | ~70k | Climbs Jul to Sep, stays high to January | Leads the 2027 planner's title and tags |

Related tags that keep coming up next to these keywords: cash stuffing, sinking funds, cash envelopes, savings
challenges, paycheck budget, biweekly budget, budget binder, a6 binder, low income budget. We use them where they're true
of the product.

Sources: [Etsy Seller Handbook: The Anatomy of a Well-Crafted Etsy Listing](https://www.etsy.com/seller-handbook/article/1347574487014);
rankhero keyword pages for [budget planner](https://www.rankhero.com/keywords/budget-planner),
[savings challenge](https://www.rankhero.com/keywords/savings-challenge), [debt snowball](https://www.rankhero.com/keywords/debt-snowball),
[debt tracker](https://www.rankhero.com/keywords/debt-tracker), [debt payoff](https://www.rankhero.com/keywords/debt-payoff),
[bill tracker](https://www.rankhero.com/keywords/bill-tracker), [money saving challenge](https://www.rankhero.com/keywords/money-saving-challenge),
[budget printable](https://www.rankhero.com/keywords/budget-printable), [52 weeks savings](https://www.rankhero.com/keywords/52-weeks-savings),
[2027 planner](https://www.rankhero.com/keywords/2027-planner); [InsightAgent printables guide](https://www.insightagent.app/guides/etsy-printables-best-sellers)
(budget planners spike in January and stay steady; bundles earn bestseller badges more often than single items).

## Seasonal calendar

Rule of thumb: have a listing live and indexed **4 to 8 weeks before** its peak. Ranking changes take a couple of weeks
to settle. Don't rename a listing that's already selling during its own peak.

| When | What people search | Push these listings | What to do |
|---|---|---|---|
| **Now to mid-Nov** | 2027 planners (already high), Christmas budgets | 2027 Budget Planner, Christmas Budget Planner, Gift Budget Planner | List the 2027 planner **first, this week**. Pin the holiday pair at the top of the shop |
| **Late Nov (Black Friday, Cyber Monday)** | Gift lists, holiday spending | Same, plus the Mega Bundle | Use an Etsy sale (a real discount, set in Shop Manager) only if you want one. No fake "ends tonight" banners |
| **December** | Savings challenges climb about 2x; New Year goals | All 12 challenges, Savings Challenge Pack, Financial Goals Planner, No-Spend Challenge, 2027 planner | Update shop sections so "Savings Challenges" sits first. Pinterest pins for the challenges go out early December |
| **January (the biggest month)** | Budget planner +20%, savings challenge about 3x, bill tracker, debt | Everything. Lead with the 2027 planner, the bundles, the 52-week and 100-envelope challenges, the debt snowball items | Make sure every listing is live. Answer messages fast; reviews from January buyers carry the whole year |
| **February to April (tax season)** | Tax prep, side income, refunds | Side Hustle Income Tracker, Irregular Income Budget, Net Worth Tracker, Debt Snowball Worksheet ("put the refund on debt") | Point the shop announcement at tax-time organising. **Don't give tax advice.** The planner only marks the usual IRS dates and says to check irs.gov |
| **March** | Debt snowball has a second peak | Debt listings, Debt-Free Date Planner | Feature the debt trackers |
| **May to July (quiet)** | Travel and vacation funds, summer spending | Travel Fund Tracker, Grocery Budget Tracker, Weekly Budget Planner | Good months to add new listings and test new first photos |
| **August to September (back to school)** | Dated planners start climbing; debt payoff bumps | **Build and list the 2028 planner by mid-August:** `planner_2027.build(2028)` already works for any year | Copy the 2027 listing, change the year in the title and tags |
| **October** | 2028 planners, Christmas budgets begin | 2028 planner, holiday + gift planners | Same cycle as this November |

## When you renew or edit

- Change one thing at a time (title **or** first photo) and wait two to three weeks before judging it.
- The Search Visibility page in Shop Manager flags listings with missing details. Clear it after each batch.
- After a year, swap any tag that has brought in no visits (Shop Manager > Stats > search terms) for one from the related list above.
