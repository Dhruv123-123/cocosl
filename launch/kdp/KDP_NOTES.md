# KDP paperbacks: notes

Three low-content paperbacks: the **2027 Budget Planner**, the **Debt Payoff Journal** and the **52-Week Savings
Challenge Log**. Everything needed to publish them on Amazon KDP is here. The two journals are covered in their own section at the end, and the
specs and the AI disclosure answers below apply to all three. **Nothing has been uploaded or submitted.**

```
python launch/kdp/build_kdp.py                        # all three → launch/kdp/dist/ (git-ignored)
python launch/kdp/build_kdp.py --only debt-journal    # or planner / savings-log
```

| File | What it is |
|---|---|
| `2027-Budget-Planner-KDP-Interior.pdf` | Manuscript: 52 pages, 8.5 x 11 in, no bleed, fonts embedded |
| `2027-Budget-Planner-KDP-Cover.pdf` | Full-wrap cover: 17.3671 x 11.25 in (back + 0.1171 in spine + front, 0.125 in bleed) |
| `2027-Budget-Planner-KDP-Cover-preview.png` | Quick look at the cover (not for upload) |

## Specs used (checked against KDP's help pages, Nov 2026)

- **Trim:** 8.5 x 11 in. **Ink and paper:** black and white interior, white paper. **Bleed:** no (interior). **Cover finish:** matte suits a planner.
- **Margins:** KDP's minimums for 24-150 pages are 0.375 in inside and 0.25 in outside. Every page keeps at least 0.55 in from every edge, and the footer sits 0.3 in from the bottom.
- **Page count:** 52, a multiple of 4. The pages are the title, a copyright page, how to use, the year at a glance, goals, the year overview, yearly bills, 26 paychecks, savings, debt, 3 pages a month for 12 months, the year review, the next year, and notes.
- **Spine:** 52 x 0.002252 in = 0.1171 in. KDP only prints spine text on books of 80 pages or more, so the spine is left plain and the same cream as the cover. Any small drift when the cover wraps then doesn't show.
- **Cover:** text stays at least 0.375 in inside the trim. KDP adds the barcode (about 2 x 1.2 in) at the bottom right of the back cover, where there's only the dark band.
- **Colour:** the interior has light green accents and tints. In a black-ink book they print as light greys, which is fine for a planner. Check the first printed proof for contrast.

Sources: [KDP trim size, bleed and margins](https://kdp.amazon.com/help/topic/G201857950), which gives the margins, the spine formula and the 80-page spine-text rule.

## Before you upload: check

- [ ] Open the interior PDF in KDP's **Print Previewer** and fix any flag (there shouldn't be any).
- [ ] Order **one author proof copy** and check it: the calendar dates, how the greys print, and whether a pen bleeds through.
- [ ] Recheck the IRS dates for 2027 once the IRS publishes its calendar. The book only marks the usual dates and says "check irs.gov".

## Listing details (copy into KDP)

- **Title:** 2027 Budget Planner
- **Subtitle:** Monthly Budget, Bill and Spending Tracker, January to December 2027, 8.5 x 11
- **Author / brand:** Money Made Simple. Use the same name across your books.
- **Description:**

  > Plan 2027 one month at a time. This dated budget planner gives every month a calendar with US holidays and the
  > usual tax dates marked, a budget page with weekly check-ins, and a spending log with a month-end review.
  >
  > Inside: year at a glance, money goals, a year overview, yearly bills and renewals, a 26-paycheck tracker, savings
  > goals and debt payoff pages, then a year in review and a look ahead to 2028. 52 pages, 8.5 x 11 in, Sunday-start
  > calendars.
  >
  > An organising tool, not financial advice.

- **Keywords (7 boxes):** 2027 budget planner · monthly budget book · bill tracker organizer · expense tracker notebook ·
  finance planner 2027 · paycheck budget planner · debt payoff and savings tracker
- **Categories:** Self-Help > Personal Finance (or Business & Money > Personal Finance > Budgeting). Pick the closest options KDP offers.
- **ISBN:** use KDP's free ISBN, or tick **low-content book** (planners qualify) to publish without one. A free KDP ISBN
  can only be used on Amazon.
- **Price:** about $9.99 to $12.99. Paperback royalty is 60% of list price minus the printing cost. Get the exact
  printing cost for 52 pages, black ink, 8.5 x 11 from KDP's pricing calculator. Don't price below the point where the
  royalty is still worth having (at least about $3).
- **Publishing timing:** list it as soon as it's checked. "2027 planner" searches climb from August and stay high through
  January (see `launch/etsy/SEO_NOTES.md`).

## AI disclosure (KDP asks this on the Content page)

KDP asks whether the book contains AI-generated **text**, **images** or **translations**. Content counts as AI-generated
when an AI tool produced it, even if a person edited it afterwards. Brainstorming, or editing your own writing with AI,
is "AI-assisted" and doesn't need disclosing. KDP doesn't show the answer to buyers, and from 2026 it removes titles
that should have been disclosed and weren't.

How this book was made, and the answers that match:

| KDP question | Answer | Why |
|---|---|---|
| AI-generated **text**? | **Yes** | The planner's text (headings, prompts, the how-to page, the back cover and the description) was drafted by an AI tool (Claude) and then reviewed |
| AI-generated **images**? | **Yes** | No image generator was used, but the cover and page layouts were produced by code that an AI tool wrote. Answering yes is the safe reading |
| AI-generated **translations**? | **No** | English only |

If KDP asks for detail, describe it like this: "Text drafted with an AI assistant and edited by the publisher. Cover
and interior layouts generated by AI-written code; no AI image generator. Calendar dates produced by software and
verified." The copyright page already says the layouts and text were made with help from AI tools.

Sources: [WriteO: KDP's AI disclosure rules and the 2026 enforcement](https://writeo.app/news/amazon-kdp-ai-disclosure-enforcement-2026).
Before answering, read KDP's own content guidelines on AI in Help > Content Guidelines.

## Rules

- Don't promise savings or income. Keep the "not financial advice" line on the back cover and the copyright page.
- No fake reviews, no review swaps, and no "bestseller" claims.
- Next year: run `python launch/kdp/build_kdp.py --year 2028` by mid-August 2027, recheck the holidays and tax dates,
  and upload it as a new book. Don't edit the 2027 one.

## The two journals

Both have original interiors (not adapted from the Etsy printables), are undated so they sell all year, and use the same
specs, rules and AI-disclosure answers as above (text: yes, images: yes, translations: no).

| | Debt Payoff Journal | 52-Week Savings Challenge Log |
|---|---|---|
| Files | `Debt-Payoff-Journal-KDP-Interior.pdf`, `-KDP-Cover.pdf` | `52-Week-Savings-Log-KDP-Interior.pdf`, `-KDP-Cover.pdf` |
| Pages / spine | 60 pages, spine 0.1351 in, cover 17.3851 x 11.25 in | 64 pages, spine 0.1441 in, cover 17.3941 x 11.25 in |
| Inside | My debts, payoff order (snowball / avalanche / own), 100-block countdown, milestones, find-extra-money worksheet, then 12 months of: balances, payment log, weekly check-ins, a journal prompt. A debt-free page and a look back | Plan tables (classic, reverse, custom: both plans total $1,378), a colour-in year chart, 52 weekly pages (amount, running total, where it came from, no-spend days, a win) with a progress strip, 4 quarter reviews and a year in review |
| Title | Debt Payoff Journal | 52-Week Savings Challenge Log |
| Subtitle | A 12-Month Debt Tracker and Payment Log with Weekly Check-Ins, 8.5 x 11 | A Weekly Money Saving Challenge Tracker, Classic or Reverse $1,378, 8.5 x 11 |
| Keywords | debt payoff tracker · debt snowball journal · credit card payoff log · debt free planner · loan payment tracker · bill payment log book · personal finance journal | 52 week savings challenge · money saving challenge book · savings tracker journal · savings goal log · cash savings planner · budget savings book · no spend challenge tracker |
| Category | Self-Help > Personal Finance (or Business & Money > Personal Finance > Budgeting) | same |
| Price | about $8.99 to $10.99 | about $8.99 to $10.99 |
| Best season | January (resolutions), then steady; second bump March | Late December to January (savings challenge searches roughly triple in January) |

Description, debt journal:

> Pay it off. Write it down. Watch it shrink. This undated twelve-month journal walks you through paying off credit cards,
> loans and everything in between: list your debts, choose snowball or avalanche, colour a 100-block countdown, and log
> balances, payments and weekly check-ins, with a journal prompt every month. 60 pages, 8.5 x 11 in. An organising tool,
> not financial advice.

Description, savings log:

> Save a little every week and watch it add up. One page for every week of the 52-week money challenge: your amount,
> the running total, where the money came from, no-spend days and a win, plus classic and reverse plan tables (both
> reach $1,378), a colour-in year chart and quarter reviews. Undated, 64 pages, 8.5 x 11 in. An organising tool, not
> financial advice.
