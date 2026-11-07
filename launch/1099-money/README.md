# Launch pack: 1099 Money

Money and taxes for US freelancers. Brand file: `brands/1099-money.yaml`. Start with `LAUNCH_DAY.md`.

| File | What it is |
|---|---|
| `content.json` | 24 scripts: 14 Shorts, 8 carousels, 2 long videos (2026 federal figures, sources, claims to verify) |
| `LAUNCH_DAY.md` | What only you can do before Day 1, the 14-day shape, per-post checklist, brand rules |
| `AFFILIATES.md` | Placeholder affiliate links, which post uses which, disclosure wording |
| `month-1/` | 39 more scripts for Nov 30 – Dec 29, 2026 (22 Shorts, 13 carousels, 4 long at 8+ min) + posting plan |
| `month-2/` | 40 scripts for Dec 30, 2026 – Jan 29, 2027 (22 Shorts, 14 carousels, 4 long at 8+ min): 1099 season, the Jan 15 payment, deductions + posting plan |
| `month-3/` | 40 scripts for Jan 30 – Mar 1, 2027 (22 Shorts, 13 carousels, 5 long at 8+ min): filing season, Schedule C, home office, mileage + posting plan |
| `etsy/` | `build_etsy.py` + Etsy listings for the three products (Etsy-safe guide wording, 2400x1800 listing images) |
| `../../apps/freelance-tax/` | Free quarterly estimated tax calculator + funnel: free 2027 tax calendar (PDF), landing and download pages, 7-email sequence selling the tracker |
| `product/` | The Quarterly Tax Tracker: spreadsheet builder, the built .xlsx, 10-page guide (HTML + PDF), store listing |
| `products/` | The ladder above it: **Rate & Contract Kit** ($29: rate calculator, project pricer, proposal, agreement, change order, invoices, 7-page guide) and the **Freelancer Money Bundle** ($49: tracker + kit + 14 client email scripts), listings, `UPSELL_PATH.md` with codes and checkout upsells |

Rebuild everything (offline, no keys needed):

```bash
factory brandkit 1099-money
factory linkpage 1099-money
factory pack export --brand 1099-money --file launch/1099-money/content.json \
  --start 2026-11-16 --days 14 --short-days mon,tue,wed,thu,fri,sat,sun \
  --carousel-days mon,wed,fri,sat --long-days sun --out 1099-money-pack/
python launch/1099-money/product/build_tracker.py
python launch/1099-money/products/build_kit.py && python launch/1099-money/products/build_guides.py
```

Month 1: `factory pack export --brand 1099-money --file launch/1099-money/month-1/content.json --start 2026-11-30 --days 30 --out month-1/` (no `--*-days` flags: it uses the brand cadence).
Month 2: `factory pack export --brand 1099-money --file launch/1099-money/month-2/content.json --start 2026-12-30 --days 31 --out month-2/`.
Month 3: `factory pack export --brand 1099-money --file launch/1099-money/month-3/content.json --start 2027-01-30 --days 31 --out month-3/`.
Etsy: `python launch/1099-money/etsy/build_etsy.py` (writes to project files).

Long videos from month 1 on are written to run 8+ minutes (about 1,300 words at 160 wpm) so YouTube allows mid-roll ads. Re-time the chapter list in each description after the voice-over is recorded.

Add `--render-video` to the export once a voice is connected.
