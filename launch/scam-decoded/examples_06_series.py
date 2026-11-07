"""Worked examples for the 8 series parts (Jul 2027 - Feb 2028): one composite victim per case, followed
step by step. The narration says each is a made-up composite, not a person from the court record."""

EXAMPLES = {
    "How the scam actually worked: the 'bail money' calls": ("Step 5: the money", [
        ("One afternoon, from the inside", "A composite, not a real victim",
         "Let's put the steps together in one afternoon. This is a made-up composite, not a person from the "
         "court record. Helen is seventy-nine and lives alone in Vermont. At one o'clock her phone rings: 'Grandma, "
         "it's me.' She says, 'Danny?' and the caller says yes. He's crying, there was a crash, he's been "
         "arrested, and please don't tell his mom.",
         "an older woman in a farmhouse kitchen answering a landline, snow outside the window"),
        ("The lawyer's numbers", "1:15 pm: '$9,000, cash, today'",
         "At one fifteen a calm man calls, says he's Danny's lawyer, and gives a case number. Bail is nine "
         "thousand dollars. Because the other driver was pregnant, there's a gag order, so she mustn't discuss it "
         "with anyone, including the bank. A bondsman will come to the house at four. Helen drives to the bank and "
         "tells the teller the cash is for a new roof.",
         "a woman at a bank counter with an envelope, a teller looking concerned"),
        ("The knock, and the second call", "4:00 pm: a courier. 6:00 pm: more",
         "At four a young man in a polo shirt collects the envelope at the door and thanks her. At six the lawyer "
         "calls back: the other driver lost the baby, the charge is now more serious, and bail is another fifteen "
         "thousand. That second call is common in these schemes, because a person who has paid once has shown they "
         "believe the story.",
         "a front door at dusk with an envelope being handed over, a phone ringing on a table"),
        ("Where it could have stopped", "Each step had an exit",
         "Now go back through the afternoon and find the exits. At one o'clock: hang up and call Danny's own "
         "number. At one fifteen: ask for the family safe word, or call his mom anyway, gag order or not. At four: "
         "no court or bail office sends a courier for cash. Any one of those ends it. In this composite, Helen's "
         "neighbour sees the second courier and asks what's going on, and that's what finally stops it, nine "
         "thousand dollars too late.",
         "a timeline with three exit signs, a neighbour talking with an older woman at a fence"),
    ]),
    "The $26 million pop-up": ("Why it works", [
        ("One evening, step by step", "A composite: Ray, 68",
         "Here's the whole funnel in one evening. A made-up composite, not a person from the FTC's case. Ray is "
         "sixty-eight and reading the news on his laptop when a window that looks like a Windows alert says his "
         "computer may be infected. He clicks scan. A progress bar runs and lists hundreds of 'issues', some in "
         "red. He buys the fix for about thirty-nine dollars, which feels sensible.",
         "an older man at a laptop in a den, a fake system alert window with a progress bar"),
        ("The activation call", "'Call to activate': the real pitch",
         "The software asks him to call a number to activate it. A friendly technician asks to connect to his "
         "computer to 'make sure it installed'. He opens a system log Ray has never seen, full of warnings and "
         "errors, the routine messages every computer collects, and says it's worse than they thought. Hackers may "
         "already be in. The full repair and protection plan is a few hundred dollars more.",
         "a phone call with a technician icon, a screen full of error messages, a worried user"),
        ("What Ray's daughter saw", "A clean computer, a big bill",
         "Ray pays. When his daughter visits that weekend, she runs the security tool already built into his "
         "computer, and it finds nothing serious. The only new things on the machine are the purchased program "
         "and the remote access tool the technician left behind. She uninstalls both, changes his passwords, and "
         "calls his card company to dispute the charges.",
         "a daughter at her father's laptop removing two programs, a phone call to a card company"),
        ("Where it could have stopped", "The exits: close, don't call",
         "The exits were early. A pop-up that tells you to scan or call isn't a real security warning, so close "
         "the tab. A scan that can't come back clean isn't a test. And never give remote access to someone you "
         "reached from a pop-up. In this composite, a card dispute might get some money back. In the real case, "
         "the FTC's refunds did that for many people, years later.",
         "a browser tab being closed, a padlock over a remote access icon"),
    ]),
    "How the scam actually worked: the fake invoices": ("Why it matters to you", [
        ("The same trick at small scale", "A composite: a house closing",
         "Here's the same trick at the size most of us live at. A made-up composite, not part of this case. "
         "Priya and Sam are buying their first house. Two days before closing, they get an email that looks like "
         "it's from their title company, same logo, same agent's name, saying the wiring instructions for the "
         "down payment have changed because of an audit. Please wire sixty-two thousand dollars to the new "
         "account today.",
         "a young couple at a laptop with a house key and a closing folder, an email with a logo"),
        ("Why it looks right", "One letter off in the address",
         "Look at it the way the tech companies' staff saw their invoices. The name matches. The amount matches "
         "what they expected. The timing matches. One thing changed: where the money goes. And the sender's email "
         "address is one letter off from the real one, which is easy to miss on a phone. Somewhere, someone got "
         "into an email thread and waited for the right moment.",
         "an email address under a magnifying glass with one letter highlighted"),
        ("The call that saved it", "Call a number you already had",
         "Sam calls the title agent on the number printed on their purchase contract, not the one in the email. "
         "The agent says the instructions haven't changed and that they never change instructions by email. "
         "Sixty-two thousand dollars stays where it belongs. They forward the email to the title company and "
         "report it to the FBI at I C 3 dot gov.",
         "a man on a phone holding a printed contract, a relieved partner beside him"),
        ("If the wire had gone", "Wire sent? Call the bank now",
         "If the wire had gone out, speed is everything. Call your bank immediately and ask it to recall the wire "
         "and contact the receiving bank, then file at I C 3 dot gov the same day. Money that's been moved on, "
         "like the payments in this case that went through several countries, gets much harder to recover with "
         "every hour.",
         "a clock face with a bank building and an arrow racing toward a border"),
    ]),
    "'Google will remove your business'": ("Why it worked", [
        ("One salon, one call", "A composite: Dee's salon",
         "Let's walk one call through, as a made-up composite, not a business from the FTC's case. Dee runs a "
         "two-chair hair salon. On a busy Saturday, a recording says her Google listing will be marked "
         "permanently closed. She's between clients and presses one, because closed sounds like the end of her "
         "walk-in trade.",
         "a small hair salon with two chairs, a stylist holding a phone between appointments"),
        ("The specialist", "'$499 to verify and boost you'",
         "A friendly 'specialist' says her listing isn't verified and that, for a one-time fee of four hundred "
         "ninety-nine dollars, they'll verify it and get her to the top of local search. He can take a card now. "
         "Every piece sounds close to true. Listings can be verified. Search position matters. Dee pays, because "
         "the cost of losing customers feels bigger.",
         "a phone call with a headset icon, a card being read out, a search ranking arrow"),
        ("What she finds later", "Free to claim. Nothing changed.",
         "A month later, a regular mentions she found the salon fine on Google, same as always. Dee signs in to "
         "her Business Profile herself for the first time and finds it was never at risk, and claiming and "
         "managing it is free. Nothing was done for the four hundred ninety-nine dollars. She calls her card "
         "company to dispute it and reports the call at the FTC's site.",
         "a laptop showing a business profile with a verified check, a phone call to a card company"),
        ("The exits", "Hang up. Sign in yourself.",
         "The exits: Google doesn't robocall you about your listing, so pressing one is the first mistake. "
         "Signing in to your own profile answers the question in two minutes. And a fee to keep something that's "
         "free is the tell. Put those on a sticky note by the salon phone, because these calls still come, under "
         "new names.",
         "a sticky note on a salon phone with three short rules"),
    ]),
    "How the scam actually worked: inside the IRS impersonation": ("Step 4: the runners", [
        ("One call, one family", "A composite: Mr. Patel, 1 morning",
         "Here's how one call could move through the whole machine, as a made-up composite, not a victim named in "
         "the case. Mr. Patel, a recent immigrant, gets a call at nine in the morning. The caller knows his name "
         "and address, says he's from the IRS, and says there's an error in his tax filings and an arrest warrant. "
         "Then a second voice, from 'immigration', says his status could be affected.",
         "a man in a small apartment taking a phone call, a coffee going cold, morning light"),
        ("The payment", "'Buy cards. Read the numbers.'",
         "They tell him to stay on the line, drive to a store, and buy four prepaid cards worth five hundred "
         "dollars each. In the car park, he reads the numbers off the back. Within minutes, according to the way "
         "the pleas describe it, numbers like these are sent overseas, loaded onto cards registered with stolen "
         "identities, and a runner somewhere in the US is already withdrawing cash or buying money orders.",
         "a man in a car reading numbers from cards into a phone, a map with a fast arrow"),
        ("The knock that never came", "No officers. No warrant.",
         "Officers never come, because there was never a warrant. When Mr. Patel tells a coworker, she shows him "
         "the IRS page that says the IRS doesn't demand immediate payment by gift card or prepaid card, and "
         "doesn't threaten arrest by phone. He reports it to TIGTA, and calls the card company, which may be able "
         "to freeze any balance not yet spent. Most of it is gone.",
         "two coworkers looking at an official website on a phone, a report form on a laptop"),
        ("Where the exits were", "The tell: how they want paid",
         "The exit was the payment method. The IRS doesn't take gift cards or prepaid cards read over the phone, "
         "and no agency asks you to stay on the line while you drive to a store. Notice also who the composite "
         "is. The fear of deportation is what made him less likely to check, and less likely to report. If you "
         "have neighbours or coworkers new to the country, this is the call to warn them about.",
         "a set of prepaid cards with a large red cross over them"),
    ]),
    "Inside a pig butchering compound": ("Step 5: the laundering", [
        ("From the other side of the chat", "A composite: Ken, 54",
         "Now see it from the phone in your hand. A made-up composite, not a victim named in this case. Ken is "
         "fifty-four and divorced. A wrong-number text from 'Anna' turns into a friendship. She sends photos of "
         "her dinners and her dog. After three weeks she mentions her uncle's crypto trading platform, and that "
         "she's made enough to put a deposit on a flat.",
         "a man on a couch smiling at a phone, a chat with a photo of a dinner and a dog"),
        ("The numbers on the screen", "$5,000 becomes '$9,200'",
         "Ken signs up through her link and deposits five thousand dollars. Within two weeks the site shows nine "
         "thousand two hundred. He withdraws two hundred, and it arrives, which settles his doubts. Over two "
         "months he moves in sixty thousand, including a loan. The site shows a hundred and ten thousand. None of "
         "it exists. The numbers are typed into a website the scammers control.",
         "a phone app with a rising chart and a large fake balance, a small real deposit icon"),
        ("The wall", "'Pay 15% tax to withdraw'",
         "When Ken asks to withdraw, the account is frozen for a 'compliance review'. Release requires a fifteen "
         "percent tax up front. Anna says she'll lend him part of it. Then comes a second fee. Meanwhile, on the "
         "other side of the screen, the person typing as Anna may be one of the trafficked workers this case "
         "describes, working from a script.",
         "a locked vault icon on a phone, a fee notice, a tired worker silhouette at a desk far away"),
        ("The exits", "4 exits before the first deposit",
         "Count the exits, all before the first deposit: a wrong-number text that kept going, a move to private "
         "chat, an investment tip from someone he'd never met, and a platform he only reached through her link. "
         "And one big one at the end: never pay a fee to withdraw your own money. Ken reports it at I C 3 dot gov "
         "with every wallet address and screenshot, which is how cases like this get built.",
         "a road with four exit signs passed and one large stop sign at the end"),
    ]),
    "How the scam actually worked: the money transfer company": ("The lesson", [
        ("One transfer, followed", "A composite: Joan's 'prize'",
         "Let's follow one transfer through the pipe. A made-up composite, not a person from this case. Joan, "
         "seventy-two, is told on the phone that she's won a large lottery prize in another country, but must "
         "first pay taxes and fees. The caller tells her to go to a store and send nine hundred dollars by money "
         "transfer to a 'customs officer', and read back the reference number.",
         "an older woman at a store counter filling out a money transfer form, a phone in her other hand"),
        ("At the counter", "The agent who doesn't ask",
         "At the counter, the form has a fraud warning on it, and the clerk could ask who she's sending to and "
         "why. In this version, he doesn't. Joan sends it, reads the number to the caller, and within minutes the "
         "money is picked up in cash somewhere else. Two days later, a new call: more fees, another transfer. That "
         "pattern, repeated payouts tied to fraud reports, is what the FTC's case was about.",
         "a counter with a transfer receipt, a cash pickup happening in a distant city"),
        ("What changes after the order", "Warnings, blocks, refunds",
         "After the order, the system is meant to work differently. Transfers to people who've been reported for "
         "fraud get blocked. Agents with too many fraud reports face action. And the form's warning is there for "
         "the moment Joan is standing at the counter. If she'd told the clerk it was for a prize, a well-trained "
         "agent should stop and explain that real prizes don't charge fees.",
         "a transfer form with a warning box highlighted, a clerk speaking kindly to a customer"),
        ("What Joan should do", "Call the company before pickup",
         "And Joan herself? The fastest move is to call the transfer company the moment she realises, because "
         "until the money is picked up, it can sometimes be stopped. Then report it at ReportFraud dot FTC dot "
         "gov. And the rule for next time: anyone who tells you to pay a prize fee, by transfer, gift card or "
         "crypto, is the scam.",
         "a woman on the phone with a transfer receipt, a stop sign over a cash pickup icon"),
    ]),
    "The 'chairmen' behind": ("Step 4: the businesses", [
        ("One relationship, followed", "A composite: Margaret, 70",
         "Here's the path one person might take through an operation like this. A made-up composite, not a "
         "victim named in the case. Margaret is seventy and widowed. A man who says he's a surgeon with an aid "
         "group abroad comments on a photo she posted. They talk daily for four months. His camera is always "
         "broken, the connection always too weak for video.",
         "an older woman reading messages on a tablet in a sunlit garden, a distant hospital tent icon"),
        ("The first ask, then the second", "Ticket fees, then 'help me'",
         "Month five, his pay is stuck and he needs two thousand dollars for a flight home to meet her. She sends "
         "it. Month six, he asks a different kind of favour: a company will deposit money in her account, and she "
         "should forward it to his business partner. That's the second form of money the prosecutors describe. "
         "Margaret thinks she's helping. She's now moving money taken from other victims.",
         "a bank transfer arrow coming into an account and going straight out again"),
        ("The bank calls", "Her bank freezes the account",
         "Her bank notices money coming in and immediately going out, and freezes the account. A fraud "
         "investigator calls and explains, gently, that the deposit came from another scam victim. Margaret is "
         "devastated, and frightened that she's in trouble. The investigator's advice: stop sending anything, stop "
         "talking to him, report it to the FBI at I C 3 dot gov, and bring in her family.",
         "an older woman on the phone at a kitchen table, a bank statement with a lock icon"),
        ("The exits", "Never met + money = stop",
         "The exits were there from month one: a profile that never video calls, a move off the platform, and "
         "then any request for money from someone she'd never met in person. And one exit people rarely hear: "
         "never receive and pass on money for anyone. When a family member asks gently, early, about a new online "
         "friend, these stories end in month two, not month six.",
         "a timeline of six months with exit signs at months one, two and five"),
    ]),
}

MORE = {
    "The $26 million pop-up": [
        ("Why Ray didn't feel scammed", "Each step felt reasonable",
         "Notice that at no point did Ray feel he was being scammed. Running a scan felt careful. Thirty-nine "
         "dollars felt modest. Calling to activate software felt normal. Letting a technician look felt helpful. "
         "The bad decision was spread across four small, sensible-looking ones. That's why the best defence is a "
         "rule made in advance: no pop-up gets my money or my screen.",
         "four small stepping stones leading to a large hole, an older man stepping carefully"),
    ],
    "How the scam actually worked: the fake invoices": [
        ("The rule for your own money", "Big payment? Confirm by voice",
         "So here's the household version of the companies' fix. Before any big payment, a house deposit, a "
         "contractor's final bill, a tuition payment, confirm the account details by voice, on a number you got "
         "before the email arrived. Write that number on the folder now, at the start, so you're not hunting for "
         "it on the day the pressure is on.",
         "a closing folder with a phone number written on the cover, a pen beside it"),
    ],
    "'Google will remove your business'": [
        ("The office version, in one week", "Fake invoice, fake renewal",
         "The same week, Dee gets two more of the patterns from the FTC's small business guide. An invoice for a "
         "'business directory' ad she never ordered, due in fifteen days. And a 'domain renewal' notice from a "
         "company that isn't her website host, at three times the price. Same shape: a name she half-recognises, "
         "a deadline, a fee. Her new rule handles both. She only pays invoices that match something she ordered, "
         "and checks renewals in her own host account.",
         "a desk with two official-looking invoices stamped not ordered, a laptop with a hosting dashboard"),
        ("If you already paid", "Paid? Dispute and report",
         "If you already paid one of these, call your card company and dispute it, explaining the service was "
         "misrepresented. Report it at the FTC's site, which helps build cases like this one. And tell other "
         "business owners on your street or in your trade group, because these calls work through local lists.",
         "a phone call to a card company, a small group of shop owners chatting on a sidewalk"),
    ],
    "How the scam actually worked: inside the IRS impersonation": [
        ("Telling someone new", "Warn one person this week",
         "If you know someone who has recently moved to the US, a coworker, a neighbour, a friend's parent, this "
         "is the conversation to have. Tell them three things: the IRS writes first, it never wants gift cards, "
         "and immigration officials don't call to collect money. A thirty-second warning from someone they trust "
         "is worth more than any website, because the scam works on fear and isolation.",
         "two neighbours talking over a fence, one showing the other a short note on a phone"),
    ],
    "Inside a pig butchering compound": [
        ("What Ken's family did", "No blame. Report. Block recovery.",
         "When Ken tells his sister, she does the most useful thing first: she doesn't blame him. Then she helps "
         "him report it, call the lender about the loan, and block every 'recovery agent' who messages him over "
         "the next month, offering to get the money back for a fee. They're the same industry, working the same "
         "list of victims, and they're the reason the second loss often follows the first. Real law enforcement "
         "doesn't charge a fee to look into your case, and a stranger who knows exactly what you lost is a reason "
         "for more caution, not less.",
         "a brother and sister at a kitchen table with a laptop, a blocked message notification"),
    ],
    "How the scam actually worked: the money transfer company": [
        ("If you're the family", "Ask about any transfer, kindly",
         "If you look after an older parent's money, here's a simple habit. Ask kindly about any money transfer, "
         "gift card purchase or crypto ATM visit, not to police them, but because those three are how most of "
         "these scams get paid. A parent who knows you'll ask is a parent who might stop at the counter and call "
         "you first.",
         "an adult child and an older parent talking over tea, a receipt on the table"),
    ],
    "The 'chairmen' behind": [
        ("If you're Margaret", "Moved money? Talk to the bank",
         "If you've received and passed on money for an online partner, it's important to know you can stop now, "
         "and the bank and law enforcement are the people to tell. Many people in Margaret's position are victims "
         "who were deceived, and saying so early, with your messages saved, is far better than waiting. Don't "
         "move another dollar for anyone you haven't met. And if you're the family member hearing this for the "
         "first time, the first words matter most: thank you for telling me, we'll sort it out together. That "
         "sentence keeps the next conversation open.",
         "a woman at a bank desk with a folder of printed messages, a calm banker listening"),
    ],
}
for _k, _beats in MORE.items():
    EXAMPLES[_k][1].extend(_beats)
