"""5 Shorts promoting the free data breach checklist (/breached/), Saturdays Apr 17 - May 15 2027.

    python3 build.py   ->  ../../breach-shorts-2027.json and ../../POSTING_PLAN_BREACH_SHORTS.md

Saturdays are the slot the weekly plans leave open; the tax pack ends Apr 10, so these follow it.
Each Short ends on the checklist, and no two in a row share a look.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, MASCOT, P_ID, seg  # noqa: E402

HIBP = "https://haveibeenpwned.com/"
ITG_BREACH = "https://www.identitytheft.gov/databreach"
FTC_BREACH = "https://consumer.ftc.gov/consumer-alerts/2022/10/have-you-been-affected-data-breach-read"
FTC_DARKWEB = "https://consumer.ftc.gov/consumer-alerts/2022/09/did-you-get-email-saying-your-personal-info-sale-dark-web"
FTC_FREEZE = "https://consumer.ftc.gov/consumer-alerts/2025/09/get-credit-freeze-stop-identity-thieves"
IPPIN = "https://www.irs.gov/identity-theft-fraud-scams/get-an-identity-protection-pin"
SITE = "https://scamdecoded.netlify.app/breached/"
PLUG = ("Free data breach checklist, 8 steps with links to the official sites: link in bio "
        "(scamdecoded.netlify.app/breached). Not sure about a follow-up message? Paste it into our free scam checker.")

POSTS = [
 dict(date="2027-04-17", look="screen recording", title="Got a data breach letter? 8 steps, in the right order",
  hook="8 steps after a data breach letter, and the order matters more than you'd think.",
  thumb="Breach letter? 8 steps",
  hashtags=["databreach", "identitytheft", "creditfreeze", "privacy", "scamalert", "scamdecoded"],
  description="The order to work through after a data breach notice, from our free checklist.",
  caption="A breach letter says what leaked, but not what to do first. Here's the order.",
  sources=[ITG_BREACH, FTC_BREACH, FTC_FREEZE], claims=["IdentityTheft.gov lists steps for each type of exposed information (FTC)",
                                                       "A credit freeze is free (FTC)"],
  original_element="Dhruv scrolls through scamdecoded.netlify.app/breached/ on his own phone, ticking the boxes as he talks.",
  segments=[
   ("Hook", "Eight steps after a data breach letter, and the order matters. Here's the list I use.",
    "8 steps. In order.", "Dhruv's screen: the breach checklist page"),
   ("First", "First, find out what leaked: email and password, card, bank account, or Social Security number. Each one "
             "needs different steps.", "1. What leaked?", "Dhruv's screen: step 1 ticked"),
   ("Then", "Change the password and anywhere you reused it, and turn on two-step sign-in. Card exposed? Call the bank. "
            "Social Security number? Freeze your credit at all three bureaus, and get an IRS IP PIN.",
    "Passwords, bank, freeze, IP PIN", "Dhruv's screen: steps 3 to 6"),
   ("Last", "Then the official steps at identity theft dot gov, and one warning: the scam follow-ups. The whole list "
            "is free, link in bio.", "Free checklist: link in bio", f"{MASCOT} holding a checklist"),
  ]),
 dict(date="2027-04-24", look="face cam", title="'Your account was in the breach': 1 call to hang up on",
  hook="1 call comes a few days after breach news, from your 'bank's fraud team'. Hang up.",
  thumb="'Fraud team' calling? Hang up.",
  hashtags=["databreach", "bankscam", "fraudalert", "phonescam", "scamalert", "scamdecoded"],
  description="The fake fraud team call that follows data breach news, and what to do instead.",
  caption="Breach in the news, then a call: 'Your account was in the breach. Read me the code we just sent so we can "
          "secure it.' That's the scammer, using the news.",
  sources=[FTC_BREACH, ITG_BREACH], claims=["Scammers use data breach news to contact people pretending to help (FTC)"],
  original_element="Dhruv on camera, acting out the call with his own phone; illustrated beat for the code.",
  segments=[
   ("Hook", "One call, a few days after a breach is in the news. This is your bank's fraud team. Your account was in "
            "the breach.", "'Your account was in the breach'", "Dhruv on camera holding a phone"),
   ("The ask", "We need to secure it now. Read me the code we just texted you. That code signs them in as you.",
    "'Read me the code'", "a phone with a six-digit code"),
   ("The tell", "Your bank won't ask for a code, a password or your PIN, and won't ask you to move money to keep it safe.",
    "Banks don't ask for codes", "a bank with a red X over a code"),
   ("Do this", "Hang up and call the number on your card. Then do the breach checklist. It's free, link in bio.",
    "Call the number on your card", f"{MASCOT} hanging up a phone"),
  ]),
 dict(date="2027-05-01", look="walkthrough", title="Breach settlement with a $25 fee? 0 real claims charge you",
  hook="$412 from a data breach settlement, after a $25 processing fee. Real claims don't charge you.",
  thumb="Settlement fee? No.",
  hashtags=["databreach", "classaction", "settlement", "textscam", "scamalert", "scamdecoded"],
  description="The fake breach settlement text, and how to find a real settlement.",
  caption="Big breaches often end in real settlements, and scammers copy them. A real claim form doesn't charge a fee.",
  sources=[FTC_BREACH, ITG_BREACH], claims=["Scammers use breach news to send fake offers and links (FTC)",
                                            "Legitimate class action settlements don't charge a fee to file a claim"],
  original_element="Walkthrough of a fictional settlement text with the flags lighting up, in the originality/render.mjs style.",
  segments=[
   ("Hook", "Four hundred twelve dollars from a data breach settlement. Just pay a twenty-five dollar processing fee.",
    "'$412, after a $25 fee'", "walkthrough: a text with a payout amount"),
   ("The catch", "The link goes to a lookalike claim page that takes your card, and often your Social Security number "
                 "to 'confirm' you.", "The link takes your card", "walkthrough: a fake claim form"),
   ("The tell", "A real settlement doesn't charge a fee to file a claim. Find it through the court notice or a news "
                "story, not a text.", "Real claims cost $0", "a court building with a $0 tag"),
   ("Do this", "Delete the text. Then do the breach checklist, because the real breach still happened. Link in bio.",
    "Delete it. Do the checklist.", f"{MASCOT} holding a phone"),
  ]),
 dict(date="2027-05-08", look="illustrated", title="SSN in a breach? 2 free locks to turn on today",
  hook="2 free locks protect you when your Social Security number shows up in a breach.",
  thumb="SSN leaked? 2 free locks",
  hashtags=["databreach", "ssn", "creditfreeze", "ippin", "identitytheft", "scamdecoded"],
  description="A credit freeze and an IRS IP PIN: the two free locks after an SSN breach.",
  caption="If a breach letter says your Social Security number was exposed, two free locks do most of the work.",
  sources=[FTC_FREEZE, IPPIN, ITG_BREACH], claims=["A credit freeze is free and stops new accounts being opened in your name (FTC)",
                                                   "An IRS IP PIN stops others e-filing a federal return with your SSN (IRS)"],
  original_element="Illustrated beats: two padlocks, one on a credit report and one on a tax form.",
  segments=[
   ("Hook", "Two free locks, when your Social Security number shows up in a breach letter.",
    "SSN leaked? 2 free locks", f"{MASCOT} holding two padlocks"),
   ("Lock 1", "A credit freeze, at Equifax, Experian and TransUnion. It's free, it doesn't hurt your score, and it stops "
              "new accounts in your name.", "1. Freeze your credit", "a padlock on a credit report"),
   ("Lock 2", "An IRS identity protection PIN. Six digits, free, and nobody can e-file a federal return with your number "
              "without it.", "2. Get an IP PIN", "a padlock on a tax form"),
   ("Do this", "Both links are on our free breach checklist, with the other six steps. Link in bio.",
    "Both links: breach checklist", f"{MASCOT} giving a thumbs up"),
  ]),
 dict(date="2027-05-15", look="quiz pause", title="'Your data is on the dark web': real alert or sales pitch?",
  hook="1 email says your data is on the dark web. Pause: real alert or sales pitch?",
  thumb="Dark web alert? Pause.",
  hashtags=["darkweb", "databreach", "phishing", "privacy", "scamalert", "scamdecoded"],
  description="The 'your info is on the dark web' email, and the free way to check.",
  caption="The FTC warns about emails saying your personal info is for sale on the dark web. Many want you to click, "
          "pay or install something. You can check your email address for free.",
  sources=[FTC_DARKWEB, HIBP], claims=["Scammers send emails claiming your info is for sale on the dark web (FTC)",
                                       "Have I Been Pwned lets you check your email address against known breaches for free"],
  original_element="Quiz format with a real 3-second pause card; the answer beat shows haveibeenpwned.com typed into a browser.",
  segments=[
   ("Hook", "One email. Your personal information was found on the dark web. Scan now to see what's exposed.",
    "'Found on the dark web'", "an email with a skull icon"),
   ("Pause", "Pause. Real alert, or sales pitch? Decide before I tell you.", "Pause: real or pitch?", "a full-screen countdown card"),
   ("Answer", "Usually a pitch, or a phishing link. The FTC warns about these emails. You can check your own email "
              "address for free at have I been pwned dot com, typed in yourself.", "Check free, typed yourself",
    "a browser with haveibeenpwned.com"),
   ("Do this", "If it finds breaches, our free checklist says what to do next, step by step. Link in bio.",
    "Next steps: breach checklist", f"{MASCOT} holding a checklist"),
  ]),
]


def item(p):
    return {"format": "short", "pillar": P_ID, "platforms": ["instagram", "youtube"], "post_on": f"{p['date']} 12:00",
            "topic": "data breach", "look": p["look"], "original_element": p["original_element"],
            "idea_angle": f"Breach checklist push: {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": [seg(*r) for r in p["segments"]], "cta": CTA,
                       "caption": p["caption"] + "\n\n" + PLUG + "\n\n" + CTA, "hashtags": p["hashtags"],
                       "description": p["description"] + " Checklist: " + SITE, "thumbnail_text": p["thumb"],
                       "sources": p["sources"], "claims_to_verify": p["claims"]}}


def main():
    items = [item(p) for p in POSTS]
    assert all(a["look"] != b["look"] for a, b in zip(items, items[1:]))
    for i in items:
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        assert 60 <= w <= 120, (i["script"]["title"], w)
        assert any(ch.isdigit() for ch in i["script"]["hook"].split(".")[0][:60]), i["script"]["hook"]
        assert all(len(s["on_screen_text"].split()) <= 12 for s in i["script"]["segments"])
        assert dt.date.fromisoformat(i["post_on"][:10]).weekday() == 5
    root = HERE.parent.parent
    (root / "breach-shorts-2027.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    rows = ["# Scam Decoded: 5 Shorts for the data breach checklist, Sat Apr 17 – Sat May 15 2027", "",
            "Reels + YouTube Shorts at 12:00 America/New_York, on Saturdays (the slot the weekly plans leave open; the tax "
            "pack ends Apr 10). Each one ends on the free checklist at scamdecoded.netlify.app/breached/. Set it as the bio "
            "link the week these run. Nothing has been posted.", "",
            "| # | Date | Look | Title |", "|---|---|---|---|"]
    for n, i in enumerate(items):
        d = dt.date.fromisoformat(i["post_on"][:10])
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} | {i['look']} | {i['script']['title']} |")
    rows += ["", "Before posting: verify each item's `claims_to_verify` against its `sources` that week."]
    (root / "POSTING_PLAN_BREACH_SHORTS.md").write_text("\n".join(rows) + "\n")
    for n, i in enumerate(items):
        print(n, i["post_on"], i["look"], sum(len(s["narration"].split()) for s in i["script"]["segments"]), i["script"]["title"][:60])


if __name__ == "__main__":
    main()
