---
alert_date: 2027-01-29
severity: warning
scam: "A return was already filed with your SSN"
channel: e-file rejection or IRS letter
sender: the IRS (this one can be real)
subject: Scam alert: someone filed taxes in your name
preheader: Real letters ask you to confirm online at irs.gov. Never through a link in a text.
example: Your e-filed return was rejected: a return using this Social Security number has already been filed for tax year 2026.
flags: was rejected | already been filed | tax year 2026
tell_1: Your e-file is rejected because your SSN was already used.
tell_2: An IRS letter about a return you didn't file.
tell_3: Texts that "help" you fix it are scams.
do_1: Follow the IRS identity theft guide on irs.gov.
do_2: Get an IP PIN at irs.gov to lock future returns.
do_3: Report it at IdentityTheft.gov.
if_already: Already happened? The IRS guide below walks through the forms and steps. Keep copies of everything.
source_title: IRS: Identity theft guide for individuals
source_url: https://www.irs.gov/identity-theft-central/identity-theft-guide-for-individuals
explainer: government-impostor-scams
---
