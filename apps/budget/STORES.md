# Putting the 20-Minute Budget in the app stores

Nothing here has been submitted. These are the steps and the copy for when you decide to.
Store rules and fees change often: check each item marked **verify** against the current
Google Play and Apple pages before you submit.

## The short version

| | Google Play | Apple App Store |
|---|---|---|
| How | Trusted Web Activity (TWA): a thin Android app that opens the live site full-screen | Capacitor: a native iOS shell around the same web files |
| Account | Google Play Console, one-time $25 | Apple Developer Program, $99 a year |
| Build effort | About half a day | 1 to 2 days, plus a Mac with Xcode |
| Review risk | Low | Medium: Apple rejects apps that are "just a website" (guideline 4.2), so the app needs real native value |
| Selling Pro inside the app | Must use Google Play Billing for digital unlocks (**verify** current US rules) | Must use Apple In-App Purchase for digital unlocks (**verify** current US rules on external links) |
| Store fee on sales | 15% (on the first $1M a year and on subscriptions) | 15% with the Small Business Program (under $1M a year) |

**Recommendation:** start with Google Play only. It's cheap, quick, and it reuses the website as is.
Do iOS once the Android app shows people will install it.

## Before either store

1. **Give the budget app its own domain.** Deploy `apps/budget` as its own Netlify site (base
   directory `apps/budget`), e.g. `budget-moneymadesimple.netlify.app` or a custom domain. Android
   checks a file at the root of the domain (`/.well-known/assetlinks.json`), and that's simpler
   when the app isn't in a sub-folder of a shared site.
2. **Icons are ready:** `icon-192.png`, `icon-512.png` and `icon-maskable-512.png` (made from
   `icon.svg`). The manifest lists them, plus shortcuts to the bill tracker and deal countdown.
3. **Store builds hide web checkout.** Set `distribution: 'play'` or `'appstore'` in `config.js`
   for the build you submit. The upgrade dialog then hides the Gumroad/Stripe buttons and only
   offers "Already have Pro? Enter your license key". See *Payments* below for the decision you
   still need to make.
4. **Privacy:** the app stores everything on the device. It has no accounts and no ads. The only
   network calls are the license check (when someone enters a key) and Plausible page counts if
   you turn analytics on. For the store builds, consider leaving `analytics.plausibleDomain` empty
   so the privacy answers are simply "no data collected".
5. **A privacy policy URL** is required by both stores. Publish a short page on the main site
   (what's stored on the device, the license check, no selling of data, contact email).

## Google Play (TWA)

1. Create a Play Console account ($25 one-time). New personal accounts must run a **closed test
   with at least 12 testers for 14 days** before going to production (**verify** the current
   numbers). Friends and family on Android count.
2. Build the Android wrapper with either:
   - **PWABuilder** (pwabuilder.com): enter the site URL, choose Android, download the package.
     Easiest.
   - **Bubblewrap** (Google's command-line tool): `npx @bubblewrap/cli init --manifest https://YOUR-SITE/manifest.webmanifest`,
     then `bubblewrap build`. Gives you an `.aab` to upload and a signing key.
   Package name suggestion: `com.moneymadesimple.budget`.
3. **Digital Asset Links:** Play shows the SHA-256 fingerprint of the app signing key
   (Play Console > App integrity). Put it in `/.well-known/assetlinks.json` on the budget site:

   ```json
   [{
     "relation": ["delegate_permission/common.handle_all_urls"],
     "target": { "namespace": "android_app", "package_name": "com.moneymadesimple.budget",
                 "sha256_cert_fingerprints": ["AA:BB:...:ZZ"] }
   }]
   ```

   Without it, the app shows a browser address bar at the top.
4. Fill in the listing (copy below), the Data safety form, content rating questionnaire
   (it's a finance tool with no user-generated content), target audience (18+), and upload
   screenshots: at least 2 phone screenshots (**verify** sizes in the Play Console).
5. Payments: Play requires Google Play Billing for digital features bought inside the app.
   A TWA can use Play Billing through the browser's Digital Goods API, which would need a small
   addition to `lib/license.js` and the verify function. Until that's built, ship with
   `distribution: 'play'`: the app is fully usable free, and people who bought Pro on the
   website enter their key.

## Apple App Store (Capacitor)

Needs a Mac with Xcode and an Apple Developer account ($99 a year).

1. In a new folder: `npm init -y && npm i @capacitor/core @capacitor/cli @capacitor/ios`, then
   `npx cap init "20-Minute Budget" com.moneymadesimple.budget --web-dir=www`, copy the contents of
   `apps/budget` into `www/` (with `distribution: 'appstore'` in `config.js`), then
   `npx cap add ios && npx cap open ios`.
2. **Avoid a 4.2 rejection ("minimum functionality").** Apple rejects wrapped websites that add
   nothing. The budget already works fully offline, which helps. Add at least one native feature
   before submitting. The best fit is **local notifications for the promo-end and 0% deadline
   reminders** (`@capacitor/local-notifications`), replacing the `.ics` download in the iOS build.
   Haptics and a native share sheet are cheap extras.
3. The license check calls `/api/verify-license` on the website. In the iOS build, point
   `verifyEndpoint` at the full URL (`https://YOUR-SITE/api/verify-license`) and allow that
   origin in the Netlify function's CORS headers.
4. Payments: digital unlocks bought inside the app must use In-App Purchase (StoreKit), outside
   the exceptions Apple allows (**verify** current US rules on linking to web checkout). The
   simplest first version: free app, no purchase buttons, and Pro unlocks with a key bought on
   the web. Apple tends to reject apps that unlock paid features this way when the app itself
   points people to buy elsewhere, so the iOS build must not mention web prices. Adding StoreKit
   (e.g. via RevenueCat's Capacitor plugin) is the next step if iOS installs justify it.
5. App Privacy ("nutrition label"): "Data Not Collected" if analytics are off in the build.
6. Screenshots: Apple requires a set for the largest iPhone size (**verify** pixel sizes in App
   Store Connect). Take them from the iOS simulator.

## Store listing copy

**App name (30 characters max):** `20-Minute Budget` (16)

**Apple subtitle (30 max):** `Budget, bills and 0% deadlines` (30)

**Google short description (80 max):**
`A private budget you keep in 20 minutes a month, plus bill and 0% deal trackers.` (80)

**Apple keywords (100 max, comma-separated, no spaces needed):**
`budget,budget planner,expense tracker,bills,bill negotiation,0% apr,deferred interest,50/30/20,money` (100)

**Full description (Google 4000 max; also Apple's description):**

> The 20-Minute Budget is a simple monthly budget you can keep up in about 20 minutes a month.
> No bank logins, no ads, no account. Everything stays on your phone.
>
> GIVE EVERY DOLLAR A JOB
> • Enter your take-home pay and split it across needs, wants and savings
> • Log spending in seconds and see what's left in each category
> • Check your 50/30/20 split at a glance
> • Track savings goals
>
> LOWER YOUR BILLS YOURSELF
> • List your internet, phone, insurance and other bills with the date each promo price ends
> • Get a call script for each type of bill
> • Log every call and see what you've saved this year
> • Keep 100% of the savings: no negotiation service taking a cut
>
> BEAT THE 0% DEADLINE
> • Enter a 0% balance transfer, store card or pay-over-time plan
> • See the monthly payment that clears it a month early
> • See what deferred interest would cost if you miss the deadline
>
> PRIVATE BY DESIGN
> Your budget never leaves your device. Back it up to a file any time.
>
> PRO (optional): unlimited categories, every bill and every deal, past and future months,
> CSV import from your bank, unlimited goals and deadline reminders.
>
> Not financial advice. Made by Money Made Simple.

**Apple promotional text (170 max):**
`New: track when every bill's promo price ends, and count down to your 0% deadline so deferred interest never catches you out.` (125)

**Category:** Finance. **Content rating:** Everyone / 4+. **Price:** Free.

**Screenshot captions (one per screenshot):**
1. "Give every dollar a job in 20 minutes a month"
2. "See what's left in every category"
3. "Know when every bill's promo price ends"
4. "Clear your 0% deal before the deadline"
5. "Private: your data stays on your phone"

## Costs summary

| Item | Cost |
|---|---|
| Google Play Console | $25 once |
| Apple Developer Program | $99 a year |
| Mac for the iOS build | Any Mac that runs current Xcode, or a cloud Mac rental |
| Store fees on in-app sales | 15% (both stores, under $1M a year; **verify**) |
| Sales on the website (Gumroad/Stripe) | Unchanged: Gumroad 10% + processing, or Stripe about 2.9% + 30¢ |
