# Brand shops: Scam Decoded and 1099 Money

Printables, a spreadsheet, mockups and listing copy for two more brands. **Nothing has been listed or uploaded.**

```
python launch/brandshop/build_brandshop.py --check     # both brands; --brand scam-decoded or 1099-money for one
```

Output lands in `launch/brandshop/dist/<brand>/<listing>/` (git-ignored): the PDFs or workbook, a bundle zip,
mockups (01 is the thumbnail), `LISTING.md` with every Etsy and Gumroad field, and `listings.csv` per brand. The build
fails on page overflow, Etsy title/tag limits, banned wording, off-Etsy links, or a formula error in the workbook.

| Brand | Listing | Price | Files |
|---|---|---|---|
| Scam Decoded | Family Scam-Safety Kit | $9 | 11 pages, Letter + A4 |
| Scam Decoded | Scam Fridge Card Set | $5 | 6 cards: 4x6 and two-per-sheet Letter + A4 |
| Scam Decoded | Caller ID Script Card for Seniors | $4 | Large-print page, 4x6 card, 8 wallet cards per sheet |
| Scam Decoded | Family Scam-Safety Bundle | $12 | All of the above (zip) |
| 1099 Money | 2027 Freelancer Tax-Year Planner | $12 | 25 pages, Letter + A4 |
| 1099 Money | 2027 Freelancer Tax Tracker (Sheets) | $14 | .xlsx (opens in Google Sheets, Excel, Numbers) + start-here PDF |
| 1099 Money | 2027 Freelancer Tax Bundle | $19 | Planner + tracker (zip) |

## Before listing

- **One Etsy shop per account.** Each brand needs its own Etsy account and shop (or list them in an existing shop
  under sections). Gumroad can hold several products under one profile.
- **Check the facts on the day you list.** Scam contacts (ReportFraud.ftc.gov, ic3.gov, IdentityTheft.gov, DOJ Elder
  Fraud Hotline 1-833-372-8311, AARP 877-908-3360) were current in November 2026. The 2027 tax dates follow the IRS
  weekend and federal-holiday rule (Q4 lands on Tue Jan 18 2028 because of MLK Day); confirm on irs.gov, and confirm the
  1099-NEC threshold and the 2027 mileage rate once the IRS publishes it (the tracker leaves the rate blank on Setup).
- Every page and listing says it is educational, not financial, tax or legal advice, and discloses the AI help.
