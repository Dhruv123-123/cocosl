# Monthly B2B review (about 30 minutes, last Sunday of the month)

It runs right after the Sunday one-pager, so the month's B2B numbers sit at the bottom of that week's
`factory weekly-review`. Nothing here sends anything.

## 1. Numbers (5 minutes)

```bash
factory weekly-review --save                     # writes output/weekly-review/<sunday>.md
cd launch/b2b
python3 pipeline_tracker.py                      # refresh PIPELINE.xlsx from your PIPELINE.csv edits
python3 b2b_review.py --append-to ../../output/weekly-review/<sunday>.md
```

Before this, copy any edits you made in `PIPELINE.xlsx` back to `PIPELINE.csv` (File > Save as CSV), because
the CSV is what's kept. If `factory weekly-review` isn't set up yet, run `python3 b2b_review.py --save`, which
writes `reviews/<month>.md`.

## 2. Pipeline (10 minutes)

- [ ] **Every send this month is logged.** If "contacts logged" is far below "sends planned", update the
      stages before reading anything else.
- [ ] **Overdue next steps:** do them or close them. A reply waiting more than 2 working days is the most
      expensive line on the page.
- [ ] **Do not contact:** every "no thanks", "unsubscribe" and bounce is marked, and none of them is in next
      month's `OUTREACH_DATES.md` rows.
- [ ] **Reply rate per offer** (after about 30 contacted). Under 5%: change the subject line and first
      sentence before touching the price (`LAUNCH_CHECKLIST.md` §5). Replies but no samples: shorten email 1.
      Samples but no yeses: read the replies against `OBJECTIONS.md` and add any new objection.
- [ ] **Not now (revisit):** anyone whose revisit month is next month gets a date in `next_step_date`.

## 3. Calendar (5 minutes)

- [ ] **Next month's sends fit the shared inbox:** at most 4 B2B a day (2 new) from Dec 1, 2026 alongside the
      ad studio's 6. If the ad studio calendar changed, rerun `python3 outreach_dates.py` and
      `python3 pipeline_tracker.py`.
- [ ] **Seasonal windows:**
  - Accounting firms: none from Jan 16 to Apr 19.
  - The Consumer Protection Week package: orders close Jan 29, deliver by Feb 15.
  - Schools: budgets are set in spring.

## 4. Clients (5 minutes, once anyone has signed)

- [ ] **Deliveries due next month:** run `python3 deliver.py <offer> --client <offer>/clients/<slug>.json
      --month YYYY-MM` for each client, at least 2 days before each `deliver_by`, and email the zip yourself.
- [ ] **Invoices** sent for the month (`<offer>/onboarding/invoice.html`), and payments checked.
- [ ] **One question to each client:** "Anything members/clients asked about this month?" Their answers are
      next quarter's topics.

## 5. Content and facts (5 minutes)

- [ ] **Runway:** any product under 60 days of written issues needs writing (credit unions: from
      `credit-union-alert/CONTENT_CALENDAR.md`, 2 issues ahead).
- [ ] **Sources:** re-open the sources of next month's issues. A page that has moved or changed means the
      issue is fixed before delivery. Run `python3 -m pytest ../../tests/test_b2b.py` after any edit.
- [ ] **Dated facts:** tax thresholds and dates in January, NCPW sources in January (the FTC posts that
      year's materials), and school standards each summer.

## 6. Decide one thing

Write one line at the bottom of the review: what you'll change next month (a subject line, an offer to pause,
a price to test), or "no change".
