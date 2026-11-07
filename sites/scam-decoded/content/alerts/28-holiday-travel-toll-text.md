---
alert_date: 2026-12-22
severity: warning
scam: Unpaid toll texts during holiday travel
channel: text
sender: a toll agency
subject: Scam alert: the holiday road trip toll text
preheader: Check your real toll account. Don't tap the link.
example: TOLL NOTICE: You have an unpaid toll of $4.15 from your recent trip. Pay today to avoid a $35 penalty: toll-roadpay-services.com
flags: unpaid toll of $4.15 | avoid a $35 penalty | toll-roadpay-services.com
tell_1: A small toll with a big penalty.
tell_2: It arrives right when you've been traveling.
tell_3: A link that isn't your toll agency's site.
do_1: Don't tap. Log in to your toll account yourself.
do_2: No balance there? It's fake.
do_3: Forward the text to 7726 (SPAM).
if_already: Paid on that page? Call your card company today and dispute it.
source_title: FBI IC3: Smishing scam targeting toll road users
source_url: https://www.ic3.gov/PSA/2024/PSA240412
explainer: toll-texts
---
