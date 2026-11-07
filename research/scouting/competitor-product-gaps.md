# What the top personal-finance sellers on Etsy and Gumroad sell that we don't make

Written 2026-11-07. **Docs only.** Etsy and Gumroad pages don't load listings for this environment (they
render client-side), so seller data comes from **EHunt's public Etsy rankings** (updated 1 Nov 2026,
ranked by weekly sales, revenue estimated by EHunt) and **InsightRaider's Gumroad snapshot** (23 Sep
2026, list price × public sales counter, so estimates, not reported earnings). Our side is
`PRODUCTS_CATALOG.md` (111 listings across four brands, PR #6) plus the templates and brand-shop products.

## TL;DR

The top Etsy finance sellers are mostly products we already make: paycheck budgets, annual budget
spreadsheets and savings challenges. **Five gaps are worth building**, in this order:

1. **A hyperlinked GoodNotes/Notability digital budget planner** (a tabbed PDF for iPad). It's #1 among
   EHunt's digital planners: LiveLovePlanners, **18,690 sales, 76 a week**. We have printables, Sheets
   and Notion, but nothing for iPad planner apps. The factory already renders PDFs, so this means adding
   internal links and tabs to a planner we already have.
2. **A wedding budget spreadsheet.** PrioriDigitalStudio's wedding planner spreadsheet: **10,719 sales,
   ~$104K**, #3 among digital planners. Our catalog has no life-event budgets (wedding, baby, moving).
   It's a Money Made Simple product, and it's a Google Sheet, which we already build.
3. **An "ADHD-friendly" budget planner.** Two of the top 10 budget-planner sellers use the term
   (MasterMoneyBudget's browser app, 68 a week; CustomGroupGifts' sheet, 4,728 sales). Our catalog uses
   it 0 times. Only use it for a real format difference (one screen, big buttons, a few decisions a day,
   colour cues), and never claim medical benefit.
4. **A Spanish budget spreadsheet on Etsy.** Heart2HeartbyYoli's Spanish monthly budget sheet sells
   **50 a week**, #6 among budget planners, with only 147 sales so far, so it's new and growing. Dinero
   Simple has Spanish printables (`Presupuesto Familiar` $9), but no Google Sheet. Blocked on the native
   review, like everything Spanish.
5. **A net-worth and investment dashboard ($19-39).** SendOwl (Jul 2026, no dataset) lists it as the
   higher-priced finance category, and our catalog has one net-worth item. Lower priority, since
   investment content carries more compliance care.

**Not worth copying:** physical savings binders and cash envelopes (four of the top Etsy ads are shipped
products, which means inventory or print-on-demand fulfilment), browser "apps" (hosting and support), and
$497 courses (Gumroad's "Notion Money Academy", ~1,152 sales). That's a course with a face and a teacher,
which doesn't fit faceless brands in year 1.

## 1. The top sellers we could see

**Etsy, "best budget planner" (EHunt, 1 Nov 2026):**

| # | Shop | Product | Type | Weekly | Total sales | We make it? |
|---|---|---|---|---:|---:|---|
| 1 | TheWeeklyCrew | Budget planner, monthly paycheck tracker | Excel / Google Sheets | 130 | 13,533 | **Yes**: Paycheck Budget Sheet $7, Paycheck Budget Planner $4 |
| 2 | PrioriDigitalStudio | Ultimate annual budget spreadsheet | Google Sheets | 91 | 16,104 | **Yes**: 2027 Budget Sheet $12 |
| 3 | LiveLovePlanners | Digital budget planner, GoodNotes | Hyperlinked PDF | 76 | 18,690 | **No** (gap 1) |
| 4 | MasterMoneyBudget | ADHD budget planner, browser app | Web app | 68 | 219 | No (app; see gap 3 for the sheet version) |
| 5 | ByHeidiGB | Wedding planner bundle | Sheets + Canva | 60 | 1,404 | **No** (gap 2) |
| 6 | Heart2HeartbyYoli | Spanish monthly budget planner | Google Sheets | 50 | 147 | Printable only (gap 4) |
| 7 | TheWeeklyCrew | Biweekly paycheck budget | Google Sheets | 43 | 7,352 | **Yes** (paycheck sheet) |
| 8 | CustomGroupGifts | ADHD digital budget planner | Google Sheets | 37 | 4,728 | **No** (gap 3) |
| 9 | PlannerSheetsCo | Budget by paycheck | Google Sheets | 35 | 83 | **Yes** |
| 10 | DigitalDoodlesToday | Biweekly budget sheet | Google Sheets | 34 | 973 | **Yes** |

**Etsy, "best digital planner" (EHunt, same date), finance-related rows:** LiveLovePlanners (above),
PrioriDigitalStudio's **wedding planner spreadsheet with a budget tracker (10,719 sales, ~$104K)**, and
MasterMoneyBudget. The others are general, reading or student planners.

**Etsy search page "best seller budget" (read today):** besides the sheets above, four ads were for
**physical** savings products (a $27 savings-challenge set, a $36 "Happy Mail Jail" box, a $19.99 100
Envelopes binder), plus a 124-page printable planner at $9.97 and a bundle at $4.40.

**Gumroad (InsightRaider, Sep 2026, 365 fixed-price Notion templates with public counters):** the top
sellers "sell systems and education, not single pages". Ultimate Brain ($129, ~15K sales) isn't finance.
**The Notion Money Academy ($497, ~1,152 sales)** is the only finance product in the top three.

## 2. Our coverage against what sells

| Product type selling | Ours | Gap? |
|---|---|---|
| Paycheck / biweekly budget sheet | Paycheck Budget Sheet $7, Notion Paycheck Budget $7, printable $4 | No |
| Annual budget spreadsheet | 2027 Budget Sheet $12, 2027 Money HQ (Notion) $24 | No |
| Savings challenges (printable) | 52-week, 100-envelope, 26-paycheck, holiday, Savings Challenge Pack $8 | No |
| Savings challenges (poster) | Print-on-demand challenge posters | No |
| Sinking funds, bill tracker, debt payoff | Yes (printables, sheets, $17 Debt-Free Date Planner, KDP journal) | No |
| **Hyperlinked iPad planner** | — | **Yes** |
| **Wedding / baby / moving budget** | — | **Yes** |
| **"ADHD-friendly" budget** | — | **Yes** |
| **Spanish budget Google Sheet** | Spanish printables only | **Yes** (after review) |
| Net-worth / investment dashboard | 1 item | Partly |
| Physical binders and envelopes | — | Skip (fulfilment) |
| Finance course ($200+) | — | Skip for now |

## 3. How to build the top two (for the products thread)

1. **GoodNotes budget planner, $12-15 on Etsy and Gumroad.** Take the 2027 Budget Planner PDF
   (`planner_2027.py`). Add side tabs (months, bills, savings, debt) that link to their pages, with a
   "home" link on every page, at iPad landscape and portrait sizes. Title it for search: "Digital Budget
   Planner 2027, GoodNotes, Notability, iPad, Hyperlinked". Test the links in GoodNotes and Notability
   before listing.
2. **Wedding Budget Spreadsheet, $9-12.** A Google Sheet with categories (venue, catering, attire,
   photo…), budget vs actual, a payment-due calendar and a "who's paying" column. Sell it alone first.
   A baby or moving version can reuse it later. Avoid wedding-industry statistics without a source.

Prices are suggestions, sitting between our current ladder and the medians in
`template-pricing-jan-2027.md`. Launch both before the January peak (`bfcm-plan-2026.md`: budget searches
peak in January), with wedding planning also strong around New Year engagements. That last point is
common industry lore and isn't sourced here.

## Sources

Read 2026-11-07:
[EHunt: top 100 best-selling budget planners on Etsy](https://ehunt.ai/etsy-competitor-research/best-etsy-budget-planner) (updated 1 Nov 2026);
[EHunt: best-selling digital planners on Etsy](https://ehunt.ai/etsy-competitor-research/best-etsy-digital-planner) (updated 1 Nov 2026);
[Etsy search: best seller budget](https://www.etsy.com/market/best_seller_budget);
[InsightRaider: Notion template earnings on Gumroad](https://insightraider.com/en/answers/how-much-can-you-make-selling-notion-templates-on-gumroad) (23 Sep 2026);
[SendOwl: best-selling Notion template categories](https://www.sendowl.com/blog/tips-and-advice/best-selling-notion-template-categories) (6 Jul 2026; no dataset);
our side from `content-factory/PRODUCTS_CATALOG.md` (PR #6).
