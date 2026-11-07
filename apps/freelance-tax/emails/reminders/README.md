# Quarterly-tax reminder emails (2027)

Twelve short emails, three per estimated-tax deadline: **one week before**, **the day before** and
**the day after**. They keep the promise in email 7 of the intro series ("a reminder one week before
each deadline"). The day-before and day-after emails are short, so you can drop them if you'd rather
send less.

| # | Send on | Deadline | Email |
|---|---|---|---|
| 1 | Fri Jan 8, 2027 | Fri Jan 15, 2027 | One week to the January 15 payment (4th payment for 2026; choose tax year 2026) |
| 2 | Thu Jan 14 | Jan 15 | Tomorrow: your January 15 payment |
| 3 | Sat Jan 16 | Jan 15 | Paid on January 15? Log it; missed it, pay now; 1099s due Feb 1 |
| 4 | Thu Apr 8 | Thu Apr 15, 2027 | April 15: two payments, one day (2026 return + balance, 1st payment for 2027, IRA/HSA) |
| 5 | Wed Apr 14 | Apr 15 | Tomorrow: file (or extend) and pay |
| 6 | Fri Apr 16 | Apr 15 | The next payment is only 2 months away (payment plans) |
| 7 | Tue Jun 8 | Tue Jun 15, 2027 | One week to the June 15 payment (annualized method, state payments) |
| 8 | Mon Jun 14 | Jun 15 | Tomorrow: your June 15 payment |
| 9 | Wed Jun 16 | Jun 15 | Halfway through 2027's tax payments (mid-year check, one tracker mention) |
| 10 | Wed Sep 8 | Wed Sep 15, 2027 | One week to the September 15 payment (what's after it) |
| 11 | Tue Sep 14 | Sep 15 | Tomorrow: your September 15 payment |
| 12 | Thu Sep 16 | Sep 15 | One payment left for 2027 (Jan 18, 2028) |

**How to send them:** these go out on fixed dates, not a delay after signup, so schedule each one as a
**broadcast** on its `send_on` date (Kit, MailerLite and Buttondown all do this) to everyone on the
list: the `tax-calendar` subscribers and the buyers. For buyers, delete the one tracker line in
email 9 (or send them a copy without it). Send at about 9am Eastern.

**Front matter:** `order`, `send_on` (date to send), `deadline` (the IRS date it's about), `subject`,
`preheader`, `goal`. Same idea as the intro series, with `send_on` in place of `day`.

**Placeholders:** `{{calculator_url}}` (the site root) and `{{tracker_url}}` (the Gumroad link).
Footer: add your mailing address (CAN-SPAM) and keep the unsubscribe link.

**Still to write:** the reminder for the 4th 2027 payment (send about Jan 11, 2028, for Tue Jan 18,
2028), once the IRS publishes the 2027 Form 1040-ES and confirms the date. Email 12 promises it.

**Rules these follow:** every date is a real IRS date for a calendar-year sole proprietor (weekends and
holidays already applied), checked as of November 2026; no countdown timers or invented urgency; the
tracker is linked once in twelve emails; and nothing promises that a payment avoids the penalty, only
that the safe harbor "generally" does. `test/reminders.test.js` checks the dates, weekdays and links.
