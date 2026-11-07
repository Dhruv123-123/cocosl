# 2027 Budget Planner: KDP paperback notes

Everything needed to publish the planner as an Amazon KDP paperback. **Nothing has been uploaded or submitted.**

```
python launch/kdp/build_kdp.py          # → launch/kdp/dist/ (git-ignored)
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
