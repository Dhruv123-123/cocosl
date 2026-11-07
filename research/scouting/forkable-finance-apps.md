# Open-source money apps we could fork or extend into a paid product

Pulled 2026-11-07 from GitHub's search API (stars, SPDX licence, last push), 95 repos across personal-finance,
budgeting, expense, invoice, accounting, subscription, net-worth, FIRE, retirement, tax and YNAB topics.
For every candidate below the licence was **read from its LICENSE file or README**, because GitHub's label
is wrong or blank on several. **Docs only. Nothing has been forked.** `oss-landscape.md` covers the
content angle; this file is about **selling a product built on the code**.

## What each licence lets us do commercially

| Licence | Fork and sell as a hosted service (SaaS)? | Sell a modified app people install? | Must we publish our changes? |
|---|---|---|---|
| **MIT, Apache-2.0, BSD** | **Yes** | **Yes** | No. Keep the copyright notice (Apache: also the NOTICE file and a note of changes) |
| MPL-2.0 | Yes | Yes | Only changes to their files, not our own new files |
| GPL-3.0 | Yes (GPL has no network clause) | Yes, but buyers get the source under GPL | Yes, to anyone we distribute to |
| **AGPL-3.0** | Only if we offer our whole modified source to every user | Same | **Yes, including for hosted users.** Kills a closed paid product |
| **Business Source License (BSL 1.1)** | **No**, during the restricted period. Akaunting's BSL bans "an Accounting Service" | No, beyond its limits | — |
| **CC BY-NC 4.0** | **No** commercial use at all | No | — |
| Elastic License 2.0 | No (can't offer as a managed service) | Self-host for own business only | — |

**Trademark, for every fork:** an open-source licence gives no right to the project's name or logo. A fork
we sell gets **our own name**, and says "based on X (MIT)" in its credits, never "X Pro" or "Official X".

## Candidates that pass (MIT or Apache, licence text checked)

| Repo | Stars | Last push | Licence (checked) | What it is | Paid product we could make | Fit |
|---|---|---|---|---|---|---|
| **actualbudget/actual** | 30.1K | 2026-11-06 | MIT ("Copyright James Long") | Local-first envelope budgeting with sync and an official Node API | **Don't fork, extend.** (a) Starter budget files and templates sold with our guides (`actual-budget-tutorials.md`). (b) A small paid add-on built on `@actual-app/api`: a "weekly number" dashboard or report that reads a user's own Actual file. Managed hosting is already a commodity: PikaPods runs it for about **$1.50/month** and shares revenue with Actual ([Actual docs](https://actualbudget.org/docs/install/pikapods/)), so there's no margin in hosting it | **High** (MMS) |
| **mayswind/ezbookkeeping** | 6.0K | 2026-11-06 | MIT ("Copyright (c) 2020-2026 MaysWind"), no extra terms | Self-hosted personal finance app (Go + Vue), multi-currency, mobile web | A renamed, pre-configured **Spanish-first** build for Dinero Simple readers (categories for remittances, cash income, tandas), sold as a one-time "set up for you" install. It's niche, and support costs could eat the price | Medium (Dinero Simple) |
| **vas3k/TaxHacker** | 6.8K | 2026-10-31 | MIT ("Copyright (c) 2025 Vasily Zubarev"), no extra terms | Self-hosted AI receipt and invoice reader for freelancers (Next.js, Prisma, Postgres; OpenAI, Gemini, Mistral or a local model). Exports for tax reporting. README: "still in early development" | **A 1099 Money receipt tracker:** photo a receipt → it's sorted into Schedule C categories → a CSV at tax time. Self-host guide (free, content) or a hosted version (paid). **Hosting other people's receipts is a real data-security job** (see flags) | **High** (1099 Money) |
| **oss-apps/split-pro** | 1.5K | 2026-11-04 | MIT (repo label; LICENSE text not shown on the page, so check before forking) | Splitwise alternative: groups, split types, multi-currency, receipts, PWA, optional Plaid import. The old public instance is unmaintained (stuck at v1.3.4) | A hosted **roommates and couples bill splitter** under an MMS name, free with a paid tier (recurring bills, exports). Splitting is a crowded market | Medium (MMS) |
| **Hasnayeen/invobook** | 2.2K | 2026-10-31 | MIT per README (the badge points to another repo path, so check the LICENSE file) | Time tracking, invoices, clients and projects (Laravel, Filament) | Base for idea #7 in `software-ideas.md` (invoices with automatic tax set-aside) instead of building from zero | Medium (1099 Money) |
| **kevinschaich/mintable** | 1.6K | 2026-10-29 | MIT (SPDX) | Pulls transactions into Google Sheets | Reference for a "your bank feed in Sheets" template product, like Tiller ($99/year, below). Needs a bank-data provider (Plaid or SimpleFIN) and its costs | Low-medium |
| **MikePiper/open-social-security** | 75 | 2026-10-25 | MIT (SPDX) | Social Security claiming-age calculator | Embed a free calculator on MMS for email sign-ups. Not a paid product (no investment advice) | Lead gen |
| **Gregable/social-security-tools** | 98 | 2026-10-31 | MIT (SPDX) | Source of ssa.tools, which reads your SSA earnings record | Same: free tool and content | Lead gen |
| **JackMorrissey/beyond-rule-4** | 97 | 2026-04-13 | MIT (SPDX) | FIRE calculator on YNAB data | Pattern for a calculator on Actual data instead | Low |
| huhusmang/Subscription-Management | 901 | 2025-11-14 | MIT (SPDX) | Subscription tracker | A permissive alternative to Wallos (GPL) for a "find every repeating charge" tool tied to the Bill Cut Kit | Medium |
| simonwep/ocular, econumo/econumo, Tanq16/ExpenseOwl | 0.1-1.5K | 2025-10 to 2026-11 | MIT (SPDX) | Small budgeting and expense apps | UI references only; small communities | Low |
| sparksuite/simple-html-invoice-template | 1.7K | 2024-07 | MIT | HTML invoice template | Use inside any invoice product | Utility |

## Looks open, but isn't usable for a paid product

| Repo | Stars | Why not | Checked |
|---|---|---|---|
| **whisper-money/whisper-money** | 1.1K | **CC BY-NC 4.0** (NonCommercial), despite "open source" framing | README licence section |
| **akaunting/akaunting** | 10.3K | **Business Source License 1.1**: no "Accounting Service" for third parties, no rebranding, production limited to 2 users / 1 company / 1,000 invoices; converts to GPLv3 four years after each release | LICENSE.txt |
| **TNT-Likely/BeeCount** | 2.8K | **BSL**: personal use free, commercial use needs a paid licence | README |
| invoiceninja/invoiceninja | 10.5K | Elastic License 2.0: no managed service | `oss-landscape.md` |
| maybe-finance/maybe, firefly-iii, ghostfolio, wealthfolio, securo, bigcapital, budgetzero, OpenBudgeteer, paisa, ignidash | 0.3-54K | **AGPL-3.0**: a hosted paid version must publish all our source | SPDX |
| ellite/Wallos, jameskokoska/Cashew, moneymanagerex, hledger, Owl | 0.1-8.8K | GPL: OK for a separate program, but no closed app | SPDX |
| portfolio-performance | 4.2K | EPL-1.0, and investment tracking is off-strategy | SPDX |
| toolkit-for-ynab and YNAB API projects | — | MIT code, but a product depends on YNAB's API terms and YNAB's own business | — |

## Recommendations, in order

1. **Extend Actual, don't fork it.** Ship the starter budget file as a bonus now, and test the demand for a
   paid add-on with a waitlist on the tutorial series before building anything. Lowest risk; it rides the
   content we're already making.
2. **Prototype the 1099 receipt tracker on TaxHacker (MIT), self-hosted first.**
   - Publish a "run your own receipt tracker in 20 minutes" guide (free) and a paid **1099 category pack**
     (prompts and categories mapped to Schedule C lines, plus a year-end export template).
   - Only consider hosting other people's receipts after a security and legal review (flags below).
3. **Keep split-pro and ezbookkeeping as options, not plans.** Both are crowded and support-heavy for a
   one-person business.
4. **Use the MIT calculators as free lead magnets** on the MMS site (Social Security claiming age), with the
   copyright notice in the page footer.

## Flags before selling anything built on these

- **Keep notices.** MIT and Apache require the copyright and licence text in every copy (an "Open-source
  credits" page or file). Apache-2.0 also needs NOTICE, and changed files must say they changed.
- **Rename every fork.** No project names or logos in our product name, domain or ads.
- **Hosting people's financial data is a different business.**
  - It needs encryption, backups, access logs, a breach plan and a privacy policy that tells the truth.
  - The FTC's Safeguards Rule covers many non-bank "financial institutions" (tax preparers among them).
    Whether a receipt app is covered needs a lawyer's answer **before** launch, not after.
  - Sending receipts to an LLM API means the provider's data terms apply, and users must be told.
- **Bank feeds cost money** (Plaid, or SimpleFIN's own fee). A free-plan product shouldn't depend on one.
- **No investment advice.** Calculators show maths, not recommendations, and say so.
- **Licence labels lie.** whisper-money says "open source" but is NonCommercial. Read the LICENSE file
  before any fork, and save a copy with the date in the fork's repo.
