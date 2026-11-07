# Apps: start here

This folder has 7 Netlify configs, but the two-brand launch (Money Made Simple and Scam Shield)
needs only **2 sites**. Everything works on free Netlify with no blanks filled: links that still
contain `REPLACE_ME` stay hidden, signups fall back to Netlify Forms, and the email box stays off.

## Which sites to put up

| Order | Netlify base directory | What it serves | When |
|---|---|---|---|
| 1 | `apps` | The MMS tools hub, the budget app, money calculators, medical bill letters, wedding, moving and bill-splitter tools, the Spanish hub, search, embeds and the installable MMS app at `/app/` | Launch day |
| 2 | `apps/scam-checker` | Scam Shield: the checker, scam guide pages (EN + ES), quiz, vendor check and the installable scam app at `/app/` | Launch day |
| 3 | `apps/freelance-invoices` | 1099 Money: invoice tracker plus the quarterly tax, mileage and deductions app | When 1099 Money launches |
| 4 | `apps/ad-script-builder` | AI ad studio's free script builder | When the studio site is live |
| skip | `apps/budget`, `apps/money-calculators`, `apps/medical-bills` | Standalone copies of tools already inside site 1 | Only if you want one on its own domain |

Site 1 already includes every folder, so the scam checker also works at `/scam-checker/` there.
Site 2 gives Scam Shield its own domain, which is what the brand needs.

## Netlify steps (same for each site)

1. Netlify > Add new site > Import an existing project > GitHub > `cocosl`.
2. Branch: `main` (after PR #8 merges). Base directory: from the table above.
3. Leave build command and publish directory blank. Each folder's `netlify.toml` sets them,
   plus the functions folder, security headers and no-cache rules for service workers.
4. Deploy. The `ignore` rule skips rebuilds when nothing in that folder changed, which saves build minutes.
5. Site settings > Domain: rename to the domain you want (for example `moneymadesimple-tools`,
   `scamshield`). If it differs from `siteUrl` in that folder's `config.js`, update `siteUrl`
   (and run the scam rename below for site 2) so canonical links and sitemaps are right.
6. Site settings > Forms: turn on form detection, so signups are kept before Sender is connected.

## The blanks, in the order they matter

**Before launch (5 minutes):**
- `siteUrl` in `money-calculators/config.js`, `budget/config.js`, `medical-bills/config.js` (MMS) and
  `scam-checker/config.js` (Scam Shield): set to the real domains.
- Scam brand name: if it isn't "Scam Shield", run
  `node scam-checker/rename-brand.mjs "New Name" newdomain.netlify.app` from `apps/`. It changes
  every page, script and doc and rebuilds the guide pages and extension.

**To collect emails (Sender, free up to 2,500 subscribers):**
- `shared/optin.js`: replace `REPLACE_ME_SENDER_FORM_ID` with the Sender form ID, then
  `node tools/sync-shared.mjs`. Until then the box is hidden (add `?optin=preview` to any page to see it).
- Netlify > Site settings > Environment variables, on sites 1 and 2:
  `SENDER_API_TOKEN` (Sender > Settings > API access tokens), `SENDER_GROUP_ID`, and optionally
  `SENDER_GROUP_SCAM` / `SENDER_GROUP_1099` for a separate list per brand.

**To get paid (each one stays hidden until filled):**
- `budget/config.js`: Pro plan checkout links ($3/month, $29 once), Bill Cut Kit, Money Dashboard Pro,
  Wedding Budget Sheet ($12), Moving Budget Sheet ($9), budget review.
  Pro license checks need one of: `GUMROAD_PRODUCT_ID`, `LEMONSQUEEZY_STORE_ID` + `LEMONSQUEEZY_PRODUCT_IDS`,
  or `STRIPE_SECRET_KEY` as env vars on site 1.
- `money-calculators/config.js`: The 20-Minute Budget link, plus the five affiliate links
  (savings account, brokerage, debt, credit, remittance). Approved programs are in the affiliate kit.
- `medical-bills/config.js`: medical bill pack link.
- `scam-checker/config.js`: Scam-Proof Kit and Spot It Stop It links, plus the three protection
  partner links (identity, password manager, VPN).
- `freelance-invoices/config.js` (site 3): rate and contract kit link.
- `shared/offers.js` > `OFFERS.links`: one tracking link per affiliate category (identity protection,
  password manager, VPN, high-yield savings, 1099 write-off app, credit monitoring, balance transfer), then
  `node tools/sync-shared.mjs`. Each link turns on a labelled "Affiliate link" box under the matching free
  tools (`PLACEMENT` in the same file says which). Add `?offers=preview` to any page to see it. To switch the
  boxes off: `OFFERS.enabled = false`, or list a page in `OFFERS.off`.

**Optional:**
- `analytics.plausibleDomain` in each `config.js`: the domain registered in Plausible. Blank means no analytics script.
- Scam text-line (site 2 only): see `scam-checker/sms/SMS_SETUP.md`. Needs `TWILIO_AUTH_TOKEN`,
  `SMS_HASH_SALT`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`. Skip it at launch.

After editing any `config.js`, run the builds from `apps/` and commit:

```
node tools/sync-shared.mjs
node money-calculators/build.mjs && node scam-checker/build.mjs && node scam-extension/build.mjs
node tools/build-es-hub.mjs && node tools/build-apps-page.mjs && node tools/build-embed-page.mjs && node tools/build-search.mjs
node tools/build-app-shell.mjs
npm test
```

## Check it after deploy

- Open `/` and `/app/` on site 1 and `/` and `/app/` on site 2 on a phone; "Add to Home Screen" should offer the app.
- Submit a test email on any tool page. With Sender connected it lands in the Sender group;
  without it, it shows in Netlify > Forms.
- Nothing marked `REPLACE_ME` should be visible anywhere. If a buy button is showing, its link is filled.

Before going live, also skim `NATIVE_REVIEW_ES.md` (Spanish pages a native speaker should check).

## Every week or two

Refresh Scam Shield's offline phishing list (credits in `THIRD_PARTY.md`):
`node scam-checker/tools/refresh-blocklist.mjs && node tools/build-app-shell.mjs && npm test`, then commit.
The test fails if the file grows past 420 KB.
