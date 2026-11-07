"""10 Shorts cut from Scam Alert newsletter issues, for Instagram Reels and TikTok.

    python3 build.py   ->  ../../newsletter-cuts.json and ../../POSTING_PLAN_NEWSLETTER_CUTS.md

Each cut posts at 20:00 on its issue's send date (a time no other plan uses), so the email and the video land the
same evening. 5 hashtags max (Instagram's cap), an original element in every cut, Dhruv's own voice.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, MASCOT, P_FAMILY, P_ID, P_INVEST, P_TEXT, seg  # noqa: E402

ROOT = HERE.parent.parent
NEWS = ROOT.parent.parent / "sites" / "scam-decoded" / "content" / "newsletter"
VOICE = "Dhruv's own voice, no AI voice."
PLUG = ("This is from this week's free Scam Alert email, one scam a week (link in bio). Not sure about a message? "
        "Paste it into our free scam checker.")
FTC = "https://consumer.ftc.gov/articles/how-avoid-scam"

CUTS = [
 dict(issue=6, look="face cam", pillar=P_TEXT,
  title="'$389.99 renewed, call to cancel': check your bank app",
  hook="1 email says $389.99 was just charged for a plan you don't remember. Check your bank app, not the number.",
  thumb="$389.99 'renewed'? Check first.", hashtags=["scamalert", "phishing", "autorenewal", "newyear", "scamdecoded"],
  caption="A fake renewal email wants you to call about a charge that never happened. The call is where it goes wrong.",
  sources=["https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams", FTC],
  claims=["Scammers send fake renewal or invoice emails to get people to call them (FTC)"],
  original_element="Dhruv on camera holding his phone, opening his own bank app (balance blurred) to show the charge "
                   "isn't there. " + VOICE,
  segs=[("Hook", "One email. Your annual protection plan renewed, three hundred eighty-nine ninety-nine charged. Call "
                 "within forty-eight hours to cancel.", "'$389.99 charged'", "Dhruv on camera holding a phone"),
        ("The catch", "The call goes to a fake support team. To 'refund' you, they ask to connect to your computer, or "
                      "for your bank login.", "The call is the trap", "a phone with a headset icon"),
        ("The check", "Open your bank app and look. No charge? It's fake. A real charge? Call the number on your card, "
                      "not the email.", "Check your bank app", "Dhruv's phone: bank app, blurred"),
        ("Do this", "Delete the email. Never let a caller connect to your computer to process a refund.",
         "No remote access for refunds", f"{MASCOT} with a stop hand")]),
 dict(issue=7, look="walkthrough", pillar=P_TEXT,
  title="'Confirm your card for your $84.50 refund': 1 fake text",
  hook="1 text says your $84.50 return is stuck. Real refunds don't need your card number again.",
  thumb="Stuck refund? Not real.", hashtags=["scamalert", "returns", "textscam", "onlineshopping", "scamdecoded"],
  caption="After the holidays come the returns, and the fake 'refund failed' texts. Here's the tell.",
  sources=["https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams", FTC],
  claims=["Scammers send texts posing as stores or delivery companies to steal card details (FTC)"],
  original_element="Walkthrough of the newsletter's fictional text on a phone mockup, flags lighting up one by one. " + VOICE,
  segs=[("Hook", "One text. Your return couldn't be processed. To receive your eighty-four fifty, confirm your card "
                 "details within twenty-four hours.", "'Confirm your card'", "walkthrough: the refund text"),
        ("Flag 1", "A refund goes back to the card you paid with. It never needs your card number again.",
         "Refunds don't need your card", "walkthrough: flag 1 lit"),
        ("Flag 2", "A twenty-four-hour deadline, and a link that isn't the store's website. Two more flags.",
         "Deadline + odd link", "walkthrough: flags 2 and 3 lit"),
        ("Do this", "Check the return in the store's own app or account. Typed your card? Call your bank today.",
         "Check in the store's app", f"{MASCOT} holding a receipt")]),
 dict(issue=9, look="quiz pause", pillar=P_INVEST,
  title="'Hi Emma, still on for dinner?' 1 wrong number to block",
  hook="1 wrong-number text, then 'you seem nice'. Pause: reply, block, or ignore?",
  thumb="Wrong number? Pause.", hashtags=["scamalert", "wrongnumber", "cryptoscam", "textscam", "scamdecoded"],
  caption="The friendliest text you'll get this month, and the start of many crypto investment scams.",
  sources=["https://www.justice.gov/opa/pr/chairman-prince-group-indicted-operating-cambodian-forced-labor-scam-compounds-engaged",
           "https://consumer.ftc.gov/articles/what-know-about-cryptocurrency-scams"],
  claims=["Crypto investment scams often start with friendly messages that build trust over time (DOJ, FTC)"],
  original_element="Quiz format with a real 3-second pause card; the answer beat shows the newsletter's archive page "
                   "on Dhruv's phone. " + VOICE,
  segs=[("Hook", "Hi Emma, are we still on for dinner Saturday? Oh sorry, wrong number. You seem nice though.",
         "'Wrong number! You seem nice'", "a text bubble on a phone"),
        ("Pause", "Pause. Reply, block, or ignore? Pick one.", "Pause: reply, block or ignore?", "a full-screen countdown card"),
        ("Answer", "Block and delete. A friendly reply starts weeks of chat, then a crypto app where your money can't "
                   "come out. Federal prosecutors say messages like this can come from scam compounds.",
         "Block. Don't chat.", "a phone with a block button"),
        ("Do this", "Never invest on an app someone you met by text recommends. Not once, not a little.",
         "No apps from text 'friends'", f"{MASCOT} with a shield")]),
 dict(issue=12, look="illustrated", pillar=P_FAMILY,
  title="'Send a photo of the back of the gift cards': it's a scam",
  hook="1 photo of the back of a gift card is all a romance scammer needs. Here's the ask.",
  thumb="Back of the card? No.", hashtags=["scamalert", "romancescam", "giftcards", "valentinesday", "scamdecoded"],
  caption="'My card isn't working out here. Could you grab 3 gift cards and send me a photo of the backs?' That's the "
          "whole scam.",
  sources=["https://consumer.ftc.gov/articles/what-know-about-romance-scams", "https://consumer.ftc.gov/consumer-alerts/2024/10/only-scammers-tell-you-buy-gift-card-pay-them"],
  claims=["Romance scammers ask for gift cards and the numbers on the back (FTC)"],
  original_element="Illustrated beats; the closing beat is Dhruv's hand covering the back of a real gift card. " + VOICE,
  segs=[("Hook", "One message. Babe, my card isn't working out here. Could you grab three gift cards and send me a "
                 "photo of the backs?", "'Send a photo of the backs'", f"{MASCOT} holding a gift card"),
        ("The catch", "The numbers on the back are the money. Once they have the photo, the cards are drained in "
                      "minutes.", "The back is the money", "a gift card with a timer"),
        ("The tell", "Someone you haven't met in person, asking for gift cards. That's never love. It's always the scam.",
         "Gift cards = scam", "a heart with a crack"),
        ("Do this", "Don't send it. Already did? Call the gift card company on the number on the card, right now.",
         "Sent it? Call the card company.", "a hand covering the back of a card")]),
 dict(issue=17, look="screen recording", pillar=P_ID,
  title="'Loan forgiveness approved, $499 fee': 0 fees to apply",
  hook="$499 to apply for student loan forgiveness? Applying is free, and here's the screen.",
  thumb="Forgiveness for $499? No.", hashtags=["scamalert", "studentloans", "studentloanforgiveness", "fsa", "scamdecoded"],
  caption="Student loan help is free at StudentAid.gov. A fee, or a request for your FSA ID, is the scam.",
  sources=["https://consumer.ftc.gov/consumer-alerts/2025/05/spotting-student-loan-scams",
           "https://consumer.ftc.gov/articles/paying-school-and-avoiding-scams"],
  claims=["You never have to pay for help with federal student loans; apply free at StudentAid.gov (FTC)",
          "Never share your FSA ID (FTC)"],
  original_element="Dhruv screen-records StudentAid.gov's sign-in page and its scam warning page on his own phone. " + VOICE,
  segs=[("Hook", "Final notice. You've been approved for student loan forgiveness. One-time enrollment fee, four "
                 "hundred ninety-nine dollars.", "'$499 enrollment fee'", "Dhruv's screen: the text"),
        ("The catch", "They take the fee, and ask for your F S A I D to 'manage' your account. Then they change the "
                      "contact details.", "They want your FSA ID", "a key with a red X"),
        ("The real screen", "Here's Student Aid dot gov. Applying for repayment plans and forgiveness is free, right "
                            "here.", "StudentAid.gov: free", "Dhruv's screen: StudentAid.gov"),
        ("Do this", "Never pay to apply, never share your F S A I D, and check your contact details tonight.",
         "No fees. No FSA ID sharing.", f"{MASCOT} with a graduation cap")]),
 dict(issue=18, look="face cam", pillar=P_TEXT,
  title="A friend got a $9,000 grant? 1 call before you reply",
  hook="1 message from a friend about a $9,000 grant. Call her first. Her account was probably hacked.",
  thumb="Friend's grant? Call her.", hashtags=["scamalert", "grantscam", "hackedaccount", "facebook", "scamdecoded"],
  caption="Free government money with a $250 'delivery fee', sent from a friend's account. It's not your friend.",
  sources=["https://consumer.ftc.gov/articles/government-grant-scams",
           "https://consumer.ftc.gov/consumer-alerts/2026/03/how-avoid-government-grant-scams-offer-free-money-personal-expenses"],
  claims=["The government doesn't charge fees to receive a grant (FTC)",
          "Scammers use hacked social media accounts to message friends (FTC)"],
  original_element="Dhruv on camera calling a friend (who agreed to be filmed) to check a message, on speaker. " + VOICE,
  segs=[("Hook", "One message from a friend. I just got nine thousand dollars from a government grant, and your name "
                 "is on the list too.", "'Your name is on the list'", "Dhruv on camera holding a phone"),
        ("The catch", "The agent wants a two hundred fifty dollar delivery fee. Then taxes. The grant never comes.",
         "Fee, then more fees", "a pile of bills with a padlock"),
        ("The check", "Call your friend on the number you already have. Watch, I'm calling mine now.",
         "Call the friend", "Dhruv on a speakerphone call"),
        ("Do this", "Free money never has a fee. Report the account, and turn on two-step sign-in on yours.",
         "Free money has no fee", f"{MASCOT} with a phone")]),
 dict(issue=19, look="walkthrough", pillar=P_TEXT,
  title="IRS letter says call in 10 days? 1 number to look up",
  hook="1 letter, an eagle, a case number and 10 days to call. Check the number before you dial.",
  thumb="Fake IRS letter? Check.", hashtags=["scamalert", "irs", "taxseason", "irsletter", "scamdecoded"],
  caption="Scammers mail fake IRS letters too. The phone number is the one thing they can't copy.",
  sources=["https://www.irs.gov/help/how-to-know-its-the-irs", "https://www.irs.gov/help/tax-scams/recognize-tax-scams-and-fraud"],
  claims=["The IRS generally contacts people by mail first; scammers send fake letters too (IRS)",
          "Check any balance in your IRS Online Account (IRS)"],
  original_element="Walkthrough over a fictional letter (marked SAMPLE) with the notice number and phone number circled. " + VOICE,
  segs=[("Hook", "Notice of intent to levy. Balance four thousand one hundred eighteen dollars. Call our Resolution "
                 "Department within ten days.", "'Call within 10 days'", "walkthrough: a sample letter"),
        ("The catch", "The number goes to the scammer, who 'settles' your debt by payment app, gift card or wire.",
         "The number is the trap", "walkthrough: phone number circled"),
        ("The check", "Look up the notice number on I R S dot gov, and check your balance in your IRS online account.",
         "Check your IRS account", "walkthrough: notice number circled"),
        ("Do this", "Need to call? Use the number on I R S dot gov, never the one on the letter.",
         "Call the IRS.gov number", f"{MASCOT} with an envelope")]),
 dict(issue=21, look="quiz pause", pillar=P_TEXT,
  title="'Your refund needs an adjustment': real IRS text or fake?",
  hook="1 text says your $1,284 refund needs an adjustment. Pause: real or fake?",
  thumb="Refund 'adjustment'? Pause.", hashtags=["scamalert", "taxrefund", "irs", "qrcode", "scamdecoded"],
  caption="You filed. Now come the refund texts. There's one place to check a refund.",
  sources=["https://www.irs.gov/help/report-fraud/report-fake-irs-treasury-or-tax-related-emails-and-messages",
           "https://www.irs.gov/refunds"],
  claims=["The IRS doesn't start contact about refunds by text (IRS)", "Check refunds at IRS.gov/refunds (IRS)"],
  original_element="Quiz format; the answer beat is Dhruv typing IRS.gov/refunds into his own browser. " + VOICE,
  segs=[("Hook", "IRS: your refund of twelve eighty-four requires an adjustment before release. Scan the code within "
                 "forty-eight hours.", "'Requires an adjustment'", "a phone with a QR code"),
        ("Pause", "Pause. Real or fake? Decide.", "Pause: real or fake?", "a full-screen countdown card"),
        ("Answer", "Fake. The IRS doesn't text about your refund, and refunds don't expire in forty-eight hours. The "
                   "code leads to a page that asks for your Social Security number and bank details.",
         "Fake. Every time.", "a QR code with a red X"),
        ("Do this", "Check your refund only at I R S dot gov slash refunds, typed yourself. Forward the text to seven "
                    "seven two six.", "IRS.gov/refunds only", "Dhruv typing in a browser")]),
 dict(issue=24, look="illustrated", pillar=P_FAMILY,
  title="'My lawyer will send someone for the bail': don't open",
  hook="1 call, 1 'lawyer', and 1 courier at Grandma's door. That's the newest grandparent scam.",
  thumb="Courier for 'bail'? No.", hashtags=["scamalert", "grandparentscam", "mothersday", "elderfraud", "scamdecoded"],
  caption="A grandchild in trouble, a lawyer, and someone coming to the house for cash. Real courts don't send couriers.",
  sources=["https://www.justice.gov/usao-vt/pr/25-canadian-nationals-charged-vermont-connection-nationwide-multimillion-dollar",
           "https://consumer.ftc.gov/articles/scammers-use-fake-emergencies-steal-your-money"],
  claims=["Prosecutors allege a grandparent scam network sent fake 'bail bondsmen' to collect cash at victims' homes (DOJ, 2025)"],
  original_element="Illustrated beats; the closing beat shows our case board from 'How the scam actually worked' part 1. " + VOICE,
  segs=[("Hook", "Grandma, it's me. I was in an accident. Please don't tell Mom. My lawyer will send someone for the "
                 "bail money.", "'Don't tell Mom'", f"{MASCOT} next to a ringing phone"),
        ("The catch", "A fake lawyer names the amount. Then a 'bail bondsman' knocks on the door to collect cash.",
         "A courier at the door", "a door with a shadow"),
        ("The tell", "No court or lawyer sends a stranger to your house for cash. And 'don't tell anyone' is the scam "
                     "talking.", "Courts don't send couriers", "a courthouse with a red X"),
        ("Do this", "Hang up and call the grandchild on the number you have. Someone coming to the door? Call the police.",
         "Call back. Then the police.", "the case board, part 1")]),
 dict(issue=27, look="screen recording", pillar=P_TEXT,
  title="'Flight canceled, call to rebook': check the app first",
  hook="1 text says your flight is canceled. Open the airline app before you call anyone. Here's mine.",
  thumb="Canceled? Check the app.", hashtags=["scamalert", "travel", "flightcanceled", "summertravel", "scamdecoded"],
  caption="Fake cancellation texts send you to a fake agent who charges to rebook. The airline app tells the truth.",
  sources=["https://consumer.ftc.gov/consumer-alerts/2024/07/scammers-impersonate-airline-customer-service-representatives"],
  claims=["Scammers impersonate airline customer service by text, search ads and social media (FTC)"],
  original_element="Dhruv screen-records his own airline app's trips page (booking details blurred). " + VOICE,
  segs=[("Hook", "Your flight has been canceled due to a schedule change. To rebook at no cost, call our support line.",
         "'Call to rebook'", "Dhruv's screen: the text"),
        ("The catch", "The number goes to a fake agent who charges a rebooking fee, and takes your card and your "
                      "frequent flyer login.", "A fake agent, a real fee", "a headset with a price tag"),
        ("The check", "Here's my airline app. Trips, my flight, still on time. Real changes show up here first.",
         "Check the airline app", "Dhruv's screen: trips page, blurred"),
        ("Do this", "Need help? Use the number in the app or on the airline's own website.",
         "Use the app's number", f"{MASCOT} with a suitcase")]),
]


def issue_meta(n):
    f = next(NEWS.glob(f"{n:02d}-*.md"))
    head = f.read_text().split("---")[1]
    meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
    return meta, f.stem.split("-", 1)[1]


def item(c):
    meta, slug = issue_meta(c["issue"])
    return {"format": "short", "pillar": c["pillar"], "platforms": ["instagram", "tiktok"],
            "post_on": f"{meta['send_date']} 20:00", "look": c["look"], "newsletter_issue": c["issue"],
            "original_element": c["original_element"],
            "idea_angle": f"Cut from Scam Alert #{c['issue']} ({meta['subject'].split(': ', 1)[1]})",
            "script": {"title": c["title"], "hook": c["hook"], "segments": [seg(*r) for r in c["segs"]], "cta": CTA,
                       "caption": c["caption"] + "\n\n" + PLUG + "\n\n" + CTA, "hashtags": c["hashtags"],
                       "description": f"From Scam Alert #{c['issue']}: https://scamdecoded.netlify.app/newsletter/{slug}/",
                       "thumbnail_text": c["thumb"], "sources": c["sources"], "claims_to_verify": c["claims"]}}


def main():
    items = [item(c) for c in CUTS]
    assert all(a["look"] != b["look"] for a, b in zip(items, items[1:]))
    for i in items:
        sc = i["script"]
        w = sum(len(s["narration"].split()) for s in sc["segments"])
        assert 60 <= w <= 120, (sc["title"], w)
        assert len(sc["hashtags"]) <= 5 and any(ch.isdigit() for ch in sc["hook"].split(".")[0][:60]), sc["title"]
        assert all(len(s["on_screen_text"].split()) <= 12 for s in sc["segments"])
    (ROOT / "newsletter-cuts.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    rows = ["# Scam Decoded: 10 Shorts cut from the Scam Alert newsletter", "",
            "Instagram Reels + TikTok, 20:00 America/New_York on each issue's send date (a time no other plan uses), so "
            "the email and the video land the same evening. 5 hashtags each (Instagram's cap). Every cut has its own "
            "original element and Dhruv's own voice. Nothing has been posted.", "",
            "| # | Date | Issue | Look | Title |", "|---|---|---|---|---|"]
    for n, i in enumerate(items):
        d = dt.date.fromisoformat(i["post_on"][:10])
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} {d.year} | #{i['newsletter_issue']} | {i['look']} | "
                    f"{i['script']['title']} |")
    rows += ["", "Before posting: verify each `claims_to_verify` against its `sources`, and check the issue numbers "
             "still match the newsletter (they were renumbered once on Nov 7 2026)."]
    (ROOT / "POSTING_PLAN_NEWSLETTER_CUTS.md").write_text("\n".join(rows) + "\n")
    for n, i in enumerate(items):
        print(n, i["post_on"], i["look"], sum(len(s["narration"].split()) for s in i["script"]["segments"]),
              i["script"]["title"][:60])


if __name__ == "__main__":
    main()
