---
alert_date: 2026-12-28
severity: warning
scam: "Your refund failed, confirm your card" emails
channel: email
sender: a store you just returned something to
subject: Scam alert: the refund that "failed"
preheader: Check returns in the store's app. Refunds don't need your full card.
example: We couldn't process your refund of $86.40. Confirm your card details within 48 hours to receive it: returns-refund-verify.com
flags: couldn't process your refund | Confirm your card details | returns-refund-verify.com
tell_1: It arrives after the holidays, when lots of people have returns.
tell_2: It asks you to re-enter your card.
tell_3: A link that isn't the store's real site.
do_1: Don't click. Check the return in the store's app or account.
do_2: Delete the email.
do_3: Forward it to reportphishing@apwg.org.
if_already: Typed your card? Call your card company and ask for a new card.
source_title: FTC: How to recognize and avoid phishing scams
source_url: https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams
explainer: fake-order-and-refund-emails
---
