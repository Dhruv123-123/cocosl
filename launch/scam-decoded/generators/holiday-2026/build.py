"""Holiday-season scam pack, Nov 9 - Dec 16 2026: delivery texts, fake charities, gift cards, marketplace.

    python3 build.py   ->  ../../holiday-2026.json

10 posts in 3 formats (4 Shorts, 2 TikTok minute cuts, 4 Instagram carousels), following ORIGINALITY_PASS.md:
no two consecutive posts in the same format, a walkthrough or quiz in each video, human voice on TikTok.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, CTA_TIKTOK, MASCOT, P_FAMILY, P_TEXT, seg  # noqa: E402

DELIV = "https://consumer.ftc.gov/consumer-alerts/2024/12/scammers-are-delivering-phishing-messages-holiday-season"
SHIP = ("https://consumer.ftc.gov/consumer-alerts/2023/12/"
        "fake-shipping-notification-emails-text-messages-what-you-need-know-holiday-season")
SPAM = "https://consumer.ftc.gov/articles/how-recognize-and-report-spam-text-messages"
GIFT = "https://consumer.ftc.gov/gift-card-scams"
GIFT_ONLY = "https://consumer.ftc.gov/consumer-alerts/2024/10/only-scammers-tell-you-buy-gift-card-pay-them"
GIFT_CHECK = "https://consumer.ftc.gov/consumer-alerts/2024/12/check-out-gift-cards-you-buy-them"
CHARITY = "https://consumer.ftc.gov/articles/giving-charity"
GIVING_TUE = "https://consumer.ftc.gov/consumer-alerts/2025/11/donate-charities-not-scammers-giving-tuesday"
TEOS = "https://apps.irs.gov/app/eos/"
SHOP = "https://consumer.ftc.gov/consumer-alerts/2025/11/how-avoid-online-shopping-scam-holiday-season"
ONLINE = "https://consumer.ftc.gov/articles/online-shopping"
SELLING = "https://consumer.ftc.gov/consumer-alerts/2022/07/selling-stuff-online-heres-how-avoid-scam"
CHECKS = "https://consumer.ftc.gov/articles/how-spot-avoid-and-report-fake-check-scams"
REPORT = "https://reportfraud.ftc.gov/"
VOICE = "Dhruv records the narration in his own voice. No AI voice on TikTok cuts."
CHECKER = "Not sure about a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends nothing anywhere."
P_SHOP = "online shopping and marketplace scams"


def segs(rows):
    return [seg(*r) for r in rows]


def slides(cover, items, save, cover_vis):
    out = [("Hook", "", cover, cover_vis)]
    out += [(str(i), n, o, v) for i, (n, o, v) in enumerate(items, 1)]
    out.append(("Save this", save, "Save it. Share it.", f"{MASCOT} giving a thumbs up"))
    return out


POSTS = [
 dict(date="2026-11-09", day="Mon", time="12:00", kind="short", topic="delivery", pillar=P_TEXT,
  title="'Your package is on hold': 1 holiday text to never tap",
  hook="1 text shows up more than any other in November. Here's how to spot it.",
  thumb="Package on hold? Don't tap.",
  hashtags=["packagescam", "deliveryscam", "holidayscams", "smishing", "scamdecoded"],
  description="The fake 'package on hold' text that spikes every holiday season, and the safe way to track a parcel.",
  caption="Everyone's expecting a package this month, and scammers know it. The tells: a link, a countdown and a tiny "
          "'redelivery fee'. Track from the shop's own email instead. Example is fictional.",
  sources=[DELIV, SHIP, SPAM], claims=["Fake delivery texts and emails increase around the holidays (FTC)",
                                         "Forwarding spam texts to 7726 reports them to your carrier"],
  original_element="Walkthrough video w2-delivery (originality/out/walkthroughs/w2-delivery) as the visual.",
  segments=[
   ("Hook", "One text shows up more than any other in November. Your package is on hold. Update your address in twelve hours, "
            "or it goes back.", "'Your package is on hold'", "walkthrough w2-delivery, message arriving"),
   ("The bait", "Then a tiny fee. Thirty cents for redelivery. Nobody argues with thirty cents. But they don't want thirty "
                "cents. They want the card number you type in.", "The fee is the bait", "walkthrough w2-delivery, fee highlighted"),
   ("The tell", "Look at the link. It isn't the carrier's real site. And you never gave a carrier your number for this order.",
                "Not the carrier's site", "walkthrough w2-delivery, link highlighted"),
   ("Do this", "Track it with the number in the shop's own order email or app. Then forward the text to seven seven two six, "
               "and delete it.", "Track from the shop's email. Forward to 7726.", f"{MASCOT} holding a parcel and a phone"),
  ]),
 dict(date="2026-11-12", day="Thu", time="19:30", kind="carousel", topic="gift cards", pillar=P_FAMILY,
  title="5 gift card requests only a scammer makes",
  hook="5 gift card asks you'll hear this season, and every one is a scam.",
  thumb="5 gift card scams",
  hashtags=["giftcards", "giftcardscam", "holidayscams", "protectyourparents", "scamdecoded"],
  description="Five ways scammers ask for gift cards, and the one rule that covers all of them.",
  caption="Gift cards are for gifts. Anyone who asks you to pay with one, for anything else, is scamming you:\n"
          "1. The 'boss'\n2. The 'utility company'\n3. The 'government agency'\n4. The grandchild in trouble\n5. The online seller",
  sources=[GIFT, GIFT_ONLY], claims=["Only scammers tell you to buy a gift card to pay them (FTC)",
                                     "Scammers ask for the numbers on the back of the card"],
  original_element="Final slide reuses the quiz style; Dhruv adds a 10-second story showing a real gift card's back (unscratched).",
  segments=slides("5 gift card scams", [
   ("A text from your 'boss': grab gift cards for the team, send photos of the codes, keep it quiet.", "1. The 'boss'", "an office desk with a phone"),
   ("A call from your 'power company': pay the overdue bill with gift cards in an hour or we cut you off.", "2. The 'utility'", "a light bulb with a clock"),
   ("A call from the 'IRS' or 'Social Security' saying you owe money, payable by gift card.", "3. The 'government'", "a government building with a phone"),
   ("A grandchild in trouble who needs bail money now, in gift cards, and begs you not to tell anyone.", "4. The 'grandchild'", "a crying phone emoji"),
   ("An online seller who only takes gift cards for that hard-to-find toy or ticket.", "5. The 'seller'", "a shopping bag with a padlock"),
  ], "One rule covers all 5: gift cards are for gifts. Save this and send it to someone who buys them.",
     f"{MASCOT} holding a gift card with a red flag")),
 dict(date="2026-11-17", day="Tue", time="18:00", kind="tiktok", topic="marketplace", pillar=P_SHOP,
  title="Selling gifts on Marketplace? 3 flags in this 'payment'",
  hook="3 red flags in 1 'payment pending' email. Pause and find them before I do.",
  thumb="Find the 3 red flags",
  hashtags=["facebookmarketplace", "marketplacescam", "sellingonline", "holidayscams", "scamdecoded"],
  description="The fake payment app email that makes sellers pay to 'receive' money.",
  caption="Selling things before the holidays? This fake 'payment pending' email is aimed at you. Example is fictional.",
  sources=[SELLING, CHECKS, REPORT], claims=["Payment apps don't charge sellers to receive a payment",
                                            "Scammers send fake payment emails to online sellers (FTC)"],
  original_element="Built on quiz carousel q2-marketplace, with a pause card. " + VOICE,
  segments=[
   ("Hook", "Three red flags in one payment email. Selling stuff before the holidays? Pause and find them before I do.",
            "3 red flags. Find them.", "quiz slide q2-marketplace/slide-01"),
   ("The email", "You listed a bike. A buyer says they'll pay through a payment app. Then this email arrives. The buyer sent four "
                 "hundred fifty dollars. Because it's your first sale, upgrade to a business account for a hundred fifty dollars, "
                 "refundable, before the money is released.", "Pause: how many flags?", "quiz slide q2-marketplace/slide-01, zooming in"),
   ("Pause", "Pause. Count them. Three seconds.", "Pause", "a full-screen countdown card"),
   ("Flag 1", "Red flag one: the sender. Look at the address. It isn't the payment app's real domain. It's a lookalike.",
              "1: not the real app", "quiz slide q2-marketplace/slide-03"),
   ("Flag 2", "Red flag two: an upgrade before you can be paid. Payment apps don't charge you to receive money. Ever.",
              "2: pay to get paid", "quiz slide q2-marketplace/slide-04"),
   ("Flag 3", "Red flag three: refundable. That word is doing all the work. You pay first, and the refund never comes. There "
              "was never a four hundred fifty dollar payment either.", "3: 'refundable'", "quiz slide q2-marketplace/slide-05"),
   ("The fix", "So check payments only inside your own payment app, opened yourself. Hand over the bike when the money is "
               "really there. Better yet, meet in person and get paid on the spot.", "Check the app, not the email",
               f"{MASCOT} holding a phone with a green check"),
   ("Close", "How many did you find before I said them?", "How many did you get?", f"{MASCOT} holding up three fingers"),
  ]),
 dict(date="2026-11-20", day="Fri", time="12:00", kind="short", topic="marketplace", pillar=P_SHOP,
  title="A $200 deposit to 'hold' it: 1 marketplace rule",
  hook="$200 to hold a game console you've never seen. Here's the 1 rule that stops it.",
  thumb="Never pay to hold it",
  hashtags=["marketplacescam", "blackfriday", "onlineshopping", "holidayscams", "scamdecoded"],
  description="Why you should never send a deposit to hold an item from an online marketplace seller.",
  caption="Hard-to-find gift, great price, seller wants a deposit by payment app to hold it? That's the scam. "
          "Example is fictional.",
  sources=[SHOP, ONLINE, REPORT], claims=["Payment app transfers are hard to reverse",
                                          "FTC advises paying by credit card for online purchases for dispute rights"],
  original_element="Face cam: Dhruv reads the seller's messages from his phone, then the rule on screen.",
  segments=[
   ("Hook", "Two hundred dollars to hold a game console you've never seen. That's the whole scam, and it peaks right now.",
            "$200 to 'hold' it", f"{MASCOT} looking at a game console behind glass"),
   ("The setup", "Great price, sold out everywhere else. The seller says three people are asking, so send a deposit by "
                 "payment app and it's yours.", "'3 people are asking'", "a chat bubble with a clock"),
   ("The tell", "Pressure, plus a payment you can't take back. Payment apps work like cash. Once it's sent, it's gone, "
                "and so is the seller.", "Payment apps work like cash", "a coin disappearing from a phone"),
   ("The rule", "Never pay before you see the item. Meet somewhere public and pay on the spot, or buy through a checkout "
                "with a credit card, so you can dispute it.", "See it first. Then pay.", f"{MASCOT} shaking hands at a table"),
  ]),
 dict(date="2026-11-24", day="Tue", time="19:30", kind="carousel", topic="charity", pillar=P_FAMILY,
  title="Before Giving Tuesday: a 4-step charity check",
  hook="4 steps, 2 minutes, and your Giving Tuesday donation reaches a real charity.",
  thumb="Check a charity in 2 minutes",
  hashtags=["givingtuesday", "charity", "donate", "charityscam", "scamdecoded"],
  description="Four quick checks before you donate this Giving Tuesday.",
  caption="Giving Tuesday is Dec 1. Before you give:\n1. Look the charity up yourself\n2. Check it at Give.org or Charity "
          "Navigator\n3. Want a tax deduction? Check the IRS list\n4. Pay by card or check, never gift card, wire or crypto",
  sources=[CHARITY, GIVING_TUE, TEOS], claims=["Giving Tuesday 2026 falls on Dec 1 (the Tuesday after Thanksgiving)",
                                               "The IRS Tax Exempt Organization Search shows which groups can receive tax-deductible donations"],
  original_element="Slide 3 is a 10-second screen recording Dhruv makes of the IRS Tax Exempt Organization Search (search a well-known charity).",
  segments=slides("Charity check: 4 steps", [
   ("Look the charity up yourself. Don't use the link in the text, call or post that asked you.", "1. Look it up yourself", "a magnifying glass over a heart"),
   ("Check it at Give.org or Charity Navigator. A charity with no record, or a name one letter off a famous one, is a warning.", "2. Check a watchdog", "a checklist with stars"),
   ("Want the tax deduction? Search the IRS Tax Exempt Organization Search to see if gifts to it are deductible.", "3. Check the IRS list", "a receipt with a tick"),
   ("Give on the charity's own website by credit card or check. Never by gift card, wire or crypto.", "4. Card or check only", "a credit card with a heart"),
  ], "Save this for Dec 1, and share it with the most generous person you know.", f"{MASCOT} holding a heart-shaped box")),
 dict(date="2026-11-30", day="Mon", time="12:00", kind="short", topic="charity", pillar=P_FAMILY,
  title="'Thanks for your pledge last year': 1 charity text to skip",
  hook="1 thank-you text for a donation you never made. It's the most polite scam of the year.",
  thumb="Thanks for... what pledge?",
  hashtags=["givingtuesday", "charityscam", "donate", "holidayscams", "scamdecoded"],
  description="Fake charity texts that thank you for a past pledge to get you to 'renew' it.",
  caption="Giving Tuesday is tomorrow. Real charities welcome your gift next week too; scammers need it today. "
          "Example is fictional.",
  sources=[CHARITY, GIVING_TUE, REPORT], claims=["Scammers thank you for donations you don't remember to get you to pay (FTC)",
                                                  "Charities don't ask for donations by gift card or wire (FTC)"],
  original_element="Quiz carousel q7-charity slides as the visuals (originality/out/quizzes/q7-charity).",
  segments=[
   ("Hook", "One thank-you text, for a donation you never made. Thank you for your generous pledge last year. Families "
            "are counting on you again.", "'Thanks for your pledge'", "quiz slide q7-charity/slide-01"),
   ("The trick", "You don't remember the pledge, but who wants to look stingy? That doubt is the point. The text asks you to "
                 "renew today, by gift card or payment app.", "Doubt + 'renew today'", "quiz slide q7-charity/slide-04"),
   ("The tell", "Real charities don't need it today, and don't take gift cards. The link is a new site, not one you can look up.",
                "No real charity wants gift cards", "quiz slide q7-charity/slide-05"),
   ("Do this", "Want to give? Look the charity up yourself and donate on its own site, by card. Then delete the text.",
               "Look it up. Give on its site.", f"{MASCOT} holding a heart and a credit card"),
  ]),
 dict(date="2026-12-03", day="Thu", time="19:30", kind="carousel", topic="charity", pillar=P_FAMILY,
  title="Spot the red flags: the 'holiday relief' text",
  hook="4 red flags in 1 holiday charity text. How many can you find?",
  thumb="Find 4 red flags",
  hashtags=["charityscam", "spotthescam", "holidayscams", "donate", "scamdecoded"],
  description="A quiz: find the four red flags in a fake holiday charity text.",
  caption="Quiz time. Count the red flags before you swipe. Answers on slides 3–6. Example is fictional.",
  sources=[CHARITY, GIVING_TUE], claims=["Fake charities pressure you to give immediately (FTC)",
                                         "Fake charities ask for gift cards, wire or crypto (FTC)"],
  original_element="Rendered quiz carousel q7-charity: use the 7 PNG slides as-is (originality/out/quizzes/q7-charity).",
  segments=slides("Find 4 red flags", [
   ("Thanks for a pledge you don't remember making. It plays on doubt and politeness.", "1. A pledge you never made", "quiz slide 3"),
   ("Today. Real charities welcome your gift next week too.", "2. 'Today'", "quiz slide 4"),
   ("Gift card or payment app. No real charity asks for gift cards.", "3. Gift cards", "quiz slide 5"),
   ("A brand-new site with an odd ending, not a charity you can look up.", "4. The link", "quiz slide 6"),
  ], "Look the charity up yourself and give on its own site. How many did you get?", f"{MASCOT} holding a score card")),
 dict(date="2026-12-08", day="Tue", time="18:00", kind="tiktok", topic="gift cards", pillar=P_FAMILY,
  title="The 'boss' who needs 5 gift cards for the team, played out",
  hook="5 gift cards, 1 text from your 'boss'. Watch how December's favourite office scam plays out.",
  thumb="Your boss didn't send this",
  hashtags=["giftcardscam", "workscams", "holidayscams", "officelife", "scamdecoded"],
  description="The boss impersonation gift card text, walked through, and the 10-second check that stops it.",
  caption="Holiday gifts for the team, bought with your money, codes sent by text. Your boss didn't send it. "
          "Example is fictional.",
  sources=[GIFT, GIFT_ONLY, REPORT], claims=["Only scammers ask you to buy gift cards and send the numbers (FTC)",
                                             "Contact the gift card company right away if you paid a scammer with one (FTC)"],
  original_element="Walkthrough video w7-boss-gift-cards for segments 1-5. " + VOICE,
  segments=[
   ("Hook", "Five gift cards, one text from your boss. Watch how December's favourite office scam plays out, message by message.",
            "5 gift cards. 1 'boss'.", "walkthrough w7-boss-gift-cards, blank"),
   ("Text 1", "Hi, it's Karen. Are you free? I'm stuck in meetings all day and can't talk. You reply, sure, what's up?",
              "'I can't talk'", "walkthrough w7, first two messages"),
   ("Text 2", "I want to surprise the team with holiday gifts. Pick up five hundred dollar gift cards, scratch the backs, and "
              "text me photos of the codes. I'll pay you back today. Keep it quiet, it's a surprise.",
              "'Text me photos of the codes'", "walkthrough w7, third message"),
   ("Pause", "Pause. How many red flags? Count them before I say them.", "Pause: count the flags", "a full-screen countdown card"),
   ("The flags", "There are four. She can't talk, so you can't check her voice. Gift cards. Photos of the codes, which are the "
                 "money itself. And keep it quiet, so no coworker says, wait, that's a scam.", "Can't talk · gift cards · codes · secret",
                 "walkthrough w7, all four flags lit"),
   ("The fix", "So walk over to her desk, or call her on the number you already have. Not the number that texted you. "
               "Real bosses can wait ten seconds.", "Call her real number", f"{MASCOT} walking to an office door"),
   ("Already sent?", "Already sent the codes? Call the gift card company right away, using the number on the card, and ask for a "
                     "refund. Keep the cards and receipts, and report it at report fraud dot f t c dot gov.",
                     "Sent codes? Call the card company now.", "a phone dialling, gift cards and receipt on a table"),
  ]),
 dict(date="2026-12-11", day="Fri", time="12:00", kind="short", topic="gift cards", pillar=P_FAMILY,
  title="Buying gift cards this weekend? 1 check at the rack first",
  hook="1 check at the gift card rack takes 5 seconds and stops a holiday scam.",
  thumb="Check the back first",
  hashtags=["giftcards", "christmasshopping", "holidayscams", "shoppingtips", "scamdecoded"],
  description="How tampered gift cards work, and the five-second check before you buy one.",
  caption="Some scammers tamper with gift cards on the rack so your money lands on their card. Check the packaging, "
          "or buy from behind the counter.",
  sources=[GIFT_CHECK, GIFT], claims=["Scammers tamper with gift cards in stores so the balance goes to them (FTC)",
                                      "Keep the receipt and contact the card company if a card is empty"],
  original_element="Dhruv films his own hands checking a real gift card's packaging and back at home (no store footage).",
  segments=[
   ("Hook", "One check at the gift card rack takes five seconds, and it stops a scam that peaks right now.",
            "5 seconds at the rack", f"{MASCOT} at a gift card rack"),
   ("The scam", "Scammers take cards off the rack, record the numbers, cover the PIN again and put them back. When you load "
                "money onto it, they spend it first.", "Your money, their card", "a gift card with a peeled sticker"),
   ("The check", "Before you buy, check the packaging isn't torn and the PIN area isn't scratched or re-stuck. Better yet, "
                 "pick a card from behind the counter.", "Torn? Scratched? Put it back.", "two hands inspecting a gift card"),
   ("After", "Keep the receipt with the card. If the balance is empty, call the card company right away.",
             "Keep the receipt", "a receipt stapled to a gift card"),
  ]),
 dict(date="2026-12-16", day="Wed", time="19:30", kind="carousel", topic="delivery", pillar=P_TEXT,
  title="Last shipping week: 4 delivery scam texts and the 1 safe way to track",
  hook="4 delivery texts you'll get before Christmas, and 1 safe way to track every package.",
  thumb="4 fake delivery texts",
  hashtags=["deliveryscam", "packagescam", "christmasshopping", "smishing", "scamdecoded"],
  description="Four fake delivery messages that spike in the last shipping week, and how to track packages safely.",
  caption="The last shipping week is peak season for fake delivery texts:\n1. 'Package on hold'\n2. 'Redelivery fee'\n"
          "3. 'Customs charge'\n4. 'Missed delivery, reschedule'\nThe safe way: track from the shop's own email or app.\n\n" + CHECKER,
  sources=[DELIV, SHIP, SPAM], claims=["Fake delivery notices increase around the holidays (FTC)",
                                       "Carriers don't text you links to pay fees unless you signed up for alerts for that package"],
  original_element="Slide 5 is a screenshot of the Scam Decoded checker flagging the slide 1 text (take it on the live site).",
  segments=slides("4 fake delivery texts", [
   ("'Your package is on hold. Update your address within 12 hours.' A countdown and a link.", "1. 'On hold'", "a parcel with a clock"),
   ("'A small redelivery fee applies.' The fee is the bait. They want your card number.", "2. 'Redelivery fee'", "a parcel with a coin"),
   ("'Customs charge due before release.' For a gift that never left the country.", "3. 'Customs charge'", "a parcel with a stamp"),
   ("'We missed you. Reschedule here.' A link to a page that asks for your details.", "4. 'Missed you'", "a door with a note"),
  ], "The safe way: track with the number in the shop's own order email or app. Forward fakes to 7726.",
     f"{MASCOT} holding a phone with a tracking map")),
]


def item(p):
    fmt = {"short": "short", "tiktok": "short", "carousel": "carousel"}[p["kind"]]
    platforms = {"short": ["instagram", "youtube"], "tiktok": ["tiktok"], "carousel": ["instagram"]}[p["kind"]]
    cta = CTA_TIKTOK if p["kind"] == "tiktok" else CTA
    caption = p["caption"] if CHECKER in p["caption"] else p["caption"] + "\n\n" + CHECKER
    return {"format": fmt, "pillar": p["pillar"], "platforms": platforms, "post_on": f"{p['date']} {p['time']}",
            "topic": p["topic"], "original_element": p["original_element"],
            "idea_angle": f"Holiday 2026 pack: {p['topic']}. {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": segs(p["segments"]), "cta": cta,
                       "caption": caption + "\n\n" + cta, "hashtags": p["hashtags"], "description": p["description"],
                       "thumbnail_text": p["thumb"], "sources": p["sources"], "claims_to_verify": p["claims"]}}


def plan(items):
    rows = ["# Scam Decoded: holiday scam pack, Nov 9 – Dec 16 2026", "",
            "10 posts on the four holiday scams: package delivery texts, fake charities, gift cards and marketplace scams. "
            "Times America/New_York. Nothing has been posted; Dhruv posts each by hand.", "",
            "Formats rotate (Short, carousel, TikTok minute cut), so no two posts in a row look alike. Every caption points "
            "to the free in-browser scam checker on the site (link in bio). Newsletter issues 1 (Thu Nov 19) and 2 "
            "(Thu Dec 3) cover the same topics.", "",
            "| # | Date | Time | Where | Format | Topic | Title | Original element |", "|---|---|---|---|---|---|---|---|"]
    for n, (p, i) in enumerate(zip(POSTS, items)):
        where = {"short": "Reels + Shorts", "tiktok": "TikTok", "carousel": "Instagram"}[p["kind"]]
        fmt = {"short": "Short", "tiktok": "TikTok minute cut", "carousel": "Carousel"}[p["kind"]]
        rows.append(f"| #{n} | {p['day']} {p['date'][5:]} | {p['time']} | {where} | {fmt} | {p['topic']} | "
                    f"{p['title']} | {p['original_element']} |")
    rows += ["", "Key dates: Black Friday Nov 27, Cyber Monday Nov 30, Giving Tuesday Dec 1. Check the carriers' "
             "published holiday shipping deadlines before the Dec 16 post and add the real date to the caption.", "",
             "Before posting: verify each item's `claims_to_verify` against its `sources`, record voiceovers (TikTok "
             "cuts in Dhruv's own voice), and set the bio link to the site's /checker/ page."]
    return "\n".join(rows) + "\n"


def main():
    items = [item(p) for p in POSTS]
    root = HERE.parent.parent
    (root / "holiday-2026.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (root / "POSTING_PLAN_HOLIDAY_2026.md").write_text(plan(items))
    for n, i in enumerate(items):
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        hook = i["script"]["hook"]
        assert any(ch.isdigit() for ch in hook.split(".")[0][:60]), hook
        print(n, i["format"], i["platforms"], w, i["script"]["title"])


if __name__ == "__main__":
    main()
