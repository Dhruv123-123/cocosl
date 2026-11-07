# Money Made Simple product line

Five new products next to The 20-Minute Budget (`launch/product/`). Start with `UPSELL_PATH.md`.

| Folder | Product | Price | Files buyers get |
|---|---|---|---|
| `bill-cut-kit/` | The Bill Cut Kit | $5 | 9-page PDF + Bill-Cut-Tracker.xlsx |
| `credit-report-audit-kit/` | The Credit Report Audit Kit | $9 | 12-page PDF + Credit-Audit-Tracker.xlsx |
| `debt-free-date-planner/` | The Debt-Free Date Planner | $17 | 10-page PDF + Debt-Free-Date-Planner.xlsx |
| `investing-starter-kit/` | Start Investing With $100 a Month | $19 | 12-page PDF + Investing-Starter-Calculators.xlsx |
| `money-toolkit-bundle/` | The Money Made Simple Toolkit | $39 | Start Here PDF + all five kits |

Each folder has `guide.html` (the PDF source) and `LISTING.md` (Gumroad copy). Spreadsheets are built by
`sheets.py`. `catalog.json` holds names, prices and the upsell order.

## Build

    python launch/products/build.py --check

Writes PDFs, spreadsheets, zips and store covers (1280x720 + 600x600) to `launch/products/dist/<slug>/`.
Needs Node + Playwright (Chromium) for PDFs and covers; `--check` also recalculates every workbook in LibreOffice
and fails on any formula error. The build fails if any PDF page's text overflows its page.

Edit text in `guide.html`, numbers and tabs in `sheets.py`, then rebuild. Before selling, replace `[your store link]`
on each guide's last page with your real store URL.
