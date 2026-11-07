---
alert_date: 2027-01-07
severity: warning
scam: "Your Social Security number has been suspended" calls
channel: call
sender: Social Security or a federal agent
subject: Scam alert: "your SSN has been suspended"
preheader: Social Security numbers don't get suspended. Hang up.
example: This is Agent Ross with the Social Security Administration. Your SSN has been suspended due to suspicious activity. Press 1 to avoid arrest.
flags: Your SSN has been suspended | Press 1 | to avoid arrest
tell_1: A threat of arrest or a suspended number.
tell_2: A caller ID that may look official.
tell_3: They want payment or your number to "fix" it.
do_1: Hang up. Don't press anything.
do_2: Call the agency on a number from its real website if you're worried.
do_3: Report it at ReportFraud.ftc.gov.
if_already: Gave your SSN or paid? Go to IdentityTheft.gov, and call your bank if you paid.
source_title: FTC: How to avoid a government impersonation scam
source_url: https://consumer.ftc.gov/articles/how-avoid-government-impersonation-scam
explainer: government-impostor-scams
---
