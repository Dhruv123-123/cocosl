# 1099 Money: launch day

The third brand from `research/04-adjacent-niches.md`: money and taxes for US freelancers, creators and
side hustlers. Promise: **get paid, keep more, never fear April.** Handle: **@1099money** everywhere.

Nothing here posts by itself. Every post still goes through human review, and every tax figure is listed
under CHECK BEFORE POSTING in its caption.txt.

## Before Day 1 (about 2 hours, only you can do these)

1. **Claim the handle** `@1099money` on Instagram, YouTube and TikTok (fallbacks: `@1099.money`,
   `@the1099money`; if you change it, update `watermark` and `accounts` in `brands/1099-money.yaml`
   and re-run `factory brandkit 1099-money`).
2. **Upload the brand kit** from `brand-kit/`: profile picture, YouTube banner + watermark, Instagram
   highlight covers. Paste bios from `brand-kit/bio-pack.txt` (keep "AI-assisted" visible).
3. **Product:** create the Gumroad (or Lemon Squeezy) listing from
   `product-quarterly-tax-tracker/LISTING.md`. Upload the PDF + XLSX. $15, launch offer $9 for 7 days.
   Put the real URL in `products` in the brand file.
4. **Link-in-bio page:** `link-in-bio-page/index.html`. Replace example.com links, host it free (Netlify
   Drop / GitHub Pages), and set `link_in_bio` in the brand file.
5. **Affiliates:** apply now (see `AFFILIATES.md`). Until a program approves you, **don't post the
   affiliate-tagged pieces with a link**: either hold them, or post them with the affiliate paragraph
   removed and no link. Never post an example.com link.
6. **Voice:** the 14 Shorts and 2 long videos need narration. Connect a voice (docs/CREDENTIALS.md §4),
   then `factory import launch/1099-money/content.json --brand 1099-money` renders them narrated.
   Until then, the carousels can go out on their own.

## The first 14 days (Mon Nov 16 – Sun Nov 29, 2026)

`POSTING_PLAN.md` has the full table; `calendar.ics` imports into any calendar. Shape:

- **Every day, 12:30 ET:** one Short to TikTok, YouTube Shorts and Instagram Reels.
- **Mon/Wed/Fri/Sat, 19:00 ET:** one Instagram carousel.
- **Sundays, 19:00 ET:** one long video on YouTube.
- Never more than 2 posts per platform per day.

This is a launch pace (14 Shorts + 8 carousels + 2 long in two weeks). From Day 15 drop to the brand
cadence: 5 Shorts, 3 carousels, 1 long video a week.

Timing note: the Jan 15, 2027 estimated-tax deadline is the brand's first big moment. The deadline Short
("The tax deadline after New Year's") and the calendar carousel are early in the plan on purpose; repost
the deadline Short (or a fresh cut) around Jan 8–14.

## Each post, every time

1. Open the post in the review queue (`factory review`) or its folder here.
2. Tick every line under **CHECK BEFORE POSTING** in caption.txt against the linked irs.gov / ssa.gov
   source. These are 2026 federal figures: standard deduction $16,100, brackets, SS wage base $184,500,
   mileage 72.5¢ Jan–Jun / 76¢ Jul–Dec, 401(k) $24,500, HSA $4,400/$8,750, 1099-NEC $2,000, 1099-K $20,000/200.
3. Paste the caption exactly (it already has the AI disclosure, "not tax advice" and any affiliate
   disclosure). Set the platform's AI-label toggle where required.
4. Revenue pieces (marked **affiliate** / **product** in the plan): make sure the link-in-bio page has
   that link live on that day.

## Rules for this brand

- Every tax number is dated ("for 2026") and sourced. Re-check all of them every January and update
  `Tax Tables` in the tracker (`python launch/1099-money/product/build_tracker.py`).
- "Educational, not tax advice" in every tax caption. No "write off everything", no hiding income, no
  guaranteed refunds, no state-specific claims without a source.
- No fake clients or testimonials. Examples are labelled (Sam is fictional).
- Cross-sell: freelancers and small businesses are the AI Ad Studio's buyers. Once the account has
  ~1,000 followers, a "how I make video ads for small brands" piece can point there (with disclosure).
