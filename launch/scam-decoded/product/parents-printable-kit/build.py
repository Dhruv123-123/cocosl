"""Build the "Scam-Proof Your Parents" printable kit (Etsy + Gumroad, price [PRICE]).

    python3 build.py            # dist/*.pdf + dist/mockup-*.png (needs Chromium via contentfactory.business.pdf, and pdftoppm)
    python3 build.py --no-pdf   # dist/*.html only

Outputs (dist/):
  Scam-Proof-Your-Parents-Kit.pdf   9 pages, US Letter: cover, how to use, fridge card, 8 call scripts, code word guide,
                                    code word practice page, one-afternoon checklist, sources
  Fridge-Card.pdf                   the fridge card on its own (2 per page, cut in half)
  Call-Script-Cards.pdf             the 8 call scripts on their own, to keep by the phone
  mockup-01-hero.png, -02-inside.png, -03-details.png   2000x1500 listing photos made from the real pages

How it differs from the other parent products: Protect Your Parents ($29) is the 20-page setup guide for the adult child;
Scam Decoded for Seniors ($7) is the large-print booklet for the parent. This kit is the short printable set the two
of you fill in together in one afternoon. All wording here is new; no page is copied from either.
"""
from __future__ import annotations

import html
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"
SHARED_CSS = (HERE.parent / "shared.css").read_text()
TITLE = "Scam-Proof Your Parents"
esc = html.escape

SOURCES = [
    ("FBI IC3 public service announcement, Dec 2024: criminals use generative AI (create a secret word or phrase with your family)",
     "https://www.ic3.gov/PSA/2024/PSA241203"),
    ("FTC: scammers use AI to enhance their family emergency schemes (don't trust the voice; call back on a number you know)",
     "https://consumer.ftc.gov/consumer-alerts/2023/03/scammers-use-ai-enhance-their-family-emergency-schemes"),
    ("FTC: avoiding and reporting gift card scams", "https://consumer.ftc.gov/articles/avoiding-and-reporting-gift-card-scams"),
    ("FTC: what to know about credit freezes and fraud alerts",
     "https://consumer.ftc.gov/articles/what-know-about-credit-freezes-fraud-alerts"),
    ("US Department of Justice / OVC: National Elder Fraud Hotline, 833-FRAUD-11 (833-372-8311), Mon–Fri 10am–6pm ET",
     "https://ovc.ojp.gov/program/stop-elder-fraud/providing-help-restoring-hope"),
    ("Report fraud to the FTC", "https://reportfraud.ftc.gov/"),
]

# (who the caller says they are, what they say, what you say, what you do next)
SCRIPTS = [
    ("A grandchild or family member in trouble",
     "\"Grandma, it's me. I'm in trouble and I need money now. Please don't tell Mom.\"",
     "\"What's our code word?\" If they can't say it: \"I'm going to call you back on your own number.\"",
     "Hang up. Call them, or another family member, on the number in your phone. A cloned voice can sound exactly right."),
    ("Your bank's \"fraud department\"",
     "\"We've stopped a suspicious charge. To protect your account, move your money to a safe account.\"",
     "\"I'll call the number on the back of my card.\"",
     "Hang up and call that number yourself. A bank never asks you to move money to keep it safe."),
    ("Medicare or a benefits office",
     "\"Your card is being replaced. Confirm your Medicare number so your benefits don't stop.\"",
     "\"I don't give my number to anyone who calls me.\"",
     "Hang up. Call the number on your own card or letter if you're worried."),
    ("Social Security, the IRS or the police",
     "\"There's a warrant in your name. Pay today, or an officer will come to your home.\"",
     "\"I'll check this with the agency myself.\"",
     "Hang up. Government agencies don't demand payment by phone, gift card or crypto, and they don't threaten arrest."),
    ("Computer or phone \"support\"",
     "\"Your computer has a virus. Let us connect to it so we can fix it.\" (Often after a loud pop-up.)",
     "\"No one connects to my computer.\"",
     "Hang up, or close the pop-up. Turn the computer off if it won't close. Call family before you call anyone back."),
    ("The power, gas or water company",
     "\"Your service will be cut off in one hour unless you pay now.\"",
     "\"I'll call the number on my bill.\"",
     "Hang up and call the number printed on a real bill. Shut-off notices come in the mail first."),
    ("You've won a prize or sweepstakes",
     "\"Congratulations! You just need to pay the taxes and fees before we send your winnings.\"",
     "\"If I have to pay, it isn't a prize. No thank you.\"",
     "Hang up. A real prize never costs money to collect."),
    ("A delivery or shipping company",
     "\"Your package can't be delivered. Pay a small redelivery fee, or confirm your card.\"",
     "\"I'll check my orders myself.\"",
     "Hang up or delete the text. Check any order on the store's own app or website, typed in yourself."),
]

FRIDGE = [
    ("STOP", "if anyone rushes me, scares me, or tells me to keep it secret."),
    ("NEVER", "pay with gift cards, wire transfers, crypto, or cash in the mail."),
    ("NEVER", "read out a code someone texts me, or let a stranger into my computer."),
    ("ASK", "family callers for our code word. No word, no money."),
    ("HANG UP", "and call back on a number I find myself, not one they give me."),
]

CHECKLIST = {
    "Phone": ["Turn on the phone's unknown-caller or spam filter, and add family to Favorites",
              "Save family numbers with clear names (\"Sam, son\", not just \"Sam\")",
              "Ask the carrier for an account PIN, so no one can move the number without it",
              "Put the fridge card and the call scripts by the phone they answer most"],
    "Bank and cards": ["Turn on text or app alerts for every withdrawal and card charge",
                       "Ask the bank about adding a trusted contact person to the account",
                       "Write the number on the back of each card on the fridge card's call-back list"],
    "Credit": ["Freeze credit at Equifax, Experian and TransUnion (free; the FTC page explains how)",
               "Write where the freeze PINs or logins are kept (not the PINs themselves)"],
    "Email and accounts": ["Turn on two-step verification for email first, then the bank",
                           "Check that the recovery phone number and email on each account are theirs, or yours",
                           "Remove any remote-access app they don't recognize from the computer"],
    "Family plan": ["Pick the family code word together (page 6) and practice it once (page 7)",
                    "Agree on who they call first before paying anyone: name and number on the fridge card",
                    "Book a 10-minute check-in call each month, and put it in both calendars"],
}

KIT_CSS = """
  html,body{font-size:12.5pt;line-height:1.45}
  .page{padding:0.6in 0.7in 0.8in}
  h2{font-size:26pt} h3{font-size:14pt}
  .lede{font-size:13pt}
  .fridge2{border:3px solid var(--ink);border-radius:16px;padding:16px 22px;height:4.6in;margin-bottom:0.35in;overflow:hidden;position:relative}
  .fridge2 h2{font-size:22pt;margin-bottom:8px}
  .fridge2 .r{display:flex;gap:12px;margin:0 0 7px;font-size:13pt;line-height:1.3}
  .fridge2 .r b{flex:0 0 1.05in;color:var(--teal-d);font-weight:800}
  .fridge2 .ln{display:flex;gap:10px;font-size:11pt;margin-top:8px}
  .fridge2 .ln span{flex:1;border-bottom:1.4px solid var(--ink);height:20px}
  .fridge2 .hot{position:absolute;left:22px;right:22px;bottom:12px;font-size:10pt;color:var(--muted)}
  .cutline{border-top:2px dashed var(--muted);margin:-0.18in 0 0.17in;text-align:center;font-size:8pt;color:var(--muted)}
  .sc{border:1.6px solid var(--line);border-radius:12px;padding:9px 13px;margin:0 0 9px;break-inside:avoid;font-size:10.6pt;line-height:1.35}
  .sc h3{margin:0 0 4px;font-size:12pt}
  .sc p{margin:0 0 3px}.sc p b{display:inline-block;width:0.95in;color:var(--teal-d);font-size:8.6pt;text-transform:uppercase;letter-spacing:.06em}
  .sc p.say{font-weight:600}.sc p.say b{color:#a35f00}
  .sources li{font-size:10pt;margin-bottom:6px;word-break:break-all}
  .drill td.blank{height:30px}
"""


def page(body: str, n: int | None) -> str:
    folio = (f'<div class="folio"><span>{esc(TITLE)} · Scam Decoded · personal use only</span><span>{n}</span></div>'
             if n else "")
    return f'<section class="page">{body}{folio}</section>'


def doc(title: str, pages: list[str]) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{SHARED_CSS}{KIT_CSS}</style></head><body>{''.join(pages)}</body></html>")


def cover() -> str:
    return """<section class="page cover"><div class="badge"></div>
      <div class="kicker" style="color:var(--amber)">Scam Decoded · printable kit</div>
      <h1>Scam-Proof Your <span>Parents</span></h1>
      <p class="sub">Four printables you fill in together in one afternoon: a fridge card, 8 call scripts, a family code word, and a setup checklist.</p>
      <ul><li>A fridge card with your own call-back numbers</li><li>8 word-for-word scripts for the calls scammers make most</li>
      <li>How to pick, practice and use a family code word</li><li>A one-afternoon checklist for phone, bank, credit and email</li></ul>
      <div class="foot">General education, not legal or financial advice. No kit can promise nobody will be scammed; this one helps your family
      slow down and check. Numbers and sources checked November 2026. All example calls are fictional. Personal use only. © Scam Decoded.</div></section>"""


def how_to(n: int) -> str:
    return page("""<div class="kicker">Start here</div><h2>One afternoon, four printables</h2>
      <p class="lede">Do this with your parent, not for them. Bring a pen, their phone, and about two hours.</p>
      <div class="step"><b class="n">1</b><div><strong>The checklist (page 8), 60–90 minutes.</strong> Work through it on their phone and accounts,
        with them holding the device. Tick each line. Skip anything they don't want; it's their phone.</div></div>
      <div class="step"><b class="n">2</b><div><strong>The code word (pages 6–7), 15 minutes.</strong> Pick it together, then do one practice call
        from the next room. It's the part people remember.</div></div>
      <div class="step"><b class="n">3</b><div><strong>The fridge card (page 3), 10 minutes.</strong> Fill in the names and numbers, cut it out
        and stick it where they see it when the phone rings. The spare copy goes by a second phone, or to a sibling.</div></div>
      <div class="step"><b class="n">4</b><div><strong>The call scripts (pages 4–5), 20 minutes.</strong> Read two out loud together, you as the
        caller and them as themselves. Keep the pages by the phone.</div></div>
      <div class="box tip"><strong>Make it mutual.</strong> Set up your own code word answer, alerts and credit freeze in the same visit.
        It stops feeling like a test of them and starts feeling like a family plan.</div>
      <div class="box warn"><strong>If money has already gone:</strong> call the bank or card company now, using the number on the card,
        then report it at ReportFraud.ftc.gov. The National Elder Fraud Hotline (833-372-8311, Mon–Fri 10am–6pm ET) helps
        people 60 and over. Nobody from the hotline will call you first asking for money.</div>""", n)


def fridge_card() -> str:
    rows = "".join(f'<div class="r"><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in FRIDGE)
    return f"""<div class="fridge2"><div class="kicker">Keep on the fridge · by the phone</div>
      <h2>Before I pay, click or share anything</h2>{rows}
      <div class="ln">Before I pay anyone, I call:<span></span></div>
      <div class="ln">Their number:<span></span></div>
      <div class="ln">My bank (back of my card):<span></span></div>
      <div class="hot">Report a scam: ReportFraud.ftc.gov · Elder Fraud Hotline 833-372-8311 (Mon–Fri 10–6 ET).
        Our code word is never written here.</div></div>"""


def fridge_page(n: int | None) -> str:
    return page(fridge_card() + '<div class="cutline">cut here</div>' + fridge_card(), n)


def script_card(s) -> str:
    who, says, say, do = s
    return (f'<div class="sc"><h3>{esc(who)}</h3><p><b>They say</b>{esc(says)}</p>'
            f'<p class="say"><b>You say</b>{esc(say)}</p><p><b>Then</b>{esc(do)}</p></div>')


def script_pages(start: int | None) -> list[str]:
    intro = ('<div class="kicker">Call scripts · keep by the phone</div><h2>8 calls, and what to say</h2>'
             '<p class="lede" style="margin-bottom:8px">You never have to be polite to a caller who wants money. Saying the line and hanging up is enough.</p>')
    a = page(intro + "".join(script_card(s) for s in SCRIPTS[:4]), start)
    b = page('<div class="kicker">Call scripts · continued</div>' + "".join(script_card(s) for s in SCRIPTS[4:]) +
             '<div class="box dark"><div class="kicker">The one rule under all eight</div><p class="big" style="margin:0">'
             "Hang up, then call back on a number you found yourself: the back of the card, a real bill, or your own contacts.</p></div>",
             start + 1 if start else None)
    return [a, b]


def code_word(n: int) -> str:
    return page("""<div class="kicker">Family code word</div><h2>A word only your family knows</h2>
      <p class="lede">Scammers can now copy a voice from a few seconds of video. The FBI suggests a secret word or phrase to check who's
        really calling. Here's how to make one work.</p>
      <h3>Pick it together</h3><ul>
        <li><strong>Easy to remember, hard to guess.</strong> Not a pet's name, street, birthday or anything on social media.
          Two odd words work well: "purple toaster", "Tuesday pancakes".</li>
        <li><strong>Everyone who might call in a panic knows it:</strong> children, grandchildren, the sibling who travels.</li>
        <li><strong>Say it out loud. Never text, email or post it.</strong> Don't write it on this page or the fridge card.</li></ul>
      <h3>How to use it</h3><ul>
        <li>Anyone who calls upset and asking for money, a code or a secret gets one question: <em>"What's our code word?"</em></li>
        <li>A real family member will say it, or won't mind being called back.</li>
        <li>No word, wrong word, or "I don't have time for that"? Hang up and call them on the number in your phone.</li></ul>
      <h3>If someone forgets it</h3>
      <p>That's fine. Call them back on their own number, or call someone who's with them. Change the word if you think anyone outside the
        family has heard it.</p>
      <div class="box tip"><strong>What it doesn't replace:</strong> the call-back rule. Even with the right word, never pay by gift card,
        wire, crypto or cash in the mail. The FTC says those payment requests are a scam sign on their own.</div>""", n)


def drill(n: int) -> str:
    rows = "".join("<tr><td class='blank'></td><td></td><td></td></tr>" for _ in range(4))
    return page(f"""<div class="kicker">Code word · practice</div><h2>The 3-minute practice call</h2>
      <p class="lede">Do it once today, from the next room or a sibling's phone. It feels silly for ten seconds, and then it sticks.</p>
      <div class="step"><b class="n">1</b><div>Call and say: <em>"It's me. I've had an accident and I need $800 for a lawyer right now. Don't tell anyone."</em></div></div>
      <div class="step"><b class="n">2</b><div>Your parent asks: <em>"What's our code word?"</em> Don't say it. Push a bit: <em>"There's no time, please!"</em></div></div>
      <div class="step"><b class="n">3</b><div>They say: <em>"I'll call you back on your own number,"</em> and hang up. Then they really do call you back.</div></div>
      <div class="step"><b class="n">4</b><div>Swap. You take the call, and they play the caller. Laugh about it; the habit still forms.</div></div>
      <h3>Who knows the word</h3>
      <p style="color:var(--muted);font-size:11pt">Names only. Never write the word itself.</p>
      <table class="drill"><tr><th>Name</th><th>Told on (date)</th><th>Practiced?</th></tr>{rows}</table>
      <h3>Monthly check-in questions</h3><ul class="check">
        <li>Any calls or texts about money, prizes, or a family emergency this month?</li>
        <li>Anyone ask you to keep something secret, or to pay a new way?</li>
        <li>Do you still remember our code word? (Just nod; don't say it on the phone.)</li></ul>""", n)


def checklist(n: int) -> str:
    groups = "".join(f"<h3>{esc(k)}</h3><ul class='check'>" + "".join(f"<li>{esc(x)}</li>" for x in v) + "</ul>"
                     for k, v in CHECKLIST.items())
    return page(f"""<div class="kicker">Checklist · one afternoon</div><h2>The setup checklist</h2>
      <p class="lede" style="margin-bottom:4px">Menus differ by phone and bank, so follow the wording on the screen. If a step gets stuck, skip it and come back.</p>
      {groups}""", n)


def sources(n: int) -> str:
    items = "".join(f"<li>{esc(t)}<br>{esc(u)}</li>" for t, u in SOURCES)
    return page(f"""<div class="kicker">Sources and notes</div><h2>Where this comes from</h2>
      <p>Every rule in this kit comes from public advice by the FBI, the FTC and the US Department of Justice. Check the pages
        yourself; agencies update them.</p><ol class="sources">{items}</ol>
      <h3>Important</h3><ul><li>General education, not legal or financial advice.</li>
        <li>All example calls, names and amounts are fictional.</li>
        <li>No kit can promise nobody will ever be scammed. This one helps your family slow down and check.</li>
        <li>Personal use only: print as many copies as your own family needs. Please don't resell or share the files.</li></ul>
      <p style="color:var(--muted);font-size:10pt">How it's made: AI tools helped with drafting and layout, and a person checked every page
        and every source.</p>""", n)


def kit_pages() -> list[str]:
    return [cover(), how_to(2), fridge_page(3), *script_pages(4), code_word(6), drill(7), checklist(8), sources(9)]


def to_pdf(html_text: str, name: str) -> Path:
    src = DIST / f".{name}.html"
    src.write_text(html_text)
    out = DIST / f"{name}.pdf"
    from contentfactory.business.pdf import html_to_pdf
    if not html_to_pdf(src, out):
        raise SystemExit(f"PDF render failed for {name}")
    src.unlink()
    return out


def mockups(pdf: Path) -> None:
    """3 listing photos (2000x1500, Etsy's 4:3 grid) from the real pages."""
    from PIL import Image, ImageDraw, ImageFont
    tmp = DIST / ".pages"
    tmp.mkdir(exist_ok=True)
    subprocess.run(["pdftoppm", "-r", "110", "-png", str(pdf), str(tmp / "p")], check=True)
    pages = sorted(tmp.glob("p-*.png"))
    def font(size, bold=True):
        w = "Bold" if bold else "Regular"
        for f in (f"/usr/share/fonts/opentype/inter/Inter-{w}.otf",
                  f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"):
            if Path(f).exists():
                return ImageFont.truetype(f, size)
        return ImageFont.load_default()
    sets = [("01-hero", [0, 2, 3], "Scam-Proof Your Parents", "Fridge card · 8 call scripts · code word · checklist"),
            ("02-inside", [3, 4, 5], "8 calls, and what to say", "Word-for-word scripts to keep by the phone"),
            ("03-details", [5, 6, 7], "Code word + setup checklist", "Fill it in together in one afternoon")]
    for name, idx, head, sub in sets:
        im = Image.new("RGB", (2000, 1500), "#0d1b2a")
        d = ImageDraw.Draw(im)
        d.text((100, 80), head, fill="#f4f1ea", font=font(84))
        d.text((100, 190), sub, fill="#2ec4b6", font=font(44, bold=False))
        for k, i in enumerate(idx):
            pg = Image.open(pages[min(i, len(pages) - 1)]).convert("RGB")
            pg.thumbnail((560, 760))
            x, y = 100 + k * 610, 330 + (0 if k == 1 else 60)
            d.rectangle((x - 8, y - 8, x + pg.width + 7, y + pg.height + 7), fill="#2ec4b6")
            im.paste(pg, (x, y))
        d.text((100, 1420), "Printable PDF · US Letter · instant download", fill="#9fb0c0", font=font(34, bold=False))
        im.save(DIST / f"mockup-{name}.png")
    shutil.rmtree(tmp)


def main() -> None:
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    docs = {"Scam-Proof-Your-Parents-Kit": doc(TITLE, kit_pages()),
            "Fridge-Card": doc("Fridge card", [fridge_page(None)]),
            "Call-Script-Cards": doc("Call scripts", script_pages(None))}
    for name, text in docs.items():
        if "--no-pdf" in sys.argv:
            (DIST / f"{name}.html").write_text(text)
        else:
            to_pdf(text, name)
    if "--no-pdf" not in sys.argv:
        mockups(DIST / "Scam-Proof-Your-Parents-Kit.pdf")
    for p in sorted(DIST.iterdir()):
        print(f"{p.name:36s} {p.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
