---
alert_date: 2027-01-21
severity: watch
scam: Bank log-in links that are one letter off
channel: text or email
sender: your bank
subject: Scam alert: the bank link that's one letter off
preheader: Read the part right before the first single slash, or use the bank's app.
example: Your account has been locked after 3 failed log-in attempts. Restore access now: secure-chasse-banking.com/login
flags: has been locked | 3 failed log-in attempts | secure-chasse-banking.com
tell_1: A locked account you didn't lock.
tell_2: A link with an extra letter or word in the bank's name.
tell_3: A log-in page that looks exactly right.
do_1: Don't tap. Open your bank's app or type its website.
do_2: Check whether anything's really wrong there.
do_3: Forward it to your bank's fraud email or 7726 (SPAM).
if_already: Typed your password? Change it now, from the bank's app, and call the bank.
source_title: FTC: How to recognize and avoid phishing scams
source_url: https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams
explainer: lookalike-links
---
