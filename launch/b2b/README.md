# B2B newsletter products (white label)

Three products, one engine. Each sells a ready-made, branded monthly or weekly pack that an
organization sends to its own people. Built from existing brand content (Scam Decoded, Money Made
Simple, 1099 Money). **Nothing here has been sent or posted.** Dhruv sends every email by hand, payment
links stay as placeholders, and nothing was bought.

| Folder | Product | Buyer | Price | Cadence |
|---|---|---|---|---|
| `credit-union-alert/` | Weekly Scam Alert | Credit unions | $49 / $99 / $149 a month | Weekly |
| `employer-wellness/` | Money Made Simple at Work | Employer HR and benefits teams (and benefits brokers) | $59 / $129 / $249 a month | Monthly |
| `community-scam-watch/` | Scam Watch (large print) | Public libraries, senior centers, Area Agencies on Aging | $19 / $59 a month, talks $150 | Monthly |

Each folder has: `product.json` (labels, call to action, formats), `issues.json` (4 sample issues),
`samples/*.md` (readable masters with brand slots shown), `brands/` (a fictional sample brand and a
placeholders brand), `sales-sheet.html`, `COMPLIANCE_NOTE.md`, `COLD_EMAILS.md`, `PROSPECTS.csv` + `.md`
(30 public-info prospects) and `README.md`. The credit union folder also has the full
`DELIVERY_WORKFLOW.md`; the other two describe only what's different.

## Build

```bash
cd launch/b2b
python3 build.py                                  # all products: sample + placeholder packs, sales sheet + compliance PDFs
python3 build.py employer-wellness                # one product
python3 build.py employer-wellness --brand employer-wellness/clients/acme.json --issue 2027-02
```

`build.py` uses only the Python standard library; PNG and PDF need Node + Playwright (`render.mjs`)
and the compliance PDF needs pandoc. A client pack fails to build if any `{{TOKEN}}` is unfilled.
`*/out/`, `*/clients/` and `site/dist/` are gitignored. The credit union folder also has `roi.html`, rendered to `out/roi.pdf`. Rendered copies are in project files under
`content-factory/b2b/`.

## Landing page (`site/`)

One static page for all three offers: offer cards, how it works, sample images, downloads (sample
packs, sales sheets, the credit union ROI one-pager, compliance notes), a credit union break-even
calculator and a "request a sample" button that opens the visitor's own email app (mailto).

```bash
python3 build.py && python3 site/build_site.py    # writes site/dist/ (about 4 MB)
```

Before deploying, set `salesEmail` in `site/config.js` (it's `REPLACE_ME@example.com`). Then drag
`site/dist/` onto Netlify Drop, or connect the repo with base `launch/b2b/site` and publish `dist`
(build locally first: Netlify's build image has no Playwright for the PNG/PDF step). No analytics,
forms backend or cookies.
