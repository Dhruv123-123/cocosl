# Freelancer affiliate programs for 1099 Money (Nov 2026)

These are the programs behind the 1099 Money comparison pages (`apps/freelance-tax/compare/`). The
figures were checked on Nov 7, 2026 against each program's own page where one exists, and against
affiliate directories where it doesn't (flagged below). **Payouts change often, and directory figures are
estimates.** Confirm the live terms in the dashboard once you're approved, then paste the real link into
`apps/freelance-tax/config.js` → `affiliates`. Until then the pages render with no link at all.

## The seven programs

| Program | What you're paid | Network / how you join | Approval needs | Fits page |
|---|---|---|---|---|
| **Keeper** (expense tracking + tax filing for 1099 workers) | Up to **$50 per referral**, paid when the referred user scans their purchases for write-offs | **Tune** (Keeper's own Tune portal; sign up from keepertax.com/become-an-affiliate) | Not published. Payouts are monthly, by direct deposit. | Tax software |
| **QuickBooks** (Online / Solopreneur) | **$25–$300 one-time** per eligible subscription, depending on plan. The customer must stay active for 60 days. | **Direct**: the QuickBooks Business Affiliate Program (quickbooks.intuit.com/partners/qbbusinessaffiliates). Some publishers use a separate CJ program. | A **US EIN**, US address and US bank account, plus onboarding and a compliance review. As a sole prop, get a free EIN first. | Invoicing tools, tax software |
| **FreshBooks** (invoicing + accounting) | **Up to $200 per paid subscriber**, plus a payment for trial signups (amount not published). The structure is "customized" and grows with volume. | **PartnerStack** | Manual review, usually a few business days. Denied: coupon/cashback sites, unoriginal content, ad-only or social-only promotion, unfinished sites. **Launch the site first.** Commissions have a 14-day hold and then a FreshBooks review. Paid monthly. | Invoicing tools |
| **Found** (banking + bookkeeping + tax set-aside for the self-employed) | About **$40 per funded account** (directory figure; Found doesn't publish it) | **Impact** | Not published. Impact programs reject sites with little traffic or that look unfinished; approval can take hours to weeks. | Freelancer banking |
| **Lili** (banking for freelancers) | **No creator affiliate program found.** The Accountant Program pays $150–$350 per qualified client plus a 10% ongoing revenue share, for accountants only. Customers get a referral bonus. | Direct (accountant portal). One directory places Lili on Impact, but that isn't confirmed. | The accountant program needs clients to invite you from their own account, so it doesn't fit us. **Email Lili's partnerships team** and ask whether they run a publisher program. | Freelancer banking |
| **Bluevine** (business checking) | Not published. One directory estimates about $200 per funded account, which is unconfirmed. Bluevine runs creator partner pages (bluevine.com/partner/<name>), so a program does exist. | **Email partnerinquiry@bluevine.com.** No public network. | Not published. Expect a review of traffic and audience. | Freelancer banking |
| **Collective** (S corp setup + payroll + bookkeeping + taxes, all in one) | **$600 per qualified S corp referral**, **$300 per LLC**. The friend gets a month free. Paid by ACH or PayPal. | **Direct** member referral program (help.collective.com). There's no affiliate network; ask Collective about a publisher deal. | The referral must become a paying member and stay 30 days. **No unapproved paid social or search ads**, no posting your link on Collective's social accounts, no misleading claims, and email must follow CAN-SPAM. As written, the program is for members. | S corp services |

### What this means in practice

1. **Best fit for our content:** Collective ($600 per S corp, and it matches the "when should I become an
   S corp" videos) and Keeper ($50, matching every deductions video). Both are direct programs, so we can
   apply on day one.
2. **Apply after the site is live with the comparison pages:** FreshBooks (PartnerStack rejects unfinished
   sites), Found (Impact), and QuickBooks (needs an EIN and a compliance review).
3. **Email first:** Bluevine (partnerinquiry@bluevine.com) and Lili. Use the comparison pages as the pitch.
4. **Collective caveat:** its terms read as a *member* referral program. Before putting the link on a public
   page, ask Collective in writing whether publisher placement is allowed. If it isn't, apply through
   whatever partner channel they offer instead.

## Also on the comparison pages (not checked in depth)

| Page | Other names on it | Program notes from earlier research (`02-affiliate-programs.md`) |
|---|---|---|
| Freelancer banking | Novo, Relay | Novo: PartnerStack, payout not published. Relay: directory says $50–$300 CPA, unconfirmed. |
| Tax software | FreeTaxUSA, TurboTax, H&R Block | FreeTaxUSA: 50% per sale, 90-day cookie, direct. TaxAct (not on the page): 15%, CJ. |
| Invoicing tools | Wave | Not checked. |
| S corp services | Gusto (payroll only), a local CPA | Gusto: $50–$100 per lead, 120-day cookie. |
| Health insurance | HealthCare.gov / state exchanges, HealthSherpa, Stride Health | The marketplace has no affiliate program. That's fine: the page is an honest explainer first, and the exchange is the main recommendation. |

## Compliance for these pages

- **FTC:** every comparison page carries the affiliate disclosure *above* the first link. Links are
  `rel="sponsored"`, and a card says "affiliate" next to the button when the link pays us.
- **Rank on merit, not payout.** Every page states how picks were made. The table includes options that pay
  us nothing (FreeTaxUSA before approval, Wave, HealthCare.gov) where they're the right answer.
- **No made-up numbers.** Prices and APYs change and aren't printed on the pages. Each card says "check
  current pricing", and the pages compare features that rarely change (FDIC via a partner bank, tax
  set-aside buckets, invoicing, payroll).
- **Banking:** fintech apps aren't banks. Each card says to check the partner bank, and the page explains
  pass-through FDIC insurance (see the Synapse collapse, 2024).
- **S corp:** the page shows the real break-even math (reasonable salary, payroll and filing costs) and
  says plainly that most freelancers under roughly $60–80K profit shouldn't elect.
- **UTM:** affiliate links never get UTM tags (`docs/UTM.md` §1). Plausible counts them with the
  `Affiliate Click` event instead.

## Sources

- Keeper affiliate page: https://keepertax.com/become-an-affiliate
- QuickBooks Business Affiliate Program: https://quickbooks.intuit.com/partners/qbbusinessaffiliates/ and
  https://quickbooks.intuit.com/learn-support/en-us/help-article/small-business/promote-sell-quickbooks-quickbooks-business/L1WmCWEMR_US_en_US
- FreshBooks affiliate program: https://www.freshbooks.com/affiliate-program
- Found ($40 per funded account, directory figure): https://linkclicky.com/affiliate-program/found-banking/
- Fintech payout directory (estimates; reviewed 2026-10-29): https://fintech-pays-7vr.pages.dev/business-banking/us/
- Lili Accountant Program: https://lili.co/accountants
- Bluevine partner inquiry: https://support.bluevine.com/s/article/Can-I-become-a-partner-with-Bluevine
- Collective referral program: https://help.collective.com/hc/en-us/articles/33544636605971-How-to-Use-the-Collective-Referral-Program
