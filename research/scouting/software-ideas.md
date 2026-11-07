# 10 small software products our brands could sell (ranked)

Researched 2026-11-07. Goal: products beyond content, sold to the audiences of Money Made Simple,
Scam Shield / Scam Decoded, 1099 Money and the AI Ad Studio.

**Already built or in progress, so not repeated here** (from `apps/IDEAS.md` in PR #8 and the 1099 Money
branch): money calculators (EN/ES) and embeds, take-home pay, scam text checker, link checker and browser
extension, scam guide pages, the 20-Minute Budget PWA with Pro, subscription finder, Rate My Budget,
debt payoff PDF, ad script builder, the Family Scam-Proofing Kit, Etsy/Gumroad spreadsheet templates,
and the 1099 quarterly tax estimator and comparison pages.
**Already passed on there:** native mobile apps, stock/crypto signal tools, bank-connected budgeting (Plaid),
and a credit card rewards optimizer.

**Our stack**, which sets the effort estimates: static vanilla-JS apps under `apps/` on Netlify, with
Netlify Functions for licence checks (Gumroad/Stripe); the Python `contentfactory` package with FastAPI,
SQLite, the email funnel and PDF invoices; and Claude for drafting. "Days" means Claude build time; anything
that needs Dhruv (accounts, a phone number, legal review) is listed separately.

**How they're ranked:** expected revenue per build day for a business with no audience yet, weighted
down for legal risk and for any human work each sale needs.

## Summary

| Rank | Product | Brand | Price | Build | Main risk |
|---|---|---|---|---|---|
| 1 | Bill negotiation tracker (DIY, keep 100% of savings) | Money Made Simple | In Budget Pro ($3/mo, $29 once) or $9 standalone | 2 days | Low |
| 2 | Promo-rate and deferred-interest countdown | Money Made Simple | Free tool; reminders in Budget Pro | 1.5 days | Low (card affiliates need compliance review) |
| 3 | "Text it to us" scam check by SMS | Scam Shield | Free 5 checks/mo; family plan $3/mo | 3 days | A2P 10DLC registration; never claim certainty |
| 4 | Medical bill check and dispute letters | Money Made Simple | Free checklist; $19 letter pack | 4 days | Not legal or medical advice; keep files in the browser |
| 5 | Family security setup wizard | Scam Shield | Free; $19 family "done-with-you" pack | 2 days | Low |
| 6 | Debt collector response kit with deadline tracker | Money Made Simple | Free letters; $9 tracker + mailing guide | 2.5 days | Not legal advice; avoid debt-relief affiliates |
| 7 | Freelancer invoices with automatic tax set-aside | 1099 Money | Free 3 invoices/mo; $6/mo | 5 days | Competes with the invoicing affiliates we recommend |
| 8 | Credit dispute tracker (FCRA clocks) | Money Made Simple | $5/mo or $19 once | 3 days | Credit Repair Organizations Act: legal check before charging |
| 9 | Vendor payment-change verifier for small businesses | AI Ad Studio / 1099 Money | $12/mo per business | 4 days | B2B sale; needs outreach |
| 10 | 401(k) fee checker | Money Made Simple | Free; email list | 1.5 days | No personal investment advice; robo affiliates need compliance review |

## 1. Bill negotiation tracker

**What it is.** A list of every bill (internet, phone, insurance, streaming, gym) with its promo end date,
the last price you got, a call script by provider type, a call log ("asked for retention, got $15 off for
12 months"), and a running "saved this year" total. It reminds you 2 weeks before each promo ends.
Nothing connects to a bank and nothing asks for logins.

**Demand evidence.** The paid alternatives take a big cut and want your logins. Rocket Money charges
35-60% of first-year savings (or a $7-14/month subscription), BillShark 40% of 12 months' savings, and
Experian's BillFixer $25/month, and all of them ask for account credentials, some for SSNs
([Atlanta News First, Jul 2026](https://www.atlantanewsfirst.com/2026/07/10/online-bill-negotiators-promise-savings-require-personal-data-access/)).
Our existing $5 Bill Cut Kit and subscription finder show the topic already fits the brand.

**Competitors.** Rocket Money, BillShark, BillFixer (done-for-you, fee-based); spreadsheets (DIY).

**Build.** 2 days. A new page in `apps/budget/` reusing its storage, the subscription finder's CSV import
to pre-fill bills, and the Pro licence check. Reminders as an `.ics` calendar download (no server), with
optional email reminders from the funnel mailer later.

**Monetization.** A Budget Pro feature (raises the value of $3/month or $29 once), the Bill Cut Kit
upsell, and content: "we saved $X on these bills this month" posts from our own test accounts.

## 2. Promo-rate and deferred-interest countdown

**What it is.** Enter a 0% balance transfer, a "no interest if paid in full" store card or a BNPL plan:
the balance, the end date, and whether it's deferred interest. It shows the monthly payment that clears
it in time, the retroactive interest you'd owe if you miss, and reminders.

**Demand evidence.** CFPB data cited by NerdWallet: only about 80% of credit card deferred-interest
offers were paid in full before the promo ended (2020), so about 1 in 5 got hit; on 25-35 month promos,
retroactive interest can reach about half the original purchase price
([NerdWallet](https://www.nerdwallet.com/credit-cards/learn/deferred-interest-promos-huge-interest-charges)).

**Competitors.** No dedicated tool found; generic calculators and calendar reminders.

**Build.** 1.5 days. One static page in `apps/money-calculators/` (calculator plus FAQ schema for search),
with the reminder list in `apps/budget/` Pro.

**Monetization.** Search traffic into the email list; a Budget Pro feature; balance-transfer card
affiliates only after compliance review (flag them `complianceReview: true`, as PR #8 does).

## 3. "Text it to us" scam check by SMS

**What it is.** A phone number people forward a suspicious text, email or voicemail transcript to.
It replies within a minute with a risk level, the red flags it found, and what to do, using the same
rule engine as the web checker and extension. The family plan lets an adult child get a copy when a
parent forwards something high-risk.

**Demand evidence.** People reported $16B in fraud losses to the FTC in 2025 (over 3M reports). Older
adults reported over $3B, with text-message losses up 61% and phone-call losses $578M
([FTC to Congress via PPC Land, Oct 2026](https://ppc.land/older-americans-lost-3-billion-to-fraud-in-2025-ftc-tells-congress/)).
The FBI's IC3 recorded $20.9B in losses in 2025, up 26%
([SpyCloud summary](https://spycloud.com/blog/fbi-internet-crime-report-2025/)).
SMS reaches the people least likely to install a browser extension.

**Competitors.** Robokiller (from about $4.99/month, call screening), Truecaller (free plus Premium),
carriers' built-in spam filters, and free scam-checker apps from security vendors
([Cloaked comparison, Jul 2026](https://www.cloaked.com/post/best-ai-spam-call-blockers)). Most block
calls; few let you forward a message and get a plain-English answer.

**Build.** 3 days. A Netlify Function (or the FastAPI app) receiving Twilio SMS webhooks, calling the
existing JS rule engine, with Claude as an optional second opinion on borderline cases. Store nothing
beyond a hashed phone number and a check count. **Dhruv's part:** a Twilio account, a number, and A2P
10DLC registration for business texting (takes days to weeks).

**Monetization.** Free tier, then a $3/month family plan via Stripe; the same identity-protection and
password-manager affiliates as the checker; the $9 Family Scam-Proofing Kit. The reply always says
"we can't be certain; if unsure, call the company using the number on your card or statement".

## 4. Medical bill check and dispute letters

**What it is.** A guided checklist: request the itemized bill, spot common errors (duplicates, charges
for care not received, out-of-network surprises), check whether the hospital's charity care policy may
apply, and generate the letters (itemized bill request, billing error dispute, charity care application
cover letter, and a No Surprises Act dispute where it fits). Files stay in the browser.

**Demand evidence.** 41% of US adults had health care debt in KFF's survey, and 44% of those had skipped
paying a bill in full because they weren't sure it was accurate
([KFF Health Care Debt Survey, 2022](https://www.kff.org/health-costs/kff-health-care-debt-survey/)).
Paid advocates show people pay for this: Goodbill takes 20% of savings (capped at $1,000), CoPatient 35%,
BillShark 40%, Resolve 10-25% with a $249-499 deposit
([CoveredUSA comparison](https://coveredusa.org/en/blog/medical-bill-negotiation-services-compared)).
That page's "80% of bills contain an error" figure is a vendor claim and isn't verified.

**Competitors.** The fee-based advocates above; free help from Dollar For (charity care) and Patient
Advocate Foundation; CoveredUSA's free bill analyzer.

**Build.** 4 days for the checklist and letter builder. A later phase could compare charges with
Medicare rates from CMS's public fee schedules (more work, add only if the letters sell).

**Monetization.** Free checklist; a $19 letter pack with mailing instructions; email list; content
series. Every page says it isn't legal or medical advice. No Claude-written letters go out without the
user reading them.

## 5. Family security setup wizard

**What it is.** An interactive, per-person checklist for protecting a parent or the whole family:
credit freezes at the three bureaus, a carrier port-out PIN against SIM swaps, a bank "trusted contact",
a family safe word, unknown-caller silencing, and a password manager. It tracks progress for each
person and sends reminders.

**Demand evidence.** The FTC older-adult figures above (over $3B, and the FTC itself estimates the true
cost at $13.3B-$119.5B). Freezes and trusted contacts are free but scattered across many sites.

**Competitors.** Paid monitoring services such as Aura, EverSafe and Carefull, which monitor rather than
walk you through setup (check their current prices before comparing publicly); our own $9 PDF kit.

**Build.** 2 days, static under `apps/scam-checker/`, sharing styles and the Spanish translations.

**Monetization.** Free, with the $9 kit, password-manager and identity-protection affiliates (only
where a paid tool genuinely adds something), and a $19 "done-with-you" pack (printable sheets plus a
setup-call script for adult children).

## 6. Debt collector response kit with deadline tracker

**What it is.** Answer a few questions (do you recognise the debt, when did the first notice arrive?) to
get the right letter: debt validation request, dispute, or a request to stop contact. Then track
the response deadlines and what the collector must do before collecting. English and Spanish.

**Demand evidence.** The CFPB received 207,800 debt collection complaints in 2024. The top issue was
debts people didn't recognise, often linked to identity theft
([CFPB FDCPA report via AccountsRecovery.net](https://www.accountsrecovery.net/2025/12/02/cfpb-fdcpa-report-offers-insights-into-complaint-trends/)).

**Competitors.** SoloSuit (free documents, paid filing and attorney review; its settlement product takes
up to 19% of the debt), template sellers on Gumroad, and the CFPB's own free sample letters.

**Build.** 2.5 days, starting from the CFPB's sample letters (public domain) rather than writing legal
text from scratch.

**Monetization.** Free letters for search traffic and trust; a $9 tracker with a certified-mail guide;
email list into the budget and debt-payoff products. Avoid debt-settlement and debt-relief affiliates:
they're heavily regulated and don't fit the brand.

## 7. Freelancer invoices with automatic tax set-aside

**What it is.** Simple invoices with Stripe payment links. Each time one is marked paid, it shows how much
to move to a tax savings account (using the 1099 estimator's set-aside %), and it reminds you before each
quarterly deadline.

**Demand evidence.** MBO Partners reported the number of US independent workers rose again in 2025
([MBO Partners, Sept 2025](https://www.mbopartners.com/blog/news/number-of-independent-workers-rises-again-mbo-partners));
the 1099 Money thread's research already found high-paying affiliate programs in this space.

**Competitors.** Wave (free invoicing), FreshBooks, Bonsai, QuickBooks Self-Employed, and open-source
Invoice Ninja. The set-aside link is our difference.

**Build.** 5 days. Reuse `business/invoices.py` (PDF invoices already exist) and the 1099 estimator's
maths; it needs accounts and a database, so it would live in the FastAPI app rather than as a static page.

**Monetization.** Free for 3 invoices a month, then $6/month. **Conflict:** it competes with the
invoicing tools 1099 Money earns affiliate commissions from. Decide which to push before building.

## 8. Credit dispute tracker

**What it is.** Track each disputed item: which bureau or lender, the date sent, the 30-day
investigation clock, and the result. It generates follow-up letters and builds on the Credit Report Audit
Kit we already sell.

**Demand evidence.** The CFPB got about 6.6M complaints in 2025, and about 5.8M (88%) were about credit
or consumer reporting, up 182% against the prior two-year monthly average
([Orrick summary of the CFPB annual report](https://infobytes.orrick.com/2026-04-10/cfpb-reports-complaint-volume-doubled-in-2025-citing-surge-in-credit-reporting-disputes/)).

**Competitors.** Credit repair companies (monthly fees), free bureau dispute portals, and AI dispute-letter tools.

**Build.** 3 days, static, alongside the audit kit.

**Monetization and risk.** $5/month or $19 once. The **Credit Repair Organizations Act** restricts
charging for help "improving" someone's credit before the work is done. Self-help software may fall outside it, but
get a lawyer's view before charging. Until then, make it free and sell only the audit kit.

## 9. Vendor payment-change verifier for small businesses

**What it is.** When a supplier emails "we've changed bank accounts", the tool walks the business through
a callback to a number already on file, logs who checked and when, and holds the change until a second
person approves it. It's a simple process tool for businesses too small for enterprise payment security.

**Demand evidence.** IC3 2025: business email compromise losses of $3.04B, up from $2.77B, with 86% sent
by wire or ACH ([SpyCloud summary](https://spycloud.com/blog/fbi-internet-crime-report-2025/)).

**Competitors.** Eftsure and Trustmi (enterprise bank-account validation, demo-only pricing); manual
checklists.

**Build.** 4 days in the FastAPI app (accounts, two-person approval, audit log).

**Monetization.** $12/month per business, sold to the AI Ad Studio's small-business leads and 1099 Money's
audience. Ranked low only because it needs outreach to sell; the need is real and the price is easy.

## 10. 401(k) fee checker

**What it is.** Paste the funds and expense ratios from your plan's annual fee disclosure. It shows the
yearly fee in dollars, the 30-year drag, and the lowest-cost fund in each asset class in your own plan.
It's educational, not a recommendation.

**Demand evidence.** Fee-drag content is a proven hook ("A 1% fee eats..."), and our own launch video
"The fee that eats $18,000" was written for it. No hard public demand data found, which is why it's ranked last.

**Competitors.** Free fee analysers from large advisers (as lead magnets for their paid services).

**Build.** 1.5 days, static under `apps/money-calculators/`.

**Monetization.** Email list and search traffic. IRA or robo-adviser affiliates only after compliance
review. Never say which fund someone should pick.

## Suggested order

1. Build **1 and 2 together** as "Promo & Bill Tracker" inside the budget app (3 days). Both make Budget Pro
   worth paying for.
2. **3 (SMS scam check)** once Dhruv has a Twilio number. It's the most distinctive thing on this list.
3. **5 and 6**: cheap, free, and they bring in search traffic and trust for both brands.
4. **4 (medical bills)** after that. It's the biggest pain point, but needs the most careful writing.
5. Hold **7, 8 and 9** until there's a decision on the affiliate conflict, a legal view on CROA, and an
   outreach plan, respectively.
