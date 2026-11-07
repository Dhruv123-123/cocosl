---
alert_date: 2027-01-11
severity: watch
scam: "Your new Medicare card is ready, confirm your number" calls
channel: call
sender: Medicare
subject: Scam alert: the Medicare card call
preheader: Don't give your Medicare number to anyone who calls you.
example: Hello, this is Medicare. Your new 2027 card is ready to mail, but we need to confirm your Medicare number and bank details first.
flags: this is Medicare | Your new 2027 card is ready | confirm your Medicare number and bank details
tell_1: A call you didn't ask for.
tell_2: A new card that needs your number confirmed.
tell_3: They ask for bank details too.
do_1: Hang up.
do_2: Call the number on your own Medicare card if you're worried.
do_3: Report it at ReportFraud.ftc.gov.
if_already: Gave your number? Call 1-800-MEDICARE and check your statements for services you didn't get.
source_title: FTC: How to avoid a government impersonation scam
source_url: https://consumer.ftc.gov/articles/how-avoid-government-impersonation-scam
explainer: government-impostor-scams
---
