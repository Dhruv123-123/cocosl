# Etsy SEO and listing playbook, with an audit of our listings

Written 2026-11-07 from Etsy's own Seller Handbook, Help Center and policy pages, plus public keyword data
and seller research. **Docs only.** Nothing was listed or changed. The product thread (PR #6) owns the
listings. This builds on its `launch/etsy/SEO_NOTES.md`, which already covers keywords and the seasonal
calendar.

**What was audited:** the 74 rendered Etsy listing files in project files (`content-factory/etsy/`,
`brands/`, `pod/`). That's every Etsy listing in `PRODUCTS_CATALOG.csv` (78 Etsy rows) except 4, which have
no rendered listing yet: the Scam Decoded seniors pack and three combined Etsy-and-Gumroad rows. Script:
[`etsy_audit.py`](etsy_audit.py).

## TL;DR

The basics are already right. Every listing has 13 tags of 20 characters or less, a category,
attributes, an honest "digital download" description and an AI-use line, and 66 of 74 titles are under 15
words. The gaps are in **photos, description openings and a few titles**:

1. **Photos (all 74 listings).** Each listing has 3 images, or 1 for the posters, and Etsy allows 20.
   Etsy also recommends at least 2,000 px on both sides, but ours are 2000×1500. The first photo is a text
   panel next to the pages. Etsy's advice is to **avoid text overlays and collages in the first photo**,
   keep the item centred so it survives square crops, and use a landscape or square first photo. All 10
   posters have a single portrait 900×1200 image.
2. **Description openings (64 of 74).** The first line is a friendly hook that doesn't name the item ("A
   simple monthly budget you'll actually keep"). Etsy: "incorporate relevant keywords in the first few
   sentences." A one-line change in `listings.py`'s `_desc()` fixes the 50 Money Made Simple listings at once.
3. **Long titles (8).** The 5 Dinero Simple products have titles of 20-22 words, and the 3 1099 Money Etsy
   listings have 17-18. Etsy suggests fewer than 15. Draft rewrites are below (the Spanish ones still need
   the native review).
4. **Repeated words in titles (44)** and **single-word tags (13)**. Etsy says "try not to repeat words" and
   to use tags that are "multi-word phrases". These are small fixes, best batched.
5. **January timing.** Everything should be live by **1 December**. Don't edit titles on listings that are
   selling in January. **The Quarterly Tax Tracker still says "2026 Tax Year"**, so a 2027 edition is
   needed by about 20 December for January buyers.

## 1. The playbook (Etsy's own guidance first)

### How Etsy search ranks a listing

Etsy's [How Etsy Search Works](https://www.etsy.com/seller-handbook/article/375461474487) (26 Aug 2025)
first matches listings to the search, then orders them by how likely a shopper is to buy. Etsy says it
takes "a holistic view of your listing":

- **Matching:** title, tags, attributes, categories, description, first photo and reviews. "If those
  keywords are an exact match for the query, your listing may be ranked higher."
- **Ordering:**
  - Listing quality: multiple high-quality photos.
  - Customer service: average review rating, message response rate and case rate over the last 3 months.
  - Engagement: how well views turn into purchases.
  - Language: the listing should match the shop's language.
  - Recency: new or renewed listings get a boost lasting "hours to a few days". Renewing only for the
    boost "isn't an effective strategy".
  - Personalisation for each shopper.
- **Not factors:** Etsy Plus, Star Seller (a trust signal only) and Etsy Ads.

### Titles

From [New Guidance for Listing Titles](https://www.etsy.com/seller-handbook/article/1399426136697) (27 Apr 2026):

- **Fewer than 15 words.** Name the item first, then its key traits (for printables: format, size, what's
  inside).
- **Don't repeat words.** Leave out subjective words ("perfect", "cute") and gift or occasion words unless
  they're essential to the item. Leave out price, shipping and sale details.
- **The title doesn't have to carry every keyword.** Tags, attributes and the description count too.
- **Etsy's AI title tool** (in the search visibility dashboard) suggests titles from your title, first
  photo and description. It's "a starting point—not a directive". Download a CSV of your listings before
  bulk changes.

**Our rule:** `[Item] [format], [the 1-2 traits a shopper filters by]`, under 15 words, with each word
used once. Example: "Monthly Budget Planner Printable, Undated Binder Pages with Bill and Savings Tracker".

### Tags and attributes

From [The Anatomy of a Well-Crafted Etsy Listing](https://www.etsy.com/seller-handbook/article/1347574487014)
(26 Aug 2025):

- **Use all 13 tags.** Make them "multi-word phrases" in "natural-sounding language", covering what the item
  is, who it's for and the synonyms people type. Etsy's tag field allows 20 characters.
- **Attributes "act like tags".** Fill every attribute Etsy shows for the category, and pick the closest
  option even if it isn't your wording. A phrase that's already an attribute (e.g. "Google Sheets" as
  Software) doesn't need a tag too, so use that tag for something else.

### Description

Put the item name and its main keywords in the **first sentence or two**, then sizes, formats and what's
included near the top. Etsy's handbook: "Aim to incorporate relevant keywords in the first few sentences."
Ours already do the rest well: what you get, how it works, a "digital download, nothing is shipped" line,
personal-use terms and an AI-use line.

### Photos and video

From Etsy's [image requirements](https://help.etsy.com/hc/en-us/articles/115015663347-Requirements-and-Best-Practices-for-Images-in-Your-Etsy-Shop),
its [listing image policy](https://www.etsy.com/legal/policy/listing-image-requirements/253962679005)
(updated 22 Oct 2026) and the Anatomy article:

| Rule | Etsy's words | What it means for us |
|---|---|---|
| Size | "at least 2000 pixels" wide and high; first photo at least 635 px | Render at **2700×2025** (4:3) or larger, not 2000×1500 |
| Shape | First photo "horizontal (landscape) or square"; the rest match it | Posters need a landscape or square first photo, not a portrait one |
| Cropping | Leave "enough of a border" for square, portrait and landscape thumbnails; important part "in the center" | Pages centred, with no headline on the left half that a square crop cuts off |
| First photo | It "can help get you the click from search results". **Avoid text overlays, collages or a collection of images** as the first thumbnail to optimise for search | First photo: the pages themselves, clean. Move the "Instant download / Letter + A4" panel to photo 2 |
| Count | Up to 20 photos | Aim for 7-10 (list below) |
| Digital downloads | "should include a visual preview or excerpt of the content buyers will receive" | Already done. Keep real page renders, not invented scenes |
| Print on demand | Mockups allowed (the production partner prints your design on a standard product) | Use the print partner's room or frame mockups for the posters |
| Video | Etsy supports one short listing video (5-15 seconds, no sound) | A page flip-through for each bestseller |

**Photo set for a printable (7-10 images):**
1. A clean first photo: the pages fanned and centred, with no headline.
2. The current hero: title, "Instant download · Letter + A4 · Undated".
3. 2-3 page close-ups people can read.
4. "What's inside": a page list or thumbnail grid. For bundles, every item.
5. How it works in 3 steps (print, fill in, check in weekly).
6. Sizes and formats (Letter and A4, PDF and XLSX, works on a tablet).
7. For spreadsheets: a screenshot in Google Sheets and in Excel.
8. A filled-in example with fictional numbers, labelled as an example.

**A test, not a rule:** many top printable sellers do put text on the first photo, and Etsy's advice
is about search, not conversion. Test it: switch half the listings in one group (the 12 savings challenges)
to the clean first photo by about 20 November, keep the other half as they are, and compare visits and
orders after 3 weeks. Then apply the winner everywhere before mid-December.

### Seasonal timing (January is the peak)

From `SEO_NOTES.md` (rankhero keyword data) and `bfcm-plan-2026.md`:

- Etsy "budget planner" searches peak in **January (about 74K vs about 60K)**. "Savings challenge" is about 3× in
  January, and "debt snowball" peaks in January and March.
- **Be live and settled by 1 December.** Ranking changes take a couple of weeks to settle, and the recency
  boost lasts only hours to days, so a listing posted on 2 January won't be ready for January.
- **Freeze titles and first photos from about 20 December to 31 January** on listings that are selling.
  Make changes in early December or February.
- **Answer messages fast in January.** Response rate is a ranking factor, and January reviews carry the whole
  year.
- **Dated products:** list the 2028 planner by mid-August 2027 (already in `SEO_NOTES.md`). **New: the 1099
  Money Quarterly Tax Tracker needs its 2027 tax-year edition by about 20 December.** From January, buyers
  are planning 2027 payments, and the current title and photos say "2026 tax year".

## 2. Audit results

### Fix codes

| Code | Issue | Count | Fix | Effort |
|---|---|---:|---|---|
| **P2** | Photos below 2,000 px on one side (2000×1500; 2400×1800 for 1099 Money; 900×1200 portrait for posters) | 74 | Render at 2700×2025 in `mockgen.py` / `mockups.py`; posters get a landscape or square mockup | One code change, re-render |
| **P1** | Fewer than 5 photos (3 on most listings, 1 on posters) | 71 | Add photos 1 and 4-8 from the set above. Generated from the PDFs, so it's code, not hand work | `mockgen.py`, half a day |
| **D1** | Description's first line doesn't name the item | 64 | In `listings.py` `_desc()`, start with the item: "**This [name] is a printable [format].** [hook]". Same for the brand-shop scripts | One line per generator |
| **T2** | A word repeated in the title | 44 | Rewrite with each word once (examples below). Keep the lead phrase | 20 minutes for the batch |
| **G1** | Single-word tags (e.g. "bookkeeping", "presupuesto", "remesas") | 13 | Make them phrases: "bookkeeping log", "presupuesto mensual", "envio de dinero" | 10 minutes |
| **T1** | Title of 15+ words | 8 | Rewrites below | 10 minutes |
| **G2** | A tag that repeats an attribute ("google sheets" when Software is set) | 5 | Swap for a new phrase ("budget spreadsheet", "debt calculator") | 5 minutes |
| **Gift Budget Planner** | Uses "gift" in the title | 1 | **No change.** "Gift" is the item itself, which Etsy allows | — |

### Title rewrites for the 8 long titles

| Listing | Now (words) | Suggested (words) |
|---|---|---|
| 1099 Money: Quarterly Tax Tracker | 18 | Quarterly Estimated Tax Tracker Spreadsheet, 1099 Freelancer Planner for Excel and Google Sheets (13). Put the tax year in an attribute and the photos, and switch it to 2027 in December |
| 1099 Money: Freelancer Money Bundle | 17 | Freelancer Business Bundle: Quarterly Tax Tracker, Rate Calculator and Contract Templates (11) |
| 1099 Money: Rate & Contract Kit | 17 | Freelance Rate Calculator and Contract Kit, Proposal and Invoice Templates (11) |
| Dinero Simple: Fecha Sin Deudas | 22 | Planificador para Pagar Deudas en Español, Método Bola de Nieve, Excel y Google Sheets (14) |
| Dinero Simple: Invertir con $100 | 21 | Guía de Inversión para Principiantes en Español, Calculadoras en Excel y Google Sheets (13) |
| Dinero Simple: Paquete | 21 | Paquete de Finanzas Personales en Español: Presupuesto, Deudas, Ahorro e Inversión (11) |
| Dinero Simple: Presupuesto de 20 Minutos | 21 | Plantilla de Presupuesto Semanal en Español, Excel y Google Sheets, Guía de 14 Páginas (14) |
| Dinero Simple: Recortar Gastos | 20 | Kit para Recortar Gastos en Español, Lista de Suscripciones y Guiones para Bajar Cuentas (14) |

**The Spanish rewrites are drafts for the native reviewer.** Every Dinero Simple listing is already gated
on "REVISIÓN NATIVA PENDIENTE".

**Examples of repeated-word fixes (T2):**
- "Paycheck Budget Planner Printable, Biweekly Budget by Paycheck, Bill Planner" → "Paycheck Budget Planner
  Printable, Biweekly Pay Period Sheets with Bill Tracker".
- "Monthly Budget Planner Printable, Undated Budget Binder Pages, Bill and Savings Tracker" → "Monthly Budget
  Planner Printable, Undated Binder Pages with Bill and Savings Tracker".
- "Bill Tracker Printable, Monthly Bill Payment Checklist and Yearly Bill Organizer" → "Bill Tracker
  Printable, Monthly Payment Checklist and Yearly Due Date Organizer".

### One more check: language

Etsy ranks listings that match the shop's language. The Dinero Simple listings mix Spanish titles with
English phrases ("Spanish Budget Planner", "Remittance Tracker"). That reaches bilingual shoppers on the
English Etsy, which is where most US buyers browse. Whichever shop they go in, **add the other language
as a listing translation in Etsy** rather than mixing more English into the Spanish titles. The open
question for Dhruv is whether Dinero Simple gets its own shop or a section in the Money Made Simple shop.

### Every listing

Codes as above. **Bold** means fix first. "Words" is the title's word count.

| Listing | Words | Fixes |
|---|---:|---|
| `brands/1099-money/freelancer-tax-planner-2027` | 12 | T2 (tax), G1 (bookkeeping), P1 (3), P2, D1 |
| `brands/dinero-simple/construir-credito` | 12 | G1 (credito, itin), P1 (3), P2, D1 |
| `brands/dinero-simple/paquete-familia` | 13 | G1 (presupuesto, remesas, credito, ahorro, planificador), P1 (3), P2, D1 |
| `brands/dinero-simple/presupuesto-familiar` | 12 | G1 (presupuesto, ahorro, planificador), P1 (3), P2, D1 |
| `brands/dinero-simple/registro-de-envios` | 13 | G1 (remesas, familia), P1 (3), P2, D1 |
| `brands/scam-decoded/scam-card-set` | 14 | T2 (cards), P1 (3), P2, D1 |
| `etsy/100-envelope-challenge` | 11 | T2 (envelope), P1 (3), P2, D1 |
| `etsy/1099-money/freelancer-money-bundle` | 17 | **T1** title 17 words, P2, D1 |
| `etsy/1099-money/quarterly-tax-tracker` | 18 | **T1** title 18 words, T2 (tax), P2, D1 |
| `etsy/1099-money/rate-and-contract-kit` | 17 | **T1** title 17 words, P2, D1 |
| `etsy/20-minute-budget` | 13 | T2 (budget), P1 (3), P2, D1 |
| `etsy/2027-budget-planner` | 11 | T2 (budget, planner), P1 (3), P2, D1 |
| `etsy/30-day-savings-challenge` | 13 | P1 (3), P2 |
| `etsy/50-30-20-budget-worksheet` | 11 | T2 (budget), P1 (3), P2, D1 |
| `etsy/52-week-savings-challenge` | 11 | T2 (challenge), P1 (3), P2, D1 |
| `etsy/bill-cut-kit` | 11 | T2 (bill), G2 (google sheets), P1 (3), P2, D1 |
| `etsy/bill-payment-tracker` | 11 | T2 (bill), P1 (3), P2, D1 |
| `etsy/budget-binder-bundle` | 13 | T2 (budget), P1 (3), P2 |
| `etsy/car-expense-tracker` | 10 | T2 (log), P1 (3), P2, D1 |
| `etsy/cash-envelope-trackers` | 8 | T2 (cash), P1 (3), P2, D1 |
| `etsy/checking-account-register` | 9 | T2 (register), P1 (3), P2, D1 |
| `etsy/credit-card-payoff-tracker` | 11 | P1 (3), P2, D1 |
| `etsy/credit-report-audit-kit` | 12 | T2 (credit), G2 (google sheets), P1 (3), P2 |
| `etsy/daily-spending-log` | 9 | T2 (spending), P1 (3), P2, D1 |
| `etsy/debt-free-date-planner` | 11 | T2 (debt), G2 (google sheets), P1 (3), P2, D1 |
| `etsy/debt-mountain-coloring-chart` | 8 | T2 (debt), P1 (3), P2, D1 |
| `etsy/debt-payoff-coloring-tracker` | 11 | T2 (debt), P1 (3), P2, D1 |
| `etsy/debt-snowball-worksheet` | 8 | T2 (debt), P1 (3), P2, D1 |
| `etsy/dinero-simple/fecha-sin-deudas` | 22 | **T1** title 22 words, T2 (deudas), G1 (avalancha), P1 (3), P2, D1 |
| `etsy/dinero-simple/invertir-con-100` | 21 | **T1** title 21 words, G1 (invertir, 401k, principiantes, calculadora, retirement), P1 (3), P2, D1 |
| `etsy/dinero-simple/paquete` | 21 | **T1** title 21 words, G1 (presupuesto, invertir, ahorro, regalo), P1 (3), P2, D1 |
| `etsy/dinero-simple/presupuesto-20-minutos` | 21 | **T1** title 21 words, T2 (presupuesto), G1 (presupuesto, ahorro, planificador), P1 (3), P2 |
| `etsy/dinero-simple/recorte-de-gastos` | 20 | **T1** title 20 words, G1 (suscripciones, presupuesto), P1 (3), P2, D1 |
| `etsy/emergency-fund-tracker` | 10 | P1 (3), P2 |
| `etsy/financial-goals-planner` | 10 | T2 (goals), P1 (3), P2, D1 |
| `etsy/gift-budget-planner` | 9 | T2 (gift), P1 (3), P2, D1 |
| `etsy/grocery-budget-tracker` | 9 | P1 (3), P2, D1 |
| `etsy/holiday-savings-planner` | 9 | P1 (3), P2, D1 |
| `etsy/home-fund-tracker` | 10 | P1 (3), P2, D1 |
| `etsy/investing-starter-kit` | 12 | T2 (investing), G1 (401k), G2 (google sheets), P1 (3), P2, D1 |
| `etsy/irregular-income-budget` | 10 | T2 (budget), P1 (3), P2, D1 |
| `etsy/loan-payoff-tracker` | 11 | T2 (loan), P1 (3), P2, D1 |
| `etsy/mega-budget-bundle` | 12 | T2 (budget), P1 (3), P2, D1 |
| `etsy/money-toolkit-bundle` | 12 | G2 (google sheets), P1 (3), P2, D1 |
| `etsy/monthly-budget-planner` | 12 | T2 (budget), P1 (3), P2 |
| `etsy/monthly-expense-tracker` | 9 | P1 (3), P2, D1 |
| `etsy/monthly-money-review` | 10 | P1 (3), P2, D1 |
| `etsy/net-worth-tracker` | 10 | P1 (3), P2, D1 |
| `etsy/no-spend-challenge` | 12 | T2 (no, spend), P1 (3), P2, D1 |
| `etsy/paycheck-budget-planner` | 10 | T2 (budget, paycheck, planner), P1 (3), P2, D1 |
| `etsy/paycheck-savings-challenge` | 8 | T2 (savings), P1 (3), P2, D1 |
| `etsy/roll-and-save-challenge` | 10 | P1 (3), P2, D1 |
| `etsy/savings-account-register` | 8 | P1 (3), P2 |
| `etsy/savings-bingo` | 10 | T2 (bingo), P1 (3), P2, D1 |
| `etsy/savings-challenge-pack` | 12 | P1 (3), P2 |
| `etsy/savings-challenge-tracker` | 10 | T2 (challenge, savings), P1 (3), P2, D1 |
| `etsy/side-hustle-income-tracker` | 11 | T2 (income), G1 (bookkeeping), P1 (3), P2 |
| `etsy/sinking-funds-tracker` | 11 | P1 (3), P2, D1 |
| `etsy/spare-change-jar-tracker` | 12 | T2 (jar), P1 (3), P2, D1 |
| `etsy/subscription-tracker` | 9 | G1 (subscriptions), P1 (3), P2, D1 |
| `etsy/travel-fund-tracker` | 11 | P1 (3), P2, D1 |
| `etsy/utility-bill-tracker` | 11 | T2 (bill), P1 (3), P2, D1 |
| `etsy/weekly-budget-planner` | 8 | T2 (weekly), P1 (3), P2, D1 |
| `etsy/zero-based-budget-worksheet` | 11 | P1 (3), P2, D1 |
| `pod/100-envelope-challenge-poster` | 12 | T2 (challenge), **P1** (1), P2 **portrait** |
| `pod/52-week-savings-poster` | 10 | T2 (challenge), **P1** (1), P2 **portrait**, D1 |
| `pod/debt-mountain-poster` | 11 | T2 (debt), **P1** (1), P2 **portrait**, D1 |
| `pod/emergency-fund-poster` | 11 | **P1** (1), P2 **portrait**, D1 |
| `pod/house-fund-poster` | 12 | T2 (house), **P1** (1), P2 **portrait**, D1 |
| `pod/no-spend-challenge-poster` | 12 | T2 (no, spend), **P1** (1), P2 **portrait**, D1 |
| `pod/save-1000-poster` | 12 | **P1** (1), P2 **portrait**, D1 |
| `pod/savings-bingo-poster` | 11 | T2 (bingo), **P1** (1), P2 **portrait**, D1 |
| `pod/savings-jar-poster` | 12 | **P1** (1), P2 **portrait**, D1 |
| `pod/travel-fund-poster` | 11 | **P1** (1), P2 **portrait**, D1 |
## 3. Order of work for the product thread

1. **By 16 Nov:** fix D1 in the generators, the 8 long titles (T1), G1 and G2, then re-render the
   listing files. It's text only, so it's fast.
2. **By 20 Nov:** fix mockup size (P2) and add the extra photos (P1), with the clean first photo on half
   the savings challenges as the test. Give the posters landscape or square mockups.
3. **By 1 Dec:** everything live. Then T2 title tidy-ups on listings that haven't sold yet.
4. **By 20 Dec:** the 2027 tax-year edition of the Quarterly Tax Tracker.
5. **20 Dec-31 Jan:** freeze titles and first photos on listings that are selling. Answer messages the same
   day.
6. **February:** read Etsy Stats (search terms and visits per listing), swap tags that brought no visits,
   and apply the first-photo test's winner.

## Sources

- Etsy Seller Handbook: [How Etsy Search Works](https://www.etsy.com/seller-handbook/article/375461474487) (26 Aug 2025);
  [New Guidance for Listing Titles](https://www.etsy.com/seller-handbook/article/1399426136697) (27 Apr 2026);
  [The Anatomy of a Well-Crafted Etsy Listing](https://www.etsy.com/seller-handbook/article/1347574487014) (26 Aug 2025).
- Etsy Help: [Requirements and Best Practices for Images](https://help.etsy.com/hc/en-us/articles/115015663347-Requirements-and-Best-Practices-for-Images-in-Your-Etsy-Shop);
  Etsy policy: [Listing Image Requirements](https://www.etsy.com/legal/policy/listing-image-requirements/253962679005) (updated 22 Oct 2026).
- Seller research: [Marmalead, Dec 2025](https://blog.marmalead.com/etsy-algorithm-2026/). Its claims (lead with the product
  phrase in the first 3-5 words, since the app shows only the first few; show digital-download details in the photos) are
  its own opinion, not Etsy's.
- Keyword and season data: `launch/etsy/SEO_NOTES.md` (rankhero.com keyword pages, Nov 2026), `bfcm-plan-2026.md`.
