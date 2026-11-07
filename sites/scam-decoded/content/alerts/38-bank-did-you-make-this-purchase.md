---
alert_date: 2027-01-08
severity: warning
scam: "Did you make this $1,180 purchase?" bank texts
channel: text, then a call
sender: your bank's fraud department
subject: Scam alert: "did you make this purchase?"
preheader: Call the number on your card, not the one that calls you.
example: Fraud alert: did you attempt a purchase of $1,180.00 at an electronics store? Reply YES or NO. A specialist will call you to secure your account.
flags: $1,180.00 | Reply YES or NO | A specialist will call you
tell_1: A text that leads to a call from the "fraud team".
tell_2: They ask for a code, your PIN, or to move money.
tell_3: Caller ID can be faked to look like your bank.
do_1: Don't reply. Call the number on the back of your card.
do_2: Never read out a code or move money to "keep it safe".
do_3: Report it at ReportFraud.ftc.gov.
if_already: Moved money or shared a code? Call your bank on the number on your card right away.
source_title: FTC: How to avoid a scam
source_url: https://consumer.ftc.gov/articles/how-avoid-scam
explainer: bank-impersonation-calls
---
