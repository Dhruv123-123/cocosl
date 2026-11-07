# Apps

Small web apps that earn money without needing an audience first. They pull in search traffic,
capture emails and route people to affiliate offers and paid upgrades. All are static sites (plain
HTML, CSS and JavaScript, no framework, no build step needed) and deploy free.

| App | Brand | How it earns | Folder |
|---|---|---|---|
| **Money calculators** (7 tools, including 2026 take-home pay) | Money Made Simple | SEO traffic → email list, HYSA / brokerage / debt affiliates, The 20-Minute Budget product | `money-calculators/` |
| **Is this a scam?** message checker | Scam Shield | Identity protection, password manager and VPN affiliates, weekly scam-alert list, $9 Family Scam-Proofing Kit | `scam-checker/` |
| **The 20-Minute Budget** web app | Money Made Simple | Freemium: Pro at $3/month or $29 once via Lemon Squeezy, Gumroad or Stripe license keys; first-run setup, upgrade prompts at each free limit, pricing page (`budget/pricing.html`); setup in `budget/CHECKOUT.md` | `budget/` |
| **Rate My Budget** (8 numbers → score, grade, 3 next moves; anonymous submissions for the video series) | Money Made Simple | Budget app upsell, $19 personal review, content for the "Rate My Budget" series | `budget/rate.html` |
| **Subscription audit** (upload a bank CSV or paste statement text; every recurring charge and its yearly cost) | Money Made Simple | Free tool → budget app and Pro upsell, email list | `budget/subscriptions.html` |
| **Bill negotiation tracker** (bills, promo end dates, call scripts, call log, "saved this year"; finds bills in a bank CSV) | Money Made Simple | Budget Pro feature (free: 3 bills, Pro: every bill + calendar reminders), Bill Cut Kit upsell | `budget/bills.html` |
| **0% deal countdown** (deferred-interest and 0% APR deals: payment that clears it a month early, back-dated interest if you miss) | Money Made Simple | Free calculator for search traffic; Pro saves every deal + calendar reminders | `budget/deals.html` |
| **Credit dispute tracker** (30-day bureau clocks, replies, next steps, calendar reminders; tracking only, no letters) | Money Made Simple | Free tool for search traffic; deliberately no paid features, which keeps it clear of credit repair law | `budget/disputes.html` |
| **Net worth snapshot** (own vs owe, dated snapshots and trend, PDF made in the browser, CSV, backup; localStorage only) | Money Made Simple | Free tool with a Budget Pro upsell slot | `budget/networth.html` |
| **Side hustle profit calculator** (drivers, Etsy, eBay, Poshmark: platform fees, real driving cost vs IRS 76-cent mileage deduction, SE tax, income tax after the QBI deduction; real hourly profit and weekly tax set-aside; sources in `lib/sidehustle.js`) | 1099 Money | Free SEO tool, leads into the invoice tracker | `freelance-invoices/side-hustle.html` |
| **Spanish hub** (`/es/`: every Spanish calculator and scam tool, with its own search; built by `tools/build-es-hub.mjs` from `pages-es.mjs`) | Dinero Simple | Dinero Simple links to `/es/` | `es/` |
| **Money date: couples budget** (split shared bills 50/50, by income or a custom split; joint-account amounts and settle-up; 8-step monthly money date checklist with streak and notes; backup file to share; localStorage only) | Money Made Simple | Free tool for couples content, Budget Pro slot | `budget/couples.html` |
| **Can I afford this?** (a car, a phone or anything big: cash vs loan vs buy now, pay later; all-in price with tax, fees and trade-in, monthly fit against what's left after bills, 20/4/10 car checks, months to save; localStorage only) | Money Made Simple | Free search tool ("how much car can I afford"), Budget Pro upsell slot, links to the paycheck calculator | `budget/afford.html` |
| **Student loan repayment chooser** (2026 rules: Standard, Graduated, Extended, IBR, RAP, Tiered Standard for loans from July 2026; rules hardcoded from StudentAid.gov with sources in `lib/student-loans.js`; "verify with your servicer" note; EN + ES) | Money Made Simple | Free SEO calculator, Budget Pro box | `money-calculators/student-loans/` |
| **Rent vs buy** (owning costs vs renting and investing the difference, break-even year; EN + ES) | Money Made Simple | Free SEO calculator, mortgage affiliate slot later | `money-calculators/rent-vs-buy/` |
| **Paycheck calculator by state** (2026 federal brackets plus every state's and DC's 2026 brackets, standard deduction and exemptions, hardcoded from the Tax Foundation table with sources cited in `lib/state-tax-2026.js`; no API calls; custom-rate fallback) | Money Made Simple | Free SEO calculator, high-search "paycheck calculator [state]" | `money-calculators/take-home-pay/` |
| **Holiday spending planner** (gift list, per-person budgets, total cap, extras, BNPL true cost and monthly schedule; localStorage only) | Money Made Simple | Free seasonal tool for the /holiday/ page, Budget Pro upsell slot | `budget/holiday.html` |
| **Installable tools hub** (manifest, offline service worker `sw.js`, add-to-home-screen banner with iOS instructions) | All brands | The hub at `index.html` works as an app; tools you've opened work offline | `index.html`, `sw.js`, `install.js` |
| **Freelance invoice tracker** (status per invoice, late fees under your own terms, 5 polite reminder emails, calendar and CSV) | 1099 Money | Free tool; upsell slot for the $29 Rate & Contract Kit (invoice templates), email list form `freelance-invoices` | `freelance-invoices/` |
| **Medical bill letters** (guided form → itemized bill request, billing error dispute, financial assistance request, No Surprises Act letter; print, copy or download) | Money Made Simple | Free tool → email list; optional $19 letter pack (config link) | `medical-bills/` |
| **Debt collector letters** (debt validation under the FDCPA and Regulation F, stop-contact letter; not-legal-advice framing) | Money Made Simple | Free tool, trust and search traffic | `medical-bills/debt.html` |
| **Family scam-proofing checklist** (credit freezes at all 3 bureaus, family safe word, 2-step verification, phone number lock, child freezes; progress per person) | Scam Decoded / Scam Shield | Free tool → email list, Family Scam-Proofing Kit | `scam-checker/family/` |
| **Vendor payment check** (bank-change and invoice fraud: look-alike sender domains, red flags, verify steps, printable payment rule) | Scam Shield | B2B lead magnet: free poster sign-up (Netlify form `vendor-check`), offers the $99 team training pack once its link is set | `scam-checker/vendor/` |
| **Text-us scam check** (Twilio webhook: forward a text, get a verdict; 5 free a month, family numbers unlimited) | Scam Shield | Family plan $3/month; setup in `scam-checker/sms/SMS_SETUP.md` | `scam-checker/sms/`, `/api/sms` |
| **401(k) fee checker** (funds and expense ratios → fees in dollars, 30-year drag, lowest-cost fund per category in your own plan; EN/ES) | Money Made Simple | Free SEO tool → email list. Never recommends a fund | `money-calculators/401k-fees/` |
| **Calculadoras en español**: all 7 calculators in Spanish with hreflang links | Money Made Simple / Dinero Simple | Spanish search traffic, Spanish email list | `money-calculators/es/` |
| **¿Es una estafa?** Spanish checker (Dinero Simple audience): Spanish scam patterns and fully translated results | Scam Shield | Same offers, Spanish scam-alert list | `scam-checker/es/` |
| **Link checker** ("Is this website legit?", EN `scam-checker/link/` + ES `scam-checker/es/enlace/`): look-alike spellings, brand on the wrong domain, risky endings | Scam Shield | Search traffic → checker, list, affiliates | `scam-checker/link/` |
| **Scam guides**: 12 search pages (USPS, toll, IRS, Amazon...) feeding the checker, plus all 12 in Spanish (`scam-checker/es/estafas/`) with hreflang pairs | Scam Shield | Search traffic → checker, list, affiliates | `scam-checker/scams/` |
| **Video ad script builder** for small product brands: hook, shot list, voiceover, on-screen text, 3 test hooks, caption, plus a lint for fake-testimonial and health-claim wording. No AI calls, so it's free to run | AI Ad Studio | Free-sample request form (Netlify Forms `ad-sample-request`) → inbound leads for the $249 Starter package | `ad-script-builder/` |
| **Browser extension** (Chrome/Edge): check a text or link from the right-click menu or toolbar, optional red badge on look-alike sites, English and Spanish | Scam Shield | Free; drives people to the site, kit and list. Chrome Web Store listing is its own discovery channel | `scam-extension/` |

Privacy is a selling point for all three: nothing the user types is sent anywhere. The only server code is
one serverless function that checks budget-app license keys.

## Test

```bash
cd apps
npm test            # 130 unit tests, Node 20+, no dependencies
npm run smoke       # opens every page in Chromium at desktop and phone width, and loads the extension (needs Playwright)
```

## Deploy (free)

**One site for everything (quickest):** Netlify > Add new site > Import from GitHub > `cocosl` >
base directory `apps`. You get `/money-calculators/`, `/budget/` and `/scam-checker/` on one URL.
Use its own address, not the Money Made Simple site's: name it **`mms-tools`** (so `https://mms-tools.netlify.app`).
The main site already uses `/budget/` for its budget-by-salary pages, and it links to these tools through `apps_url` in its `site.json`.
`siteUrl` in each app's `config.js` is only the "Made by" link back to the main site, so it stays as is. If you pick a different name, update `apps_url` on the site.

**One site per brand (better for SEO and branding):** create three Netlify sites with base directories
`apps/money-calculators`, `apps/scam-checker` and `apps/budget`. Each has its own `netlify.toml`.
Cloudflare Pages and GitHub Pages also work for the calculators and scam checker (no functions needed).
The budget app's license check needs Netlify Functions (or port the 60-line function to a Cloudflare Worker).

After deploying, update the URLs in each `config.js` (`siteUrl`, `calculatorsUrl`) and run
`node money-calculators/build.mjs` so canonical links and the sitemap point at the real domain.

## Turn on the money (all config, no code)

Every link containing `REPLACE_ME` is hidden automatically, so the apps are safe to deploy today.

1. **Email capture.** Works out of the box on Netlify (Forms > enable form detection, redeploy once).
   For Kit, MailerLite, Buttondown or Formspree, set `email.provider` and `email.action` in `config.js`.
2. **Affiliate links.** Paste your approved links into `affiliates` (calculators) and `offers` (scam checker).
   Brokerage and adviser offers are marked `complianceReview: true`: check FINRA 2210 / SEC Marketing Rule
   before turning them on (see `research/`).
3. **Products.** Set `product.url` to the Gumroad or Stripe Payment Link for The 20-Minute Budget and the
   Family Scam-Proofing Kit.
4. **Budget app Pro.**
   - Gumroad: make two products (monthly membership and one-time), tick "Generate a unique license key",
     put the checkout links in `budget/config.js`, and set the env var `GUMROAD_PRODUCT_ID` on Netlify.
     Buyers paste the key from their receipt into the app.
   - Stripe: make a Payment Link, set its success URL to `https://YOUR-SITE/budget/?session_id={CHECKOUT_SESSION_ID}`,
     put it in `pricing.stripe.url`, and set `STRIPE_SECRET_KEY` (a restricted read-only key) on Netlify.
     Pro switches on automatically when the buyer comes back.
   - Gumroad with several products: the function checks one `GUMROAD_PRODUCT_ID`; give the monthly and
     lifetime options as variants of one product.
5. **Analytics (optional).** Set `analytics.plausibleDomain` in each app's `config.js`. Every page then counts visits (no cookies), sends Affiliate Click / Product Click / Signup events, and tags Gumroad and Stripe links with the visit's UTM so sales are credited to the pin, post or bio that brought the buyer. Setup, goals and the link rules for bios, pins and newsletters: [docs/UTM.md](../docs/UTM.md). `node tools/utm.mjs bios` prints the bio link for every brand and platform; `node tools/utm.mjs check <files>` finds our links that are missing UTM.

Nothing here takes a payment by itself, and nothing goes live until you paste in real links and keys.

## Embeds and licences

`money-calculators/embed/` lets any site embed a calculator with two lines of HTML (`embed.js` makes a
self-resizing iframe; no cookies). Free embeds carry a "Free calculator by Money Made Simple" link, so each
one is a backlink. For paying licensees (credit unions, coaches), set `embed.allowUnbranded: true` and give
them `data-brand="0"`, or deploy a copy with their colours. Set `embed.licenceUrl` to your contact link.

## Browser extension

`scam-extension/` is a Manifest V3 extension built from the checker's own rule engine (`node scam-extension/build.mjs`
copies it in; CI fails if the copy is stale). It asks only for `contextMenus`, `activeTab` and `storage`; the
look-alike badge needs the optional `tabs` permission, which Chrome asks for only when the user turns it on.
To publish: `node scam-extension/package.mjs`, then upload the zip from `scam-extension/dist/` to the Chrome
Web Store (one-time $5 developer fee). Listing text, privacy answers and steps are in `scam-extension/STORE.md`.

## Renaming the scam brand

The brand name and domain live in `scam-checker/config.js`. To rename everywhere (pages, guides and the extension):
`node scam-checker/rename-brand.mjs "Scam Decoded" scamdecoded.netlify.app`.
The checker sells the brand's Family Scam-Proofing Kit (`launch/scam-decoded/product/`); set its URL in
`scam-checker/config.js` > `product.url`.

## Notes and limits

- The free/Pro gate in the budget app runs in the browser, so a determined person could bypass it. That's
  normal for a $3 tool: the cost of stronger DRM (accounts, a database) isn't worth it at this stage.
- The scam checker is rule-based. It catches the common patterns (toll and delivery texts, gift cards,
  crypto, code requests, look-alike links) but it can miss new scams, and the page says so. Add new
  patterns to `RULES` in `scam-checker/lib/scan.js` with a test.
- Scam guide pages are generated from `scam-checker/scams.mjs` by `scam-checker/build.mjs`. Every example
  message there must score high risk in the checker, so adding a guide also tests the checker.
- Spanish wording uses tú and neutral Latin American vocabulary to match Dinero Simple. The Spanish checker (`scam-checker/es/`, `scam-checker/lib/i18n.js`) and calculators need a native speaker's
  read before you promote it, same as the Dinero Simple content. A test fails if any rule lacks Spanish text.
- Calculator pages are generated from `money-calculators/pages.mjs` and `pages-es.mjs` (all on-page result
  wording is in `money-calculators/lib/text.js`) by `build.mjs`; edit the copy there.

See `IDEAS.md` for what to build next.

## Hub search and accessibility

- The hub has a search box over every tool. `node tools/build-search.mjs` writes `search-index.json`
  from the hub's cards plus each page's title, description and headings. Netlify runs it on deploy, and a
  test fails if the committed index is stale. Search runs in the browser; nothing typed is sent anywhere.
- `node tools/a11y.mjs` runs axe-core (WCAG 2.1 A and AA) on the hub and every tool it links to, in
  light and dark mode. It needs Playwright and axe-core (`npm i -D axe-core`, or `AXE_PATH=/path/to/axe.min.js`)
  and skips if they're missing. All 60 page checks passed on 2026-11-07, after colour contrast fixes.
