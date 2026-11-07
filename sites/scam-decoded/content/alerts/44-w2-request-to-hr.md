---
alert_date: 2027-01-19
severity: urgent
scam: The "CEO" who emails HR for every employee's W-2
channel: email
sender: a company executive
subject: Scam alert: the W-2 request to HR
preheader: Confirm any W-2 request by phone or in person before sending anything.
example: Hi, I need copies of all employee W-2s for 2026 in PDF format for a meeting with the accountants. Please send them to me today. Thanks, CEO
flags: all employee W-2s for 2026 | in PDF format | send them to me today
tell_1: An urgent request for everyone's W-2s.
tell_2: It's from an executive, but the reply-to address is off.
tell_3: It's January, when W-2s are ready.
do_1: Call the executive on a known number to check.
do_2: Have a rule: W-2s never go out by email.
do_3: Tell IT and report it.
if_already: Already sent them? The IRS says to report it right away. Tell staff so they can watch for tax identity theft.
source_title: IRS: Form W-2/SSN data theft: information for businesses
source_url: https://www.irs.gov/newsroom/form-w-2-ssn-data-theft-information-for-businesses-and-payroll-service-providers
explainer: 
---
