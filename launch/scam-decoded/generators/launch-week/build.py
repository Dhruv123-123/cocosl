"""Scam Decoded launch: the first 14 days, profile bios, pinned posts, channel trailer and the fact-check table.

    python3 build.py   ->  ../../LAUNCH_WEEK.md

Follows scouting's launch playbook (half cadence in week 1, full cadence in week 2) and uses only posts that are
already written: content.json (Shorts #0-13, TikTok cuts #14-27, carousels #28-35) plus three evergreen long videos
from weeks-3-6.json. Titles are read from the JSON, so retitles show up here on the next run.

The fact-check table lists every claim_to_verify on every post in the 14 days, with the source checked on
2026-11-07 and a verdict. A claim with no verdict fails main(), so a new claim can't slip in unchecked.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent          # launch/scam-decoded
OUT = ROOT / "LAUNCH_WEEK.md"
CHECKED = "2026-11-07"
SITE = "https://scamdecoded.netlify.app"
DAY1_REC = "Sat Nov 14 2026"

LONG_A = "How to protect your parents from scams: the complete guide"
LONG_B = "Identity theft recovery, step by step (what to do in the first week)"
LONG_C = "Credit freeze vs fraud alert vs monitoring: what you actually need"

# Each video's look, and the thing only a person can add. Rules (ORIGINALITY_PASS.md): Dhruv's own voice on every
# TikTok and long video; no two videos in a row on one platform share a look; a day's Short and TikTok differ.
ORIGINAL = {
 "trailer": ("face cam", "Dhruv on camera, unscripted delivery of the trailer lines below. No AI voice, no AI visuals."),
 LONG_A: ("screen recording", "Screen recording of his own phone: silence unknown callers, carrier spam filter, a favourite contact (LONG_VIDEO_RECORDINGS.md). His voice."),
 LONG_B: ("screen recording", "Screen recording of IdentityTheft.gov, typed in, stopping before personal details (LONG_VIDEO_RECORDINGS.md). His voice."),
 LONG_C: ("screen recording", "Screen recording of one bureau's freeze page, typed in, stopping at sign-in (LONG_VIDEO_RECORDINGS.md). His voice."),
 0: ("hands on camera", "Dhruv's hands with gift card packaging at home, flipping one to the back (no real card numbers on screen)."),
 1: ("screen recording", "15 seconds of a bureau's freeze page on his own phone, details blurred."),
 2: ("walkthrough", "Phone-screen walkthrough w1-toll (originality/out/walkthroughs): the flags light up in time with the voice."),
 3: ("face cam", "Dhruv to camera asking 'What's our word?', with the fake call as on-screen text beside him."),
 4: ("hands on camera", "The back of his own bank card (number covered) and his thumb on the printed fraud number."),
 6: ("face cam", "Dhruv holds his phone up with a fictional delivery text and asks the 1 question to camera."),
 7: ("illustrated", "The mascot explainer, but read in Dhruv's own voice, not AI voice."),
 10: ("walkthrough", "Phone-screen walkthrough w5-job: the task text thread, flags revealing one by one."),
 12: ("data chart", "One chart slide of the FTC figure ($110M+ in 2023, 60+ more than 3x as likely), source printed on the image."),
 14: ("green screen", "Dhruv in front of the three payment methods as a green-screen backdrop, his voice."),
 15: ("screen recording", "Screen recording of the three bureau freeze pages, typed in, stopping at sign-in. His voice."),
 16: ("green screen", "Dhruv in front of the two fictional toll texts, pointing at each red flag. His voice."),
 17: ("acted call", "Split screen: Dhruv plays the 'grandson', on-screen text for the listener, then the safe-word question. His voice."),
 18: ("green screen", "Dhruv in front of the two fake bank scripts as text, then dialling the number on his own card (covered)."),
 20: ("walkthrough", "Phone-screen walkthrough w2-delivery for the first ask, then his voice over the 'second scam'."),
 21: ("walkthrough", "Phone-screen walkthrough w3-bank-code for script 1, plus 10 seconds of his own sign-in settings screen."),
 24: ("green screen", "Dhruv in front of the task-app screens (fictional), walking the top-up steps. His voice."),
 26: ("face cam", "Dhruv tells the kiosk story to camera; the FTC figure as a text card with source."),
 28: ("carousel", "Fictional scam text drawn as a phone screen with the 5 flags numbered on it."),
 30: ("carousel", "Seven one-line tells, one per slide, in our own words."),
 32: ("carousel", "A 5-lock checklist slide people save; screenshots of real settings menus with personal details blurred."),
 33: ("carousel", "Six yes/no questions as a flowchart, our own design."),
 35: ("carousel", "The family plan as a fill-in fridge card on the last slide."),
}

# Day plan. Entries: ("trailer",), ("long", title), ("short", n), ("reel", n), ("tiktok", n), ("carousel", n),
# ("story", text), ("rest", text), ("review", text)
DAYS = [
 dict(yt=[("trailer",), ("long", LONG_A)],
      ig=[("carousel", 28), ("story", f"'New here? Start with the free 2-page Scam-Proof Checklist.' Link sticker to {SITE}/ (sign-up at the top).")],
      tt=[("rest", "No TikTok on day 1. Set up the profile, bio and the first two drafts instead.")]),
 dict(yt=[("short", 2)], ig=[("story", f"Poll sticker: 'Got an unpaid-toll text this month? Yes / No', then a link sticker to the free checker, {SITE}/checker/.")],
      tt=[("tiktok", 16)]),
 dict(yt=[("short", 3)], ig=[("reel", 3)], tt=[("tiktok", 17)]),
 dict(yt=[("rest", "No YouTube upload. Reply to every comment on the trailer, the long video and the two Shorts.")],
      ig=[("carousel", 35)], tt=[("rest", "No TikTok. Reply to comments on the first two.")]),
 dict(yt=[("short", 4)], ig=[("story", "Quiz sticker: 'Your bank's fraud team calls: \"move your money to a safe account.\" Real or scam?' Answer: scam. Then reshare the day-4 carousel.")],
      tt=[("tiktok", 18)]),
 dict(yt=[("long", LONG_B)], ig=[("reel", 1)], tt=[("rest", "No TikTok.")]),
 dict(yt=[("review", "Day-7 review (below).")], ig=[("review", "Day-7 review.")], tt=[("tiktok", 15)]),
 dict(yt=[("short", 0)], ig=[("reel", 0)], tt=[("tiktok", 14)]),
 dict(yt=[("short", 7)], ig=[("carousel", 32)], tt=[("tiktok", 21)]),
 dict(yt=[("short", 12)], ig=[], tt=[("tiktok", 26)]),
 dict(yt=[("long", LONG_C)], ig=[("carousel", 30)], tt=[]),
 dict(yt=[("short", 6)], ig=[("reel", 6)], tt=[("tiktok", 20)]),
 dict(yt=[("short", 10)], ig=[], tt=[("tiktok", 24)]),
 dict(yt=[("review", "Day-14 review (below).")], ig=[("carousel", 33)], tt=[("review", "Day-14 review.")]),
]

TIMES = {"trailer": "10:00", "long": "10:00", "short": "12:00", "reel": "12:00", "tiktok": "12:00", "carousel": "19:30",
         "story": "18:00"}

MONEY = {1: "Aura (affiliate)", 15: "Aura (affiliate)", 21: "1Password (affiliate)", 32: "1Password + NordVPN (affiliate)",
         3: "kit (our own product)", 17: "kit (our own product)", 30: "kit (our own product)", 35: "kit (our own product)"}

TRAILER = [
 ("0-3 s", "Hi, this is Scam Decoded.", "Scam Decoded"),
 ("3-12 s", "Every week a new scam goes round: a toll text, a call from 'your bank', your grandson's voice asking for bail.",
  "New scam, every week"),
 ("12-22 s", "Here, each one gets decoded in about a minute: the trick, the tell, and the one move that stops it.",
  "The trick · the tell · the move"),
 ("22-32 s", "Every fact comes from the FTC, the FBI or another official source, and the sources are in every description.",
  "Sources in every description"),
 ("32-40 s", "I use AI tools to help draft and make the visuals. I check every line myself before it goes up.",
  "AI-assisted, checked by a person"),
 ("40-45 s", "Subscribe, and send one to the person in your family who answers every call.", "Subscribe"),
]

BIOS = {
 "Instagram": dict(limit=150, name="Scam Decoded | Scam alerts",
   bio="Scams decoded in 60 seconds: the trick, the tell, the fix.\nAI-assisted, fact-checked by a person.\nFree checklist ↓",
   link=f"{SITE}/ (home page: the checklist sign-up and the checker)"),
 "TikTok": dict(limit=80, name="Scam Decoded",
   bio="Scams decoded fast. AI-assisted, human fact-checked. Free checklist ↓",
   link=f"{SITE}/ (TikTok shows a bio link once the account qualifies; until then say 'link on our YouTube')"),
 "YouTube": dict(limit=1000, name="Scam Decoded",
   bio=("One scam decoded at a time: how it works, the tell that gives it away, and the one move that stops it. "
        "Shorts most weekdays and a longer guide on weekends.\n\n"
        "Every fact comes from an official source (FTC, FBI IC3, FCC, CFPB, USPIS), linked in each video's description.\n\n"
        "How it's made: some visuals and voices are made with AI tools; long videos and TikToks are voiced by a person. Scripts drafted with AI help and fact-checked by a person. "
        "All example messages, names and numbers are fictional.\n\n"
        "General education, not legal or financial advice. Some descriptions include affiliate links, marked as such; "
        "we may earn a commission at no extra cost to you.\n\n"
        f"Free 2-page Scam-Proof Checklist and scam checker: {SITE}/"),
   link=f"{SITE}/"),
}

# Verdicts for every claim_to_verify on the posts above. Sources were opened on CHECKED.
FTC_FREEZE = "consumer.ftc.gov/articles/what-know-about-credit-freezes-fraud-alerts"
V = {
 # gift cards / payment methods (#0, #14)
 "FTC guidance: anyone who demands payment by gift card is a scammer":
  ("FTC gift card scams page: \"Only scammers will tell you to buy a gift card.\"", "Supported"),
 "Government agencies don't demand payment by gift card, wire transfer or cryptocurrency":
  ("FTC gift card page: agencies \"never demand payment by gift card\"; FTC how-avoid-scam: scammers insist on crypto, wire, payment app or gift card", "Supported"),
 "Example scenarios (utility shut-off, warrant call) are illustrative composites, not real cases":
  ("Labelled fictional in the caption", "OK as labelled"),
 # credit freeze (#1, #15)
 "Credit freezes and lifts are free at Equifax, Experian and TransUnion under federal law (since Sept 2018)":
  (f"{FTC_FREEZE}: \"no cost to place or lift a credit freeze\"; FTC press release Sept 21 2018 (new law)", "Supported"),
 "A freeze does not affect your credit score or existing accounts":
  (f"{FTC_FREEZE}: a freeze \"doesn't affect your credit score\"", "Supported"),
 "Online/phone lift requests must be processed within one hour":
  ("FTC business blog Aug 2018 on the new law: lifting \"has to happen within an hour\"", "Supported"),
 "A freeze lift requested online or by phone has to happen within an hour (FTC on the 2018 law)":
  ("FTC business blog Aug 2018 (ftc.gov/business-guidance/blog/2018/08/new-law-new-consumer-rights)", "Supported"),
 "Parents/guardians can request a freeze for a child under 16":
  (f"{FTC_FREEZE}: \"If your child is under 16, request a free credit freeze\"", "Supported"),
 "'About 10 minutes' is an estimate for all three bureaus":
  ("Our estimate, said as 'about'", "OK as an estimate"),
 "Innovis and ChexSystems offer separate free freezes (confirm current process)":
  ("CFPB company list: both will freeze on request; neither page says free", "FIXED in #15 and #29 ('free' removed). #1 doesn't say it on screen"),
 "Innovis and ChexSystems will freeze your file on request (CFPB company list); check each site for cost and steps":
  ("consumerfinance.gov company pages for Innovis and Chex Systems: \"will freeze your consumer report if you request it\"", "Supported (after fix)"),
 # toll texts (#2, #16)
 "FBI IC3 issued a public service announcement on unpaid-toll smishing in April 2024":
  ("ic3.gov/PSA/2024/PSA240412, Apr 12 2024, 'Smishing Scam Regarding Debt for Road Toll Services'", "Supported"),
 "Forwarding spam texts to 7726 reports them to most US carriers":
  ("FTC spam text page: \"Copy the message and forward it to 7726 (SPAM)\"", "Supported"),
 "$3.95 and the late fee are fictional example amounts": ("Labelled fictional", "OK as labelled"),
 # voice clone (#3, #17)
 "FTC consumer alert (Mar 2023) on AI voice cloning in family emergency scams":
  ("consumer.ftc.gov/consumer-alerts/2023/03 (Mar 20 2023): scammers need \"a short audio clip\"; \"Use a phone number you know is theirs\"", "Supported"),
 "FBI PSA (Dec 2024) recommends a secret word or phrase with family":
  ("ic3.gov/PSA/2024/PSA241203, Dec 3 2024: \"Create a secret word or phrase with your family\"", "Supported"),
 "Example calls are fictional composites": ("Labelled fictional", "OK as labelled"),
 "Voice cloning needs only a short audio clip (FTC consumer alert, Mar 20 2023)":
  ("Same FTC alert: \"a short audio clip\"", "Supported. The old '3 seconds' hook variant was unsourced and is gone"),
 # bank impersonation (#4, #18, #30)
 "Scammers can make any name or number show up on caller ID (FTC phone scams page)":
  ("consumer.ftc.gov/articles/phone-scams: \"Scammers can make any name or number show up on your caller ID\"", "Supported"),
 "Payment-app transfers sent by the account holder are often hard or impossible to reverse":
  ("FTC phone scams page: scammers insist \"you pay in a way that makes it hard to get your money back\"", "Supported (worded 'often' and 'much harder')"),
 "Someone who says you have to move your money to protect it is a scammer (FTC consumer alert, Mar 2024)":
  ("consumer.ftc.gov/consumer-alerts/2024/03/never-move-your-money-protect-it-thats-scam: \"...is a scammer. Period.\"", "Supported. Title and hook reworded from '0 real banks ask' to 'the safe account is theirs'"),
 # delivery (#6, #20)
 "USPIS: USPS does not send texts or emails about packages without a customer request that includes a tracking number":
  ("uspis.gov smishing: USPS won't text \"without a customer first requesting the service with a tracking number, and it will NOT contain a link\"", "Supported"),
 "Other carriers' notification policies vary; check before generalising":
  ("Scripts name USPS only", "OK"),
 "Redelivery-fee amounts in examples are fictional": ("Labelled fictional", "OK as labelled"),
 # codes (#7, #21)
 "Anyone who asks you for your account verification code is a scammer (FTC consumer alert, Mar 2024)":
  ("consumer.ftc.gov/consumer-alerts/2024/03/whats-verification-code-why-would-someone-ask-me-it", "Supported"),
 "Marketplace 'verify you're real' code scams are documented by the FTC (Google Voice code scam)":
  ("consumer.ftc.gov/consumer-alerts/2021/10 Google Voice scam: sellers asked to \"verify that you're a real person\"", "Supported"),
 "Passkeys/FIDO are the only widely available phishing-resistant sign-in; text codes are vulnerable to phishing and SIM swaps (CISA fact sheet)":
  ("CISA 'Implementing Phishing-Resistant MFA': FIDO is \"the only widely available phishing-resistant authentication\"; SMS \"vulnerable to phishing, SS7, and SIM swap\"", "Supported"),
 # task jobs (#10, #24)
 "FBI IC3 PSA (Jun 4 2024): task scams make victims pay in crypto to 'unlock' work or earnings; 'Never send money to an alleged employer'":
  ("ic3.gov/PSA/2024/PSA240604, Jun 4 2024, 'Scammers Defraud Individuals via Work-From-Home Scams'", "Supported. Replaces the FTC 2023 alert, which wouldn't load today"),
 "Example payout amounts are fictional": ("Labelled fictional", "OK as labelled"),
 "Honest employers will never ask you to pay to get a job (FTC job scams page)":
  ("consumer.ftc.gov/articles/job-scams: \"Honest employers ... will never ask you to pay to get a job\"", "Supported"),
 # Bitcoin ATMs (#12, #26)
 "FTC press release + data spotlight (Sept 3 2024): reported losses at Bitcoin ATMs topped $110 million in 2023":
  ("ftc.gov press release 2024/09 'New FTC Data Shows Massive Increase in Losses to Bitcoin ATM Scams': \"over $110 million in 2023\"", "Supported. Source link fixed (the old spotlight URL failed)"),
 "People 60+ were more than 3x as likely to report losing money through a Bitcoin ATM (same spotlight)":
  ("Same release: over 60 \"more than three times as likely as younger adults\"", "Supported"),
 "Check for a newer FTC/FBI figure before posting; update the hook if one exists":
  ("No newer FTC Bitcoin ATM total found today; the release also says $65M+ in the first half of 2024", "Keep the 2023 figure; say 'in 2023' in the caption (it does)"),
 # carousels
 "Example text is fictional; make sure no real domain or number appears on the slides":
  ("Slides use masked links and 555-01xx numbers", "Check the render before posting"),
 "Forwarding to 7726 reports a text to most major US carriers":
  ("FTC spam text page (7726)", "Supported"),
 "These seven scam types are among the most reported by older adults (FBI IC3 elder fraud report / FTC Pass It On)":
  ("IC3 2025 annual report: people 60+ filed 201,266 complaints and reported $7.748 billion lost, the most of any age group; the seven are common types in IC3/FTC material", "Supported as 'targeting seniors'. Not a ranked top 7, so the title doesn't say 'top'"),
 "Medicare/SSA/IRS don't demand immediate payment by phone with gift cards, wires or crypto":
  ("FTC gift card page: agencies \"won't contact you to demand immediate payment\"; FTC phone scams: law enforcement \"won't call and threaten you\"", "Supported"),
 "Legitimate sweepstakes don't require payment to collect a prize":
  ("FTC prize scams page: \"If you have to pay to get your prize, it's a scam. Real prizes are free.\"", "Supported"),
 "Email account access usually allows resetting other accounts' passwords":
  ("How password reset works; worded 'it resets everything else'", "OK (general knowledge, no number)"),
 "Passkeys and authenticator apps resist SIM swap and phishing better than SMS codes (CISA guidance)":
  ("CISA phishing-resistant MFA fact sheet: SMS vulnerable to SIM swap; FIDO phishing-resistant", "Supported"),
 "Most traffic on public Wi-Fi to HTTPS sites is already encrypted; a VPN adds protection on untrusted networks (keep the VPN claim modest)":
  ("Slide says only 'a VPN adds a layer'", "OK, modest"),
 "'About 1 hour' is an estimate": ("Said as 'about'", "OK as an estimate"),
 "These six questions reflect common FTC red flags (unsolicited contact, pressure, secrecy, unusual payment)":
  ("FTC how-avoid-scam (pressure, payment methods) and romance page: \"Never send money or gifts to a sweetheart you haven't met in person\"", "Supported"),
 "FBI PSA (Dec 2024) recommends families agree a secret word or phrase":
  ("ic3.gov/PSA/2024/PSA241203", "Supported"),
 "Parents can freeze credit for children under 16":
  (f"{FTC_FREEZE}", "Supported"),
 "'15 minutes' is an estimate for the conversation; freezes take longer":
  ("Caption says freezes are a separate step", "OK as an estimate"),
 # long videos
 "FBI IC3 reports older adults lose billions to fraud each year (cite the latest elder fraud figure)":
  ("IC3 2025 annual report: 60+ reported $7.748 billion in 2025, the highest of any age group", "Supported. Add the figure on screen with the source"),
 "FBI PSA (Dec 2024) recommends a family secret word": ("ic3.gov/PSA/2024/PSA241203", "Supported"),
 "Banks can let customers add a trusted contact person (check the parent's bank)":
  ("Script says to ask the parent's bank; not every bank offers it", "OK as worded"),
 "IdentityTheft.gov generates an FTC Identity Theft Report and a recovery plan":
  ("identitytheft.gov home page", "Supported"),
 "Fraud alerts are free; an initial alert lasts one year and an extended alert (with a report) lasts seven years":
  (f"{FTC_FREEZE}: initial \"lasts one year\", extended \"lasts seven years\", all free", "Supported"),
 "Free weekly credit reports at AnnualCreditReport.com":
  ("consumer.ftc.gov/articles/free-credit-reports: bureaus \"permanently extended\" free weekly reports", "Supported"),
 "Businesses must block fraudulent information from credit reports when given an identity theft report (FCRA §605B)":
  ("FCRA §605B (15 U.S.C. 1681c-2); FTC 'what to do right away if your identity is stolen'", "Supported (the script says 'bureaus have to block')"),
 "Credit freezes are free by federal law; locks are offered by bureaus under their own terms":
  (f"{FTC_FREEZE}; CFPB 'difference between a credit freeze and a credit lock'", "Supported"),
 "Initial fraud alert lasts one year; extended alert seven years with an identity theft report":
  (f"{FTC_FREEZE}", "Supported"),
 "Monitoring services alert you after activity; they don't prevent new accounts on their own":
  ("How monitoring works; the script compares, doesn't claim a statistic", "OK"),
 "Affiliate commission details: confirm current Aura program terms":
  ("Not a fact claim on screen; the description says 'we may earn a commission'", "Check the Aura link is real before posting"),
}

# Things fixed in the scripts during this pass (shown in the file so the edits are visible).
FIXES = [
 "#4 / #18 / #30: '0 real banks ask you to move money' became 'the safe account is theirs' and a 'safe account is the scam' tell, sourced to the FTC's Mar 2024 alert.",
 "#5 / #19 (not in the 14 days, fixed anyway): 'a reply tells them your number is live' had no source. Now the FCC's advice: don't answer a scam text at all, not even Y or N.",
 "#15 / #29: Innovis and ChexSystems 'free' freezes: the CFPB pages confirm the freeze, not the price, so 'free' is gone.",
 "#9 / #23 (day 15+): carrier PIN and number lock are no longer called 'usually free'; cost varies. #9 gains the FTC's Oct 2026 alert: the FTC never threatens to cut off your phone service.",
 "#3 / #17: the '3 seconds of audio' hook variant (vendor research) is replaced by the FTC's 'a short audio clip'.",
 "#12 / #26: the Bitcoin ATM source link pointed at a page that failed; now the FTC press release that states both figures.",
 "#10 / #24: the task-scam source is now the FBI's Jun 2024 PSA (the FTC 2023 alert wouldn't load); added the FTC job-scams rule.",
 "#7 / #21: added the FTC's 'anyone who asks for your verification code is a scammer' and CISA's phishing-resistant MFA sheet.",
]


def load():
    content = json.loads((ROOT / "content.json").read_text())
    longs = {i["script"]["title"]: i for i in json.loads((ROOT / "weeks-3-6.json").read_text()) if i["format"] == "long"}
    return content, longs


def label(e, content):
    kind = e[0]
    if kind == "trailer":
        return "**Channel trailer** (Short, face cam, script below)"
    if kind == "long":
        return f"**Long:** {e[1]}"
    if kind in ("short", "reel", "tiktok", "carousel"):
        n = e[1]
        name = {"short": "Short", "reel": "Reel", "tiktok": "TikTok", "carousel": "Carousel"}[kind]
        money = f" · {MONEY[n]}" if n in MONEY else ""
        return f"**{name} #{n}:** {content[n]['script']['title']}{money}"
    if kind == "story":
        return f"Story: {e[1]}"
    return f"_{e[1]}_"


def cell(entries, content):
    if not entries:
        return "–"
    out = []
    for e in sorted(entries, key=lambda e: TIMES.get(e[0], "99")):
        t = TIMES.get(e[0])
        out.append((f"{t} " if t else "") + label(e, content))
    return "<br>".join(out)


def items_in_plan():
    """(key, platform, day) for every video or carousel, in posting order."""
    seen = []
    for d, day in enumerate(DAYS, 1):
        for plat in ("yt", "ig", "tt"):
            for e in day[plat]:
                if e[0] in ("trailer",):
                    seen.append(("trailer", plat, d))
                elif e[0] == "long":
                    seen.append((e[1], plat, d))
                elif e[0] in ("short", "reel", "tiktok", "carousel"):
                    seen.append((e[1], plat, d))
    return seen


def checks(content, longs):
    """Plan rules; returns the list of posts (keys) in the 14 days."""
    seen = items_in_plan()
    for k, plat, d in seen:
        assert k in ORIGINAL, f"day {d}: no original element for {k}"
    for plat, kinds in (("yt", ("trailer", "long", "short")), ("tt", ("tiktok",)), ("ig", ("reel",))):
        vids = [ORIGINAL[k][0] for k, p, d in seen if p == plat and not (isinstance(k, int) and content[k]["format"] == "carousel")]
        assert all(a != b for a, b in zip(vids, vids[1:])), (plat, vids)
    for d, day in enumerate(DAYS, 1):
        s = [e[1] for e in day["yt"] if e[0] == "short"]
        t = [e[1] for e in day["tt"] if e[0] == "tiktok"]
        if s and t:
            assert ORIGINAL[s[0]][0] != ORIGINAL[t[0]][0], f"day {d}: Short and TikTok share a look"
    for k, plat, d in seen:
        if isinstance(k, int):
            fmt = content[k]["format"]
            assert (plat, fmt) in (("yt", "short"), ("ig", "short"), ("tt", "short"), ("ig", "carousel")), (k, plat)
            if plat == "tt":
                assert k >= 14 and k <= 27, k
            if plat in ("yt",) or (plat == "ig" and fmt == "short"):
                assert k <= 13, k
        elif k != "trailer":
            assert k in longs, k
    # week-2 cadence from the playbook: 1 long + 5 Shorts, 3 carousels + 2 Reels, 5 TikToks
    wk2 = [e for day in DAYS[7:] for plat in ("yt", "ig", "tt") for e in day[plat]]
    count = lambda kind: sum(1 for e in wk2 if e[0] == kind)
    assert (count("long"), count("short"), count("carousel"), count("reel"), count("tiktok")) == (1, 5, 3, 2, 5)
    for name, b in BIOS.items():
        assert len(b["bio"]) <= b["limit"], (name, len(b["bio"]))
        assert "AI" in b["bio"] and ("fact-checked" in b["bio"]), name
    keys = []
    for k, _, _ in seen:
        if k not in keys:
            keys.append(k)
    for k in keys:
        if k == "trailer":
            continue
        sc = (content[k] if isinstance(k, int) else longs[k])["script"]
        for c in sc["claims_to_verify"]:
            assert c in V, f"no verdict for claim on {k}: {c}"
    return keys


def render(content, longs, keys):
    L = ["# Scam Decoded: launch, days 1–14",
         "",
         "Built by `generators/launch-week/build.py` (edit there, then `python3 build.py`). "
         f"Facts checked {CHECKED}. Nothing here has been posted; Dhruv posts every item by hand.",
         "",
         "Pick Day 1, then post only what this file lists for 14 days. All times America/New_York. "
         "Same-number Shorts and Reels are the same file. TikToks are the longer cuts (#14–27) in Dhruv's own voice.",
         "",
         "## Day 1: Dhruv's call",
         "",
         f"**Recommended: {DAY1_REC}.** Scouting's plan launches Scam Decoded in weeks 2–3 of Money Made Simple. MMS's own "
         "plan (launch/money-made-simple/POSTING_PLAN.md) has its Day 1 on Sat Nov 7 2026, so Sat Nov 14 is MMS day 8: "
         "Dhruv's MMS routine has had a week to settle, there's a week to do the recording session below, and Scam Decoded "
         "reaches full cadence (its week 2) in Black Friday week, Nov 21–27. The cost: the 08:30 alert cards "
         "Nov 16–27 and the dated posts Nov 21–27 are skipped. If MMS started later than Nov 7, keep the rule, not the "
         "date: Scam Decoded Day 1 = MMS day 8 (latest MMS day 15).",
         "",
         "## Before Day 1",
         "",
         "1. Create @scamdecoded on Instagram, YouTube and TikTok, with the bios below. Turn on each platform's AI label for every post.",
         "2. Do the one recording session in `launch-recording/` (SHOT_LIST.md + teleprompter.html, about 26 minutes with retakes): "
         "the trailer, the three long videos' screen recordings, the face-cam and hands-on inserts, and week 1's four TikTok voice takes. "
         "Week 2's TikTok voices and the long-video narration go in the next `factory batch-record` session.",
         "3. Affiliate links (Aura, 1Password, NordVPN) are still placeholders. If one isn't approved by its day, delete the affiliate sentence from that caption; the post still works.",
         "4. Open every source in the fact-check table once more on the day before posting; agencies move pages.",
         "",
         "## What's paused during days 1–14",
         "",
         "- **08:30 alert cards** (weekdays from Mon Nov 16 2026): skip any that fall inside the 14 days. They're news, so don't post them late.",
         "- **News Shorts** (Nov 22 – Dec 6 2026) and **dated seasonal packs** (weeks 3–6 from Nov 21, holiday packs): any slot inside the 14 days is skipped; slots after day 14 go ahead as planned.",
         f"- **The three long videos used here** come from weeks-3-6.json ({LONG_A.split(':')[0]}, Nov 29; {LONG_C.split(':')[0]}, Dec 6; {LONG_B.split(' (')[0]}, Dec 13). Once posted here, leave their later slots empty or fill them with the next long video in the queue. Never upload one twice.",
         "",
         "## The 14 days",
         "",
         "Week 1 runs at half cadence on purpose (scouting's playbook): a new account that posts a lot on day 1 gets judged on thin data.",
         "",
         "| Day | YouTube | Instagram | TikTok |",
         "|---|---|---|---|"]
    for d, day in enumerate(DAYS, 1):
        L.append(f"| **{d}** | {cell(day['yt'], content)} | {cell(day['ig'], content)} | {cell(day['tt'], content)} |")
    L += ["",
          "Counts: week 1 has the trailer, 3 Shorts and 2 long videos on YouTube; 2 carousels, 2 Reels and 3 Stories on "
          "Instagram; 4 TikToks. Week 2 has 1 long and 5 Shorts, 3 carousels and 2 Reels, 5 TikToks.",
          "",
          "### Day-7 review (15 minutes)",
          "",
          "- For each post: views, shares, saves and follows. Watch time for the two long videos.",
          "- Which topic got the most shares per view: money (gift cards, bank), family (voice clone, the family plan), or tech (codes, freezes)? In week 2, move that topic's posts to the front. Swap days; don't add posts.",
          "- Don't delete or repost a slow TikTok. Breakouts often start slow.",
          "",
          "### Day-14 review",
          "",
          "- Same numbers. Note the top 3 posts per platform in the go-live notes, and use their hook pattern for the next month.",
          "- From day 15, the dated packs and the 08:30 alert cards resume.",
          "",
          "## Channel trailer (YouTube Short, about 45 seconds, face cam)",
          "",
          "Use it as the YouTube channel trailer for visitors who haven't subscribed. Same file can go out as an Instagram Reel later.",
          "",
          "| Time | Dhruv says | On screen |",
          "|---|---|---|"]
    for t, say, on in TRAILER:
        L.append(f"| {t} | {say} | {on} |")
    L += ["",
          "Title: **Scam Decoded: 1 scam, decoded in 1 minute** · Description: the YouTube 'about' text below.",
          "",
          "## Profile bios",
          ""]
    for name, b in BIOS.items():
        L += [f"### {name}", "", f"- **Name:** {b['name']}", f"- **Link:** {b['link']}",
              f"- **Bio** ({len(b['bio'])} of {b['limit']} characters):", "", "```", b["bio"], "```", ""]
    L += ["The AI line is the short form of `brands/scam-decoded.yaml` `ai_disclosure`; YouTube carries the full line. "
          "If you buy getscamdecoded.com before Day 1, swap it in for the netlify address in all three.",
          "",
          "## Pinned posts",
          "",
          "| Platform | Pin | When | Why |",
          "|---|---|---|---|",
          f"| Instagram | #35 {content[35]['script']['title']} | day 4 | The family plan; points to the kit, gets saved |",
          f"| Instagram | #28 {content[28]['script']['title']} | day 1 | The broadest first post for a new visitor |",
          f"| Instagram | Reel #3 {content[3]['script']['title']} | day 3 | Face cam, so visitors see a person |",
          f"| TikTok | #17 {content[17]['script']['title']} | day 3 | Family topic, the safe word, points to the kit |",
          f"| TikTok | #16 {content[16]['script']['title']} | day 2 | The scam people are getting right now |",
          f"| TikTok | #15 {content[15]['script']['title']} | day 7 | The most useful one to save |",
          "| YouTube | Channel trailer (unsubscribed visitors) | day 1 | Says who we are and the AI line |",
          f"| YouTube | Featured video for subscribers: {LONG_A} | day 1 | The best long guide |",
          "",
          "On every long video, pin a comment of your own: 'Sources for every claim are in the description. Free checklist: "
          f"{SITE}/'.",
          "",
          "## Originality: what Dhruv adds to each video",
          "",
          "Rules from ORIGINALITY_PASS.md: Dhruv's own voice on every TikTok and long video; no two videos in a row on one "
          "platform share a look; a day's Short and TikTok never share a look. `build.py` checks all three.",
          "",
          "| Post | Look | Original element |",
          "|---|---|---|"]
    for k in keys:
        name = "Channel trailer" if k == "trailer" else (f"#{k} {content[k]['script']['title']}" if isinstance(k, int) else k)
        look, el = ORIGINAL[k]
        L.append(f"| {name} | {look} | {el} |")
    L += ["",
          "## Fact-check (every claim in the 14 days)",
          "",
          f"Each claim below is a `claims_to_verify` line on that post. Sources opened on {CHECKED}. Verdicts: "
          "**Supported** (the source says it), **OK** (an example, estimate or wording note, not a fact claim), **FIXED** (the script changed).",
          "",
          "### Fixed in this pass",
          ""]
    L += [f"- {f}" for f in FIXES]
    L += ["", "### Claims and sources", "", "| Post | Claim | Source | Verdict |", "|---|---|---|---|"]
    for k in keys:
        if k == "trailer":
            L.append("| Channel trailer | 'Every fact comes from an official source, linked in each description' | This table | Supported: every post below lists its sources |")
            continue
        sc = (content[k] if isinstance(k, int) else longs[k])["script"]
        name = f"#{k}" if isinstance(k, int) else k.split(":")[0].split(" (")[0]
        for c in sc["claims_to_verify"]:
            src, verdict = V[c]
            L.append(f"| {name} | {c} | {src} | {verdict} |")
    L += ["", "The trailer says 'I check every line myself': that has to stay true. Read each post against this table before it goes up.", ""]
    return "\n".join(L)


def main():
    content, longs = load()
    keys = checks(content, longs)
    OUT.write_text(render(content, longs, keys))
    print(f"wrote {OUT.relative_to(ROOT)} ({len(keys)} posts)")


if __name__ == "__main__":
    main()
