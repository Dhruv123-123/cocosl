# First Year Freelancing: a free 7-lesson email course (lead magnet)

Signup page: `first-year/` (Netlify form `first-year-course`). Same front matter as the main sequence
(`order`, `day`, `subject`, `preheader`, `goal`), so it loads into Kit, MailerLite or Buttondown as an automation:
trigger = new subscriber on the `first-year-course` form, wait `day` days, send.

| # | Day | Lesson | What they do today |
|---|---|---|---|
| 1 | 0 | Three accounts | Open tax savings, move 25% of the last payment |
| 2 | 1 | How first-year taxes work (SE tax, 4 payments, the first-year safe harbor) | Find last year's total tax, divide by 4 |
| 3 | 2 | Records from day one (+ startup costs up to $5,000) | Start a mileage log and a startup-costs note |
| 4 | 4 | Pricing your work ($75/hour floor example) | Run the rate calculator |
| 5 | 6 | Getting paid (agreements, deposits, invoices, W-9, 1099-NEC/1099-K) | Add a deposit and late fee to the next proposal |
| 6 | 9 | Health insurance and retirement on your own | Calendar Nov 1; pick a retirement account |
| 7 | 13 | The first-year calendar (2027 dates) | Put five payment dates in the phone |

**Other email tools:** with Kit, MailerLite or Buttondown every form posts to `email.action`; tag subscribers by the hidden `source` field (`first-year-page`) to start this course instead of the calendar sequence.

**After the course:** move subscribers to the weekly list and the dated deadline reminders in `../reminders/`.
Don't also send them the calendar sequence's emails 2–3, which repeat lessons 2 and 6.

**Placeholders:** `{{calculator_url}}`, `{{rate_calculator_url}}` (…/rate-calculator/), `{{invoice_template_url}}`
(…/invoice-template/) and `{{tracker_url}}` (the store link). Add a mailing address to the footer (CAN-SPAM) and keep the
unsubscribe link.

**Rules this course follows:** every figure comes from the site's 2026 tax model (`../../lib/tax.js`) or an IRS or
healthcare.gov page; the example people are fictional; the only product mention is one link in lesson 7; no fake
deadlines. A test (`test/first-year.test.js`) checks the order, the dates and these rules.
