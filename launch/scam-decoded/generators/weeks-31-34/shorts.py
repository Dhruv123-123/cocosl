"""12 Shorts for weeks 31-34 (Jun 6 - Jul 3 2027), each with its TikTok minute cut.

Each Short: 4 beats, 60-120 words. Each TikTok cut: a new hook, the Short's middle beats, a pause beat,
extra beats and the fix: 165-230 words. `look` is the visual format (see ORIGINALITY_PASS.md);
consecutive videos never share one.
"""
from sources import *
from common import MASCOT, P_FAMILY, P_TEXT, P_SECURITY

P_TEENS = "teens, games and payment apps"
P_JOBS = "job, school and rental scams"
P_HOME = "home, car and small business scams"
PAUSE_VIS = "a full-screen countdown card"


def S(**k):
    return k


SHORTS = [
# ===================================================================== week 31: summer, teens
S(week=31, pillar=P_TEENS, look="illustrated", tt_look="face cam",
 title="'Send $50, get $500': 1 money flip that only goes one way",
 hook="1 post promises to turn $50 into $500 on a payment app. Here's where the $50 goes.",
 thumb="Money flips aren't real",
 hashtags=["cashapp", "moneyflip", "teens", "paymentapps", "scamdecoded"],
 description="How the 'money flipping' scam on payment apps works, and why there's no such thing.",
 caption="'Send me $50 and I'll flip it to $500.' It's all over social media in summer, aimed at teens with job money. "
         "There's no flip. The $50 is gone, and then they ask for a 'fee'.",
 sources=[CASH_FLIP, FTC_FREE_MONEY, FTC_PAY_APPS],
 claims=["Cash App warns that 'cash flipping' offers are scams (Cash App)",
         "Scammers promise free money on social media to get people to send payments (FTC)"],
 short=[
  ("Hook", "One post. Send fifty dollars, get five hundred back. Screenshots of happy customers, a timer, spots running out.",
   "'$50 becomes $500'", f"{MASCOT} looking at a phone full of money emojis"),
  ("The catch", "There's no flip. Once you send it, the fifty is gone. Then comes a message: your five hundred is ready, "
                "just pay a release fee first.", "Then a 'release fee'", "a padlock on a pile of cash"),
  ("The tell", "Nobody can multiply money you send them. Payment apps don't run giveaways where you pay first. The "
               "screenshots are fake.", "Nobody multiplies your money", "a calculator with a red X"),
  ("Do this", "Scroll past. Payment apps are for people you know. If a friend's account posts a flip, their account "
              "was hacked. Tell them another way.", "Pay only people you know", f"{MASCOT} with a stop hand"),
 ],
 tt_title="My brother almost sent $50 to a 'money flipper'",
 tt_hook="1 talk with your teen before their first summer paycheck hits a payment app.",
 tt_extra=[
  ("Pause", "Pause. If you sent the fifty and they asked for a twenty-dollar release fee, would you pay it to get the "
            "five hundred? Think about it.", "Pause: pay the fee?", PAUSE_VIS),
  ("The fee ladder", "That's how it keeps going. A release fee, then a verification fee, then a tax. Every payment is real "
                     "money and the five hundred never existed.", "Fee, fee, fee. No $500.", "a ladder made of bills"),
  ("Already sent?", "Already sent money? Report the account in the app, and contact the app's support from inside the app, "
                    "not from a comment. Payments to strangers are hard to get back, so tell your teen it's not their "
                    "fault, and that telling you was the right move.", "Sent it? Report in the app.",
   "a parent and teen looking at a phone"),
 ]),
S(week=31, pillar=P_TEENS, look="walkthrough", tt_look="quiz pause",
 title="'Free game coins, just log in': 1 site that takes accounts",
 hook="1 'free coins' site asks your kid to log in. That's how the whole game account gets taken.",
 thumb="Free coins? No such thing.",
 hashtags=["gaming", "roblox", "parents", "accountsecurity", "scamdecoded"],
 description="Why 'free game currency' generators steal accounts, and two settings that protect a kid's game account.",
 caption="'Free Robux' and other 'free coins' generators don't exist. Roblox says so itself. What they want is your "
         "kid's username and password, and sometimes a parent's card.",
 sources=[ROBLOX_GEN, ROBLOX_SCAMS, FTC_GAMES],
 claims=["Roblox says free Robux generators are scams and can steal account information (Roblox)",
         "Turn on 2-step verification for game accounts (Roblox)"],
 short=[
  ("Hook", "One video in your kid's feed: free coins, unlimited, just enter your username and password.",
   "'Free coins, just log in'", "walkthrough: a game-style site with a coin pile"),
  ("The catch", "There's no generator. The site saves the login, and the scammer takes the account, the items and "
                "anything bought with real money.", "It saves the login", "walkthrough: login box glowing red"),
  ("The tell", "Game companies sell their currency through the game and gift cards. Any site that gives it away free "
               "and asks for a password is a scam.", "Real coins come from the game", "a game controller with a coin"),
  ("Do this", "Tell your kid the rule: never type the password anywhere but the game. Then turn on two-step "
              "verification and a parent PIN together.", "Password goes in the game only", f"{MASCOT} with a game controller"),
 ],
 tt_title="Quiz: which of 3 'free coins' offers is safe?",
 tt_hook="3 'free coins' offers, and only 1 answer is right. Play along with your kid.",
 tt_extra=[
  ("Pause", "Pause. Offer A: a site that asks for your password. Offer B: a player who'll trade if you go first. Offer C: "
            "a gift card from a store, redeemed in the game. Which one is safe?", "Pause: A, B or C?", PAUSE_VIS),
  ("Answer", "C. A store gift card, redeemed inside the game, is the real way. A steals your account. B keeps your items "
             "and disappears, because trades where you go first are the oldest trick in the game.",
   "C. Only C.", "card C with a green check"),
  ("Already logged in?", "Already typed the password into one? Change it right away inside the game, log out other "
                         "sessions, and turn on two-step verification. If the account is gone, use the game's own "
                         "support page to recover it, never a 'recovery' person in the comments.",
   "Typed it? Change it now.", "a key and a refresh arrow"),
 ]),
S(week=31, pillar=P_JOBS, look="screen recording", tt_look="illustrated",
 title="'Babysitting, $600 a week, check first': 1 offer to refuse",
 hook="1 babysitting job pays $600 a week and sends a check before you've met. That check is the scam.",
 thumb="The check-first nanny job",
 hashtags=["babysitting", "summerjob", "nanny", "fakecheck", "scamdecoded"],
 description="How the fake check nanny and babysitting job scam works.",
 caption="A family you've never met hires you by text, mails a big check, and asks you to send some of it to a "
         "'supplier' for furniture or gear. The check bounces later. The money you sent is real.",
 sources=[FTC_NANNY, FTC_CHILDCARE_CHECK, FTC_CHECKS],
 claims=["Scammers posing as families send fake checks to nannies and caregivers and ask them to send money back (FTC)",
         "A deposited check can bounce days or weeks later, and you owe the bank the money (FTC)"],
 original_element="Dhruv screen-records a fictional job post and message thread on his own phone, then the bank "
                  "app screen that says 'funds available' (which isn't the same as the check clearing).",
 short=[
  ("Hook", "One summer job by text. Babysitting, six hundred a week, and the family will mail a check before you meet.",
   "'I'll mail you a check first'", "Dhruv's screen: a message thread"),
  ("The ask", "The check is for more than your pay. Keep your wages, they say, and send the rest to our supplier for "
              "a car seat and a stroller.", "'Send the rest to our supplier'", "Dhruv's screen: a check photo"),
  ("The trap", "The check looks real and the bank shows the money. Days later, it bounces, and you owe the bank every "
               "dollar you sent.", "It bounces. You owe it.", "Dhruv's screen: bank app balance"),
  ("The rule", "Meet the family first, on video and in person. Never send money back from a check. A real job doesn't "
               "pay you in advance.", "No job pays you to pay someone", f"{MASCOT} holding a stop sign"),
 ],
 tt_title="The nanny job that pays before you start, played out",
 tt_hook="3 messages turn a summer babysitting job into a bounced check.",
 tt_extra=[
  ("Pause", "Pause. The bank app says the money is available. Is it safe to send the rest to the supplier now? Think "
            "about it.", "Pause: is it safe now?", PAUSE_VIS),
  ("Available isn't cleared", "No. Banks often make deposited money available within a day or two, before they know "
                              "if the check is good. Finding a fake can take weeks. Available isn't the same as cleared.",
   "Available isn't cleared", "a bank building with a clock"),
  ("Already sent?", "Already sent money from the check? Call your bank right away, tell them the check may be fake, and "
                    "report the 'family' to the job site and at report fraud dot f t c dot gov.",
   "Sent it? Call your bank.", "a phone and a bank"),
 ]),
# ===================================================================== week 32: before Father's Day
S(week=32, pillar=P_HOME, look="walkthrough", tt_look="face cam",
 title="'Your car warranty is about to expire': 1 call to hang up on",
 hook="1 'final notice' about your car warranty. It isn't from your carmaker, and it isn't final.",
 thumb="'Final notice'? Hang up.",
 hashtags=["carwarranty", "robocall", "fathersday", "cars", "scamdecoded"],
 description="How 'final notice' car warranty calls and mailers work, and how to check your real warranty.",
 caption="'This is your final notice about your vehicle's warranty.' By phone or a postcard that looks official. "
         "It's usually a seller of service contracts, and sometimes a scam. Your dealer can tell you what you have.",
 sources=[FTC_WARRANTY, FTC_WARRANTY_CALLS, FTC_SERVICE],
 claims=["Auto warranty robocalls and mailers often aren't from the manufacturer or dealer (FTC)",
         "What's sold as an 'extended warranty' is often a service contract (FTC)"],
 short=[
  ("Hook", "One call. This is your final notice. Your vehicle's warranty is about to expire. Press one to speak to a "
           "specialist.", "'Your final notice'", "walkthrough: incoming call, 'Vehicle Services'"),
  ("Who it is", "It's not your carmaker or your dealer. It's someone selling a service contract, and some of them take "
                "a down payment and disappear.", "Not your carmaker", "walkthrough: a postcard stamped FINAL"),
  ("The tell", "They don't say which car, they want payment today, and pressing one gets you more calls.",
   "Which car? Pay today?", "a phone ringing off the hook"),
  ("Do this", "Hang up. Your dealer or the manual tells you what warranty you already have. Want more coverage? "
              "Compare it yourself, in writing.", "Ask your dealer, not the caller", f"{MASCOT} holding car keys"),
 ],
 tt_title="Dad's 'final notice' warranty calls: 3 questions end them",
 tt_hook="3 questions end the 'final notice' car warranty call. Dad can try them this week.",
 tt_extra=[
  ("Pause", "Pause. Before the questions, what would you ask a caller who says your warranty is expiring? Think about it.",
   "Pause: what would you ask?", PAUSE_VIS),
  ("The questions", "One: which car, and what's the VIN? Two: what company are you, and where are you? Three: can you "
                    "mail me the full contract before I pay anything? Scammers hang up. A real company sends it.",
   "Which car? Who are you? Mail it.", "three numbered cards"),
  ("Before you buy", "If you do want a service contract, read what's not covered, who does the repairs, and whether you can "
                     "cancel. Many people never use the one they bought.", "Read what's not covered",
   "a contract with a magnifying glass"),
 ]),
S(week=32, pillar=P_HOME, look="illustrated", tt_look="quiz pause",
 title="'Removed from Google today': 1 robocall business owners get",
 hook="1 robocall tells small business owners they'll vanish from Google today. Google didn't call.",
 thumb="Google didn't call",
 hashtags=["smallbusiness", "google", "robocall", "fathersday", "scamdecoded"],
 description="The fake 'Google listing' robocall aimed at small business owners, and how real listings work.",
 caption="Dad runs a shop or a one-truck business? He's probably had this call. The FTC has taken action against "
         "robocallers using it. A Google Business Profile is free.",
 sources=[FTC_GOOGLE_RC, FTC_SMB, FTC_DIRECTORY],
 claims=["The FTC took action against robocallers who falsely threatened small businesses with removal from Google (FTC)",
         "Scammers target small businesses with fake directory listing charges (FTC)"],
 short=[
  ("Hook", "One robocall. Your business listing will be removed from Google today unless you verify now. Press one.",
   "'Removed from Google today'", f"{MASCOT} next to a shop sign"),
  ("The pitch", "A person comes on and offers to fix it, or get you on the first page, for a fee. Some are sales pitches, "
                "some are scams.", "'Pay us to fix it'", "a search page with a price tag"),
  ("The tell", "A basic Google Business Profile is free, and you manage it yourself. A threat with a deadline is the "
               "sales tactic.", "A Google listing is free", "a storefront with a free tag"),
  ("Do this", "Hang up. Sign in to your own business profile and check it yourself. Pass this to anyone who runs a "
              "small business.", "Check your own profile", f"{MASCOT} hanging up a phone"),
 ],
 tt_title="3 calls to your business: only 1 is real",
 tt_hook="3 calls a small business gets in 1 week. Pause and pick the real one.",
 tt_extra=[
  ("Pause", "Pause. Call A: your Google listing will be removed today. Call B: your directory renewal is overdue, we'll "
            "invoice you. Call C: a customer asking your opening hours. Which one is real?", "Pause: A, B or C?", PAUSE_VIS),
  ("Answer", "C. A is the robocall. B is the directory scam: an invoice for a listing you never ordered, in a book or "
             "site nobody reads. The FTC warns businesses not to pay invoices they can't match to an order.",
   "C. A and B want money.", "card C with a green check"),
  ("The office rule", "Make it an office rule. Anyone can answer the phone, but only one person approves payments, and "
                      "only for invoices that match an order. Write it on a sticky note by the phone.",
   "1 person approves payments", "a sticky note by a phone"),
 ]),
S(week=32, pillar=P_HOME, look="face cam", tt_look="walkthrough",
 title="Selling Dad's truck? 1 'buyer' who overpays by check",
 hook="1 buyer offers full price for Dad's truck, sight unseen, and sends a check for $2,000 too much.",
 thumb="The overpaying buyer",
 hashtags=["carsales", "marketplace", "fakecheck", "fathersday", "scamdecoded"],
 description="The fake check overpayment scam aimed at people selling cars online.",
 caption="Selling a car online? The buyer who doesn't want to see it, sends a check for more than the price and asks "
         "you to send back the difference is the scam. The FTC warned car sellers about it.",
 sources=[FTC_CAR_SELLERS, FTC_CHECKS, FBI_CAR],
 claims=["Scammers send fake checks to online car sellers and ask for the overpayment back (FTC)",
         "A deposited check can bounce after the bank makes funds available (FTC)"],
 short=[
  ("Hook", "One buyer. Full asking price for Dad's truck, doesn't need to see it, and the check is two thousand too much.",
   "Full price, sight unseen", "Dhruv on camera holding a phone"),
  ("The ask", "Just send back the extra to my shipper, they say, and he'll pick up the truck. The check looks perfect.",
   "'Send the extra to my shipper'", "a tow truck with a question mark"),
  ("The trap", "Days later the check bounces. The two thousand you sent is gone, and sometimes so is the truck.",
   "Check bounces. Money's gone.", "a check tearing in half"),
  ("The rule", "Sell to buyers who see the car and pay in a way you can confirm, like meeting at your bank. Never send "
               "back an overpayment.", "Never refund an overpayment", f"{MASCOT} with car keys"),
 ],
 tt_title="Selling a car online: the overpaying buyer, played out",
 tt_hook="4 messages from a car 'buyer' and the 1 that gives the scam away.",
 tt_extra=[
  ("Pause", "Pause. Which message gave it away: not wanting to see the truck, the shipper, or the check for too much? "
            "Pick one.", "Pause: which message?", PAUSE_VIS),
  ("Answer", "The overpayment. Lots of real buyers are far away. But nobody honest pays too much on purpose and asks you to "
             "send money back. That one line is the whole scam.", "The overpayment is the scam",
   "walkthrough: the overpayment message circled"),
  ("Buying, too", "Buying a car online works the other way. A price far below market, a seller who can't meet, and an "
                  "'escrow' site you've never heard of. The FBI warns about that one. See the car, or walk away.",
   "Buying? See the car first.", "a car on a laptop screen"),
 ]),
# ===================================================================== week 33: official-looking scams
S(week=33, pillar=P_FAMILY, look="face cam", tt_look="illustrated",
 title="'You missed jury duty, there's a warrant': courts don't call",
 hook="1 call says you missed jury duty and there's a warrant. Federal courts say they don't call like that.",
 thumb="Missed jury duty? No.",
 hashtags=["juryduty", "governmentimposter", "warrant", "scamcall", "scamdecoded"],
 description="The fake jury duty warrant call, and what federal courts say about it.",
 caption="'This is the sheriff's office. You failed to appear for jury duty. Pay the fine now or we'll arrest you.' "
         "The federal courts warn about this call. Courts don't take fines over the phone.",
 sources=[COURTS_JUROR, REPORT],
 claims=["Federal courts warn about callers claiming people missed jury duty and must pay fines (US Courts)",
         "Federal courts don't ask for payment or sensitive information by phone or email for jury service (US Courts)"],
 short=[
  ("Hook", "One call. You missed jury duty, there's a warrant for your arrest, and you can pay the fine right now.",
   "'There's a warrant'", "Dhruv on camera holding a phone"),
  ("The ask", "The caller sounds official, gives a badge number, and wants a payment app, gift cards or a prepaid card, "
              "to cancel the warrant.", "'Pay now to cancel it'", "a badge next to a gift card"),
  ("The tell", "The federal courts say they don't call demanding fines, and don't ask for your Social Security number "
               "or card by phone.", "Courts don't take fines by phone", "a courthouse"),
  ("Do this", "Hang up. Call the court yourself, using the number on its own website, and ask if anything is real.",
   "Call the court yourself", f"{MASCOT} hanging up a phone"),
 ],
 tt_title="The jury duty warrant call: 3 tricks that make it sound real",
 tt_hook="3 tricks make the fake jury duty call sound real. Here they are, one at a time.",
 tt_extra=[
  ("Pause", "Pause. They gave you a badge number and a case number. Does that make it more real? Think about it.",
   "Pause: does a badge number help?", PAUSE_VIS),
  ("The tricks", "It doesn't. One: real-sounding names and badge numbers, made up in seconds. Two: a real court's name, "
                 "copied from the web. Three: they stay on the line while you go to the store, so you can't call anyone.",
   "Names, courts, 'stay on the line'", "three cards with a phone, a courthouse and a clock"),
  ("Already paid?", "Already paid? Call the gift card company or your bank right away, then report it at report fraud dot "
                    "f t c dot gov. Then tell someone. These calls work by keeping you alone.",
   "Paid? Call the card company.", "a phone and a gift card"),
 ]),
S(week=33, pillar=P_SECURITY, look="walkthrough", tt_look="screen recording",
 title="'Cloud storage full, photos deleted': check Settings instead",
 hook="1 email says your cloud storage is full and your photos will be deleted. Check Settings, not the link.",
 thumb="Storage full? Check Settings.",
 hashtags=["phishing", "cloudstorage", "photos", "iphone", "scamdecoded"],
 description="The fake 'cloud storage full' email, and the 10-second check in your phone's settings.",
 caption="'Your storage is full. Your photos and videos will be deleted.' Then a too-good upgrade deal. The FTC warns "
         "about these. Your phone's settings show your real storage.",
 sources=[FTC_CLOUD, FTC_PHISH],
 claims=["Scammers send fake 'cloud storage full' messages threatening to delete photos (FTC)",
         "Check your storage through your device or account settings, not a link in the message (FTC)"],
 short=[
  ("Hook", "One email. Your cloud storage is full, and your photos and videos will be deleted. Upgrade now, with a "
           "loyalty discount.", "'Your photos will be deleted'", "walkthrough: an email with a full storage bar"),
  ("The catch", "The link goes to a lookalike page that takes your card details, and sometimes your account password too.",
   "The link takes your card", "walkthrough: a fake payment form"),
  ("The tell", "Fear about your photos, a deadline, and a discount you never asked for. Real storage warnings show up in "
               "your phone's settings.", "Fear, deadline, discount", "a photo album with a clock"),
  ("Do this", "Don't click. Open Settings on your phone, tap your name, and look at storage. That's the real number.",
   "Settings, then storage", f"{MASCOT} holding a phone"),
 ],
 tt_title="'Photos will be deleted' email? My real storage screen",
 tt_hook="10 seconds in Settings tells you if the 'storage full' email is real. Here's the screen.",
 tt_extra=[
  ("Pause", "Pause. Before I open Settings, guess: is my storage full, like the email says?",
   "Pause: is it full?", PAUSE_VIS),
  ("The real screen", "Here's my screen. Settings, my name, then storage. Plenty of room. On Android it's under your "
                      "Google account storage. Either way, the real number is one tap from your home screen.",
   "Plenty of room", "Dhruv's screen: storage page, details blurred"),
  ("Already paid?", "Already typed your card into the upgrade page? Call your card company and ask for a new card. If you "
                    "typed a password, change it now and turn on two-step verification.",
   "Typed your card? Call the bank.", "a credit card and a padlock"),
 ]),
S(week=33, pillar=P_HOME, look="quiz pause", tt_look="face cam",
 title="'Your deed copy for $89': 1 official-looking letter",
 hook="1 official-looking letter offers your property deed for $89. Your county has it for a few dollars.",
 thumb="Your deed isn't $89",
 hashtags=["homeowner", "propertydeed", "mail", "realestate", "scamdecoded"],
 description="The deed copy and property notice mailers that look official, and what they really are.",
 caption="A letter with a seal, your parcel number and a 'response due' date offers a copy of your deed. It's a private "
         "company. The FTC says you can usually get a copy from your county for much less, or free.",
 sources=[FTC_DEED],
 claims=["Mailers offering property deed copies or records for a fee often come from private companies, not government (FTC)",
         "Homeowners can usually get a copy of their deed from the county recorder for little or no cost (FTC)"],
 short=[
  ("Hook", "One letter. Official seal, your parcel number, response due in ten days. Get a certified copy of your deed, "
           "eighty-nine dollars.", "'Response due in 10 days'", "a letter with a seal on a doormat"),
  ("Pause", "Pause. Government notice, or a company selling something? Look for the small print.",
   "Pause: government or company?", PAUSE_VIS),
  ("Answer", "A company. The small print says it's not a government agency. Your county recorder has your deed, often "
             "for a few dollars, or free online.", "A company, not the county", "small print under a magnifying glass"),
  ("Do this", "Don't pay. If you need a copy, go to your county recorder's own website. Check Mom and Dad's mail for "
              "these too.", "Go to your county's website", f"{MASCOT} holding a letter"),
 ],
 tt_title="My parents got a property letter. Here's what it was.",
 tt_hook="2 kinds of 'property notice' letters show up after people buy a home. Here's what they want.",
 tt_extra=[
  ("The other one", "The second kind is about property taxes: we can lower your assessment, or file your homestead "
                    "exemption, for a fee. Your county lets you do those yourself, usually for free.",
   "'We'll file it for a fee'", "a property tax form with a price tag"),
  ("The tell", "Both kinds use words like notice, record and due, plus a seal. Neither one is a bill. If you can't find "
               "who sent it, look for the words 'not a government agency' or 'not affiliated'.",
   "Look for 'not a government agency'", "a seal with a question mark"),
  ("Already paid?", "Already paid? Check what you got for it. If you never received anything, call your bank or card "
                    "company and report the mailer at report fraud dot f t c dot gov.",
   "Paid? Ask your bank.", "a phone and a bank card"),
 ]),
# ===================================================================== week 34: July 4th weekend
S(week=34, pillar=P_TEXT, look="illustrated", tt_look="walkthrough",
 title="'I found your dog, send me a code': 1 lost pet text to stop",
 hook="1 text says they found your lost dog, if you send a code to prove you're the owner.",
 thumb="Found your dog? Prove it.",
 hashtags=["lostpet", "lostdog", "fourthofjuly", "pets", "scamdecoded"],
 description="The scams that target people who post about a lost pet, and how to post safely.",
 caption="Fireworks scare a lot of pets out of yards. When you post a lost pet flyer with your number, scammers text "
         "too. Two versions: a code to 'verify' you, or money to bring the pet home.",
 sources=[BBB_LOST_PET, FTC_GVOICE],
 claims=["Scammers contact people who post lost pet flyers and ask for verification codes or money (BBB)",
         "Sharing a verification code can let a scammer set up an account in your name, like Google Voice (FTC)"],
 short=[
  ("Hook", "One text, right after you post a lost dog flyer. I think I found your dog. Send me the code I'm about to "
           "text, so I know you're really the owner.", "'Send me the code'", f"{MASCOT} holding a lost dog flyer"),
  ("The catch", "The code isn't from them. It's a sign-up code for an account in your name, like a phone number they can "
                "use for other scams.", "The code opens an account", "a phone with a key"),
  ("The tell", "Someone who has your dog sends a photo or meets you. They don't need a code, or money first.",
   "Real finders send a photo", "a dog with a camera"),
  ("Do this", "Never send a code. Ask for a current photo with something you name, and meet in a public place. Bring "
              "a friend.", "No codes. Ask for a photo.", f"{MASCOT} with a leash"),
 ],
 tt_title="Lost pet after the fireworks: 2 texts that aren't the finder",
 tt_hook="2 kinds of texts come after a lost pet flyer goes up. Neither is the finder.",
 tt_extra=[
  ("Pause", "Pause. Text two says: I have your dog, but I'm two hours away. Send fifty for gas and I'll drive her back. "
            "Would you send it?", "Pause: send $50 for gas?", PAUSE_VIS),
  ("Text two", "Don't. The money-first text is the other version. Ask for a photo of your pet next to today's newspaper, "
               "or something you name. Then meet in person, and pay nothing before you see your pet.",
   "No money before you see your pet", "walkthrough: the gas money message"),
  ("Posting safely", "When you post, leave out one detail only you'd know, like a marking or a collar color, and ask "
                     "callers to describe it. And call local shelters every day. Many lost pets end up there.",
   "Hold back 1 detail", "a flyer with one detail hidden"),
 ]),
S(week=34, pillar=P_TEENS, look="face cam", tt_look="quiz pause",
 title="'I sent you $300 by mistake': 1 payment to leave alone",
 hook="1 payment app message: 'I sent you $300 by mistake.' Sending it back is the mistake.",
 thumb="Sent by mistake? Don't send back.",
 hashtags=["venmo", "cashapp", "paymentapps", "fakepayment", "scamdecoded"],
 description="The 'accidental payment' scam on payment apps, and what to do instead of sending it back.",
 caption="Money shows up from a stranger, then a polite message asks for it back. The payment was made with a stolen "
         "card or account and gets reversed later. The money you sent back doesn't.",
 sources=[VENMO_SCAMS, CASH_SCAMS, FTC_PAY_APPS],
 claims=["Payment apps warn about strangers who send money 'by mistake' and ask for it back (Venmo)",
         "Payments from stolen accounts can be reversed, leaving you short (Venmo/Cash App)"],
 short=[
  ("Hook", "One payment from a stranger, three hundred dollars, and a message. So sorry, I sent that by mistake. Can "
           "you send it back?", "'Sent by mistake'", "Dhruv on camera holding a phone"),
  ("The catch", "Their payment came from a stolen card or account. It gets reversed, and the three hundred you sent "
                "from your own money doesn't.", "Their payment gets reversed", "a payment arrow bouncing back"),
  ("The tell", "A stranger, a polite rush, and a request to send it back yourself instead of asking the app.",
   "They ask you, not the app", "a speech bubble with a clock"),
  ("Do this", "Don't send it back. Contact the app's support from inside the app, and let them reverse it.",
   "Let the app reverse it", f"{MASCOT} pointing at a phone"),
 ],
 tt_title="Quiz: someone sent you $300 by mistake. Which reply is safe?",
 tt_hook="3 ways to answer the 'I sent you $300 by mistake' message. Only 1 is safe.",
 tt_extra=[
  ("Pause", "Pause. A: send the three hundred back. B: send it to a different account they give you. C: report it "
            "in the app and let support handle it. Which is safe?", "Pause: A, B or C?", PAUSE_VIS),
  ("Answer", "C. A costs you three hundred when their payment reverses. B is worse, because now the money goes somewhere "
             "else entirely. C costs nothing and moves nothing.", "C. Let support handle it.", "card C with a green check"),
  ("Already sent?", "Already sent it back? Report it in the app, and tell your bank if the app is linked to your card. Then "
                    "turn on payment notifications and set your payment app to private.",
   "Sent it? Report it in the app.", "a phone with a bell"),
 ]),
S(week=34, pillar=P_TEXT, look="screen recording", tt_look="illustrated",
 title="Famous face selling a 4th of July deal? 1 check first",
 hook="1 ad shows a famous face promoting a 4th of July deal. The video may be fake.",
 thumb="That celebrity didn't say it",
 hashtags=["deepfake", "fakeads", "fourthofjuly", "onlineshopping", "scamdecoded"],
 description="Fake celebrity endorsements in social media ads, and how to report them.",
 caption="A celebrity or TV doctor 'endorsing' a holiday deal, a miracle gadget or an investment. The FTC says many of "
         "these endorsements are fake, sometimes made with AI. Check before you buy.",
 sources=[FTC_CELEB, FTC_IMPOSTER_ADS],
 claims=["Scammers use fake celebrity endorsements, including AI-made videos, in ads (FTC)",
         "The FTC asks people to report imposter ads they see online (FTC, Nov 2026)"],
 original_element="Dhruv screen-records reporting an ad on his own phone (the platform's 'report ad' menu), no real "
                  "celebrity footage shown.",
 short=[
  ("Hook", "One ad in your feed. A famous face, a 4th of July sale, a product they 'use every day', seventy percent off.",
   "A famous face, a big deal", "Dhruv's screen: a feed with a blurred ad"),
  ("The catch", "The video can be made with AI, or the face borrowed without asking. The store behind it may not ship "
                "anything.", "The face can be fake", "a face with a pixel grid"),
  ("The check", "Search the celebrity's name plus the product. If they really endorsed it, it's on their own pages, not "
                "only in an ad.", "Search name + product", "Dhruv's screen: a search bar"),
  ("Do this", "Scroll past, and report the ad. Here's the menu. Two taps.", "Report the ad: 2 taps",
   "Dhruv's screen: the report ad menu"),
 ],
 tt_title="3 signs a celebrity ad in your feed is fake",
 tt_hook="3 signs the celebrity in that ad never said a word of it.",
 tt_extra=[
  ("Pause", "Pause. What's the first thing you'd check before buying from an ad with a famous face? Think about it.",
   "Pause: what would you check?", PAUSE_VIS),
  ("Signs", "Sign one, the lips don't quite match the words, or the voice sounds flat. Sign two, the deal ends today, "
            "with a countdown. Sign three, the site was set up recently and has no real contact details.",
   "Lips, countdown, new site", "three cards with a mouth, a clock and a globe"),
  ("Already bought?", "Already bought? If nothing arrives, or it's not what was shown, dispute the charge with your card "
                      "company. And report the ad to the FTC, which is asking people to send them in.",
   "Bought? Dispute the charge.", "a credit card with a phone"),
 ]),
]
