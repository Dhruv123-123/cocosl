# Etsy shop: setup and launch

A second sales channel for Money Made Simple: 17 listings, all digital downloads. Every listing folder has the
files to upload, three mockup images and `LISTING.md` with the title, 13 tags, price and description to paste in.
`listings.csv` has everything on one sheet.

## The 17 listings

| # | Listing | Price | You keep (approx.) | Files |
|---|---|---|---|---|
| 1 | Monthly Budget Planner | $6 | $4.98 | Letter + A4 PDF |
| 2 | Paycheck Budget Planner | $4 | $3.17 | Letter + A4 PDF |
| 3 | Savings Challenge Tracker ($500 to $5,000) | $3 | $2.26 | Letter + A4 PDF |
| 4 | 52-Week Savings Challenge | $3 | $2.26 | Letter + A4 PDF |
| 5 | Bill Payment Tracker | $4 | $3.17 | Letter + A4 PDF |
| 6 | Sinking Funds Tracker | $4 | $3.17 | Letter + A4 PDF |
| 7 | Debt Payoff Coloring Trackers | $4 | $3.17 | Letter + A4 PDF |
| 8 | Monthly Expense Tracker | $3 | $2.26 | Letter + A4 PDF |
| 9 | No-Spend Challenge | $3 | $2.26 | Letter + A4 PDF |
| 10 | Subscription Tracker | $3 | $2.26 | Letter + A4 PDF |
| 11 | **Printable Budget Binder** (all 10 above) | $12 | $10.41 | 1 zip ($37 separately) |
| 12 | The Bill Cut Kit | $5 | $4.07 | PDF + XLSX |
| 13 | The 20-Minute Budget | $12 | $10.41 | PDF + XLSX |
| 14 | The Credit Report Audit Kit | $9 | $7.70 | PDF + XLSX |
| 15 | The Debt-Free Date Planner | $17 | $14.94 | PDF + XLSX |
| 16 | Start Investing With $100 a Month | $19 | $16.74 | PDF + XLSX |
| 17 | **The Money Made Simple Toolkit** (12 to 16) | $39 | $34.84 | Start Here PDF + 1 zip |

"You keep" uses US seller fees as of November 2026: $0.20 listing fee, 6.5% transaction fee, 3% + $0.25 payment
processing. Check etsy.com/legal/fees before you list; fees differ outside the US. Opt out of Offsite Ads while
you're small (it's optional until $10,000 a year in sales), or a single ad-driven sale costs 15%.

Gumroad prices and Etsy prices are the same for the six guides, so nobody is penalised for where they buy.

## Before your first listing (about 45 minutes)

1. **Open the shop:** etsy.com/sell. Shop name: MoneyMadeSimple (or the closest available; Etsy shop names have no spaces).
   Etsy may charge a one-time shop setup fee in some countries; it shows during sign-up.
2. **Shop icon and banner:** use `brand-kit/profile-picture.png` from the launch pack as the icon.
3. **About and policies:** the sample text is below. Digital downloads usually say "no returns", but offer help if a file
   won't open; it costs nothing and prevents bad reviews.
4. **Sections** (Shop Manager > Listings > Sections): "Budget Planners", "Savings Challenges", "Trackers",
   "Guides + Spreadsheets", "Bundles". Put each bundle in "Bundles" too. Sections are how buyers browse from one item to the next.
5. **Thank-you coupon** (Marketing > Sales and discounts > "Thank you" coupon): 20% off the next order, so a $3 buyer
   comes back for the binder or a guide. This is the Etsy version of the Gumroad upsell codes.
6. **Abandoned-cart and favourites coupons** (same menu): 10% off. Etsy sends them for you.

## Listing each item (5 minutes each)

For every folder in this `etsy/` folder:

1. Shop Manager > Listings > **Add a listing** > Digital files.
2. **Photos:** upload `mockup-01-hero.png`, `mockup-02-inside.png`, `mockup-03-details.png` in that order.
3. **Title, price, tags, description:** paste from `LISTING.md`. Use all 13 tags.
4. **About this listing:** Who made it: *I did*. What is it: *A finished product*. When was it made: the most recent range.
5. **Digital files:** upload the PDF/XLSX/ZIP files in the folder (never the mockups or LISTING.md).
6. **Category:** as suggested in `LISTING.md`, or the closest one Etsy offers.
7. Add it to its sections. Publish.

List the cheap printables first; they get the first sales and reviews. Then the binder, then the guides.

## Rules that keep the shop safe

- **No links or prompts to buy off Etsy** in listings, files or messages. The Etsy editions of the guides already have the
  Gumroad codes and store links taken out. They point to "the Money Made Simple shop on Etsy" instead. Never upload the
  Gumroad PDFs to Etsy.
- **Say how it's made.** Each description has a "How it's made" line saying AI tools helped with drafting and layout,
  and that a human checked every page. Etsy's creativity standards ask for that.
- **Personal use only** is stated in every description and on every page footer.
- **No made-up reviews, no "bestseller" claims, no fake sale prices.** If you run a sale, use Etsy's own sale tool.
- **Not advice:** every listing says "organising tool / educational, not financial advice".

## Sample shop text

**Shop title (55 characters max):** Simple budget printables and money spreadsheets

**Announcement:** Undated budget printables and plain-English money guides. Instant download, US Letter and A4.
Start with the Printable Budget Binder for everything at once.

**About:** Money Made Simple makes calm, practical money tools for people who feel behind. No jargon, no hype. Every
planner is undated, ink-friendly and printable at home; every guide comes with a spreadsheet that does the maths. Made
by a small team. AI tools help with drafting and layout, and a human checks every page.

**Policies, digital items:** Because these are instant downloads, we can't accept returns. If a file won't open or
print properly, message us and we'll fix it or refund you.

## After launch

- Week 1: list all 17. Share the hero mockups on Instagram/Pinterest with "find it on Etsy, search Money Made Simple".
- Week 2: check Shop Manager > Stats. For any listing with views but no favourites, change the first image or the first
  40 characters of the title. Etsy search weighs those most.
- Month 2: the best-selling printable gets a variant (e.g. a dated 2027 version, or a "couples" monthly planner).
- Rebuild with `python launch/etsy/build_etsy.py` after any edit; it re-checks every title, tag and page.
