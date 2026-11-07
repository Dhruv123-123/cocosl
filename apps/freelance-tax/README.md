# 1099 Money site: calculator, comparisons and funnel

| Page | What it is |
|---|---|
| `/` | Quarterly estimated tax calculator |
| `compare/` | Hub + 5 comparison pages: freelancer banking, tax software, invoicing tools, S corp services, health insurance |
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
npm run smoke         # Chromium at desktop + phone width: calculator, compare pages, free/, free/thanks/ (needs Playwright)
node tools/build-pages.mjs   # regenerate compare/ and sitemap.xml after editing tools/compare-data.mjs
```

**Deploy:** Netlify > Add new site > base directory `apps/freelance-tax` (or include it in the combined
`apps` site). Then set `siteUrl` in `config.js` and update the canonical/og URLs, `robots.txt` and `sitemap.xml`.

**Turn on the money (config.js):** the product URL and affiliate links containing `REPLACE_ME` stay hidden
until you paste real ones. Email capture works out of the box with Netlify Forms (form name
`tax-calendar`, shared by the calculator and `free/`; both forms post through `signup.js`); set `email.provider` / `email.action` for Kit, MailerLite, Buttondown or Formspree.

**Every January:** update `TABLES` and `TAX_YEAR` in `lib/tax.js`, the due-date labels in `index.html`,
and the FAQ figures. Each autumn, make the next year's calendar (dates on pages 2, 3 and 5).
