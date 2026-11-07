# Quarterly estimated tax calculator (1099 Money)

A free, static calculator for US freelancers: full-year federal tax (SE tax + income tax, 2026 figures),
the prior-year safe harbor vs. 90% of this year, what to pay by each deadline, and a set-aside %.
It feeds the email list (deadline reminders) and The Quarterly Tax Tracker ($15).

Same layout as the other apps (plain HTML/CSS/JS, no build step). The math in `lib/tax.js` matches
`launch/1099-money/product/build_tracker.py` and the brand's $60K worked example.

```bash
cd apps/freelance-tax
npm test              # unit tests (Node 20+, no dependencies)
npm run smoke         # Chromium at desktop + phone width (needs Playwright)
```

**Deploy:** Netlify > Add new site > base directory `apps/freelance-tax` (or include it in the combined
`apps` site). Then set `siteUrl` in `config.js` and update the canonical/og URLs, `robots.txt` and `sitemap.xml`.

**Turn on the money (config.js):** the product URL and affiliate links containing `REPLACE_ME` stay hidden
until you paste real ones. Email capture works out of the box with Netlify Forms (form name
`tax-calculator-signup`); set `email.provider` / `email.action` for Kit, MailerLite, Buttondown or Formspree.

**Every January:** update `TABLES` and `TAX_YEAR` in `lib/tax.js`, the due-date labels in `index.html`,
and the FAQ figures.
