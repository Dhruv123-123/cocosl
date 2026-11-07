---
alert_date: 2027-01-26
severity: urgent
scam: "Your grandson needs bail, a courier will pick up the cash"
channel: call
sender: a grandchild, then a "lawyer"
subject: Scam alert: the courier who comes for bail money
preheader: Hang up and call your grandchild. No court sends a courier for cash.
example: This is his lawyer. Your grandson is in jail after an accident. Bail is $9,000. A courier will come to your house today to collect it. Don't tell anyone.
flags: Bail is $9,000 | A courier will come to your house | Don't tell anyone
tell_1: A family emergency, then a "lawyer" or "officer".
tell_2: A courier sent to your door for cash.
tell_3: Secrecy.
do_1: Hang up and call your grandchild or their parents.
do_2: Never hand cash to a courier.
do_3: Call the police if a courier shows up.
if_already: Already paid? Call your bank and local police right away, then the Elder Fraud Hotline at 1-833-372-8311.
source_title: FTC: Scammers use fake emergencies to steal your money
source_url: https://consumer.ftc.gov/articles/scammers-use-fake-emergencies-steal-your-money
explainer: family-emergency-scams
---
