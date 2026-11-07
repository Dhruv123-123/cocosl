# Weekly Scam Alert for credit unions (white label)

A B2B product from the scouting memo (`research/scouting/product-ideas-beyond-content.md`, idea #1, on
the scouting branch): a weekly scam alert that credit unions send to their members under their own
brand. **$49 / $99 / $149 a month**, with 2 free months for the first 3 credit unions.

**Nothing has been sent or posted.** Dhruv sends every email himself. Payment links are placeholders.
Nothing was bought.

## What's here

| File | What it is |
|---|---|
| `product.json` | Labels, call-to-action line and formats for this product. |
| `issues.json` | The 4 sample issues (Jan 5, 12, 19, 26 2027 member send dates), rewritten for credit unions from Scam Decoded newsletter research (#22, #8, #9, #11/#13). One source of truth for every format. |
| `samples/week-1.md` … `week-4.md` | Readable master copy of each issue with every brand slot shown as a token: email, lobby, poster, social post, staff brief and sources. |
| `../build.py` (+ `../render.mjs`, shared by all B2B products) | Builds a branded pack per credit union: email HTML + text, 1080×1080 social image + caption + alt text, 1920×1080 lobby slide, letter poster PDF, staff brief, sources. Fails on any unfilled token. |
| `brands/example.json` | A **fictional** credit union ("Sample Community Credit Union", 555 phone, example.org) used for the sample pack. |
| `brands/placeholders.json` | Renders the pack with `{{TOKENS}}` visible, for compliance teams. |
| `sales-sheet.html` | One-page sales sheet with pricing tiers (`build.py` renders it to `out/sales-sheet.pdf`, plus `out/COMPLIANCE_NOTE.pdf` via pandoc). |
| `roi.html` | ROI one-pager: cost vs writing it in-house, break-even, fill-in table for their own numbers (renders to `out/roi.pdf`). |
| `COMPLIANCE_NOTE.md` | No legal advice; sourcing rules; NCUA advertising, UDAAP, Reg E, CAN-SPAM, GLBA/vendor, accessibility, social, SMS; fact-check list. |
| `COLD_EMAILS.md` | Email 1 (two versions), contact form, LinkedIn note, 2 follow-ups, final note, and replies to 9 common answers. |
| `PROSPECTS.csv` + `PROSPECTS.md` | 60 credit unions from NCUA call report data (Q2 2026): batch 1 in MT/ID/OR/WA, batch 2 in WY/UT/CO. |
| `CONTENT_CALENDAR.md` + `.csv` | 12 weeks of planned issues after the samples (member sends Feb 2 to Apr 20 2027), with delivery, fact-check and write-by dates, Scam Decoded source issue and official sources. |
| `es/` | Spanish edition of the 4 samples (Plus tier), in Dinero Simple's style using usted. **Not yet reviewed by a native speaker**: see `es/REVIEW_CHECKLIST.md`. |
| Sponsored Scam Watch | Add-on for any plan: **$99 a month** to sponsor Scam Watch (the large-print monthly in `../community-scam-watch/`) at up to 5 local libraries or senior centers, marked "brought to you by [credit union]". Same build: a Scam Watch brand file per location with the credit union's name in `credit_line`. That line prints on the email edition today; make it print on the handout and flyer too before the first sponsored sale. |
| `onboarding/` | First-client kit: kickoff email series, brand intake form (PDF), approval workflow and sign-off log, invoice template with `{{PAYMENT_LINK}}` (PDF). |
| `DELIVERY_WORKFLOW.md` | How each weekly issue is picked, written, checked, built, delivered and corrected; client onboarding. |

`out/` and `clients/` are gitignored. Rendered copies live in project files at
`content-factory/b2b/credit-union-alert/`.

## Build

```bash
cd launch/b2b
python3 build.py credit-union-alert                # sample pack + placeholder pack + samples/*.md + PDFs
python3 build.py credit-union-alert --brand credit-union-alert/clients/<slug>.json   # a real client
```

Python standard library only; images need Node with Playwright (already in the cloud sessions).

## Dhruv's next steps

The full list for all three products is in `../LAUNCH_CHECKLIST.md`. For credit unions:

1. Fill `{{YOUR_NAME}}`, `{{YOUR_EMAIL}}`, `{{YOUR_PHONE}}` in `sales-sheet.html` and run
   `python3 build.py credit-union-alert` from `launch/b2b/` (it also writes `out/sales-sheet.pdf` and `out/COMPLIANCE_NOTE.pdf`).
2. Fill `website` and `contact_route` for the first 8 rows of `PROSPECTS.csv` (about 3 minutes each).
3. Send email 1 from `COLD_EMAILS.md` to 5 to 8 a day. Attach nothing to the first email.
4. When someone says yes: send `out/sample-community-cu.zip`, `out/sales-sheet.pdf` and the compliance
   note. Then make their branded version (`DELIVERY_WORKFLOW.md`, onboarding).

## Open decisions

- **Brand name:** this uses "Scam Decoded", which is still waiting on the name decision (Scam Decoded vs.
  other options). The member-facing packs don't show our name at all, so only the sales sheet and
  emails would change.
- **Spanish edition and exclusivity** are in the Plus tier. Spanish samples exist in `es/` but need a
  native review first. Drop Spanish from the sheet if you don't want to promise it yet.
