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
| `month-4/` | 39 scripts for Mar 2 – Apr 1, 2027 (22 Shorts, 13 carousels, 4 long at 8+ min): filing, paying the IRS, extensions, the two Apr 15 payments + posting plan |
| `month-5/` | 40 scripts for Apr 2 – May 2, 2027 (22 Shorts, 13 carousels, 5 long at 8+ min): tax day, extensions, the Jun 15 payment, withholding instead of quarterlies, mid-year planning + posting plan |
| `q4/` | Q4 and year-end text posts, Nov 20, 2026 – Jan 15, 2027: 15 posts (LinkedIn, Threads/X, Facebook-group versions) on the Jan 15 payment, year-end equipment and deductions, SEP vs Solo 401(k) and reading 1099s, with square cards; 2 matching emails in `apps/freelance-tax/emails/year-end/` |
| `tax-season/` | Tax-season text posts, Jan 19 – Apr 14, 2027: 20 posts (LinkedIn, Threads/X, Facebook-group versions) on filing, Schedule C, missed deductions, the home office, mileage and the Apr 15 payments, rotating six formats, with cards. Pairs with the site's deduction finder |
| `linkedin/` | LinkedIn growth kit for freelancers and solo consultants: page profile (tagline, overview, specialties), page cover, personal banner and logo, 30 daily posts Nov 16 – Dec 15, 2026 (rates, clients, contracts, invoicing, taxes; links only in first comments), 24 comment templates. Posted by hand from the personal profile. Pairs with the site's rate calculator |
| `drivers/` | Gig-driver series: 10 Shorts for Uber, Lyft, DoorDash, Uber Eats and Instacart drivers, paired with the site's driver mileage calculator (`apps/freelance-tax/mileage/`), with a Wednesday posting plan and the driver communities for each |
| `distribution/ANSWER_BANK.md` | 30 Quora and Reddit answer drafts (18 Quora, 12 Reddit incl. driver subreddits), no links, disclosure and pacing rules |
| `channels/` | `config.json`: launch–month 2 pins, threads and newsletter. `spring.json`: 40 pins from Jan 4, 2027 (month 3–4 content, the calculator, compare pages and 6 Etsy listing pins), 26 threads and 8 newsletter issues Feb 14 – Apr 4. `exclude` drops pins that only make sense on their posting day |
| `b2b/` | Outreach kit: 75 coworking spaces and freelancer groups (45 coworking, 20 translator/interpreter associations, 10 writer, editor and other freelancer groups) with emails verified on their own sites. 3 emails each (free 2027 tax calendar, then the $49 bundle as a member code or group license), tracker at 8 a day from Wed Nov 11, reply branches and draft group-license terms. Nothing sent |
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
Month 4: `factory pack export --brand 1099-money --file launch/1099-money/month-4/content.json --start 2027-03-02 --days 31 --out month-4/`.
Month 5: `factory pack export --brand 1099-money --file launch/1099-money/month-5/content.json --start 2027-04-02 --days 31 --out month-5/`.
Driver series: `factory pack export --brand 1099-money --file launch/1099-money/drivers/content.json --start 2027-01-06 --days 14 --out drivers/` (post on the Wednesdays in `drivers/README.md`).
Spring channels: `factory channels export --brand 1099-money --config launch/1099-money/channels/spring.json --out channels-spring/` (Etsy listing URLs are `REPLACE_ME` until the listings are live).
B2B kit: `python3 launch/1099-money/b2b/build_b2b.py` (edit `leads_source.tsv` or `openers.py`, then rebuild).
Etsy: `python launch/1099-money/etsy/build_etsy.py` (writes to project files).

Long videos from month 1 on are written to run 8+ minutes (about 1,300 words at 160 wpm) so YouTube allows mid-roll ads. Re-time the chapter list in each description after the voice-over is recorded.

Add `--render-video` to the export once a voice is connected.
