"""Holiday scam season pack, Tue Nov 24 - Thu Dec 31 2026: the holiday scams the other plans don't cover yet.

    python3 build.py   ->  ../../holiday-season-2026.json and ../../POSTING_PLAN_HOLIDAY_SEASON_2026.md

6 Shorts on Tuesdays at 12:00 and 4 carousels on Thursdays at 12:00, the two weekday slots the weekly plans and
the earlier holiday pack leave open. Delivery texts, gift card draining, charities, marketplace, tickets and puppies
are already covered (weeks 3-6, holiday-2026), so this pack takes the rest of BBB's 2026 '12 scams of the holidays'
plus the FTC's holiday job and unordered-package alerts. Every post cites a public FTC or BBB page.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, MASCOT, seg  # noqa: E402

BBB12 = "https://www.bbb.org/all/holiday-hq/scams/12-scams-of-christmas"
SISTER = "https://www.bbb.org/all/holiday-hq/scams/secret-sister-gift-exchange-is-illegal"
ADVENT = "https://www.bbb.org/all/holiday-hq/scams/social-media-advent-calendar-scams"
JOBS = "https://consumer.ftc.gov/consumer-alerts/2023/12/spot-holiday-job-scams"
JOBS_FTC = "https://consumer.ftc.gov/articles/job-scams"
QR_PKG = "https://consumer.ftc.gov/consumer-alerts/2025/01/scam-alert-qr-code-unexpected-package"
UNORDERED = ("https://consumer.ftc.gov/articles/"
             "what-do-if-youre-billed-things-you-never-got-or-you-get-unordered-products")
NOT_ORDERED = "https://consumer.ftc.gov/consumer-alerts/2023/11/so-online-scam-not-what-you-ordered"
REPORT = "https://reportfraud.ftc.gov/"
CHECKER = "Not sure about a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends nothing anywhere."
P = "holiday scams"
SEASON = "holiday scam season 2026"


def slides(cover, items, save, cover_vis):
    out = [("Hook", "", cover, cover_vis)]
    out += [(str(i), n, o, v) for i, (n, o, v) in enumerate(items, 1)]
    out.append(("Save this", save, "Save it. Send it to the group chat.", f"{MASCOT} giving a thumbs up"))
    return out


POSTS = [
 dict(date="2026-11-24", kind="short", look="illustrated", topic="gift exchange", pillar=P,
  title="'Send 1 gift, get 36 back': the Secret Santa chain",
  hook="1 gift in, 36 gifts back. That's the promise of the social media gift exchange.",
  thumb="It's a pyramid",
  hashtags=["secretsanta", "giftexchange", "holidayscams", "pyramidscheme", "scamdecoded"],
  description="Why the viral holiday gift exchange is a pyramid scheme, according to BBB.",
  caption="The 'Secret Sister' or Secret Santa exchange on social media sounds harmless: buy one gift, get dozens back. "
          "BBB calls it a pyramid scheme, and the Postal Inspection Service treats these as illegal gambling.",
  sources=[SISTER, BBB12],
  claims=["BBB classifies the social media gift exchange as a pyramid scheme (BBB)",
          "The US Postal Inspection Service describes these exchanges as gambling, with possible penalties (cited by BBB)"],
  original_element="Illustrated beats; Dhruv adds a 5-second face-cam close reading the invite's '36 gifts' line aloud.",
  segments=[
   ("Hook", "One post in your feed: send a single gift to a stranger, add your name to the list, and up to thirty-six "
            "gifts come back to you.", "Send 1 gift. Get 36?", f"{MASCOT} holding one small present"),
   ("How it works", "You mail a gift to the name at the top, then recruit friends to do the same. It only pays the people "
                    "near the top, and only while new people keep joining.", "Only the top of the list wins",
    "a pyramid of tiny gift boxes"),
   ("Why it's a problem", "BBB calls it a pyramid scheme, and says the Postal Inspection Service treats these exchanges "
                          "as illegal gambling. You also hand your home address to strangers.",
    "BBB: it's a pyramid scheme", "an envelope with a home address showing"),
   ("Do this", "Skip it, and report the post to the platform. Want a gift swap? Do one with people you actually know.",
    "Swap with people you know", f"{MASCOT} with friends around a tree"),
  ]),
 dict(date="2026-11-26", kind="carousel", look="checklist", topic="fake shops", pillar=P,
  title="Advent calendar ads that never ship: 4 checks before you pay",
  hook="4 checks before you buy that themed advent calendar from a social media ad.",
  thumb="Advent ad? 4 checks",
  hashtags=["adventcalendar", "onlineshopping", "holidayscams", "fakestores", "scamdecoded"],
  description="BBB's warning about advent calendar ads on social media, as a 4-step checklist.",
  caption="Themed advent calendars are everywhere in ads right now. BBB warns that many of the sellers behind those ads "
          "take the money and never ship. 4 checks before you pay.",
  sources=[ADVENT, BBB12],
  claims=["BBB warns advent calendar ads lead to sites that take payment and never ship, or ship something different",
          "Buyers may get a tracking number that leads nowhere (BBB)"],
  original_element="Slide 2 is a screen recording Dhruv makes of searching a made-up shop name plus 'complaints' (no real shop named).",
  segments=slides("Advent ad? 4 checks", [
   ("Leave the app and type the brand's own website. A link inside the ad can hide where it really goes.",
    "1. Go to the brand's own site", "a phone leaving a social app for a browser"),
   ("Search the shop's name with 'complaints' or 'scam'. If people say nothing arrived, stop there.",
    "2. Search the name + 'complaints'", "a magnifying glass over a shop sign"),
   ("A big box of famous treats at a tiny price is the hook. BBB says too-good gifts at low prices usually are.",
    "3. Tiny price, big box = no", "an advent calendar with a price tag crossed out"),
   ("Pay by credit card, so you can dispute it if nothing comes, or if the box isn't what the ad showed.",
    "4. Credit card only", "a credit card with a shield"),
  ], "Save this for the next ad that looks too good.", f"{MASCOT} with an advent calendar")),
 dict(date="2026-12-01", kind="short", look="face cam", topic="holiday jobs", pillar=P,
  title="Holiday warehouse job by text? 1 fee means walk away",
  hook="1 fee before your first shift is all it takes to spot a fake holiday job.",
  thumb="Pay to work? No.",
  hashtags=["holidayjobs", "jobscams", "seasonaljobs", "holidayscams", "scamdecoded"],
  description="The FTC's rule for holiday job offers: anyone who asks you to pay to get a job is a scammer.",
  caption="Seasonal jobs are real, and so are the fake ones that copy them. The FTC's rule is simple: an employer who "
          "asks you to pay to get the job is a scammer.",
  sources=[JOBS, JOBS_FTC, BBB12],
  claims=["The FTC says anyone who asks you to pay to get a job is a scammer",
          "BBB lists fake temporary holiday jobs, with text-only interviews and training fees, among its 12 holiday scams"],
  original_element="Face cam: Dhruv reads a made-up job text from his phone, then says the rule to camera.",
  segments=[
   ("Hook", "One text: holiday warehouse job, twenty-two dollars an hour, interview today by chat.",
    "$22/hr, interview by chat", f"{MASCOT} reading a phone"),
   ("The ask", "You're hired in an hour. Now pay forty-nine dollars for safety training, or buy your uniform from our "
               "vendor, or send your bank login for direct deposit.", "Then: pay for training", "a fee notice on a phone"),
   ("The rule", "The FTC is blunt about it: anyone who asks you to pay to get a job is a scammer. Real employers pay "
                "you, not the other way round.", "FTC: pay to get a job = scam", "a scale tipping toward a paycheck"),
   ("Do this", "Find the company's real careers page yourself and apply there. Never pay a fee or send a bank login to "
               "get hired.", "Apply on the real careers page", f"{MASCOT} at a laptop"),
  ]),
 dict(date="2026-12-08", kind="short", look="walkthrough", topic="free gift cards", pillar=P,
  title="'Your points expire tonight': 1 text to check in the app",
  hook="1 text says your reward points expire tonight. Here's what happens if you tap it.",
  thumb="Points expiring? Check the app",
  hashtags=["rewardpoints", "giftcardscam", "phishing", "holidayscams", "scamdecoded"],
  description="BBB's warning about fake free gift card and expiring points messages, as a walkthrough.",
  caption="Free gift cards and 'your points expire tonight' messages copy real brands. BBB says they lead to pages "
          "that collect your login or card. Open the brand's own app instead.",
  sources=[BBB12],
  claims=["BBB warns messages posing as brands offer free gift cards or say points are expiring, and link to pages that "
          "harvest logins or payment details"],
  original_element="Phone-screen walkthrough mockup (originality/render.mjs style): the text, the fake login page, then the real app.",
  segments=[
   ("Hook", "One text from a store you shop at: you have twelve thousand points, worth sixty dollars, expiring tonight.",
    "12,000 points expire tonight", "a phone with a reward text"),
   ("The page", "The link opens a login page in the store's colors. Type your password, and the next screen asks for "
                "your card to 'cover shipping' on your reward.", "Then: login, then card", "a fake login page"),
   ("The tell", "Real points live in the store's own app or account. A deadline in a text, plus a link, is how BBB "
                "says these phishing pages get your details.", "Points live in the real app", "an app icon with a star"),
   ("Do this", "Don't tap. Open the store's app yourself and check your points there. Then delete the text.",
    "Check the app. Delete the text.", f"{MASCOT} deleting a message"),
  ]),
 dict(date="2026-12-10", kind="carousel", look="quiz", topic="holiday jobs", pillar=P,
  title="Spot the red flags: the 'seasonal delivery driver' offer",
  hook="5 red flags in 1 holiday job offer. Find them before you swipe.",
  thumb="Find 5 red flags",
  hashtags=["holidayjobs", "jobscams", "spotthescam", "seasonaljobs", "scamdecoded"],
  description="A quiz carousel: five red flags in a fake seasonal delivery job, from the FTC's holiday job alert.",
  caption="A made-up seasonal driver offer with 5 red flags from the FTC's holiday job alert. Count them, then swipe.",
  sources=[JOBS, JOBS_FTC],
  claims=["The FTC warns fake employers move quickly to an offer and ask for sensitive data like license or bank numbers",
          "The FTC advises contacting the company using contact details you already know are real"],
  original_element="Rendered quiz carousel in the q-series style: the offer on slide 1, one flag circled per slide.",
  segments=slides("Find 5 red flags", [
   ("Hired with no interview, the same hour you applied. The FTC says scammers move fast to an offer.",
    "1. Hired in an hour", "a stopwatch next to a job offer"),
   ("They want your driver's license photo and bank number for 'paperwork' before any real offer letter.",
    "2. ID and bank details first", "an ID card and a bank card on a form"),
   ("A 'starter kit' fee for the vest and scanner. Real employers don't charge you to start.",
    "3. A starter kit fee", "a delivery vest with a price tag"),
   ("The contact is a chat app number, not the company's own email or careers site.",
    "4. Chat app only", "a chat bubble with no company name"),
   ("The pay is far above what the same job pays everywhere else.",
    "5. Pay too good to be real", "a paycheck with an extra zero"),
  ], "Save this for anyone job hunting this month.", f"{MASCOT} holding a magnifying glass")),
 dict(date="2026-12-15", kind="short", look="data chart", topic="unordered packages", pillar=P,
  title="A gift with no sender and a QR code: 1 thing not to scan",
  hook="1 package you didn't order, 1 note, 1 QR code. Don't scan it.",
  thumb="Mystery gift? Don't scan",
  hashtags=["brushingscam", "qrcode", "packages", "holidayscams", "scamdecoded"],
  description="The FTC's warning about unexpected packages with a QR code to 'find out who sent it'.",
  caption="An unexpected package with a note: scan this to see who sent your gift. The FTC says that QR code can lead "
          "to a page that steals your details, or to malware. You can keep the package.",
  sources=[QR_PKG, UNORDERED],
  claims=["The FTC warns a QR code on an unexpected package can lead to a site that steals information or downloads malware",
          "The FTC says you can keep unordered merchandise as a gift"],
  original_element="A data-chart beat: three steps drawn as a simple flow (scan, fake page, stolen login), like originality/out/charts.",
  segments=[
   ("Hook", "One box on your step with your name on it. No sender. A note says: scan this code to find out who sent your "
            "gift.", "No sender. Scan to find out?", "a package with a QR code note"),
   ("The catch", "The FTC says that code can open a page that asks for your card or login, or put malware on your "
                 "phone. Curiosity is the bait.", "The code is the scam", "a phone with a warning icon"),
   ("The good news", "If you didn't order it, the FTC says you can keep it as a gift. You don't owe anyone for it, and "
                     "you don't have to scan anything.", "Didn't order it? It's yours", "an open box with a bow"),
   ("Do this", "Don't scan. If you already did and typed a password, change it now, and check your card and bank "
               "statements.", "Scanned? Change the password", f"{MASCOT} with a padlock"),
  ]),
 dict(date="2026-12-17", kind="carousel", look="myth vs fact", topic="unordered packages", pillar=P,
  title="Got a package you didn't order? 5 things to know",
  hook="5 things to know when a package you never ordered lands on your doorstep.",
  thumb="Didn't order it? 5 facts",
  hashtags=["brushingscam", "packages", "identitytheft", "holidayscams", "scamdecoded"],
  description="What brushing is, what to do, and what not to do, from the FTC.",
  caption="Unordered packages pick up in December. Usually it's a seller faking reviews in your name, which the FTC "
          "calls brushing. 5 things to know, and the one check worth doing.",
  sources=[QR_PKG, UNORDERED],
  claims=["The FTC says you can keep unordered products as a gift and have no obligation to pay",
          "The FTC suggests checking your credit report at AnnualCreditReport.com and your statements if your details may be exposed"],
  original_element="Slide 5 is a screenshot Dhruv takes of the AnnualCreditReport.com home page, reached by typing the address.",
  segments=slides("Didn't order it? 5 facts", [
   ("Myth: you have to send it back. Fact: the FTC says unordered products are yours to keep, and you owe nothing.",
    "1. You can keep it", "a package with a gift tag"),
   ("Myth: someone made a mistake. Fact: often a seller is using your name and address to post fake 'verified' reviews.",
    "2. It may be fake reviews", "a five-star review with your name"),
   ("Myth: scan the note to find the sender. Fact: the FTC warns that QR code can steal your details.",
    "3. Don't scan the code", "a QR code crossed out"),
   ("Myth: a bill is coming. Fact: if one does arrive for unordered goods, you don't have to pay it.",
    "4. No bill to pay", "an invoice with a no sign"),
   ("Worth doing: pull your free credit report and check your statements, since someone has your name and address.",
    "5. Check your credit report", "a credit report with a magnifying glass"),
  ], "Save this for the next mystery box.", f"{MASCOT} opening a box carefully")),
 dict(date="2026-12-22", kind="short", look="quiz pause", topic="counterfeit gifts", pillar=P,
  title="The sold-out toy at 60% off: 1 deal to skip",
  hook="1 sold-out toy, 60% off, and the seller will ship today. Pause: real or not?",
  thumb="Sold out? Then why 60% off?",
  hashtags=["christmasshopping", "counterfeit", "marketplace", "holidayscams", "scamdecoded"],
  description="BBB's warning about deep discounts on sold-out wish list items.",
  caption="The toy every kid wants is sold out everywhere, and a seller online has it at 60% off. BBB warns these are "
          "counterfeits or don't exist. One question to ask first.",
  sources=[BBB12, NOT_ORDERED],
  claims=["BBB warns resellers sell counterfeit hot toys, electronics and luxury goods, especially sold-out items at steep discounts",
          "The FTC advises paying by credit card and reporting to the payment company if what arrives isn't what you ordered"],
  original_element="A 3-second PAUSE card before the answer, quiz-style.",
  segments=[
   ("Hook", "One listing: the toy that's sold out in every store, sixty percent off, ships today. Pause. Real, or not?",
    "Sold out everywhere. 60% off here?", "a toy box with a big discount sticker"),
   ("Pause", "Pause. What would make you trust it?", "PAUSE", "a full-screen countdown card reading PAUSE"),
   ("The answer", "Not. BBB warns that deep discounts on sold-out wish list items are how counterfeit and never-shipped "
                  "gifts get sold, often on marketplace sites.", "BBB: deep discount + sold out = fake",
    "a counterfeit toy with mismatched colors"),
   ("Do this", "If it's sold out at the real stores, a stranger's bargain isn't the fix. Buy from the brand or a store "
               "you know, by credit card.", "Buy from a store you know", f"{MASCOT} with a shopping bag"),
  ]),
 dict(date="2026-12-29", kind="short", look="screen recording", topic="impostor support", pillar=P,
  title="Late order? 1 'support' reply to ignore",
  hook="1 public complaint about a late order, and 3 'support' accounts reply within minutes.",
  thumb="Fake support replies",
  hashtags=["customerservice", "impostorscam", "socialmedia", "holidayscams", "scamdecoded"],
  description="BBB's warning about fake brand support accounts on social media.",
  caption="Post about a missing order and fake 'support' accounts show up in the replies, asking you to DM your order "
          "number and card. BBB says find the brand's real handles on its own website.",
  sources=[BBB12],
  claims=["BBB warns scammers pose as brands with look-alike sites and fake customer support accounts on social media",
          "BBB advises finding official social handles on the company's own website"],
  original_element="Screen recording: Dhruv finds a big retailer's real support page by typing its address (no account shown).",
  segments=[
   ("Hook", "You post: my order never came. Within minutes, three accounts reply. Sorry to hear that, DM us your order "
            "number.", "'DM us your order number'", "a post with three reply bubbles"),
   ("The catch", "They use the brand's logo and a name one letter off. In the DM, they need your email, then your card "
                 "for a 'refund verification', then a code.", "Logo copied. Name one letter off",
    "two similar account names side by side"),
   ("The tell", "BBB says scammers pose as big brands' support on social media. Real support doesn't need your full "
                "card or a code to send a refund.", "Real support won't ask for a code",
    "a refund form with a lock"),
   ("Do this", "Don't DM replies. Go to the store's own website, typed in, and use the help page there.",
    "Use the help page on the real site", "a screen recording of a typed web address"),
  ]),
 dict(date="2026-12-31", kind="carousel", look="data", topic="season recap", pillar=P,
  title="12 holiday scams, 1 line each: the 2026 season recap",
  hook="12 scams BBB flagged this holiday season, each in 1 line, plus the 1 habit that beat most of them.",
  thumb="12 scams, 1 line each",
  hashtags=["holidayscams", "scamalert", "newyear", "staysafe", "scamdecoded"],
  description="A one-line-each recap of BBB's 12 holiday scams for 2026, ending with the habit that beats them.",
  caption="BBB's 12 holiday scams, one line each, as we head into the new year. Most fall to one habit: go to the source "
          "yourself instead of using their link, number or account.",
  sources=[BBB12, REPORT],
  claims=["The list is BBB's 12 scams of the holidays (2026 version)"],
  original_element="Slide 2 is a simple tally chart Dhruv draws of which of the 12 our own posts covered this season.",
  segments=slides("12 scams, 1 line each", [
   ("Ads with fake celebrity endorsements, gift card draining at the rack, and toll texts.",
    "1-3: ads, gift cards, tolls", "three small icons in a row"),
   ("Cloned voices of family, free gift card and points texts, and holiday jobs that charge you.",
    "4-6: voices, points, jobs", "a phone, a gift card, a name badge"),
   ("Brand impostors, fake charities, and fake shipping notices, plus brushing packages.",
    "7-9: impostors, charities, shipping", "a logo, a donation box, a parcel"),
   ("Holiday romance, sold-out wish list fakes, and puppies that don't exist.",
    "10-12: romance, fakes, puppies", "a heart, a toy, a puppy"),
   ("The habit that beats most of them: go to the source yourself, not through their link, number or reply.",
    "Go to the source yourself", f"{MASCOT} pointing at an address bar"),
  ], "Save this, and report anything you see at ReportFraud.ftc.gov.", f"{MASCOT} with confetti")),
]


def item(p):
    fmt = "carousel" if p["kind"] == "carousel" else "short"
    platforms = {"short": ["instagram", "youtube"], "carousel": ["instagram"]}[p["kind"]]
    return {"format": fmt, "pillar": p["pillar"], "platforms": platforms, "post_on": f"{p['date']} 12:00",
            "topic": p["topic"], "look": p["look"], "original_element": p["original_element"],
            "idea_angle": f"{SEASON}: {p['topic']}. {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": [seg(*r) for r in p["segments"]], "cta": CTA,
                       "caption": p["caption"] + "\n\n" + CHECKER + "\n\n" + CTA, "hashtags": p["hashtags"],
                       "description": p["description"], "thumbnail_text": p["thumb"], "sources": p["sources"],
                       "claims_to_verify": p["claims"]}}


def plan(items):
    rows = ["# Scam Decoded: holiday scam season pack, Tue Nov 24 – Thu Dec 31 2026", "",
            "10 posts: 6 Shorts (Reels + YouTube Shorts) on Tuesdays and 4 Instagram carousels on Thursdays, all at 12:00 "
            "America/New_York. Those two slots are free in the weekly plans and the earlier holiday pack. Nothing has "
            "been posted; Dhruv posts each by hand.", "",
            "Topics are the holiday scams the other plans don't cover yet: the gift exchange chain, advent calendar ads, "
            "holiday job offers, 'points expiring' texts, unordered packages with QR codes, sold-out toy fakes and fake "
            "support replies. Delivery texts, gift cards at the rack, charities, marketplace, tickets and puppies are "
            "already in weeks 3–6 and holiday-2026.", "",
            "| # | Date | Time | Where | Format | Look | Topic | Title |", "|---|---|---|---|---|---|---|---|"]
    for n, (p, i) in enumerate(zip(POSTS, items)):
        d = dt.date.fromisoformat(p["date"])
        where = {"short": "Reels + Shorts", "carousel": "Instagram"}[p["kind"]]
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} | 12:00 | {where} | {p['kind'].capitalize()} | {p['look']} | "
                    f"{p['topic']} | {p['title']} |")
    rows += ["", "Sources: every item lists public FTC or BBB pages in `sources`. Before posting, check each "
             "`claims_to_verify` line against them that week (BBB updates its holiday list each year).", "",
             "Key dates: Thanksgiving Nov 26, Black Friday Nov 27, Cyber Monday Nov 30, Giving Tuesday Dec 1."]
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
        assert len(i["script"]["title"]) <= 60 or i["format"] == "carousel", i["script"]["title"]
        assert len(i["script"]["hashtags"]) <= 5
        for s in i["script"]["segments"]:
            assert len(s["on_screen_text"].split()) <= 12, s["on_screen_text"]
        hook = i["script"]["hook"]
        assert any(ch.isdigit() for ch in hook.split(".")[0][:60]), hook
    (root / "holiday-season-2026.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (root / "POSTING_PLAN_HOLIDAY_SEASON_2026.md").write_text(plan(items))
    for n, i in enumerate(items):
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        print(n, i["post_on"], i["format"], i["look"], w, i["script"]["title"])


if __name__ == "__main__":
    main()
