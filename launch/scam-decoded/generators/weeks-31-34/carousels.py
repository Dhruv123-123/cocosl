"""8 Instagram carousels for weeks 31-34. Weekly: one checklist carousel and one in a rotating format
(quiz, comparison, script, data)."""
from sources import *
from common import MASCOT, P_FAMILY, P_SECURITY, P_TEXT
from shorts import P_TEENS, P_JOBS, P_HOME


def C(**k):
    return k


def slides(cover, items, save, cover_vis):
    out = [("Hook", "", cover, cover_vis)]
    out += [(str(i), n, o, v) for i, (n, o, v) in enumerate(items, 1)]
    out.append(("Save this", save, "Save it. Share it.", f"{MASCOT} giving a thumbs up"))
    return out


CAROUSELS = [
C(week=31, look="checklist", pillar=P_TEENS, title="Teen money safety: 5 rules before the first summer paycheck",
 hook="5 rules to set up before your teen's first summer paycheck lands.", thumb="Teen money: 5 rules",
 hashtags=["teens", "summerjob", "paymentapps", "parenting", "scamdecoded"],
 description="Five money-safety rules for teens starting summer jobs.",
 caption="First job, first paycheck, first payment app. Five rules to go over together this weekend.",
 sources=[CASH_FLIP, FTC_PAY_APPS, ROBLOX_GEN, FTC_JOBS],
 claims=["Cash flipping offers are scams (Cash App)", "Payment apps are meant for people you know (FTC)"],
 segs=slides("Teen money: 5 rules", [
  ("Payment apps are for people you know in real life. Not sellers in DMs, not 'flippers'.", "1. Pay only people you know", "a phone with two friends"),
  ("Nobody multiplies money you send them. 'Send $50, get $500' is always a scam.", "2. No money flips", "a $50 bill with a red X"),
  ("Passwords go into the app or game only. Never into a 'free coins' site.", "3. Passwords stay in the app", "a padlock on a game controller"),
  ("A real job never pays you first and asks you to send part back.", "4. No check-first jobs", "a check with a stop sign"),
  ("Something feels off? Tell a parent. Nobody gets in trouble for asking.", "5. Ask first, always", "a parent and teen talking"),
 ], "Save this and go over it together this weekend.", f"{MASCOT} with a piggy bank")),
C(week=31, look="quiz", pillar=P_JOBS, title="Quiz: real summer job or scam? 3 offers to sort",
 hook="3 summer job offers, 2 are scams. Can you tell which before you swipe?", thumb="Real job or scam?",
 hashtags=["summerjob", "jobscam", "teens", "spotthescam", "scamdecoded"],
 description="A quiz carousel sorting three summer job offers.",
 caption="Quiz time. Three offers, and two of them are scams. Answers on the last slides. Examples are fictional.",
 sources=[FTC_JOBS, FTC_NANNY, FTC_CHECKS],
 claims=["Fake employers send checks and ask for money back (FTC)", "Real jobs don't charge you to start (FTC)"],
 segs=slides("Real job or scam?", [
  ("A: 'Babysit 3 days a week, $600. I'll mail a check before we meet. Send some to our supplier.'", "A: check-first babysitting", "a check in an envelope"),
  ("B: 'Lifeguard at the town pool. Apply online, interview in person, training paid.'", "B: town pool lifeguard", "a lifeguard chair"),
  ("C: 'Brand ambassador! Buy our starter kit for $99, then earn commissions.'", "C: pay-to-start 'ambassador'", "a box with a price tag"),
  ("Answer: B is real. A is the fake check scam. C makes you pay to get the job.", "B is the real one", "card B with a green check"),
 ], "How did you do? Save this for anyone job hunting this summer.", f"{MASCOT} holding a score card")),
C(week=32, look="checklist", pillar=P_HOME, title="Selling a car online: 6 checks before you hand over the keys",
 hook="6 checks before you sell a car to someone online.", thumb="Selling a car: 6 checks",
 hashtags=["carsales", "marketplace", "fathersday", "fakecheck", "scamdecoded"],
 description="Six checks for selling a car online safely.",
 caption="Selling Dad's old car this summer? Six checks that keep the money and the keys where they belong.",
 sources=[FTC_CAR_SELLERS, FTC_CHECKS, FBI_CAR],
 claims=["Scammers send fake checks to car sellers and ask for the difference back (FTC)"],
 segs=slides("Selling a car: 6 checks", [
  ("The buyer wants to see the car or have it inspected. No interest at all is a warning.", "1. They want to see it", "a car in a driveway"),
  ("Meet in daylight, in a public place. Many police stations have safe exchange spots.", "2. Meet in public", "a parking lot with a sign"),
  ("Get paid in a way you can confirm before the keys move, like at your bank together.", "3. Confirm the payment", "a bank building"),
  ("Never accept more than the price and send back the difference. That's the scam.", "4. No overpayments", "a check with a red X"),
  ("Don't share codes sent to your phone to 'prove you're real'.", "5. No codes", "a phone with a lock"),
  ("Sign over the title only after the money has truly cleared.", "6. Title last", "a title document with a pen"),
 ], "Save this, and send it to anyone selling a car this summer.", f"{MASCOT} with car keys")),
C(week=32, look="comparison", pillar=P_HOME, title="Your car's warranty vs the 'final notice' caller: 4 differences",
 hook="4 differences between your car's real warranty and the 'final notice' call.", thumb="Real warranty vs caller",
 hashtags=["carwarranty", "robocall", "fathersday", "cars", "scamdecoded"],
 description="How a manufacturer's warranty differs from what 'final notice' callers sell.",
 caption="What you already have, and what the caller is selling. Four differences.",
 sources=[FTC_SERVICE, FTC_WARRANTY, FTC_WARRANTY_CALLS],
 claims=["What's often sold as an 'extended warranty' is a service contract (FTC)", "Auto warranty robocalls often aren't from your dealer or manufacturer (FTC)"],
 segs=slides("Real warranty vs caller", [
  ("Who: your warranty comes from the carmaker. The caller is usually a service contract seller.", "1. Carmaker vs seller", "a car and a phone"),
  ("Cost: a warranty comes with the car. A service contract costs extra, sometimes thousands.", "2. Included vs extra", "a price tag"),
  ("Proof: your warranty is in the manual or with the dealer. The caller can't say which car.", "3. Written vs vague", "an owner's manual"),
  ("Pressure: a warranty doesn't have a 'final notice'. The caller wants payment today.", "4. No rush vs today", "a clock"),
 ], "Save this for Dad, and tell him he can hang up.", f"{MASCOT} holding a manual")),
C(week=33, look="checklist", pillar=P_FAMILY, title="Jury duty: 4 facts that end the fake warrant call",
 hook="4 facts about jury duty that end the fake warrant call.", thumb="Jury duty: 4 facts",
 hashtags=["juryduty", "governmentimposter", "scamcall", "seniors", "scamdecoded"],
 description="Four facts about jury service that expose the fake warrant call.",
 caption="The fake jury duty call goes after people who are scared of being arrested. Four facts that take the fear away.",
 sources=[COURTS_JUROR, REPORT],
 claims=["Federal courts don't ask for sensitive information or payment by phone or email for jury service (US Courts)"],
 segs=slides("Jury duty: 4 facts", [
  ("Jury notices come by mail. A surprise call about a missed date is the warning sign.", "1. Courts write first", "an envelope with a courthouse"),
  ("Federal courts say they don't ask for your Social Security number or card by phone.", "2. No SSN by phone", "a phone with a red X"),
  ("No court takes gift cards, crypto or a payment app to cancel a warrant.", "3. No gift cards", "a gift card with a red X"),
  ("Worried? Call the court yourself, using the number on its own website.", "4. Call the court yourself", "a phone and a courthouse"),
 ], "Save this, and share it with parents and grandparents.", f"{MASCOT} with a gavel")),
C(week=33, look="script", pillar=P_FAMILY, title="Official-looking mail: 4 lines to read before you pay anything",
 hook="4 lines on any official-looking letter tell you if it's a bill or a sales pitch.", thumb="Bill or sales pitch?",
 hashtags=["homeowner", "mail", "seniors", "propertydeed", "scamdecoded"],
 description="Four things to read on any official-looking letter before paying.",
 caption="Seals, case numbers and 'response due' dates make sales mail look like a bill. Read these four lines first.",
 sources=[FTC_DEED, FTC_DIRECTORY],
 claims=["Mailers offering property records for a fee often come from private companies (FTC)"],
 segs=slides("Bill or sales pitch?", [
  ("The sender. Look for a company name, not just a seal. 'Records Office' isn't a government agency.", "1. Who sent it?", "an envelope with a seal"),
  ("The small print. 'Not affiliated with any government agency' means it's an offer.", "2. Read the small print", "a magnifying glass"),
  ("The ask. A real bill matches something you ordered or owe. An offer wants a fee for something you can get free.", "3. Did you order it?", "a receipt"),
  ("The check. Look up your county or the agency yourself and ask. Don't use the number on the letter.", "4. Check it yourself", "a laptop with a county site"),
 ], "Save this and look through Mom and Dad's mail pile together.", f"{MASCOT} holding a letter")),
C(week=34, look="checklist", pillar=P_TEXT, title="Lost pet over the 4th? 5 steps that keep scammers out",
 hook="5 steps to find a lost pet after the fireworks, without feeding scammers.", thumb="Lost pet: 5 steps",
 hashtags=["lostpet", "lostdog", "fourthofjuly", "pets", "scamdecoded"],
 description="Five steps for finding a lost pet safely around July 4th.",
 caption="Fireworks send pets running. Five steps to get yours home, and to keep the fake 'finders' out.",
 sources=[BBB_LOST_PET, FTC_GVOICE],
 claims=["Scammers target lost pet posts asking for codes or money (BBB)"],
 segs=slides("Lost pet: 5 steps", [
  ("Before the 4th: check the microchip details are current, and the collar tag has your number.", "1. Update the chip", "a dog with a tag"),
  ("Post the flyer, but hold back one detail only you know, like a marking.", "2. Hold back 1 detail", "a flyer with a hidden spot"),
  ("Call and visit local shelters every day. Many lost pets end up there.", "3. Call shelters daily", "an animal shelter"),
  ("Never send a code or money to a 'finder'. Ask for a photo with something you name.", "4. No codes, no money", "a phone with a red X"),
  ("Meet in a public place, with a friend, and pay nothing until you see your pet.", "5. Meet in public", "two people at a park"),
 ], "Save this before the fireworks, and share it with your neighbourhood group.", f"{MASCOT} with a leash")),
C(week=34, look="script", pillar=P_TEENS, title="'I sent you money by mistake': 3 replies to copy",
 hook="3 replies to copy when a stranger says they sent you money by mistake.", thumb="'Sent by mistake'? Copy this.",
 hashtags=["venmo", "cashapp", "paymentapps", "fakepayment", "scamdecoded"],
 description="Three safe replies to the 'accidental payment' message.",
 caption="A stranger sends money and asks for it back. Three replies you can copy, and the one thing not to do.",
 sources=[VENMO_SCAMS, CASH_SCAMS],
 claims=["Payment apps warn about strangers who send money 'by mistake' and ask for it back (Venmo)"],
 segs=slides("'Sent by mistake'? Copy this.", [
  ("'Please contact the app's support to reverse it. I've reported it too.'", "1. Point them to support", "a speech bubble with a phone"),
  ("'I don't send payments to people I don't know. Support can sort it out.'", "2. Hold the line", "a speech bubble with a shield"),
  ("Or no reply at all. Report the payment in the app and leave the money alone.", "3. Say nothing, report it", "a phone with a flag"),
  ("Don't send it back, and never to a different account they name.", "Not this: send it back", "an arrow with a red X"),
 ], "Save this, and send it to anyone who uses a payment app.", f"{MASCOT} pointing at a phone")),
]
