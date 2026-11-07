# The Freelancer Tax Season Bundle ([PRICE]): store listing kit

Gumroad (or Lemon Squeezy / Stan Store) listing for January to April 15. Not sold on Etsy: it includes guides, and
Etsy's 22 Oct 2026 rule bans AI-generated functional guides. Replace anything in `[brackets]`.

## Files to upload

`python launch/1099-money/products/build_gumroad.py` writes `freelancer-tax-season-bundle/`:

| File | What it is |
|---|---|
| `1-Start-Here-and-S-Corp-Check.pdf` | 3 pages: a five-step tax-season plan, the S corp worked table, a fill-in worksheet (`the-tax-season-bundle.html`) |
| `Freelancer-Tax-Season-Bundle.zip` | folders `2-Quarterly-Tax-Tracker` (spreadsheet + guide), `3-Tax-Checklist` |

Add `--edition 2027` to ship the 2027 tracker (for buyers after Apr 15).

## Pricing

- **Price: [PRICE].** Coordinator suggested $19; Dhruv picks.
- Be exact about value: the $15 tracker, the checklist (free to email subscribers) and an S corp worksheet. The
  S corp calculator itself is free on the site; the bundle includes a printed worked table and worksheet, not a
  separate app. Never "a $50 value", never a crossed-out price that wasn't charged.
- **Overlap:** the Freelancer Tax Kit has the tracker and checklist too. Don't pitch this bundle to Tax Kit buyers;
  for tracker buyers, an upgrade code for the difference (`[CODE]`, $15 off) is fair.
- Sell it Jan 1 – Apr 15, 2027; after that, point people to the Tax Kit or the tracker.

## Title options

1. **Freelancer Tax Season Bundle: quarterly tax tracker, filing checklist and S corp check** (recommended)
2. The 1099 Tax Season Bundle (2026 return + 2027 quarters)
3. Freelancer Tax Season Kit: tracker, checklist, S corp worksheet

## Short description

Pay the Jan 15 estimate, file by April 15, and check whether an S corp makes sense for 2027. One spreadsheet, two printables.

## Full description

> Tax season for freelancers is three jobs: the last 2026 estimated payment on Jan 15, the return by Apr 15, and the
> question you keep putting off, whether an S corp would save you money. This bundle covers all three.
>
> **What's inside**
>
> - **The Quarterly Tax Tracker** (spreadsheet + 10-page guide): your 2026 income, expenses and miles (priced at
>   72.5¢ to Jun 30 and 76¢ from Jul 1), the Jan 15 payment, then the 2027 quarters. Excel, Google Sheets and Numbers.
> - **The Freelancer Tax Checklist** (printable PDF): what to gather and do before you file.
> - **The S Corp Check** (2 printable pages): sole prop vs S corp at six profit levels and two salary levels, with
>   2026 federal figures, plus a worksheet and questions to take to a CPA. Run your own numbers in the free
>   calculator on 1099money.netlify.app.
> - **A Start Here page**: your tax season in five dated steps.
>
> The checklist is also free when you join the 1099 Money email list, and the S corp calculator is free on the site.
>
> Federal figures for the 2026 tax year. Educational tools, not tax, legal or financial advice. 14-day refunds.

## Before it goes live (manual)

- [ ] Pick the price and replace every `[PRICE]` and `[CODE]`.
- [ ] Re-run the S corp table if the site's calculator changes (`node` against `apps/freelance-tax/lib/scorp.js`).
- [ ] Unpublish or retitle after Apr 15, 2027.
