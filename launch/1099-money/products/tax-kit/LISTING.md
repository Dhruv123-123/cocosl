# The Freelancer Tax Kit ([PRICE]): store listing kit

Gumroad (or Lemon Squeezy / Stan Store) listing for a tax-only bundle built from products that already exist.
The Etsy version is `../../etsy/freelancer-tax-kit.md`. Replace anything in `[brackets]`.

## Files to upload

| File | From |
|---|---|
| `Start-Here-Freelancer-Tax-Kit.pdf` | `the-freelancer-tax-kit.html` in this folder (3 pages; built by `etsy/build_etsy.py`) |
| `Quarterly-Tax-Tracker.xlsx` + `The-Quarterly-Tax-Tracker.pdf` | `../../product/` |
| `freelancer-tax-calendar-2027.pdf` | `apps/freelance-tax/downloads/` (free lead magnet) |
| `freelancer-tax-checklist.pdf` | `apps/freelance-tax/downloads/` (free lead magnet) |
| `tax-jar-tracker.pdf` | `apps/freelance-tax/downloads/` (free lead magnet) |

`python launch/1099-money/etsy/build_etsy.py` builds the zip (`Freelancer-Tax-Kit.zip`, folders `2-Quarterly-Tax-Tracker`,
`3-Tax-Calendar-2027`, `4-Tax-Checklist`, `5-Tax-Jar-Tracker`) plus the Start Here PDF and 5 listing images.
The same zip works on Gumroad.

## Pricing

- **Price: [PRICE].** Placeholder until Dhruv picks it. $19 to $24 fits between the $15 tracker and the $49 Freelancer Money Bundle.
- Be exact about value: the tracker ($15) plus three printables that are free to email subscribers, in one download.
  Never "a $60 value", never a crossed-out price that wasn't charged.
- **Upgrade code** for tracker buyers: `TAXKIT15` ($15 off, so they pay only the difference). Keep it out of public posts.
- **Launch:** optional `LAUNCH` code for the first 7 days, only if it's a real, dated window.

## Where it sits on the ladder

| Step | Product | Price |
|---|---|---|
| 1 | The Quarterly Tax Tracker | $15 |
| 1b | **The Freelancer Tax Kit** (tracker + calendar + checklist + jar tracker) | [PRICE] |
| 2 | The Rate & Contract Kit | $29 |
| 3 | The Freelancer Money Bundle (tracker + kit + email scripts + calendar) | $49 |

Who it's for: people who only want the tax side and like printables. Anyone who also needs rates, contracts and invoices
should be pointed at the $49 bundle instead.

## Title options

1. **The Freelancer Tax Kit: quarterly tax tracker + 2027 calendar, checklist and tax jar log** (recommended)
2. The 1099 Tax Kit for Freelancers
3. Freelancer Estimated Tax Kit (spreadsheet + printables)

## Short description (cards and link-in-bio)

Set aside the right amount, pay the IRS on time each quarter, and be ready at filing time. One spreadsheet, three printables.

## Full description

> Freelancers pay their own taxes, four times a year, with nothing withheld. The Freelancer Tax Kit puts the whole routine in one folder.
>
> **What's inside**
>
> - **The Quarterly Tax Tracker** (spreadsheet + 10-page guide): log income, expenses and miles; before each deadline it shows a suggested payment, the lesser of the two IRS penalty-avoidance methods, minus what you've paid. Excel, Google Sheets and Numbers.
> - **The 2027 Freelancer Tax Calendar** (printable PDF): every federal deadline for 2027, month by month.
> - **The Freelancer Tax Checklist** (printable PDF): what to do in your first weeks, every month, each quarter and at filing time.
> - **The Tax Jar Tracker** (printable PDF): a one-page log for setting aside a share of every client payment.
> - **A 3-page Start Here guide**: set it all up in about 30 minutes.
>
> The three printables are also free when you join the 1099 Money email list. This kit bundles them with the tracker so everything is in one place.
>
> Federal figures are for the 2026 tax year. Educational tools, not tax, legal or financial advice. 14-day refunds.

## After purchase

- Send tracker buyers' email 1 (setup) from `apps/freelance-tax/emails/buyers/`; the kit includes the tracker, so the same sequence fits.
- Skip the "upgrade to the tracker" emails for kit buyers; the bundle-upgrade email can offer the $49 bundle for the difference ([PRICE] off).

## Before it goes live (manual)

- [ ] Pick the price and replace every `[PRICE]` here and in the Etsy listing.
- [ ] Create `TAXKIT15` (Gumroad) / `TAXKITUP` (Etsy private coupon).
- [ ] Add the product URL to `apps/freelance-tax/config.js` only if you want it on the thank-you page.
