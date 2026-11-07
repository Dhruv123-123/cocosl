# Publishing the Scam Shield extension

A Scam Decoded build of the same extension (its own name, colours, icon and explainer links) is made with
`node scam-extension/build.mjs --brand scam-decoded` into `build/scam-decoded/`; zip it with
`node scam-extension/package.mjs build/scam-decoded`. Its listing draft is the "Scam Decoded extension: store
listing draft" doc. Publish one brand or the other, not both: two near-identical listings can be rejected as spam.

Everything below is ready to paste into the Chrome Web Store developer dashboard. Edge Add-ons takes the
same zip and the same text. If the brand is renamed, run `node scam-checker/rename-brand.mjs ...` first:
it rebuilds the extension with the new name.

## Your part (about 30 minutes, once)

1. Make the files: from `apps/`, run `node scam-extension/package.mjs` and `node scam-extension/store-shots.mjs`.
   You'll get `scam-extension/dist/scam-shield-extension-1.0.0.zip`, two 1280x800 screenshots and a 440x280 promo tile.
2. Sign up at https://chrome.google.com/webstore/devconsole (one-time $5 fee) using the brand's Google account.
3. Click **New item**, upload the zip, then fill in the fields below.
4. Deploy the scam checker site first, so `privacy.html` is live for the privacy policy field.
5. Submit for review. Reviews usually take a few days; the narrow permissions help.

## Store listing

**Name** (from the manifest): Scam Shield: Is This a Scam?

**Summary** (132 characters max):
Check any text, email or link for scam red flags in one click. Free, private, and nothing you check leaves your device.

**Category:** Tools. **Language:** English (Spanish is included and shows automatically for Spanish browsers).

**Description:**

Got a text about an unpaid toll? A package that "couldn't be delivered"? A bank alert asking you to verify your account?

Scam Shield tells you in one click whether it has the signs of a scam, and what to do next.

HOW IT WORKS
• Paste a text, email or link into the toolbar button and click Check.
• Or highlight text or right-click any link on a page and choose "Check with Scam Shield".
• You get a risk score, the exact red flags it found, and plain next steps.

WHAT IT CATCHES
• Unpaid toll and fake delivery texts
• Fake bank fraud alerts and "verify your account" phishing
• IRS, Social Security and other government impersonation
• Job, task and crypto investment scams, wrong-number openers
• Gift card, Zelle and crypto payment demands, requests for one-time codes
• Look-alike web addresses like amaz0n-secure.help or paypa1-login.com

OPTIONAL LOOK-ALIKE WARNINGS
Turn on one setting and the toolbar icon shows a red "!" when the site you're on looks like a fake copy of a bank, store or delivery company.

PRIVATE BY DESIGN
Every check runs on your device. Nothing you paste, and none of the sites you visit, is sent to us or anyone else. No account, no ads, no tracking.

EN ESPAÑOL
Si tu navegador está en español, la extensión y los resultados aparecen en español.

Scam Shield is an educational tool. It looks for the patterns common scams use, so it can miss new tricks and can flag real messages. Use it as a second opinion, and when in doubt, contact the company through its official app or website.

## Privacy tab

**Single purpose:** Check messages, links and the current website for signs of a scam, so the user can avoid fraud.

**Permission justifications:**
- `contextMenus`: adds "Check this text/link with Scam Shield" to the right-click menu.
- `activeTab`: when the user opens the extension, reads the current tab's address to say whether it looks like a fake site.
- `scripting`: on that same click, reads the visible words of the current page once, to check them for scam patterns (pressure to pay plus gift cards, unpaid tolls and similar). Runs locally; nothing is stored or sent. No host permissions.
- `storage`: saves one on/off setting for look-alike warnings.
- `tabs` (optional, requested only when the user turns on look-alike warnings): reads each page's address so the extension can show a warning badge on look-alike sites. The check runs locally and nothing is stored or sent.

**Remote code:** No. All code is in the package.

**Data usage:** Tick nothing under "collects". The extension does not collect or transmit any user data.
Certify all three statements (not sold, not used for unrelated purposes, not used for creditworthiness).

**Privacy policy URL:** `https://scamshield.netlify.app/privacy.html` (the page is `scam-checker/privacy.html`).

## Later: making money from it

The extension is free on purpose: it is a discovery channel (people search the store for "scam checker")
that sends people to the site, the $9 Family Scam-Proofing Kit and the scam-alert list. A paid family plan
($2/month: warnings on several family members' browsers, a weekly "scams going around" digest) can be
added later using the same Gumroad/Stripe license check as the budget app.
