"""Content for "Spot It, Stop It", the Scam Decoded scam-awareness training pack for small teams.

Everything a facilitator presents lives here, so the slides (PPTX + PDF), facilitator guide, quiz and
answer key stay in sync. Build with `python3 build.py` in this folder.
All example emails, names, companies and domains are fictional (domains use the reserved .example TLD).
"""

TITLE = "Spot It, Stop It"
SUBTITLE = "Scam awareness training for teams · 45 minutes"
PRODUCT = "Spot It, Stop It: Scam Awareness Training Pack"
REPORT_PLACEHOLDER = "[how to report at our company: e.g. forward to security@yourcompany.com or call IT on ext. 200]"

# Each slide: kind, title, optional kicker, body (list of bullets or text), notes (speaker notes), minutes.
SLIDES = [
 dict(kind="title", title=TITLE, body=SUBTITLE, minutes=1,
  notes=("Welcome everyone. Over the next 45 minutes we'll look at the scams that target businesses like ours, "
         "how to spot them in seconds, and exactly what to do. Nobody here is being tested on whether they've "
         "been fooled before. These scams fool bankers, accountants and IT people. The goal is that by the end, "
         "everyone knows the three tells, the verify rule, and how to report something here without worrying "
         "about blame.")),
 dict(kind="bullets", kicker="Why this matters", title="Scams aimed at businesses are a people problem, not a tech problem", minutes=2,
  body=["Business email compromise costs US businesses billions of dollars a year (FBI IC3)",
        "Most attacks start with a message to a person, not a hack of a computer",
        "Small businesses are targeted because they have fewer checks",
        "One rushed payment or one shared code can be enough"],
  notes=("The FBI's Internet Crime Complaint Center reports that business email compromise alone costs billions "
         "of dollars a year in the US. [Facilitator: check ic3.gov for the latest annual figure before the "
         "session.] What these scams have in common is that they don't break in through technology. They ask "
         "a person to do something: pay an invoice, change bank details, share a code, buy gift cards. That's "
         "good news, because it means a few habits from everyone in this room stop most of them.")),
 dict(kind="bullets", kicker="Today", title="What we'll cover", minutes=1,
  body=["The 3 tells every scam shares", "Email: phishing, fake bosses, fake invoices, payroll changes",
        "Phone, voice and video: fake IT, codes, voice clones", "The verify rule and how to report here",
        "3 practice scenarios, a short quiz, and your certificate"],
  notes="Quick tour of the agenda. Let people know there's a quiz at the end, it's short, and it's open-book."),
 dict(kind="rules", kicker="Remember this if nothing else", title="Every scam has the same 3 tells", minutes=3,
  body=["Rush: “I need this in the next hour.”",
        "Secrecy or a broken process: “Keep this between us,” “skip the usual approval.”",
        "An unusual payment or request: gift cards, new bank details, crypto, a code, remote access."],
  notes=("Every scam we'll see today uses some mix of these three. Rush stops you thinking. Secrecy, or a "
         "request to skip the normal process, stops you checking with anyone. And the ask itself is unusual: a "
         "payment method we don't use, new bank details, a login code. The rule: if you spot two of the three, "
         "stop and verify. You'll never be in trouble here for slowing down a request to check it.")),
 dict(kind="section", title="Email and messages", minutes=0, body="Phishing · fake bosses · fake invoices · payroll", notes="Section one: email and messages."),
 dict(kind="email", kicker="Anatomy of a phishing email", title="5 red flags in one email", minutes=2,
  email=dict(sender="IT Service Desk <it-support@brightline-helpdesk.example>",
             subject="ACTION REQUIRED: Your mailbox will be disabled today",
             body=("Your email password expires in 2 hours. To avoid losing access to your mailbox and files, "
                   "re-confirm your account now.\n\n[ Keep my mailbox active ]\n\nIT Service Desk")),
  body=["Sender domain isn't ours (brightline-helpdesk.example)", "Urgent deadline: “2 hours”",
        "Threat: losing access", "A login button instead of telling you to use the usual portal",
        "Generic sign-off, no name or ticket number"],
  notes=("Walk through the five flags. Then make the key point: you don't need to spot all five. Any message "
         "that asks you to log in from a link is worth checking by going to the site or app yourself, the way "
         "you normally would. Hover over links on a computer to see where they really go, but don't rely on "
         "that alone, because look-alike domains are easy to miss.")),
 dict(kind="email", kicker="Your turn", title="Spot the fake: what's wrong here?", minutes=3,
  email=dict(sender="Dana Okafor <dana.okafor@brightIine-supply.example>",
             subject="Updated bank details for invoice #4471",
             body=("Hi, quick note before you process this month's invoice. We've moved banks, so please use the "
                   "new account below from now on. Our auditors need the change made today.\n\nNew account: "
                   "[details]\n\nThanks so much, Dana")),
  body=["Look closely at the sender: brightIine (capital I, not l)", "A bank change by email only",
        "“Today” deadline", "No phone call, no paperwork, no change request form"],
  notes=("Give the room 60 seconds before revealing the answers. The sender looks like a real supplier but "
         "uses a capital I instead of a lowercase l. Even if the address were exactly right, the supplier's "
         "real email can be hacked. That's why the rule for any bank detail change is the same: call the "
         "supplier on a number you already have on file, never one in the email, and confirm before changing "
         "anything.")),
 dict(kind="bullets", kicker="Business email compromise", title="The “boss” who needs gift cards", minutes=2,
  body=["“Are you at your desk? I need a quick favour.” from a manager's name",
        "Then: buy gift cards for a client or staff reward, send the codes, keep it quiet",
        "Often sent when the real person is travelling or in meetings",
        "Real managers don't buy gifts with codes over email or text"],
  notes=("This is the most common small-business scam. It starts friendly and vague, then turns urgent. "
         "Scammers check LinkedIn and out-of-office replies to time it. The fix is simple: any request for gift "
         "cards, from anyone, gets a call or an in-person check with that person on their known number. "
         "Ask the room: has anyone had one of these? Most offices have.")),
 dict(kind="bullets", kicker="Fake invoices and bank changes", title="Invoice and vendor payment fraud", minutes=2,
  body=["Fake invoices for services we never ordered", "Real invoices from a hacked supplier, with new bank details",
        "Pressure: late fees, “final notice”, “auditors need it today”",
        "Rule: bank detail changes are always confirmed by phone, on a number we already have",
        "Two people approve new payees and changes"],
  notes=("Invoice fraud works because paying invoices is routine. Two controls stop most of it: any change of "
         "bank details is verified by phone using contact details we already had, not ones in the message; "
         "and new payees or changes need a second person's approval. [Facilitator: name who that second "
         "person is at your company.]")),
 dict(kind="bullets", kicker="Payroll and W-2s", title="Payroll diversion and W-2 requests", minutes=2,
  body=["“Please update my direct deposit to this new account” from an employee's name",
        "“Send me all employee W-2s for a review” from an executive's name",
        "Both are confirmed in person or by phone, never by email alone",
        "Staff: change your own pay details only through our payroll system"],
  notes=("Payroll diversion targets whoever handles payroll. A message looks like it's from an employee asking "
         "to change their bank account before payday. W-2 requests peak in January and February, when a fake "
         "executive asks for every employee's tax forms, which can then be used for tax refund fraud. Both get "
         "a phone call to the real person before anything changes.")),
 dict(kind="section", title="Phone, voice and video", minutes=0, body="Fake IT · codes · voice clones · QR codes", notes="Section two: phone, voice and video."),
 dict(kind="bullets", kicker="Phone scams", title="The fake IT call and the code request", minutes=2,
  body=["“Hi, it's IT. We're seeing an issue with your account, I just need to verify you.”",
        "Then: read me the code we just sent, or approve this sign-in prompt",
        "A flood of sign-in prompts you didn't start? Deny them all and report it",
        "Nobody legitimate needs your one-time code, ever, including our IT team"],
  notes=("This is how many company accounts are taken over. The caller already has the password from a data "
         "breach and needs the second factor. So they call or text pretending to be IT. Our IT team will never "
         "ask you to read out a code or approve a prompt you didn't start. If you get a burst of approval "
         "requests, deny them and report it, because it means someone has your password.")),
 dict(kind="bullets", kicker="AI voice and video", title="Voice clones and deepfake calls", minutes=2,
  body=["A few seconds of audio can be enough to clone a voice",
        "Fake video calls with an “executive” have been used to authorise large transfers",
        "If a call asks for money or sensitive data, verify on a known number or in person",
        "Agree a verification step for urgent payment requests, not just “it sounded like her”"],
  notes=("Voice cloning is cheap now, and criminals have used fake video calls with several 'colleagues' on "
         "screen to talk staff into large transfers. The defence isn't spotting the fake. It's process: urgent "
         "money requests are confirmed by calling the person back on a number we already have, or in person, "
         "however convincing the call was.")),
 dict(kind="bullets", kicker="Texts and QR codes", title="Smishing and QR codes", minutes=2,
  body=["Texts about deliveries, tolls, password resets or “your boss needs you”",
        "QR codes in emails or stuck on posters can lead to fake login pages",
        "Treat a QR code like a link: check where it goes before signing in",
        "Log in to work systems only from the usual app or bookmark"],
  notes=("Phishing has moved to texts and QR codes because they're harder to inspect and often arrive on "
         "personal phones. Same rule as email: don't sign in from a link or code someone sent you. Go to the "
         "app or the bookmark you always use.")),
 dict(kind="section", title="Protect yourself and the company", minutes=0, body="Verify · lock down · report", notes="Section three: what we all do."),
 dict(kind="rules", kicker="The verify rule", title="Stop. Verify on a known channel. Then act.", minutes=2,
  body=["Stop when you see two of the three tells",
        "Verify using contact details you already have: the phone list, the supplier file, in person",
        "Never use the phone number, link or reply address in the message you're checking",
        "Payments: new payees and bank changes need a second person's approval"],
  notes=("This is the single most important slide. Almost every scam today fails if you verify through a "
         "channel the scammer doesn't control. It feels awkward to call a manager to check. Every manager here "
         "has agreed that's exactly what you should do. [Facilitator: if possible, have a manager say this "
         "out loud.]")),
 dict(kind="bullets", kicker="Lock it down", title="4 habits that block most account takeovers", minutes=2,
  body=["A unique password for work accounts, in a password manager",
        "Multi-factor sign-in on, ideally passkeys or an authenticator app",
        "Updates installed when prompted, on laptops and phones",
        "Lock your screen when you step away"],
  notes=("Quick practical habits. If your company has a password manager or MFA policy, mention it here and "
         "how to get help setting it up.")),
 dict(kind="report", kicker="Reporting", title="How to report something here", minutes=2,
  body=[REPORT_PLACEHOLDER, "Report even if you're not sure. Especially if you're not sure.",
        "Report even if you clicked. Fast reports limit the damage.",
        "No blame. The person who reports early is helping everyone."],
  notes=("[Facilitator: replace the first line on this slide with your real reporting route before the "
         "session.] Make the no-blame point clearly. People who are afraid of getting in trouble hide mistakes, "
         "and hidden mistakes are what turn a click into a loss.")),
 dict(kind="bullets", kicker="It happened", title="I clicked, or I paid. Now what?", minutes=2,
  body=["Clicked a link or entered a password: report it now, then change that password",
        "Shared a code or approved a prompt: report it now so IT can lock the account",
        "Sent a payment: call the bank immediately; the first hours matter most for recalling it",
        "Write down what happened, when, and who you spoke to"],
  notes=("Speed matters more than anything. Banks can sometimes recall a wire if contacted within hours. IT "
         "can reset an account before it's used. That's why reporting fast, without fear, is the most valuable "
         "thing anyone can do.")),
 dict(kind="scenario", kicker="Scenario 1 of 3", title="The urgent invoice", minutes=2,
  body=("It's 4:45 pm on Friday. An email from a supplier you use every month says their bank account has "
        "changed and this month's invoice must be paid to the new account today, or they'll stop deliveries. "
        "The email address looks right. What do you do?"),
  notes=("Answer: don't change anything from the email. Call the supplier on the number in our supplier file "
         "(not the email), confirm the change, and follow our two-person approval for bank changes. If you "
         "can't reach them before close, the payment waits until Monday. A real supplier will understand.")),
 dict(kind="scenario", kicker="Scenario 2 of 3", title="The call from IT", minutes=2,
  body=("Your phone rings. “Hi, this is Sam from IT. We've spotted suspicious sign-ins on your account and we're "
        "locking it down. I've just sent you a code, can you read it back so I can confirm it's you?”"),
  notes=("Answer: never read out the code. Hang up and contact IT through the usual route. A real IT team never "
         "needs your code. The fact they're asking means someone else is trying to sign in as you. Report it.")),
 dict(kind="scenario", kicker="Scenario 3 of 3", title="The manager on the road", minutes=2,
  body=("A text from your manager's name: “In back-to-back meetings, can't talk. Need 5 x $200 gift cards for a "
        "client thank-you before 3pm. Send me photos of the codes and I'll sort the expense later. Keep it a "
        "surprise.”"),
  notes=("Answer: all three tells, rush, secrecy and an unusual payment. Don't buy anything. Call your manager "
         "on the number you already have, or ask someone who can reach them. Then report the message.")),
 dict(kind="bullets", kicker="Check what stuck", title="Quiz: 12 questions, 5 minutes", minutes=5,
  body=["Open book, no trick questions", "Pass mark: 10 out of 12", "Answers and explanations straight after",
        "Everyone who completes it gets a certificate"],
  notes="Hand out the quiz. Read the answers out together afterwards using the answer key."),
 dict(kind="rules", kicker="Take these with you", title="The 5 rules", minutes=1,
  body=["Two tells (rush, secrecy, unusual request)? Stop.", "Verify on a channel you already have.",
        "Never share a code or approve a prompt you didn't start.",
        "Bank changes and new payees: phone check + second approval.", "Report fast. No blame."],
  notes="Read the five rules out loud. Point to the poster if you've put it up."),
 dict(kind="title", title="Thank you", body="Questions? · Certificates · " + "Scam Decoded", minutes=1,
  notes="Take questions, hand out certificates, and remind everyone where to report."),
]

QUIZ = [
 ("Which three tells do almost all scams share?",
  ["Spelling mistakes, logos, attachments", "Rush, secrecy or a broken process, and an unusual payment or request",
   "Unknown senders, long emails, links", "Foreign phone numbers, bad grammar, caps lock"], 1,
  "Rush, secrecy and an unusual payment or request. Spot two, stop and verify."),
 ("A supplier emails new bank details for this month's invoice. What do you do first?",
  ["Reply to the email to confirm", "Update the details, the address looks right",
   "Call the supplier on the number already in our files", "Call the number in the email signature"], 2,
  "Always verify bank changes on contact details we already had. Email accounts can be hacked."),
 ("Someone from “IT” calls and asks you to read back a code that just arrived. You should:",
  ["Read it, IT needs it to fix the account", "Hang up and report it through our usual route",
   "Read only the first three digits", "Ask them to email you instead"], 1,
  "Nobody legitimate needs your one-time code. A request for it means someone is trying to sign in as you."),
 ("You get a burst of sign-in approval prompts you didn't start. What's the right move?",
  ["Approve one so they stop", "Ignore them", "Deny them all and report it", "Turn your phone off"], 2,
  "Deny and report. It means someone has your password."),
 ("Your manager texts asking you to buy gift cards urgently and send the codes. You:",
  ["Buy them, it's your manager", "Buy one to be safe",
   "Verify with your manager on a number you already have before doing anything", "Reply asking if it's really them"], 2,
  "Gift card requests are a classic scam. Verify through a known channel; replying goes to the scammer."),
 ("Which of these is the safest way to check a link in an email asking you to log in?",
  ["Click it and see if the page looks right", "Go to the site or app yourself, the way you normally would",
   "Forward it to a colleague to click", "Reply and ask if it's genuine"], 1,
  "Use your usual bookmark or app. Look-alike pages can be perfect copies."),
 ("A voice call sounds exactly like a senior manager approving an urgent transfer. You should:",
  ["Make the transfer, the voice matched", "Ask a personal question",
   "Confirm by calling them back on a known number or in person", "Ask them to send an email too"], 2,
  "Voices can be cloned. Verification through a known channel is what counts."),
 ("An email asks HR for all employees' W-2 forms “for a review today” from an executive's name. HR should:",
  ["Send them, executives are allowed to ask", "Send them as a password-protected file",
   "Confirm with the executive by phone or in person first", "Send only half today"], 2,
  "W-2 requests are a common January scam. Confirm before sending any employee data."),
 ("You clicked a link and typed your password before realising it was fake. What now?",
  ["Say nothing and hope", "Report it right away, then change that password",
   "Wait to see if anything happens", "Delete the email"], 1,
  "Fast reporting limits damage. No blame for reporting."),
 ("A QR code on a poster in the break room says “scan to update your benefits login”. You:",
  ["Scan it and log in", "Treat it like a link: use the usual benefits site or app instead, and report the poster",
   "Scan it but don't log in", "Take a photo of it"], 1,
  "QR codes are links. Sign in only through the usual route."),
 ("Who should approve a new payee or a change of bank details?",
  ["Whoever receives the request", "A second person, after a phone check", "The supplier", "Nobody, it's routine"], 1,
  "Phone verification plus a second person's approval stops most invoice fraud."),
 ("Why is reporting quickly, even when you're not sure, so important?",
  ["It's not; only report confirmed scams", "Banks and IT can often limit or reverse damage in the first hours",
   "So the person can be disciplined", "To fill in a form"], 1,
  "The first hours matter most for recalling payments and locking accounts."),
]
