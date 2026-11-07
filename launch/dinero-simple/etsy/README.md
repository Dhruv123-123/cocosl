# Dinero Simple on Etsy

Etsy-ready, Spanish versions of the five Dinero Simple products. Each folder has the files to upload, three
2000x1500 listing images (upload `mockup-01-hero.png` first; it's the thumbnail) and `LISTING.md` (title,
13 tags, price, description). `listings.csv` has one row per listing.

| Folder | Price | Files |
|---|---|---|
| recorte-de-gastos | $5 | guide PDF + xlsx |
| presupuesto-20-minutos | $12 | guide PDF + xlsx |
| fecha-sin-deudas | $17 | guide PDF + xlsx |
| invertir-con-100 | $19 | guide PDF + xlsx |
| paquete | $29 | start-here map PDF + zip of all four kits |

**Etsy editions.** The PDFs here differ from the store versions in one way: the last pages don't mention
discount codes, a store link or "reply to your purchase email". Those lines point to the Dinero Simple shop
on Etsy and to Etsy messages instead, because Etsy doesn't allow sending buyers off Etsy. Upgrade discounts
for repeat buyers go through Etsy's private coupons.

**Which shop.** An Etsy shop has one main language. Two options:
1. A separate **Dinero Simple** shop with Spanish as its language (cleanest, matches the brand).
2. The existing shop, with these as their own listings. Etsy shows the Spanish text to everyone; the
   English words in the tags ("spanish budget", "spanish planner") help English searches find them.

**Before listing:** a fluent Spanish speaker reads every title, tag, description and the PDFs and
spreadsheets. Listing is a manual step; nothing here is listed yet.

Rebuild after changing a guide: `python launch/dinero-simple/products/build.py`, then
`python launch/dinero-simple/etsy/build_etsy.py --out <folder>`.
