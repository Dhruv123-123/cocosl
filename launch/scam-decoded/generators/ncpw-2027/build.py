"""National Consumer Protection Week pack, Sun Feb 28 - Sat Mar 6 2027 (consumer.ftc.gov/ncpw).

    python3 build.py   ->  ../../ncpw-2027.json and ../../POSTING_PLAN_NCPW_2027.md

The FTC calls NCPW "a time to talk about frauds, scams, and consumer rights", so the week runs both:
  * 5 scam alerts, Mon Mar 1 - Fri Mar 5 (sites/scam-decoded/content/alerts/53-57), 08:30 cards like every weekday;
  * 2 carousels at 19:30: Sun Feb 28 (5 rights you already have) and Fri Mar 5 (the week's 5 scams in one list);
  * 1 long video, Sat Mar 6 10:00 (the Sunday 10:00 slots either side are taken by weeks 13-21 #67 and #68).
Alerts are weekday-only (the card test enforces it), so the weekend ends of the week are the kickoff carousel and the
long video. All three posts cite FTC pages; the FTC says its consumer education material is public domain.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
sys.path.insert(0, str(ROOT))
from common import CTA, MASCOT, seg  # noqa: E402
from long_originals import apply as add_original_elements  # noqa: E402
from long_examples import chapters  # noqa: E402

NCPW = "https://consumer.ftc.gov/ncpw"
COOLING = "https://consumer.ftc.gov/articles/buyers-remorse-ftcs-cooling-rule-may-help"
DISPUTE = "https://consumer.ftc.gov/articles/using-credit-cards-and-disputing-charges"
REPORTS = "https://consumer.ftc.gov/articles/free-credit-reports"
CREDIT_FIX = "https://consumer.ftc.gov/articles/fixing-your-credit-faqs"
DEBT = "https://consumer.ftc.gov/articles/fake-abusive-debt-collectors"
RECOVERY = "https://consumer.ftc.gov/articles/refund-and-recovery-scams"
FTC_IMP = "https://consumer.ftc.gov/consumer-alerts/2023/07/ftc-wont-demand-money-threaten-you-or-promise-you-prize"
TRIALS = "https://consumer.ftc.gov/articles/getting-and-out-free-trials-auto-renewals-and-negative-option-subscriptions"
CHECKER = "Not sure about a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends nothing anywhere."
SEASON = "National Consumer Protection Week 2027"
P_RIGHTS = "identity theft and credit freezes"
P_TEXT = "text and email scams, decoded"


def slides(cover, items, save, cover_vis):
    out = [("Hook", "", cover, cover_vis)]
    out += [(str(i), n, o, v) for i, (n, o, v) in enumerate(items, 1)]
    out.append(("Save this", save, "Save it. Send it to the person who handles the bills.", f"{MASCOT} giving a thumbs up"))
    return out


CAROUSELS = [
 dict(date="2027-02-28", time="19:30", look="checklist", pillar=P_RIGHTS, topic="consumer rights",
  title="National Consumer Protection Week: 5 rights you already have",
  hook="5 consumer rights most people never use, for National Consumer Protection Week.",
  thumb="5 rights. All free.",
  hashtags=["consumerrights", "ncpw", "moneytips", "ftc", "scamdecoded"],
  description="Five consumer rights from the FTC's own pages, for National Consumer Protection Week (Feb 28 - Mar 6 2027).",
  caption="It's National Consumer Protection Week, which the FTC calls a time to talk about frauds, scams and consumer "
          "rights. Here are 5 rights you already have, each from the FTC's own pages. Save it for the day you need one.",
  sources=[NCPW, COOLING, DISPUTE, REPORTS, CREDIT_FIX, DEBT],
  claims=["FTC: NCPW 2027 runs February 28 - March 6",
          "FTC Cooling-Off Rule: cancel until midnight of the third business day; sales of $25+ at home, $130+ at temporary locations",
          "FTC: a billing-error letter must reach the card issuer within 60 days after the first bill with the error",
          "FTC: free credit reports from each bureau once a week at AnnualCreditReport.com",
          "FTC: disputing mistakes on your credit report is free",
          "FTC: debt collectors must give the creditor and amount within 5 days of first contact; dispute within 30 days"],
  original_element="Slide 6 is a fill-in 'my rights' card (bank dispute address, credit report date) drawn for this carousel.",
  segments=slides("5 rights you already have", [
   ("Bought something at your door, or at a pop-up event? The FTC's Cooling-Off Rule lets you cancel until midnight of "
    "the third business day, for sales of $25 or more at home, or $130 or more at a temporary location.",
    "1. Cancel door sales within 3 business days", "a front door with a calendar showing 3 days"),
   ("A wrong charge on your credit card? Your letter has to reach the card company within 60 days after the first bill "
    "with the error, at the billing disputes address.", "2. Dispute card errors within 60 days", "an envelope addressed to Billing Disputes"),
   ("You can see your credit report from each of the three bureaus free, every week, at AnnualCreditReport.com, the "
    "only official site.", "3. Free credit reports, every week", "three report pages side by side"),
   ("Found a mistake? Disputing it with the bureau is free. Anyone charging you first to 'fix' your credit is breaking "
    "the law.", "4. Fix real errors yourself, free", "a pencil correcting a line on a report"),
   ("A collector calls? They must tell you the creditor and the amount within 5 days. Don't recognize it? Dispute it "
    "within 30 days and they have to stop until they check.", "5. Ask a collector to prove it", "a phone with a question mark"),
  ], "Report scams, and companies that ignore these rights, at ReportFraud.ftc.gov.", "a shield made of five checkmarks")),
 dict(date="2027-03-05", time="19:30", look="data", pillar=P_TEXT, topic="NCPW scam recap",
  title="This week's 5 scam alerts, in 1 list to save",
  hook="5 scams, 5 days of National Consumer Protection Week, and 1 list to send to your family.",
  thumb="5 scams, 1 list",
  hashtags=["scamalert", "ncpw", "consumerprotection", "fraudprevention", "scamdecoded"],
  description="The five scam alerts from National Consumer Protection Week 2027, each with its tell and its FTC source.",
  caption="One scam alert every day of National Consumer Protection Week. Here they are in one list: recovery fees, "
          "fake FTC calls, free trials, fake debt collectors and credit repair. All from FTC pages.",
  sources=[RECOVERY, FTC_IMP, TRIALS, DEBT, CREDIT_FIX],
  claims=["FTC: never pay upfront for a refund or help with a refund",
          "FTC: the FTC will never call to demand money, threaten arrest or promise a prize",
          "FTC: if you have to pay shipping or fees for a 'free' trial, it's not really free",
          "FTC: fake collectors threaten arrest and refuse to give a mailing address or phone number",
          "FTC: it's illegal for credit repair companies to charge you before they help you"],
  original_element="A five-row table slide built from this week's alert cards: scam, the tell, and the one move.",
  segments=slides("5 scams this week", [
   ("Monday: someone offers to recover money you lost, for a fee first. The FTC says never pay upfront for a refund.",
    "Mon: 'We'll recover it, $350 fee'", "a vault with a price tag"),
   ("Tuesday: a caller says they're the FTC. The FTC never calls to demand money, threaten arrest or promise a prize.",
    "Tue: 'This is the FTC'", "a phone with a fake badge"),
   ("Wednesday: a free trial that needs $4.95 shipping. If you pay shipping or fees, it isn't free. Find the cancel terms first.",
    "Wed: 'Free, just pay shipping'", "a parcel with a hidden price tag"),
   ("Thursday: a collector threatens arrest and won't give an address. Ask for the creditor and amount in writing.",
    "Thu: 'A warrant will be issued'", "a phone with a red warning"),
   ("Friday: credit repair for $499 up front. Charging before they help is illegal, and fixing real errors is free.",
    "Fri: 'Erase late payments, $499'", "an eraser over a credit report"),
  ], "Every one ended the same way: hang up, check it yourself, report it at ReportFraud.ftc.gov.", "a calendar week with five red flags")),
]

LONG = dict(date="2027-03-06", time="10:00", look="screen recording", pillar=P_RIGHTS, topic="consumer rights",
 title="Your consumer rights in 2027: 5 that work when money goes wrong",
 title_variants=["5 consumer rights the FTC wants you to use", "National Consumer Protection Week: your rights, explained"],
 hook="5 rights protect your money when a company or a scammer gets it wrong, and most people never use one. Here's each one, with the deadline that matters.",
 thumb="5 rights. Know the deadlines.",
 hashtags=["consumerrights", "ncpw", "creditreport", "moneytips", "scamdecoded"],
 caption="For National Consumer Protection Week: five consumer rights, the deadlines that come with them, and how a "
         "made-up 'free trial' case uses two of them. Every right is from the FTC's own pages. Examples are fictional.",
 description_intro="Five consumer rights for National Consumer Protection Week 2027 (Feb 28 - Mar 6): cancelling door "
                   "sales, disputing card charges, free credit reports, fixing credit errors yourself, and what a debt "
                   "collector has to tell you. Sources are FTC pages. General education, not legal advice.",
 sources=[NCPW, COOLING, DISPUTE, REPORTS, CREDIT_FIX, DEBT, TRIALS],
 claims=["FTC: NCPW is 'a time to talk about frauds, scams, and consumer rights'; 2027 runs February 28 - March 6",
         "FTC Cooling-Off Rule: cancel until midnight of the third business day; Saturdays count, Sundays and federal holidays don't",
         "FTC Cooling-Off Rule: sales of $25+ at your home, $130+ at temporary locations; refund within 10 days of cancelling",
         "FTC Cooling-Off Rule: some sales are excluded (the page lists them, e.g. real estate and insurance)",
         "FTC: billing-error letter must reach the issuer within 60 days after the first bill with the error; issuer acknowledges within 30 days and resolves within 90",
         "FTC: you can withhold payment on the disputed amount while it's investigated",
         "FTC: free reports from each bureau once a week at AnnualCreditReport.com, the only authorized site",
         "FTC: it's illegal for credit repair companies to charge before they help; they can't remove true information",
         "FTC: collectors must give the creditor and amount within 5 days of first contact; you can dispute within 30 days"],
 segs=[
  ("Why this week", "It's National Consumer Protection Week, which the Federal Trade Commission calls a time to talk "
   "about frauds, scams and consumer rights. We spend most of the year on the scams. Today is the rights: five of them, "
   "each with a deadline, each from the FTC's own pages. None of them cost anything to use. All of them work better if "
   "you know about them before you need them, so this is one to save. And if you only remember one thing, remember the "
   "deadlines, because most of these rights quietly run out if you wait.", "NCPW: frauds, scams and your rights"),
  ("Right 1: cancel a door sale", "Right one. Someone sells you something at your front door, or at a pop-up event in "
   "a hotel room or a fairground. Under the FTC's Cooling-Off Rule you can cancel for a full refund until midnight of the "
   "third business day after the sale. Saturdays count as business days, Sundays and federal holidays don't. It covers "
   "sales of twenty-five dollars or more at your home, and a hundred and thirty or more at temporary locations. The "
   "seller has to tell you about the right and give you two cancellation forms. Mail one back, postmarked in time, "
   "and keep a copy. The refund is due within ten days. Some sales, like real estate and insurance, aren't "
   "covered, and the FTC's page lists the exceptions.", "Cancel by midnight, business day 3"),
  ("Right 2: dispute a card charge", "Right two. A wrong charge on your credit card: something you cancelled, never "
   "got, or never bought. Write to the card company at the billing disputes address, which isn't the address you send "
   "payments to. Your letter has to arrive within sixty days after the first bill with the error. The company must "
   "acknowledge it within thirty days and resolve it within ninety, and while it does, you can hold off paying the "
   "disputed amount. Call first if you like, but the letter is what protects you.", "60 days. In writing. Billing disputes address"),
  ("Right 3: free credit reports", "Right three. You can see your credit report from each of the three big bureaus, "
   "Equifax, Experian and TransUnion, free, once a week, at AnnualCreditReport dot com. That's the only site authorized "
   "to give them out. Lookalike sites with 'free report' in the name may try to sell you something or collect your "
   "details, so type the address yourself. Look for accounts you didn't open and addresses you've never lived at. "
   "Because it's weekly now, there's no reason to wait for a bad month: pick a day each season and check.",
   "AnnualCreditReport.com: weekly, free"),
  ("Right 4: fix errors yourself", "Right four. Found a mistake? Disputing it with the credit bureau, and with the "
   "business that reported it, is free. The FTC has sample letters. And here's the scam this right protects you from: "
   "it's illegal for a credit repair company to charge you before it helps you, and nobody can legally remove true, "
   "accurate information. A company that wants money up front, promises to erase real late payments, or tells you not "
   "to contact the bureaus is showing you all three red flags at once.", "Disputes are free. Up-front fees are illegal"),
  ("Right 5: make a collector prove it", "Right five. A debt collector has to tell you who they are, their mailing "
   "address, the creditor, and how much you owe, within five days of first contacting you. If you don't recognize the "
   "debt, dispute it within thirty days of getting that information, and they have to stop collecting until they "
   "verify it. A caller who threatens arrest and won't give you an address isn't using a right. That's the FTC's "
   "description of a fake collector.", "Creditor, amount, address: within 5 days"),
  ("Put them to work", "So here's the short version to keep. Three business days for a door sale. Sixty days for a card "
   "error. Weekly credit reports, free. Fix errors yourself, free. Five days for a collector to tell you what you owe. "
   "And when a company or a scammer ignores any of this, report it at ReportFraud dot FTC dot gov. Reports are how the "
   "FTC spots patterns and builds cases. Examples in this video were fictional. Save this, and send it to whoever "
   "handles the bills in your house.", "3 days · 60 days · weekly · free · 5 days"),
 ])


def item_carousel(p):
    return {"format": "carousel", "pillar": p["pillar"], "platforms": ["instagram"], "post_on": f"{p['date']} {p['time']}",
            "topic": p["topic"], "look": p["look"], "original_element": p["original_element"],
            "idea_angle": f"{SEASON}: {p['topic']}. {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": [seg(*r) for r in p["segments"]], "cta": CTA,
                       "caption": p["caption"] + "\n\n" + CHECKER + "\n\n" + CTA, "hashtags": p["hashtags"],
                       "description": p["description"], "thumbnail_text": p["thumb"], "sources": p["sources"],
                       "claims_to_verify": p["claims"]}}


def item_long(L):
    rows = [(h, n) for h, n, _ in L["segs"]]
    desc = (L["description_intro"] + "\n\nChapters\n" + "\n".join(chapters([{"heading": h, "narration": n} for h, n in rows]))
            + "\n\nSources\n" + "\n".join(L["sources"]) + "\n\nExamples are fictional.")
    return {"format": "long", "pillar": L["pillar"], "platforms": ["youtube"], "post_on": f"{L['date']} {L['time']}",
            "topic": L["topic"], "look": L["look"], "original_element": "", "idea_angle": f"{SEASON}: {L['description_intro']}",
            "script": {"title": L["title"], "hook": L["hook"],
                       "segments": [seg(h, n, o, "Face cam or screen recording; see original_element") for h, n, o in L["segs"]],
                       "cta": CTA, "caption": L["caption"] + "\n\n" + CTA, "hashtags": L["hashtags"], "description": desc,
                       "thumbnail_text": L["thumb"], "sources": L["sources"], "claims_to_verify": L["claims"],
                       "title_variants": L["title_variants"]}}


def plan(items):
    rows = ["# Scam Decoded: National Consumer Protection Week pack, Sun Feb 28 – Sat Mar 6 2027", "",
            "The FTC's National Consumer Protection Week (consumer.ftc.gov/ncpw) is \"a time to talk about frauds, scams, "
            "and consumer rights\", so this week covers both. Times America/New_York. Nothing has been posted; Dhruv "
            "posts each by hand. Check consumer.ftc.gov/ncpw in January 2027: the FTC adds its events and materials then.",
            "", "| # | Date | Time | Where | Format | Title |", "|---|---|---|---|---|---|"]
    for n, i in enumerate(items):
        d = dt.date.fromisoformat(i["post_on"][:10])
        where = {"carousel": "Instagram", "long": "YouTube"}[i["format"]]
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} | {i['post_on'][11:]} | {where} | {i['format'].capitalize()} | "
                    f"{i['script']['title']} |")
    rows += ["", "## Daily scam alerts (08:30 cards, emails and /alerts/ pages)", "",
             "| Date | Alert |", "|---|---|"]
    for f in sorted((ROOT.parent.parent / "sites" / "scam-decoded" / "content" / "alerts").glob("5[3-7]-*.md")):
        meta = dict(l.split(": ", 1) for l in f.read_text().split("---")[1].strip().splitlines() if ": " in l)
        d = dt.date.fromisoformat(meta["alert_date"])
        rows.append(f"| {d.strftime('%a %b')} {d.day} | {meta['scam']} (`{f.name}`) |")
    rows += ["", "Weeks 13–21 already put the 6-agencies carousel (#57, Tue Mar 2) and the Slam the Scam Day long video "
             "(#68, Sun Mar 7) in this window; they fit the week as they are.", "",
             "B2B: NCPW is the natural week to time credit union and library pilots (told the B2B thread)."]
    return "\n".join(rows) + "\n"


def main():
    items = [item_carousel(p) for p in CAROUSELS] + [item_long(LONG)]
    add_original_elements(items)
    items.sort(key=lambda i: i["post_on"])
    for i in items:
        sc = i["script"]
        assert len(sc["hashtags"]) <= 5 and sc["sources"] and sc["claims_to_verify"]
        for s in sc["segments"]:
            assert len(s["on_screen_text"].split()) <= 12, s["on_screen_text"]
        assert any(ch.isdigit() for ch in sc["hook"].split(".")[0][:60]), sc["hook"]
        assert "guarantee" not in json.dumps(i).lower()
        if i["format"] == "long":
            assert sum(len(s["narration"].split()) for s in sc["segments"]) >= 800, [s["heading"] for s in sc["segments"]]
    (ROOT / "ncpw-2027.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (ROOT / "POSTING_PLAN_NCPW_2027.md").write_text(plan(items))
    for n, i in enumerate(items):
        print(n, i["post_on"], i["format"], sum(len(s["narration"].split()) for s in i["script"]["segments"]), i["script"]["title"])


if __name__ == "__main__":
    main()
