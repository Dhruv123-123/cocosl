# Products: start here

Read this before listing anything. It covers what to put up first, every price and link still blank, and what each platform charges. Built by `launch/catalog/start_here.py` from `PRODUCTS_CATALOG.md` and the launch kit; nothing has been listed, uploaded or paid for.

## 1. Decide how much of wave 1 goes up (your call)

Gumroad costs nothing until something sells. Etsy charges **$0.20 per listing** up front. Under the spend-nothing rule, you decide whether wave 1 starts small. **Recommendation: start with these 5**, then add the rest of wave 1 as the first ones sell or the weeks come round.

| # | Product | Where | Why first | Cost to list | Kit # |
|---|---|---|---|---|---|
| 1 | The 20-Minute Budget | Gumroad | Money Made Simple's featured product: the welcome emails, the site and most posts point here. | Free to list | 3 |
| 2 | The Bill Cut Kit | Gumroad | The $5 first purchase; its receipt points to The 20-Minute Budget. | Free to list | 4 |
| 3 | 2027 Budget Planner | Etsy | Dated for 2027, so it sells from December to the January peak and not after. First in the Etsy sitting. | $0.20 | 45 |
| 4 | Digital Budget Planner (undated, hyperlinked) | Etsy | The tablet planner scouting found missing from our shop; undated, so it keeps selling. | $0.20 | 86 |
| 5 | The Family Scam-Proofing Kit | Gumroad | Scam Decoded's featured product (week 2): the site funnel and the scam checker sell it. | Free to list | 35 |

The top 5 cost **$0.40** on Etsy (two listings). All of wave 1 on Etsy is 51 listings, about **$10.20** in listing fees. A new Etsy shop may also ask for a one-time setup fee (it has been $15 in the US); check at sign-up before deciding.

## 2. Wave 1 upload steps

Wave 1 is Money Made Simple and Scam Decoded (scouting's two-brand plan, PR #2). 1099 Money is wave 2 (after the brand-3 check, about Jan 10 2027) and Dinero Simple wave 3 (after a paid Spanish review).

1. **Before anything (10 minutes):** set the prices (section 3) and fill the link blanks (section 4) that your first listings need, and decide the top 5 question above.
2. **Week 0 (Nov 9), Gumroad, Money Made Simple:** open `storefront/launch-kit/WAVE1_LISTINGS.md` and go down the "Week 0" table. Each row's "Kit #" is the entry in `SITTING_1_GUMROAD.md` with the images, the files and the copy to paste. Cross-sell targets come first, so every receipt link points at a live page.
3. **Set up the profile and emails** from `storefront/money-made-simple/STOREFRONT.md` and `storefront/emails/`.
4. **Week 2 (Nov 23), Gumroad, Scam Decoded:** the "Week 2" table, from its own Gumroad account.
5. **Week 4 (Dec 7), Etsy, Money Made Simple shop:** `etsy/SHOP_SETUP.md`, then the "Week 4" table in order (the 2027 planner first, singles, then bundles). Create the saved replies in `storefront/NEXT_STEP_ALL_PRODUCTS.md`.
6. **Tick each listing off** in `storefront/launch-kit/launch_kit.csv` (the `done` column).
7. **Dated items** in the "Wave 1, but not yet" table of `WAVE1_LISTINGS.md` go up on their own dates (the January Reset on Dec 30, the Valentine's pack by Feb 1, the moving products by Mar 1).

Before you list on Etsy, `ETSY_COMPLIANCE.md` (next to this file) shows the final check of every Etsy listing and its files.

## 3. Prices not set yet

| Brand | Product | Platform | Where it stands | Where the price lives |
|---|---|---|---|---|
| Scam Decoded | Scam-Proof Your Parents printable kit | Gumroad | [PRICE] (PR #9 suggests $9-$12) | `scam-decoded/parents-printable-kit/LISTING.md` and `launch/catalog/build_catalog.py` (OTHER_BRANCHES) |
| 1099 Money | The Freelancer Tax Kit | Gumroad | [PRICE] (PR #10 suggests $19-$24) | `1099-money/products/tax-kit/LISTING.md` and `launch/catalog/build_catalog.py` (OTHER_BRANCHES) |
| Dinero Simple | Registro de Cuentas y Pagos | Etsy | [PRICE] (PR #11 suggests $5-$7) | `dinero-simple/imprimibles-etsy/registro-de-cuentas/LISTING.md` and `launch/catalog/build_catalog.py` (OTHER_BRANCHES) |
| Dinero Simple | Retos de Ahorro | Etsy | [PRICE] (PR #11 suggests $5-$7) | `dinero-simple/imprimibles-etsy/reto-de-ahorro/LISTING.md` and `launch/catalog/build_catalog.py` (OTHER_BRANCHES) |
| Dinero Simple | Registro de Renta y Reparaciones | Etsy | [PRICE] (PR #11 suggests $5-$7) | `dinero-simple/imprimibles-etsy/renta-y-reparaciones/LISTING.md` and `launch/catalog/build_catalog.py` (OTHER_BRANCHES) |

Set each price in its listing first, then in `build_catalog.py`, and rebuild the catalog and the launch kit.

## 4. Link blanks

Every placeholder still in the launch files, grouped by kind. Fill a group when the thing it points to is live; the builds keep the placeholders visible so nothing ships with a broken link.

| Blank | How to fill it | Count | Where (top files) |
|---|---|---|---|
| Gumroad store link in the Money Made Simple guides and Start Here pages | Put the store URL in `launch/products/catalog.json`, then `python launch/products/build.py` | 10 | `launch/etsy/build_etsy.py` (2); `launch/catalog/build_catalog.py` (1); `launch/products/README.md` (1); and 6 more |
| A Google Sheets "make a copy" link for each sheet template | Share each sheet as a /copy link and paste it into `launch/templates/links.json`, then `python launch/templates/build_templates.py` | 12 | `launch/templates/links.json` (12) |
| A published Notion duplicate link for each Notion template | Run `notion_build.py` once per template, paste the link into `launch/templates/links.json`, rebuild | 11 | `launch/templates/links.json` (11) |
| The template link line in a Start Here PDF (fills from links.json) | Same as the Sheets links above | 1 | `launch/templates/previews.py` (1) |
| Product links in brand Gumroad copy (The Money Reset, the Schedule C pack) | Replace in the Gumroad page text when you paste it, once the linked product is live | 4 | `launch/brandshop/schedule_c_pack.py` (2); `launch/brandshop/money_reset.py` (1); `launch/storefront/launch_kit.py` (1) |
| Product links in the Spanish storefront (Dinero Simple, wave 3) | Only after the native review | 3 | `launch/storefront/gumroad_es.py` (2); `launch/storefront/README.md` (1) |
| Merge fields in the post-purchase emails ({{download_url}}, {{planner_url}} and so on) | Set them in Gumroad Workflows or the email tool when you set up each sequence | 15 | `launch/storefront/post_purchase.py` (13); `launch/storefront/README.md` (1); `launch/ebook/build_ebook.py` (1) |
| Store and newsletter URLs in the site config | Fill in when the store and the newsletter exist | 2 | `launch/templates/links.json` (2) |

`launch/templates/links.json` has **25 links to fill**: `newsletter`, `notion_52_week`, `notion_bills`, `notion_budget`, `notion_debt`, `notion_debt_coloring`, `notion_hq`, `notion_hq_2027`, `notion_no_spend`, `notion_paycheck`, `notion_savings`, `notion_starter`, `sheet_52_week`, `sheet_bills`, `sheet_budget`, `sheet_budget_2027`, `sheet_debt`, `sheet_debt_coloring`, `sheet_moving`, `sheet_no_spend`, `sheet_paycheck`, `sheet_savings`, `sheet_sinking`, `sheet_wedding`, `store`.
The free apps (PR #8) hold upsell slots with `REPLACE_ME` Gumroad URLs in `apps/budget/config.js` (for example `sinking-funds-sheet`); use the same slugs when you create the Gumroad products, or tell the apps thread the real ones.

## 5. What each platform charges

| | Etsy | Gumroad |
|---|---|---|
| To list | $0.20 per listing, renewed every 4 months or after each sale | Free |
| Per sale | 6.5% transaction fee, plus payment processing (US: 3% + $0.25) | 10% + $0.50 on direct sales, plus card processing; 30% on sales through Gumroad Discover |
| Setup | A one-time fee for new shops in some countries ($15 in the US so far) | None |
| Example: a $12 item | about $0.78 + $0.61 + $0.20 listing = **$1.59**, you keep about $10.41 | about $1.70 + processing, you keep about $10 |

These are the published fees as of Nov 2026 (Etsy's fee schedule and Gumroad's pricing page, plus [Checkout Page on Etsy fees](https://checkoutpage.com/blog/etsy-fees) and [on Gumroad fees](https://checkoutpage.com/blog/gumroad-fees)). Check both pages on the day you sign up; they change. `launch/etsy/listings.py` `fees()` has the Etsy maths for every listing.

