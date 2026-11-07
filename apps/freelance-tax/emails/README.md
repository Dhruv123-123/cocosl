# 1099 Money email sequence

Seven emails that deliver the free 2027 Freelancer Tax Calendar and sell The Quarterly Tax Tracker ($15).
Same front matter as the Money Made Simple sequence (`order`, `day`, `subject`, `preheader`, `goal`), so
it can go into Kit, MailerLite or Buttondown as an automation: trigger = new subscriber on the
`tax-calendar` form, wait `day` days, send.

| # | Day | Email | Job |
|---|---|---|---|
| 1 | 0 | Your 2027 Freelancer Tax Calendar | Deliver the PDF, start the set-aside habit |
| 2 | 2 | Why $60,000 of profit costs $12,037 | The math (SE tax) |
| 3 | 4 | The rule that makes the penalty optional | Safe harbor |
| 4 | 6 | What to pay the IRS, from your own numbers | Main pitch |
| 5 | 8 | The deductions you already earned | Value + soft mention |
| 6 | 11 | "Do I need this if I have a CPA?" | Objections |
| 7 | 14 | What happens from here | Last mention, move to weekly |

**Placeholders to fill before turning it on:**
`{{download_url}}` (https://YOUR-SITE/downloads/freelancer-tax-calendar-2027.pdf),
`{{calculator_url}}` (the site root), `{{tracker_url}}` (the Gumroad link) and `{{price}}` ($15, or $9 at launch).
Add your business mailing address to the footer (CAN-SPAM) and keep the unsubscribe link.

Rules this sequence follows: no fake deadlines or countdowns, every number checkable against the
2026 figures in `../lib/tax.js`, the refund promise matches the store listing (14 days), and the tracker is
mentioned in four emails out of seven, never more than once per email as a link.

**Getting Netlify Forms signups into your email tool:** Netlify > Forms > tax-calendar > export CSV, or
switch `email.provider` in `../config.js` to post straight to Kit, MailerLite or Buttondown.

**Buyers:** people who buy the tracker move to the 3-email buyers sequence in `buyers/` (setup, first payment, one bundle upgrade offer). Pull them out of this sequence when they buy.
