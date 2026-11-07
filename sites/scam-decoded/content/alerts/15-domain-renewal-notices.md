---
alert_date: 2026-12-02
severity: watch
scam: Domain "expiration notices" that aren't from your registrar
channel: letter or email
sender: a company that looks like your domain registrar
subject: Scam alert: the domain notice that isn't your registrar
preheader: Check the renewal date inside your real registrar account before paying.
example: DOMAIN NAME EXPIRATION NOTICE for yourbusiness.org. Annual website address listing and search submission: $89. Failure to pay may result in loss of your online presence.
flags: yourbusiness.org | website address listing and search submission | loss of your online presence
tell_1: The name is a close variant of yours, like .org instead of .com.
tell_2: The small print sells a "listing" or "search submission", not your registration.
tell_3: It warns you'll lose your website if you don't pay this sender.
do_1: Sign in to your real registrar account and check the renewal date there.
do_2: Turn on auto-renew with your registrar.
do_3: Tell whoever pays bills: domain bills only get paid inside the registrar account.
if_already: Paid? Call your card company or bank and dispute it. Report it at ReportFraud.ftc.gov.
source_title: FTC halts domain name registration scam
source_url: https://www.ftc.gov/news-events/news/press-releases/2010/08/ftc-halts-cross-border-domain-name-registration-scam
explainer: domain-renewal-notices
---
