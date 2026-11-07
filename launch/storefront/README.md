# Gumroad storefront kit

`python launch/storefront/build_storefront.py` writes `dist/<brand>/STOREFRONT.md` (profile name, username, bio,
about text, profile sections with products in order, after-purchase recommendations), `avatar.png` (800x800) and
`cover.png` (2400x800) for Money Made Simple, Scam Decoded, 1099 Money and Dinero Simple, plus `dist/CROSS_SELL.md`
and `dist/cross_sell.csv`: what to recommend after each Gumroad purchase, why, where (checkout upsell, receipt note or
email) and the code the product already prints.

The product list comes from `launch/catalog/build_catalog.py`, so it matches `launch/PRODUCTS_CATALOG.md`. The build
fails if a Gumroad product is missing from the sections or has no cross-sell inside its own brand. Nothing is set up on
Gumroad; Dinero Simple's text needs the same native review as its products.
