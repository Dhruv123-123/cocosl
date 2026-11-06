# Launch day: the first 7 days

Two income lines go live tomorrow:

1. **AI video ad studio** (fastest money): service site + rate card + pitches to small brands. Folder: `launch/ugc-service/`
2. **The 20-Minute Budget** ($12, launch price $7): guide PDF + spreadsheet. Folder: `launch/product/`

Content and affiliate income (the Money Made Simple channel) builds slowly in the background. Tomorrow you
post the first two pieces so the channel exists and points at the product.

## Honest expectations (read before you start)

- **Tomorrow is about getting live, not getting paid.** By tonight you'll have a product for sale, a live
  service page, 30 researched leads and 10 pitches out. That's what "ready to make money" looks like.
- **First client:** usually takes **1–3 weeks** of steady daily outreach, sometimes longer. Cold outreach
  reply rates are low (often a few percent). Most replies come after a follow-up, and most "yes" answers come
  after a free sample. No guarantees.
- **First product sale:** with no audience yet, expect few or no sales in week 1. Sales come once the channel
  has viewers, or from people you tell directly. Don't buy followers or ads to fake momentum.
- **What compounds:** 10 good pitches a day, 3 free samples a week, 1–2 posts a day, every day. A rough way
  to think about it (illustrative, not a forecast): ~70 pitches in a week, a handful of replies, 2–3 samples,
  and with luck one Starter order ($249).
- Anything below that says "the software does it" means this kit has already written it. **Nothing sends,
  posts or charges automatically.** You press every button.

---

## What only you can do (the software can't, and shouldn't)

Do these yourself; they involve your identity, money or legal responsibility.

- [ ] **Create every account in your own name**: business email, Gumroad (or Lemon Squeezy/Stan), Stripe
      and/or PayPal Business, Netlify or GitHub, Instagram/TikTok/YouTube for Money Made Simple, Fiverr/Upwork.
- [ ] **Identity verification** (government ID, selfie checks) on Stripe, PayPal, Gumroad, Fiverr, Upwork.
- [ ] **Payout details**: connect your bank account / debit card for payouts. Never share bank logins with anyone or any tool.
- [ ] **Tax info**: W-9 (US) or W-8BEN (non-US) on the platforms that ask; decide sole trader vs. LLC
      (sole proprietor is fine to start in most places). Keep 25–30% of profit aside for tax until an
      accountant tells you your real number. Gumroad and Lemon Squeezy handle sales tax/VAT on product
      sales as merchant of record (check their current terms); for service invoices, ask an accountant.
- [ ] **A postal address for cold email** (CAN-SPAM requires one): your business address, a PO box, or a
      virtual mailbox (US virtual mailboxes need USPS Form 1583 and can take a few days). Until you have one
      you're comfortable publishing, use Instagram DMs and marketplaces, and hold the cold emails.
- [ ] **Two-factor authentication** on email, payment and social accounts.
- [ ] **Approve every pitch, post and invoice** before it goes out. Check facts in each post.
- [ ] **Sign contracts and decide pricing exceptions.**

**Already done by the software (this kit):** the guide (HTML + PDF), the spreadsheet with working formulas,
the listing copy, the studio website, rate card, pitch/DM/follow-up templates, lead criteria and CSV template,
5 portfolio ad scripts, contract template, Fiverr/Upwork copy, and the two posts at the bottom of this file.
The factory (`factory` CLI + dashboard) can draft more posts, pitches, quotes and invoices; you review and send.

---

## Tomorrow, hour by hour (~7.5 hours)

Times are a suggestion; keep the order.

### 09:00–09:30 · Accounts and email (30 min)
- [ ] Create one business email for both lines, e.g. a new Gmail (`yourstudio.ads@gmail.com`) or an
      address on your own domain if you have one. Turn on 2FA.
- [ ] Decide your studio name (check it isn't an existing ad agency's name or trademark: a quick web search
      plus your country's trademark search).
- [ ] Fill in the blanks once in a note: name, studio name, email, postal address, city. You'll paste them everywhere.

### 09:30–10:15 · Payments (45 min)
- [ ] **Gumroad** (simplest for the product): sign up, verify, add payout method. Or Lemon Squeezy / Stan
      Store if you prefer (Stan needs a subscription; Gumroad and Lemon Squeezy take a percentage per sale).
- [ ] **Stripe** account (for service invoices) and/or **PayPal Business** (invoices + many small brands pay
      this way). Complete verification; it can take from minutes to a couple of days, so start it now.
- [ ] Create an invoice template: 50% deposit line, your details, payment terms from `RATE_CARD.md`.

### 10:15–11:00 · List the product (45 min)
- [ ] Open `launch/product/The-20-Minute-Budget.pdf` and `20-Minute-Budget-Template.xlsx`; skim both.
      Change the brand name on the cover/footer if you're not using "Money Made Simple".
      (Edit `the-20-minute-budget.html` and re-export to PDF if you change text.)
- [ ] New product on Gumroad: upload both files, paste title/description/FAQ/refund line/tags from
      `launch/product/LISTING.md`. Price $12, create `LAUNCH` code for $5 off with an end date 7 days out.
- [ ] Cover image: screenshot page 1 of the PDF and crop to 1280×720 (Cover A in LISTING.md). 10 minutes, done.
- [ ] Make a 100%-off code for yourself and **do a test purchase** to check the download and thank-you email.
- [ ] Put the product link in the Money Made Simple link-in-bio.

### 11:00–11:45 · Publish the studio website (45 min)
- [ ] Open `launch/ugc-service/index.html` in a text editor. Change only the `STUDIO` block at the top
      (name, email, owner, location). Open it in your browser and click through every section.
- [ ] Publish (free), either:
  - **Netlify Drop**: go to app.netlify.com/drop, drag the `ugc-service` folder in (it serves `index.html`).
    Sign up to keep the site and rename it to `yourstudio.netlify.app`. Or:
  - **GitHub Pages** (e.g. your new GitHub account): new public repo, upload `index.html`, Settings →
    Pages → deploy from `main` branch. URL: `yourname.github.io/reponame`.
- [ ] On your phone: open the URL, submit the form, confirm it opens your mail app addressed to you.

### 11:45–12:30 · Studio presence (45 min)
- [ ] Create an Instagram business/creator account for the studio (bio: "AI video ads for small brands ·
      clearly labeled AI · free sample → link"). Link the site.
- [ ] Pick one AI video tool for presenters/voice you're licensed to use commercially (check its terms allow
      ads). Generate a 10-second test so you know the workflow before anyone says yes.

### 12:30–13:15 · Lunch (away from the screen)

### 13:15–15:15 · Build 30 leads (2 hours)
- [ ] Follow `launch/ugc-service/LEAD_CRITERIA.md`: 10 from Meta Ad Library, 10 from Shopify/search/launch
      sites, 5 Etsy (own website), 5 local. ~4–5 minutes each.
- [ ] Log in `launch/ugc-service/leads.csv` (delete the 3 EXAMPLE rows first). Score each; keep 4+/6.
- [ ] Import into the factory: dashboard → Clients → CSV import.

### 15:15–16:30 · Send 10 personalised pitches (75 min)
- [ ] Top 10 leads by score. For each: pick the matching template in `PITCH_TEMPLATES.md` (Email 1 default,
      Email 2 if they run Meta ads, Email 3 for local), write a real first line from your notes,
      add the compliance footer, send from your own inbox. ~7 minutes each.
- [ ] No postal address yet? Send DMs (template in the same file) to the leads with Instagram accounts
      instead, and hold the emails.
- [ ] Mark `pitched 2026-MM-DD` in notes. Set a reminder for follow-ups in 4–5 days.

### 16:30–17:15 · Post the first 2 pieces of content (45 min)
- [ ] Create the Money Made Simple accounts if they don't exist (one per platform).
- [ ] Post the Short and the carousel below (or generate via `factory daily --brand money-made-simple`,
      review, approve). Check every number in them yourself. Tick the AI-content label where the platform asks.

### 17:15–17:30 · Close the day (15 min)
- [ ] Note what's live (URLs), pitches sent, posts up.
- [ ] Calendar: recurring 30-minute "Pitch block" every weekday morning, and "Content review" every day.

---

## Days 2–7

| Day | Studio (≈2–3 h) | Product + content (≈1 h) |
|---|---|---|
| **2** | Make portfolio ads #1–2 from `SAMPLE_ADS.md`. 10 new leads, 10 pitches. Reply to anything within hours. | 1–2 posts. Share the product once with friends/family/personal network honestly ("I made this"). |
| **3** | Portfolio ads #3–5; upload to one unlisted showcase; paste link into `STUDIO.portfolio` and republish. 10 pitches. | 1–2 posts. Reply to every comment. |
| **4** | Fiverr gig and/or Upwork profile from `PLATFORM_LISTINGS.md` using the portfolio. 10 pitches. Make any free samples requested (max 3/week). | 1–2 posts. |
| **5** | Follow-up 1 to day-1 pitches. 10 new pitches. 5 Upwork proposals to posts where AI is OK. | 1–2 posts. Carousel version of the debt payoff chapter. |
| **6** | Follow-up 1 to day-2 pitches. Deliver samples with the offer note. Send contract + 50% invoice to anyone who says yes. | 1–2 posts. |
| **7** | Review: replies, samples, what first lines got answers. Rewrite the weakest template. Build 30 more leads for next week. | Check which post did best (`factory insights`), plan next week's 5 Shorts + 3 carousels. End the $7 launch price on schedule. |

**If someone says yes:** send `CONTRACT_TEMPLATE.md` (filled in) + 50% invoice → brief form → scripts for
approval → produce → deliver watermarked preview → final 50% → final files. Log revenue and costs in the
factory's Revenue page.

**Weekly targets for weeks 1–3:** 50 pitches, 2–3 samples, 10 posts, 30 new leads. Change one variable at
a time (first lines, niche, offer) based on replies.

---

## Ready-to-post content (Money Made Simple)

Disclosure goes on both: *"Visuals and voice made with AI tools. Script written and fact-checked by a human.
Not financial advice."* (from the brand YAML). The product is yours, so say so plainly.

### Post 1: Short / Reel / TikTok (~40s)

**Hook (on screen):** Stop dividing your budget by 4.

**Script:**
> If you split your monthly spending money by four to get a weekly budget, you're short every few months.
> A month isn't four weeks. It's about four point three three.
> So here's the fix. Take what's left after bills and savings, multiply by twelve, divide by fifty-two.
> Eight hundred dollars a month? That's not two hundred a week. It's a hundred and eighty-four.
> Dividing by four quietly gives you an extra week of money you don't have, and that's the five-Friday month
> that wrecks your budget.
> One number per week. Twelve over fifty-two. Follow for one money move a week.

**On-screen math:** $800 ÷ 4 = $200 ✗ · $800 × 12 ÷ 52 = $184.62 ✓
**Caption:** Your weekly budget is probably about 8% too high. Here's the 10-second fix. (I made a guide + spreadsheet that does this math for you: The 20-Minute Budget, link in bio. It's my own product.)
[AI disclosure line] #budgeting #personalfinance #moneytips #moneymadesimple

### Post 2: Carousel (7 slides)

1. **The 20-minute budget** — set it up once, run it in 20 minutes a week
2. **Every dollar goes into 4 lines** — Bills · Funds · Goals · Weekly
3. **Bills** — rent, utilities, phone, insurance, minimum debt payments. On autopay.
4. **Funds** — the "surprise" costs that aren't surprises: car repairs, gifts, renewals. Yearly cost ÷ 12, every month.
5. **Goals** — emergency fund, extra debt payments. Paid first, not with leftovers.
6. **Weekly** — everything else in ONE number: (pay − bills − funds − goals) × 12 ÷ 52. Groceries, fun, coffee: your call.
7. **Your 20 minutes a week** — Look (5) · Log (5) · Check (5) · Decide one thing (5). Save this for Sunday.

**Caption:** The budget system that's one number per week. Save it for your next check-in. Full guide +
spreadsheet (my own product) in bio: The 20-Minute Budget. [AI disclosure line]
#budgeting #budgettips #personalfinance #moneymadesimple


## Two weeks of content, already written

`launch/money-made-simple/content.json` holds 24 finished scripts (14 Shorts, 8 carousels, 2 long videos)
and `launch/money-made-simple/POSTING_PLAN.md` says what goes out on which day. Load them into the
review queue with:

```bash
factory import launch/money-made-simple/content.json --brand money-made-simple
```

Each one lists the facts to verify and the source links; tick them off in the dashboard before approving.
Add a voice (docs/CREDENTIALS.md section 4) and re-render the Shorts so they're narrated; the carousels are
ready as they are.
