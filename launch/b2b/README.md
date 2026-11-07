# B2B newsletter products (white label)

Five products plus a one-week package, one engine. Each sells a ready-made, branded monthly or weekly pack that an
organization sends to its own people. Built from existing brand content (Scam Decoded, Money Made
Simple, 1099 Money). **Start with `LAUNCH_CHECKLIST.md`**: what to fill in, what to send first, how to follow up. **Nothing here has been sent or posted.** Dhruv sends every email by hand, payment
links stay as placeholders, and nothing was bought.

| Folder | Product | Buyer | Price | Cadence |
|---|---|---|---|---|
| `credit-union-alert/` | Weekly Scam Alert | Credit unions | $49 / $99 / $149 a month | Weekly |
| `employer-wellness/` | Money Made Simple at Work | Employer HR and benefits teams (and benefits brokers) | $59 / $129 / $249 a month | Monthly |
| `community-scam-watch/` | Scam Watch (large print) | Public libraries, senior centers, Area Agencies on Aging | $19 one site, $49 for 2–4, $12 a location for 5–20, quote 21+; CU-sponsored $99 for 5 sites; talks $150 | Monthly |
| `freelancer-client-letter/` | Freelancer Money Notes | Small CPA, tax and bookkeeping firms, for their 1099 clients | $39 / $79 / $129 a month | Monthly |
| `ncpw-sponsor/` | Consumer Protection Week package (Mar 1–5, 2027) | Credit unions (+ up to 3 local libraries) | $149 one-time, $249 with the library add-on, included for CU Standard/Plus | Daily for one week |
| `schools/` | Money Made Simple for Schools | High school teachers and college advisors (districts, community colleges) | $79 teacher / $299 school / $899 district / $399 college, per school year; or credit-union sponsored | Weekly in the school year |

The first three folders each have: `product.json` (labels, call to action, formats), `issues.json` (12 issues: 3 months for the weekly credit union alert, Jan to Dec 2027 for the monthly products),
`samples/*.md` (readable masters with brand slots shown), `brands/` (a fictional sample brand and a
placeholders brand), `sales-sheet.html`, `COMPLIANCE_NOTE.md`, `COLD_EMAILS.md`, `PROSPECTS.csv` + `.md`
(public-info prospects, with a fit score for employers and accounting firms) and `README.md`. The credit union folder also has the full
`DELIVERY_WORKFLOW.md`; the others describe only what's different. `freelancer-client-letter/` is the lean one: 12 issues, a sales sheet, 40 prospects, and its cold emails and compliance notes inside its README.

## Agreements and invoices: `paperwork.py`

Every offer has `onboarding/services-agreement.html` and `onboarding/invoice.html`, which the build renders to
`out/onboarding/*.pdf`. They're one-page **templates** with every party, price and date as a `{{TOKEN}}`.
**Have a lawyer in your state check the agreement before anyone signs it.** It covers services, approval,
fees, the 30-day exit, the content license, the AI disclosure, no guarantees and a liability cap. To change the
wording, edit `paperwork.py` and run `python3 paperwork.py`, not the generated files. `{{PAYMENT_LINK}}` stays a
placeholder.

## AI disclosure

Every issue footer ends with "Drafted with AI help and fact-checked by a person." This adapts the factory's
disclosure (`src/contentfactory/config.py`) for text-only packs. A client may reword it with `"ai_disclosure"`
in its brand file but can't remove it, and the fact-check has to really happen before each delivery.

## Delivering to a client: `deliver.py`

When a client signs, one command renders a month of issues with their name and logo swapped in:

```
python3 deliver.py credit-union-alert --month 2027-02 --name "Big Sky Credit Union" --short "Big Sky CU" \
    --logo ~/Downloads/logo.png --color "#1D4E89" --set CU_PHONE="(406) 123-4567" --promise "..." --footer "..."
```

It saves the client as `<product>/clients/<slug>.json` (gitignored), so next month is just
`python3 deliver.py credit-union-alert --client credit-union-alert/clients/big-sky-cu.json --month 2027-03`.
Output: `<product>/out/deliveries/<slug>-<month>.zip`, every format for that month's issues, ready to email
to the client yourself. It refuses to build while any sample detail (555 numbers, example.com, "Sample")
is left in the brand, and warns if the issues still need native-language review. Run
`python3 deliver.py --help` for every option.

## Outreach dates: `outreach_dates.py`

`OUTREACH_DATES.md` (and `.csv`) give every B2B prospect an Email 1 date and two follow-up dates in the one
inbox shared with the ad studio. The cap is 10 emails a day (5 new), and from 1 Dec 2026 B2B gets 4 of them
(at most 2 new) while the ad studio keeps 6. Accounting firms go first, in December and early January. The script
reads the ad studio's `OUTREACH_CALENDAR.md` and warns if that calendar uses more than its 6. Rerun it after either
calendar changes. `OUTREACH_DATES_OWN_INBOX.md` is the second-inbox alternative, which costs money, so it isn't the plan.

## Live sample pages

`python3 site/build_site.py` also writes one sample issue per offer, as readers get it, with a banner that says it's a
sample for a fictional organization: `dist/samples/credit-union/`, `employer/`, `scam-watch/` and `accounting-firm/`.
Once the site is on Netlify they live at `https://YOUR-SITE.netlify.app/samples/<offer>/`, which is the link each
product's `FOLLOW_UP_SEQUENCE.md` uses. The site's downloads are the 3-issue demo packs. The full 12-issue packs
are for paying clients only.

## Pitch attachments

Every product's build also writes `out/demo-packet.pdf`: the sales sheet, then the first 3 sample emails, as
one file to attach to a pitch. `out/demo-packet.zip` holds the same 3 issues as email HTML, email PDF and print
files. The Spanish editions (`credit-union-alert/es/`, `community-scam-watch/es/`) get one too.
The employer product also has a **broker partner kit** (`employer-wellness/broker/`): a one-pager with referral fee
placeholders and a co-branded sample pack.

## Build

```bash
cd launch/b2b
python3 build.py                                  # all products: sample + placeholder packs, sales sheet + compliance PDFs
python3 build.py employer-wellness                # one product
python3 build.py credit-union-alert/es            # the Spanish credit union edition (also built by plain build.py)
python3 build.py employer-wellness --brand employer-wellness/clients/acme.json --issue 2027-02
```

`build.py` uses only the Python standard library; PNG and PDF need Node + Playwright (`render.mjs`)
and the compliance PDF needs pandoc. A client pack fails to build if any `{{TOKEN}}` is unfilled.
`*/out/`, `*/clients/` and `site/dist/` are gitignored. The credit union folder also has `roi.html`, rendered to `out/roi.pdf`. Rendered copies are in project files under
`content-factory/b2b/`.

## Landing page (`site/`)

One static page for all four offers: offer cards, how it works, sample images, downloads (sample
packs, sales sheets, the credit union ROI one-pager, compliance notes), a credit union break-even
calculator and a "request a sample" button that opens the visitor's own email app (mailto).

```bash
python3 build.py && python3 site/build_site.py    # writes site/dist/ (about 4 MB)
```

Before deploying, set `salesEmail` in `site/config.js` (it's `REPLACE_ME@example.com`). Then drag
`site/dist/` onto Netlify Drop, or connect the repo with base `launch/b2b/site` and publish `dist`
(build locally first: Netlify's build image has no Playwright for the PNG/PDF step). No analytics,
forms backend or cookies.
