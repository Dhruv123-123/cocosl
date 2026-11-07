# The January 15, 2027 email series (4 emails)

The four emails for the Jan 15, 2027 estimated payment are already written. They live with the series
they belong to, so they are listed here in send order rather than copied (copies would drift apart, and
subscribers would get each email twice).

| # | Send on | File | Subject | Job |
|---|---|---|---|---|
| 1 | Mon Dec 28, 2026 | `../year-end/02-jan-15-and-your-1099s.md` | Your January 15 number, before the new year | Work out the amount in the quiet week; the file-by-Feb-1 option; what 1099s to expect |
| 2 | Fri Jan 8, 2027 | `../reminders/01-jan-week-before.md` | One week to the January 15 payment | The 15-minute routine, the safe harbor, choosing tax year 2026, open enrollment ends the same day |
| 3 | Thu Jan 14, 2027 | `../reminders/02-jan-day-before.md` | Tomorrow: your January 15 payment | Short reminder with the payment steps |
| 4 | Sat Jan 16, 2027 | `../reminders/03-jan-day-after.md` | Paid on January 15? Do this now | Log it; missed it, pay now; 1099s arrive by Feb 1 |

All four are **broadcasts** on fixed dates to the whole list, about 9am Eastern. The `{{q4_url}}` and
`{{calculator_url}}` placeholders point at the January 15 calculator (`/q4/`) and the site root. Nothing is
scheduled or sent from here; set them up in the email tool by hand.

`test/reminders.test.js` checks the dates and weekdays in the reminder files.
