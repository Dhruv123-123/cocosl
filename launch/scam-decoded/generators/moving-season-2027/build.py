"""Moving-season pack, Tue Jul 6 - Thu Aug 5 2027: rental listing scams and moving-company scams.

    python3 build.py   ->  ../../moving-season-2027.json and ../../POSTING_PLAN_MOVING_SEASON_2027.md

10 Shorts (Reels + YouTube Shorts) at 12:00 on Tuesdays and Thursdays and 2 carousels at 19:30 on Saturdays, after the
last planned week (weeks 31-34 end Sat Jul 3). Asked for by scouting (seasonal-demand-feb-jun-2027.md, PR #2): fake
listings, deposit-before-viewing and fake movers, citing the FTC's rental guidance, with the free "Renting safely"
checklist (/renting/) as the lead magnet. Weeks 22-34 already cover 'owner abroad, can't show it' (#16, May 21), the
moving long video (#43, Apr 25) and county tax records (spring #7), so those angles don't repeat.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, MASCOT, seg  # noqa: E402

FTC_RENTAL = "https://consumer.ftc.gov/articles/rental-listing-scams"
FTC_SUMMER = "https://consumer.ftc.gov/consumer-alerts/2025/08/moving-summer-watch-rental-scams"
FTC_MOVERS = "https://consumer.ftc.gov/consumer-alerts/2024/09/avoid-scams-when-you-hire-moving-company"
FMCSA_FLAGS = "https://www.fmcsa.dot.gov/protect-your-move/red-flags"
FMCSA_MOVE = "https://www.fmcsa.dot.gov/protect-your-move"
FMCSA_BROKERS = "https://www.fmcsa.dot.gov/protect-your-move/movers-vs-brokers"
MAGNET = "Renting or moving this summer? Our free one-page checklist covers listings, deposits and movers (link in bio)."
CHECKER = "Not sure about a listing or a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends nothing anywhere."
P = "job, school and rental scams"
P_HOME = "home, car and small business scams"
SEASON = "Moving season 2027"


def slides(cover, items, save, cover_vis):
    out = [("Hook", "", cover, cover_vis)]
    out += [(str(i), n, o, v) for i, (n, o, v) in enumerate(items, 1)]
    out.append(("Save this", save, "Save it for your next move.", f"{MASCOT} carrying a moving box"))
    return out


POSTS = [
 dict(date="2027-07-06", kind="short", look="screen recording", pillar=P, topic="duplicate listings",
  title="Rental listing scam: 1 address search before you pay",
  hook="1 apartment, 2 listings, 2 different owners, and only 1 of them is real.",
  thumb="Same place. 2 owners?",
  hashtags=["rentalscam", "apartmenthunting", "moving", "renting", "scamdecoded"],
  description="Searching a listing's address to catch hijacked and fake rentals, from the FTC.",
  caption="Scammers copy real rental ads and post them under their own name. The FTC says search the address with the "
          "owner's or company's name: if the same place shows up under a different name, that's a sign of a scam.",
  sources=[FTC_RENTAL], claims=["FTC: search the address and the owner or company name; other ads under a different name are a sign of a scam",
                                "FTC: check whether the property is on the rental company's own website"],
  original_element="Screen recording of an address search: two listing cards for the same photo, with the two owner names circled.",
  segments=[
   ("Hook", "Found the perfect place? Before you send a cent, paste the address into a search. Here's what a fake one "
            "looks like.", "Paste the address first", "a listing with a search bar over it"),
   ("The tell", "The same photos come up twice, with two different owner names. Scammers copy real ads and swap in "
                "their own contact details.", "Same photos, 2 owner names", "two identical listing cards"),
   ("Check more", "The FTC also says look for the place on the rental company's own website, and search the owner's "
                  "name with the word scam.", "Company site. Name + 'scam'.", "a magnifying glass over a name"),
   ("Do this", "Two names for one place? Walk away. Report the fake listing to the site, and at ReportFraud.ftc.gov.",
    "Two owners? Walk away", f"{MASCOT} walking past a for-rent sign"),
  ]),
 dict(date="2027-07-08", kind="short", look="face cam", pillar=P, topic="deposit before viewing",
  title="Rental deposit before a viewing? 1 rule: see it first",
  hook="1 landlord, 5 other applicants, and a deposit due today before you've seen the place.",
  thumb="Deposit before viewing? No.",
  hashtags=["rentalscam", "renting", "apartment", "moving", "scamdecoded"],
  description="Pressure to pay before you've seen a rental, from the FTC.",
  caption="'Five people want it, send the deposit today to hold it.' The FTC says scammers rush you into a quick "
          "decision, and the fix is to see the place in person, or on a live video tour, before you pay.",
  sources=[FTC_RENTAL, FTC_SUMMER], claims=["FTC: scammers may rush you into a quick decision; walk away if someone pushes you",
                                            "FTC: check out the listing in person if possible, or ask for a video or virtual tour"],
  original_element="Face-to-camera with the landlord's 'hold it today' text on a printed phone mockup.",
  segments=[
   ("Hook", "A landlord texts: five other people want it, send the deposit today and it's yours. You haven't even "
            "seen the inside.", "'5 others want it. Pay today.'", "a phone with an urgent text"),
   ("Why", "Rush is the whole trick. The FTC says scammers push you into a quick decision, before you've checked "
           "anything.", "The rush is the scam", "a stopwatch over a house"),
   ("The rule", "See it first. In person if you can. If you can't, a live video tour where they open the doors you "
                "ask them to.", "See it first. Live tour at least.", "a phone showing a live video of a kitchen"),
   ("Do this", "No viewing, no deposit. A real landlord will wait a day for a video call.", "No viewing, no deposit",
    f"{MASCOT} holding up a stop hand"),
  ]),
 dict(date="2027-07-10", kind="carousel", look="checklist", pillar=P, topic="renting checklist",
  title="Renting this summer? 6 checks before you pay anything",
  hook="6 checks that catch most fake rentals, in the order you'd do them.",
  thumb="6 checks before you pay",
  hashtags=["rentalscam", "renting", "apartmenthunting", "moving", "scamdecoded"],
  description="Six checks before you pay for a rental, from the FTC's rental listing advice.",
  caption="Six checks before any money leaves your hands, from the FTC's rental scam advice. " + MAGNET,
  sources=[FTC_RENTAL, FTC_SUMMER], claims=["FTC: search the address and owner name; check the rental company's site",
                                            "FTC: visit or get a video tour; walk away if rushed",
                                            "FTC: anyone who demands cash, wire, gift cards or crypto is a scammer",
                                            "FTC: ask the agent to confirm in writing any fees on top of rent"],
  original_element="Slide 7 is a tick-box version of the six checks, drawn to match the free checklist.",
  segments=slides("6 checks before you pay", [
   ("Search the address with the owner's name. Two names for one place is a red flag.", "1. Search address + owner",
    "a search bar over a house"),
   ("Find the place on the rental company's own website.", "2. Check the company's own site", "a laptop with a listing"),
   ("See it in person, or on a live video tour.", "3. See it, or a live tour", "a phone video of a living room"),
   ("Feeling rushed? That's the tell. Walk away.", "4. Rushed? Walk away", "a stopwatch with a cross"),
   ("Never pay by cash, wire, gift card or crypto. The FTC says anyone demanding those is a scammer.",
    "5. No cash, wire, gift card, crypto", "four payment icons crossed out"),
   ("Get every fee on top of rent confirmed in writing.", "6. Fees in writing", "a contract with a highlighted line"),
  ], "Get the free one-page checklist (link in bio).", "a clipboard with six ticks")),
 dict(date="2027-07-13", kind="short", look="illustrated", pillar=P, topic="cash-only landlords",
  title="Landlord wants cash or crypto only? 1 rule from the FTC",
  hook="1 landlord, 1 deposit, and 4 ways they'll accept it: cash, wire, gift card or crypto.",
  thumb="Cash or crypto only? Scam.",
  hashtags=["rentalscam", "renting", "cryptoscam", "moving", "scamdecoded"],
  description="Rental payment methods only scammers insist on, from the FTC's 2025 alert.",
  caption="The FTC is clear: anyone who demands you pay a rental deposit with cash, a wire transfer, gift cards or "
          "crypto is a scammer. Those payments are like sending cash, and they're hard to get back.",
  sources=[FTC_SUMMER], claims=["FTC: anyone who demands you pay by cash, gift cards, crypto or wire transfer is a scammer",
                                "FTC: wiring money, gift cards or crypto is like sending cash; it's hard to get back"],
  original_element="Illustrated: four payment icons sliding into a drain, then a card with a 'dispute' button.",
  segments=[
   ("Hook", "The deposit's due, and the landlord has rules: cash only. Or a wire. Or gift cards. Or crypto, if that's "
            "easier for you.", "'Cash, wire, gift cards or crypto'", "a hand holding four payment icons"),
   ("The rule", "The FTC puts it in one line: anyone who demands you pay those ways is a scammer.",
    "FTC: demands these = scammer", "a stamp reading SCAM"),
   ("Why", "Each one is like handing over cash. Once it's sent, it's very hard to get back, and that's exactly why "
           "they want it.", "Like cash. Hard to get back.", "money flying away"),
   ("Do this", "Pay a real landlord by a method with a record, after you've seen the place and signed a lease.",
    "Seen it, signed it, then pay", f"{MASCOT} signing a lease"),
  ]),
 dict(date="2027-07-15", kind="short", look="walkthrough", pillar=P, topic="hidden rental fees",
  title="Rental 'fees' in the fine print: 1 question to ask first",
  hook="1 listing says $1,400 a month, and 3 fees are hiding in a footnote.",
  thumb="$1,400? Ask what else.",
  hashtags=["renting", "apartmenthunting", "junkfees", "moving", "scamdecoded"],
  description="Hidden mandatory rental fees, and getting them in writing, from the FTC's 2025 alert.",
  caption="The FTC says some listings bury mandatory fees in footnotes, links or fine print. Ask whether the advertised "
          "rent includes all mandatory monthly fees, and get any extra fees confirmed in writing.",
  sources=[FTC_SUMMER], claims=["FTC: some listings bury fees in footnotes, hyperlinks or fine print",
                                "FTC: ask whether the advertised price includes all mandatory monthly fees",
                                "FTC: ask the agent to confirm in writing any fees on top of rent"],
  original_element="Phone walkthrough of a listing: scroll to the footnote, circle the three fees, add them to the headline rent.",
  segments=[
   ("Hook", "Fourteen hundred a month, says the listing. Scroll down to a tiny star, and there's a tech fee, an amenity "
            "fee and a trash fee.", "$1,400... plus 3 tiny fees", "a listing with a footnote star"),
   ("The FTC", "The FTC says some listings bury fees in footnotes, links or fine print, so the real monthly cost is "
               "higher than the headline.", "Fees hide in the fine print", "a magnifying glass on small text"),
   ("Ask this", "One question: does this price include every mandatory monthly fee? Then ask for any extras in "
                "writing.", "Ask: is every fee included?", "a speech bubble with a question"),
   ("Do this", "Add the fees to the rent before you compare places. In writing, or it doesn't count.",
    "Fees in writing, or no deal", f"{MASCOT} with a calculator"),
  ]),
 dict(date="2027-07-20", kind="short", look="data chart", pillar=P, topic="people working with the owner",
  title="Rental 'assistant' wants your SSN? 1 rule before you send it",
  hook="1 'property assistant' says the owner needs 3 things today: your SSN, a pay stub and a bank login.",
  thumb="An 'assistant' wants your SSN",
  hashtags=["rentalscam", "identitytheft", "renting", "moving", "scamdecoded"],
  description="Not giving personal details to someone claiming to work with the owner, from the FTC.",
  caption="Someone says they work with the owner and needs your personal and financial details to 'process' you. "
          "The FTC says don't give them out. Contact the owner or company yourself, using information you already have.",
  sources=[FTC_RENTAL], claims=["FTC: don't give personal or financial information to someone claiming to work with the owner",
                                "FTC: contact the owner or company using information you already have"],
  original_element="A data-chart beat: what a real application asks for vs what this 'assistant' asked for, as two short lists.",
  segments=[
   ("Hook", "The owner's assistant emails: to hold the place, send your Social Security number, a pay stub and your "
            "bank login, today.", "SSN, pay stub, bank login. Today.", "an email with three attachments requested"),
   ("The rule", "The FTC says don't give personal or financial details to someone who says they work with the owner.",
    "FTC: don't send it to 'the assistant'", "a hand stopping a document"),
   ("The check", "Reach the owner or the rental company yourself, on contact details you found, not the ones in the "
                 "email. And never send a bank login to anyone.", "Contact the owner yourself", "a phone dialing a known number"),
   ("Do this", "Already sent it? Freeze your credit, free, at all three bureaus, and change that bank password now.",
    "Sent it? Freeze credit. Change passwords.", f"{MASCOT} locking a padlock"),
  ]),
 dict(date="2027-07-22", kind="short", look="quiz pause", pillar=P_HOME, topic="phone estimates",
  title="Moving company scam: 1 estimate you should never accept",
  hook="1 mover quotes your whole 3-bedroom move by phone in 5 minutes, sight unseen.",
  thumb="Quote by phone? Pause.",
  hashtags=["movingscam", "movingday", "moving", "movers", "scamdecoded"],
  description="Estimates without an inspection, and written estimates, from FMCSA and the FTC.",
  caption="FMCSA's first red flag: a mover or broker who quotes by phone or online without seeing your things, or "
          "won't give a written estimate. The FTC says get written estimates from several movers that list all your "
          "property.",
  sources=[FMCSA_FLAGS, FTC_MOVERS], claims=["FMCSA: red flag when a mover or broker doesn't do an on-site inspection and quotes by phone or online",
                                             "FMCSA: red flag when they won't give a written estimate or say they'll set the cost after loading",
                                             "FTC: get written estimates from several movers; estimates should list all your property"],
  original_element="Quiz pause: 'Which quote do you trust?' with three quotes on screen, held two seconds before the answer.",
  segments=[
   ("Hook", "Three movers. One quotes by phone in five minutes. One wants to see the place. One says we'll know the "
            "price after we load. Pause. Which one?", "Pause: which quote do you trust?", "three quote cards"),
   ("Answer", "The one that looks first. FMCSA's top red flag is a quote by phone or online, without anyone seeing "
              "your things.", "The one that looks first", "a mover with a clipboard in a living room"),
   ("And", "'We'll set the price after loading' is another red flag. By then your things are on their truck.",
    "'Price after loading' = red flag", "a truck with a question mark"),
   ("Do this", "Get written estimates from several movers that list everything you own, then compare.",
    "Several written estimates. Compare.", f"{MASCOT} comparing papers"),
  ]),
 dict(date="2027-07-24", kind="carousel", look="data", pillar=P_HOME, topic="mover red flags",
  title="11 red flags of a rogue mover, from FMCSA",
  hook="11 red flags the federal moving regulator lists, and the 3 that show up first.",
  thumb="11 mover red flags",
  hashtags=["movingscam", "movers", "movingday", "moving", "scamdecoded"],
  description="FMCSA's red flags for dishonest movers, grouped by when you'll see them.",
  caption="The Federal Motor Carrier Safety Administration lists 11 red flags for dishonest movers. Here they are, "
          "grouped by when you'll see them: the quote, the paperwork and moving day. " + MAGNET,
  sources=[FMCSA_FLAGS, FMCSA_MOVE], claims=["FMCSA lists 11 red flags (no on-site inspection, no written estimate, cash or large deposit, blank documents, no booklet, no local address, 'all covered by our insurance', generic phone greeting, poor or no offices, rental truck, 'more belongings than estimated')",
                                             "FMCSA: interstate movers must give the 'Your Rights and Responsibilities When You Move' booklet"],
  original_element="Slide 2 is a timeline chart: the 11 flags placed at quote, paperwork and moving day.",
  segments=slides("11 red flags, by stage", [
   ("At the quote: no one looks at your things, no written estimate, or 'we'll price it after loading'.",
    "Quote: no look, nothing in writing", "a phone quote bubble"),
   ("At the quote: they want cash or a large deposit before the move.", "Quote: cash or a big deposit",
    "a stack of cash with a lock"),
   ("Paperwork: they ask you to sign blank documents, or don't give you the federal 'rights and responsibilities' "
    "booklet.", "Paperwork: blanks, no booklet", "a blank form with a pen"),
   ("Checking them out: no local address on the website, the phone answered just 'Movers', offices that don't exist.",
    "Check: no address, no name", "a website with an empty address box"),
   ("Checking them out: 'everything's covered by our insurance'.", "'All covered by our insurance'",
    "an umbrella with holes"),
   ("Moving day: a rental truck shows up instead of a marked one, or suddenly you have 'more stuff than estimated'.",
    "Moving day: rental truck, 'more stuff'", "a plain rental truck"),
  ], "Report problems with an interstate mover to FMCSA, and scams at ReportFraud.ftc.gov.", "a timeline with flags")),
 dict(date="2027-07-27", kind="short", look="myth vs fact", pillar=P_HOME, topic="mover registration",
  title="Moving out of state? 1 registration your mover must have",
  hook="1 interstate move, 1 friendly mover, and 0 federal registration.",
  thumb="Registered? Check first.",
  hashtags=["movingscam", "moving", "movers", "outofstate", "scamdecoded"],
  description="Checking an interstate mover's US DOT registration, from the FTC and FMCSA.",
  caption="Movers that cross state lines must be registered with the US Department of Transportation. The FTC says "
          "look them up, and FMCSA's mover search shows registration and complaint history. Brokers must be "
          "registered too, and say they arrange moves rather than haul them.",
  sources=[FTC_MOVERS, FMCSA_BROKERS], claims=["FTC: movers crossing state lines must be registered with the US DOT",
                                               "FMCSA: brokers don't own trucks, act as middlemen, and must be registered with FMCSA",
                                               "FMCSA: its search tool shows a broker's or mover's registration and complaint history"],
  original_element="Myth vs fact cards, then the FMCSA mover search page as a still.",
  segments=[
   ("Hook", "Myth: a mover with a nice website and good reviews must be legit for a move across state lines.",
    "Myth: nice website = legit", "a slick moving website"),
   ("Fact", "The FTC says movers that cross state lines must be registered with the US Department of Transportation. "
            "Look them up first.", "Fact: interstate = DOT registered", "a badge with a DOT label"),
   ("Brokers", "Some companies are brokers, not movers. They don't own trucks. They have to be registered too, and say "
               "they arrange moves.", "Broker? Must say so. Registered too.", "a middleman between a house and a truck"),
   ("Do this", "Search the company in FMCSA's mover search before you sign. It shows registration and complaint "
               "history.", "Search FMCSA before you sign", f"{MASCOT} searching on a laptop"),
  ]),
 dict(date="2027-07-29", kind="short", look="walkthrough", pillar=P_HOME, topic="blank moving documents",
  title="Moving day paperwork: 1 thing never to sign",
  hook="1 clipboard, 3 blank lines where the price should be, and a mover saying just sign here.",
  thumb="Blank lines? Don't sign.",
  hashtags=["movingscam", "movingday", "moving", "movers", "scamdecoded"],
  description="Never signing moving documents with blank spaces, from the FTC and FMCSA.",
  caption="The FTC says say no to paperwork with blank spaces where prices, dates or signatures should be. FMCSA lists "
          "asking you to sign blank documents as a red flag.",
  sources=[FTC_MOVERS, FMCSA_FLAGS], claims=["FTC: say no to paperwork with blank spaces where prices, dates or signatures should be",
                                             "FMCSA: a mover asking you to sign blank documents is a red flag"],
  original_element="Walkthrough of a mock bill of lading: the blank price and date fields circled, then filled in.",
  segments=[
   ("Hook", "The truck's loaded, everyone's tired, and the mover hands you a clipboard. Just sign here, we'll fill in "
            "the rest later.", "'Sign here. We'll fill it in.'", "a clipboard held out"),
   ("The rule", "The FTC says say no to paperwork with blank spaces where prices, dates or signatures should be. FMCSA "
                "calls it a red flag.", "Blank spaces? Say no.", "a form with blank lines circled"),
   ("Why", "A blank price can become any price once your things are on their truck.", "A blank price = any price",
    "a price tag with a question mark"),
   ("Do this", "Read it, fill every blank or cross it out, and keep a copy before the truck leaves.",
    "Fill every blank. Keep a copy.", f"{MASCOT} holding a signed copy"),
  ]),
 dict(date="2027-08-03", kind="short", look="illustrated", pillar=P_HOME, topic="moving deposits",
  title="Moving company wants a big cash deposit? 1 red flag",
  hook="1 mover, a 50% deposit, and they'd prefer cash, today, to lock the date.",
  thumb="Big cash deposit? Red flag.",
  hashtags=["movingscam", "moving", "movers", "movingday", "scamdecoded"],
  description="Cash and large deposits before a move, from FMCSA and the FTC.",
  caption="FMCSA and the FTC both list it: a mover who demands cash or a big deposit before the move. Once they have "
          "the money, there's little reason to show up, or to deliver at the price they quoted.",
  sources=[FMCSA_FLAGS, FTC_MOVERS], claims=["FMCSA: red flag when a mover demands cash or a large deposit before the move",
                                             "FTC: say no to anyone who demands cash or a big deposit before the move"],
  original_element="Illustrated: a calendar date 'locked' with a padlock made of cash, then the padlock opening.",
  segments=[
   ("Hook", "Summer dates are filling up, says the mover. Half up front, cash is best, today, or we can't hold your "
            "Saturday.", "'50% up front. Cash. Today.'", "a calendar with a cash padlock"),
   ("The flag", "FMCSA and the FTC both list it: a mover who demands cash or a large deposit before the move.",
    "FMCSA + FTC: cash or big deposit", "a red flag on a moving box"),
   ("Why", "Once they have your money, there's not much reason to show up, or to stick to the price they quoted.",
    "Paid up front = no leverage", "a truck driving away empty"),
   ("Do this", "Pick a mover that doesn't need a big deposit, and pay by card, so you can dispute it if needed.",
    "No big deposit. Pay by card.", f"{MASCOT} holding a card"),
  ]),
 dict(date="2027-08-05", kind="short", look="face cam", pillar=P_HOME, topic="moving day surprises",
  title="'You have more stuff than we estimated': 1 moving day flag",
  hook="1 loaded truck, 1 new price: double the estimate, because you have more stuff.",
  thumb="Price doubled? Red flag.",
  hashtags=["movingscam", "movingday", "moving", "movers", "scamdecoded"],
  description="Moving-day price changes and the booklet you should get, from FMCSA.",
  caption="FMCSA lists it as a red flag: the mover claims you have more belongings than estimated. Interstate movers "
          "also have to give you the 'Your Rights and Responsibilities When You Move' booklet. Read it before moving day.",
  sources=[FMCSA_FLAGS, FMCSA_MOVE], claims=["FMCSA: red flag when the mover claims you have more belongings than estimated",
                                             "FMCSA: movers must give the 'Your Rights and Responsibilities When You Move' booklet before an interstate move",
                                             "FMCSA does not resolve claims against moving companies; it takes complaints"],
  original_element="Face-to-camera next to a stack of real moving boxes, holding up a printed estimate.",
  segments=[
   ("Hook", "Everything's on the truck. Then the foreman says: you have way more stuff than we estimated. The price "
            "just doubled.", "'More stuff. Price doubled.'", "a foreman with a clipboard by a full truck"),
   ("The flag", "FMCSA lists exactly this as a red flag: the mover claims you have more belongings than estimated.",
    "FMCSA: a listed red flag", "a red flag on a truck"),
   ("Your rights", "For a move across state lines, the mover must give you a booklet called Your Rights and "
                   "Responsibilities When You Move. Read it before moving day.", "Get the rights booklet", "a booklet on a box"),
   ("Do this", "Get a written estimate that lists everything first. Problems with an interstate mover? File a complaint "
               "with FMCSA.", "Written estimate first. Complain to FMCSA.", f"{MASCOT} filing a form"),
  ]),
]


def item(p):
    fmt = "carousel" if p["kind"] == "carousel" else "short"
    time = "19:30" if fmt == "carousel" else "12:00"
    platforms = {"short": ["instagram", "youtube"], "carousel": ["instagram"]}[fmt]
    tail = "" if MAGNET in p["caption"] else "\n\n" + MAGNET
    return {"format": fmt, "pillar": p["pillar"], "platforms": platforms, "post_on": f"{p['date']} {time}",
            "topic": p["topic"], "look": p["look"], "original_element": p["original_element"],
            "idea_angle": f"{SEASON}: {p['topic']}. {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": [seg(*r) for r in p["segments"]], "cta": CTA,
                       "caption": p["caption"] + tail + "\n\n" + CHECKER + "\n\n" + CTA, "hashtags": p["hashtags"],
                       "description": p["description"], "thumbnail_text": p["thumb"], "sources": p["sources"],
                       "claims_to_verify": p["claims"]}}


def plan(items):
    rows = ["# Scam Decoded: moving-season pack, Tue Jul 6 – Thu Aug 5 2027", "",
            "10 Shorts (Reels + YouTube Shorts) at 12:00 on Tuesdays and Thursdays, and 2 Instagram carousels at 19:30 on "
            "Saturdays, America/New_York, after the last planned week (weeks 31–34 end Sat Jul 3). Nothing has been "
            "posted; Dhruv posts each by hand.", "",
            "Rentals first (fake and copied listings, deposit before viewing, cash-only landlords, hidden fees, "
            "'assistants' who want your SSN), then movers (phone quotes, registration, blank paperwork, big deposits, "
            "moving-day price jumps). Every caption points to the free **Renting safely** checklist at /renting/ "
            "(sites/scam-decoded/lead-magnet/renting-safely-checklist.html).", "",
            "| # | Date | Time | Where | Format | Look | Topic | Title |", "|---|---|---|---|---|---|---|---|"]
    for n, (p, i) in enumerate(zip(POSTS, items)):
        d = dt.date.fromisoformat(p["date"])
        where = {"short": "Reels + Shorts", "carousel": "Instagram"}[i["format"]]
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} | {i['post_on'][11:]} | {where} | {i['format'].capitalize()} | "
                    f"{p['look']} | {p['topic']} | {p['title']} |")
    rows += ["", "Sources: FTC rental and moving pages and FMCSA's Protect Your Move pages, listed in each item's "
             "`sources`. Check every `claims_to_verify` line the week it posts."]
    return "\n".join(rows) + "\n"


def main():
    items = [item(p) for p in POSTS]
    root = HERE.parent.parent
    videos = [i for i in items if i["format"] == "short"]
    assert all(a["look"] != b["look"] for a, b in zip(videos, videos[1:]))
    for i in items:
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        if i["format"] == "short":
            assert 60 <= w <= 120, (i["script"]["title"], w)
            assert len(i["script"]["title"]) <= 60, i["script"]["title"]
        assert len(i["script"]["hashtags"]) <= 5
        for s in i["script"]["segments"]:
            assert len(s["on_screen_text"].split()) <= 12, s["on_screen_text"]
        assert any(ch.isdigit() for ch in i["script"]["hook"].split(".")[0][:60]), i["script"]["hook"]
        assert "guarantee" not in json.dumps(i).lower()
    (root / "moving-season-2027.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (root / "POSTING_PLAN_MOVING_SEASON_2027.md").write_text(plan(items))
    for n, i in enumerate(items):
        print(n, i["post_on"], i["format"], i["look"], sum(len(s["narration"].split()) for s in i["script"]["segments"]),
              len(i["script"]["title"]), i["script"]["title"])


if __name__ == "__main__":
    main()
