# Money Made Simple: product ladder

Free → $9–12 → $15 → $24 bundle. Every rung is built and in this folder; this page says what each one is for, where it gets promoted, and why it costs what it costs.

| Rung | Product | Price (launch) | Folder | Job |
|---|---|---|---|---|
| 0 | **The 7-Day Money Reset** (5-page printable PDF) | Free, for email signup | `free-lead-magnet/` | Turns a viewer into a subscriber. One action a day for a week. |
| 1a | **The 20-Minute Budget** (14-page guide + spreadsheet) | $12 ($7) | `../product/` (existing) | First purchase for budgeting-pillar viewers. The reset's Day 7 points here. |
| 1b | **Debt Payoff Planner** (spreadsheet + 8-page guide) | $9 ($5) | `debt-payoff-planner/` | First purchase for debt-pillar viewers. Picks up where the reset's Day 6 stops. |
| 2 | **First Investing Account Kit** (17-page guide) | $15 ($10) | `first-investing-account-kit/` | Next step once budget and debt are handled; first purchase for investing-pillar viewers. |
| 3 | **Starter Bundle** (all three paid products) | $24 ($19) | `bundle/` | Higher order value; the obvious choice for anyone who wants two or more. |

Each paid folder has `LISTING.md` (titles, description, bullets, pricing, FAQ, refund line, tags, delivery message) and a 1600×1200 cover PNG. The free one has its PDF and a cover for the link page.

## The path a reader takes

```
short / carousel / long video  ──>  link page  ──>  free 7-Day Money Reset (email signup)
                                        │                    │
                                        │          welcome emails, days 0-14 (below)
                                        ▼                    ▼
                         $12 Budget  /  $9 Debt Planner  ──>  $15 Investing Kit  ──>  $24 Bundle
```

Most people will buy whichever product matches the video that found them. The email sequence then introduces the others in a sensible order: budget first, then debt, then investing.

## Where each rung gets promoted

Content pillars come from `brands/money-made-simple.yaml`. Piece numbers (#n) refer to `launch/money-made-simple/content.json` and the 14-day `POSTING_PLAN.md`.

| Product | Pillar(s) | Posts that point to it (from the launch plan) | CTA wording |
|---|---|---|---|
| 7-Day Money Reset (free) | All four | Default CTA on every post that doesn't name a product: #0 two-account trick, #6 credit freeze, #9 bank alerts (that's the reset's Day 4), #13 forgotten subscriptions (Day 2), #5 and #18 credit reports | "Free 7-day money reset at the link in bio." |
| 20-Minute Budget | Budgeting systems that actually stick | #14 money date, #1 budget weekly, #10 "surprise" bills, #20 app vs spreadsheet, #23 30-day reset (long) | "I made a guide + spreadsheet for this (my own product): link in bio." |
| Debt Payoff Planner | Credit scores and debt payoff | #19 avalanche vs snowball carousel (Day 11; best fit), #7 $60 vs $150 on a $3,000 card, #12 don't cancel that old card | "The spreadsheet that does this math for your own debts is in bio (my own product)." |
| First Investing Account Kit | First-time investing basics | #21 opening your first investment account carousel (Day 12; best fit), #22 investing with $100 a month (long), #16 Roth or Traditional, #2 Roth money isn't locked away, #4 the fee that eats $18,000, #17 index funds, #11 one-fund retirement, #3 401(k) match | "Step-by-step weekend guide in bio (my own product). Education, not advice." |
| Starter Bundle | All | Not pushed in posts. Shown on the link page and in emails 7 and 14 only. | "All three, $12 less than separately." |

Rules for every promotion: it's your own product, so say so plainly ("my own product"); keep the brand AI disclosure; no testimonials until real buyers give them, word for word, with permission; no earnings or results claims; investing posts never name or recommend a company or fund.

Fit with the launch calendar: the existing plan already sends template traffic on Days 1, 2, 3, 8 and 14. Use the new products on their best-fit days without adding extra posts:

- **Day 11 (Tue Nov 17), carousel #19, avalanche vs snowball:** last slide → Debt Payoff Planner.
- **Day 12 (Wed Nov 18), carousel #21, first investment account:** last slide → Investing Kit.
- **Day 9 (Sun Nov 15), long #22, investing with $100/month:** description → Investing Kit (pin it as the first comment); keep the template as the second link.
- **Everything else:** the free reset is the default call to action. A subscriber is worth more than a click.

## Link-in-bio page order

1. **Free: The 7-Day Money Reset** (signup form; cover `free-lead-magnet/cover-7-day-money-reset.png`)
2. **The 20-Minute Budget**: $12
3. **Debt Payoff Planner**: $9
4. **First Investing Account Kit**: $15
5. **Starter Bundle**: all three for $24 (save $12)
6. Affiliate HYSA link, with the affiliate disclosure (already on the page via `AFFILIATE_NOTE`)

### Wiring it into the factory (for the lead)

`funnel/linkpage.lead_magnet()` already uses a product with `price: 0` and a `url` as the signup freebie, so no code change is needed. Upload `The-7-Day-Money-Reset.pdf` somewhere with a stable URL (a $0 Gumroad product, or the static site folder next to `index.html`), then set `products:` in `brands/money-made-simple.yaml` to:

```yaml
products:
  - {name: "The 7-Day Money Reset", url: "https://[host]/the-7-day-money-reset.pdf", price: 0}
  - {name: "The 20-Minute Budget (guide + spreadsheet)", url: "https://[you].gumroad.com/l/[budget]", price: 12}
  - {name: "Debt Payoff Planner (spreadsheet + guide)", url: "https://[you].gumroad.com/l/[planner]", price: 9}
  - {name: "First Investing Account Kit", url: "https://[you].gumroad.com/l/[kit]", price: 15}
  - {name: "Starter Bundle: all three", url: "https://[you].gumroad.com/l/[bundle]", price: 24}
```

(The current entry calls the budget a "Notion + Sheets template", but the product is an .xlsx + PDF; the name above fixes that.)

## Welcome email sequence (days after signup)

The factory sends the double opt-in confirmation (which delivers the reset) and a weekly digest. These welcome emails are drafts to load into Kit/Beehiiv/Mailchimp as an automation, or to send by hand. One idea per email, plain text, with the brand's real sender identity, postal address and unsubscribe link (CAN-SPAM). Product mentions are always labelled as your own product.

| Day | Subject (draft) | Content | Product mention |
|---|---|---|---|
| 0 | Your 7-Day Money Reset is here | PDF link. "Start with Day 1 today: 20 minutes." | None |
| 2 | The 10-minute money win most people skip | Day 2 subscription sweep; reply and tell me what you cancelled | None |
| 4 | Three alerts that save you from fees | Day 4, with where to find alert settings | None |
| 6 | Avalanche or snowball? Here's the actual math | Day 6 + the worked example (avalanche vs snowball within ~$255 over 43 months; extra $250/month vs minimums only saves ~$7,658: computed numbers from the planner's fictional example) | **Debt Payoff Planner** ($9; launch price only if the window is open) |
| 7 | Your weekly number (and how to keep it) | Day 7 + the 20-minute weekly check-in | **The 20-Minute Budget** ($12) |
| 10 | Did the reset stick? | Ask for a reply: what was hardest? (Gives you real, permissioned feedback; never turn replies into testimonials without asking.) | None |
| 14 | What comes after budget and debt | Order of operations: buffer, match, high-rate debt, then invest | **First Investing Account Kit** ($15) and the **Starter Bundle** ($24, save $12) |
| then | Weekly digest | `newsletter.draft_digest` | One product or affiliate mention per digest, rotating |

## Pricing rationale

- **Free reset:** the cheapest thing to give and the most useful to get: an email address you own on no platform's terms. It's genuinely useful on its own (no "the real answers are in the paid version"), which is what makes the soft upsell on its last page acceptable.
- **$9 planner, $12 budget (impulse rung):** under the point where most people buy without much deliberation. The planner is $3 cheaper than the budget because it's a narrower tool with a shorter guide. Launch prices ($5/$7) are real, time-limited discounts to get first buyers and first real feedback.
- **$15 investing kit:** longer (17 pages) and covers a higher-stakes decision. It's priced as a guide, not a course; it's still an easy yes for someone about to put thousands into an account. No upsell into "advice" or coaching. That would need licensing considerations.
- **$24 bundle:** a third off the $36 combined price, so it's clearly the better deal for anyone who wants two of the three ($21–27 separately). It raises average order value without discounting the single products. At launch prices the bundle ($19) stays below buying all three on launch ($22).
- **Gumroad fees** (check current terms): a percentage plus a per-sale fee, which hits low prices hardest. That's one reason the floor is $9, not $5, after launch.
- **Refunds:** 14 days, no questions. On digital products under $25 the cost is small and it removes the main reason people hesitate.
- **Revisit after 30 days** with real data: conversion per product, refund rate, which pillar sells. Raise a price only after it's selling. Don't invent scarcity.

## Rebuilding and checking the files

Everything is generated from `_build/` (Python + Jinja templates + node Playwright):

```bash
cd launch/products/_build
python3 build_planner_xlsx.py          # Debt-Payoff-Planner.xlsx (formulas only)
python3 verify_planner.py              # LibreOffice recalc vs Python simulation, 6 scenarios -> ALL PASS
python3 build_docs.py                  # all PDFs (+ HTML sources) and the four cover PNGs
PREVIEW_DIR=/tmp/prev python3 build_docs.py reset   # also writes page PNGs to look at
```

`build_docs.py` flags any page whose content runs into the footer. All numbers in the PDFs come from `figures.py` / `debtsim.py`; nothing is typed in by hand. The 2026 contribution limits in `templates/investing-kit.html.j2` are the only hand-entered facts, and they're marked "verify at irs.gov".
