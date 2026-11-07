---
alert_date: 2026-12-09
severity: watch
scam: "Your reward points expire tonight" texts
channel: text
sender: a store or card you use
subject: Scam alert: "your points expire tonight"
preheader: Check points in the store's own app. The link wants your login and card.
example: Reminder: your 12,400 reward points ($62.00) expire at midnight. Redeem now before they're gone: rewards-redeem-center.top
flags: 12,400 reward points ($62.00) | expire at midnight | rewards-redeem-center.top
tell_1: A specific dollar value to make it feel real.
tell_2: A tonight-only deadline.
tell_3: A link that isn't the store's real website.
do_1: Don't tap. Open the store's own app and check your points there.
do_2: No points there? Delete the text.
do_3: Forward it to 7726 (SPAM).
if_already: Typed your password or card? Change the password, call your card company, and watch for small charges.
source_title: BBB: 12 scams of the holidays
source_url: https://www.bbb.org/all/holiday-hq/scams/12-scams-of-christmas
explainer: lookalike-links
---
