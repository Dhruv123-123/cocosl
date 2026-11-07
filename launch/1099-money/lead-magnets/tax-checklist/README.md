# The Freelancer Tax Checklist (lead magnet draft)

A 5-page printable PDF: set up once, every payment, every month, every quarter (with the 2027 dates),
year-end and tax-time documents. Same facts and dates as the 2027 Freelancer Tax Calendar and the site.

- Source: `checklist.html` (Letter, 1099 Money colours). Edit this, then rebuild:
  `node launch/1099-money/lead-magnets/tax-checklist/build_pdf.mjs` (needs Playwright; it fails if any
  page's content runs into the footer).
- Output: `apps/freelance-tax/downloads/freelancer-tax-checklist.pdf`, deployed with the site at
  `/downloads/freelancer-tax-checklist.pdf`. **Nothing links to it yet.**

**Ways to use it (your call):**
1. A bonus on the calendar download page (`free/thanks/`), so every new subscriber gets both.
2. Its own opt-in on the deduction finder or invoice template, tagged `source=tax-checklist`, to see
   which magnet converts better.
3. A B2B extra for coworking spaces and associations (`../../b2b/`).

Before using it: re-check the 2026 figures and 2027 dates on irs.gov (same list as the calendar).
