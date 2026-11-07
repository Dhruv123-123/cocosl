# Selling Budget Pro: checkout and license keys

Budget Pro is sold with hosted checkout links, so the site stays static. A buyer pays on the provider's page, gets a license key, and pastes it into the app or `pricing.html`. A small Netlify Function (`netlify/functions/verify-license.mjs`, served at `/api/verify-license`) checks the key with the provider. No card details or provider secrets ever reach the page.

Pick **one** provider. Lemon Squeezy is the recommended one: it is the merchant of record, so it collects and remits sales tax and VAT for you, and it issues license keys itself.

## Option A: Lemon Squeezy (recommended)

1. Create a store at lemonsqueezy.com and finish payout and identity setup.
2. Create the product "Budget Pro" with two variants:
   - Monthly: $3, subscription.
   - Lifetime: $29, single payment.
3. On each variant, turn on **Generate license keys**. Set the activation limit to 5 so a buyer can use a phone and a laptop. For the monthly variant, set the license length to match the subscription.
4. Copy each variant's **checkout link** (Share > checkout URL, which looks like `https://STORE.lemonsqueezy.com/buy/...`) into `config.js` > `pricing.monthly.url` and `pricing.lifetime.url`.
5. Optional: set the product's thank-you button to `https://YOUR-SITE/budget/pricing.html#activate`.
6. In Netlify (Site settings > Environment variables), set:
   - `LEMONSQUEEZY_STORE_ID`: the number under Settings > Stores.
   - `LEMONSQUEEZY_PRODUCT_IDS`: optional, comma-separated. It stops keys for your other products from unlocking Budget Pro.
7. Test in Lemon Squeezy test mode. Buy with test card 4242 4242 4242 4242, paste the key from the receipt, and Pro should turn on.

Validation uses Lemon Squeezy's public license API (`/v1/licenses/validate`), so no API key is needed. The function rejects any key whose `store_id` (and product, if set) isn't yours.

## Option B: Gumroad

1. Create the products, and turn on license keys under Content > License key.
2. Paste the product links into `config.js` > `pricing`.
3. Set `GUMROAD_PRODUCT_ID` in Netlify.

## Option C: Stripe Payment Links

1. Create a Payment Link and set its success URL to `https://YOUR-SITE/budget/?session_id={CHECKOUT_SESSION_ID}`. The app activates itself on return, and the session ID works as the key.
2. Paste the link into `config.js` > `pricing.stripe.url`.
3. Set `STRIPE_SECRET_KEY` in Netlify. Use a restricted key with read access to Checkout Sessions and Subscriptions.
4. Stripe doesn't handle sales tax for you unless you turn on Stripe Tax.

Lemon Squeezy and Gumroad keys can be live at the same time. The function routes UUID-shaped keys to Lemon Squeezy, `cs_` keys to Stripe, and everything else to Gumroad.

## Before you sell

- **Refund policy:** `config.js` > `refundPolicy` is shown on the pricing page. Set the policy you will honour, or `''` to hide it.
- **Prices:** `priceLine` and the `pricing` labels. The free limits are in `lib/plans.js`, and the pricing table reads them from there.
- **App store builds:** set `distribution: 'play'` or `'appstore'`. This hides web checkout, because the stores require their own billing (see STORES.md).

## What's tracked (Plausible, once `analytics.plausibleDomain` is set)

| Event | When | Props |
|---|---|---|
| Upgrade Shown | A free limit shows the upgrade prompt, or someone opens the pricing page | `where`: categories, goals, history, csv, bills, deals, reminders, badge, link, `pricing:<from>` |
| Upgrade Click | A click on any `data-upgrade` link or button: "See Pro", "Get Pro", buy buttons | `where` |
| Product Click | A click on a checkout link. The link is tagged with UTM, plus `checkout[custom][ref]` (Lemon Squeezy) or `client_reference_id` (Stripe), so the sale is credited to its source | `link` |

In Plausible, add Upgrade Shown, Upgrade Click and Product Click as goals. Upgrade Click ÷ Upgrade Shown, broken down by `where`, shows which limit sells Pro.
