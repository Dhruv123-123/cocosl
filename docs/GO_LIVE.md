# Go live: the one checklist

Written 2026-11-07 for Dhruv, refreshed the same night after the round-2 work landed on `main`. This merges
every "only you can do this" step from `docs/CREDENTIALS.md`, `docs/QUICKSTART.md`, `docs/DEPLOY.md`,
`launch/LAUNCH_DAY.md`, `launch/VERIFY_BEFORE_POSTING.md`, the open PRs (#1–#6), the round-2 commits on `main`
and the project files in `content-factory/`, with the duplicates removed. Everything else is already built.

It's ordered by **fastest path to first revenue**: the ad studio can pay this month, products can sell as
soon as there's traffic, affiliates and platform money come later. Times are hands-on time, not waiting time.
Where something has a waiting period (verification, affiliate approval), start it early and keep going.

Totals: **Stage 1–3 ≈ 5–6 hours** gets you able to take money. All stages ≈ 12–15 hours spread over two weeks.

Nothing in this repo sends, posts or charges on its own. You press every button.

---

## Stage 0 · Merge the PRs (15 min, do first)

Merge in this order (details in [PR merge order](#pr-merge-order) at the bottom):
**#1 → #3 → #2 → #4 → #5 → #6 → this PR.**

- [ ] Merge the PRs in that order on GitHub (≈ 2 min each). 10 min

---

## Stage 1 · Identity and getting paid (≈ 1 h 15 min, tonight)

Verification can take a day or two, so start these first.

- [ ] **Business email** for both lines (new Gmail or your own domain), with 2FA on. 10 min
- [ ] **Postal address you're OK publishing** (PO box or virtual mailbox; US virtual mailboxes need USPS
      Form 1583 and take a few days). CAN-SPAM needs it on every cold email and newsletter. Until you have one,
      pitch by Instagram DM only and hold the cold emails. 10 min to order
- [ ] **Gumroad** (or Lemon Squeezy): sign up, verify identity, add payout bank, tax form (W-9 / W-8BEN). 20 min
- [ ] **Stripe** and/or **PayPal Business** for ad-studio invoices: verify identity, add bank, tax form. 25 min
- [ ] **2FA** on Gumroad, Stripe, PayPal and every social account you make later. 10 min
- [ ] Write down once: your name, studio name, email, postal address, city. You'll paste them everywhere.

## Stage 2 · Ad studio: the fastest money (≈ 2 h, then 1 h a day)

One Starter order ($249) covers about six months of lean running costs (`docs/FINANCIAL_MODEL.md`).
The 76 leads and pitches are already written in `content-factory/ai-ad-studio-v2/`.

- [ ] Pick a studio name and check it isn't someone's trademark (web search + trademark search). 10 min
- [ ] Edit the `STUDIO` block at the top of `launch/ugc-service/index.html` (name, email, owner, location). 5 min
- [ ] Publish it free: drag the folder onto app.netlify.com/drop, sign up, rename the site. Test the form on
      your phone. 15 min
- [ ] Optional: host `content-factory/ugc-portfolio/portfolio.html` the same way and put its URL in
      `STUDIO.portfolio`. 10 min
- [ ] Studio Instagram (business/creator), bio "AI video ads for small brands · clearly labeled AI · free
      sample", link the site. 15 min
- [ ] Choose one AI video tool whose terms allow commercial ads, and make a 10-second test so you know the
      workflow before someone says yes. 30 min
- [ ] Invoice template: 50% deposit, terms from `launch/ugc-service/RATE_CARD.md`. 10 min
- [ ] In `.env`: `FACTORY_PORTFOLIO_URL` (the hosted portfolio) and `FACTORY_PAYMENT_INSTRUCTIONS`
      (e.g. "Pay by the Stripe link in the invoice email"), so the factory's proposals and onboarding drafts
      fill in correctly. 5 min
- [ ] **From Tue Nov 10: send 15 first emails a day** from `ai-ad-studio-v2/pitches/` (highest rank first),
      compliance footer under each, from your own inbox. Log dates in `TRACKER.csv`. Follow-ups on day 4 and
      day 11, per `FOLLOW_UP_SEQUENCE.md`. ≈ 1 h/day
- [ ] Anyone who says stop → `do_not_contact` in `leads.csv`, never contact again.

## Stage 3 · Sell the six products on Gumroad (≈ 2 h)

Needs PR #6 merged. Files are in `content-factory/products/` and `launch/products/dist/`.

- [ ] Create the 6 products from each `LISTING.md`: The 20-Minute Budget $12, Bill Cut Kit $5,
      Credit Report Audit Kit $9, Debt-Free Date Planner $17, Start Investing With $100 a Month $19,
      Money Made Simple Toolkit bundle $39. Upload each zip and cover. ≈ 10 min each, 60 min
- [ ] **Create the discount codes before the first sale** (they're printed inside the PDFs).
      Gumroad > Checkout > Discounts, each restricted to one product, unlimited uses, no expiry. 15 min

      | Code | $ off | Valid on |
      |---|---|---|
      | `BILLCUT5` | 5 | The 20-Minute Budget |
      | `BUDGET5` | 5 | The Debt-Free Date Planner |
      | `AUDIT5` | 5 | The Debt-Free Date Planner |
      | `DEBTFREE5` | 5 | Start Investing With $100 a Month |
      | `INVEST5` | 5 | The 20-Minute Budget |
      | `LAUNCH` | per LISTING.md | each product, **ending 2026-11-14** (the welcome emails on `main` print that date) |

- [ ] Upsells (one per product), per `launch/products/UPSELL_PATH.md` step 3. 10 min
- [ ] Post-purchase workflow email 3 days after each purchase (drafts in `UPSELL_PATH.md`). 15 min
- [ ] Replace `[your store link]` in each `launch/products/<slug>/guide.html`, run
      `python launch/products/build.py --check`, re-upload the zips. (Or ask a thread to do it; just give it
      the store URL.) 15 min
- [ ] 100%-off code for yourself, **test-buy one product**, check download and thank-you email. 5 min
- [ ] Remember the bundle promise: anyone who emails a receipt gets a single-use code for what they paid.

## Stage 4 · Money Made Simple accounts and first posts (≈ 1 h 15 min)

- [ ] Create Instagram, YouTube and TikTok as `@moneymadesimple` (or the nearest free handle; update
      `brands/money-made-simple.yaml` if it differs). Instagram → Professional (Creator/Business), linked to a
      Facebook Page. 30 min
- [ ] Upload the brand kit from `content-factory/launch-pack/brand-kit/` (profile picture, banner, watermark,
      bios from `bio-pack.txt`). Verify the YouTube channel by phone (custom thumbnails). 20 min
- [ ] **Before each post, tick `launch/VERIFY_BEFORE_POSTING.md`:** the real HYSA APY (scripts use an
      illustrative 3.5%), that the linked bank is FDIC-insured with no monthly fee, take-home pay and tax
      estimates, the student-loan autopay discount and HSA/FSA limits. 15 min once, then 2 min per piece
- [ ] Post by hand from `content-factory/launch-pack/POSTING_PLAN.md` (Nov 7–20): carousels are ready now;
      videos wait for a voice (Stage 6). Check every number, keep the AI disclosure, switch on the
      platform AI label. 10 min/post
- [ ] `SUPPORT_EMAIL` in `.env` (reply-to on the factory's welcome emails and sales pages). 2 min
- [ ] Month 1 (Nov 21 – Dec 20) follows `content-factory/month-1/POSTING_PLAN.md`; import `calendar.ics`
      into your calendar. 5 min

## Stage 4b · Second brand: Tiny Histories (optional, ≈ 1 h)

On `main` already: 24 launch pieces and `launch/tiny-histories/POSTING_PLAN.md` (Nov 7–20, 17:00 ET daily,
YouTube + Instagram). No product or affiliate links yet, so it earns only from views later. Do it after
Money Made Simple is posting, not before.

- [ ] Create its YouTube and Instagram accounts with the handles in `brands/tiny-histories.yaml`. 30 min
- [ ] Open the four source links listed under Tiny Histories in `launch/VERIFY_BEFORE_POSTING.md` and keep
      CONTESTED/LEGEND/UNPROVEN stories worded as uncertain. 20 min
- [ ] Don't add a product link until its PDF exists.

## Stage 5 · Website and email funnel (≈ 1 h 30 min)

Needs PR #4 merged. Turns followers into an email list that sees the products 3 times.

- [ ] Netlify > Add new site > Import from GitHub > `cocosl`. It reads `netlify.toml`; click Deploy, rename the
      site. Forms > Enable form detection, redeploy. 15 min
- [ ] Pick an email provider (MailerLite, Kit or Buttondown; check the current free tier). Turn on double
      opt-in, put your **postal address in the footer**. Paste its form action into `site/site.json` > `email`
      (or set `EMAIL_PROVIDER` / `EMAIL_FORM_ACTION`). 20 min
- [ ] Fill `site/site.json`: `url`, `contact_email`, `socials`. Set each product's real Gumroad `buy_url` in
      `site/content/products/*.md` and delete `status: coming-soon` once it's live. Replace
      `example.gumroad.com` and `link_in_bio: https://example.com/links` in `brands/money-made-simple.yaml`.
      (A thread can do these edits if you send it the URLs.) 15 min
- [ ] Rebuild with the real URL (`SITE_URL=https://your-site python3 site/build.py`), then build the 10-email
      automation in your provider from `site/public/emails/` (days 0, 1, 3, 5, 7, 9, 12, 15, 18, 21; skip the
      pitch emails for buyers). 30 min
- [ ] Put `https://your-site/links/` in every profile's link in bio. 5 min
- [ ] Submit `sitemap.xml` to Google Search Console and Bing Webmaster Tools. 10 min

## Stage 6 · Voice and writing keys (≈ 45 min)

Needs PR #2 merged. Unlocks the 16 launch videos and 26 month-1 videos waiting in `videos-need-voice/`.

- [ ] **Free voice (Kokoro):** `docker compose --profile voice up -d kokoro`, then in `.env`
      `KOKORO_URL=http://localhost:8880/v1` (`http://kokoro:8880/v1` inside compose). Or pay for ElevenLabs
      with **your own** cloned voice. 15 min
- [ ] `ANTHROPIC_API_KEY` from console.anthropic.com (prepay $5–10). Without it new drafts are placeholders. 5 min
- [ ] `factory status` to confirm, then re-render: `factory rerender <id>` per short, or re-export month 1 with
      `--render-video`. Review and approve in the dashboard (`factory serve`). 20 min
- [ ] Optional: `FACTORY_MUSIC_DIR` with tracks you hold a licence for.

## Stage 7 · Affiliate networks (≈ 1 h; approval takes days)

- [ ] **This week:** apply to **Impact** and **CJ Affiliate** (one application each unlocks most programs). 30 min
- [ ] **After ~10 posts are live and the site is up:** apply to SoFi, CIT Bank, Empower, Rocket Money, Monarch,
      Aura, Acorns (list and payouts in `research/02-affiliate-programs.md`). Only ones you'd recommend to a friend.
      Treat brokerage links (Robinhood, M1, Betterment) as needing compliance review. 30 min
- [ ] As each is approved: replace the "Example HYSA" entry under `affiliates` in
      `brands/money-made-simple.yaml`, run `factory links sync`, and add it to `site/site.json` > `affiliates`. 5 min each

## Stage 8 · Automation and a server (≈ 2–3 h, when manual posting gets tedious)

Manual posting is fine for the first weeks. Do this when it isn't.

- [ ] **Instagram token:** Meta developer app (Facebook Login for Business + Instagram + Threads), add the
      permissions in `docs/CREDENTIALS.md` §6 (now including `instagram_manage_comments` for the comment inbox,
      which needs App Review for Advanced Access), Graph API Explorer token, then
      `factory auth meta --token <token>`. Add `META_APP_ID`, `META_APP_SECRET`. Optional `IG_TRIAL_REELS=SS_PERFORMANCE`.
      This token also runs `research/scouting/watchlist.py`. 45 min
- [ ] **YouTube:** Cloud project, YouTube Data API v3, OAuth consent (you as test user) with scopes
      `youtube.upload`, `youtube.readonly`, `youtube.force-ssl` (comment replies), Desktop client,
      `factory auth youtube`. Optional `YT_CHANNEL_ID` and `IG_USERNAME` so the inbox skips your own comments. Testing-mode tokens expire every 7 days. 30 min
- [ ] **TikTok:** developer app with Login Kit + Content Posting API, `factory auth tiktok`, submit the audit
      (posts are private until it passes; post from the app meanwhile). 30 min
- [ ] **Server:** a $5–10 VPS + domain, follow `docs/DEPLOY.md` (Caddy, `DASHBOARD_TOKEN`,
      `PUBLIC_MEDIA_BASE_URL`, `FUNNEL_PUBLIC_URL`). 45 min
- [ ] Webhooks: Stripe → `/webhooks/stripe`; Gumroad ping → `/webhooks/gumroad?secret=...`. 10 min
- [ ] Sender identity in `.env`: `FACTORY_SENDER_*`, `BUSINESS_ADDRESS`; SMTP if the server sends newsletters. 10 min
- [ ] Keep `FACTORY_DRY_RUN=1` until `factory status` is green and one manual test post looks right, then set `0`.

## Every week after that

- Monday: `factory report`, do its "Next actions". 20 min
- Daily: 15 pitches + follow-ups, 2 approved posts, reply to comments (the dashboard's `/inbox` drafts
  replies once platforms are connected; you send them). ≈ 1.5 h

---

## PR merge order

Checked 2026-11-07 against `main` after the round-2 commits (welcome sequences, comment inbox, site export,
Tiny Histories). In this order, #1, #3, #2, #4 and this PR merge cleanly and all tests pass.
**#5 and #6 now have one small conflict each with `main`** and need a rebase before they can merge:

- #5: `src/contentfactory/cli.py`, the list of command modules (keep both: `community.cli`, `site` and `pack`).
- #6: `brands/money-made-simple.yaml`, the `products:` list (keep #6's six products, plus `main`'s `slug:` field).

The threads that opened them are being asked to fix this; this table gets updated when they're green.

| # | Merge | Why here |
|---|---|---|
| 1 | **#1** Research: competitors, affiliates, hooks, next niches | docs only (`research/`), no risk |
| 2 | **#3** Financial model | docs only (`docs/FINANCIAL_MODEL.md`) |
| 3 | **#2** Scouting, Kokoro voice, Instagram Trial Reels | code; touches voice and the IG publisher, nothing the later PRs touch |
| 4 | **#4** Website, lead magnet, 10-email funnel | adds `site/` and `netlify.toml`; must land before #6 |
| 5 | **#5** Month 1 pack and `factory pack` | after its rebase; edits `README.md` like #4, which Git merges cleanly |
| 6 | **#6** Product line | after its rebase; adds product pages under `site/content/products/`, which need #4's site |
| 7 | **#7** This go-live checklist | docs only; any time |

If a new PR lands, merge it after these unless its description says otherwise.
