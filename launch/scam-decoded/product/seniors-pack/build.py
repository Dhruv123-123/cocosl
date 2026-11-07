"""Build "Scam Decoded for Seniors" (large print).

    python3 build.py            # dist/*.pdf (needs Chromium via contentfactory.business.pdf)
    python3 build.py --no-pdf   # dist/*.html only

Outputs (dist/):
  Scam-Decoded-for-Seniors.pdf   12-page large-print booklet (includes the fridge checklist and wallet cards)
  Fridge-Checklist.pdf           1 page, print and stick on the fridge
  Wallet-Cards.pdf               4 cut-out cards per page, front + back (print double-sided, flip on long edge)
  Group-Print-License.pdf        1-page license certificate for the $49 group listing (fill in the organization)
"""
from __future__ import annotations

import html
import shutil
import sys
from pathlib import Path

import seniors_content as C

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"
SHARED_CSS = (HERE.parent / "shared.css").read_text()
esc = html.escape

LARGE = """
  html,body{font-size:16pt;line-height:1.42}
  .page{padding:0.65in 0.75in 0.85in}
  h2{font-size:32pt;margin-bottom:12px} h3{font-size:19pt;margin:18px 0 6px}
  .kicker{font-size:12pt} .lede{font-size:17pt;color:var(--ink)}
  li{margin-bottom:10px} .folio{font-size:11pt}
  .rule{display:flex;gap:16px;margin:0 0 16px}.rule b.n{flex:0 0 46px;height:46px;border-radius:50%;background:var(--amber);
    display:flex;align-items:center;justify-content:center;font-size:20pt;font-weight:800}
  .call{border:2.5px solid var(--ink);border-radius:14px;padding:10px 16px;margin:0 0 12px;break-inside:avoid}
  .call h3{margin:0 0 4px;font-size:17pt}.call .say{font-style:italic;margin:0 0 4px}.call .do{font-weight:700;margin:0}
  table{font-size:15pt} td,th{padding:9px 8px} td.blank{height:44px}
  .fridge{font-size:18pt;padding:24px 30px}.fridge h2{font-size:36pt}.fridge li{margin-bottom:12px}
  .cover h1{font-size:54pt}.cover .sub{font-size:19pt}.cover ul{font-size:16pt}.cover .foot{font-size:11pt}
  .cards{display:grid;grid-template-columns:3.5in 3.5in;grid-auto-rows:2in;gap:0.35in 0.3in;justify-content:center;margin-top:0.2in}
  .card{border:1.5px dashed var(--muted);border-radius:12px;padding:0.14in 0.18in;font-size:10.5pt;line-height:1.28;overflow:hidden}
  .card b.t{display:block;font-size:13pt;margin-bottom:4px}.card ol{padding-left:18px;margin:0}.card li{margin:0 0 2px}
  .card .ln{border-bottom:1px solid var(--ink);height:0.24in;margin-top:2px}
"""


def page(body: str, n: int | None) -> str:
    folio = f'<div class="folio"><span>{esc(C.TITLE)} · large print</span><span>{n}</span></div>' if n else ""
    return f'<section class="page">{body}{folio}</section>'


def doc(title: str, pages: list[str]) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{SHARED_CSS}{LARGE}</style></head><body>{''.join(pages)}</body></html>")


def fridge_page(n: int | None) -> str:
    items = "".join(f"<li>{esc(x)}</li>" for x in C.FRIDGE)
    rows = "".join("<tr><td class='blank'></td><td></td></tr>" for _ in range(3))
    return page(f"""<div class="fridge"><div class="kicker">Keep by the phone</div>
      <h2>Before I pay, click or share anything</h2><ol>{items}</ol>
      <table><tr><th>I call first</th><th style="width:45%">Phone number</th></tr>{rows}</table>
      <p style="font-size:14pt;margin:0">Report a scam: <strong>1-877-382-4357</strong> · Elder Fraud Hotline: <strong>1-833-372-8311</strong></p></div>""", n)


def wallet_pages() -> list[str]:
    front = ("<div class='card'><b class='t'>STOP. Is this a scam?</b><ol>"
             "<li>Hurry? Secret? Strange payment? <b>Stop.</b></li>"
             "<li>Never gift cards, wire, crypto or cash.</li>"
             "<li>Never share a texted code.</li>"
             "<li>Hang up. Call back on a number I look up.</li></ol></div>")
    back = ("<div class='card'><b class='t'>Before I pay, I call:</b>"
            "<div>Name</div><div class='ln'></div><div style='margin-top:4px'>Phone</div><div class='ln'></div>"
            "<div style='margin-top:6px'>Report a scam: <b>1-877-382-4357</b></div>"
            "<div>Elder Fraud Hotline: <b>1-833-372-8311</b></div></div>")
    note = "<p style='font-size:12pt;color:var(--muted);margin:0'>Cut along the dashed lines. Print double-sided (flip on long edge), or glue front to back.</p>"
    return [page(f"<div class='kicker'>Wallet cards · fronts</div>{note}<div class='cards'>{front * 8}</div>", None),
            page(f"<div class='kicker'>Wallet cards · backs</div>{note}<div class='cards'>{back * 8}</div>", None)]


def booklet() -> list[str]:
    cover = f"""<section class="page cover"><div class="badge"></div>
      <div class="kicker" style="color:var(--amber)">Scam Decoded · large print</div>
      <h1>Scam Decoded <span>for Seniors</span></h1>
      <p class="sub">{esc(C.SUBTITLE)}</p>
      <ul><li>5 golden rules that stop most scams</li><li>The 5 calls to hang up on</li>
      <li>Fill-in “who I call first” page</li><li>Fridge checklist and cut-out wallet cards</li></ul>
      <div class="foot">General education, not legal or financial advice. Phone numbers checked {esc(C.VERSION)}. All example
      calls, texts and names are made up. © Scam Decoded. For personal and family use.</div></section>"""
    rules = "".join(f'<div class="rule"><b class="n">{i}</b><div><strong>{esc(a)}</strong><br>{esc(b)}</div></div>'
                    for i, (a, b) in enumerate(C.GOLDEN_RULES, 1))
    p2 = page(f"""<div class="kicker">Start here</div><h2>The 5 golden rules</h2>
      <p class="lede">Scammers are professionals. Smart, careful people get fooled every day. These five rules beat almost every trick.</p>{rules}""", 2)
    calls = "".join(f'<div class="call"><h3>{esc(t)}</h3><p class="say">{esc(s)}</p><p class="do">{esc(d)}</p></div>'
                    for t, s, d in C.CALLS)
    p3 = page(f"""<div class="kicker">Phone calls</div><h2>5 calls to hang up on</h2>{calls}""", 3)
    texts = "".join(f'<div class="call"><p class="say">{esc(s)}</p><p class="do">{esc(d)}</p></div>' for s, d in C.TEXTS)
    p4 = page(f"""<div class="kicker">Texts and emails</div><h2>Don't tap the link</h2>
      <p class="lede">Scam texts look like they come from the post office, your bank or the toll road. If you're not sure, go to the company yourself.</p>{texts}
      <p><strong>Free:</strong> forward scam texts to <strong>7726</strong>, then delete them.</p>""", 4)
    online = "".join(f"<li>{esc(x)}</li>" for x in C.ONLINE)
    p5 = page(f"""<div class="kicker">Online friends and romance</div><h2>When a new friend needs money</h2>
      <p class="lede">Romance scammers spend weeks being kind before they ask for anything. Watch for someone:</p><ul>{online}</ul>
      <div class="box warn"><strong>The rule:</strong> never send money, gift cards or crypto to someone you have only met online. No matter how real they feel.</div>
      <h3>Investment “opportunities”</h3>
      <p>If a new online friend shows you how much they've made on an app or with crypto, it's almost always a scam. The app's numbers are fake, and the money can't be taken out.</p>
      <h3>Talk to someone</h3><p>Tell a family member or friend about your new friend. A scammer will try to keep you from doing that. That alone is a warning sign.</p>""", 5)
    p6 = page("""<div class="kicker">Computers and phones</div><h2>The scary pop-up</h2>
      <div class="call"><p class="say">“WARNING! Your computer is infected. Call Microsoft Support now: 1-8XX-XXX-XXXX.”</p>
      <p class="do">Don't call. Close the browser. If it won't close, turn the computer off and on again.</p></div>
      <ul><li>Real warnings never give you a phone number to call.</li>
      <li>Never let anyone you don't know control your computer (“remote access”).</li>
      <li>Never log in to your bank while a stranger is on the phone or on your screen.</li>
      <li>Already let someone in? Turn the computer off, call your bank, and ask a trusted helper to check it.</li></ul>
      <h3>Passwords</h3><p>Use a different password for your email than for anything else, and turn on “two-step” sign-in. Ask a family member to help you set it up. It takes about 10 minutes.</p>""", 6)
    lines = "".join(f"<li>{esc(x)}</li>" for x in C.HANG_UP_LINES)
    p7 = page(f"""<div class="kicker">What to say</div><h2>Your hang-up lines</h2>
      <p class="lede">You never have to be polite to a stranger who calls you. Pick one line and say it out loud a few times now.</p><ol style="font-size:19pt">{lines}</ol>
      <div class="box tip"><strong>Pick a family safe word.</strong> Agree on a word with your family that a scammer could never guess. If someone calls “in trouble”, ask for the word.<br><br>Our word: <span class="fill"></span></div>""", 7)
    nums = "".join(f"<tr><td>{esc(a)}</td><td><strong>{esc(b)}</strong></td></tr>" for a, b in C.OFFICIAL_NUMBERS)
    p8 = page(f"""<div class="kicker">Numbers you can trust</div><h2>Official numbers</h2>
      <p class="lede">These are real numbers to call. Scammers sometimes copy official names, so dial these yourself.</p>
      <table><tr><th>Who</th><th style="width:46%">How to reach them</th></tr>{nums}</table>
      <p style="font-size:12pt;color:var(--muted)">Checked {esc(C.VERSION)}. If a number doesn't work, look it up on the official .gov website.</p>""", 8)
    rows = "".join("<tr><td class='blank'></td><td></td></tr>" for _ in range(6))
    p9 = page(f"""<div class="kicker">Fill this in</div><h2>My important numbers</h2>
      <p class="lede">Write these from your cards and bills, not from a call or text.</p>
      <table><tr><th>Who</th><th style="width:46%">Number</th></tr>
      <tr><td>My bank (back of my card)</td><td></td></tr><tr><td>My credit card company</td><td></td></tr>
      <tr><td>My doctor / pharmacy</td><td></td></tr><tr><td>My phone company</td><td></td></tr>
      <tr><td><strong>I call first if I'm unsure</strong></td><td></td></tr>{rows}</table>""", 9)
    steps = "".join(f'<div class="rule"><b class="n">{i}</b><div><strong>{esc(a)}</strong> {esc(b)}</div></div>'
                    for i, (a, b) in enumerate(C.IF_IT_HAPPENS, 1))
    p10 = page(f"""<div class="kicker">If it happens</div><h2>The first hour</h2>
      <p class="lede">Acting fast gives you the best chance of getting money back.</p>{steps}""", 10)
    return [cover, p2, p3, p4, p5, p6, p7, p8, p9, p10, fridge_page(11)] + wallet_pages()


def license_page() -> str:
    terms = "".join(f"<li>{esc(t)}</li>" for t in C.GROUP_LICENSE["terms"])
    return page(f"""<div class="kicker">Group print license · ${C.GROUP_LICENSE['price']}</div>
      <h2>{esc(C.TITLE)}: group print license</h2>
      <p class="lede">This certificate goes with your purchase. Keep it with your printed copies.</p>
      <table><tr><td>Licensed organization</td><td class="blank"></td></tr><tr><td>Order number</td><td class="blank"></td></tr>
      <tr><td>Date of purchase</td><td class="blank"></td></tr></table>
      <h3>You may</h3><ul>{terms}</ul>
      <h3>Please don't</h3><ul><li>Resell the files, or post them on a public website or shared drive</li>
      <li>Remove the Scam Decoded name, or present the pack as your own</li>
      <li>Give the files to another organization (they can buy their own license)</li></ul>
      <p style="font-size:12pt;color:var(--muted)">Questions, or need a license for several branches? Email [contact email]. General education, not legal or financial advice.</p>""", None)


def to_pdf(html_text: str, name: str) -> Path:
    src = DIST / f".{name}.html"
    src.write_text(html_text)
    out = DIST / f"{name}.pdf"
    from contentfactory.business.pdf import html_to_pdf
    if not html_to_pdf(src, out):
        raise SystemExit(f"PDF render failed for {name}")
    src.unlink()
    return out


def main() -> None:
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    docs = {"Scam-Decoded-for-Seniors": doc(C.TITLE, booklet()),
            "Fridge-Checklist": doc("Fridge checklist", [fridge_page(None)]),
            "Wallet-Cards": doc("Wallet cards", wallet_pages()),
            "Group-Print-License": doc("Group print license", [license_page()])}
    for name, text in docs.items():
        if "--no-pdf" in sys.argv:
            (DIST / f"{name}.html").write_text(text)
        else:
            to_pdf(text, name)
    for p in sorted(DIST.iterdir()):
        print(f"{p.name:34s} {p.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
