"""4 YouTube long videos for weeks 27-30, each with an original_element (ORIGINALITY_PASS.md rule 3)."""
from sources import *
from common import P_FAMILY
from shorts import P_HEALTH, P_JOBS, P_TRAVEL


def L(**k):
    return k


LONG = [
L(week=27, pillar=P_HEALTH,
 title="Medicare fraud: free tests, free braces, and the card thieves want",
 title_variants=["Medicare scams explained: what to say when they call", "Your Medicare number is worth stealing. Here's why."],
 hook="5 Medicare scams target your parents' Medicare number. Here's each one, and how to read the statement that catches them.",
 thumb="Medicare scams: 5 to know",
 hashtags=["medicare", "medicarefraud", "seniors", "mothersday", "scamdecoded"],
 caption="Five Medicare scams, why your Medicare number is the prize, and how to read a Medicare statement to catch "
         "fraud early. Examples are fictional.",
 description_intro="Five Medicare scams, why your Medicare number is the prize, and how to spot fraud on a Medicare statement.",
 original_element="Dhruv walks through a Medicare Summary Notice sample (Medicare's own published example, on screen) "
                  "and circles where fake tests and equipment would show up; face cam intro and outro.",
 sources=[OIG_GENETIC, OIG_BRACE, FTC_DNA, MEDICARE_FRAUD, MEDICARE_4RS, FTC_HEALTH],
 claims=["Scammers offer free genetic tests and braces to get Medicare numbers (HHS-OIG)",
         "Medicare Summary Notices list services billed to your Medicare number (Medicare)",
         "Report suspected Medicare fraud to 1-800-MEDICARE (Medicare)"],
 segs=[
  ("Why your number", "Your Medicare number is worth more to a scammer than your credit card. A card gets cancelled in a "
   "day. A Medicare number can be billed for tests, equipment and services for months before anyone notices, and the "
   "person it belongs to is often the last to find out. So the scams on this list all have one goal: get the number. "
   "Here are five of them, and the one habit that catches all five."),
  ("Free genetic tests", "Scam one, the free genetic test. A caller, a table at a health fair, or someone at the door offers "
   "a cheek swab to check for cancer or heart risk, covered by Medicare. They need your Medicare number to send the kit. "
   "The test may never be read by anyone, but Medicare gets billed, and if your own doctor didn't order it and Medicare "
   "denies it, the bill can come back to you. The rule: only take a test your own doctor orders."),
  ("Free braces", "Scam two, the free brace. Do you have back pain, knee pain, shoulder pain? Medicare will cover a brace at "
   "no cost. Then a box arrives with equipment nobody needed, sometimes several. Medicare pays for it, and your number "
   "goes on a list that gets sold to the next scammer. Medicare and your doctor don't cold-call to sell equipment."),
  ("The new card call", "Scam three, the new card call. Medicare is issuing new cards, or your card has expired, just "
   "confirm your number. Medicare doesn't call you out of the blue for your number. If you need a replacement card, you "
   "get it through Medicare's own website or by calling 1-800-MEDICARE yourself."),
  ("Plan switch pressure", "Scam four is pressure to switch plans, especially during enrollment periods. A caller says you "
   "qualify for extra benefits, a grocery card or more money back, if you switch today and confirm your details. Some "
   "are aggressive salespeople, some are scammers. Either way, don't decide on a cold call. Compare plans yourself on "
   "Medicare's site or with your State Health Insurance Assistance Program, which is free."),
  ("Fake fraud department", "Scam five is the twist: someone calls from Medicare's fraud department, saying your number has "
   "been used in fraud and they need to verify it. They're the fraud. Real investigators don't need you to read your "
   "number to them."),
  ("Read the statement", "Now the habit that catches all five. Every few months, Medicare sends a Medicare Summary Notice, "
   "or you can see the same thing in your online account. It lists every service and supply billed to your number. Go "
   "down the list with your parent. Any test you didn't have, any equipment that never came, any doctor you've never "
   "seen, is a red flag. It takes ten minutes, and it's the only way most people ever find out."),
  ("If you spot fraud", "If you spot something, call 1-800-MEDICARE and report it, or report it to the inspector general's "
   "hotline. Keep the statement. And remember the rule for every one of these calls: never give your Medicare number to "
   "anyone who contacted you. Your doctor already has it. Nobody else needs it on the phone."),
 ]),
L(week=28, pillar=P_JOBS,
 title="Graduates' guide: fake jobs, fake landlords and scholarship scams",
 title_variants=["Just graduated? 6 scams aimed right at you", "The new grad scam guide"],
 hook="6 scams target new graduates in their first summer. Here's each one, and a 10-minute setup before the first paycheck.",
 thumb="New grad scam guide",
 hashtags=["newgrad", "classof2027", "jobsearch", "firstapartment", "scamdecoded"],
 caption="Fake recruiters, fake landlords, scholarship fees and the first-paycheck setup that protects you. "
         "Examples are fictional.",
 description_intro="Six scams aimed at new graduates, and a 10-minute setup that protects your money before your first paycheck.",
 original_element="Screen recording: Dhruv checks a (real, public) company's careers page and a recruiter's email domain, "
                  "then reverse-searches a listing photo; plus the w5-job walkthrough clip.",
 sources=[FTC_JOB_TEXT, FTC_TELEGRAM, FTC_SSN_WA, FTC_CHECKS, FTC_SCHOLAR, FTC_RENTAL, FTC_RENTAL_DATA, FTC_STUDENT_JOBS],
 claims=["Scammers interview over chat apps and send fake checks (FTC)", "You don't pay to apply for scholarships or the FAFSA (FTC)",
         "People have reported $65 million in losses to rental scams (FTC Data Spotlight, Dec 2025)"],
 segs=[
  ("Why grads", "Your first summer after graduation is a scammer's favourite season. You're applying for jobs, looking for "
   "an apartment, and handling money on your own, often for the first time. Scammers know exactly what you're searching "
   "for. Here are six scams aimed right at you, and a ten-minute setup that protects you."),
  ("The chat interview", "Scam one, the chat-app interview. A recruiter finds you, the interview happens entirely by text on "
   "Telegram, WhatsApp or Signal, and you're hired within hours. Real employers interview on video or in person. Look the "
   "company up yourself, and email the recruiter at the company's real domain."),
  ("The equipment check", "Scam two follows straight on: the equipment check. Your new employer sends a check to buy a "
   "laptop from their approved vendor. You deposit it, pay the vendor, and days later the check bounces. The bank takes "
   "the money back. What you sent the vendor is gone. Real employers never send you money to buy their equipment."),
  ("Onboarding identity theft", "Scam three, early paperwork. They want your Social Security number, a photo of your "
   "license and your bank details for direct deposit before you've seen an offer letter or met anyone. That's identity "
   "theft. Real onboarding comes after a real offer, through a real HR system."),
  ("Scholarship fees", "Scam four, scholarship and aid fees. You've won a scholarship you never applied for, just pay a "
   "processing fee. Or a service charges to file your FAFSA. Real scholarships don't charge, and the FAFSA is free. Your "
   "school's financial aid office will help for nothing."),
  ("The apartment", "Scam five, the apartment that can't be shown. Great rent, copied photos, a landlord who's out of the "
   "country, and a deposit by payment app to hold it. People have reported sixty-five million dollars lost to rental scams. "
   "Never pay before you, or someone you trust, has been inside."),
  ("Pay to play", "Scam six, paying to get hired. Training fees, starter kits, certification you must buy from them. If "
   "you pay to get the job, it isn't a job."),
  ("Your 10-minute setup", "Now the setup. Freeze your credit at Equifax, Experian and TransUnion. It's free. Turn on alerts "
   "for every bank and card transaction. Put a strong, unique password and two-step sign-in on your email. And make one "
   "rule: you never pay to get a job, an apartment or a scholarship. That rule alone beats most of this list."),
 ]),
L(week=29, pillar=P_FAMILY,
 title="Veterans' benefit scams and fake military charities: what to know before Memorial Day",
 title_variants=["Pension poaching, fake charities and fake soldiers", "Scams that target veterans and military families"],
 hook="4 scams target veterans and the people who want to help them. Here's each one, and who to trust for free help.",
 thumb="Veteran scams: 4 to know",
 hashtags=["veterans", "memorialday", "militaryfamily", "vapension", "scamdecoded"],
 caption="Pension poaching, fake veterans' charities, impostor 'VA' calls and fake soldier profiles, and where veterans "
         "get free, accredited help. Examples are fictional.",
 description_intro="Four scams aimed at veterans and military families, and where to get free, accredited help with VA benefits.",
 original_element="Screen recording of VA's accreditation search (search a common surname, no personal data) and a "
                  "charity watchdog lookup; the quiz carousel from week 29 as a mid-video pause.",
 sources=[VA_POACH, VAOIG_POACH, VA_NEWS_POACH, VA_REP, VA_ACCRED, FTC_VET_CHARITY, FTC_MIL_ROMANCE, ARMY_ROMANCE],
 claims=["Pension poachers charge fees and sell products that can affect eligibility (VA)",
         "VA-accredited representatives help with claims for free (VA)",
         "Romance scammers impersonate service members (Army CID; FTC)"],
 segs=[
  ("Why veterans", "Veterans and military families are targeted for the same reasons they're respected: steady benefits, "
   "a strong sense of duty, and a public that wants to help. Scammers use all three. Here are four scams to know before "
   "Memorial Day, and where to get real help for free."),
  ("Pension poaching", "Scam one, pension poaching. It often starts with a free lunch seminar or a friendly adviser who "
   "promises to get an older veteran, or a surviving spouse, a bigger VA pension fast. Then come fees to fill in forms, "
   "and advice to move savings into annuities or trusts. Moving assets can tie up money the family needs and can affect "
   "eligibility for other help, like Medicaid. VA warns about exactly this."),
  ("Free help", "The answer is simple. Help applying for VA benefits is available for free from VA-accredited "
   "representatives, including veterans service organizations. Anyone can check a helper's name on VA's accreditation "
   "search. If they're not listed, or they're charging to file a first claim, or selling an investment, walk away."),
  ("Impostor VA calls", "Scam two, the impostor VA call. Your benefits are on hold, or you're owed back pay, just confirm "
   "your Social Security number and bank account. VA doesn't call to ask for that. Hang up and contact VA on the number "
   "from its own website."),
  ("Fake charities", "Scam three, the fake veterans' charity. Calls spike before Memorial Day and Veterans Day. The name "
   "sounds like a big, real charity. The caller wants a pledge tonight, sometimes by gift card. Look the charity up "
   "yourself, check it with a watchdog, and give on its own site. Ask how much reaches veterans; a real charity can tell you."),
  ("Fake soldiers", "Scam four aims at everyone else: the fake soldier. Stolen photos of a real service member, a profile on "
   "a dating app, a deployment that means no video calls, and then a need for money: leave, a flight home, a package fee. "
   "Real service members don't pay for their leave. Never send money to someone you haven't met."),
  ("Your checklist", "Your checklist. One, VA help is free from accredited representatives. Two, never move savings because "
   "someone promised more pension. Three, VA won't call for your numbers. Four, check a charity before you give. Five, "
   "never send money to an online love interest you haven't met."),
  ("If it happened", "If a veteran in your family already paid a pension poacher or gave out their details, contact VA, "
   "report it to the VA inspector general, and report it to the FTC at report fraud dot f t c dot gov. And thank you, to "
   "everyone who served, and everyone who looks out for them."),
 ]),
L(week=30, pillar=P_TRAVEL,
 title="The summer travel scam guide: flights, bookings, rentals and road trips",
 title_variants=["5 travel scams to know before summer", "Before you book summer travel, watch this"],
 hook="5 travel scams peak in June. Here's each one, from the fake airline text to the gas pump skimmer.",
 thumb="Summer travel scams",
 hashtags=["summertravel", "vacation", "travelscam", "roadtrip", "scamdecoded"],
 caption="Fake flight cancellation texts, lookalike booking sites, fake vacation rentals, skimmers and the safe way to "
         "book. Examples are fictional.",
 description_intro="Five summer travel scams, and the booking and payment habits that beat them.",
 original_element="Dhruv films a real gas pump check (wiggling the reader, checking the seal) and screen-records finding an "
                  "airline's real help number in its app; plus a rental listing reverse image search.",
 sources=[FTC_AIRLINE, FTC_TRAVEL, FTC_TRAVEL_2026, FTC_RENTAL, FTC_SKIM, FBI_SKIM],
 claims=["Scammers pose as airline customer service (FTC)", "Lookalike booking sites and fake rentals target travelers (FTC)",
         "Skimmers can be hidden on gas pumps (FTC, FBI)"],
 segs=[
  ("Why summer", "Summer travel means booking under pressure, delays you can't control, and lots of card payments on the "
   "road. That's the perfect setup for five scams. Here's each one, and the habits that beat all of them."),
  ("Flight canceled texts", "Scam one, the canceled flight text. Your flight has been canceled, call this number to rebook. "
   "The agent charges a rebooking fee, takes your card, and your new ticket never appears. Scammers also buy search ads "
   "for airline help lines and reply to people complaining on social media. Get help only through the airline's app, or "
   "the number on your booking confirmation."),
  ("Lookalike booking sites", "Scam two, the lookalike booking site. A search ad that looks like the hotel's official site, "
   "with the same photos and a great price. You get a confirmation the hotel has never heard of, or fees that double the "
   "price. Type the hotel's address yourself, then call the hotel to confirm your booking."),
  ("Fake rentals", "Scam three, the vacation rental that doesn't exist. Photos copied from a real listing, a host who wants "
   "you off the platform to save on fees, and payment by wire or payment app. Search the photos and the address, keep every "
   "message and payment on the platform, and pay by credit card."),
  ("Skimmers", "Scam four, skimmers. At the gas pump or an ATM, a hidden device copies your card. Wiggle the reader, check "
   "the pump's security seal, choose pumps near the store, use ATMs inside banks, and best of all, tap to pay. Use a credit "
   "card, not debit, on the road."),
  ("Free trip offers", "Scam five, the free trip. You've won a cruise or a vacation, just pay taxes and port fees, or sit "
   "through a pitch. Real prizes don't make you pay to collect them."),
  ("Your checklist", "Your summer travel checklist. Type travel sites yourself. Read the web address before you pay. Pay by "
   "credit card. Stay on the booking platform. Get airline numbers from the app. Tap to pay at the pump. And turn on card "
   "alerts before you leave."),
  ("If it happened", "If you paid a fake agent or a fake host, call your card company the same day and dispute the charge, "
   "then report it to the FTC at report fraud dot f t c dot gov. Then go and enjoy your summer."),
 ]),
]
