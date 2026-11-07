# Launch pack: 1099 Money

Money and taxes for US freelancers. Brand file: `brands/1099-money.yaml`. Start with `LAUNCH_DAY.md`.

| File | What it is |
|---|---|
| `content.json` | 24 scripts: 14 Shorts, 8 carousels, 2 long videos (2026 federal figures, sources, claims to verify) |
| `LAUNCH_DAY.md` | What only you can do before Day 1, the 14-day shape, per-post checklist, brand rules |
| `AFFILIATES.md` | Placeholder affiliate links, which post uses which, disclosure wording |
| `month-1/` | 39 more scripts for Nov 30 – Dec 29, 2026 (22 Shorts, 13 carousels, 4 long) + posting plan |
| `../../apps/freelance-tax/` | Free quarterly estimated tax calculator (email signups → the tracker) |
| `product/` | The Quarterly Tax Tracker: spreadsheet builder, the built .xlsx, 10-page guide (HTML + PDF), store listing |

Rebuild everything (offline, no keys needed):

```bash
factory brandkit 1099-money
factory linkpage 1099-money
factory pack export --brand 1099-money --file launch/1099-money/content.json \
  --start 2026-11-16 --days 14 --short-days mon,tue,wed,thu,fri,sat,sun \
  --carousel-days mon,wed,fri,sat --long-days sun --out 1099-money-pack/
python launch/1099-money/product/build_tracker.py
```

Month 1: `factory pack export --brand 1099-money --file launch/1099-money/month-1/content.json --start 2026-11-30 --days 30 --out month-1/` (no `--*-days` flags: it uses the brand cadence).

Add `--render-video` to the export once a voice is connected.
