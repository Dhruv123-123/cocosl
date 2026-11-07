# Brand shops: Scam Decoded, 1099 Money and Dinero Simple

Printables, a spreadsheet, mockups and listing copy for two more brands. **Nothing has been listed or uploaded.**

```
python launch/brandshop/build_brandshop.py --check     # both brands; --brand scam-decoded or 1099-money for one
```

Output lands in `launch/brandshop/dist/<brand>/<listing>/` (git-ignored): the PDFs or workbook, a bundle zip,
mockups (01 is the thumbnail), `LISTING.md` with every Etsy and Gumroad field, and `listings.csv` per brand. The build
fails on page overflow, Etsy title/tag limits, banned wording, off-Etsy links, or a formula error in the workbook.

| Brand | Listing | Price | Files |
|---|---|---|---|
| Scam Decoded | Scam Decoded Card Set | $6 | 6 fridge cards + caller ID script card (4x6), large-print phone page, 8 wallet cards; Letter + A4 |
| 1099 Money | 2027 Freelancer Tax-Year Planner | $12 | 25 pages, Letter + A4 |
| Dinero Simple | El Presupuesto Familiar | $9 | 12 pages, Carta + A4 |
| Dinero Simple | El Registro de Envíos | $7 | 7 pages, Carta + A4, plus a remittance workbook (.xlsx) |
| Dinero Simple | La Lista para Construir tu Crédito | $6 | 8 pages, Carta + A4 |
| Dinero Simple | El Paquete de la Familia | $16 | All three (zip) |

**Merged to avoid near-duplicates (Nov 7 2026, reversible).** The 11-page Family Scam-Safety Kit, the fridge cards,
the caller ID card and their $12 bundle overlapped Scam Decoded's Family Scam-Proofing Kit and large-print seniors
pack (PR #9), so the cards became one cards-only Card Set and the rest is not listed. The 2027 tax sheet and its bundle
overlapped 1099 Money's Quarterly Tax Tracker (PR #10), so the planner is sold as its paper companion. Each module's
`RETIRED` dict says why; remove a slug from it and rebuild to list it again. The pages still render and are checked.

**Dinero Simple is Spanish and needs a fluent speaker's review before anything is listed.** Every `LISTING.md` opens
with a NATIVE REVIEW PENDING banner, `listings.csv` has a `review` column, and the build writes
`dist/dinero-simple/REVIEW_CHECKLIST_ES.md` for the reviewer to sign.

Every product across every brand (with platform, paths and launch date) is in `launch/PRODUCTS_CATALOG.md`, built by
`launch/catalog/build_catalog.py`. It flags where these products overlap with the Scam Decoded and 1099 Money products
on PRs #9 and #10.

## Before listing

- **One Etsy shop per account.** Each brand needs its own Etsy account and shop (or list them in an existing shop
  under sections). Gumroad can hold several products under one profile.
- **Check the facts on the day you list.** Scam contacts (ReportFraud.ftc.gov, ic3.gov, IdentityTheft.gov, DOJ Elder
  Fraud Hotline 1-833-372-8311, AARP 877-908-3360) were current in November 2026. The 2027 tax dates follow the IRS
  weekend and federal-holiday rule (Q4 lands on Tue Jan 18 2028 because of MLK Day); confirm on irs.gov, and confirm the
  1099-NEC threshold and the 2027 mileage rate once the IRS publishes it (the tracker leaves the rate blank on Setup).
- Every page and listing says it is educational, not financial, tax or legal advice, and discloses the AI help.
- **Schedule C Setup Pack for TaxHacker (1099 Money, $12, `schedule_c_pack.py`, built as `1099-money-taxhacker`).** A
  guide, 26 categories with AI prompts mapped to Schedule C lines, three custom fields, a CSV/JSON category map and a
  year-end packet workbook that reads TaxHacker's CSV export by header name (totals by line, quarterly set-asides,
  receipts over $75 with no note, a mileage log). Written against the TaxHacker 0.8.5 source; **it has not been tried in
  a live install**, so the listing carries a BLOCKER: install 0.8.5 with made-up receipts, run 30 through it, confirm the
  menu names, then list. TaxHacker is MIT (Copyright (c) 2025 Vasily Zubarev): the pack names and links it, says it
  isn't affiliated, uses no logo and contains none of its code. Restoring a TaxHacker backup deletes existing data, so
  the pack never asks anyone to restore one.
