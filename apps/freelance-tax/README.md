# 1099 Money site: calculator, comparisons and funnel

| Page | What it is |
|---|---|
| `/` | Quarterly estimated tax calculator |
| `compare/` | Hub + 5 comparison pages: freelancer banking, tax software, invoicing tools, S corp services, health insurance |
| `deduction-finder/`, `lib/deductions.js` | Deduction finder: 18 yes/no questions → a personal list of 2026 freelance deductions (rule, where it goes, source), what each $100 saves, print to PDF, and an email opt-in (Netlify form `deduction-finder`, with the ticked items in a hidden `deductions` field) |
| `q4/`, `lib/q4.js` | January 15 (Q4) estimated payment calculator: the Jan 15, 2027 amount, the catch-up share for missed quarters, the file-by-Feb-1 alternative, what's left for April |
| `mileage/`, `lib/mileage.js` | Gig-driver mileage deduction calculator (72.5¢/mile for 2026): tax saved by logged miles, set-aside per payout and per delivery, own log vs the app's miles |
| `about/` | Who writes the site, how pages are made (AI-assisted, sourced, dated), how it makes money |
| `free/`, `free/thanks/` | Lead magnet landing page and download page |
| `emails/` | 7-email welcome sequence + 3 buyer emails |

**Comparison pages** are generated: edit `tools/compare-data.mjs`, then run `node tools/build-pages.mjs`
(it also rewrites `sitemap.xml`; a test fails if you forget). Affiliate buttons read `config.js` →
`affiliates.<key>.url`. While a URL still contains `REPLACE_ME`, the button links to the provider's own homepage
with no affiliate label. Paste a real link and it becomes `rel="sponsored"`, gains the "Affiliate link" tag, and the
disclosure line appears. Which programs to apply to, and what they pay: `research/06-freelancer-affiliate-programs.md`.

**Analytics + UTM (per `docs/UTM.md`):** `site.js` runs on every page. It loads Plausible for
`analytics.plausibleDomain` (default `1099money.netlify.app`; never on localhost), sends `Affiliate Click`,
`Product Click` and `Signup` events with `brand`/`app`/`link`/`form` props, and tags Gumroad/Stripe/Lemon Squeezy
links at click time. They get the visit's own UTM, or `utm_source=freelance-tax&utm_medium=app&utm_campaign=<page>`,
and Stripe links also get `client_reference_id`. Affiliate links never get UTM. In Plausible, add the goals
`Affiliate Click`, `Product Click`, `Signup` and `Outbound Link: Click`, and the custom properties
`brand`, `app`, `link` and `form`.

## The calculator

A free, static calculator for US freelancers: full-year federal tax (SE tax + income tax, 2026 figures),
the prior-year safe harbor vs. 90% of this year, what to pay by each deadline, and a set-aside %.
It feeds the email list and The Quarterly Tax Tracker ($15).

**The funnel:** calculator or `free/` (landing page) → email signup (Netlify form `tax-calendar`) →
`free/thanks/` (PDF download + tracker card) → the 7-email sequence in `emails/` → the tracker.
The free lead magnet is `downloads/freelancer-tax-calendar-2027.pdf`; its source is
`lead-magnet/freelancer-tax-calendar-2027.html` (rebuild with `contentfactory.business.pdf.html_to_pdf`).

Same layout as the other apps (plain HTML/CSS/JS, no build step). The math in `lib/tax.js` matches
`launch/1099-money/product/build_tracker.py` and the brand's $60K worked example.

```bash
cd apps/freelance-tax
npm test              # unit tests (Node 20+, no dependencies)
npm run smoke         # Chromium at desktop + phone width: calculator, mileage/, compare pages, free/, free/thanks/ (needs Playwright)
node tools/build-pages.mjs   # regenerate compare/, about/ and sitemap.xml after editing tools/compare-data.mjs
node tools/seo-audit.mjs     # near-duplicate check: shared wording between pages (fails over 50%)
```

**Deploy:** Netlify > Add new site > base directory `apps/freelance-tax` (or include it in the combined
`apps` site). Then set `siteUrl` in `config.js` and update the canonical/og URLs, `robots.txt` and `sitemap.xml`.

**Search (research/scouting/pinterest-seo.md):**
- *Near-duplicates:* `tools/seo-audit.mjs` compares every page's wording (digits dropped, 5-word sequences).
  The highest overlap today is 11% (invoicing vs tax software); the test fails any page over 50%. Run it
  before adding a batch of similar pages, and merge or `noindex` anything that fails.
- *Staggered release:* `tools/schedule.mjs` dates every page, one new page a week from Mon Nov 16, 2026
  (banking first, the driver mileage page on Dec 21). On Netlify the build command
  `node tools/build-pages.mjs --release` leaves out pages not yet due (folder, sitemap, hub card, nav
  link). Add a Netlify build hook and call it weekly so each page appears on its date. Committed files
  keep every page for previews. If you deploy this folder inside the combined `apps` site, run the same
  command there.
- *Author:* set `author.name` and a short, true `author.bio` in `config.js` and rebuild. Until then the
  byline and the Article JSON-LD credit "1099 Money". `about/` says how pages are made: keep it true
  (if a person stops checking figures, change the wording).

**Turn on the money (config.js):** the product URL and affiliate links containing `REPLACE_ME` stay hidden
until you paste real ones. Email capture works out of the box with Netlify Forms (form name
`tax-calendar`, shared by the calculator and `free/`; both forms post through `signup.js`); set `email.provider` / `email.action` for Kit, MailerLite, Buttondown or Formspree.

**Every January:** update `TABLES` and `TAX_YEAR` in `lib/tax.js`, the due-date labels in `index.html`,
and the FAQ figures. Each autumn, make the next year's calendar (dates on pages 2, 3 and 5).
