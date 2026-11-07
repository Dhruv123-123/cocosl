# Money Made Simple (the ebook): KDP notes

A short book, about 24,000 words in 19 chapters, compiled and edited from the five Money Made Simple guides (the
20-Minute Budget, Bill Cut Kit, Debt-Free Date Planner, Credit Report Audit Kit and Start Investing With $100 a Month),
the welcome emails and the newsletter. It has the same examples and figures as the guides, with US spelling, no sales
links or discount codes, and new chapters on living on the weekly number, the emergency fund, big goals, a money
calendar, the first thirty days and common questions. **Nothing has been uploaded or submitted.**

```
python launch/ebook/build_ebook.py              # → launch/ebook/dist/ (git-ignored), under 10 seconds
python launch/ebook/build_ebook.py --skip-pdf   # EPUB and Kindle cover only
```

| File | What it is | Upload to |
|---|---|---|
| `Money-Made-Simple.epub` | Kindle eBook manuscript: EPUB 3, reflowable, contents page, cover embedded | Kindle eBook > Manuscript |
| `Money-Made-Simple-Kindle-Cover.jpg` | 1600 x 2560 px RGB JPEG (KDP's recommended 1.6:1) | Kindle eBook > Cover |
| `Money-Made-Simple-Paperback-Interior.pdf` | 103 pages, 6 x 9 in, no bleed, fonts embedded, mirrored margins | Paperback > Manuscript |
| `Money-Made-Simple-Paperback-Cover.pdf` | Full wrap 12.482 x 9.25 in: back + 0.232 in spine + front, 0.125 in bleed | Paperback > Cover |
| `Money-Made-Simple-Paperback-Cover-preview.png` | Quick look at the wrap (not for upload) | — |

The text lives in `chapters/*.md` (pandoc Markdown). Cross-references are written `Chapter {{chapter-id}}` and the
build turns them into numbers, so chapters can be moved. The build stops if the text uses banned wording
("guarantee", "risk-free" and so on), if any reference is unknown, or if any printed word sits closer than 0.4 in to the
page edge. The contents page numbers come from the rendered PDF and are checked again on a second pass.

## Specs used

- **Paperback trim:** 6 x 9 in, black ink on white paper, no bleed. Matte cover.
- **Margins:** 0.8 in inside, 0.6 in outside, 0.7 in top, 0.8 in bottom. KDP's minimums are 0.375 in inside for 24-150
  pages and 0.5 in for 151-300, with 0.25 in outside; these clear both, so the book can grow without a layout change.
- **Spine:** 103 x 0.002252 in = 0.232 in. KDP allows spine text from 79 pages, so the spine says MONEY MADE SIMPLE in
  small type, centred. If the page count changes, rebuild: the cover is sized from the real page count.
- **Kindle:** EPUB 3 from pandoc, Kindle's own fonts, no fixed layout. Tables are short so they reflow on a phone.
  `epubcheck` wasn't available here; KDP's previewer runs its own checks, so open the file in **Kindle Previewer**
  before you publish.
- **Barcode:** KDP prints it at the bottom right of the back cover, over the dark band. Nothing important sits there.

## Before you upload: check

- [ ] Read the whole book once on paper or a tablet. It was compiled and edited with AI tools; a human read is the last step.
- [ ] Open the EPUB in Kindle Previewer (phone and tablet views) and the interior PDF in KDP's Print Previewer.
- [ ] Check the 2026 figures in Chapter 16 (IRA $7,500, 401(k) $24,500, Roth income ranges) against IRS.gov, and change
      them to 2027 figures if you publish after the IRS announces them.
- [ ] Order one paperback proof copy.
- [ ] Decide the author name. The files use **Money Made Simple** as the author and brand, to match the planner and
      journals. If you'd rather publish under your own name or a pen name, change `AUTHOR` in `build_ebook.py` and rebuild.

## Listing details

- **Title:** Money Made Simple
- **Subtitle:** A Plain-English Guide to Budgeting in 20 Minutes a Week, Cutting Your Bills, Paying Off Debt and Starting to Invest
- **Author:** Money Made Simple (see the check above)
- **Edition:** first
- **Description (same for both formats):**

  > Most budgets fail because they ask for dozens of small decisions every day. This one asks for one decision a month
  > and a twenty-minute check-in each week.
  >
  > Money Made Simple is a short, plain-English guide to getting your money organized and keeping it that way. Split
  > your take-home pay into four lines (bills, funds, goals and one weekly spending number), put the first three on
  > autopilot, and spend the fourth however you like. Then use the same simple approach on everything else:
  >
  > - Find your real numbers in one evening, including the costs that aren't monthly but aren't surprises either
  > - Cut forgotten subscriptions, with word-for-word scripts for lowering the bills you keep
  > - Put a date on paying off debt, with the avalanche and snowball methods worked through using example numbers
  > - Build an emergency fund and save for big goals
  > - Read your credit reports, dispute errors and freeze your credit for free
  > - Start investing with $100 a month: which account to open, what to buy, and why fees matter
  > - Follow a month-by-month money calendar and a plan for your first thirty days
  >
  > Written for US readers. Educational content, not financial, tax, legal or investment advice. The people in the
  > examples are fictional.

- **Keywords (7 boxes):** budgeting for beginners · personal finance book · how to pay off debt · debt snowball and
  avalanche · money management made easy · investing for beginners with little money · fix credit report errors
- **Categories:** Business & Money > Personal Finance > Budgeting & Money Management; Business & Money > Personal
  Finance > Debt (pick the closest KDP offers). Paperback categories are chosen separately; use the same.
- **Language:** English. **Adult content:** no. **Low-content book:** no (this one needs an ISBN for the paperback; use
  KDP's free ISBN unless you have your own).

## Prices and royalties

| Format | List price | Royalty option | Roughly per sale |
|---|---|---|---|
| Kindle eBook | **$8.99** (the "$9" slot) | 70% (allowed from $2.99 to $9.99) | about $6.27 after the delivery fee (about $0.03 for a 0.2 MB file) |
| Paperback | **$14.99** | 60% minus printing | about $6.69, if printing is $2.30 (KDP's flat US rate for black ink under 110 pages on the current rate card) |

Check both in KDP's pricing pages before you publish; KDP sets the printing cost and the delivery fee, and they change.
Expanded Distribution pays 40% minus printing (about $3.70) and is optional.

**KDP Select** (Kindle Unlimited) needs the eBook to be exclusive to Amazon for 90 days. It's a reasonable start for a
new author with no other ebook store; it doesn't stop you selling the paperback or the separate guides elsewhere,
because they're different products. Don't sell this same EPUB on Gumroad while it's enrolled.

## AI disclosure (KDP asks this on the Content page)

| KDP question | Answer | Why |
|---|---|---|
| AI-generated **text**? | **Yes** | The book was compiled, rewritten and expanded from the guides with an AI tool (Claude) and then reviewed. Several chapters are new AI-drafted text |
| AI-generated **images**? | **Yes** | No image generator was used, but the cover and the interior layout were produced by code an AI tool wrote. Answering yes is the safe reading, as for the planner |
| AI-generated **translations**? | **No** | English only |

If KDP asks for detail: "Text drafted and edited with an AI assistant from the publisher's own guides, then reviewed by
the publisher. Cover and interior layouts generated by AI-written code; no AI image generator. Worked examples
calculated with software and checked." The copyright page says the same.

## Rules

- No promises of savings, income or credit scores; no fake reviews, review swaps or "bestseller" claims. The book's
  About page asks for an honest review of any kind, which is allowed; don't offer anything in return for one.
- Keep "not financial advice" on the copyright page, the back cover and the description.
- Update it once a year: retirement limits, credit bureau policies and federal student loan rules change. Edit the
  chapter files, rebuild, and upload the new files to the same KDP title (a new edition only if the changes are large).
