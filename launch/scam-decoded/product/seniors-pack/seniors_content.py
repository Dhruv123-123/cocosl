"""Content for "Scam Decoded for Seniors", a large-print printable pack ($7, Etsy).

Everything printed lives here so the booklet, fridge checklist and wallet cards stay in sync.
All example calls, texts, names and numbers in examples are fictional. The official numbers in
OFFICIAL_NUMBERS were checked November 2026; re-check them before each new listing version.
"""

TITLE = "Scam Decoded for Seniors"
SUBTITLE = "The large-print guide to spotting phone, text, email and computer scams"
VERSION = "November 2026"

GOLDEN_RULES = [
    ("Don't trust the caller ID.", "Scammers can make any name or number show up."),
    ("Hang up, then call back.", "Use a number you look up yourself: on your card, your bill or the official website."),
    ("Never pay in a hurry.", "Real banks and agencies give you time. Scammers never do."),
    ("Never pay with gift cards, wire transfers, crypto or cash by courier.", "Only scammers ask for these."),
    ("Never share a code.", "If someone asks for the code that was just texted to you, it's a scam."),
]

CALLS = [
    ("The grandchild in trouble",
     "“Grandma, it's me. I'm in jail. Please don't tell Mom.”",
     "Hang up and call your grandchild, or their parent, on the number you already have. Voices can be faked with AI."),
    ("The government",
     "“This is Social Security. Your number has been suspended.”",
     "Social Security, the IRS and Medicare don't call to threaten you or demand payment. Hang up."),
    ("Your bank's “fraud department”",
     "“We've stopped a suspicious charge. Read me the code we just sent.”",
     "Your bank will never ask for that code. Hang up and call the number on the back of your card."),
    ("Computer support",
     "“Your computer has a virus. Let us connect to fix it.”",
     "Microsoft and Apple don't call you. Never let a caller on to your computer."),
    ("You've won a prize",
     "“You've won $2.5 million! Just pay the taxes and fees first.”",
     "Real prizes are never paid for. If you have to pay, you didn't win."),
]

TEXTS = [
    ("“Your package can't be delivered. Pay $1.99 to reschedule.”", "Check the delivery company's own app or website."),
    ("“You owe an unpaid toll. Pay now to avoid a fine.”", "Look up your toll account yourself. Don't tap the link."),
    ("“Your bank account is locked. Tap here.”", "Call the number on the back of your card."),
    ("“Hi, is this Margaret? Sorry, wrong number!”", "Don't reply. A friendly chat that follows often turns into an investment scam."),
]

ONLINE = [
    "Someone you've only met online who soon says they love you",
    "Who can never meet or video chat",
    "Who then needs money for a ticket, a medical bill, customs or a “sure” investment",
]

HANG_UP_LINES = [
    "“I don't do business on the phone. I'll call you back on the number I have.”",
    "“I'm going to check with my family first.”",
    "“Send it to me in writing.”",
    "“No, thank you.” (Then hang up. You don't owe them a goodbye.)",
]

OFFICIAL_NUMBERS = [
    ("Report a scam to the FTC", "ReportFraud.ftc.gov or 1-877-382-4357"),
    ("National Elder Fraud Hotline (US Dept. of Justice)", "1-833-372-8311 (1-833-FRAUD-11)"),
    ("AARP Fraud Watch Network helpline (free for anyone)", "1-877-908-3360"),
    ("Social Security", "1-800-772-1213"),
    ("Medicare", "1-800-633-4227 (1-800-MEDICARE)"),
    ("Stop most sales calls: Do Not Call Registry", "1-888-382-1222 or DoNotCall.gov"),
    ("Forward scam texts for free", "7726 (spells SPAM)"),
]

IF_IT_HAPPENS = [
    ("Stop.", "Don't send any more money, even if they say it will get the first payment back."),
    ("Call your bank", "on the number on your card. Ask them to stop or reverse the payment."),
    ("Gift cards?", "Call the gift card company on the number on the back of the card, and keep the card and receipt."),
    ("Tell someone you trust.", "Scammers count on you keeping it secret. It is not your fault: these are professional criminals."),
    ("Report it", "at ReportFraud.ftc.gov or call the Elder Fraud Hotline: 1-833-372-8311."),
    ("Watch for the second scam.", "Anyone who calls offering to “recover” your money for a fee is another scammer."),
]

FRIDGE = [
    "Caller ID can lie. A real name on the screen means nothing.",
    "Never pay with gift cards, wire transfers, crypto or cash.",
    "Never share a code that was texted to you.",
    "Never let a caller on to your computer.",
    "Hurry + secret + unusual payment = SCAM.",
    "Hang up. Call back on a number you look up yourself.",
    "Not sure? Call someone on my list below first.",
]

LISTING = dict(price=7, title=("Scam Decoded for Seniors, Large Print Scam Awareness Guide, Printable Fridge Checklist "
                               "and Wallet Card, Elderly Parent Gift, Phone Scam Prevention PDF"))
