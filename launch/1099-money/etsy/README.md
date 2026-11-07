# 1099 Money on Etsy

Etsy's 22 Oct 2026 rule bans AI-generated functional guides: instructions buyers rely on must be the seller's own
work. Our guides say honestly that AI helped draft them, so **only the Quarterly Tax Tracker spreadsheet is sold on
Etsy**, without its PDF guide. Everything else is Gumroad and site only:

| Product | Etsy | Gumroad |
|---|---|---|
| The Quarterly Tax Tracker ($15) | Spreadsheet only (`quarterly-tax-tracker.md`) | Spreadsheet + 10-page guide |
| The Rate & Contract Kit ($29) | No (guide kit) | Yes |
| The Freelancer Money Bundle ($49) | No (includes guides) | Yes |
| The Freelancer Tax Kit ([PRICE]) | No (includes guides) | Yes (`../products/build_gumroad.py`) |

PR #6's `launch/catalog/etsy_rules.py` checks the same rule across every brand's catalog. A guide can go back on
Etsy only if Dhruv rewrites it so it really is his own work.

`python launch/1099-money/etsy/build_etsy.py [out] [--edition 2027]` writes `quarterly-tax-tracker/` with `files/`
(the .xlsx), `images/` (8 photos at 2700x2025, made from the real spreadsheet tabs, upload in number order) and
`LISTING-ETSY.md`. The build fails if a PDF, zip or Word file would go on Etsy.

Other Etsy rules this follows: no links or instructions that send buyers to buy off Etsy, downloads come from the
Etsy Purchases page, at most 5 files of 20 MB each, and the description discloses AI help. Nothing here is listed
yet; listing is a manual step.
