"""12 Shorts for weeks 27-30 (May 9 - Jun 5 2027), each with its TikTok minute cut.

Each Short: 4 beats, 60-120 words. Each TikTok cut: a new hook, the Short's middle beats, a pause beat,
a second example and the fix: 165-230 words. `look` is the visual format (see ORIGINALITY_PASS.md);
consecutive videos never share one.
"""
from sources import *
from common import MASCOT, P_FAMILY, P_INVEST, P_TEXT

P_HEALTH = "Medicare and health scams"
P_JOBS = "job, school and rental scams"
P_TRAVEL = "travel and on-the-road scams"


def S(**k):
    return k


SHORTS = [
# ===================================================================== week 27: Mother's Day
S(week=27, pillar=P_HEALTH, look="illustrated", tt_look="face cam",
 title="'Free' Medicare genetic test: 1 cheek swab that costs your Medicare number",
 hook="1 cheek swab, 'free with Medicare.' What it really costs is your Medicare number.",
 thumb="The 'free' DNA test",
 hashtags=["medicare", "medicarefraud", "seniors", "geneticTesting", "scamalert", "scamdecoded"],
 description="How the 'free genetic test' Medicare scam works, and the one rule that stops it.",
 caption="A free cancer or heart DNA test, paid for by Medicare, offered by phone, at a health fair or at your door. "
         "It's a way to get your Medicare number, and the bill can land on you.",
 sources=[OIG_GENETIC, FTC_DNA, MEDICARE_4RS],
 claims=["Scammers offer 'free' genetic tests to get Medicare numbers (HHS-OIG fraud alert)",
         "If Medicare denies a test your doctor didn't order, you could be responsible for the cost (HHS-OIG)",
         "Medicare doesn't call to offer DNA kits (FTC)"],
 short=[
  ("Hook", "One cheek swab, free with Medicare. That's the pitch, by phone, at a health fair, or at the door.",
   "'Free with Medicare'", f"{MASCOT} looking at a cotton swab with a price tag"),
  ("The catch", "To send the kit, they need your Medicare number. Then they bill Medicare for a test you didn't need, and "
                "your number can be used again.", "They want your Medicare number", "a Medicare-style card with a hook"),
  ("The cost", "If your own doctor didn't order it and Medicare denies the claim, the bill can come back to you.",
   "The bill can come to you", "an envelope with a large bill"),
  ("The rule", "Only take a test your own doctor orders. Never give your Medicare number to a caller or a stranger at "
               "a booth.", "Only tests your doctor orders", f"{MASCOT} holding a stop sign"),
 ],
 tt_title="Mom got a call about a free DNA test. Here's the 1 question to ask.",
 tt_hook="1 question ends the 'free Medicare DNA test' call. Here's how the call goes first.",
 tt_extra=[
  ("Pause", "Pause. What would you say if they asked you, right now, for your Medicare number to ship the kit? Think about it.",
   "Pause: what do you say?", "a full-screen countdown card"),
  ("Example 2", "The door version is the same. A table outside the pharmacy, a clipboard, a free swab, and a form that "
                "asks for your card. Same rule. Walk on.", "Same scam, at a booth", "a folding table with a clipboard"),
  ("The question", "Here's the question: which doctor ordered this? If the answer isn't your doctor, hang up. Then check "
                   "your Medicare statements for tests you never had.", "'Which doctor ordered this?'",
   f"{MASCOT} holding a phone and a statement"),
 ]),
S(week=27, pillar=P_HEALTH, look="walkthrough", tt_look="illustrated",
 title="'Your doctor approved a free back brace': 1 call to hang up on",
 hook="1 call offers a free back brace. Medicare pays, the scammer profits, and your number is out there.",
 thumb="Free brace? Hang up.",
 hashtags=["medicare", "medicarefraud", "backbrace", "seniors", "scamalert", "scamdecoded"],
 description="Why calls offering free braces and medical equipment through Medicare are a scam.",
 caption="'Do you have back or knee pain? Medicare will cover a brace at no cost.' A brace you never needed shows up, "
         "Medicare gets billed, and your number is now in a scammer's list.",
 sources=[OIG_BRACE, MEDICARE_4RS, MEDICARE_FRAUD],
 claims=["Scammers call offering braces and medical equipment to get Medicare numbers (HHS-OIG)",
         "Check Medicare statements for equipment you didn't order (Medicare)"],
 short=[
  ("Hook", "One call. Do you have back or knee pain? Medicare will cover a brace at no cost to you.",
   "'A brace at no cost'", "phone screen mockup: incoming call, 'Medical Benefits'"),
  ("The ask", "Then: just confirm your Medicare number so we can ship it. A brace you didn't need arrives. Medicare gets "
              "the bill, and your number gets sold on.", "'Just confirm your number'", "a box on a doorstep"),
  ("The tell", "Medicare and your doctor don't cold-call to sell you equipment. A caller who wants your number is the scam.",
   "Medicare doesn't cold-call", "a phone with a red X"),
  ("Do this", "Hang up. If a box arrives that nobody ordered, refuse the delivery, and call 1-800-MEDICARE to report it.",
   "Hang up. Report boxes you didn't order.", f"{MASCOT} pointing at a phone number"),
 ],
 tt_title="A brace arrived that nobody ordered: 3 things to do today",
 tt_hook="3 things to do today if a brace or medical kit shows up that nobody ordered.",
 tt_extra=[
  ("Pause", "Pause. Before I say it, what would you do with the box? Keep it? Send it back? Call the number on the slip?",
   "Pause: what would you do?", "a full-screen countdown card"),
  ("The three", "One, don't call the number on the packing slip. Two, call 1-800-MEDICARE and tell them what arrived. "
                "Three, read your Medicare statement for the next few months and look for equipment you never got.",
   "Don't call the slip · call Medicare · check statements", "a three-step checklist"),
 ]),
S(week=27, pillar=P_FAMILY, look="face cam", tt_look="walkthrough",
 title="A 'courier' at Grandma's door: 1 grandparent scam twist to know",
 hook="1 knock at the door turns a grandparent scam phone call into a cash pickup.",
 thumb="Never hand cash to a courier",
 hashtags=["grandparentscam", "mothersday", "protectyourparents", "familysafety", "scamalert", "scamdecoded"],
 description="Grandparent scammers now send a 'courier' to collect cash. Here's the tell and the safe word that stops it.",
 caption="The call says a grandchild is in jail and needs bail. Then a courier comes to the house for the cash. "
         "No real court or lawyer sends someone to pick up cash at your door.",
 sources=[FTC_GRAND_DOOR, IC3_COURIER, FTC_AI_VOICE],
 claims=["Grandparent scammers send couriers to collect cash at victims' homes (FBI IC3 PSA, Jul 2021; FTC)",
         "Scammers can clone voices from short audio clips (FTC)"],
 short=[
  ("Hook", "Grandma, it's me. I was in an accident, I'm in jail, and I need bail. Don't tell Mom.",
   "'Don't tell Mom'", "Dhruv on camera, reading from a phone"),
  ("The twist", "Then: a courier will come by to pick up the cash. No wire, no gift cards. Just a stranger at the door.",
   "'A courier will pick it up'", "a front door with a shadow"),
  ("The tell", "No court, lawyer or bail office sends someone to your house to collect cash. And a panicked voice can be "
               "faked now.", "Courts don't send couriers", "a gavel with a red X"),
  ("The fix", "Hang up and call your grandchild, or their parents, on a number you already have. And pick a family safe "
              "word this Mother's Day.", "Hang up. Call them back. Safe word.", f"{MASCOT} with a family photo"),
 ],
 tt_title="Mother's Day gift idea: 1 safe word that stops the courier scam",
 tt_hook="1 word, picked at Mother's Day lunch, stops the grandparent courier scam.",
 tt_extra=[
  ("Pause", "Pause. If someone knocked right now and said, I'm here for your grandson's bail money, what would you do?",
   "Pause: someone knocks. Now what?", "a full-screen countdown card"),
  ("Example 2", "Some callers keep you on the phone the whole time the courier is driving over, so you can't check. "
                "Others send a second courier for more money the next day. Any courier at all is the tell.",
   "They keep you on the line", "a phone timer and a car"),
  ("Safe word", "So at lunch, pick a word only the family knows. Anyone calling in a panic for money has to say it. No "
                "word, no money, no door.", "No word, no money, no door", f"{MASCOT} whispering to a grandmother"),
 ]),
# ===================================================================== week 28: graduation
S(week=28, pillar=P_JOBS, look="walkthrough", tt_look="face cam",
 title="'Interview on Telegram today': 1 job offer new grads should walk away from",
 hook="1 'interview' over a chat app, an offer an hour later, and a check for your equipment. It's a scam.",
 thumb="Chat-app interview? Walk away.",
 hashtags=["newgrad", "jobscam", "jobsearch", "classof2027", "scamalert", "scamdecoded"],
 description="Fake recruiters interview new grads over chat apps, then send a fake check for equipment.",
 caption="An interview done entirely by text on Telegram, WhatsApp or Signal, a same-day offer, then a check to buy your "
         "laptop from 'our vendor'. The check bounces, and the money you sent the vendor is gone.",
 sources=[FTC_TELEGRAM, FTC_JOB_TEXT, FTC_CHECKS, FTC_STUDENT_JOBS],
 claims=["Scammers conduct fake job interviews over messaging apps (FTC)",
         "Fake job scams send checks for equipment, then ask you to pay a 'vendor' (FTC)"],
 short=[
  ("Hook", "One interview, all by text on a chat app. An hour later: congratulations, you're hired.",
   "'You're hired' in 1 hour", "phone mockup: chat app interview messages"),
  ("The check", "Next, a check arrives to buy your laptop, from their approved vendor. You deposit it and pay the vendor.",
   "'Buy equipment from our vendor'", "phone mockup: a check image in chat"),
  ("The bounce", "Days later the check bounces. The bank takes the money back, and what you paid the vendor is gone.",
   "The check bounces. You pay.", "a rubber check bouncing"),
  ("The rule", "Real employers interview by video or in person, and never send you money to buy their equipment.",
   "Real jobs don't send checks first", f"{MASCOT} in a graduation cap holding a stop sign"),
 ],
 tt_title="I almost got hired by a scammer: the 3 messages that gave it away",
 tt_hook="3 messages give away a fake job offer. Here's the whole chat, step by step.",
 tt_extra=[
  ("Pause", "Pause. Which message would have made you stop? The chat-app interview, the instant offer, or the check?",
   "Pause: where would you stop?", "a full-screen countdown card"),
  ("Example 2", "A newer version skips the check and asks for your Social Security number and bank details for "
                "onboarding, before you've signed anything. That's identity theft, not paperwork.",
   "SSN before an offer letter? No.", "a form with an SSN box highlighted"),
  ("The check", "Look the company up yourself, find its real careers page, and email the recruiter at the company's real "
                "domain. If they won't do a video call, walk away.", "Find the real careers page",
   f"{MASCOT} at a laptop with a magnifying glass"),
 ]),
S(week=28, pillar=P_JOBS, look="illustrated", tt_look="quiz pause",
 title="'You won a scholarship, just pay the fee': 0 real ones charge you",
 hook="0 real scholarships make you pay to apply, or pay a fee to collect.",
 thumb="Scholarships don't charge",
 hashtags=["scholarships", "financialaid", "fafsa", "collegebound", "scamalert", "scamdecoded"],
 description="How scholarship and financial aid scams work, and where to get help for free.",
 caption="A letter says you've won a scholarship you never applied for, just pay a processing fee. Or a service charges "
         "to fill in the FAFSA. Real scholarships don't charge, and the FAFSA is free.",
 sources=[FTC_SCHOLAR, FTC_SCHOOL],
 claims=["You don't have to pay to apply for scholarships or federal aid (FTC)",
         "The FAFSA is free to fill out (FTC; studentaid.gov)"],
 short=[
  ("Hook", "Zero real scholarships make you pay to apply, or pay a fee to collect. Here's what the fake ones look like.",
   "Real scholarships don't charge", f"{MASCOT} in a graduation cap"),
  ("The letter", "Congratulations, you've been selected for a scholarship you never applied for. Just pay a small "
                 "processing fee.", "'Just pay a small fee'", "an envelope with a gold seal"),
  ("The service", "Or a company charges to fill in the FAFSA, or promises money in exchange for a fee. The FAFSA is free, "
                  "and you can do it yourself.", "The FAFSA is free", "a form with a free tag"),
  ("Do this", "Get free help from your school's financial aid office. Never pay to apply or to claim a prize.",
   "Ask the aid office. Never pay.", "a school building with a help sign"),
 ],
 tt_title="Quiz: which of these 3 scholarship offers is the scam?",
 tt_hook="3 scholarship offers, 1 is real. Pause and pick before I tell you.",
 tt_extra=[
  ("Pause", "Pause. Offer A says you won, pay a fee to claim it. Offer B charges to file your FAFSA. Offer C is free, "
            "with an essay due in March. Which ones are scams?", "Pause: A, B or C?", "three cards labelled A B C"),
  ("Answer", "A and B are the scams. C is how real scholarships work: you apply, it's free, and there's a deadline.",
   "A and B: scams. C: real.", "card C with a green check"),
 ]),
S(week=28, pillar=P_JOBS, look="data chart", tt_look="walkthrough",
 title="'I'm out of the country, so I can't show you the apartment': 1 rental red flag",
 hook="1 line from a landlord ends the deal: I can't show you the apartment, but send the deposit.",
 thumb="Can't see it? Don't pay.",
 hashtags=["firstapartment", "rentalscam", "newgrad", "apartmenthunting", "scamalert", "scamdecoded"],
 description="Rental listing scams aimed at first-time renters, and the rule that stops them.",
 caption="A great price, a landlord who's 'out of the country', and a deposit by payment app before you see the place. "
         "People have reported $65 million in losses to rental scams, according to the FTC.",
 sources=[FTC_RENTAL, FTC_RENTAL_ALERT, FTC_RENTAL_DATA],
 claims=["Rental scammers copy real listings and ask for deposits before you see the place (FTC)",
         "People reported $65 million in losses to rental scams (FTC Data Spotlight, Dec 2025)"],
 short=[
  ("Hook", "One line ends the deal. I'm out of the country, so I can't show you the apartment, but send the deposit to "
           "hold it.", "'I can't show it, but send the deposit'", "an apartment door with a padlock"),
  ("The setup", "The photos are copied from a real listing. The rent is low. Two other people are interested, so pay today.",
   "Copied photos. Low rent. Rush.", "a listing photo with a copy icon"),
  ("The number", "People reported losing sixty-five million dollars to rental scams to the FTC, and that's only the "
                 "ones who reported it.", "$65M reported lost to rental scams", "a bold amber number on navy"),
  ("The rule", "Never pay before you, or someone you trust, has been inside and met the landlord or agent.",
   "See it first. Then pay.", f"{MASCOT} holding a key"),
 ],
 tt_title="Your first apartment listing has 4 red flags. Can you find them?",
 tt_hook="4 red flags in 1 apartment listing. Pause and count them before I say them.",
 tt_extra=[
  ("Pause", "Pause and count. Low rent. A landlord who can't meet. A deposit by payment app or wire. And pressure to pay "
            "today. That's four.", "Pause: count the flags", "a full-screen countdown card"),
  ("The checks", "Before you pay, search the address and the photos online. If the same photos show up under another "
                 "name or price, it's copied. Ask for a video tour in real time, and pay by check or card, never wire or "
                 "gift card.", "Reverse search the photos", "a magnifying glass over a photo"),
 ]),
# ===================================================================== week 29: Military Appreciation Month
S(week=29, pillar=P_FAMILY, look="face cam", tt_look="illustrated",
 title="'We'll get you a bigger VA pension, for a fee': 1 offer veterans should refuse",
 hook="1 'free seminar' about VA pension, then a fee and a new annuity. It's called pension poaching.",
 thumb="VA help is free",
 hashtags=["veterans", "vapension", "militaryappreciationmonth", "seniors", "scamalert", "scamdecoded"],
 description="How pension poaching works, and where veterans get free, accredited help with VA claims.",
 caption="Advisers who promise a bigger VA pension, charge fees, and move savings into trusts or annuities can cost "
         "veterans and their families. Free help comes from VA-accredited representatives.",
 sources=[VA_POACH, VAOIG_POACH, VA_REP, FTC_VET_BENEFITS],
 claims=["Pension poachers charge fees and move assets into products that can hurt eligibility (VA, VA OIG)",
         "Accredited representatives from veterans service organizations help with claims for free (VA)"],
 short=[
  ("Hook", "One free lunch seminar about your VA pension. Then a fee, and a plan to move your savings into an annuity.",
   "A free seminar, then a fee", "Dhruv on camera holding a flyer"),
  ("The pitch", "They promise to qualify you for more pension, fast. They charge to fill in forms, and sell products that "
                "lock up your money.", "'More pension, fast'", "a stack of forms with a dollar sign"),
  ("The tell", "Help with a VA claim is free from accredited representatives. Fees and investment products are the tell.",
   "Real help is free", "a veteran's cap with a green check"),
  ("Do this", "Look up an accredited representative on VA's own website, or ask a veterans service organization.",
   "Use a VA-accredited rep", f"{MASCOT} saluting"),
 ],
 tt_title="Dad's a veteran? 3 questions before anyone 'helps' with his pension",
 tt_hook="3 questions to ask anyone offering to help a veteran with a VA pension.",
 tt_extra=[
  ("Pause", "Pause. If someone offers to help, what would you ask first? Think about it.",
   "Pause: what would you ask?", "a full-screen countdown card"),
  ("The three", "One: are you accredited by VA? You can check their name on VA's accreditation search. Two: what will "
                "this cost? Help filing a first claim shouldn't cost anything. Three: will this move any of my savings? If "
                "yes, get a second opinion first.", "Accredited? Cost? Moving savings?", "three question marks"),
 ]),
S(week=29, pillar=P_FAMILY, look="quiz pause", tt_look="face cam",
 title="'Help veterans this Memorial Day': 2-minute check before you give",
 hook="2 minutes before you give to a veterans' charity, and your money reaches veterans.",
 thumb="Check before you give",
 hashtags=["memorialday", "veterans", "charity", "donate", "scamalert", "scamdecoded"],
 description="Fake veterans' charity calls spike before Memorial Day. Here's how to check one in two minutes.",
 caption="Calls and texts asking for donations to help veterans spike before Memorial Day. Some are real, some aren't, "
         "and some send very little to veterans. Check before you give.",
 sources=[FTC_VET_CHARITY, FTC_CHARITY],
 claims=["Scammers use names that sound like real veterans' charities (FTC)",
         "Check charities with watchdog groups before giving; don't pay by gift card or wire (FTC)"],
 short=[
  ("Hook", "Two minutes before you give to a veterans' charity. Quiz first: which of these is a red flag?",
   "Quiz: spot the red flag", "three cards: name, pressure, payment"),
  ("The asks", "A name that sounds like a big charity. A caller who wants the money today. And a request for a gift card "
               "or a wire.", "Lookalike name · today · gift card", "the three cards lit amber"),
  ("Answer", "All three. Real charities take your gift next week too, and never ask for gift cards or wires.",
   "All 3 are red flags", "a green check over the answer"),
  ("The check", "Look the charity up yourself, check it with a watchdog like Give.org or Charity Navigator, and give on "
                "its own website.", "Look it up · check it · give direct", f"{MASCOT} holding a flag and a heart"),
 ],
 tt_title="Before Memorial Day: the veterans' charity call, line by line",
 tt_hook="1 Memorial Day charity call, line by line, and the 2-minute check that beats it.",
 tt_extra=[
  ("Pause", "Pause. The caller says most of your gift goes straight to wounded vets. How would you check that?",
   "Pause: how would you check?", "a full-screen countdown card"),
  ("Example 2", "Some calls are real fundraisers, but the charity keeps very little. A watchdog report tells you how "
                "much goes to programs. If the caller can't answer, or won't send anything in writing, hang up.",
   "Ask: how much reaches vets?", "a pie chart with a small slice"),
 ]),
S(week=29, pillar=P_INVEST, look="walkthrough", tt_look="data chart",
 title="'Deployed overseas, can't video call': 4 tells of a fake soldier profile",
 hook="4 tells of a fake soldier on a dating app, and why they always need money.",
 thumb="Fake soldier: 4 tells",
 hashtags=["romancescam", "militaryromance", "onlinedating", "veterans", "scamalert", "scamdecoded"],
 description="Scammers pose as deployed service members online. Here are the tells.",
 caption="Scammers steal service members' photos and names to start online romances, then need money for leave, "
         "a flight home or a 'shipping fee'. Real service members don't need you to pay for their leave.",
 sources=[FTC_MIL_ROMANCE, ARMY_ROMANCE, FTC_ROMANCE, SPOT],
 claims=["Romance scammers impersonate service members using stolen photos (Army CID; FTC)",
         "Service members don't need to pay for leave or to come home (Army CID)",
         "Nearly 60% of 2025 romance scam reports with a loss started on social media (FTC Data Spotlight, Apr 2026)"],
 short=[
  ("Hook", "Four tells of a fake soldier profile. One: deployed overseas, so they can never video call.",
   "1: never on video", "phone mockup: dating app chat"),
  ("Two and three", "Two: they move fast to love and marriage. Three: they want to move to WhatsApp or email.",
   "2: fast love · 3: off the app", "phone mockup: chat moving apps"),
  ("Four", "Four: they need money. For leave, a flight home, a package, or a fee to end their deployment. That's not how "
           "the military works.", "4: they need money", "phone mockup: money request highlighted"),
  ("The fix", "Reverse search their photos, keep chatting in the app, and never send money to someone you haven't met.",
   "Never send money to someone you haven't met", f"{MASCOT} holding a reverse search icon"),
 ],
 tt_title="Romance scams by the numbers, and the 1 rule that beats them",
 tt_hook="1 rule beats every romance scam, including the fake soldier. Here's why it matters.",
 tt_extra=[
  ("Pause", "Pause. If they finally agree to a video call but the camera is always broken, what does that tell you?",
   "Pause: broken camera again?", "a full-screen countdown card"),
  ("The number", "In FTC data, nearly six in ten reported romance scams started on social media. Fake soldiers are one of "
                 "the oldest versions, because a uniform earns trust fast.", "~6 in 10 started on social media",
   "a bold amber number on navy"),
 ]),
# ===================================================================== week 30: summer travel
S(week=30, pillar=P_TRAVEL, look="walkthrough", tt_look="quiz pause",
 title="'Your flight is canceled, call to rebook': 1 text to check in the airline app",
 hook="1 text says your flight is canceled and gives a number to rebook. Don't call it.",
 thumb="Flight canceled? Check the app.",
 hashtags=["travel", "flightcanceled", "summertravel", "airline", "scamalert", "scamdecoded"],
 description="Fake flight cancellation texts and lookalike airline help lines, and how to rebook safely.",
 caption="A text says your flight is canceled, call this number to rebook. The 'agent' charges a rebooking fee and takes "
         "your card. Check the airline's own app or website instead.",
 sources=[FTC_AIRLINE, FTC_TRAVEL, FTC_TRAVEL_2026],
 claims=["Scammers pose as airline customer service by text, search ads and social media (FTC)",
         "Contact airlines using the number or app from your booking or the airline's website (FTC)"],
 short=[
  ("Hook", "One text: your flight has been canceled. Call this number to rebook.", "'Your flight is canceled'",
   "phone mockup: flight cancellation text"),
  ("The call", "A friendly agent finds you a new flight, for a rebooking fee. They take your card, and your new ticket "
               "never shows up.", "'Small rebooking fee'", "phone mockup: call with fee"),
  ("The tell", "The number came from a text, not from the airline's app or your booking. Scammers also buy search ads "
               "for airline help lines.", "Wrong number, not the airline", "a search result with a fake badge"),
  ("Do this", "Open the airline's own app, or the website you typed yourself. Your real flight status is there.",
   "Check the airline's own app", f"{MASCOT} holding a boarding pass"),
 ],
 tt_title="Quiz: which airline help number is real?",
 tt_hook="2 airline help numbers on your screen, 1 is a scammer. Pause and pick.",
 tt_extra=[
  ("Pause", "Pause. One number came from a text about your canceled flight. The other is printed in the airline app. "
            "Which do you call?", "Pause: which number?", "two phone numbers side by side"),
  ("Answer", "The app. Search ads and social media replies can be scammers too, so the safest numbers are in the "
             "airline's app and on your booking confirmation.", "The app. Always.", "the app number with a green check"),
 ]),
S(week=30, pillar=P_TRAVEL, look="illustrated", tt_look="walkthrough",
 title="That 'official' hotel site in your search: 1 check before you book",
 hook="1 search ad looks like the hotel's own site. It isn't, and the room may not exist.",
 thumb="Is it the real hotel site?",
 hashtags=["summertravel", "hotelbooking", "travelscam", "vacation", "scamalert", "scamdecoded"],
 description="Lookalike booking sites in search ads, and how to make sure you're booking the real thing.",
 caption="Lookalike booking sites buy ads, copy hotel photos and take your card. Some are real resellers with hidden "
         "fees, some are scams. Book on the hotel's own site, or a booking site you already trust.",
 sources=[FTC_TRAVEL, FTC_TRAVEL_2026],
 claims=["Scammers create lookalike travel booking sites and ads (FTC)",
         "Paying by credit card gives you dispute rights (FTC)"],
 short=[
  ("Hook", "One search ad looks exactly like the hotel's own website. Same photos, great price.",
   "'Official site'", f"{MASCOT} looking at a search result"),
  ("The catch", "You pay, and get a confirmation that the hotel has never heard of. Or the price doubles with fees at "
                "checkout.", "A booking the hotel's never seen", "a hotel front desk with a question mark"),
  ("The tell", "Look at the web address. If it isn't the hotel's real address, it's a reseller at best, and a scam at worst.",
   "Read the web address", "an address bar zoomed in"),
  ("Do this", "Type the hotel's address yourself, call the hotel to confirm, and pay by credit card.",
   "Type it yourself. Confirm. Card.", f"{MASCOT} with a suitcase"),
 ],
 tt_title="I booked the 'official' site. Here's what the hotel said.",
 tt_hook="1 phone call to the hotel shows whether your booking is real. Here's the walkthrough.",
 tt_extra=[
  ("Pause", "Pause. You booked from an ad and got a confirmation number. What's the one thing you do next?",
   "Pause: what next?", "a full-screen countdown card"),
  ("Example 2", "Call the hotel on the number from its own website and read them the confirmation number. If they can't "
                "find it, call your card company the same day and dispute the charge.", "Call the hotel. Then your card.",
   "a phone and a credit card"),
 ]),
S(week=30, pillar=P_TRAVEL, look="face cam", tt_look="illustrated",
 title="Road trip this summer? 1 tug at the gas pump that spots a skimmer",
 hook="1 tug on the card reader before you pay at the pump can spot a skimmer.",
 thumb="Tug the reader",
 hashtags=["roadtrip", "summertravel", "skimmer", "gasstation", "scamalert", "scamdecoded"],
 description="How gas pump skimmers work, and four habits that protect your card on a road trip.",
 caption="Skimmers hidden in gas pumps copy your card. A quick check, tap to pay, and card alerts go a long way.",
 sources=[FTC_SKIM, FBI_SKIM],
 claims=["Skimmers can be hidden inside or on gas pumps (FTC, FBI)",
         "Using a credit card rather than a debit card limits what you can lose (FTC)"],
 short=[
  ("Hook", "One tug on the card reader before you pay at the pump. Here's why.",
   "Tug the card reader", "Dhruv at a gas pump, filmed on his phone"),
  ("The skimmer", "Skimmers copy your card at the pump. Some sit on top of the reader, some are hidden inside, behind "
                  "a broken seal.", "Skimmers hide in pumps", "a pump with an open panel"),
  ("The checks", "Wiggle the reader. Check the security tape on the panel. Pick a pump near the store, where staff can "
                 "see it.", "Wiggle · check the seal · pump near the door", "three pumps, one highlighted"),
  ("Pay smart", "Better still, tap to pay or pay inside. Use a credit card, not debit, and turn on card alerts.",
   "Tap, or pay inside. Credit, not debit.", f"{MASCOT} with a credit card"),
 ],
 tt_title="Gas pump skimmers: 4 road trip habits and the 1 that matters most",
 tt_hook="4 road trip habits protect your card at the pump, and 1 matters most.",
 tt_extra=[
  ("Pause", "Pause. Which do you think protects you most: checking the seal, tapping to pay, or using credit not debit?",
   "Pause: which matters most?", "a full-screen countdown card"),
  ("Answer", "Tapping to pay, because a tap doesn't share the data a skimmer copies. Credit over debit is next: if your "
             "card is copied, the money missing isn't from your checking account while the bank sorts it out.",
   "Tap first. Credit second.", "a phone tapping a reader"),
 ]),
]

# Extra "already happened?" beats that take the shorter TikTok cuts past 65 seconds.
_AFTER = {
 "A brace arrived that nobody ordered: 3 things to do today":
  ("Already gave it?", "Already gave your Medicare number to a caller? Call 1-800-MEDICARE, tell them what happened, and watch "
   "every statement for the next year. It's not your fault, and reporting it protects the next person.",
   "Gave the number? Call Medicare.", "a phone and a Medicare statement"),
 "I almost got hired by a scammer: the 3 messages that gave it away":
  ("Already deposited?", "Already deposited the check? Don't spend it and don't pay any vendor. Call your bank and tell them "
   "you think the check is fake, then report the 'employer' at report fraud dot f t c dot gov.",
   "Deposited it? Call your bank.", "a bank building with a phone"),
 "Quiz: which of these 3 scholarship offers is the scam?":
  ("Free help", "Want real help? Your school's financial aid office is free, the FAFSA is free, and real scholarship searches "
   "don't charge. If anyone asks for a fee to apply or to claim money, close the tab. And never give a bank account number "
   "to claim a scholarship you didn't apply for.", "Real help is free", "a school building with a help sign"),
 "Your first apartment listing has 4 red flags. Can you find them?":
  ("Already paid?", "Already paid a deposit? Call your bank or payment app the same day and ask them to stop or reverse it, "
   "then report the listing to the site.", "Paid? Call your bank today.", "a phone dialling"),
 "Dad's a veteran? 3 questions before anyone 'helps' with his pension":
  ("Already signed?", "Already signed something or moved money? Talk to a VA-accredited representative or a veterans service "
   "organization before anything else changes, and report the adviser to the VA inspector general. There's no fee to ask.",
   "Signed? Get free accredited help.", "a veteran shaking hands with a helper"),
 "Before Memorial Day: the veterans' charity call, line by line":
  ("Already pledged?", "Already pledged on the phone? A pledge isn't a payment. You don't owe anything you didn't agree to in "
   "writing. If you paid by card, call your card company and ask about a dispute. If you paid by gift card, call the card "
   "company right away.", "A pledge isn't a payment", "a phone with a checkmark"),
 "Romance scams by the numbers, and the 1 rule that beats them":
  ("The rule", "So here's the one rule. Never send money, gift cards or crypto to someone you haven't met in person, however "
   "long you've been talking and however real it feels. If a friend or parent is in one of these, start with kindness, not "
   "blame. Shame is what keeps people sending.", "Never send money to someone you haven't met",
   "two hands, one holding a phone"),
 "Quiz: which airline help number is real?":
  ("Already paid?", "Already paid a fake agent a rebooking fee? Call your card company the same day and dispute the charge, "
   "then check your real booking in the airline app. Your original flight may still be fine, and you may not have needed "
   "to change a thing.", "Paid a fake agent? Dispute it.", "a credit card with a phone"),
 "I booked the 'official' site. Here's what the hotel said.":
  ("Booking next time", "Next time, start from the hotel's own website, or a booking site you've used before and typed in "
   "yourself. Check the price matches, read the cancellation terms, and pay with a credit card, so a fake booking is a "
   "dispute and not a loss.", "Start from the hotel's own site", "a suitcase next to a laptop"),
 "Gas pump skimmers: 4 road trip habits and the 1 that matters most":
  ("Card alerts", "And turn on card alerts before you leave. If a skimmed card gets used, you'll see the charge in minutes, "
   "not at the end of the month, and you can lock the card from the app while you're still on the road.",
   "Turn on card alerts", "a phone with a bell"),
}
for _s in SHORTS:
    if _s["tt_title"] in _AFTER:
        _s["tt_extra"].append(_AFTER[_s["tt_title"]])
