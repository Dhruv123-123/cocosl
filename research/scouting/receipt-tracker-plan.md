# 1099 Money receipt tracker built on TaxHacker (MIT): features, hosting cost, licence duties

Researched 2026-11-07 from TaxHacker's repo (README, `.env.example`, `package.json`, `Dockerfile`, LICENSE)
and its website. **Docs only. Nothing forked, installed or hosted.** Follows idea #4 in
`product-ideas-beyond-content.md` and the TaxHacker row in `forkable-finance-apps.md`.

## TL;DR

1. **TaxHacker already does about 80% of the job.**
   - It reads receipt and invoice photos and PDFs with an LLM, and auto-categorises them.
   - It supports custom fields with their own AI prompts, projects, and multi-currency.
   - It exports CSV with the files attached, and it can pull receipts from email over IMAP (it ships
     `imap-simple` and `mailparser`).
   - **What's missing for 1099 Money:** Schedule C categories, a mileage log, quarterly set-aside numbers,
     and a year-end packet for a tax preparer.
2. **The maintainer already sells a hosted version: TaxHacker Cloud, €10/month (early access),** and the
   billing code (Stripe) is in the repo. A hosted fork of ours would compete directly with the author on
   price, at higher risk. **Recommendation: don't host. Sell the 1099 setup pack** for people who self-host
   or use TaxHacker Cloud, and ask the author about a referral arrangement (Dhruv sends that message).
3. **If we ever host:**
   - The server costs about **$12-25/month** (4 GB, after Hetzner's 2026 price rise; see section 3).
   - The LLM costs about **$0.002 per receipt** (Gemini 2.5 Flash at list price).
   - The real cost is security and legal: people's financial documents, possibly the FTC Safeguards Rule,
     and LLM data terms.
4. **Licence duties are light but real.**
   - MIT: keep the copyright and permission notice in every copy, including the JS bundle served to browsers.
   - Rename the product (no "TaxHacker" in our name).
   - Keep Ghostscript (AGPL-3.0, installed as a separate program in the Docker image) unmodified, and offer
     its source if we ship the image.

## 1. What TaxHacker does today

| Area | Today (README, code) | Needed for a 1099 Money tracker | Gap |
|---|---|---|---|
| Capture | Upload photos or PDFs; an "unsorted" inbox; email import over IMAP (dependencies `imap-simple`, `mailparser`) | Snap on phone, forward e-receipts | **None.** The mobile web upload works; check the phone layout |
| Extraction | LLM reads date, amount, merchant, line items, tax. Split invoice items into separate transactions | Same, plus "business vs personal" and "business-use %" | Small: two custom fields with prompts |
| Categories | User-defined categories and projects, each with its own prompt | **Schedule C lines** (advertising, car and truck, contract labor, supplies, home office, phone, software...) | **Our pack:** a category set with prompts mapped to Schedule C lines |
| Custom fields | Unlimited fields, each with its own AI prompt | "Deductible?", "Schedule C line", "Business %", "Notes for my preparer" | Our pack |
| Currency | 170+ currencies and 14 crypto, converted at historical rates | USD | None |
| Reports | Dashboard, filters, full-text search, CSV export with files, full data archive | Year totals by Schedule C line; a quarterly set-aside figure; a year-end packet (CSV + PDF summary + receipts zip) | **Our pack:** a spreadsheet that takes the CSV and builds the packet; later a small PR upstream |
| Mileage | Not a feature | IRS standard mileage log (date, purpose, miles) | Our pack: a mileage sheet (1099 Money already has a driver mileage page, PR #10) |
| Users | Sign-up with `DISABLE_SIGNUP` to turn it off; `SELF_HOSTED_MODE=true` for auto-login and your own API keys; auth via better-auth | One user per install (self-host) | None for self-hosting |
| AI models | OpenAI (`gpt-4o-mini` default), Google (`gemini-2.5-flash`), Mistral, or any OpenAI-compatible local endpoint (Ollama, LM Studio...). Keys in env or in the app. Local models "must be good at OCR" | Cheap and accurate on receipts | None |
| Storage | Files on local disk (`UPLOAD_PATH`), Postgres 17+ | Backups | User's job when self-hosting; we write the backup steps |
| Status | "Still in early development", use at your own risk | Stable enough to recommend | **Pin a tested version tag** in our guide (`ghcr.io/vas3k/taxhacker:<tag>`) |

## 2. The product: "1099 Receipt Kit" (self-host first)

**Free (content, lead magnet):** "Track every freelance receipt for free: set up your own receipt tracker in
20 minutes".
- A written guide plus a screen-recorded video.
- Two install paths: a computer at home with Docker Desktop, or a small VPS.
- Recommended: Gemini 2.5 Flash with the user's own key, or a local model for people who want nothing to
  leave their machine.
- Mention that TaxHacker Cloud (€10/month) exists for people who don't want to run anything.

**Paid ($12, Gumroad):**
1. **Schedule C category set:** about 20 categories, each with a tested prompt and an IRS Schedule C line
   reference. Plus the custom fields "Business %", "Deductible?" and "Preparer note". It's a settings
   file or step-by-step list, depending on whether TaxHacker can import settings (check this first).
2. **Year-end packet spreadsheet:** paste the CSV, and get totals by Schedule C line, a quarterly set-aside
   estimate (it links to 1099 Money's quarterly calculator), and a list of receipts over $75 without
   notes.
3. **Mileage log sheet** (standard-mileage method, with the IRS rate cell to update each January).
4. **"What counts" cheat sheet** for common 1099 expenses, cross-checked against the IRS Schedule C
   instructions (Publication 535 was retired after 2022). A human fact-checks it every January.

**Bundle:** with the Quarterly Tax Club (idea #3) at $39/year.

**Effort:**
- About 2 days: install with fictional receipts, test prompts on 30 sample receipts, build the sheets, write
  the guide.
- Plus about 90 minutes of Dhruv's screen recording.

**Why not host it ourselves (yet):**
- The author's hosted version is €10/month. Undercutting them with their own code would be legal under MIT,
  but bad for our reputation with exactly the indie audience we want, and we'd carry all the risk below.
- A pack works for both self-hosters and Cloud users, so we sell to the author's customers instead of
  competing with them.

## 3. If we ever host: cost and duties

**Monthly running cost, for up to about 100 users:**

| Item | Cost | Source |
|---|---|---|
| Server, 4 GB RAM (Next.js + Postgres + Ghostscript) | **About $12-25/mo.** Hetzner's cheap CX plans showed "currently not available" in Aug-Sep 2026, and CPX22 (4 GB) is €19.99/mo plus €0.50 per IPv4 address. Other providers' 4 GB plans are in the same range, so check before buying | [Findstack, Sep 2026](https://findstack.com/resources/hetzner-price-increase-2026) |
| Backups (receipts and database, encrypted, off-site) | About $0.10-1/mo at small scale: Backblaze B2 at $6.95/TB/month, first 10 GB free | [egresscost.com, checked 30 Sep 2026](https://egresscost.com/backblaze-b2) |
| LLM per receipt | About **$0.002** with Gemini 2.5 Flash ($0.30 per 1M input tokens, $2.50 per 1M output; about 2,000 tokens in and 400 out per receipt, our estimate). 100 receipts a month per user is about $0.20 | [pricepertoken.com, 1 Jul 2026](https://pricepertoken.com/pricing-page/model/google-gemini-2.5-flash) |
| Email (Resend, optional) | Free tier | `.env.example` |
| Payments | Stripe fees (2.9% + 30¢ in the US) | Stripe code already in the repo |

**Break-even** at $6/month: about 5 paying users covers the server. The money isn't the hard part.

**What hosting adds (all before launch, none optional):**
- **Security:**
  - Encryption at rest for uploads and the database, and HTTPS.
  - 2FA for our admin access, and access logs.
  - Encrypted off-site backups with restore tests.
  - A breach plan.
  - Patching on every upstream release.
- **Legal:**
  - The FTC Safeguards Rule applies to many non-bank financial businesses, tax preparers among them. Whether a
    receipt app is covered needs a lawyer's answer.
  - A privacy policy that names the LLM provider and what's sent.
  - Terms that say it isn't tax advice.
  - State privacy laws if we grow.
- **LLM data terms:** paid API tiers usually don't train on API data, but check each provider's terms and
  say which one we use. Free tiers may differ.
- **Telemetry:** the app depends on `@sentry/nextjs`. Check whether any DSN is set by default, and turn
  error reporting off or point it at our own project, with no receipt data in error reports.
- **Support:** someone answers "it read my receipt wrong" emails. For a one-person business that's the
  real cost.

## 4. Licence notice requirements

| Component | Licence | What we must do |
|---|---|---|
| TaxHacker code | **MIT**, "Copyright (c) 2025 Vasily Zubarev" | Keep the copyright line and full MIT text **in all copies or substantial portions**: in the repo (`LICENSE`), in any Docker image, and in the web app's "Open-source licences" page. A hosted app sends its JavaScript to browsers, which counts as a copy, so the notice goes in the served bundle's licence comments too (Next.js keeps them) |
| npm dependencies | Mostly MIT, Apache-2.0 or ISC (Next.js, React, Prisma, LangChain, Radix, better-auth, Stripe SDK, zod...) | Generate a third-party notices file (`npx license-checker --production --summary`, then the full list) and include it with the app. Apache-2.0 packages need their NOTICE text if they have one |
| `sharp` (image processing) | Apache-2.0; its prebuilt libvips binaries are **LGPL-3.0** | Fine to use as shipped (dynamic linking). Include the LGPL notice and don't statically re-link it |
| **Ghostscript** (installed by apt in the Docker image, for PDFs) | **AGPL-3.0** (Artifex; commercial licences sold separately) | Run it **unmodified** as a separate program (the app calls it; no code is copied). If we distribute a Docker image, include its licence and offer its source (Debian's source package is enough). **Never patch Ghostscript**, or the AGPL network clause would apply to our patch |
| GraphicsMagick | MIT-style (X11) | Keep its notice in the image |
| Postgres | PostgreSQL licence (permissive) | Keep its notice |
| Our additions (category pack, sheets, guide) | Ours | Choose: MIT for any code we send upstream; our own copyright for the paid pack |
| **Name** | MIT grants no trademark rights | **Rename** any fork ("1099 Receipts by 1099 Money"). Credit it as "based on TaxHacker (MIT)". No TaxHacker logo |

For the **pack only** (our recommendation), none of the hosting duties apply. We just name TaxHacker
accurately, link it, and say we're not affiliated.

## 5. Next steps (in order)

1. Install TaxHacker locally with fictional receipts. Check whether categories and fields can be exported
   and imported, which decides the pack's format.
2. Build and test the Schedule C prompts on 30 sample receipts. Record accuracy and fix the prompts.
3. Build the year-end packet and mileage sheets.
4. Write the guide, and have Dhruv record the setup video.
5. **Dhruv's call:** message the maintainer (vas3k) about a referral or partner link for TaxHacker Cloud. Dhruv
   sends it himself.
6. Re-evaluate hosting only if the pack sells 100+ copies and a lawyer has answered the Safeguards Rule
   question.
