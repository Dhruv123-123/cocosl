"""8 Instagram carousels for weeks 27-30. Weekly: one checklist carousel and one in a rotating format
(script, quiz, comparison, data)."""
from sources import *
from common import MASCOT, P_FAMILY
from shorts import P_HEALTH, P_JOBS, P_TRAVEL


def C(**k):
    return k


def slides(cover, items, save, cover_vis):
    out = [("Hook", "", cover, cover_vis)]
    out += [(str(i), n, o, v) for i, (n, o, v) in enumerate(items, 1)]
    out.append(("Save this", save, "Save it. Share it.", f"{MASCOT} giving a thumbs up"))
    return out


CAROUSELS = [
C(week=27, look="script", pillar=P_FAMILY, title="How to talk to Mom about scams, in 4 lines that don't sound like a lecture",
 hook="4 lines that start the scam talk with Mom, without a lecture.", thumb="The scam talk, minus the lecture",
 hashtags=["mothersday", "protectyourparents", "familysafety", "eldercare", "scamdecoded"],
 description="Four conversation openers for talking to a parent about scams.",
 caption="Mother's Day is a good day for the scam talk, if it doesn't feel like a lecture. Four openers that work.\n\n"
         "Want the whole plan? Our Protect Your Parents guide has the three-visit version (link in bio, our own product).",
 sources=[FTC_EMERG, FTC_AI_VOICE], claims=["Scammers can clone voices from short audio clips (FTC)"],
 segs=slides("The scam talk, minus the lecture", [
  ("Make it about you: 'I got the weirdest text pretending to be my bank. Have you had those?'", "1. Start with your story", "two coffee cups"),
  ("Make it about the scammers: 'They can copy voices now. Can we pick a family word so nobody can fake me?'", "2. Blame the scammers", "a phone with a sound wave"),
  ("Ask, don't tell: 'What would you do if someone called saying I was in jail?'", "3. Ask a question", "a speech bubble with a question mark"),
  ("Offer a backup, not a rule: 'If anything feels off, call me first. I'll never be annoyed.'", "4. Offer a backup", "a phone with a heart"),
 ], "Save this for Sunday, and share it with your siblings so you all say the same thing.", f"{MASCOT} holding flowers")),
C(week=27, look="checklist", pillar=P_FAMILY, title="A family safe word in 4 steps (set it up at Mother's Day lunch)",
 hook="4 steps, 5 minutes, and nobody can fake your voice to your mom.", thumb="Safe word: 4 steps",
 hashtags=["safeword", "mothersday", "aivoice", "grandparentscam", "scamdecoded"],
 description="How to set up a family safe word that stops voice-clone and grandparent scams.",
 caption="A family safe word beats a cloned voice. Set it up in 4 steps at lunch on Sunday.",
 sources=[FTC_AI_VOICE, FTC_EMERG], claims=["Scammers can clone voices from short audio clips (FTC)"],
 segs=slides("Safe word: 4 steps", [
  ("Pick a word or phrase only the family knows, that isn't on social media. Not a pet's name.", "1. Pick it together", "a family around a table"),
  ("Say it out loud, don't text or post it. Make sure the grandparents can remember it.", "2. Say it, don't text it", "a whisper bubble"),
  ("Agree the rule: anyone who calls in a panic asking for money has to say it.", "3. Agree the rule", "a phone with a lock"),
  ("No word? Hang up and call them back on the number you already have. Practise once.", "4. No word? Call back.", "a phone dialling"),
 ], "Save this and set yours up on Sunday.", f"{MASCOT} with a key")),
C(week=28, look="checklist", pillar=P_JOBS, title="5 signs a job offer isn't real (for new grads)",
 hook="5 signs a job offer isn't real, and every new grad should know them.", thumb="Fake job: 5 signs",
 hashtags=["newgrad", "jobsearch", "jobscam", "classof2027", "scamdecoded"],
 description="Five signs a job offer is a scam.",
 caption="Job hunting after graduation? 5 signs the offer is fake:\n1. You never applied\n2. Interview by text only\n"
         "3. Offer in hours\n4. They send you a check\n5. SSN or bank details before an offer letter",
 sources=[FTC_JOB_TEXT, FTC_TELEGRAM, FTC_SSN_WA, FTC_STUDENT_JOBS],
 claims=["Fake employers interview over chat apps and send fake checks (FTC)", "Don't send your SSN to an 'employer' on WhatsApp (FTC)"],
 segs=slides("Fake job: 5 signs", [
  ("They found you, for a job you never applied for, by text or social media.", "1. You never applied", "a phone with a surprise message"),
  ("The whole interview happens by text on a chat app. No video, no call.", "2. Text-only interview", "chat bubbles"),
  ("You're hired within hours, often for more pay than the job should offer.", "3. Hired in hours", "a clock with a dollar sign"),
  ("They send a check to buy equipment from 'their vendor'. It'll bounce.", "4. They send a check", "a check with a red flag"),
  ("They want your SSN or bank details before you've seen an offer letter.", "5. SSN before an offer", "a form with an SSN box"),
 ], "Save this for your job hunt, and send it to a friend who's graduating.", f"{MASCOT} in a graduation cap")),
C(week=28, look="comparison", pillar=P_JOBS, title="New grad money-safety checklist: 6 things to set up before your first paycheck",
 hook="6 money-safety moves before your first paycheck, and 4 of them are free.", thumb="First paycheck: 6 moves",
 hashtags=["newgrad", "firstjob", "moneytips", "identitytheft", "scamdecoded"],
 description="Six things new graduates should set up to protect their money and identity.",
 caption="Before the first paycheck lands: freeze your credit, turn on bank alerts, lock your email, and know the scams aimed at new grads.",
 sources=[FTC_STUDENT_JOBS, FTC_RENTAL, FTC_SCHOLAR],
 claims=["Credit freezes are free (FTC)", "Rental scammers ask for deposits before you see the place (FTC)"],
 segs=slides("First paycheck: 6 moves", [
  ("Freeze your credit at all three bureaus. It's free and stops new accounts in your name.", "1. Freeze your credit", "three padlocks"),
  ("Turn on alerts for every bank and card transaction.", "2. Turn on alerts", "a phone with a bell"),
  ("Lock your email with a unique password and its strongest sign-in option.", "3. Lock your email", "an envelope with a shield"),
  ("Use a password manager, starting with bank, email and phone accounts.", "4. Password manager", "a key ring"),
  ("Never pay a deposit on an apartment you haven't seen.", "5. See it before you pay", "a door with a key"),
  ("Never pay for a job, training or equipment to get hired.", "6. Never pay to get hired", "a briefcase with a stop sign"),
 ], "Save this for your first week at work.", f"{MASCOT} holding a diploma")),
C(week=29, look="quiz", pillar=P_FAMILY, title="Quiz: spot 3 red flags in this veterans' charity call",
 hook="3 red flags in 1 Memorial Day charity call. How many can you spot?", thumb="Find 3 red flags",
 hashtags=["memorialday", "veterans", "charityscam", "spotthescam", "scamdecoded"],
 description="A quiz on a fake veterans' charity call before Memorial Day.",
 caption="Quiz time. Read the call on slide 1 and count the red flags before you swipe. Example is fictional.",
 sources=[FTC_VET_CHARITY, FTC_CHARITY], claims=["Fake charities pressure you to give immediately and ask for gift cards or wires (FTC)"],
 segs=slides("Find 3 red flags", [
  ("'Hi, I'm calling for the Veterans Hope Relief Fund' (a made-up name). A name built to sound like a charity you know.", "1. A soundalike name", "a name tag with a question mark"),
  ("'We need your pledge before Memorial Day, so tonight if you can.' Rush.", "2. 'Tonight'", "a clock"),
  ("'You can pay with a gift card at any store.' No real charity asks for gift cards.", "3. Gift cards", "a gift card with a red flag"),
 ], "Look the charity up yourself and give on its own site. How many did you get?", f"{MASCOT} with a flag")),
C(week=29, look="comparison", pillar=P_FAMILY, title="VA benefits help: free accredited reps vs paid 'consultants'",
 hook="2 kinds of VA benefits help: 1 is free and accredited, 1 charges and may cost you more.", thumb="VA help: free vs paid",
 hashtags=["veterans", "vabenefits", "vapension", "militaryfamily", "scamdecoded"],
 description="How to tell accredited VA help from paid consultants who may be pension poachers.",
 caption="Need help with a VA claim? Free help comes from VA-accredited representatives, including veterans service "
         "organizations. Watch out for consultants who charge fees or sell investments.",
 sources=[VA_REP, VA_ACCRED, VA_POACH, FTC_VET_BENEFITS],
 claims=["VA-accredited representatives at veterans service organizations help with claims for free (VA)",
         "VA's accreditation search lists accredited representatives, agents and attorneys (VA)"],
 segs=slides("VA help: free vs paid", [
  ("Accredited representative: listed on VA's accreditation search. Free help from veterans service organizations.", "Accredited: on VA's list", "a list with a check"),
  ("Paid 'consultant': not on the list, charges to fill in forms, promises a bigger pension fast.", "Consultant: fees and promises", "a dollar sign on a form"),
  ("Accredited: helps you apply. Doesn't sell you anything.", "Accredited: no products", "an empty hand"),
  ("Consultant: sells annuities or trusts that move savings, which can affect other benefits.", "Consultant: moves your savings", "coins moving into a box"),
 ], "Save this for a veteran in your family. Check any helper's name on VA's accreditation search.", f"{MASCOT} saluting")),
C(week=30, look="checklist", pillar=P_TRAVEL, title="Before you book summer travel: 6 checks",
 hook="6 checks before you book a flight, hotel or rental this summer.", thumb="Before you book: 6 checks",
 hashtags=["summertravel", "vacation", "travelscam", "travelhacks", "scamdecoded"],
 description="Six checks before booking travel, to avoid lookalike sites and fake rentals.",
 caption="Booking summer travel? 6 checks before you pay. Most travel scams fail at check 1 or 2.",
 sources=[FTC_TRAVEL, FTC_TRAVEL_2026, FTC_AIRLINE, FTC_RENTAL],
 claims=["Scammers create lookalike travel sites and fake rentals (FTC)", "Paying by credit card gives dispute rights (FTC)"],
 segs=slides("Before you book: 6 checks", [
  ("Type the site yourself. Search ads can be lookalikes.", "1. Type the site", "an address bar"),
  ("Read the web address before you pay.", "2. Read the address", "a magnifying glass on a URL"),
  ("Search the rental's photos and address. Copied listings show up elsewhere.", "3. Search the photos", "a photo with a magnifier"),
  ("Pay by credit card, never wire, gift card or payment app to a host.", "4. Credit card only", "a credit card"),
  ("Keep messages and payment on the booking platform.", "5. Stay on the platform", "a chat bubble inside a box"),
  ("Save airline numbers from the app, not from texts or ads.", "6. Numbers from the app", "a phone with an airline app"),
 ], "Save this before you book, and share it with whoever's planning the trip.", f"{MASCOT} with a suitcase")),
C(week=30, look="data", pillar=P_TRAVEL, title="Road trip money safety: 5 habits for the pump, the ATM and the motel",
 hook="5 road trip habits that protect your cards at the pump, the ATM and the motel.", thumb="Road trip: 5 habits",
 hashtags=["roadtrip", "summertravel", "skimmer", "moneytips", "scamdecoded"],
 description="Five habits that protect your money on a road trip.",
 caption="Road trip season. 5 habits that keep skimmers and scammers out of your wallet.",
 sources=[FTC_SKIM, FBI_SKIM, FTC_TRAVEL],
 claims=["Skimmers can be hidden on gas pumps and ATMs (FTC, FBI)", "Credit cards limit your losses more than debit cards (FTC)"],
 segs=slides("Road trip: 5 habits", [
  ("Tap to pay at the pump, or pay inside.", "1. Tap or pay inside", "a phone tapping a reader"),
  ("Wiggle the card reader and check the pump's security seal.", "2. Wiggle and check", "a pump panel with tape"),
  ("Use ATMs inside banks, and cover your hand when you type the PIN.", "3. Bank ATMs, cover the PIN", "an ATM indoors"),
  ("Use a credit card, not debit, so a copied card doesn't drain checking.", "4. Credit, not debit", "two cards, one with a check"),
  ("Turn on card alerts before you leave, so you see every charge on the road.", "5. Card alerts on", "a phone with a bell"),
 ], "Save this for the trip, and share it with whoever's driving.", f"{MASCOT} in a car")),
]
