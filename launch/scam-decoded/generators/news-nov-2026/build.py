"""News-hook Shorts, Sun Nov 22 - Sun Dec 6 2026: five scams in the news with no post yet (scouting's
research/scouting/keywords-scam-decoded-first-20.md on PR #2).

    python3 build.py   ->  ../../news-nov-2026.json and ../../POSTING_PLAN_NEWS_NOV_2026.md

5 Shorts (Reels + YouTube Shorts) at 12:00 in the only free noon slots between Black Friday week and mid-December
(weeks 3-6, the holiday packs and the launch plan fill the rest). Titles put the searched scam name first, then the
number hook, per scouting's keyword file. Check each phrase in the YouTube search box before scheduling.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, MASCOT, seg  # noqa: E402

BBB_TAP = "https://www.bbb.org/article/scams/32343-bbb-scam-alert-what-is-ghost-tapping-how-to-spot-and-avoid-tap-to-pay-scams"
FTC_SWEEPS = "https://consumer.ftc.gov/consumer-alerts/2026/10/spot-scammers-impersonating-well-known-charities-and-sweepstakes"
FTC_ADS = "https://consumer.ftc.gov/consumer-alerts/2026/11/tell-ftc-about-imposter-ads-online"
FTC_ENROLL = "https://consumer.ftc.gov/consumer-alerts/2026/10/seeing-lots-ads-health-insurance-plans-during-open-enrollment-read"
FTC_SHOP = "https://consumer.ftc.gov/articles/online-shopping"
CHECKER = "Not sure about a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends nothing anywhere."
SEASON = "In the news, Nov 2026"

POSTS = [
 dict(date="2026-11-22", look="walkthrough", pillar="online shopping and marketplace scams", topic="ghost tapping",
  title="Ghost tapping scam: check 1 screen before you tap",
  hook="1 tap at a holiday market, and a $15 box of cookies turns into a $1,500 charge.",
  thumb="Check the screen. Then tap.",
  hashtags=["ghosttapping", "taptopay", "holidayshopping", "scamalert", "scamdecoded"],
  description="Tap-to-pay scams at markets, crowds and fake charity stands, from the BBB.",
  caption="Tap-to-pay is fast, and that's what these scams count on. The BBB warns about fake stands and charity "
          "collectors who charge your card far more than they said, and people who brush past you in a crowd. "
          "The $15 example here is made up.",
  sources=[BBB_TAP],
  claims=["BBB: fraudsters run fake stands at events and markets and ask for tap payments",
          "BBB: fake charity collectors ask for a small donation and charge much more",
          "BBB: check the merchant's name and amount on the terminal before tapping; set up transaction alerts",
          "BBB: an RFID-blocking wallet or sleeve can help stop wireless skimming; swipe or insert when in doubt"],
  original_element="Phone walkthrough: a mock card reader screen showing the merchant name and amount, with the two things to read circled.",
  segments=[
   ("Hook", "A holiday market. A stand selling cookies, fifteen dollars, tap here. You tap without looking. Later your "
            "bank app shows fifteen hundred.", "$15 cookies... $1,500 charge?", "a card reader at a market stall"),
   ("How", "The BBB says fake stands and charity collectors ask you to tap, then charge far more than they said. In "
           "crowds, someone may brush past with a reader.", "Fake stands. Fake charities. Crowds.", "a crowded market with a hidden reader"),
   ("The check", "Before you tap, read two things on the reader's screen: the business name and the amount. No screen, "
                 "or they won't show you? Don't tap.", "Read the name and the amount", "a terminal screen with two circles"),
   ("Do this", "Turn on alerts for every charge, and swipe or insert if anything feels off. Charged wrong? Call your "
               "bank on the number on your card.", "Alerts on. Swipe if unsure.", f"{MASCOT} holding a phone with an alert"),
  ]),
 dict(date="2026-11-28", look="face cam", pillar="text and email scams, decoded", topic="sweepstakes fees",
  title="Sweepstakes scam: 0 real prizes make you pay a fee",
  hook="1 call says you won a famous sweepstakes, and 1 small fee will release the check.",
  thumb="You won? Then why pay?",
  hashtags=["sweepstakes", "prizescam", "givingtuesday", "scamalert", "scamdecoded"],
  description="Scammers using the names of well-known sweepstakes and charities, from the FTC's October 2026 alert.",
  caption="Scammers use the names of famous sweepstakes and charities, and caller ID can show a real name. The FTC: "
          "the moment someone tells you to pay to claim your prize, you're dealing with a scam.",
  sources=[FTC_SWEEPS],
  claims=["FTC: the moment someone tells you to pay to claim your prize, it's a scam",
          "FTC: legitimate sweepstakes are free and by chance",
          "FTC: don't trust caller ID, even if it shows a real agency or company name",
          "FTC: scammers use real charity names or ones that sound similar"],
  original_element="Face-to-camera explainer holding a printed 'prize check' with the fee line circled.",
  segments=[
   ("Hook", "Giving Tuesday week, and the phone says a famous sweepstakes name. You've won. Just pay a small fee and the "
            "check ships today.", "'You won. Just pay the fee.'", "a phone showing a famous-looking caller ID"),
   ("The rule", "The FTC is blunt: the moment someone tells you to pay to claim a prize, it's a scam. Real sweepstakes "
                "are free and by chance.", "Pay to claim? It's a scam.", "a prize check with a fee stamped on it"),
   ("The trick", "Caller ID can be faked to show a real company or charity name, and scammers borrow real charity names "
                 "too, so the name proves nothing.", "Caller ID proves nothing", "a phone screen with a mask"),
   ("Do this", "Hang up. Never pay to get a prize. Want to give this week? Look the charity up yourself, past the ads at "
               "the top of the search.", "Never pay to win. Look it up.", f"{MASCOT} hanging up a phone"),
  ]),
 dict(date="2026-11-29", look="screen recording", pillar="text and email scams, decoded", topic="impostor ads",
  title="Impostor ads: 1 sponsored result that isn't the company",
  hook="1 search, 1 ad at the top with the right logo, and it's not the company at all.",
  thumb="Right logo. Wrong company.",
  hashtags=["scamads", "cybermonday", "onlineshopping", "scamalert", "scamdecoded"],
  description="Ads that impersonate businesses and government agencies, from the FTC's November 2026 alert.",
  caption="The FTC says scammers pay for ads that pose as well-known businesses and government agencies, in social "
          "feeds, search results and shopping sites, hoping you'll think they're the real thing. Skip the ads and go to "
          "the real site yourself. The FTC is taking public comments on platform rules until Nov 30.",
  sources=[FTC_ADS, FTC_SWEEPS],
  claims=["FTC: scammers pose as well-known businesses or government agencies in ads in feeds, search results and shopping platforms",
          "FTC: scammers pay for ad placement and people are losing big money",
          "FTC: comments on possible platform rules due Nov 30, 2026 (check the Federal Register link)",
          "FTC: don't rely on the first search results you see; paid ads can lead to fake information"],
  original_element="Screen recording of a search page: the sponsored result's address next to the real one, typed in by hand.",
  segments=[
   ("Hook", "Cyber Monday tomorrow. You search for a big store's support line. The top result has the logo, the colors, "
            "the name. It's an ad.", "Top result. Right logo. An ad.", "a search page with a sponsored result"),
   ("What's going on", "The FTC says scammers pay for ads that pose as well-known businesses and government agencies, "
                       "in feeds, search results and shopping sites.", "FTC: scammers buy impostor ads", "a stack of ad cards with masks"),
   ("The check", "Look at the web address under the ad. One letter off, an extra word, an odd ending? Skip it. Type the "
                 "real address yourself.", "Read the address. Type it yourself.", "an address bar with one letter circled"),
   ("Do this", "Report impostor ads at ReportFraud.ftc.gov. The FTC is also asking for public comments on platform "
               "rules until November thirtieth.", "Report it: ReportFraud.ftc.gov", f"{MASCOT} pointing at a report button"),
  ]),
 dict(date="2026-12-03", look="data chart", pillar="Medicare and health scams", topic="open enrollment ads",
  title="Open enrollment scam: 1 site to start at, not an ad",
  hook="1 open enrollment season, a flood of health plan ads, and 1 safe place to start.",
  thumb="Start at HealthCare.gov",
  hashtags=["openenrollment", "healthinsurance", "healthcare", "scamalert", "scamdecoded"],
  description="Health insurance ads and robocalls during open enrollment, from the FTC's October 2026 alert.",
  caption="Open enrollment brings a flood of health plan ads, calls and texts. The FTC warns about plans that promise "
          "'comprehensive' coverage but offer limited benefits, discount cards sold as insurance, and ads that look like "
          "they're from the government. Start at HealthCare.gov, and check the deadline there.",
  sources=[FTC_ENROLL],
  claims=["FTC: some plans promise comprehensive health insurance but offer limited benefits",
          "FTC: medical discount cards are sometimes sold as if they were health insurance",
          "FTC: prerecorded robocalls marketing health insurance are illegal",
          "FTC: start at HealthCare.gov or call the Marketplace Call Center at 1-800-318-2596"],
  original_element="A data-chart beat: 'what the ad says' vs 'what the plan covers', drawn as two bars, then the HealthCare.gov address.",
  segments=[
   ("Hook", "Open enrollment. Ads everywhere: full coverage, ninety-nine a month, call now. Some of them aren't what they "
            "say.", "'Full coverage, $99, call now'", "a phone feed full of insurance ads"),
   ("What the FTC sees", "Plans that promise comprehensive coverage but pay for little, and medical discount cards sold "
                         "as if they were insurance.", "'Comprehensive'? Or a discount card?", "two bars, one tall, one tiny"),
   ("The calls", "And a recorded voice selling a health plan? The FTC says those robocalls are illegal, so whoever's "
                 "behind one isn't someone to buy from.", "Recorded sales call = illegal", "a phone with a robot voice icon"),
   ("Do this", "Start at HealthCare.gov, typed in yourself, or call the Marketplace Call Center. Report bad ads at "
               "ReportFraud.ftc.gov.", "Start at HealthCare.gov", f"{MASCOT} typing an address"),
  ]),
 dict(date="2026-12-06", look="illustrated", pillar="online shopping and marketplace scams", topic="fake online stores",
  title="Fake online store scam: 2 searches before a late gift",
  hook="1 shop you've never heard of has the sold-out gift, and 2 searches tell you if it's real.",
  thumb="Never heard of the shop?",
  hashtags=["onlineshopping", "fakestore", "holidaygifts", "scamalert", "scamdecoded"],
  description="Checking an unfamiliar online store before you buy, from the FTC's online shopping advice.",
  caption="A shop you've never heard of has the gift everyone else sold out of. Before you pay, the FTC suggests "
          "searching the store's name with 'complaint' or 'scam', and paying by credit card, which best protects you "
          "if something goes wrong. A padlock doesn't prove a store is real.",
  sources=[FTC_SHOP],
  claims=["FTC: search the product or company name plus 'complaint' or 'scam'",
          "FTC: some reviews and ratings are fake or misleading",
          "FTC: scammers know how to encrypt sites too (https isn't proof)",
          "FTC: paying by credit card best protects you; never buy from sellers who insist on gift cards"],
  original_element="Illustrated two-search sequence: the store name + 'scam', then the store name + 'complaint', with results drawn as cards.",
  segments=[
   ("Hook", "Two weeks to go. Every store is sold out of the gift, except one you've never heard of, with free "
            "shipping and a padlock.", "Sold out everywhere... but here?", "a shopping site with a padlock and a gift"),
   ("Search 1 and 2", "Before you pay, the FTC says search the store's name plus the word scam, then plus complaint. "
                      "Read what other buyers say.", "Search: name + scam, name + complaint", "two search bars"),
   ("Not proof", "A padlock isn't proof. The FTC says scammers can encrypt sites too, and some star ratings are fake.",
    "Padlock? Stars? Not proof.", "a padlock with a question mark"),
   ("Do this", "Pay by credit card, which best protects you if it goes wrong. Gift cards only? Close the tab.",
    "Credit card. Never gift cards.", f"{MASCOT} closing a browser tab"),
  ]),
]


def item(p):
    return {"format": "short", "pillar": p["pillar"], "platforms": ["instagram", "youtube"], "post_on": f"{p['date']} 12:00",
            "topic": p["topic"], "look": p["look"], "original_element": p["original_element"],
            "idea_angle": f"{SEASON}: {p['topic']}. {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": [seg(*r) for r in p["segments"]], "cta": CTA,
                       "caption": p["caption"] + "\n\n" + CHECKER + "\n\n" + CTA, "hashtags": p["hashtags"],
                       "description": p["description"], "thumbnail_text": p["thumb"], "sources": p["sources"],
                       "claims_to_verify": p["claims"]}}


def plan(items):
    rows = ["# Scam Decoded: news-hook Shorts, Sun Nov 22 – Sun Dec 6 2026", "",
            "5 Shorts (Reels + YouTube Shorts) at 12:00, America/New_York, in the free noon slots between Black Friday week "
            "and mid-December. Each is a scam in the news with no post yet (scouting's keyword file on PR #2). Titles put "
            "the scam's searched name first. Before scheduling, type each title's first words into the YouTube search "
            "box and check autocomplete. Nothing has been posted; Dhruv posts each by hand.", "",
            "| # | Date | Time | Look | Topic | Title |", "|---|---|---|---|---|---|"]
    for n, (p, i) in enumerate(zip(POSTS, items)):
        d = dt.date.fromisoformat(p["date"])
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} | 12:00 | {p['look']} | {p['topic']} | {p['title']} |")
    rows += ["", "Sources: BBB (ghost tapping) and FTC consumer alerts from Oct–Nov 2026, listed in each item's `sources`. "
             "The impostor-ads post mentions the FTC's Nov 30 comment deadline: check the Federal Register link on the "
             "alert before posting, and cut that line if comments have closed."]
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
        assert any(ch.isdigit() for ch in i["script"]["hook"].split(".")[0][:60]), i["script"]["hook"]
        assert "guarantee" not in json.dumps(i).lower()
    (root / "news-nov-2026.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (root / "POSTING_PLAN_NEWS_NOV_2026.md").write_text(plan(items))
    for n, i in enumerate(items):
        print(n, i["post_on"], i["look"], sum(len(s["narration"].split()) for s in i["script"]["segments"]), i["script"]["title"])


if __name__ == "__main__":
    main()
