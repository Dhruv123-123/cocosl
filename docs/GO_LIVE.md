# Go live: the one checklist

Written 2026-11-07 for Dhruv and refreshed through the evening (last pass 09:50 UTC: PRs #1–#12 and `main` at
`d56189e`; newer `main` commits may need each PR to bring it in again). This merges every "only you can do this" step from `docs/CREDENTIALS.md`, `docs/QUICKSTART.md`,
`docs/DEPLOY.md`, `launch/LAUNCH_DAY.md`, `launch/VERIFY_BEFORE_POSTING.md`, the open PRs, the commits on `main`
and the project files in `content-factory/`, with the duplicates removed. Everything else is already built.

It's ordered by **fastest path to first revenue**: the ad studio can pay this month, products can sell as
soon as there's traffic, affiliates and platform money come later. Times are hands-on time, not waiting time.
Where something has a waiting period (verification, affiliate approval), start it early and keep going.

Totals: **Stage 1–3 ≈ 5–6 hours** gets you able to take money. Stages 0–8 (one brand, fully live)
≈ 13–16 hours over two weeks. Stage 9 adds the other brands, one at a time, ≈ 2–4 hours each. The
[launch runbook](#launch-runbook-after-the-merges) near the end covers the sites, placeholders, first-week
posts, recording sessions, a 15-minutes-a-day routine, each brand's launch day and a weekly scorecard once everything is merged.

Nothing in this repo sends, posts or charges on its own. You press every button.

### Decisions only you can make (5 minutes, before Stage 4)

Each one has a default, so nothing waits on these. Change a default only if you want to.

| Decision | Default | To change it |
|---|---|---|
| Money Made Simple Day 1 | **Mon Nov 16** | `python scripts/launch_week.py --day1 YYYY-MM-DD` (PR #5) rewrites `launch/money-made-simple/LAUNCH_WEEK.md` |
| The savings challenge's Sun Nov 15 kickoff, which falls before Day 1 | post it on Day 1 at 19:00 on TikTok | or drop it |
| Scam Decoded Day 1 | **Mon Nov 30** (Cyber Monday, MMS day 15); Mon Nov 23 is the earlier option | the Day 1 line in `launch/scam-decoded/LAUNCH_WEEK.md` (PR #9) |
| Site domain | the Pinterest pins say `.co`, the links go to `.netlify.app` | buy the domain before the first pin, or edit the pins to the Netlify URL |
| Brand 3 | 1099 Money once the five Stage 9 gates pass (around Jan 10) | see Stage 9 |
| B2B cold email (PR #13) | parked | say yes to start it; pitching is timed to late Jan for NCPW |

---

## Stage 0 · Merge the PRs (15 min, do first)

Merge in this order (details and current blockers in [PR merge order](#pr-merge-order) at the bottom):
**#1 → #3 → #2 → #4 → #5 → #6 → #8 → #12 → #11 → #9 → #10 → #7.**

- [ ] Merge the ones marked ✅ in that order on GitHub (≈ 2 min each). Right now that's **#1, #3, #2, #4, #5,
      #6, #8, #12, #11, #7**: checked together on top of `main`, all tests pass. Skip the rest until GitHub shows them
      green; the threads that opened them are fixing them. 15 min

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
- [ ] Optional: host `content-factory/ugc-portfolio/portfolio.html` the same way (PR #12 adds 10 more sample
      ads and links them from the studio site), put its URL in `STUDIO.portfolio` and `FACTORY_PORTFOLIO_URL`. 10 min
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

**Sell PR #6's six products, nothing else, for Money Made Simple.** `main` also has an older ladder in
`launch/products/PRODUCT_LADDER.md` (Debt Payoff Planner $9, First Investing Account Kit $15, Starter Bundle
$24). It's being moved to an archive; don't list those on Gumroad.

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

### 3b · Etsy shop (PR #6, ≈ 2 h 15 min): buyers already searching for printables
- [ ] Open the shop at etsy.com/sell (name MoneyMadeSimple or closest), icon from the brand kit, About and
      policies text from `launch/etsy/SHOP_SETUP.md`, sections, thank-you coupon (20%) and abandoned-cart /
      favourites coupons (10%). Opt out of Offsite Ads while small. 45 min
- [ ] List the 17 items: 3 mockups, title/price/tags/description from each `LISTING.md`, the digital files.
      US fees: $0.20 per listing plus 6.5% + 3% + $0.25 per sale. 5 min each, ≈ 1 h 25 min
- [ ] Later, for 1099 Money (PR #10): its Etsy listings are in `launch/1099-money/etsy/`.

## Stage 4 · Money Made Simple accounts and first posts (≈ 1 h 15 min)

- [ ] Create Instagram, YouTube and TikTok as `@moneymadesimple` (or the nearest free handle; update
      `brands/money-made-simple.yaml` if it differs). Instagram → Professional (Creator/Business), linked to a
      Facebook Page. 30 min
- [ ] Upload the brand kit from `content-factory/launch-pack/brand-kit/` (profile picture, banner, watermark,
      bios from `bio-pack.txt`). Verify the YouTube channel by phone (custom thumbnails). 20 min
- [ ] **Before each post, tick `launch/VERIFY_BEFORE_POSTING.md`:** the real HYSA APY (scripts use an
      illustrative 3.5%), that the linked bank is FDIC-insured with no monthly fee, take-home pay and tax
      estimates, the student-loan autopay discount and HSA/FSA limits. 15 min once, then 2 min per piece
- [ ] Post by hand from `launch/money-made-simple/LAUNCH_WEEK.md` (PR #5): Days 1–14 from Day 1 (default
      Mon Nov 16), each platform at its own time, plus bios, pins and the first 8 Pinterest pins. Carousels are
      ready now; videos wait for a voice (Stage 6). Check every number, keep the AI disclosure, switch on the
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
The one-page version, with every blank and what happens until it's filled, is `site/SITE_START_HERE.md`.

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
- [ ] Scheduled articles: Netlify > Build hooks > add one, then put its URL in the GitHub secret
      `NETLIFY_BUILD_HOOK`. The scheduled rebuild only deploys on days something publishes (8–13 a month,
      69 in 2027, about 120–195 of Netlify's 300 free credits), and pushes that don't touch `site/` are skipped. 5 min
- [ ] Optional 7-day Money Basics course (PR #4): `factory sequence-export money-made-simple --sequence
      money-basics --for sender`, then turn that automation on in your provider (signup source
      `money-basics-7-days`). 15 min

## Stage 6 · Voice and writing keys (≈ 45 min)

Kokoro is now built into `main`, so this no longer waits on PR #2. Unlocks the 16 launch videos and
26 month-1 videos waiting in `videos-need-voice/`.

- [ ] Run `factory doctor` first: it checks ffmpeg, storage, brands, keys, voice and the media URL and says
      what to fix. 5 min
- [ ] **Free voice (Kokoro):** on a laptop `docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:v0.2.4`
      and `KOKORO_URL=http://localhost:8880`; on the server `docker compose --profile kokoro up -d` and
      `KOKORO_URL=http://kokoro:8880`. Pick `KOKORO_VOICE` (e.g. `af_heart`). Or pay for ElevenLabs with
      **your own** cloned voice. 15 min
- [ ] `ANTHROPIC_API_KEY` from console.anthropic.com (prepay $5–10). Without it new drafts are placeholders. 5 min
- [ ] Re-voice everything rendered silent in one go: `factory renderq revoice` (add `--include-approved`
      for approved posts; they go back to review). With Docker the renderer picks the jobs up; otherwise run
      `factory renderq run`. `factory status` shows progress. Review and approve in the dashboard (`factory serve`). 20 min
- [ ] Optional: `FACTORY_MUSIC_DIR` with tracks you hold a licence for.

## Stage 7 · Affiliate networks (≈ 1 h; approval takes days)

- [ ] **This week:** apply to **Impact** and **CJ Affiliate** (one application each unlocks most programs). 30 min
- [ ] Use the application kit from PR #5: `python3 launch/affiliates/kit.py` builds `APPLICATIONS.md`
      (ready answers for all four brands, 31 programs) and `applications.csv` to track them. Fill the
      [BRACKETS] with real numbers only. Approved links go in `site/go-links.json`. Saves ≈ 15 min per application
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
- [ ] **TikTok: nothing to connect.** TikTok doesn't allow tools to post to your own accounts, so the worker
      writes a post-by-hand package (video, caption, time). Post it from `factory ui` → Post by hand (or
      `factory manual`) with the AI-generated label on, then mark it posted. 5 min per post
- [ ] **Server:** a $5–10 VPS + domain, follow `docs/DEPLOY.md` (Caddy, `DASHBOARD_TOKEN`,
      `PUBLIC_MEDIA_BASE_URL`, `FUNNEL_PUBLIC_URL`). 45 min
- [ ] Webhooks: Stripe → `/webhooks/stripe`; Gumroad ping → `/webhooks/gumroad?secret=...`. 10 min
- [ ] Backups: `BACKUP_DIR=/data/backups` and the worker backs up the database daily. 2 min
- [ ] Sender identity in `.env`: `FACTORY_SENDER_*`, `BUSINESS_ADDRESS`; SMTP if the server sends newsletters. 10 min
- [ ] Run `factory launch-check` (add `--online` to test every real link). Keep `FACTORY_DRY_RUN=1` until it's
      **green** and one manual test post looks right, then set `0`. Yellow usually means placeholder links in
      `brands/<slug>.yaml`; red names the post to fix. 10 min

## Stage 9 · More brands, one at a time (Scam Decoded in week 2; brand 3 only after the gates)

Each brand repeats Stage 4 (accounts, brand kit, first posts) and the relevant parts of 3, 5 and 7. Each
brand gets its own accounts: run the auth commands with `--brand <slug>` (e.g.
`factory auth youtube --brand scam-decoded`) and the tokens are saved under that brand's name. Do one
brand properly before starting the next.

Order (suggested by `research/scouting/two-brand-launch-plan.md` on PR #2, which replaces the 1099 + MMS week-1
order in `launch-playbook.md`): **9b Scam Decoded and 9a free apps in week 2** (Mon Nov 23; the scam checker is
the Scam site's lead tool), Scam posts at half cadence from week 3. **Brand 3 is 9d 1099 Money**, and only when
all five gates below pass (checked at the end of week 8, around Jan 10). When they pass, set `launch_stage` to
`"brand-3"` in `site/site.json` so the homepage lists 1099 Money next to Scam Decoded. **9c Dinero Simple comes last**, once a
paid Spanish reviewer is booked.

Brand-3 gates (all five must pass):
1. Both brands take under 1 h a day combined, for 4 weeks.
2. No account warnings for 4 weeks.
3. No open "change" rule in `check_thresholds.py` for 2 weeks.
4. 2 weeks of approved posts are queued.
5. The email list is growing on both brands.

Steady state with two brands is about 9–10 h a week: R6 (about 3.5 h across both), ad studio (about 3.75 h),
the Monday report (0.5 h) and Saturday recording (1–1.5 h).

### 9a · Free web apps (PR #8, ≈ 1 h): search traffic with no audience needed
- [ ] Netlify > Add new site > Import `cocosl`, base directory `apps` (one site), or one site each for
      `apps/money-calculators`, `apps/scam-checker`, `apps/budget`. Forms > enable form detection. 15 min
- [ ] Put real URLs in each `config.js` (`siteUrl`, `calculatorsUrl`) and run `node money-calculators/build.mjs`. 10 min
- [ ] Budget app Pro ($3/month or $29 once): one Gumroad product with monthly and lifetime variants and
      "Generate a unique license key" ticked; checkout links in `apps/budget/config.js`; `GUMROAD_PRODUCT_ID`
      env var on Netlify (or a Stripe Payment Link + restricted `STRIPE_SECRET_KEY`). 20 min
- [ ] Replace `REPLACE_ME` links (product URLs, approved affiliates) as they become real; they stay hidden
      until then. Brokerage offers are flagged for compliance review. 5 min each
- [ ] Optional: Chrome Web Store developer account ($5 one-time), then upload the scam extension zip using
      `apps/scam-extension/STORE.md`. 30 min

### 9b · Scam Decoded (PR #9, ≈ 2 h): $9 Family Scam-Proofing Kit
- [ ] Check `@scamdecoded` is free on Instagram, TikTok and YouTube, then create the accounts. 30 min
- [ ] Gumroad product for the kit from `launch/scam-decoded/product/LISTING.md`. This is the only scam kit. 15 min
- [ ] Deploy `sites/scam-decoded/` on Netlify; set `product.buy_url`, `scam_checker.url` (the #8 checker),
      and the email provider. Load its 7-email sequence. 40 min
- [ ] Affiliates: Aura on Impact, 1Password on FlexOffers, NordVPN direct, once the account has posts. 20 min
- [ ] Before posting: no real phone numbers or links on any slide; update figures flagged in its README.
- [ ] A long video uploads only after its recording in `LONG_VIDEO_RECORDINGS.md` is done (R5).

### 9c · Dinero Simple, Spanish (PR #11, ≈ 3 h plus a reviewer)
- [ ] **Find a fluent Spanish reviewer first.** Nothing goes live until they've read it: posts are blocked
      until `factory review-gate pass <id> native_review --by NAME`, and the site, emails and products are listed in
      `launch/dinero-simple/REVIEW_CHECKLIST.md` and `REVIEW_CHECKLIST_MONTH_1.md`. Their time, not yours.
- [ ] Accounts and brand kit from `brands/dinero-simple.yaml`. 30 min
- [ ] Gumroad: El Presupuesto de 20 Minutos $12, El Kit para Recortar Gastos $5, Tu Fecha Sin Deudas $17. 30 min
- [ ] **Discount codes `RECORTE5` and `FECHA5`**, each $5 off El Presupuesto de 20 Minutos (the guides
      promise them). 5 min
- [ ] Deploy `sites/dinero-simple/` (its own `netlify.toml`), set the email provider, load the 10 emails. 40 min
- [ ] Spanish voice: set `PIPER_MODEL_ES` (or a Spanish Kokoro/OpenAI voice), never the English one. 10 min

### 9d · 1099 Money, freelancers (PR #10, ≈ 2 h): $15 Quarterly Tax Tracker
- [ ] Accounts from `brands/1099-money.yaml`; its posting plan starts **when the brand-3 gates pass** (its
      dates are written from Nov 16; shift them). 30 min
- [ ] Gumroad product from `launch/1099-money/product/LISTING.md` ($15). 15 min
- [ ] Deploy `apps/freelance-tax/` (calculator + Tax Calendar lead magnet), set `siteUrl`, product URL and the
      7-email sequence. 40 min
- [ ] Confirm the 2026 figures and 2027 dates against irs.gov, ssa.gov and healthcare.gov before posting. 30 min
- [ ] Affiliates (FreshBooks, QuickBooks, Gusto, TaxAct, Lively on Impact/CJ; Novo on PartnerStack). 20 min

## Every week after that

- Monday: `factory report`, do its "Next actions". 20 min
- Daily: 15 pitches + follow-ups, 2 approved posts, reply to comments (the dashboard's `/inbox` drafts
  replies once platforms are connected; you send them). ≈ 1.5 h

---

## Launch runbook (after the merges)

Run this once the PRs are merged. It assumes Stages 1–3 (payments, ad studio, Gumroad) are done, because
almost every placeholder below is a Gumroad or affiliate URL. Times are hands-on.

### R1 · Netlify sites to create (≈ 1 h 15 min)

Each is Netlify > **Add new site > Import an existing project > GitHub > `cocosl`**, then the base
directory below. Turn on **Forms > Enable form detection** and redeploy once on every site that collects
emails. Rename each site (or add a domain) and write the URL down; R2 needs them.

| # | Site | Base directory | PR | Collects emails | Notes | Time |
|---|---|---|---|---|---|---|
| 1 | Money Made Simple website | repo root (reads `netlify.toml`: base `site`) | #4 | yes | the main funnel, `/links/` is the link-in-bio page | 10 min |
| 2 | Ad studio site + order page | `launch/ugc-service` (or drag it onto app.netlify.com/drop) | #12 | inquiry form | edit the `STUDIO` block first | 10 min |
| 3 | Web apps, one site | `apps` (reads `apps/netlify.toml`) | #8 | yes | calculators, scam checker, budget app (needs Functions), ad script builder, invoices, medical bills. Or split them as in 3a–3c | 15 min |
| 3a | Calculators (optional own site) | `apps/money-calculators` | #8 | yes | better SEO on its own domain | 5 min |
| 3b | Scam checker (optional own site) | `apps/scam-checker` | #8 | yes | then run `node scam-checker/rename-brand.mjs "Scam Decoded" <url>` | 5 min |
| 3c | Budget app (optional own site) | `apps/budget` | #8 | no | env vars `GUMROAD_PRODUCT_ID` and/or `STRIPE_SECRET_KEY` (restricted, read-only) | 10 min |
| 4 | Scam Decoded funnel | `sites/scam-decoded` | #9 | yes | | 10 min |
| 5 | Dinero Simple website | `sites/dinero-simple` | #11 | yes | only after the Spanish review | 10 min |
| 6 | 1099 Money calculator + funnel | `apps/freelance-tax` | #10 | yes | | 10 min |

After every site is up, submit each one's `sitemap.xml` in Google Search Console (one property per site). 15 min

### R2 · Placeholders to fill (≈ 1 h 30 min)

`factory triage` and `factory launch-check` list most of these for you (see R4). Fill them, then rebuild
or redeploy. Leave affiliate slots empty until a program approves you; empty slots stay hidden.

| Where | What to put in | Comes from |
|---|---|---|
| `.env` | `ANTHROPIC_API_KEY`, `KOKORO_URL` (or a voice key), `PUBLIC_MEDIA_BASE_URL`, `DASHBOARD_TOKEN`, `SUPPORT_EMAIL`, `FACTORY_PORTFOLIO_URL`, `FACTORY_PAYMENT_INSTRUCTIONS`, `FACTORY_SENDER_*`, `BUSINESS_ADDRESS`, `BACKUP_DIR` | Stages 6 and 8 |
| `.env` (platform tokens) | written by `factory auth youtube` and `factory auth meta --token …`; add `--brand <slug>` for each extra brand's own accounts | Stage 8 |
| `brands/money-made-simple.yaml` | `link_in_bio` (site 1 + `/links/`), `products[0–5].url` (the six Gumroad links), `affiliates[0].url` (first approved HYSA) | Stage 3, site 1 |
| `brands/tiny-histories.yaml` | `products[0].url` stays a placeholder until its PDF exists; it shows yellow, which is fine | |
| `brands/scam-decoded.yaml`, `dinero-simple.yaml`, `1099-money.yaml` | each brand's product and affiliate URLs, link in bio | Stage 9 |
| `site/site.json` + `site/content/products/*.md` | `url`, `contact_email`, `socials`, `email` provider, each `buy_url`; delete `status: coming-soon` once live | site 1, Gumroad |
| `site/go-links.json` | approved affiliate tracking links (the 20 affiliate articles read from here) | Stage 7 |
| `launch/products/<slug>/guide.html` | `[your store link]` on the last page, then `python launch/products/build.py --check` and re-upload | Gumroad |
| `launch/ugc-service/index.html` | the `STUDIO` block (name, email, owner, location, portfolio) | Stage 2 |
| `apps/*/config.js` | `siteUrl`, `calculatorsUrl`, `email`, `product.url`, `affiliates` / `offers` (every `REPLACE_ME`), then `node money-calculators/build.mjs` | sites 3–3c |
| `sites/scam-decoded/site.json` | `product.buy_url`, `scam_checker.url` (site 3 or 3b), `email` | site 4 |
| `sites/dinero-simple/site.json` + `content/products/*.md` | `url`, `email`, the three Spanish `buy_url`s | site 5 |
| `apps/freelance-tax/config.js` | `siteUrl`, tracker product URL, affiliate links, email placeholders | site 6 |
| Email provider footer (each list) | your postal address (CAN-SPAM) | Stage 1 |

### R3 · First week of posts, per brand

Each plan is dated from Sat Nov 7; if you start later, keep the order and shift the dates. Before each
post: tick its facts in Review (and `launch/VERIFY_BEFORE_POSTING.md`), keep the AI disclosure, and turn on
the platform AI label. TikTok always goes up by hand from `factory ui` → Post by hand.

**Start Money Made Simple first and alone for at least a week.** Add one brand a week after that, in the
order below, so you're never learning two sets of accounts at once.

- **Money Made Simple** (`launch/money-made-simple/LAUNCH_WEEK.md`, the source of truth; Shorts 12:30 on
  YouTube/IG/FB and 18:00 on TikTok, carousels 19:00 on Instagram and 11:00 on Pinterest, long videos 19:00):
  with the default Day 1 of Mon Nov 16: Day 1 short *Stop overdraft fees: the two-account trick* + carousel
  *The 20-minute monthly money date* · Day 2 short *Freeze your credit for free tonight* + long *How to get your
  finances in order: a 30-day money reset* · Day 3 short *Budget weekly, not monthly* + carousel *$1,000
  emergency fund in 8 weeks* · Day 4 short *401(k) match explained: the raise you're ignoring* · from Fri Nov 20
  the dated packs take over (Black Friday add-on, then month 1 from Nov 21).
- **Tiny Histories** (`launch/tiny-histories/POSTING_PLAN.md`, 17:00 ET, one post per platform per day):
  Day 1 long *Why your keyboard says QWERTY* + carousel *Jeans exist because of a $68 patent fee* ·
  Day 2 short *OK started as a misspelled joke* · Day 3 long *The fork was a scandal for 600 years* +
  carousel *Where the dollar sign came from* · Day 4 short *The barcode was drawn in the sand* ·
  Day 5 long *The Earl of Sandwich didn't invent the sandwich* + carousel *Nobody wanted the first shopping cart* ·
  Day 6 short *The glue that was too weak (Post-it)*.
- **Scam Decoded** (`launch/scam-decoded/LAUNCH_WEEK.md` on PR #9, the source of truth): Day 1 is your call,
  default **Mon Nov 30** (Cyber Monday, MMS day 15), with Mon Nov 23 as the earlier option. Day 1 is the channel
  trailer (face cam, script in the file) plus the long *How to protect your parents from scams*. Week 1 runs at
  half cadence on purpose. Anything dated before Day 1 is skipped, and the dated packs and 08:30 alert cards
  resume from day 15. Bios, pins and every claim's source are in the same file.
- **1099 Money** (`launch/1099-money/POSTING_PLAN.md`, written from Mon Nov 16 but held until the brand-3 gates pass (Stage 9), 12:30 and 19:00 ET):
  Day 1 short *Your first 1099 has no tax taken out* + carousel *$60K freelance income: what you actually owe* ·
  Day 2 short *The 15.3% tax nobody warned you about* · Day 3 short *Made $400 on the side? Read this* +
  carousel *The freelancer tax calendar for 2027* · Day 4 short *No 1099? You still owe tax on it* ·
  Day 5 short *The tax deadline after New Year's* + carousel *Work out your quarterly payment in 5 steps* ·
  Day 6 short *The rule that kills the underpayment penalty*.
- **Dinero Simple** (`launch/dinero-simple/POSTING_PLAN.md`, 12:30 and 20:00 ET): the same order as Money
  Made Simple in Spanish (Day 1 *El truco de las dos cuentas que evita sobregiros* + carrusel *Tu cita
  mensual de 20 minutos con tu dinero*, and so on). **Nothing posts until the fluent reviewer signs off.**
- **Ad studio** (`content-factory/ai-ad-studio-v2/CONTENT_PLAN_4_WEEKS.md`, Mon–Fri from **Mon Nov 16**):
  posts 1–3 and 5 are ready in `social-posts/`; post 4 needs a screen recording (see R5).

### R4 · What `factory triage` shows on a fresh install

Ran on 2026-11-07 against `main` plus the safe PRs, with Money Made Simple's launch scripts imported and
no keys set. Expect the same shape on your machine; it shrinks as you work through Stages 6–8 and R2.

```
Do this week (5)
  [money-made-simple] review: #1 The two-account trick that stops overdrafts · fact_check: 2 claim(s) need a human fact-check
      → approve, edit or reject it in Review
  … (#2–#5 the same: 1–3 claims each)

Setup (once) (18)
  [-] media URL: PUBLIC_MEDIA_BASE_URL not set: Instagram/Threads fetch media from a public HTTPS URL
  [-] voice: silent placeholder voice: set KOKORO_URL (free) or ELEVENLABS_*/OPENAI_API_KEY
  [-] writing: offline placeholder drafts: set ANTHROPIC_API_KEY for real scripts
  [money-made-simple] brand file: link_in_bio: placeholder link: https://example.com/links
  [money-made-simple] brand file: affiliates[0].url: placeholder link: https://example.com/go/hysa
  [money-made-simple] brand file: products[0–5].url: placeholder link: https://example.gumroad.com/l/…  (6 lines)
  [money-made-simple] money-made-simple/facebook: missing FB_PAGE_ID, FB_PAGE_TOKEN
  [money-made-simple] money-made-simple/instagram: missing IG_USER_ID, IG_ACCESS_TOKEN
  [money-made-simple] money-made-simple/youtube: missing YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
  [tiny-histories] brand file: products[0].url: placeholder link: https://example.gumroad.com/l/tiny
  [tiny-histories] facebook / instagram / youtube: missing tokens (3 lines)
```

How to use it: clear **Setup** top to bottom once (each line names the file or key), then treat **Do this
week** as your daily review queue. `factory triage --save` writes it to `output/triage.md`. Run
`factory launch-check` after triage is clean; go live only on green.

### R5 · Master recording schedule

Every long video needs one element a template can't make (a chart, a screen recording or a part you
record yourself), and `factory launch-check` blocks it without one. Charts are drawn automatically; the
items below need you. One short session each **Saturday**, recording everything due the following week.
Record at 1080p or better, never show personal data (blur account numbers, codes and names), keep clips
10–30 s, and save each one where its brand's file says (Scam Decoded:
`launch/scam-decoded/LONG_VIDEO_RECORDINGS.md`). `factory recordings` shows what's still missing, soonest first.

Times: about 15 min per
screen recording, 30 min per on-camera or own-voice segment.

Sources: Scam Decoded's 31 from `launch/scam-decoded/LONG_VIDEO_RECORDINGS.md`, 1099 Money's 14 from
`launch/1099-money/RECORDINGS.md` (shot lists and file names there), Money Made Simple's 5 that
`factory launch-check` blocks on PR #5, and the ad studio's 5 from `ai-ad-studio-v2/social-posts/README.md`.
Dinero Simple's screen recordings come after its Spanish review and aren't scheduled yet.

Once everything is imported, `factory batch-record --days 21 --minutes 45` builds these sessions for you
(shot list, teleprompter page and `session.json` per session), and `factory batch-record attach <session
folder>` links the recorded files into their videos. Use the table below to plan the Saturdays; use
batch-record on the day.

**Sat Nov 14, 2026** · 3 items · ≈ 60 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 11-19 | Studio | Post 4 · Process | screen-recording: Screen-record the plan → frames → export workflow |
| 11-22 | Scam | 9 holiday scams that peak before New Year (and how to beat each one) | screen-recording: Screen-record checking an unfamiliar store: search its name plus 'scam' and 'reviews', then open its contact and returns pages. (beat: 2. 1. Fake stores) |
| 11-22 | 1099 | Your first year freelancing: the complete money setup | human-segment: on-camera clip for the chapter, ~27s (shot list in launch/1099-money/RECORDINGS.md) (beat: Monthly hour) |

**Sat Nov 21, 2026** · 2 items · ≈ 30 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 11-24 | Studio | Post 7 · Seller tip | phone footage: Film 5 short phone clips of one product |
| 11-29 | Scam | How to protect your parents from scams: the complete guide | screen-recording: Screen-record your own phone: silence unknown callers, the carrier spam filter, and adding a contact as a favorite. (beat: 5. Phone settings) |

**Sat Nov 28, 2026** · 3 items · ≈ 40 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 12-02 | Studio | Post 13 · Rate the listing | permission: Get a real seller's written OK to feature their listing (not a recording) |
| 12-03 | Studio | Post 14 · Process | screen-recording: Screen-record the delivery folder and an Etsy video upload |
| 12-06 | Scam | Credit freeze vs fraud alert vs monitoring: what you actually need | screen-recording: Screen-record typing one credit bureau's freeze page address and finding the freeze button. Stop at sign-in. (beat: 2. Freeze) |

**Sat Dec 5, 2026** · 2 items · ≈ 30 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 12-10 | Studio | Post 19 · Process + offer | screen-recording: Screen-record the Shop Trio batch |
| 12-13 | Scam | Identity theft recovery, step by step (what to do in the first week) | screen-recording: Screen-record IdentityTheft.gov (typed in): start a report, pick a category, stop before personal details. (beat: 5. 3. Report) |

**Sat Dec 12, 2026** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 12-20 | Scam | 7 scams that hit after the holidays (returns, resales and new gadgets) | screen-recording: Screen-record typing the balance-check address printed on the back of your own gift card (blur the card number). (beat: 7. 6. Balance checks) |

**Sat Dec 19, 2026** · 2 items · ≈ 45 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 12-27 | MMS | The 2027 money reset: a complete plan in one sitting | human-segment: Dhruv records the 'When it breaks' chapter on camera or as his own voice: one honest, true restart tip (beat: When it breaks) |
| 12-27 | 1099 | Your freelancer tax season plan: January to April | screen-recording: screen recording for the chapter, ~24s (shot list in launch/1099-money/RECORDINGS.md) (beat: Jan 15) |

**Sat Dec 26, 2026** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 01-03 | Scam | Find and cancel every subscription you forgot (a 30-minute New Year cleanup) | screen-recording: Screen-record your own phone's subscriptions screen in the app store settings (blur prices if you like). (beat: 3. Place 2: app stores) |

**Sat Jan 2, 2027** · 3 items · ≈ 45 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 01-10 | MMS | Your first tax return, start to finish | screen-recording: Screen recording of the IRS Free File landing page and the 'Do you need to file?' interactive tool (beat: Free filing) |
| 01-10 | Scam | Tax season scams 2027: 8 to know before you file | screen-recording: Screen-record irs.gov (typed in): the Get an IP PIN page. Stop at sign-in. (beat: 10. The IP PIN) |
| 01-10 | 1099 | Your 1099s explained: every form, every mistake, every fix | screen-recording: screen recording for the chapter, ~44s (shot list in launch/1099-money/RECORDINGS.md) (beat: 1099-K) |

**Sat Jan 9, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 01-17 | Scam | How to file your taxes safely: documents, preparers and protecting your refund | screen-recording: Screen-record the IRS Directory of Federal Tax Return Preparers: search your ZIP code and show the credentials column. (beat: 4. Step 3: choose) |

**Sat Jan 16, 2027** · 2 items · ≈ 45 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 01-24 | Scam | How a wrong-number text becomes a $100,000 loss (crypto investment scams explained) | screen-recording: Screen-record FINRA BrokerCheck and the SEC's investor.gov search: look up a made-up 'platform' name and show that nothing comes back. (beat: 4. Stage 3: the tip) |
| 01-24 | 1099 | Get your freelance taxes ready to file in one weekend | human-segment: on-camera clip for the chapter, ~52s (shot list in launch/1099-money/RECORDINGS.md) (beat: Prep) |

**Sat Jan 23, 2027** · 2 items · ≈ 30 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 01-31 | Scam | Romance scams before Valentine's: how to spot one, and how to help someone in one | screen-recording: Screen-record a reverse image search of a stock photo of a person, showing where else the photo appears. (beat: 5. Video and AI) |
| 01-31 | 1099 | Schedule C explained, section by section, for freelancers | screen-recording: screen recording for the chapter, ~39s (shot list in launch/1099-money/RECORDINGS.md) (beat: Header) |

**Sat Jan 30, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 02-07 | Scam | Sextortion: what every parent and teen should know (and do) | screen-recording: Screen-record the Take It Down start page (takeitdown.ncmec.org, typed in) and scroll its how-it-works steps. Don't upload anything. (beat: 7. Take It Down) |

**Sat Feb 6, 2027** · 2 items · ≈ 30 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 02-14 | Scam | Valentine's Day: the 4 ways romance scammers ask for money | screen-recording: Screen-record reportfraud.ftc.gov (typed in): pick the romance option and stop before any personal details. (beat: 8. If money's gone) |
| 02-14 | 1099 | The mileage deduction: logs, rates, commuting rules and mistakes | screen-recording: screen recording for the chapter, ~47s (shot list in launch/1099-money/RECORDINGS.md) (beat: The log) |

**Sat Feb 13, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 02-21 | Scam | IRS scams 2027: every way scammers fake the IRS, and how the real IRS contacts you | screen-recording: Screen-record typing irs.gov and finding the Individual Online Account sign-in and the Payments page. Stop at sign-in. (beat: 8. Check and pay) |

**Sat Feb 20, 2027** · 2 items · ≈ 45 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 02-28 | Scam | Owe the IRS? Free help first, and how to spot a tax relief scam | screen-recording: Screen-record the Taxpayer Advocate Service site and the Low Income Taxpayer Clinic list on irs.gov (find your state). (beat: 6. Free help) |
| 02-28 | 1099 | 12 freelance tax mistakes that lead to IRS letters | human-segment: on-camera clip for the chapter, ~31s (shot list in launch/1099-money/RECORDINGS.md) (beat: Before you file) |

**Sat Feb 27, 2027** · 2 items · ≈ 30 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 03-07 | Scam | Government imposter scams: Social Security, Medicare, courts and more (Slam the Scam Day) | screen-recording: Screen-record ssa.gov/scam (typed in) and its 'report a scam' button. Stop before the form. (beat: 2. Social Security) |
| 03-07 | 1099 | How to file your freelance tax return, step by step | screen-recording: screen recording for the chapter, ~41s (shot list in launch/1099-money/RECORDINGS.md) (beat: Step one) |

**Sat Mar 6, 2027** · 3 items · ≈ 45 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 03-14 | MMS | Where's my tax refund? How refunds work, and what slows them down | screen-recording: Screen recording of Where's My Refund on IRS.gov (logged-out, entry screen only) and the IRS2Go app's status screen (beat: How it works) |
| 03-14 | Scam | Spring break scams: fake rentals, fake booking sites and 'free trips' | screen-recording: Screen-record a search for a big hotel chain: point at the 'Sponsored' result, then type the chain's real address yourself and compare the domains. Book nothing. (beat: 3. Fake booking sites) |
| 03-14 | 1099 | Owe the IRS more than you expected? Every option, explained | screen-recording: screen recording for the chapter, ~38s (shot list in launch/1099-money/RECORDINGS.md) (beat: Long) |

**Sat Mar 13, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 03-21 | Scam | Job scams 2027: 4 fake jobs that cost you money (and how to spot them) | screen-recording: Screen-record checking a recruiter email domain against a real, public company's careers page. (beat: 5. Fake recruiters) |

**Sat Mar 20, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 03-28 | Scam | Filing last minute? How to beat the tax deadline safely (and the scams waiting for you) | screen-recording: Screen-record irs.gov (typed in): the Free File page and the extension page for Form 4868. (beat: 4. Free extensions) |

**Sat Mar 27, 2027** · 2 items · ≈ 30 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 04-04 | Scam | After the storm: how home repair scams work, and how to hire safely | screen-recording: Screen-record your state's contractor license lookup: search a common business name and show the license status field. (beat: 6. Hiring safely) |
| 04-04 | 1099 | Tax extensions for freelancers: how, when, and what they really cost | screen-recording: screen recording for the chapter, ~39s (shot list in launch/1099-money/RECORDINGS.md) (beat: How one) |

**Sat Apr 3, 2027** · 2 items · ≈ 30 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 04-11 | Scam | After Tax Day: the scams that follow you (and what the IRS really does next) | screen-recording: Screen-record typing irs.gov and opening Where's My Refund. Stop before entering anything. (beat: 2. Refund trackers) |
| 04-11 | 1099 | Day job, side gig or working spouse: freelance tax without quarterly payments | screen-recording: screen recording for the chapter, ~36s (shot list in launch/1099-money/RECORDINGS.md) (beat: How) |

**Sat Apr 10, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 04-18 | Scam | How 1 hacked email unlocks everything (and how to lock it in 20 minutes) | screen-recording: Screen-record turning on 2-step verification in your own email account settings (blur codes and the address). (beat: 5. Two-step) |

**Sat Apr 17, 2027** · 2 items · ≈ 45 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 04-25 | Scam | Moving this spring? Rental listing scams and moving company scams, decoded | screen-recording: Screen-record the FMCSA mover search: search a moving company by name and show its USDOT number and complaint history link. (beat: 6. Check a mover) |
| 04-25 | 1099 | Mid-year tax planning for freelancers: project 2027 now and fix it early | human-segment: on-camera clip for the chapter, ~29s (shot list in launch/1099-money/RECORDINGS.md) (beat: Repeat) |

**Sat Apr 24, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 05-02 | Scam | Older Americans Month: the 7 scams that target older adults most | screen-recording: Screen-record your own phone's settings: silence unknown callers and the carrier's spam filter. (beat: 8. How families help) |

**Sat May 1, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 05-09 | Scam | Medicare fraud: free tests, free braces, and the card thieves want | screen-recording: Medicare's own sample Medicare Summary Notice on screen: circle where fake tests and equipment would show up (face cam intro and outro). (beat: 7. Read the statement) |

**Sat May 8, 2027** · 3 items · ≈ 60 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 05-16 | MMS | Budgeting App vs Spreadsheet: Which One Should You Use? | human-segment: Dhruv records 'Try it for 30 days' in his own voice, saying truthfully which method he uses (or that he's choosing one now) (beat: Try it for 30 days) |
| 05-16 | Scam | Graduates' guide: fake jobs, fake landlords and scholarship scams | screen-recording: Screen-record checking a real, public company's careers page and a recruiter's email domain, then a reverse image search of a listing photo. (beat: 2. The chat interview) |
| 05-16 | 1099 | Business travel for freelancers: what a working trip lets you deduct | screen-recording: screen recording for the chapter, ~43s (shot list in launch/1099-money/RECORDINGS.md) (beat: Per diem) |

**Sat May 15, 2027** · 2 items · ≈ 45 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 05-23 | Scam | Veterans' benefit scams and fake military charities: what to know before Memorial Day | screen-recording: Screen-record VA's accreditation search (search a common surname, no personal data) and a charity watchdog lookup. (beat: 3. Free help) |
| 05-23 | 1099 | Hiring help as a freelancer: contractors, family and the forms you need | human-segment: on-camera clip for the chapter, ~40s (shot list in launch/1099-money/RECORDINGS.md) (beat: Three questions) |

**Sat May 22, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 05-30 | Scam | The summer travel scam guide: flights, bookings, rentals and road trips | screen-recording: Film a real gas pump check: wiggle the card reader, look at the seal. Then screen-record finding an airline's help number inside its own app. (beat: 5. Skimmers) |

**Sat May 29, 2027** · 2 items · ≈ 30 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 06-06 | MMS | How to Freeze Your Credit (Free, 15 Minutes, All 3 Bureaus) | screen-recording: Screen recording of each bureau's official freeze page (landing pages only, no personal data entered) (beat: Step by step: Equifax, Experian, TransUnion) |
| 06-06 | Scam | Teens and summer money: money flips, free game coins and check-first babysitting jobs | screen-recording: Screen-record the security settings in a payment app and a game account on your own phone (2-step verification, private payments, parent PIN). (beat: 5. Settings) |

**Sat Jun 5, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 06-13 | Scam | Before Father's Day: car warranty calls, Google listing threats and the overpaying car buyer | screen-recording: Screen-record your own call log of warranty robocalls (numbers blurred), then blocking and reporting one. (beat: 6. Blocking calls) |

**Sat Jun 12, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 06-20 | Scam | Official-looking scams: jury duty warrants, deed letters and 'storage full' emails | screen-recording: Film from above: three fictional mock-ups on your desk (a call script, a deed letter, a storage email), marking the tells with a pen. Then your phone's real storage… (beat: 5. The pattern) |

**Sat Jun 19, 2027** · 1 item · ≈ 15 min

| Due | Brand | Video | Record |
|---|---|---|---|
| 06-27 | Scam | 4th of July weekend scams: lost pet texts, money 'sent by mistake' and fake celebrity ads | screen-recording: Screen-record two settings on your own phone: making a payment app private, and the 'report ad' menu in a social app. (beat: 5. Settings) |

### R6 · Dhruv's 15 minutes a day (first 30 days after launch)

Days count from the day you start posting. Once the setup above is done, the factory drafts, renders and schedules. What's left is the part only you
can do. Open `factory ui` (the Today page) and do these in order; stop at 15 minutes and carry the rest over.

**Every day (15 min)**

- [ ] **3 min · Triage.** `factory triage` (or the Today page). Clear anything red first.
- [ ] **5 min · Review 2 posts.** Watch each one, tick every fact (and `launch/VERIFY_BEFORE_POSTING.md`),
      then Approve & schedule. Reject anything you wouldn't say to a friend.
- [ ] **2 min · Post TikTok by hand.** `factory ui` → Post by hand: copy the caption, upload, switch on the
      AI-generated label, mark it posted.
- [ ] **5 min · People.** Reply to comments and DMs yourself (the `/inbox` drafts help; you send). Answer any
      ad-studio reply the same day. Note good questions as new ideas.

**Plus, on these days**

| When | Extra (time) | What |
|---|---|---|
| Mon–Fri, from Nov 10 | +45 min | 15 ad-studio first emails and due follow-ups (Stage 2). This is the fastest money; don't let the 15 minutes crowd it out |
| Mondays | +20 min | `factory report` and its "Next actions"; `factory launch-check` |
| Saturdays | +45–60 min | the recording session from R5 (prep sheets: `docs/RECORDING_PREP_2026-11-14.md`, `-11-21`, `-11-28`, `-12-05`) |
| Sat Nov 14 | +10 min | the `LAUNCH` codes end today (the welcome emails print that date): check they've expired on Gumroad |
| Day 7 | +30 min | if Money Made Simple is steady, start Scam Decoded's accounts (Stage 9b) |
| Day 10 | +30 min | ~10 posts are live: apply to the affiliate programs (Stage 7) with the kit's answers |
| Sat Nov 21 | +15 min | Month 1 starts: import `calendar.ics`, confirm its first week is approved |
| Day 21 | +20 min | look at what worked (`factory report`): keep the hooks that held viewers, drop the rest |
| Day 30 | +30 min | swap the financial model's assumptions for real numbers (`docs/FINANCIAL_MODEL.md`) and decide what to do more of |

Skip a day and nothing breaks: posts wait in the queue, and nothing goes out without your approval.

### R7 · Launch day: each brand's first public post

Do this once per brand, the morning its first post goes out. ≈ 45 minutes the first time, 30 after that.

**Every brand, before the first post (30 min)**

- [ ] Profile is finished on every platform: picture, banner, bio from the brand kit, link in bio pointing at
      the brand's live `/links/` page (open it on your phone and tap every link).
- [ ] Instagram is a Professional account linked to its Facebook Page; YouTube channel is phone-verified.
- [ ] 2FA is on for every account, and each password is in your password manager.
- [ ] The brand's email signup works: submit your own address, get the lead magnet, confirm the double opt-in.
- [ ] Any product the first week mentions is live on Gumroad (test-buy with a 100%-off code) and its
      `brands/<slug>.yaml` URL is real. Codes printed in that product's PDF exist.
- [ ] `factory launch-check --online` is **green** for this brand (yellow only for links you haven't
      got yet, such as unapproved affiliates).
- [ ] First 3 posts are approved in Review, with every fact ticked against `launch/VERIFY_BEFORE_POSTING.md`.
- [ ] Each caption carries the AI disclosure; affiliate posts carry the affiliate disclosure.
- [ ] `FACTORY_DRY_RUN=0` only once all of the above is true (or post the first one by hand).

**On the day (15 min)**

- [ ] Post at the plan's time. TikTok by hand from `factory ui` → Post by hand, **AI-generated label on**.
- [ ] Open each post on a second device: video plays, captions are right, link in bio works.
- [ ] Reply to the first comments yourself within the first hour.
- [ ] Note the post URLs in the Today page (or a note) so the weekly report has them.

**Brand by brand**

| Brand | First post | Extra checks for its launch day |
|---|---|---|
| Money Made Simple | short *Stop overdraft fees: the two-account trick*, Day 1 (default Mon Nov 16) 12:30 ET | the six Gumroad products and `BILLCUT5`/`BUDGET5`/`AUDIT5`/`DEBTFREE5`/`INVEST5` exist; `LAUNCH` ends Nov 14; swap in the real HYSA APY before any savings post; affiliate link only once approved |
| Tiny Histories | long *Why your keyboard says QWERTY*, 17:00 ET | open the four source links in `VERIFY_BEFORE_POSTING.md`; contested stories stay worded as uncertain; no product link yet |
| Scam Decoded | channel trailer + long *How to protect your parents from scams*, Day 1 (default Mon Nov 30) 10:00 ET | check `@scamdecoded` handles are yours; no real phone numbers or links on any slide; captions say a credit freeze is free; the $9 kit is live before the Day 2 kit post; Aura/1Password/NordVPN links only once approved |
| 1099 Money | short *Your first 1099 has no tax taken out*, **Mon Nov 16** 12:30 ET | confirm the 2026 figures and 2027 dates against irs.gov and ssa.gov; the $15 Quarterly Tax Tracker is live before the Day 1 product carousel |
| Dinero Simple | short *El truco de las dos cuentas que evita sobregiros*, 12:30 ET | **the fluent reviewer has signed off** (`factory review-gate pass <id> native_review --by NAME` on every post); `RECORTE5` and `FECHA5` exist; Spanish voice, never the English one |
| Ad studio | Post 1 *Before → after*, **Mon Nov 16** | studio site and order page are live; the caption says the sample is a spec ad for a made-up shop; first cold emails went out Nov 10, so the account is live when leads look it up |

### R8 · Week 1 numbers: scorecard template

From `research/scouting/launch-metrics-30-days.md` (PR #2). Copy this block once per brand each **Monday**
(≈ 20 min). Day 7 is for stop rules only; judge content from day 14. Each threshold needs its minimum sample
before it counts, so blanks are fine in week 1.

```
Brand: __________   Week of: ______   Day since launch: __

YouTube    impressions ____  CTR ___%  watch hours ____  subs ____
TikTok     posts ____  avg views ____  avg watch time ____  shares ____
Instagram  reach ____  sends/1,000 reach ____  non-follower share ___%  saves ____
Pinterest  pins ____  impressions ____  saves ____  outbound clicks ____
Site       visitors ____  sign-ups ____ (= ___%)  outbound clicks ____
Etsy       visits ____  listings under 20 visits ___%  conversion ___%
Gumroad    views ____  sales ____ (= ___%)
Email      welcome opens ___%  clicks ___%  unsubs ___%  bounces ___%  complaints ___%
Warnings   any strike / reduced distribution / monetization notice?  Y / N
Money      orders ____  revenue $____  affiliate clicks ____   (log only in month 1)

The ONE change per platform this week: ______________________________
```

| Severity | Rule (minimum sample) | From day |
|---|---|---|
| **Stop: fix today** | any platform warning · email bounces > 2% · spam complaints > 0.1% | 1 |
| **Change: one fix this week** | YouTube CTR < 2% (after 1,000 impressions) · site sign-ups < 2% (after 200 visitors) · Etsy: over half the listings < 20 visits in 14 days · welcome opens < 30% · Instagram sends < 2 per 1,000 reach (after 2,000 reach) | 14 |
| | TikTok avg < 200 views (after 10+ posts) · Etsy conversion < 0.5% (after 300 visits) · Gumroad conversion < 1% (after 150 views) · email clicks < 2% · unsubscribes > 0.5% per send · YouTube < 500 impressions | 21 |
| **Watch: act if it holds 2 weeks** | Instagram non-followers < 30% of reach · site < 100 visitors · YouTube < 50 watch hours · Pinterest < 10 saves after 20+ pins, < 20 outbound clicks per 5,000 impressions | 21–30 |
| **Go / drop (day 30)** | double the 2 formats that cleared their thresholds, drop the 1 that missed most, and re-run `revenue_model.py` with real numbers | 30 |

The research sets no rule for shutting a whole brand in month 1; the numbers are too small to judge.

**Suggested, not from the research: a day-90 "pause a brand" check.** Pause (don't delete) a brand at day 90
if, after the month-1 thresholds were reset to your own medians, it still misses on **all three**: (1)
reach: under 500 YouTube impressions a week *and* TikTok average under 200 views after 30+ posts, (2)
interest: site sign-ups under 2% after 500 visitors, (3) money: no product sale and no affiliate
conversion in the whole 90 days. Pausing means: stop new recordings and drafts, keep the site, list and
products live, keep the finished posts banked in the queue, and post one evergreen piece a week so the
accounts stay active. Re-check at day 120; a brand that hits any one of the three keeps going. If it misses
only one or two, don't pause: fix that one with the R8 change rules. The
"our judgment" thresholds (TikTok 200 views, 2% sign-ups, Pinterest saves) get reset to your own medians
after month 1. To check automatically: `factory stats import`, then
`python3 research/scouting/check_thresholds.py --day <N> --scorecard card.json --manual manual.json`
(steps in the research doc).

---

## PR merge order

Checked 08:20 UTC on 2026-11-07 against `main` at `9cb0ca4`, merging every open PR in this order in a
scratch copy and running the full test suite.

| # | PR | Status now | What's in the way |
|---|---|---|---|
| 1 | **#1** Research | ✅ safe | |
| 2 | **#3** Financial model | ✅ safe | |
| 3 | **#2** Scouting, hooks, Trial Reels | ✅ safe | |
| 4 | **#4** Website and emails | ✅ safe | |
| 5 | **#5** Months 1–8, channels, affiliate kit | ✅ safe | |
| 6 | **#6** Products, Etsy, KDP, ebook | ✅ safe (fixed) | |
| 7 | **#8** Web apps | ✅ safe (test clash fixed, tested at `12634b8`) | |
| 8 | **#9** Scam Decoded | ⏳ nearly | merges cleanly; needs `main` again to regenerate `docs/COMMANDS.md` for `launch-pack`. Merge after #11 |
| 9 | **#11** Dinero Simple | ✅ safe (tested at `0562072`) | merge after #12 |
| 10 | **#10** 1099 Money | ⏳ nearly | already contains `main`, #5 and #9; re-checked once those settle. Merge last |
| 11 | **#12** Ad studio portfolio + listing-video page | ✅ safe | |
| 12 | **#7** This checklist | ✅ safe | docs only |

**Safe to merge now, in order: #1, #3, #2, #4, #5, #6, #8, #12, #11, #7.** These ten were merged
together on top of `main` and the full test suite passed. Then #9 once its test fix lands, and #10 last.
If a new PR lands, merge it after these unless its description says otherwise.
