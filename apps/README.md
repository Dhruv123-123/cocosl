# Apps

Three small web apps that earn money without needing an audience first. They pull in search traffic,
capture emails and route people to affiliate offers and paid upgrades. All are static sites (plain
HTML, CSS and JavaScript, no framework, no build step needed) and deploy free.

| App | Brand | How it earns | Folder |
|---|---|---|---|
| **Money calculators** (6 tools) | Money Made Simple | SEO traffic → email list, HYSA / brokerage / debt affiliates, The 20-Minute Budget product | `money-calculators/` |
| **Is this a scam?** message checker | Scam Shield | Identity protection, password manager and VPN affiliates, weekly scam-alert list, $9 Family Scam Safety Kit | `scam-checker/` |
| **The 20-Minute Budget** web app | Money Made Simple | Freemium: Pro at $3/month or $29 once via Gumroad or Stripe | `budget/` |

Privacy is a selling point for all three: nothing the user types is sent anywhere. The only server code is
one serverless function that checks budget-app license keys.

## Test

```bash
cd apps
npm test            # 50 unit tests, Node 20+, no dependencies
npm run smoke       # opens every page in Chromium at desktop and phone width (needs Playwright)
```

## Deploy (free)

**One site for everything (quickest):** Netlify > Add new site > Import from GitHub > `cocosl` >
base directory `apps`. You get `/money-calculators/`, `/budget/` and `/scam-checker/` on one URL.

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
   Family Scam Safety Kit.
4. **Budget app Pro.**
   - Gumroad: make two products (monthly membership and one-time), tick "Generate a unique license key",
     put the checkout links in `budget/config.js`, and set the env var `GUMROAD_PRODUCT_ID` on Netlify.
     Buyers paste the key from their receipt into the app.
   - Stripe: make a Payment Link, set its success URL to `https://YOUR-SITE/budget/?session_id={CHECKOUT_SESSION_ID}`,
     put it in `pricing.stripe.url`, and set `STRIPE_SECRET_KEY` (a restricted read-only key) on Netlify.
     Pro switches on automatically when the buyer comes back.
   - Gumroad with several products: the function checks one `GUMROAD_PRODUCT_ID`; give the monthly and
     lifetime options as variants of one product.
5. **Analytics (optional).** Set `analytics.plausibleDomain` for privacy-friendly stats.

Nothing here takes a payment by itself, and nothing goes live until you paste in real links and keys.

## Notes and limits

- The free/Pro gate in the budget app runs in the browser, so a determined person could bypass it. That's
  normal for a $3 tool: the cost of stronger DRM (accounts, a database) isn't worth it at this stage.
- The scam checker is rule-based. It catches the common patterns (toll and delivery texts, gift cards,
  crypto, code requests, look-alike links) but it can miss new scams, and the page says so. Add new
  patterns to `RULES` in `scam-checker/lib/scan.js` with a test.
- Calculator pages are generated from `money-calculators/pages.mjs` by `build.mjs`; edit the copy there.

See `IDEAS.md` for what to build next.
