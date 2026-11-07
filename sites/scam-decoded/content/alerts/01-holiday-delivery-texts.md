---
alert_date: 2026-11-24
severity: warning
scam: "Your package is on hold" texts are spiking before Black Friday
channel: text
sender: a delivery company, from a number you don't know
subject: Scam alert: the "package on hold" text
preheader: A $1.99 redelivery fee is how they get your card. Track packages in the shipper's app instead.
example: USPS: Your package is on hold due to an incomplete address. Update within 12 hours and pay a $1.99 redelivery fee: usps-redeliver-help.com
flags: package is on hold | pay a $1.99 redelivery fee | usps-redeliver-help.com
tell_1: A text you didn't sign up for, from a regular phone number, about a package you can't name.
tell_2: A tiny fee and a short deadline. The fee is the bait; the page wants your full card details.
tell_3: A link that only looks like the shipper's site. The real domain is right before the first single slash.
do_1: Don't tap. Track packages in the shipper's app or by typing its website yourself.
do_2: Expecting something? Check the order page on the store's own site or app.
do_3: Forward the text to 7726 (SPAM), then delete it.
if_already: Typed your card number? Call the number on the back of your card and ask for a new one. Then watch your statement for small test charges.
source_title: FTC: Scammers are delivering phishing messages this holiday season
source_url: https://consumer.ftc.gov/consumer-alerts/2024/12/scammers-are-delivering-phishing-messages-holiday-season
explainer: package-delivery-texts
---
