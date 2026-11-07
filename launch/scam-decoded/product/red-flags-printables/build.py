"""Build "Scam Red Flags: Posters and Wallet Cards", a printables-only product for Etsy and Gumroad.

    python3 build.py              # dist/*.pdf + dist/mockup-*.png (Chromium via contentfactory.business.pdf, pdftoppm, Pillow)
    python3 build.py --no-pdf     # dist/*.html only (what the test uses)
    python3 build.py --out DIR    # write somewhere other than dist/

Why it can go on Etsy: Etsy's 22 Oct 2026 rule bans AI-generated *functional guides* (instructions buyers rely on).
This is wall signage and pocket cards: short red-flag lines, no steps, no how-to pages, the same reading the catalog's
etsy_rules.py (PR #6) uses to keep the Scam Decoded Card Set on Etsy. Keep it that way: don't add pages of advice.

How it differs from the Scam Decoded Card Set (PR #6, $6): that set is fridge cards, a caller-ID script page and one
wallet card design, for one family. This is 6 posters sized for a break room, library or church hall wall (Letter,
A4, 11x17, 18x24) plus 10 different wallet cards, one per scam type. All wording here is new.

Outputs (dist/):
  Scam-Red-Flags-Posters-Letter.pdf, -A4.pdf, -11x17.pdf, -18x24.pdf   6 posters + a sources page, one per page
  Scam-Red-Flags-Wallet-Cards-Letter.pdf, -A4.pdf                      fronts sheet + backs sheet (flip on long edge)
  mockup-01-hero.png, -02-posters.png, -03-wallet-cards.png          2000x1500 listing photos from the real pages
"""
from __future__ import annotations

import html
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "Scam Red Flags: Posters and Wallet Cards"
CHECKED = "Checked November 2026"
esc = html.escape

FTC_AVOID = "https://consumer.ftc.gov/articles/how-avoid-scam"
FTC_GIFT = "https://consumer.ftc.gov/articles/avoiding-and-reporting-gift-card-scams"
FTC_PHONE = "https://consumer.ftc.gov/articles/phone-scams"
FTC_TEXT = "https://consumer.ftc.gov/articles/how-recognize-and-report-spam-text-messages"
FTC_PHISH = "https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams"
FTC_FAMILY = "https://consumer.ftc.gov/consumer-alerts/2023/03/scammers-use-ai-enhance-their-family-emergency-schemes"
FTC_JOBS = "https://consumer.ftc.gov/articles/job-scams"
FTC_CHECK = "https://consumer.ftc.gov/articles/how-spot-avoid-and-report-fake-check-scams"
FTC_TECH = "https://consumer.ftc.gov/articles/how-spot-avoid-and-report-tech-support-scams"
FTC_ROMANCE = "https://consumer.ftc.gov/articles/what-know-about-romance-scams"
FTC_PRIZE = "https://consumer.ftc.gov/articles/fake-prize-sweepstakes-and-lottery-scams"
FTC_CHARITY = "https://consumer.ftc.gov/articles/donating-wisely-and-avoiding-charity-scams"
FTC_IMPOSTER = "https://consumer.ftc.gov/articles/how-avoid-government-impersonator-scam"
FTC_BUYER = "https://consumer.ftc.gov/articles/how-avoid-scam-when-you-sell-online"
IC3_AI = "https://www.ic3.gov/PSA/2024/PSA241203"
REPORT = "Report scams: ReportFraud.ftc.gov · Online crime: ic3.gov"

# (kicker, headline, [(flag, detail)], bottom line, sources)
POSTERS = [
    ("Any call, text or email", "5 signs it's a scam",
     [("They rush you", "Act now. Today. Within the hour."),
      ("They want it kept secret", "Don't tell your bank, your boss or your family."),
      ("They choose an odd way to pay", "Gift cards, wire, crypto, a payment app, cash."),
      ("They ask for a code", "A one-time code is for you alone."),
      ("They reached out first", "A call, text or pop-up you didn't expect.")],
     "See two of these? Stop, and check on a number you look up yourself.", [FTC_AVOID]),
    ("On the phone", "Hang up if the caller...",
     [("Threatens arrest or a fine", "Real agencies don't call to demand payment."),
      ("Says stay on the line", "So you can't check with anyone."),
      ("Says move money to keep it safe", "No real bank asks you to do that."),
      ("Wants into your computer", "Real tech support doesn't cold-call you."),
      ("Asks for gift cards", "Gift cards are for gifts, not payments.")],
     "Call back on the number printed on your card, bill or statement.", [FTC_PHONE, FTC_IMPOSTER, FTC_TECH, FTC_GIFT]),
    ("Texts and emails", "Don't tap if you see...",
     [("A fee you don't recognize", "An unpaid toll, a held package, a tiny charge."),
      ("A link to fix a problem", "Log in, verify, update your payment."),
      ("A deadline", "Today, 24 hours, or your account closes."),
      ("An address that's a little off", "One letter wrong, or an odd ending."),
      ("A prize you never entered", "Real winners don't pay to collect.")],
     "Open the app, or type the website yourself.", [FTC_TEXT, FTC_PHISH, FTC_PRIZE]),
    ("Payment requests", "Nobody real asks you to pay with...",
     [("Gift cards", "Read me the numbers on the back."),
      ("A wire transfer", "Hard to stop once it's sent."),
      ("Crypto or a Bitcoin ATM", "Hard to get back once it's sent."),
      ("A payment app, to a stranger", "It works like handing over cash."),
      ("Cash to a courier", "Or cash mailed in a box.")],
     "Asked to pay one of these ways? That's the scam.", [FTC_AVOID, FTC_GIFT]),
    ("A family emergency call", "Before you send money, notice...",
     [("Panic, and a plea", "Please don't tell Mom and Dad."),
      ("A stranger takes over", "A lawyer, an officer, a bail agent."),
      ("Money right now", "Bail, a hospital bill, a fine."),
      ("Secrecy", "Keep this between us."),
      ("A voice that sounds right", "Voices can be copied from a short clip.")],
     "Hang up. Call them on the number you already have.", [FTC_FAMILY, IC3_AI]),
    ("Jobs and money offers", "Red flags in an offer",
     [("Hired with no interview", "Over text or a chat app."),
      ("You pay to start", "Training, equipment, a starter fee."),
      ("A check to deposit and send back", "It bounces later, and you owe it."),
      ("Tasks that need a deposit", "Rate products, unlock your earnings."),
      ("Pay that's too good", "Big money from home, no experience.")],
     "Real employers don't charge you to work.", [FTC_JOBS, FTC_CHECK]),
]

# (scam type, [3 red flags], the one move)
CARDS = [
    ("Toll and package texts", ["A small fee to pay now", "A link in a text", "A deadline or penalty"],
     "Check the toll or shipping app yourself."),
    ("\"Your bank\" calling", ["Move money to a safe account", "Read me the code we sent", "Don't hang up"],
     "Call the number on your card."),
    ("Government callers", ["A warrant, or a fine", "Pay today, by phone", "Gift cards or crypto"],
     "Hang up. Agencies don't call to collect."),
    ("Family emergency", ["Don't tell anyone", "Money right now", "A lawyer takes the phone"],
     "Call them back. Ask your safe word."),
    ("Computer pop-ups", ["A loud alarm and a number", "Let us connect to fix it", "Pay for the repair"],
     "Close it. Don't call the number."),
    ("Job offers", ["Hired by text", "Pay for training or gear", "Deposit this check for us"],
     "Real jobs don't charge you."),
    ("Selling online", ["They overpay you", "Read me your code", "Click to get paid"],
     "Get paid inside the app only."),
    ("A new online friend", ["Never on video", "An app to invest with", "A crisis that needs money"],
     "No money to someone you haven't met."),
    ("Prizes and sweepstakes", ["You won, but pay a fee", "Taxes before the prize", "Keep it quiet for now"],
     "If you pay, it isn't a prize."),
    ("Charity appeals", ["Pressure to give today", "Gift card or wire only", "A name like a real one"],
     "Give through a charity's own site."),
]
CARD_SOURCES = [FTC_TEXT, FTC_PHONE, FTC_IMPOSTER, FTC_FAMILY, FTC_TECH, FTC_JOBS, FTC_CHECK, FTC_BUYER, FTC_ROMANCE,
                FTC_PRIZE, FTC_CHARITY]
CARD_BACK = ("Two of three?", "Stop. Hang up. Check it on a number you look up yourself.")

SIZES = {"Letter": ("8.5in", "11in", 1.0), "A4": ("210mm", "297mm", 0.973), "11x17": ("11in", "17in", 1.294),
         "18x24": ("18in", "24in", 2.118)}
CARD_SIZES = {"Letter": ("8.5in", "11in"), "A4": ("210mm", "297mm")}

CSS = """
:root{--ink:#0d1b2a;--cream:#f4f1ea;--red:#d62828;--amber:#ff9f1c;--muted:#4a5868;--paper:#fffdf9;--line:#d8d3c7}
*{box-sizing:border-box} html,body{margin:0;padding:0;color:var(--ink);background:#cdd3d9;
font-family:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:var(--w);height:var(--h);margin:0 auto;background:var(--paper);overflow:hidden;position:relative;
page-break-after:always;break-after:page}
.page:last-child{page-break-after:auto;break-after:auto}
"""
POSTER_CSS = """
.poster{display:flex;flex-direction:column;padding:calc(.55in*var(--s)) calc(.6in*var(--s));font-size:calc(1pt*var(--s))}
.band{background:var(--ink);color:var(--cream);margin:calc(-.55in*var(--s)) calc(-.6in*var(--s)) 0;
padding:calc(.42in*var(--s)) calc(.6in*var(--s)) calc(.36in*var(--s))}
.tag{display:inline-block;background:var(--red);color:#fff;font-weight:800;letter-spacing:.16em;text-transform:uppercase;
font-size:13em;padding:.25em .6em;border-radius:.3em}
.kicker{margin-top:.5em;font-size:17em;color:var(--amber);font-weight:700}
h1{margin:.08em 0 0;font-size:44em;line-height:1.02;letter-spacing:-.02em;font-weight:900}
ol{list-style:none;margin:0;padding:0;flex:1;display:flex;flex-direction:column;justify-content:space-evenly}
li{display:flex;align-items:center;gap:.7em;border-bottom:.12em solid var(--line);padding:.5em 0}
li:last-child{border-bottom:0}
.n{flex:none;width:1.6em;height:1.6em;border-radius:50%;background:var(--red);color:#fff;font-weight:900;font-size:30em;
display:flex;align-items:center;justify-content:center}
.f{font-size:27em;font-weight:800;line-height:1.1}
.d{font-size:17em;color:var(--muted);margin-top:.15em;line-height:1.25}
.bottom{background:var(--amber);color:var(--ink);font-weight:800;font-size:21em;line-height:1.25;padding:.6em .8em;border-radius:.35em}
.foot{display:flex;justify-content:space-between;margin-top:1.1em;font-size:10.5em;color:var(--muted)}
.sources{padding:calc(.7in*var(--s));font-size:calc(1pt*var(--s))}
.sources h2{font-size:26em;margin:0 0 .5em} .sources p,.sources li{font-size:11em;line-height:1.45}
.sources ul{padding-left:1.2em}
"""
CARD_CSS = """
.sheet{padding:.5in .75in;display:grid;grid-template-columns:3.5in 3.5in;grid-auto-rows:2in;gap:0;justify-content:center;align-content:start}
.a4 .sheet{padding:.45in 0}
.card{width:3.5in;height:2in;border:1px dashed #9aa5b1;padding:.15in .18in;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden}
.ct{font-size:12pt;font-weight:900;color:var(--ink);display:flex;align-items:center;gap:5px}
.ct b{background:var(--red);color:#fff;font-size:6.8pt;letter-spacing:.12em;padding:1px 4px;border-radius:2px}
.card ul{margin:0;padding:0;list-style:none}
.card li{font-size:11pt;font-weight:700;line-height:1.3;padding-left:14px;position:relative}
.card li:before{content:"!";position:absolute;left:0;color:var(--red);font-weight:900}
.mv{font-size:9.4pt;background:var(--amber);padding:2px 5px;border-radius:2px;font-weight:700}
.back{background:var(--ink);color:var(--cream);justify-content:center;gap:4px}
.back .q{font-size:20pt;font-weight:900;color:var(--amber)} .back .a{font-size:11pt;font-weight:700;margin-top:3px}
.back .r{font-size:7.6pt;margin-top:8px;color:#c9d2db}
.note{grid-column:1/-1;font-size:7.5pt;color:var(--muted);padding-top:8px}
"""


def page_doc(title: str, w: str, h: str, body: str, css: str, extra: str = "") -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)}</title><style>"
            f"@page{{size:{w} {h};margin:0}}{CSS}{css}:root{{--w:{w};--h:{h};{extra}}}</style></head>"
            f"<body>{body}</body></html>")


def poster(p, size: str) -> str:
    kicker, head, flags, bottom, _ = p
    items = "".join(f"<li><div class='n'>{i}</div><div><div class='f'>{esc(f)}</div><div class='d'>{esc(d)}</div></div></li>"
                    for i, (f, d) in enumerate(flags, 1))
    return (f"<section class='page poster'><div class='band'><span class='tag'>Scam red flags</span>"
            f"<div class='kicker'>{esc(kicker)}</div><h1>{esc(head)}</h1></div><ol>{items}</ol>"
            f"<div class='bottom'>{esc(bottom)}</div><div class='foot'><span>{esc(REPORT)}</span>"
            f"<span>Scam Decoded · {CHECKED}</span></div></section>")


def sources_page() -> str:
    rows = "".join(f"<li><b>{esc(p[0])}:</b> {' · '.join(esc(u) for u in p[4])}</li>" for p in POSTERS)
    return ("<section class='page sources'><h2>Where these red flags come from</h2>"
            "<p>Every line on these posters is based on public guidance from the US Federal Trade Commission (FTC) and the "
            f"FBI's Internet Crime Complaint Center (IC3). {CHECKED}.</p><ul>{rows}</ul>"
            f"<p>{esc(REPORT)}.</p><p>Educational signage, not legal, financial or security advice. No sign can stop every "
            "scam. For personal use, and for display in your own workplace, library, place of worship or community space. "
            "Please don't resell or share the files.</p><p>Designed by Scam Decoded. AI tools helped draft the wording and "
            "lay out the pages; a person checked every line against the sources above.</p></section>")


def posters_doc(size: str) -> str:
    w, h, s = SIZES[size]
    body = "".join(poster(p, size) for p in POSTERS) + sources_page()
    return page_doc(f"{NAME} ({size})", w, h, body, POSTER_CSS, f"--s:{s}")


def card_front(c) -> str:
    kind, flags, move = c
    lis = "".join(f"<li>{esc(f)}</li>" for f in flags)
    return f"<div class='card'><div class='ct'><b>RED FLAGS</b>{esc(kind)}</div><ul>{lis}</ul><div class='mv'>{esc(move)}</div></div>"


def card_back() -> str:
    q, a = CARD_BACK
    return f"<div class='card back'><div class='q'>{esc(q)}</div><div class='a'>{esc(a)}</div><div class='r'>{esc(REPORT)}</div></div>"


def cards_doc(size: str) -> str:
    w, h = CARD_SIZES[size]
    fronts = "".join(card_front(c) for c in CARDS)
    backs = "".join(card_back() for _ in CARDS)
    note = ("<div class='note'>10 wallet cards, 3.5 x 2 in (business card size). Print this page, then the next one on the "
            "back (flip on the long edge), or print both and glue back to back. Cut on the dashed lines. "
            f"Sources: FTC and FBI IC3 consumer pages, {CHECKED}. Personal use only.</div>")
    body = (f"<section class='page'><div class='sheet'>{fronts}{note}</div></section>"
            f"<section class='page'><div class='sheet'>{backs}</div></section>")
    return page_doc(f"{NAME}: wallet cards ({size})", w, h, body, CARD_CSS).replace("<body>", f"<body class='{size.lower()}'>")


def documents() -> dict[str, str]:
    docs = {f"Scam-Red-Flags-Posters-{s}": posters_doc(s) for s in SIZES}
    docs |= {f"Scam-Red-Flags-Wallet-Cards-{s}": cards_doc(s) for s in CARD_SIZES}
    return docs


def mockups(dist: Path) -> None:
    """3 listing photos (2000x1500) made from the real Letter pages."""
    from PIL import Image, ImageDraw, ImageFont
    tmp = dist / ".pages"
    tmp.mkdir(exist_ok=True)
    subprocess.run(["pdftoppm", "-q", "-r", "90", "-png", str(dist / "Scam-Red-Flags-Posters-Letter.pdf"), str(tmp / "p")], check=True)
    subprocess.run(["pdftoppm", "-q", "-r", "150", "-png", str(dist / "Scam-Red-Flags-Wallet-Cards-Letter.pdf"), str(tmp / "c")],
                   check=True)
    posters = sorted(tmp.glob("p-*.png"))
    cards = sorted(tmp.glob("c-*.png"))

    def font(size, bold=True):
        for f in (f"/usr/share/fonts/opentype/inter/Inter-{'Bold' if bold else 'Regular'}.otf",
                  f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"):
            if Path(f).exists():
                return ImageFont.truetype(f, size)
        return ImageFont.load_default()

    def canvas(head, sub):
        im = Image.new("RGB", (2000, 1500), "#e9e4d8")
        d = ImageDraw.Draw(im)
        d.text((100, 70), head, fill="#0d1b2a", font=font(80))
        d.text((100, 175), sub, fill="#d62828", font=font(42, bold=False))
        d.text((100, 1420), "Digital download · PDF · Letter, A4, 11x17 and 18x24 posters · 10 wallet cards",
               fill="#4a5868", font=font(32, bold=False))
        return im, d

    def framed(im, path, box, xy):
        pg = Image.open(path).convert("RGB")
        pg.thumbnail(box)
        x, y = xy
        ImageDraw.Draw(im).rectangle((x - 14, y - 14, x + pg.width + 13, y + pg.height + 13), fill="#0d1b2a")
        im.paste(pg, (x, y))

    im, _ = canvas("Scam red flags posters", "6 wall signs for a break room, library or front desk")
    for k, i in enumerate([0, 1, 4]):
        framed(im, posters[i], (600, 1000), (60 + k * 640, 290 + (0 if k == 1 else 50)))
    im.save(dist / "mockup-01-hero.png")
    im, _ = canvas("All 6 posters", "Any call · Phone · Texts · Payments · Family emergency · Jobs")
    for k in range(6):
        framed(im, posters[k], (330, 470), (110 + (k % 3) * 400 + (k // 3) * 0, 280 + (k // 3) * 560))
    pg = Image.open(posters[6]).convert("RGB")
    pg.thumbnail((520, 1000))
    im.paste(pg, (1360, 300))
    im.save(dist / "mockup-02-posters.png")
    im, _ = canvas("10 red-flag wallet cards", "One scam type per card, with the one move to make")
    sheet = Image.open(cards[0]).convert("RGB")
    w, h = sheet.size
    fronts = sheet.crop((int(w * .08), int(h * .04), int(w * .92), int(h * .965)))
    fronts.thumbnail((1200, 1110))
    ImageDraw.Draw(im).rectangle((92, 262, 108 + fronts.width, 278 + fronts.height), fill="#0d1b2a")
    im.paste(fronts, (100, 270))
    back = Image.open(cards[1]).convert("RGB").crop((int(w * .085), int(h * .045), int(w * .5), int(h * .225)))
    back.thumbnail((700, 420))
    for k in range(2):
        im.paste(back, (1180 + k * 40, 380 + k * 330))
    im.save(dist / "mockup-03-wallet-cards.png")
    shutil.rmtree(tmp)


def main(argv: list[str] | None = None) -> Path:
    argv = sys.argv[1:] if argv is None else argv
    dist = Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE / "dist"
    shutil.rmtree(dist, ignore_errors=True)
    dist.mkdir(parents=True)
    for name, text in documents().items():
        src = dist / (f"{name}.html" if "--no-pdf" in argv else f".{name}.html")
        src.write_text(text)
        if "--no-pdf" not in argv:
            from contentfactory.business.pdf import html_to_pdf
            if not html_to_pdf(src, dist / f"{name}.pdf"):
                raise SystemExit(f"PDF render failed for {name}")
            src.unlink()
    if "--no-pdf" not in argv:
        mockups(dist)
    for p in sorted(dist.iterdir()):
        print(f"{p.name:44s} {p.stat().st_size // 1024:>6} KB")
    return dist


if __name__ == "__main__":
    main()
