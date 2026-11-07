# Gumroad storefront kit

`python launch/storefront/build_storefront.py` writes `dist/<brand>/STOREFRONT.md` (profile name, username, bio,
about text, profile sections with products in order, after-purchase recommendations), `avatar.png` (800x800) and
`cover.png` (2400x800) for Money Made Simple, Scam Decoded, 1099 Money and Dinero Simple, plus `dist/CROSS_SELL.md`
and `dist/cross_sell.csv`: what to recommend after each Gumroad purchase, why, where (checkout upsell, receipt note or
email) and the code the product already prints.

The product list comes from `launch/catalog/build_catalog.py`, so it matches `launch/PRODUCTS_CATALOG.md`. The build
fails if a Gumroad product is missing from the sections or has no cross-sell inside its own brand. Nothing is set up on
Gumroad; Dinero Simple's text needs the same native review as its products.

## Spanish storefront and post-purchase emails

- `dist/dinero-simple/GUMROAD_ES.md` (from `gumroad_es.py`): the whole Dinero Simple storefront in Spanish: profile,
  sections, checkout upsells, and for each of the 9 products the Gumroad name, short link, price, button text, card
  summary, tags, description, key points and thank-you message. Links are `[ENLACE: ...]` placeholders.
  NATIVE REVIEW PENDING: nothing goes up before a fluent Spanish speaker reads it.
- `dist/emails/` (from `post_purchase.py`): three emails after each brand's lead product (day 0 thank-you, day 3
  how to use it, day 7 one cross-sell with the code from the cross-sell map). 1099 Money's tracker sequence already
  exists on PR #10 (`apps/freelance-tax/emails/buyers/`) and isn't duplicated. New code to create first: `SEMANA5`.
  Placeholders are `{{double_braces}}`. Nothing is sent or scheduled.
