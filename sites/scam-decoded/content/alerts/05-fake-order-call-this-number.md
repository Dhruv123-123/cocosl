---
alert_date: 2026-11-17
severity: warning
scam: "Your $1,299 order is confirmed" emails with a number to call
channel: email
sender: a big online store or payment app
subject: Scam alert: the order you never placed
preheader: Don't call the number in the email. Check your orders in the store's own app.
example: Order #A-77812 confirmed: MacBook Pro, $1,299.00. Not you? Call our fraud desk within 24 hours at 1-555-0142 to cancel and get a refund.
flags: $1,299.00 | Call our fraud desk | within 24 hours
tell_1: A big purchase you never made, sent to scare you into acting fast.
tell_2: A phone number to call, instead of "check your account".
tell_3: A deadline to cancel. On the call, they'll want remote access to your computer or your bank login "to refund you".
do_1: Don't call the number in the email. Open the store's app or type its website yourself and check your orders.
do_2: No order there? Delete the email. It's fake.
do_3: Forward it to reportphishing@apwg.org and report it at ReportFraud.ftc.gov.
if_already: Called and let them onto your computer? Disconnect it from the internet, call your bank on the number on your card, and change your passwords from another device.
source_title: FTC: How to recognize and avoid phishing scams
source_url: https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams
explainer: fake-order-and-refund-emails
---
