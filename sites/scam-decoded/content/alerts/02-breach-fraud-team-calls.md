---
alert_date: 2026-12-08
severity: watch
scam: Fake "fraud team" calls after a data breach
channel: call
sender: your bank's "fraud department"
subject: Scam alert: the "your account was in the breach" call
preheader: Your bank won't ask you to read out a code. Hang up and call the number on your card.
example: Hi, this is the fraud team at your bank. Your account was included in the recent data breach. To secure it, please read me the 6-digit code we just sent you.
flags: recent data breach | To secure it | read me the 6-digit code
tell_1: It arrives right after breach news, and uses that news to sound believable.
tell_2: It asks for a one-time code, a password or a PIN. That code signs them in as you.
tell_3: It's urgent, and it wants you to stay on the line rather than call back.
do_1: Hang up and call the number on your card or statement.
do_2: Work through our free data breach checklist at scamdecoded.netlify.app/breached: passwords, two-step sign-in, a credit freeze.
do_3: Report the call at ReportFraud.ftc.gov.
if_already: Read out a code? Change that account's password now from a device you trust, turn on two-step sign-in, and call the bank on the number on your card.
source_title: FTC: Have you been affected by a data breach?
source_url: https://consumer.ftc.gov/consumer-alerts/2022/10/have-you-been-affected-data-breach-read
explainer: breach-follow-ups
---
