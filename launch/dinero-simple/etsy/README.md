# Dinero Simple on Etsy

> **NOT FOR ETSY (Nov 7 2026).** Etsy has banned AI-generated functional guides since Oct 22 2026, and all five
> products here are guides drafted with AI help. Sell them on Gumroad only. These listings are kept as reference
> in case the rule changes. Planners and logs (no instructions) can still go on Etsy; see `launch/catalog/etsy_rules.py` on PR #6.

Etsy-ready, Spanish versions of the five Dinero Simple products. Each folder has the files to upload, four
2700x2025 listing images (upload `mockup-01-clean.png` first: it's the thumbnail, the pages alone with no text
on them, as Etsy advises) and `LISTING.md` (title under 15 words, 13 tags, price, a description whose first
line says what the item is). `listings.csv` has one row per listing.

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

**Before listing (REVISIÓN NATIVA PENDIENTE):** a fluent Spanish speaker reads every title, tag, description and the PDFs and
spreadsheets. Listing is a manual step; nothing here is listed yet.

Rebuild after changing a guide: `python launch/dinero-simple/products/build.py`, then
`python launch/dinero-simple/etsy/build_etsy.py --out <folder>`.

**November 2026 Etsy SEO pass** (from scouting's audit, `research/scouting/etsy-seo-playbook.md` on PR #2):
titles cut from 20-22 words to 11-14, each description now opens with what the item is, single-word tags are
phrases, and photos are 2700x2025 with a clean first photo (the old text panel is photo 2). The new Spanish
titles and first lines are drafts for the native reviewer. Don't change titles or first photos on a listing
that's selling between about 20 December and 31 January.
