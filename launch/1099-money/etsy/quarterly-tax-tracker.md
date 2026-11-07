# Etsy listing: The Quarterly Tax Tracker ($15)

**Title** (under 15 words, no repeated words, per Etsy's title guidance)
Quarterly Estimated Tax Tracker Spreadsheet, 1099 Freelancer Planner for Excel and Google Sheets

**Price:** $15.00 · **Type:** Digital download · **Category:** Paper & Party Supplies > Paper > Calendars & Planners (or Templates)
**Who made it:** I did · **What is it:** A finished product · **When made:** 2020–2026
**Renewal:** Automatic · **Quantity:** 999

**Tags** (13, each ≤20 chars)
`quarterly tax` · `estimated taxes` · `freelancer tax` · `1099 tracker` · `self employed tax` · `tax spreadsheet` · `budget spreadsheet` · `google sheets` · `excel template` · `small business tax` · `tax planner` · `side hustle` · `income tracker`

**Files to upload** (from `files/`)
1. Quarterly-Tax-Tracker.xlsx

Spreadsheet only. Etsy's 22 Oct 2026 rule bans AI-generated functional guides, so the 10-page PDF guide is not in the
Etsy edition (it stays in the Gumroad edition and the Tax Kit). The spreadsheet's own Start Here tab explains the yellow cells.

**Images** (from `images/`, upload in this order; 2700×2025): 01-clean (no text, the first photo per Etsy's advice), 02-hero, 03-inside, 04-spreadsheet, 05-pages, 06-close-up, 07-how-it-works, 08-files-and-formats

## Description

This Quarterly Estimated Tax Tracker is a spreadsheet for Excel, Google Sheets and Numbers, for US freelancers and 1099 workers.

Know exactly what to pay the IRS before each quarterly deadline, worked out from your own numbers.

If you freelance, contract or run a side business, nobody withholds tax from your pay. The IRS expects a payment four times a year, and a missed one adds a penalty. This spreadsheet turns your income, expense and mileage logs into a Suggested payment for every deadline.

WHAT'S INSIDE
• Quarterly Tax Tracker spreadsheet (.xlsx: Excel, Google Sheets, Apple Numbers)
• Setup tab: filing status, last year's tax, state rate (about 5 minutes)
• Income, expense (with categories) and mileage logs
• Suggested payment for each 2026 deadline: Apr 15, Jun 15, Sep 15, Jan 15
• Safe harbor vs this year's estimated tax, side by side
• Set-aside check: is your tax savings account big enough?
• All 2026 federal tables built in: brackets, standard deduction, SE tax, QBI, mileage rate
• Start Here tab with the example rows explained (delete them when you begin)

HOW IT WORKS
1. Download the file from your Etsy Purchases page
2. Open the spreadsheet (Google Sheets: File > Import > Upload)
3. Fill in the yellow cells; everything else calculates
4. Before each deadline, pay the Suggested payment through IRS Direct Pay

GOOD TO KNOW
• Digital download. Nothing is shipped.
• Federal figures are for the 2026 tax year. State tax uses a flat rate you enter.
• Educational tool, not tax, legal or financial advice. Check big decisions with a tax professional.

AI tools helped build this spreadsheet and draft its text. The tax figures come from IRS publications, listed on the Tax Tables tab.

## Shop coupons (create in Shop Manager > Marketing > Sales and discounts)
- `LAUNCH20`: 20% off, first two weeks
- Thank-you coupon (Etsy "Thank you" automatic coupon): 15% off the next order (next year's edition)

## Fees (check etsy.com/legal/fees before listing; these change)
At the time of writing for US sellers: $0.20 listing fee per listing (and per renewal), 6.5% transaction fee, payment processing about 3% + $0.25. On $15 that is roughly $1.90 in fees, so about $13.10 kept. Offsite Ads can add 12–15% on a sale they bring in.

## Switching to the 2027 edition (do it by Dec 20, 2026)

From January, buyers are planning 2027 payments, so swap the files before the January rush. Etsy advises against
changing titles and first photos on selling listings during the peak, and this title has no year in it, so it stays.

1. Rebuild with the 2027 tax tables: `python launch/1099-money/product/build_tracker.py --year 2027`, then
   `python launch/1099-money/product/build_edition_2027.py`, then `python launch/1099-money/etsy/build_etsy.py --edition 2027`.
2. Replace the spreadsheet on this listing with the new one from `files/`. On Gumroad, also replace the tracker files in the
   tracker, the Tax Kit (`python launch/1099-money/products/build_gumroad.py --edition 2027`) and the Money Bundle.
3. Replace photos 02–08 (photo 01 has no year on it). The chips and "what's inside" now say 2027.
4. In this description: "Suggested payment for each 2027 deadline: Apr 15, Jun 15, Sep 15, Jan 18, 2028", "All 2027 federal
   tables built in", and "Federal figures are for the 2027 tax year."
5. Mileage rate: the 2027 edition uses the latest rate (76¢, from July 1, 2026) until the IRS announces 2027's in December. Update the
   Tax Tables cell, rebuild, and re-upload if it changes.
