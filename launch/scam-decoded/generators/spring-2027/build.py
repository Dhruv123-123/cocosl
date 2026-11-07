"""Spring pack, Tue Mar 2 - Thu Apr 8 2027: March Madness betting apps, spring travel and rentals, the FAFSA window.

    python3 build.py   ->  ../../spring-2027.json and ../../POSTING_PLAN_SPRING_2027.md

11 Shorts (Reels + YouTube Shorts) at 12:00 on Tuesdays and Thursdays, which weeks 13-21, weeks 22-26, the tax pack
and the newsletter cuts leave free. Weeks 13-21 already cover 'VIP picks' groups, half-price rentals with a Zelle
deposit, student loan forgiveness fees and the spring break long video, so these take new angles from the FTC and BBB
pages cited on each post.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, MASCOT, seg  # noqa: E402

FTC_TRAVEL = "https://consumer.ftc.gov/articles/avoid-scams-when-you-travel"
FTC_RENTAL = "https://consumer.ftc.gov/articles/rental-listing-scams"
FTC_AID = "https://consumer.ftc.gov/articles/how-avoid-scholarship-and-financial-aid-scams"
BBB_BET = "https://www.bbb.org/article/scams/26620-bbb-scam-alert-betting-on-a-big-game-dont-fall-for-a-sports-betting-scam"
CHECKER = "Not sure about a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends nothing anywhere."
SEASON = "Spring 2027"
BET, TRAVEL, AID = "sports betting", "spring travel", "student aid"
# thread -> content pillar (the pillars other packs already use)
PILLAR = {BET: "sports betting scams", TRAVEL: "travel and on-the-road scams", AID: "job, school and rental scams"}

POSTS = [
 dict(date="2027-03-02", time="12:00", kind="short", look="illustrated", pillar=TRAVEL, topic="free trip fees",
  title="'You won a free cruise, pay $89 in taxes': 0 real prizes",
  hook="1 call says you won a free cruise for 2, and all you pay is $89 in port taxes.",
  thumb="Free trip? Then why pay?",
  hashtags=["travelscam", "springbreak", "freecruise", "scamalert", "scamdecoded"],
  description="Why a 'free' vacation that needs fees and taxes first is a scam, from the FTC.",
  caption="A call, email or ad says you won a free trip, and you just need to pay some fees and taxes first. The FTC "
          "says real companies don't charge for a free prize, and you shouldn't sign or pay until you know the terms.",
  sources=[FTC_TRAVEL], claims=["FTC: 'free' trip offers ask you to pay fees and taxes first",
                                "FTC: don't sign or pay until you know the terms, including cancellation and refunds"],
  original_element="Illustrated 'free' price tag that keeps growing as fees are added, ending on a $0 trip that cost $89.",
  segments=[
   ("Hook", "Congratulations, you've won a free cruise for two. There's just one thing: eighty-nine dollars in port taxes, "
            "today, by card.", "Free cruise... plus $89 today", "a cruise ship with a price tag"),
   ("The catch", "The FTC says these offers always need fees and taxes paid first. A real prize doesn't cost you money "
                 "to claim.", "A real prize costs $0 to claim", "a gift box with a card reader"),
   ("What follows", "Pay once, and the card number is theirs. Often there's no trip at all, or a dates-never-available "
                    "voucher.", "Often no trip at all", "an empty calendar"),
   ("Do this", "Don't sign or pay until you've read the full terms, including cancellations and refunds. If they won't "
               "send them, hang up.", "No terms in writing? Hang up", f"{MASCOT} hanging up a phone"),
  ]),
 dict(date="2027-03-09", time="12:00", kind="short", look="face cam", pillar=AID, topic="paid FAFSA help",
  title="'We'll file your FAFSA for $79': it's free, always",
  hook="1 email offers to file your FAFSA for $79, before the state deadline.",
  thumb="FAFSA costs $0",
  hashtags=["fafsa", "financialaid", "college", "studentaid", "scamdecoded"],
  description="The FAFSA is always free to fill out and submit, says the FTC.",
  caption="A company offers to fill out and file your FAFSA for a fee. The FTC says the FAFSA is always free to fill out "
          "and submit, at studentaid.gov, and you should never pay anyone to fill it out or process it.",
  sources=[FTC_AID], claims=["FTC: the FAFSA is always free to fill out and submit",
                             "FTC: never pay anyone to fill out or process your FAFSA",
                             "FTC links to the FAFSA at studentaid.gov"],
  original_element="Face-to-camera explainer holding up a printed FAFSA price tag reading $0.",
  segments=[
   ("Hook", "Parents, quick one. An email says the state aid deadline is close and offers to file your kid's FAFSA for "
            "seventy-nine dollars.", "File your FAFSA for $79?", "an email with a deadline banner"),
   ("The rule", "The FTC says the FAFSA is always free to fill out and submit. Never pay anyone to fill it out or "
                "process it.", "FTC: always free. Never pay.", "a price tag reading $0"),
   ("Where", "The real form is at studentaid.gov. Your kid's school counselor or the college aid office will help, "
             "free.", "Real form: studentaid.gov", "a laptop on the studentaid.gov page"),
   ("Do this", "Delete the email. If you already paid, call your card company and report it at ReportFraud.ftc.gov.",
    "Paid? Call your card company", f"{MASCOT} deleting an email"),
  ]),
 dict(date="2027-03-11", time="12:00", kind="short", look="walkthrough", pillar=BET, topic="fake sportsbook bonus",
  title="March Madness '$500 bonus bet' app? Check 1 list first",
  hook="1 text, 1 betting app you've never heard of, and a $500 bonus bet on the house for March Madness.",
  thumb="Big bonus bet? Check the list",
  hashtags=["marchmadness", "sportsbetting", "bettingscam", "scamalert", "scamdecoded"],
  description="Fake betting sites and apps that lure you with a big bonus, from the BBB.",
  caption="The BBB warns that scammers build betting sites and apps that look trustworthy, and pull you in with a big "
          "introductory bonus that makes your first bet feel free. Bet only with sportsbooks your state's gaming "
          "commission has approved.",
  sources=[BBB_BET], claims=["BBB: fake betting sites and apps lure users with an introductory bonus that makes an initial bet feel free of risk",
                             "BBB: use sportsbooks approved by your area's gaming commission",
                             "BBB: don't respond to gambling pop-ups, spam emails or texts"],
  original_element="Phone walkthrough: the text, the slick app, the bonus pop-up, then the state gaming commission's approved list side by side.",
  segments=[
   ("Hook", "A text: March Madness is here, take a five-hundred-dollar bonus bet, on the house. The app looks as slick as "
            "the big names.", "$500 bonus bet 'on the house'", "a text with a basketball emoji"),
   ("The trick", "The BBB says scammers build betting sites and apps that look trustworthy, and use a big bonus to get "
                 "your deposit and your details.", "Looks real. Built to take deposits", "a shiny app over a dark room"),
   ("Check", "Your state's gaming commission lists the sportsbooks it has approved. Not on the list? Not a sportsbook "
             "you should use.", "Not on your state's list? Skip", "a list with a magnifying glass"),
   ("Do this", "Ignore betting texts and pop-ups, and read any bonus terms first. Report fakes to BBB Scam Tracker.",
    "Ignore betting texts and pop-ups", f"{MASCOT} swiping a text away"),
  ]),
 dict(date="2027-03-16", time="12:00", kind="short", look="data chart", pillar=BET, topic="blocked betting withdrawals",
  title="Won $1,200 but can't cash out? 1 reason it's fake",
  hook="1 bracket, 1 win of $1,200 on a new betting app, and then the cash-out button stops working.",
  thumb="Can't cash out? Stop paying",
  hashtags=["marchmadness", "sportsbetting", "bettingscam", "bracket", "scamdecoded"],
  description="How fake betting apps stop you withdrawing and ask for more deposits, from the BBB.",
  caption="You win on a betting app, then can't withdraw. The BBB says fake sites blame 'technical issues' or ask for "
          "more identity checks, and may tell you to deposit more before you can cash out. Don't send more.",
  sources=[BBB_BET], claims=["BBB: on fake betting sites cash-outs fail, blamed on technical issues or extra identity verification",
                             "BBB: victims may be told to deposit more money before they can withdraw winnings",
                             "BBB: details given to the site can end up with scammers"],
  original_element="A data-chart beat: the app's balance climbing beside the line for 'money you can actually withdraw', flat at $0.",
  segments=[
   ("Hook", "Your bracket bets came in. The app says you're up twelve hundred dollars. You hit cash out, and get an "
            "error.", "Up $1,200. Cash out: error", "a phone with a red error"),
   ("Step two", "The BBB says fake betting sites blame technical issues, or ask for more and more identity checks.",
    "'Technical issue.' 'Verify again.'", "a loading spinner that never ends"),
   ("Step three", "Then the real ask: deposit three hundred more to unlock your winnings. Pay it, and there's always "
                  "another reason.", "'Deposit $300 more to unlock'", "a padlock on a pile of coins"),
   ("Do this", "Stop depositing. The balance was never real. Call your bank, and report it to BBB Scam Tracker and "
               "your state's gaming commission.", "Stop depositing. Report it.", f"{MASCOT} closing a wallet"),
  ]),
 dict(date="2027-03-18", time="12:00", kind="short", look="checklist", pillar=AID, topic="FSA ID requests",
  title="'Send us your FSA ID': 0 people should get it",
  hook="1 'aid consultant' says they can get your kid more money, if you send them your FSA ID.",
  thumb="Your FSA ID is yours",
  hashtags=["fafsa", "financialaid", "studentloans", "college", "scamdecoded"],
  description="Never share your FSA ID, even with companies or consultants, says the FTC.",
  caption="Your FSA ID is the username and password for federal student aid. The FTC says never share it, including "
          "with companies or consultants who say they'll help.",
  sources=[FTC_AID], claims=["FTC: never share your FSA ID, including with companies or consultants"],
  original_element="A three-line checklist on screen: who gets the FSA ID (you), who doesn't (everyone else), what to do if you shared it.",
  segments=[
   ("Hook", "A college aid consultant says they can find your kid thousands in extra aid. They just need your FSA ID "
            "to log in.", "'Just send your FSA ID'", "a chat bubble with a key"),
   ("What it is", "The FSA ID is the username and password for federal student aid. It signs forms and opens your "
                  "records.", "It's your federal aid password", "a key labelled FSA ID"),
   ("The rule", "The FTC says never share it, including with companies or consultants. Anyone helping you can do it "
                "while you type.", "FTC: never share it. Not even consultants", "a checklist with a red X"),
   ("Do this", "Already shared it? Change the password at studentaid.gov now, and report the company at "
               "ReportFraud.ftc.gov and to your state attorney general.", "Shared it? Change it now", f"{MASCOT} changing a lock"),
  ]),
 dict(date="2027-03-23", time="12:00", kind="short", look="myth vs fact", pillar=TRAVEL, topic="fake international driving permits",
  title="Driving abroad? 2 places issue a real permit in the US",
  hook="1 site sells an 'international driver's license' for $69, and 2 groups are allowed to issue the real permit.",
  thumb="Only 2 can issue it",
  hashtags=["travel", "springtravel", "roadtrip", "travelscam", "scamdecoded"],
  description="Fake international driving permits, and the only two US issuers, from the FTC.",
  caption="Renting a car abroad? The FTC says scammers set up sites selling fake international driving permits. In the "
          "US, the State Department has authorized only two groups to issue them: AAA and AATA.",
  sources=[FTC_TRAVEL], claims=["FTC: scammers create websites to sell fake international driving permits",
                                "FTC: the State Department authorizes only AAA and AATA to issue IDPs in the US"],
  original_element="Myth vs fact cards: 'international driver's license' (myth), 'international driving permit from AAA or AATA' (fact).",
  segments=[
   ("Hook", "Myth: you can buy an international driver's license online in five minutes for sixty-nine dollars.",
    "Myth: $69 online license", "a glossy fake ID card"),
   ("Fact", "The FTC says scammers build sites to sell fake international driving permits. The real thing is a permit, "
            "not a license.", "Fact: lots of these are fake", "a stamp reading FAKE"),
   ("Who issues it", "In the US, the State Department has authorized only two groups to issue one: AAA and AATA. "
                     "That's the whole list.", "Only 2: AAA and AATA", "two badges side by side"),
   ("Do this", "Anyone else selling one is selling you nothing. Order from one of the two, and carry your own license "
               "too.", "Anyone else? Skip it", f"{MASCOT} crossing out a website"),
  ]),
 dict(date="2027-03-25", time="12:00", kind="short", look="quiz pause", pillar=TRAVEL, topic="fake charter flight packages",
  title="Private jet spring break package? 1 approval to check",
  hook="1 ad offers a private charter flight, hotel and tours for spring break, at a group price.",
  thumb="Charter deal? Ask the DOT",
  hashtags=["springbreak", "travel", "travelscam", "charterflight", "scamdecoded"],
  description="Checking a charter package against the DOT's approval, from the FTC.",
  caption="Charter flight packages can be real, and some are scams. The FTC says if the charter filing isn't approved "
          "by the US Department of Transportation before the package is sold, you're probably dealing with a dishonest "
          "operator.",
  sources=[FTC_TRAVEL], claims=["FTC: if the charter filing isn't approved by DOT before the package is sold, it's probably a dishonest operator",
                                "FTC: check DOT's charter list, or ask a local travel agent or the American Society of Travel Advisors"],
  original_element="Quiz pause: 'Which detail would you check first?' with three options, held for two seconds before the answer.",
  segments=[
   ("Hook", "A group spring break deal: private charter flight, hotel and tours, one price. Pause. What would you check "
            "first?", "Pause: what do you check first?", "a quiz card with three options"),
   ("Answer", "The flight's approval. The FTC says a charter filing should be approved by the Department of "
              "Transportation before the package is sold.", "Answer: is it DOT-approved?", "a plane with a checkmark"),
   ("If not", "Not approved before they sold it to you? The FTC says you're probably dealing with a dishonest charter "
              "operator.", "No approval? Probably dishonest", "a plane with a question mark"),
   ("Do this", "Look up the operator on the DOT's charter list, or ask a local travel agent before paying anything.",
    "Check the DOT list before paying", f"{MASCOT} reading a list"),
  ]),
 dict(date="2027-03-30", time="12:00", kind="short", look="walkthrough", pillar=TRAVEL, topic="rental landlord checks",
  title="Spring rental 'owner abroad'? Check 1 county record",
  hook="1 listing, 1 owner who's 'out of the country', and keys they'll mail after you pay.",
  thumb="Owner abroad? Check records",
  hashtags=["rentalscam", "springbreak", "vacationrental", "travel", "scamdecoded"],
  description="Checking a private landlord against county tax records, from the FTC.",
  caption="A rental owner who's out of the country and can't show the place is a classic sign, says the FTC. Ask for a "
          "video tour, and check a private landlord's ID against county tax records before you pay anything.",
  sources=[FTC_RENTAL], claims=["FTC: fake owners often claim to be out of the country and avoid showing the property",
                                "FTC: check a private landlord's ID against county tax records",
                                "FTC: ask for a video or virtual tour if you can't visit"],
  original_element="Walkthrough of a county property-records search: owner name on the listing vs the name on the record.",
  segments=[
   ("Hook", "The beach house is perfect. The owner is working overseas, so they'll mail you the keys once your deposit "
            "clears.", "Owner abroad, keys by mail", "a beach house photo and an envelope"),
   ("The sign", "The FTC says fake owners often claim to be out of the country, so they never have to show you the "
                "place.", "Out of the country = can't show it", "a plane over a house"),
   ("The check", "Many counties put property records online. Search the address and see if the owner's name matches the "
                 "person messaging you.", "Does the owner's name match?", "a records search with two names"),
   ("Do this", "Ask for a live video tour too. Names don't match, or no tour? Walk away, however good the price is.",
    "No match or no tour? Walk away", f"{MASCOT} walking away"),
  ]),
 dict(date="2027-04-01", time="12:00", kind="short", look="face cam", pillar=AID, topic="scholarship fees",
  title="'$2,500 scholarship, pay a $35 fee': 0 real ones charge",
  hook="1 letter says your kid was picked for a $2,500 scholarship, after a $35 'redemption fee'.",
  thumb="Scholarship fee? Not real",
  hashtags=["scholarships", "college", "financialaid", "students", "scamdecoded"],
  description="Scholarship processing and redemption fees are red flags, says the FTC.",
  caption="A scholarship you didn't apply for, with a 'processing' or 'redemption' fee to claim it. The FTC says never "
          "pay to apply for a scholarship, and legitimate companies never promise you'll win one.",
  sources=[FTC_AID], claims=["FTC: never pay to apply for a scholarship",
                             "FTC: upfront 'processing' or 'redemption' fees are red flags",
                             "FTC: legitimate companies never promise scholarships or grants",
                             "FTC: report scholarship scams at ReportFraud.ftc.gov and to your state attorney general"],
  original_element="Face-to-camera with the fake award letter on a clipboard, circling the fee line.",
  segments=[
   ("Hook", "Your kid gets a letter: selected for a twenty-five-hundred-dollar scholarship. To release it, pay a "
            "thirty-five-dollar redemption fee.", "$2,500 award, $35 fee", "an award letter with a seal"),
   ("The rule", "The FTC says never pay to apply for a scholarship. Processing fees and redemption fees are red flags.",
    "FTC: never pay for a scholarship", "a fee line circled in red"),
   ("The promise", "And watch the promises. The FTC says legitimate companies never promise you'll win a scholarship "
                   "or grant.", "Real ones never promise a win", "a crossed-out pinky promise"),
   ("Do this", "Don't pay. Ask the school counselor, and report the letter at ReportFraud.ftc.gov and to your state "
               "attorney general.", "Don't pay. Report it.", f"{MASCOT} stamping a letter VOID"),
  ]),
 dict(date="2027-04-06", time="12:00", kind="short", look="screen recording", pillar=TRAVEL, topic="passport lookalike sites",
  title="Renewing a passport? 1 search result that adds a fee",
  hook="1 search for 'passport renewal' and the top result looks official, then charges you a 'service fee'.",
  thumb="Official-looking. Not official.",
  hashtags=["passport", "springtravel", "travelscam", "summertravel", "scamdecoded"],
  description="Imposter sites that copy government pages and charge high fees, from the FTC.",
  caption="Planning a trip abroad? The FTC warns that imposter sites copy official government websites and charge you "
          "high fees, sometimes for things the real site does for free. Go to the official government site directly.",
  sources=[FTC_TRAVEL], claims=["FTC: imposter sites copy official government websites and charge high fees",
                                "FTC: go directly to the official government site to check what services cost",
                                "US passport information is on the State Department's site, travel.state.gov"],
  original_element="Screen recording of a search page: an ad with a seal and a 'processing fee', then the real .gov address typed in by hand.",
  segments=[
   ("Hook", "You search passport renewal. The first result has a seal, a flag and a form. Then a sixty-dollar "
            "service fee on top.", "Seal, flag, form... and a fee", "a search results page"),
   ("Why", "The FTC says imposter sites copy official government pages and charge high fees, sometimes for things the "
           "real site does for free.", "They copy the real site", "two near-identical web pages"),
   ("How to tell", "Look at the address before you type anything. US passport help lives on the State Department's "
                   "own site, travel.state.gov.", "Check the address: travel.state.gov", "an address bar zoomed in"),
   ("Do this", "Skip the ads and type the official address yourself. Then send this to someone "
               "planning a summer trip.", "Type the .gov address yourself", f"{MASCOT} typing on a keyboard"),
  ]),
 dict(date="2027-04-08", time="12:00", kind="short", look="illustrated", pillar=TRAVEL, topic="vacation deal robocalls",
  title="'Press 1 for 70% off a vacation': 1 call to hang up on",
  hook="1 recorded voice offers you 70% off a spring vacation if you press 1 right now.",
  thumb="Robocall deal? Hang up",
  hashtags=["robocall", "travel", "vacation", "travelscam", "scamdecoded"],
  description="Robocalls offering discounted vacations are a warning sign, says the FTC.",
  caption="A recorded call offers a vacation at a big discount. The FTC calls robocalls offering vacation deals a "
          "warning sign, and says to avoid doing business with the company.",
  sources=[FTC_TRAVEL], claims=["FTC: you might get robocalls offering vacation deals at a discounted price; avoid doing business with them"],
  original_element="Illustrated call screen with the robocall audio as captions, then the block-and-report taps.",
  segments=[
   ("Hook", "Hi, this is a special message. You qualify for seventy percent off a spring vacation package. Press one "
            "to speak to an agent.", "'Press 1 for 70% off'", "a phone showing an unknown caller"),
   ("The sign", "The FTC says robocalls offering discounted vacation deals are a warning sign. Don't do business with "
                "the company.", "FTC: a robocall deal is a warning", "a phone with a warning triangle"),
   ("Why not press", "Pressing one tells them a real person answered. The agent's job is getting your card number "
                     "before you think.", "Press 1 = 'this number works'", "a finger over a keypad"),
   ("Do this", "Hang up, block the number, and plan trips with companies you looked up yourself.",
    "Hang up. Block. Book it yourself.", f"{MASCOT} tapping block"),
  ]),
]


def item(p):
    return {"format": "short", "pillar": PILLAR[p["pillar"]], "thread": p["pillar"], "platforms": ["instagram", "youtube"],
            "post_on": f"{p['date']} {p['time']}", "topic": p["topic"], "look": p["look"],
            "original_element": p["original_element"], "idea_angle": f"{SEASON}: {p['topic']}. {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": [seg(*r) for r in p["segments"]], "cta": CTA,
                       "caption": p["caption"] + "\n\n" + CHECKER + "\n\n" + CTA, "hashtags": p["hashtags"],
                       "description": p["description"], "thumbnail_text": p["thumb"], "sources": p["sources"],
                       "claims_to_verify": p["claims"]}}


def plan(items):
    rows = ["# Scam Decoded: spring pack, Tue Mar 2 – Thu Apr 8 2027", "",
            "11 Shorts (Reels + YouTube Shorts) at 12:00 on Tuesdays and Thursdays, America/New_York, in slots weeks "
            "13–21, weeks 22–26, the tax pack and the newsletter cuts leave free. Nothing has been posted; Dhruv posts "
            "each by hand.", "",
            "Three threads: **March Madness betting** (fake sportsbook bonuses, blocked withdrawals), **spring travel and "
            "rentals** (free trip fees, passport lookalike sites, fake driving permits, charter packages, owner-abroad "
            "rentals, vacation robocalls) and **the FAFSA window** (paid filing, FSA ID requests, scholarship fees). "
            "'VIP picks', half-price rentals with a Zelle deposit, student loan forgiveness fees and the spring break long "
            "video are already in weeks 13–21, so none of those angles repeat.", "",
            "| # | Date | Time | Thread | Look | Topic | Title |", "|---|---|---|---|---|---|---|"]
    for n, (p, i) in enumerate(zip(POSTS, items)):
        d = dt.date.fromisoformat(p["date"])
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} | {p['time']} | {p['pillar']} | {p['look']} | "
                    f"{p['topic']} | {p['title']} |")
    rows += ["", "Sources: every item lists the public FTC or BBB page it relies on in `sources`. Check each "
             "`claims_to_verify` line against it the week it posts, and check the March Madness dates (Selection Sunday "
             "is usually mid-March).", "",
             "Pairs: #2 and #3 sit either side of the weeks 13–21 betting "
             "carousel (#55, Thu Mar 11) and Short (#15, Fri Mar 12). #4 lands the same day as the student loan carousel "
             "(#59, Thu Mar 18, 19:30)."]
    return "\n".join(rows) + "\n"


def main():
    items = [item(p) for p in POSTS]
    root = HERE.parent.parent
    assert all(a["look"] != b["look"] for a, b in zip(items, items[1:]))
    for i in items:
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        assert 60 <= w <= 120, (i["script"]["title"], w)
        assert len(i["script"]["title"]) <= 60, i["script"]["title"]
        assert len(i["script"]["hashtags"]) <= 5
        for s in i["script"]["segments"]:
            assert len(s["on_screen_text"].split()) <= 12, s["on_screen_text"]
        hook = i["script"]["hook"]
        assert any(ch.isdigit() for ch in hook.split(".")[0][:60]), hook
        assert "guarantee" not in json.dumps(i).lower()
    (root / "spring-2027.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (root / "POSTING_PLAN_SPRING_2027.md").write_text(plan(items))
    for n, i in enumerate(items):
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        print(n, i["post_on"], i["look"], w, i["script"]["title"])


if __name__ == "__main__":
    main()
