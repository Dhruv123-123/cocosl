# Product ideas beyond content: subscriptions, templates, apps, B2B

Memo, 2026-11-07. **Docs only.** It builds on what exists:
- The six MMS products and the Scam Decoded and 1099 Money ladders (PRs #6, #9, #10).
- The 10 small software ideas in `software-ideas.md`.
- The forkable code in `forkable-finance-apps.md`.

Demand evidence comes from public sources (linked, dated). Where the only source is a competitor's
marketing page, it says so. **Prices and sizes are signals, not forecasts.**

## Summary: the 8 ideas, ranked

| # | Idea | Type | Brand | Price | Demand signal | Effort | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | **Weekly Scam Alert for credit unions and community banks**, white-labelled | B2B content subscription | Scam Decoded | $49-149/mo per institution | Credit unions already buy member-education content by subscription (FinancialFeed); 2024 fraud losses $12.5B (FTC) | Low: we already write the content | **Do first (pilot)** |
| 2 | **Actual Budget starter kit + "weekly number" add-on** | Template now, app later | MMS | Free bonus → $19 kit | Paid budgeting apps cost $80-110 a year; Actual is free with 30K stars, so its users are cost-conscious but organised | Template: 1 day. Add-on: 1-2 weeks | **Do (kit); test (add-on)** |
| 3 | **Quarterly Tax Club** for freelancers | Subscription | 1099 Money | $5/mo or $39/yr | Four fixed IRS dates a year; r/freelance 250K+; a recurring, dated problem | Low: reminders + calculator + monthly pack | **Do** |
| 4 | **1099 receipt tracker** (on TaxHacker, MIT) | App: guide + pack first, hosted later | 1099 Money | $12 pack; hosted $6/mo later | TaxHacker has 6.8K stars as a self-hosted tool for exactly this | Pack: 2 days. Hosted: weeks + legal review | **Test (pack only)** |
| 5 | **Spanish budgeting and remittance templates** | Templates | Dinero Simple | $5-12 | About 1 in 5 US residents is Hispanic (Census 2024 estimates) and few Spanish-first budget tools | 2-3 days (translate and adapt existing) | **Do** |
| 6 | **Teacher packs: scam-awareness and gig-income units** | B2B-ish templates | Scam Decoded, 1099 Money | $8-25 per unit | 30 states require a standalone personal finance course (NGPF, Apr 2026); 76% of students covered by the Class of 2031 | 1 week per unit | **Test (one unit)** |
| 7 | **Couples and roommates bill splitter** (on split-pro, MIT) | App | MMS | Free + $3/mo | Big market, but crowded (Splitwise and others) | Weeks | **Park** |
| 8 | **Employer financial-wellness bundle** | B2B | MMS | $500+/employer/yr | Experts projected 47% of employers would offer financial wellness by 2026 (Transamerica Prescience panel, via BenefitsPro, Jul 2024) | High: enterprise sales | **Park** until #1 proves we can sell B2B |

## 1. Weekly Scam Alert for credit unions (B2B content licensing)

**What:**
- A weekly, white-label email-and-social pack: "This week's scam", with what it looks like, what to do, and
  a 30-second video.
- It comes with the institution's logo, a disclaimer and a one-line "call us at the number on your card".
- Built from Scam Decoded's existing weekly content. It's not the same posts, but the same research.

**Evidence:**
- Credit unions already pay for this model. **FinancialFeed** sells a plug-in financial-literacy portal to
  credit unions on a "low-cost monthly subscription", with daily articles and social content
  ([CUInsight, Jul 2019](https://www.cuinsight.com/press-release/dugood-fcu-tackles-3-content-issues-with-financialfeed)).
  It's an older source, but it proves the buying habit.
- Scam losses keep rising (the FTC reported consumers lost **$12.5 billion** to fraud in 2024, published Mar 2025:
  [Insurance Journal, 10 Mar 2025](https://www.insurancejournal.com/news/national/2025/03/10/815001.htm)), and members ask their institution first.
- Thousands of small credit unions and community banks have no in-house content team.

**Pricing:** $49/mo (asset-size tier 1), $99, $149, with a 2-month free pilot for the first 3.

**Risks and checks:**
- Content must never tell members to send money or codes anywhere, and must match FTC, FBI IC3 and CFPB
  guidance. Our fact-check flags already do this.
- Institutions' compliance teams review marketing, so give them a review window (send each pack 7 days
  early).
- The sale is cold outreach. **Dhruv sends every email.** Use the `ai-ad-studio-outreach` workflow: 25
  hand-picked small credit unions, a sample pack attached.

**First step:** make one sample pack from an existing Scam Decoded week, and a one-page offer. About 3 hours.

## 2. Actual Budget starter kit, then a "weekly number" add-on

**What:**
- **Now:** the starter file (categories, notes, rules, schedules, fictional example) as a free bonus in the
  $12 20-Minute Budget. Also a **$19 standalone kit**: starter file, printable weekly sheet and the 6-video
  course links.
- **Later:** a small local app or web page that reads the user's own Actual file through
  `@actual-app/api` (MIT). It shows "this week: $X left of $184" and a monthly reset checklist. It's sold
  once, with the data staying on their machine.

**Evidence:**
- Budgeting apps cost **$80-110 a year** (YNAB $109/yr, Monarch $99.99/yr, EveryDollar Premium $79.99/yr,
  from [Finny, 2026](https://getfinny.app/blog/ynab-pricing-2026), a competitor's page, so check vendor
  sites). Tiller, which only feeds a spreadsheet, is $99/yr
  ([FinCompareLab, 2026](https://www.fincomparelab.com/guides/tiller-money-pricing/)).
- Actual is free and has 30K stars, and managed hosting costs $1.50/mo. People pay for the **plan and setup
  help**, not the software.

**Risks:**
- Actual's file format and API can change. Pin a tested version in the kit's instructions.
- Use our own name only, not Actual's (`actual-budget-tutorials.md`).

**First step:** build and test the starter file (product thread, PR #6). Add a "want the weekly-number add-on?"
waitlist link to the tutorial series, and build only after about 100 sign-ups.

## 3. Quarterly Tax Club (1099 Money subscription)

**What:** $5/mo or $39/yr, for:
- Email and SMS reminders 14, 7 and 1 days before each estimated-tax date.
- A monthly "set aside" check-in with our calculator.
- One new template a month (mileage log, home office, year-end packet).
- A members-only Q&A thread once a quarter.

**Evidence:**
- The IRS's four estimated-tax dates are fixed every year (15 Jan, 15 Apr, 15 Jun, 15 Sep) and missing one
  costs penalties. That's a recurring, dated pain.
- r/freelance has 250K+ members (`distribution.md`).
- 1099 Money already has 5 months of content and calculators (PR #10).

**Risks:**
- Not tax advice. It's reminders, maths and education, with "talk to a tax professional" on complex cases.
- SMS needs A2P 10DLC registration (as in `software-ideas.md` #3). Start with email only.
- Platform: Gumroad memberships or Sender (`newsletter.md`) to keep costs at $0.

**First step:** add a waitlist to the quarterly calculator page before the **15 Jan 2027** payment. Launch
if 50+ join.

## 4. 1099 receipt tracker on TaxHacker (MIT)

**What:**
- **Phase 1 (no hosting):** a free "run your own receipt tracker" guide, plus a $12 **Schedule C category
  pack** (prompts and categories for TaxHacker, a year-end CSV-to-worksheet template, a mileage add-on).
- **Phase 2 (maybe):** a hosted version at $6/mo, renamed.

**Evidence:** TaxHacker has **6.8K stars** for exactly this job (`forkable-finance-apps.md`), and 1099
Money's audience already tracks receipts by hand.

**Risks:**
- Phase 2 holds people's financial documents. That brings security work, and possibly the FTC Safeguards
  Rule; a lawyer's check comes before any hosting.
- LLM providers' data terms apply, and users must be told.
- TaxHacker says it's "still in early development", so pin a version.

**First step:** Phase 1 only. Install it locally with fictional receipts, write the guide, and build the
pack. About 2 days.

## 5. Spanish budgeting and remittance templates (Dinero Simple)

**What:** Spanish versions of the 20-Minute Budget sheet, the Bill Cut Kit and the Actual starter file. Add a
**remittance planner** (fees and exchange rate compared, monthly send budget) and a **tanda / cash-income
tracker**. $5-12 each, or a $19 bundle.

**Evidence:**
- About **1 in 5** US residents is Hispanic, and Hispanic people accounted for 58.8% of US population growth in
  2024 (Census Bureau estimates, reported by [Deseret News, Jul 2025](https://www.deseret.com/utah/2025/07/07/latino-population-still-motoring-utahs-population-growth-as-in-rest-of-the-nation/)).
  Spanish-first budget templates are scarce compared with English ones.
- Dinero Simple's long videos already cover remittances and bank accounts without SSN (PR #11).

**Risks:** a native speaker must review the copy (flagged in `thank-you-offers.md` too). No remittance
affiliate links without compliance review.

**First step:** translate the 20-Minute Budget sheet and make the remittance planner. About 2 days, product
thread.

## 6. Teacher packs (scam awareness and gig income)

**What:** classroom-ready units with slides, a worksheet, a 5-minute video, an answer key and a standards
map. "Spot the scam" (Scam Decoded) and "Your first 1099" (1099 Money). $8-25 per unit on our Gumroad, and
maybe on a teacher marketplace.

**Evidence:**
- **30 states** require a standalone personal finance course for graduation, covering **76%** of public
  high school students by the Class of 2031
  ([NGPF, 6 Apr 2026](https://dev8.ngpf.org/blog/advocacy/how-many-states-require-students-to-take-a-personal-finance-course-for-high-school-graduation/)).
  The Council for Economic Education counts 39, including courses where it's embedded.
- **Competition:** NGPF's curriculum is excellent and free. So we sell only niche units NGPF covers
  lightly (current scam scripts, gig-worker taxes), and keep each one short.

**Risks:** schools buy slowly, and student-facing content needs extra care. No data collection from
students.

**First step:** one "Spot the scam" unit from existing Scam Decoded material, listed at $8. Judge it after 60
days.

## 7-8. Parked

- **Bill splitter (split-pro fork):** big market, but a crowded one, and support for shared money between
  people is heavy for a one-person business. Revisit if MMS hits 10K email subscribers.
- **Employer financial wellness:** the demand is real (the 47% projection), but it's long enterprise sales.
  Revisit after the credit-union pilot (#1) shows we can sell B2B at all.

## What this means for the next 60 days

1. **Credit-union pilot (#1):** sample pack and offer page now. Dhruv sends 25 emails once the Scam Decoded
   site is live.
2. **Actual starter kit (#2)** with the tutorial series, plus the add-on waitlist.
3. **Quarterly Tax Club waitlist (#3)** before 15 Jan 2027.
4. **Spanish templates (#5)** in the product thread.
5. **One teacher unit (#6) and the receipt pack (#4)** as cheap tests.

Nothing here needs money up front. Gumroad, Sender, GitHub Pages and our own sites cover it.

## Open questions for Dhruv

1. Are you willing to sell B2B (credit unions)? It means sending cold emails and answering compliance
   questions, but it's the only idea here priced per institution rather than per person.
2. Should the product thread pick up #2, #3 and #5? They reuse existing material.
