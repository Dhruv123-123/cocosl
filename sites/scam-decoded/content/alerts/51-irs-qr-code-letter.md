---
alert_date: 2027-01-28
severity: watch
scam: Fake IRS letters with a QR code to "claim your refund"
channel: letter
sender: the IRS
subject: Scam alert: the IRS letter with a QR code
preheader: Check any IRS letter at irs.gov or with the number on irs.gov.
example: Internal Revenue Service: Unclaimed refund of $1,450. Scan the QR code to claim it within 7 days. Have your SSN and bank details ready.
flags: Unclaimed refund of $1,450 | Scan the QR code | Have your SSN and bank details ready
tell_1: A refund you didn't expect, with a deadline.
tell_2: A QR code to scan.
tell_3: It wants your SSN and bank details.
do_1: Don't scan it.
do_2: Check your account at irs.gov, typed in.
do_3: Report it to the IRS as the page below explains.
if_already: Entered your details? Go to IdentityTheft.gov and the IRS identity theft page.
source_title: IRS: Report fake IRS, Treasury or tax-related emails and messages
source_url: https://www.irs.gov/help/report-fraud/report-fake-irs-treasury-or-tax-related-emails-and-messages
explainer: government-impostor-scams
---
