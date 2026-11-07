"""Valentine's romance-scam pack, Tue Feb 2 - Sun Feb 14 2027: pig butchering, fake military, crypto romance.

    python3 build.py   ->  ../../valentines-2027.json and ../../POSTING_PLAN_VALENTINES_2027.md

5 Shorts at 12:00 (Tue Feb 2, Thu Feb 4, Sun Feb 7, Thu Feb 11, Sun Feb 14) and 3 carousels at 19:30 (Mon Feb 8,
Wed Feb 10, Fri Feb 12): slots weeks 13-21, the tax pack and the newsletter cuts leave free. Weeks 7-12 and 13-21
already cover gift card asks, leave papers, customs packages, withdrawal taxes, reverse image search and the 6 stages,
so these take new angles from the FTC and FBI IC3 pages cited on each post.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, MASCOT, seg  # noqa: E402

FTC_LIES = "https://www.ftc.gov/news-events/news/press-releases/2023/02/new-ftc-data-reveals-top-lies-told-romance-scammers"
FTC_MIL = "https://consumer.ftc.gov/consumer-alerts/2023/07/military-consumers-and-romance-scams"
FTC_LOVE = "https://consumer.ftc.gov/consumer-alerts/2025/02/looking-love-watch-out-scammers"
FTC_ROMANCE = "https://consumer.ftc.gov/articles/what-know-about-romance-scams"
IC3_CRYPTO = "https://www.ic3.gov/PSA/2022/psa221003"
IC3_VERIFY = "https://www.ic3.gov/PSA/2024/PSA240426"
CHECKER = "Not sure about a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends nothing anywhere."
P = "romance scams"
SEASON = "Valentine's 2027"


def slides(cover, items, save, cover_vis):
    out = [("Hook", "", cover, cover_vis)]
    out += [(str(i), n, o, v) for i, (n, o, v) in enumerate(items, 1)]
    out.append(("Save this", save, "Save it. Send it to someone who's dating online.", f"{MASCOT} giving a thumbs up"))
    return out


POSTS = [
 dict(date="2027-02-02", time="12:00", kind="short", look="walkthrough", topic="dating verification links",
  title="'Verify you're safe first': 1 dating app link to skip",
  hook="1 match, 1 week of sweet messages, then 1 link: verify you're not a predator before we meet.",
  thumb="'Verify' link? Skip it",
  hashtags=["onlinedating", "datingapps", "romancescam", "valentinesday", "scamdecoded"],
  description="The FBI IC3 warning about fake 'free' identity verification sites sent by dating matches.",
  caption="A match says they only meet people who 'verify' first, and sends a link. The FBI's IC3 says these sites take "
          "your card and sign you up for monthly charges, and can use your details for identity theft.",
  sources=[IC3_VERIFY], claims=["IC3 warns matches send links to fake 'free' verification sites that collect personal and "
                                "card details and enroll victims in recurring subscriptions"],
  original_element="Phone-screen walkthrough mockup: the chat, the 'verification' page with its scare text, then the card statement line.",
  segments=[
   ("Hook", "A week of great messages. Then: I only meet people who verify first, it's free, here's the link.",
    "'Verify first, it's free'", "a dating chat with a link"),
   ("The page", "It's full of scary stories about predators, then asks for your name, birthday and a card, just to "
                "prove you're real.", "Then: name, birthday, card", "a verification page with a padlock"),
   ("The catch", "The FBI's IC3 says that card gets signed up for monthly charges you never wanted, and your details "
                 "can be used for identity theft.", "IC3: monthly charges + ID theft", "a card statement with a repeating charge"),
   ("Do this", "Don't tap links from a match. Keep chatting inside the app, which has its own safety tools, and report "
               "the profile.", "Stay in the app. Report it.", f"{MASCOT} tapping a report button"),
  ]),
 dict(date="2027-02-04", time="12:00", kind="short", look="data chart", topic="pig butchering",
  title="Their trading app shows +240%. Here's what 1 screen hides",
  hook="1 new friend, 1 trading app, and a balance that's up 240% in 6 weeks.",
  thumb="+240%? It's a picture",
  hashtags=["pigbutchering", "cryptoscam", "romancescam", "investing", "scamdecoded"],
  description="How pig butchering scams use fake trading dashboards, from the FBI IC3.",
  caption="In pig butchering scams, a new friend or partner coaches you into 'investing' on a site or app they pick. "
          "The FBI's IC3 says those platforms show balances growing fast, and the money is already gone.",
  sources=[IC3_CRYPTO, FTC_LOVE], claims=["IC3 says fraudulent sites and apps let victims track holdings that appear to grow "
                                           "exponentially", "IC3 says victims asked to pay taxes or fees to withdraw lose more"],
  original_element="A data-chart beat: the fake app's rising line next to a flat line labelled 'what's really in the account: $0'.",
  segments=[
   ("Hook", "Your new friend has been texting for weeks. Now they're teaching you to trade, and the app says you're up "
            "two hundred and forty percent.", "Up 240% in 6 weeks?", "a phone with a steep green chart"),
   ("The screen", "The FBI's IC3 says the site or app is built by the scammers. The number on it is just a picture "
                  "they control.", "The chart is theirs, not the market", "a puppet string attached to a chart"),
   ("The end", "When you try to cash out, there's a tax or a fee to pay first. Pay it, and there's another. Then the "
               "site and the friend vanish.", "Cash out? 'Pay a fee first'", "a locked vault door"),
   ("Do this", "Never invest on an app a stranger picked for you, however long you've talked. Report it at ic3.gov.",
    "Their app? Not your money", f"{MASCOT} closing an app"),
  ]),
 dict(date="2027-02-07", time="12:00", kind="short", look="face cam", topic="fake military",
  title="Care packages for 'troops in Ukraine'? 1 detail is wrong",
  hook="1 soldier, 1 care package request, and 1 detail that gives the whole thing away.",
  thumb="No US troops there",
  hashtags=["military", "romancescam", "fakesoldier", "valentinesday", "scamdecoded"],
  description="The FTC's warning about romance scammers posing as US troops in Ukraine and selling care packages.",
  caption="Scammers posing as US service members now say they're in Ukraine and ask you to buy care packages on a "
          "'military' website. The FTC points out the US has no military presence there, and servicemembers never "
          "pay for packages.",
  sources=[FTC_MIL], claims=["FTC: a newer version claims to be US troops in Ukraine, where the US has no military presence, "
                             "and asks for care packages paid through a fake military website",
                             "FTC: servicemembers never have to pay to get packages, food, medical treatment, or to take leave"],
  original_element="Face cam: Dhruv reads the made-up message, then says the one detail to camera.",
  segments=[
   ("Hook", "He's a US soldier in Ukraine, he says. Supplies are short. Could you order him a care package from this "
            "military site?", "'Order my care package here'", "a chat with a military photo"),
   ("The detail", "The FTC says scammers now use this exact story, and the US has no troops stationed in Ukraine.",
    "FTC: no US troops there", "a map with a question mark"),
   ("The rule", "And real servicemembers never pay for packages, food, medical care or leave. The military covers it.",
    "Soldiers never pay for these", "a checklist with four crosses"),
   ("Do this", "Don't buy from the site. Search the photo online, check the story with someone who's served, and report "
               "the profile.", "Search the photo. Report it.", f"{MASCOT} holding a magnifying glass"),
  ]),
 dict(date="2027-02-08", time="19:30", kind="carousel", look="data", topic="romance lies",
  title="The 4 lies romance scammers tell most, from FTC data",
  hook="4 stories show up again and again in romance scam reports. Number 1 isn't about love at all.",
  thumb="4 lies, ranked",
  hashtags=["romancescam", "valentinesday", "onlinedating", "ftc", "scamdecoded"],
  description="The top lies in romance scam reports, from the FTC's data on $1.3 billion reported lost in 2022.",
  caption="The FTC looked at romance scam reports and ranked the stories scammers tell most. People reported losing "
          "$1.3 billion to romance scams in 2022, and more of it was sent in crypto than any other way.",
  sources=[FTC_LIES, FTC_ROMANCE],
  claims=["FTC: nearly 70,000 people reported $1.3 billion lost to romance scams in 2022",
          "FTC: top lies were a friend or relative in trouble (nearly a quarter), investment advice, then military service and an important delivery",
          "FTC: people reported losing more money in cryptocurrency than any other payment method"],
  original_element="Slide 2 is a bar chart of the 4 lies in FTC rank order, drawn like originality/out/charts.",
  segments=slides("4 lies, ranked", [
   ("Number 1: someone close to them is sick, hurt or in jail, and needs money. The FTC says that's nearly a quarter "
    "of reports.", "1. 'My son is in the hospital'", "a hospital bed icon"),
   ("Number 2: investment advice. They know a way to make money, usually in crypto.", "2. 'Let me show you how I trade'",
    "a rising chart icon"),
   ("Number 3: they're in the military, overseas, and can't get to their money.", "3. 'I'm deployed overseas'",
    "a soldier silhouette"),
   ("Number 4: an important delivery or package that needs a fee to release.", "4. 'Your package is stuck'",
    "a parcel with a lock"),
   ("$1.3 billion reported lost in 2022, from nearly 70,000 people. Any money ask from someone you haven't met is the tell.",
    "$1.3 billion in 2022", "a big number on a calendar page"),
  ], "Save this before you match with anyone new.", f"{MASCOT} with a heart and a shield")),
 dict(date="2027-02-10", time="19:30", kind="carousel", look="checklist", topic="pig butchering",
  title="Is that trading app real? 5 checks from the FBI",
  hook="5 checks before you put money in any trading app a new friend sent you.",
  thumb="5 checks, 1 app",
  hashtags=["cryptoscam", "pigbutchering", "investing", "romancescam", "scamdecoded"],
  description="Five checks for crypto investment apps and sites, from the FBI IC3's warning.",
  caption="Crypto romance scams run on fake trading apps and sites. 5 checks from the FBI's IC3 before you deposit "
          "anything, especially if someone you met online picked the app.",
  sources=[IC3_CRYPTO], claims=["IC3 advises watching for domains that imitate real financial institutions, including misspelled URLs",
                                "IC3 says victims are asked to pay taxes or fees to withdraw, and are sometimes told to wire money overseas or buy prepaid cards"],
  original_element="Slide 3 is a screen recording Dhruv makes of typing a real exchange's address next to a made-up look-alike.",
  segments=slides("5 checks, 1 app", [
   ("Who picked it? If someone you met online chose the app, stop there.", "1. Who sent you the app?",
    "a phone with an app icon and a question mark"),
   ("Read the web address letter by letter. IC3 warns about names one letter off real exchanges.", "2. Spell the address",
    "a web address under a magnifying glass"),
   ("Can you find it in the official app store, from a company you can look up? If not, don't install it.",
    "3. Can you verify the company?", "an app store shelf"),
   ("Wire to an overseas account, or buy prepaid cards, to 'deposit'? Real platforms don't work that way.",
    "4. Strange ways to deposit", "a wire transfer form"),
   ("A tax or fee before you can withdraw means the money isn't there. Don't pay it.", "5. Fees to withdraw = stop",
    "a withdraw button with a lock"),
  ], "Save this, and report anything like it at ic3.gov.", f"{MASCOT} with a shield")),
 dict(date="2027-02-11", time="12:00", kind="short", look="illustrated", topic="crypto romance",
  title="'Let's build our future' in crypto: 1 line to stop at",
  hook="3 months of good morning texts, 1 sentence about our future, and 1 crypto account.",
  thumb="'Our future' = your money",
  hashtags=["cryptoscam", "romancescam", "valentinesday", "onlinedating", "scamdecoded"],
  description="How romance scammers turn the relationship into an investment pitch, with FTC and IC3 sources.",
  caption="The FTC says online love interests often turn to investing, usually crypto. The FBI's IC3 says they build "
          "trust for weeks first. If someone you haven't met talks money, it's the scam, however real it feels.",
  sources=[FTC_LOVE, IC3_CRYPTO], claims=["FTC: romance scammers ask for money or pitch investments in crypto or the stock market",
                                           "IC3: fraudsters build trust over time before coaching victims to invest"],
  original_element="Illustrated beats with a 3-second on-screen timeline of the 3 months.",
  segments=[
   ("Hook", "Three months of good morning texts. Then one night: I want to build our future together. Let me set you "
            "up with the crypto account I use.", "'Let's build our future'", f"{MASCOT} looking at a phone with hearts"),
   ("Why it works", "The FBI's IC3 says these scammers spend weeks building trust before money ever comes up. By then, "
                    "it doesn't feel like a pitch.", "Weeks of trust, then money", "a calendar with hearts on every day"),
   ("The tell", "The FTC's rule is simple: never send money, or invest it, for a love interest you haven't met in "
                "person.", "Haven't met? No money", "a heart with a padlock"),
   ("Do this", "Tell a friend you trust what they asked. If you've sent money already, report it at ic3.gov and to "
               "your bank today.", "Tell a friend. Report it.", f"{MASCOT} talking to a friend"),
  ]),
 dict(date="2027-02-12", time="19:30", kind="carousel", look="myth vs fact", topic="dating app safety",
  title="Keep it on the app: 5 dating rules from the FBI",
  hook="5 rules from the FBI that keep a dating app match from turning into a monthly charge or worse.",
  thumb="5 dating rules",
  hashtags=["onlinedating", "datingsafety", "valentinesday", "romancescam", "scamdecoded"],
  description="Five dating-app safety rules from the FBI IC3, as myth vs fact slides.",
  caption="Before Valentine's weekend: 5 rules from the FBI's IC3 for dating apps, from links to card charges.",
  sources=[IC3_VERIFY, FTC_LOVE], claims=["IC3 advises keeping conversations on the dating platform, not clicking links from "
                                           "people met online, and using one limited card or a virtual card for new subscriptions"],
  original_element="Slide 5 is a screenshot Dhruv takes of where 'virtual card' lives in his own banking app (numbers hidden).",
  segments=slides("5 dating rules", [
   ("Myth: moving to another chat app is safer. Fact: IC3 says stay on the dating app, which has safety tools.",
    "1. Stay in the app", "two chat bubbles, one crossed out"),
   ("Myth: a match's link is fine once you trust them. Fact: don't tap links or files from someone you met online.",
    "2. No links from matches", "a link icon with a stop sign"),
   ("Myth: verification sites keep you safe. Fact: IC3 says fake ones take your card for monthly charges.",
    "3. Skip 'verification' sites", "a padlock with a dollar sign"),
   ("Myth: one card for everything is easiest. Fact: IC3 suggests a low-limit or virtual card for new sign-ups.",
    "4. Use a low-limit card", "a small card with a shield"),
   ("Myth: a charge you don't know is a mistake. Fact: check statements, and call your bank about any you don't recognize.",
    "5. Read your statement", "a statement with one line circled"),
  ], "Save this for Valentine's weekend.", f"{MASCOT} with a heart")),
 dict(date="2027-02-14", time="12:00", kind="short", look="screen recording", topic="checking a match",
  title="Oil rig engineer? 1 search before Valentine's dinner",
  hook="1 job title, 1 search, and 30 seconds that tell you a lot about a new match.",
  thumb="Job + 'scammer' search",
  hashtags=["onlinedating", "valentinesday", "romancescam", "datingtips", "scamdecoded"],
  description="The FTC's two quick checks on a new online love interest: their job plus 'scammer', and the photo.",
  caption="Happy Valentine's Day. Two checks the FTC suggests for any new online love interest: search their job plus "
          "'scammer', and run a reverse image search on their photo.",
  sources=[FTC_LOVE, FTC_ROMANCE], claims=["FTC suggests searching the person's job plus the word 'scammer' and doing a reverse image search"],
  original_element="Screen recording: Dhruv types a made-up job title plus 'scammer' into a search bar (no real person shown).",
  segments=[
   ("Hook", "Your match is an engineer on an offshore oil rig, or a doctor overseas, or deployed. Always far away, "
            "always busy.", "Always far away?", "a screen recording of a dating profile"),
   ("The search", "The FTC's tip: search their job plus the word scammer. If that story shows up in other people's "
                  "warnings, you'll see it in seconds.", "Search: job + 'scammer'", "a search bar being typed into"),
   ("The photo", "Then run a reverse image search on their photo. A different name, or a stock photo, settles it.",
    "Then search the photo", "a photo with matching results"),
   ("Do this", "Neither check is an insult. Real people pass them easily. And whoever they are, no money before you've "
               "met.", "No money before you've met", f"{MASCOT} with a heart"),
  ]),
]


def item(p):
    fmt = "carousel" if p["kind"] == "carousel" else "short"
    platforms = {"short": ["instagram", "youtube"], "carousel": ["instagram"]}[p["kind"]]
    return {"format": fmt, "pillar": P, "platforms": platforms, "post_on": f"{p['date']} {p['time']}",
            "topic": p["topic"], "look": p["look"], "original_element": p["original_element"],
            "idea_angle": f"{SEASON}: {p['topic']}. {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": [seg(*r) for r in p["segments"]], "cta": CTA,
                       "caption": p["caption"] + "\n\n" + CHECKER + "\n\n" + CTA, "hashtags": p["hashtags"],
                       "description": p["description"], "thumbnail_text": p["thumb"], "sources": p["sources"],
                       "claims_to_verify": p["claims"]}}


def plan(items):
    rows = ["# Scam Decoded: Valentine's romance-scam pack, Tue Feb 2 – Sun Feb 14 2027", "",
            "8 posts: 5 Shorts (Reels + YouTube Shorts) at 12:00 and 3 Instagram carousels at 19:30, America/New_York, in "
            "slots weeks 13–21, the tax pack and the newsletter cuts leave free. Nothing has been posted; Dhruv posts each "
            "by hand.", "",
            "New angles only: fake dating 'verification' links, fake trading dashboards, the FTC's ranked romance lies, "
            "'troops in Ukraine' care packages, app checks, crypto 'our future' pitches, the dating app rules and the "
            "job-plus-'scammer' search. Gift card asks, leave papers, customs packages, withdrawal taxes, reverse image "
            "search and the 6 stages are already in weeks 7–12 and 13–21.", "",
            "| # | Date | Time | Where | Format | Look | Topic | Title |", "|---|---|---|---|---|---|---|---|"]
    for n, (p, i) in enumerate(zip(POSTS, items)):
        d = dt.date.fromisoformat(p["date"])
        where = {"short": "Reels + Shorts", "carousel": "Instagram"}[p["kind"]]
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} | {p['time']} | {where} | {p['kind'].capitalize()} | "
                    f"{p['look']} | {p['topic']} | {p['title']} |")
    rows += ["", "Sources: every item lists public FTC or FBI IC3 pages in `sources`. Check each `claims_to_verify` line "
             "against them the week it posts.", "", "Valentine's Day is Sun Feb 14; the weeks 13–21 long video that day "
             "(#65, 10:00) pairs with the 12:00 Short here."]
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
        hook = i["script"]["hook"]
        assert any(ch.isdigit() for ch in hook.split(".")[0][:60]), hook
    (root / "valentines-2027.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (root / "POSTING_PLAN_VALENTINES_2027.md").write_text(plan(items))
    for n, i in enumerate(items):
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        print(n, i["post_on"], i["format"], i["look"], w, i["script"]["title"])


if __name__ == "__main__":
    main()
