"""10 TikTok-only minute cuts (65-90s) of the strongest Shorts, rebuilt around the new formats.

    python3 minute_cuts.py   ->  ../tiktok-minute-cuts.json

Each cut keeps the Short's lesson but changes the structure: a phone-screen walkthrough, a
"pause and count" quiz beat, and a real FTC number where one fits. `original_element` says what
makes the video more than a narrated slideshow, which is what TikTok's Creator Rewards and
YouTube's inauthentic-content rule both look for.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "generators" / "weeks-22-26"))
from common import CTA_TIKTOK, P_FAMILY, P_ID, P_INVEST, P_SECURITY, P_TEXT, seg  # noqa: E402

SPOT = ("https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2026/04/"
        "reported-losses-scams-social-media-eight-times-higher-2020")
IMPOSTER = ("https://www.ftc.gov/news-events/news/press-releases/2026/06/"
            "ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025")
FRAUD24 = ("https://www.ftc.gov/news-events/news/press-releases/2025/03/"
           "new-ftc-data-show-big-jump-reported-losses-fraud-125-billion-2024")
REPORT = "https://reportfraud.ftc.gov/"
VOICE = ("Dhruv records the narration in his own voice (or uses the recorded walkthrough audio). "
         "No AI voice on TikTok cuts.")

PHONE = "a phone screen mockup from originality/out/walkthroughs"
QUIZ = "a full-screen countdown card reading PAUSE with a 3-second timer"


def S(h, n, o, vis):
    return seg(h, n, o, vis)


CUTS = [
  dict(based_on="content.json #2", pillar=P_TEXT,
       title="Pause on this toll text: count the 4 red flags",
       hook="4 red flags in one toll text. Pause and count them before I point them out.",
       segments=[
         S("Hook", "Four red flags in one toll text. Pause right now and count them before I point them out.",
           "4 red flags. Count them.", QUIZ),
         S("The text", "Here's the text. Toll services notice. You owe four dollars and fifteen cents. Pay by "
           "midnight or face a fifty dollar late fee and a license suspension. Then a link.",
           "Pause: how many?", PHONE + " (w1-toll), messages appearing"),
         S("Flags 1 and 2", "Red flag one: it came from a random personal number, not a toll agency. Red flag "
           "two: the tiny amount. Nobody argues about four dollars, so you tap and pay.",
           "1: random number · 2: tiny amount", PHONE + " (w1-toll), flags 1 and 2 highlighted"),
         S("Flags 3 and 4", "Red flag three: the midnight deadline. Rush is the point. Red flag four: the link. "
           "It isn't your real toll account, and the page asks for your card number. That's what they wanted.",
           "3: deadline · 4: fake link", PHONE + " (w1-toll), flags 3 and 4 highlighted"),
         S("The number", "In FTC data for twenty twenty-five, about seven of every hundred scam reports where "
           "someone lost money started with a text.", "7% of money-losing scams: a text",
           "the FTC chart originality/out/charts/c2-how-it-started.png"),
         S("The fix", "So don't tap. Type your toll agency's website yourself, or open its official app. If you "
           "owe anything, it'll be there. Then forward the text to seven seven two six, which spells SPAM, and "
           "delete it.", "Type the site yourself. Forward to 7726.",
           "the mascot pointing at a phone keypad showing 7726"),
         S("Close", "How many did you count before I said them?", "How many did you get?",
           "the mascot holding up four fingers"),
       ],
       original_element="Recorded phone-screen walkthrough w1-toll as B-roll for segments 2-4, FTC chart c2 "
                        "for the data beat. " + VOICE,
       sources=["https://www.ic3.gov/PSA/2024/PSA240412", REPORT, SPOT],
       claims=["Toll agencies bill through your account or by mail, not via random texts with links",
               "7% of 2025 FTC fraud reports with a loss started with a text (FTC Data Spotlight, Apr 2026)",
               "Forwarding spam texts to 7726 reports them to your carrier"],
       hashtags=["tollscam", "textscam", "smishing", "spotthescam", "scamalert", "scamdecoded"],
       thumb="Count the 4 red flags"),

  dict(based_on="content.json #3", pillar=P_FAMILY,
       title="A cloned voice call, played out: 1 word ends it",
       hook="1 word ends a cloned voice call. Here's how the call goes, line by line.",
       segments=[
         S("Hook", "One word ends a cloned voice call. Here's how that call goes, line by line, and where the "
           "word comes in.", "1 word ends this call", "an incoming call screen labelled Grandson"),
         S("The call", "The phone rings. It's your grandson's voice. He's crying. He was in a car accident, he's "
           "been arrested, and he needs bail money now. Then: please don't tell Mom and Dad.",
           "'Please don't tell Mom and Dad'", "a phone held to an ear, sound waves in amber"),
         S("Pause", "Pause. Before you answer him, how many red flags did you just hear? Count them.",
           "Pause: how many red flags?", QUIZ),
         S("The flags", "There are three. Panic, so you don't stop to think. Urgent money. And a secret, so "
           "nobody checks. That combination is the whole scam.", "Panic · money · secret",
           "three amber flags on a line"),
         S("The voice", "And the voice? Scammers can clone a voice from a short clip posted online. The FTC and "
           "the FBI have both warned about it. So 'it sounded just like him' isn't proof anymore.",
           "'Sounded like him' isn't proof", "a waveform being copied from a video thumbnail"),
         S("The number", "Imposter scams like this one cost people three and a half billion dollars in reports to "
           "the FTC in twenty twenty-five.", "$3.5B lost to imposters in 2025",
           "a single bold amber bar labelled 2025"),
         S("The fix", "So tonight, pick a family safe word. Anyone who calls in a panic asking for money has to "
           "say it. No word? Hang up, and call them back on the number you already have. It takes two minutes "
           "at dinner.", "Pick a safe word tonight", "a family at a dinner table, a speech bubble with a key"),
       ],
       original_element="Dhruv acts out the call as a split-screen (his voice as the 'grandson', on-screen text "
                        "for the listener), then the pause card. " + VOICE,
       sources=["https://consumer.ftc.gov/consumer-alerts/2023/03/scammers-use-ai-enhance-their-family-emergency-schemes",
                "https://www.ic3.gov/PSA/2024/PSA241203", IMPOSTER],
       claims=["Scammers can clone a voice from a short audio clip (FTC alert, Mar 2023; FBI PSA Dec 2024)",
               "People reported losing $3.5 billion to imposter scams in 2025 (FTC, Jun 2026)"],
       hashtags=["grandparentscam", "aivoice", "familysafeword", "scamalert", "protectyourparents", "scamdecoded"],
       thumb="1 word stops this call"),

  dict(based_on="content.json #7", pillar=P_SECURITY,
       title="The fraud alert that ends with a code, played out",
       hook="6 digits is all this caller wants. Watch how the call gets there.",
       segments=[
         S("Hook", "Six digits. That's all this caller wants, and he'll spend three minutes getting there. "
           "Watch how, because the script is the same almost every time.", "He wants 6 digits", PHONE + " (w3-bank-code), blank"),
         S("The text", "First, a text that looks like your bank. Fraud alert: did you try to spend twelve hundred "
           "eighty dollars at an electronics store? Reply yes or no. You reply no.", "'Did you spend $1,280?'",
           PHONE + " (w3-bank-code), first two messages"),
         S("The call", "Seconds later your phone rings. Caller ID shows your bank. A calm voice: we blocked that "
           "charge. I'm sending you a code. Just read it back so I can verify it's you.",
           "'Just read me the code'", PHONE + " (w3-bank-code), the code arriving"),
         S("Pause", "Pause. What's actually happening on his end right now? Take a guess.",
           "Pause: what's he doing?", QUIZ),
         S("Reveal", "He's on your bank's login page with your username, pressing forgot password. The code your "
           "bank just sent is the last lock. Read it out loud, and he's in.", "He's logging in as you",
           "a login page with a cursor on 'Forgot password'"),
         S("The rule", "Nobody real needs that code. Not your bank, not tech support, not a buyer online. A code is "
           "for typing into a screen, never for saying to a person.", "Codes are typed, never said",
           "the mascot zipping its lips beside a 6-digit code"),
         S("The fix", "Already shared one? Change that password now, sign out of all devices, and call the number "
           "on the back of your card. Then turn on sign-in alerts, so the next attempt pings you first.", "Shared one? Change password now.",
           "a checklist with three ticks"),
       ],
       original_element="Recorded walkthrough w3-bank-code for segments 1-3, plus 10-15 seconds of Dhruv's own "
                        "screen showing where 'sign out of all devices' lives in a real account. " + VOICE,
       sources=["https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams",
                "https://www.fcc.gov/spoofing", "https://www.cisa.gov/secure-our-world/turn-mfa"],
       claims=["Caller ID can be spoofed (FCC)",
               "One-time codes are sent when someone tries to sign in or reset a password"],
       hashtags=["2fa", "verificationcode", "bankscam", "accountsecurity", "scamalert", "scamdecoded"],
       thumb="Never read a code out"),

  dict(based_on="content.json #4", pillar=P_TEXT,
       title="'Move it to a safe account': the bank call, step by step",
       hook="0 real banks make this call. Here it is, step by step.",
       segments=[
         S("Hook", "Zero real banks make this call. But it sounds exactly like one, so here it is, step by step.",
           "0 real banks make this call", "an incoming call screen labelled Bank Fraud Dept"),
         S("Step 1", "Step one, trust. Caller ID says your bank. They know your name and the last four digits of "
           "your card. Scammers can get both from old data breaches.", "1: they know your details",
           "a caller ID screen with a bank icon"),
         S("Step 2", "Step two, fear. There's fraud on your account. Someone at your branch may be involved, so "
           "don't go in, and don't tell anyone.", "2: 'Don't tell anyone'", "a padlock cracking open"),
         S("Step 3", "Step three, the ask. Move your savings to a new secure account while we fix this. They stay "
           "on the phone and walk you through every transfer.", "3: 'Move your savings'",
           "coins sliding from one box to another"),
         S("Pause", "Pause. Which step gives it away? It's step three. Your bank can freeze your account itself. "
           "It never needs you to move the money.", "Pause: which step?", QUIZ),
         S("The number", "In twenty twenty-five, people told the FTC they lost nearly a billion dollars to "
           "scammers posing as businesses, and about nine hundred twenty million to fake government agents.",
           "Fake businesses: nearly $1B", "two amber bars, labelled Business and Government"),
         S("The fix", "And caller ID can be faked, so the name on your screen proves nothing. Hang up. Call the "
           "number on the back of your card. If there's real fraud, they'll see it.",
           "Hang up. Call the number on your card.", "a hand flipping a bank card to the back"),
       ],
       original_element="Dhruv films the back of his own bank card (number covered) and dials the printed "
                        "number for the fix beat; steps 1-3 as on-screen text over his face cam. " + VOICE,
       sources=["https://www.fcc.gov/spoofing", "https://www.consumerfinance.gov/consumer-tools/fraud/", IMPOSTER],
       claims=["Caller ID can be spoofed (FCC)",
               "2025 losses: business impersonators nearly $1B, government impersonators about $920M (FTC, Jun 2026)"],
       hashtags=["bankscam", "safeaccountscam", "fraudalert", "scamalert", "moneysafety", "scamdecoded"],
       thumb="Your bank never asks this"),

  dict(based_on="content.json #11", pillar=P_SECURITY,
       title="Fake virus pop-up: 3 tricks and the 1 key combo that ends it",
       hook="1 pop-up, 3 tricks, 0 real tech companies behind it.",
       segments=[
         S("Hook", "One pop-up, three tricks, and zero real tech companies behind it. Here's each trick, so you "
           "know it when you see it.", "1 pop-up · 3 tricks", "a laptop with a red full-screen warning"),
         S("Trick 1", "Trick one: noise. An alarm sound, or a voice saying your computer is infected. It's meant "
           "to make you panic before you think.", "1: an alarm", "a speaker icon with amber sound waves"),
         S("Trick 2", "Trick two: it won't go away. It fills the screen, and the close button seems dead. It's just "
           "a web page in full-screen mode.", "2: it won't close", "a browser window stretched edge to edge"),
         S("Trick 3", "Trick three: a phone number. Call now, don't turn off your computer. Real tech companies "
           "don't put phone numbers in error messages.", "3: a number to call",
           "a warning box with a phone number masked by dots"),
         S("Pause", "Pause. What happens if you call? Someone friendly asks to connect to your computer to fix it. Then come fake "
           "scans, a bill for hundreds of dollars, and sometimes a fake refund that ends with them in your bank "
           "account.", "Pause: what happens if you call?", QUIZ + ", then a cursor moving on its own"),
         S("The fix", "So don't call. Close the browser. If it won't close, press control, alt, delete on Windows, "
           "or command, option, escape on a Mac, and force quit it. Or just restart.",
           "Ctrl+Alt+Del · Cmd+Option+Esc", "two keyboards with the key combos lit in teal"),
         S("Never", "And never let anyone who contacted you install remote access on your computer. Already did? Disconnect from the internet and call your bank.",
           "Never allow remote access", "the mascot blocking a cable plug"),
       ],
       original_element="Dhruv screen-records force-quitting a harmless full-screen page on his own Windows or Mac "
                        "(Task Manager or Force Quit window), 10-15 seconds, for the fix beat. " + VOICE,
       sources=["https://consumer.ftc.gov/articles/how-spot-avoid-and-report-tech-support-scams", REPORT],
       claims=["Legitimate tech companies don't put phone numbers in pop-up error messages (FTC)",
               "Tech support scammers ask for remote access and payment"],
       hashtags=["techsupportscam", "popupscam", "computertips", "scamalert", "seniorsafety", "scamdecoded"],
       thumb="Don't call. Force quit."),

  dict(based_on="content.json #1", pillar=P_ID,
       title="Freezing your credit, start to finish, in 3 stops",
       hook="3 websites, $0, about 10 minutes. Here's a credit freeze start to finish.",
       segments=[
         S("Hook", "Three websites, zero dollars, about ten minutes. Here's the whole credit freeze, start to "
           "finish.", "3 sites · $0 · 10 minutes", "a stopwatch next to three padlocks"),
         S("What it does", "A credit freeze stops lenders from pulling your credit report. No report, no new card "
           "or loan in your name. It's free by federal law.", "Free by federal law",
           "a credit report behind a padlock"),
         S("The 3 stops", "Stop one, Equifax. Stop two, Experian. Stop three, TransUnion. You need all three, "
           "because a lender might check any one of them.", "Equifax · Experian · TransUnion",
           "three doors with padlocks, numbered 1 2 3"),
         S("How", "On each site, you make an account, confirm who you are, and hit freeze. Some ask questions from "
           "your credit history, like an old address or a past loan. Save each login somewhere safe. You'll need it later.",
           "Make an account. Hit freeze.", "a screen recording placeholder of a bureau freeze page"),
         S("Quiz", "Quick quiz. True or false: a freeze hurts your credit score. False. True or false: your "
           "current cards stop working. Also false. They keep working exactly as before.", "True or false?", QUIZ),
         S("Lifting it", "Applying for a loan or an apartment? Lift the freeze online for a day or a week, and it "
           "locks again when the time's up.", "Lift it for a day, then it relocks",
           "a padlock opening and closing on a calendar"),
         S("The number", "People reported losing twelve and a half billion dollars to fraud in twenty twenty-four. "
           "A freeze is a free lock on one of the biggest doors.", "$12.5B reported lost in 2024",
           "a bold amber number on navy"),
       ],
       original_element="Dhruv screen-records the freeze flow on one bureau's real page (his details blurred), "
                        "15-20 seconds, for the 'How' beat. " + VOICE,
       sources=["https://consumer.ftc.gov/articles/what-know-about-credit-freezes-and-fraud-alerts",
                "https://www.equifax.com/personal/credit-report-services/credit-freeze/",
                "https://www.experian.com/freeze/center.html", "https://www.transunion.com/credit-freeze", FRAUD24],
       claims=["Credit freezes are free at all three bureaus by federal law",
               "A freeze does not affect your credit score or existing accounts",
               "Consumers reported losing $12.5 billion to fraud in 2024 (FTC, Mar 2025)"],
       hashtags=["creditfreeze", "identitytheft", "credittips", "fraudprevention", "scamalert", "scamdecoded"],
       thumb="Freeze it in 10 minutes"),

  dict(based_on="content.json #10", pillar=P_INVEST,
       title="The task job text, followed all the way to the top-up",
       hook="$0 is what a real job asks you to pay. Follow this job text to the end.",
       segments=[
         S("Hook", "Zero dollars. That's what a real job asks you to pay. Follow this job text all the way to the "
           "end, and watch that number change.", "Watch the number change", PHONE + " (w5-job), blank"),
         S("The text", "It starts out of nowhere. Hi, this is Jenna from a placement agency. Remote work, an hour "
           "or so a day, three hundred to nine hundred dollars daily. Interested?", "'$300-$900 a day'",
           PHONE + " (w5-job), first message"),
         S("The hook", "You say yes. Add our trainer on WhatsApp. You get an app, simple tasks rating products, and "
           "the first payouts are real. Twenty, forty dollars. It feels legit.", "The first payouts are real",
           PHONE + " (w5-job), messages two and three"),
         S("The turn", "Then your account goes negative. To unlock your earnings, you top it up, usually in "
           "crypto. Then again. And again. That money doesn't come back, and neither do the earnings on the screen.", "Then: pay to unlock",
           PHONE + " (w5-job), the top-up message highlighted"),
         S("Pause", "Pause. When was the moment to walk away? The very first text. A recruiter you never "
           "contacted, offering big pay for little work, is the red flag.", "Pause: when to walk away?", QUIZ),
         S("The number", "People reported losing about half a billion dollars to job scams in twenty twenty-four, "
           "according to the FTC.", "Job scams: ~$500M lost in 2024", "a bold amber number on navy"),
         S("The rule", "Here's the rule. If a job asks you to pay, deposit, or buy anything to get paid, it isn't a "
           "job.", "Pay to get paid = not a job", "the mascot holding a stop sign"),
       ],
       original_element="Recorded walkthrough w5-job for segments 1-4, with the flags revealing in time with the "
                        "narration. " + VOICE,
       sources=["https://consumer.ftc.gov/consumer-alerts/2023/09/paying-earn-money-gamified-online-job-task-scams",
                "https://consumer.ftc.gov/articles/job-scams", FRAUD24],
       claims=["Task scams pay small early amounts, then require deposits, often in crypto (FTC alert, Sep 2023)",
               "Reported job scam losses were $501 million in 2024 (FTC, Mar 2025)"],
       hashtags=["jobscam", "taskscam", "remotejobs", "workfromhome", "scamalert", "scamdecoded"],
       thumb="Real jobs don't charge you"),

  dict(based_on="weeks-13-21.json #10", pillar=P_FAMILY,
       title="'New number, can you pay a bill?': the whole text thread",
       hook="2 texts in, the money ask arrives. Here's the whole 'Hi Mom' thread.",
       segments=[
         S("Hook", "Two texts in, the money ask arrives. Here's the whole 'Hi Mom' thread, and the one question "
           "that ends it.", "The 'Hi Mom' thread, start to end", PHONE + " (w4-new-number), blank"),
         S("Text 1", "Hi Mom, it's me. Dropped my phone in the sink, this is my new number, save this one. You "
           "ask: which one of you is this? Haha, your favourite, obviously.", "'Which one of you is this?'",
           PHONE + " (w4-new-number), first three messages"),
         S("Text 2", "Then: I have a bill due today, and my banking app won't work on the new phone. Could you pay "
           "it for me? Then a stranger's name, and nineteen hundred forty dollars.", "A stranger's name. $1,940.",
           PHONE + " (w4-new-number), the payment details"),
         S("Pause", "Pause and count the red flags. There are four. A new number. Dodging a simple question. "
           "Rush. And a stranger's name on the payment.", "Pause: count the red flags", QUIZ),
         S("The fix", "So call the old number. It probably still works. Or ask something only your child would "
           "know, something that isn't on social media, like a family joke or the name of a first teacher.", "Call the old number",
           "a phone dialling a contact labelled Kid (old)"),
         S("Safe word", "Even better, agree on a family safe word tonight. It takes two minutes, and it works for "
           "phone calls too.", "Family safe word: 2 minutes", "a family group chat with a key emoji"),
         S("Already paid", "Already paid? Call your bank or payment app right away, and report it at report fraud "
           "dot f t c dot gov.", "Paid? Call your bank now.", "a phone dialling a bank"),
       ],
       original_element="Recorded walkthrough w4-new-number for segments 1-4. Optional: Dhruv's real mum reacts "
                        "to the thread on camera (with her permission). " + VOICE,
       sources=["https://consumer.ftc.gov/articles/scammers-use-fake-emergencies-steal-your-money",
                "https://consumer.ftc.gov/articles/how-recognize-and-report-spam-text-messages", REPORT],
       claims=["Family-emergency scams often start with a 'new number' text (FTC)"],
       hashtags=["himomscam", "familyscam", "scamtext", "imposterscam", "scamalert", "scamdecoded"],
       thumb="4 red flags in 4 texts"),

  dict(based_on="weeks-3-6.json #3", pillar=P_TEXT,
       title="Quiz: 4 red flags in a $499 order email",
       hook="$499 for something you didn't buy. Find the 4 red flags before I do.",
       segments=[
         S("Hook", "Four ninety-nine for something you didn't buy. Find the four red flags in this email before I "
           "do. Here's the email, word for word.", "Find 4 red flags", "the quiz slide originality/out/quizzes/q3-invoice/slide-01.png"),
         S("The email", "Thank you for your order of PC Security Plus, three years. Amount charged, "
           "four ninety-nine ninety-nine. Didn't authorize it? Call our cancellation desk within twenty-four "
           "hours. Pause here and count.", "Pause and count", "the quiz slide q3-invoice/slide-01.png, zooming in"),
         S("Flags 1 and 2", "Red flag one: the sender. A random address, not the company. Red flag two: a big "
           "charge you didn't make. It's there to panic you.", "1: sender · 2: big charge",
           "quiz slides q3-invoice/slide-03 and slide-04"),
         S("Flags 3 and 4", "Red flag three: the twenty-four hour deadline. Red flag four: the phone number. It "
           "goes to a scammer who wants into your computer or your card, to 'refund' you.",
           "3: deadline · 4: the number", "quiz slides q3-invoice/slide-05 and slide-06"),
         S("The number", "Email started about one in ten of the money-losing scams reported to the FTC in twenty "
           "twenty-five.", "Email: 10% of money-losing scams",
           "the FTC chart originality/out/charts/c2-how-it-started.png"),
         S("The fix", "So don't call the number in the email. Log into the real account, or check your card "
           "statement. No charge there means no charge. Mark the email as spam and delete it.",
           "Check your real statement", "the quiz slide q3-invoice/slide-07.png"),
         S("Close", "How many did you get before I said them? Four out of four means you're ready for the next one.", "How many did you get?",
           "the mascot holding a score card"),
       ],
       original_element="Built on the quiz carousel q3-invoice (its slides are the visuals), with a real 3-second "
                        "pause card and FTC chart c2. " + VOICE,
       sources=["https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams",
                "https://consumer.ftc.gov/articles/how-spot-avoid-and-report-tech-support-scams", SPOT],
       claims=["10% of 2025 FTC fraud reports with a loss started with an email (FTC Data Spotlight, Apr 2026)",
               "Fake invoice emails push people to call a number that leads to remote-access scams (FTC)"],
       hashtags=["phishing", "emailscam", "refundscam", "spotthescam", "scamalert", "scamdecoded"],
       thumb="Find the 4 red flags"),

  dict(based_on="weeks-7-12.json #15", pillar=P_INVEST,
       title="Dating app to WhatsApp in 1 day: the pattern, hour by hour",
       hook="1 day from match to 'let's move to WhatsApp.' Here's the pattern, hour by hour.",
       segments=[
         S("Hook", "One day from match to 'let's move to WhatsApp.' It happens fast, and it's on purpose. Here's the pattern, hour by hour.",
           "Match to WhatsApp in 1 day", "a clock face with a heart and a chat bubble"),
         S("Morning", "Morning: you match. They're warm, funny, and asking all the right questions. Afternoon: I "
           "barely use this app. Let's text on WhatsApp instead.", "'I barely use this app'",
           "a dating app chat sliding to a private chat"),
         S("Why it matters", "Here's why that matters. Dating apps can spot scam accounts and ban them, even "
           "mid-conversation. Private chat apps can't. Off the app, nobody's watching.",
           "Off the app, nobody's watching", "a lifeguard tower left behind on a beach"),
         S("The weeks after", "Then the love-bombing speeds up. Good morning texts, big feelings, fast. And later "
           "comes the money: an emergency, a plane ticket, or an investment tip they swear by.",
           "Then: love-bombing, then money", "a heart turning into a coin"),
         S("The number", "In FTC data for twenty twenty-five, people aged eighteen to twenty-nine were the most "
           "likely to have a money-losing scam start on social media. Forty percent did.",
           "18-29: 40% started on social", "the FTC chart originality/out/charts/c4-age-social.png"),
         S("Pause", "Pause. Is moving apps proof of a scam? No. Plenty of real people prefer texting. It's a "
           "reason to slow down.", "Pause: proof of a scam?", QUIZ),
         S("The fix", "Keep chatting in the app until you've met on video or in person. If they keep pushing, "
           "report the profile, and never send money to someone you haven't met.", "Stay in the app until you've met", "the mascot holding a report flag"),
       ],
       original_element="FTC chart c4 as the data beat, plus Dhruv's face cam reading the morning/afternoon "
                        "messages. " + VOICE,
       sources=["https://consumer.ftc.gov/articles/what-know-about-romance-scams",
                "https://consumer.ftc.gov/consumer-alerts/2023/02/love-lies-and-losses", SPOT],
       claims=["Romance scammers often ask to move off dating apps (FTC)",
               "40% of 2025 money-losing reports from 18-29 year olds started on social media (FTC Data Spotlight, Apr 2026)"],
       hashtags=["onlinedating", "romancescam", "datingapp", "redflags", "scamalert", "scamdecoded"],
       thumb="The 1-day red flag"),
]


def item(c: dict) -> dict:
    words = sum(len(s["narration"].split()) for s in c["segments"])
    return {
        "format": "short", "pillar": c["pillar"], "platforms": ["tiktok"],
        "idea_angle": f"65-90s TikTok-only minute cut of {c['based_on']}, rebuilt with a walkthrough or quiz "
                      f"beat and real FTC data ({words} words, about {round(words / 2.5)}s at 150 wpm).",
        "based_on": c["based_on"], "original_element": c["original_element"],
        "script": {
            "title": c["title"], "hook": c["hook"], "segments": c["segments"], "cta": CTA_TIKTOK,
            "caption": f"{c['title']}. Examples are fictional; numbers are from the FTC.\n\n{CTA_TIKTOK}",
            "hashtags": c["hashtags"], "description": c["title"], "thumbnail_text": c["thumb"],
            "sources": c["sources"], "claims_to_verify": c["claims"],
        },
    }


def main() -> None:
    items = [item(c) for c in CUTS]
    (HERE.parent / "tiktok-minute-cuts.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    for i in items:
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        print(f"{w:4d}w {round(w/2.5):3d}s  {i['script']['title']}")


if __name__ == "__main__":
    main()
