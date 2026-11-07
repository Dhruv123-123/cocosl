"""Content for "Don't Get Scammed", the Scam Decoded community talk for libraries, senior centers and churches.

A 45-minute, plain-English talk for older adults and their families. Slides, speaker notes and the handout
all come from here. Example calls, texts and names are fictional. Official numbers checked November 2026.
"""

TITLE = "Don't Get Scammed"
SUBTITLE = "A friendly 45-minute talk on phone, text and online scams"
PRODUCT = "Scam Decoded community talk"

SLIDES = [
 dict(kind="title", title=TITLE, body=SUBTITLE, minutes=1,
  notes=("Welcome, and thank you to [venue] for having me. My name is [name] from Scam Decoded. For the next 45 "
         "minutes we'll look at the scams going around right now, the warning signs they all share, and exactly "
         "what to say and do. There's time for questions at the end, and there's a large-print handout to take home.")),
 dict(kind="bullets", kicker="Before we start", title="Nobody here is being tested", minutes=2,
  body=["Scammers are professionals; this is their full-time job",
        "Doctors, bankers and police officers get fooled too",
        "If it's happened to you, you're in good company, and it's not your fault",
        "Today: what to look for, what to say, and who to call"],
  notes=("Say this slowly. Many people in the room will have had a close call, and some will have lost money. "
         "Shame keeps people quiet, and silence is what scammers count on. Invite people to share stories later "
         "only if they want to.")),
 dict(kind="bullets", kicker="Why this matters", title="Scams are big business", minutes=3,
  body=["Americans report billions of dollars lost to fraud every year (FTC)",
        "Older adults report losing more money per scam than younger people",
        "Most scams start with a phone call, a text or a pop-up",
        "Most can be stopped by one habit: hang up and call back"],
  notes=("[Before the talk: check the latest FTC Consumer Sentinel Data Book and the FBI IC3 Elder Fraud Report "
         "for this year's figures and say them out loud.] The point isn't to scare anyone. It's that these are "
         "organized criminals, and the fix is a simple habit, not a technical skill.")),
 dict(kind="rules", kicker="Remember this if nothing else", title="Every scam has the same 3 warning signs", minutes=3,
  body=["Hurry: “You must act right now.”",
        "Secret: “Don't tell your family or the bank.”",
        "Strange payment: gift cards, wire transfer, crypto, cash by courier, or a code."],
  notes=("This is the slide to remember. Ask the room to repeat it: hurry, secret, strange payment. If you notice "
         "even two of them, stop. Hang up, close the screen, or walk away. You're always allowed to call back later.")),
 dict(kind="section", title="Phone calls", body="Family emergencies · government imposters · your “bank”", minutes=0,
  notes="Section one: phone calls. Ask for a show of hands: who has had a call like this in the last month?"),
 dict(kind="bullets", kicker="Phone calls", title="“Grandma, it's me. I'm in trouble.”", minutes=3,
  body=["A crying “grandchild” or a “lawyer” says they need bail or a hospital payment today",
        "They beg you not to tell Mom or Dad",
        "AI can now copy a voice from a short video clip",
        "Fix: hang up and call your grandchild or their parent on the number you have",
        "Agree on a family safe word"],
  notes=("Explain the safe word: a word only the family knows, never posted online. If a caller can't say it, "
         "it isn't them. Mention that some scammers send a 'courier' to collect cash at the door. No real "
         "court or lawyer does that.")),
 dict(kind="bullets", kicker="Phone calls", title="Social Security, the IRS and Medicare don't call to threaten you", minutes=3,
  body=["“Your Social Security number has been suspended” – it can't be",
        "“There's a warrant for your arrest” – agencies don't call to arrest people",
        "“Your Medicare card is expiring, read me your number” – new cards are free",
        "Fix: hang up and call the agency on its official number"],
  notes=("Social Security's inspector general says Social Security numbers can't be suspended. The IRS usually "
         "contacts people by mail first. Medicare won't call to ask for your number. The official numbers "
         "are on the handout.")),
 dict(kind="bullets", kicker="Phone calls", title="“This is your bank's fraud department”", minutes=3,
  body=["Caller ID shows your bank's real name: that can be faked",
        "They ask you to read back a code “to stop the charge”",
        "Or to move your money to a “safe account”",
        "Your bank will never ask for a code or ask you to move money to protect it",
        "Fix: hang up and call the number on the back of your card"],
  notes=("The code is the key to your account. Whoever has it can get in. Say it plainly: there is no such thing "
         "as a safe account. And caller ID can show any name or number the scammer types in.")),
 dict(kind="scenario", kicker="Practice", title="What would you do?", minutes=3,
  body=("Your phone rings at 7 a.m. A young man crying says, “Grandpa, I was in a car accident and they've "
        "arrested me. Please don't tell Mom. My lawyer will call you about bail.”"),
  notes=("Answer: stay calm, hang up, and call the grandchild or their parent on the number you already have. "
         "Ask for the safe word if you have one. Never pay bail by gift card, wire, crypto or cash courier. "
         "Take two or three answers from the room and praise anyone who says 'hang up'.")),
 dict(kind="section", title="Texts, email and computers", body="Fake delivery texts · scary pop-ups", minutes=0,
  notes="Section two: texts, email and computer screens."),
 dict(kind="bullets", kicker="Texts and email", title="Don't tap the link", minutes=3,
  body=["“Your package can't be delivered, pay $1.99”",
        "“You owe an unpaid toll, pay now to avoid a fine”",
        "“Your account is locked, tap here”",
        "Fix: go to the company's app or website yourself",
        "Forward scam texts free to 7726, then delete them"],
  notes=("The link leads to a fake page that steals card details. The tiny fee is the bait. The person's real "
         "goal is your card number. Show how to forward a text to 7726 if anyone wants help after the talk.")),
 dict(kind="bullets", kicker="Computers", title="The scary pop-up", minutes=3,
  body=["A loud warning: “Virus detected! Call Microsoft now”",
        "Real warnings never give you a phone number to call",
        "Never let a stranger control your computer",
        "Fix: close the browser, or turn the computer off and on",
        "Already let them in? Turn it off and call your bank"],
  notes=("Tech support scammers often end up asking people to log in to their bank 'to receive a refund', then "
         "fake an overpayment and ask for money back. Microsoft and Apple don't call you out of the blue.")),
 dict(kind="scenario", kicker="Practice", title="What would you do?", minutes=3,
  body=("You're reading the news online. Your screen goes red, an alarm sounds, and a message says: “Your computer "
        "is locked. Call Windows Support at 1-8XX-XXX-XXXX immediately.”"),
  notes=("Answer: don't call. Close the browser; if it won't close, restart the computer. The pop-up is just a "
         "web page. If you already called and let them in, turn the computer off, call your bank, and get a "
         "trusted helper to check it.")),
 dict(kind="section", title="Online friends", body="Romance · “sure thing” investments", minutes=0,
  notes="Section three: people we meet online."),
 dict(kind="bullets", kicker="Online friends", title="When a new friend needs money", minutes=3,
  body=["Someone you met online who soon says they love you",
        "Who can never meet or video chat",
        "Who then needs money, or shows you how much they've made on an investment app",
        "Never send money, gift cards or crypto to someone you've only met online"],
  notes=("Romance and investment scams have some of the largest losses. The scammer may spend months building "
         "trust. The investment app can show fake profits, and the money can't be withdrawn. Gently: if a friend "
         "or relative is in one of these relationships, keep talking to them rather than arguing.")),
 dict(kind="scenario", kicker="Practice", title="What would you do?", minutes=3,
  body=("You've been messaging a kind widower for two months. He's working on an oil rig overseas. Today he asks "
        "you to buy $500 in gift cards to pay a customs fee so he can finally come home to meet you."),
  notes=("Answer: it's a scam. Anyone you've only met online who asks for gift cards is a scammer. Stop sending "
         "money, tell someone you trust, and report the profile on the site. It isn't the person's fault for "
         "caring.")),
 dict(kind="rules", kicker="Practice out loud", title="Your hang-up lines", minutes=3,
  body=["“I don't do business on the phone. I'll call you back on the number I have.”",
        "“I'm going to check with my family first.”",
        "“No, thank you.” (And hang up. You don't owe them a goodbye.)"],
  notes=("Have the whole room say each line out loud together. It feels silly and it works: saying it once makes "
         "it easier to say on a real call. Remind people that hanging up on someone isn't rude when they called you.")),
 dict(kind="report", kicker="If it happens", title="The first hour", minutes=3,
  body=["Stop. Don't send any more money.",
        "Call your bank on the number on your card",
        "Gift cards? Call the card company on the number on the back",
        "Tell someone you trust. It's not your fault",
        "Report it: ReportFraud.ftc.gov, or the Elder Fraud Hotline 1-833-372-8311",
        "Beware “recovery” callers who promise to get your money back for a fee"],
  notes=("Acting quickly matters: banks and gift card companies can sometimes stop money that hasn't been spent "
         "yet. The National Elder Fraud Hotline is run by the Department of Justice and staffed by case managers.")),
 dict(kind="bullets", kicker="Questions", title="Questions, and take a handout", minutes=3,
  body=["The large-print handout has the warning signs, hang-up lines and official numbers",
        "Write your bank's number and a trusted contact on it tonight",
        "Free weekly scam alerts: [newsletter link]",
        "Scam Decoded for Seniors, the full large-print pack: [link]"],
  notes=("Take questions. Don't give advice on someone's specific legal or financial case. Point them to their "
         "bank, the Elder Fraud Hotline or a local legal aid office. Mention the pack once, without pressure, "
         "only if the venue agreed to it.")),
]

HANDOUT_NUMBERS = [
    ("Report a scam (FTC)", "ReportFraud.ftc.gov · 1-877-382-4357"),
    ("National Elder Fraud Hotline", "1-833-372-8311"),
    ("AARP Fraud Watch helpline (free)", "1-877-908-3360"),
    ("Social Security", "1-800-772-1213"),
    ("Medicare", "1-800-633-4227"),
    ("Forward scam texts", "7726"),
]
