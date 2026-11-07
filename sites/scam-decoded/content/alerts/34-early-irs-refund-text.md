---
alert_date: 2027-01-04
severity: warning
scam: "Your IRS refund is ready" texts, before you've even filed
channel: text
sender: the IRS
subject: Scam alert: the IRS refund text
preheader: The IRS doesn't text you about refunds out of the blue.
example: IRS: You are eligible for a tax refund of $1,272.50. Verify your identity to receive it: irs-refund-claim.com
flags: IRS: | tax refund of $1,272.50 | irs-refund-claim.com
tell_1: The IRS doesn't start contact by text about a refund.
tell_2: A refund you haven't filed for yet.
tell_3: A link that isn't irs.gov.
do_1: Don't tap. Check refunds only at irs.gov, typed in.
do_2: Forward the text to 7726 (SPAM).
do_3: Report it to the IRS as the page below explains.
if_already: Entered your SSN or bank details? Go to IdentityTheft.gov and the IRS identity theft page for next steps.
source_title: IRS: Report fake IRS, Treasury or tax-related emails and messages
source_url: https://www.irs.gov/help/report-fraud/report-fake-irs-treasury-or-tax-related-emails-and-messages
explainer: government-impostor-scams
---
