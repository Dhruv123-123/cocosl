# Operating playbook

How to actually run this thing for 90 days. Time estimates assume the pipeline is set up and Claude is
writing the drafts.

## The model in one paragraph

Views on Shorts pay about $0.03 to $0.10 per 1,000, so a million Shorts views is roughly $50. The money
is in what the audience buys: affiliate offers, your own small digital products, and (fastest) AI video
work sold to brands. The factory automates production; you supply taste, fact-checking and approval.
That human step is also what keeps the content monetizable under YouTube's "inauthentic content" rule
and copyrightable in the US.

## Week 0: set up (one evening)

1. `factory init` in a fresh folder, then `factory demo` to see sample output with no keys.
2. Pick one niche. Score a few candidates:
   `factory niche "personal finance apps" "history of everyday objects" "excel for small business"`
   Prefer high ad value plus something to sell. Avoid the risky and saturated flags.
3. `factory new-brand "your niche" --audience "who exactly"` and edit the YAML it writes. Add real
   affiliate links (only products you would recommend to a friend) and your product ideas.
4. Add `ANTHROPIC_API_KEY` to `.env`. Optionally a voice (your own cloned voice via ElevenLabs, or Piper)
   and an image provider (ComfyUI locally, or OpenAI/Replicate).
5. Create the accounts yourself, one per platform for this brand, and connect them (docs/CREDENTIALS.md).
6. `factory status` until every platform you use says ready. Keep `FACTORY_DRY_RUN=1` for now.

## Days 1 to 30: build the machine and the portfolio

Daily, about 30 to 45 minutes:

- Morning: the worker (or `factory daily --brand <slug>`) refills ideas and produces 2 posts for review.
- Open the dashboard Review page. For each post: watch it, fix anything off in the caption, tick every
  fact-check claim only after you've checked it, then Approve & schedule or Reject with a reason.
  Rejection reasons are worth writing; feed them back as `--notes` when you re-produce.

Weekly:

- Target 5 Shorts, 3 carousels and 1 long video per brand (the YAML cadence caps enforce a ceiling).
- `factory repurpose <long-post-id>` turns each long video into 3 standalone Shorts and a carousel.
- Make 5 sample AI UGC ads for real products you like (business module) as a portfolio. These are
  spokesperson/demo ads, never fake customer reviews.

First real post: flip `FACTORY_DRY_RUN=0`, schedule one post to a single platform, check it on the app,
then let the schedule run.

## Days 31 to 60: first money

- Build a lead list of 20 small DTC brands or local businesses (CSV import on the Clients page).
- Draft pitches on each client page; send them yourself from your own inbox, a few a day.
  Offer the Starter package (4 videos). Track replies in the pipeline board.
- Add affiliate links to posts where they are genuinely relevant. The guardrails block a post that has
  an affiliate link without a disclosure.
- Log every payout on the Revenue page (or import the CSV exports). Log costs too, so the P&L is honest.

## Days 61 to 90: double down

- `factory insights --brand <slug> --rescore` shows which formats, pillars and posting hours work, and
  pushes similar ideas up the backlog. Make more of those, drop the bottom third.
- Once you pass about 1,000 followers, build a small product (`factory product ...` from the business
  CLI) and add it to the link in bio.
- Consider a second brand only if the first runs in under 30 minutes a day.

## Numbers to watch

| Metric | Healthy | Action if not |
|---|---|---|
| Review time per post | under 5 minutes | Tighten the brand YAML voice and pillars |
| Short-form average view % | 60%+ | Stronger hooks; cut the first sentence |
| Save rate on carousels | 2%+ | More checklist / reference style slides |
| Link clicks per 1k views | 1+ | Clearer CTA, better offer fit |
| Revenue per hour of your time | rising month on month | Shift time to the line that pays (usually UGC) |

## What not to do

No bought followers, engagement pods, follow-for-follow, or multiple accounts per niche to game reach.
No reposting other creators' clips. No real person's face or voice without a signed licence. No AI
presenter claiming they used a product. These get accounts removed and some are illegal (FTC rule on
fake reviews: up to $51,744 per violation).
