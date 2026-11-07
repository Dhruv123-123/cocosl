"""Build the Scam Decoded speaking kit (drafts).

    python3 build.py            # dist/: PPTX + PDF deck, handout PDF, pricing sheet PDF
    python3 build.py --no-pdf   # PPTX + HTML only

Reuses the slide styles from ../team-training/build.py so both decks look the same.
"""
from __future__ import annotations

import html
import importlib.util
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import talk as T  # noqa: E402

DIST = HERE / "dist"
esc = html.escape


def _deck_builder():
    tt = HERE.parent / "team-training"
    sys.path.insert(0, str(tt))
    try:
        spec = importlib.util.spec_from_file_location("sd_slide_styles", tt / "build.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(tt))
        sys.modules.pop("content", None)
    mod.C = T  # same slide kinds, our content
    return mod


TB = _deck_builder()
LARGE = """html,body{font-size:15pt;line-height:1.4} h2{font-size:28pt} h3{font-size:17pt} .kicker{font-size:11pt}
  .lede{font-size:16pt;color:var(--ink)} li{margin-bottom:8px} table{font-size:14pt} td,th{padding:8px}
  .folio{font-size:10pt} .tier{border:2px solid var(--ink);border-radius:12px;padding:10px 16px;margin:0 0 12px}
  .tier h3{margin:0 0 4px} .tier .p{float:right;font-size:20pt;font-weight:800;color:var(--teal-d)}"""


def page(body: str, n: int | None, label: str) -> str:
    folio = f'<div class="folio"><span>Scam Decoded · {esc(label)}</span><span>{n}</span></div>' if n else ""
    return f'<section class="page">{body}{folio}</section>'


def doc(title: str, pages: list[str]) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{TB.SHARED_CSS}{LARGE}</style></head><body>{''.join(pages)}</body></html>")


def handout() -> str:
    rules = next(s for s in T.SLIDES if s["kind"] == "rules")
    lines = [s for s in T.SLIDES if s["kind"] == "rules"][-1]
    first = next(s for s in T.SLIDES if s["kind"] == "report")
    li = lambda xs: "".join(f"<li>{esc(x)}</li>" for x in xs)  # noqa: E731
    nums = "".join(f"<tr><td>{esc(a)}</td><td><strong>{esc(b)}</strong></td></tr>" for a, b in T.HANDOUT_NUMBERS)
    p1 = page(f"""<div class="kicker">{esc(T.TITLE)} · take-home sheet</div><h2>The 3 warning signs</h2>
      <ol style="font-size:18pt">{li(rules['body'])}</ol>
      <div class="box warn"><strong>Two of the three? Stop.</strong> Hang up and call back on a number you look up yourself: on your card, your bill or an official website.</div>
      <h3>Never</h3><ul><li>pay with gift cards, wire transfers, crypto or cash by courier</li><li>read out a code that was texted to you</li>
      <li>let a caller on to your computer</li><li>move money to a “safe account”</li></ul>
      <h3>Say it out loud</h3><ul>{li(lines['body'])}</ul>""", 1, "handout")
    rows = "".join("<tr><td class='blank'></td><td></td></tr>" for _ in range(3))
    p2 = page(f"""<div class="kicker">If it happens</div><h2>The first hour</h2><ol>{li(first['body'])}</ol>
      <h3>Official numbers (checked November 2026)</h3><table>{nums}</table>
      <h3>My numbers</h3><table><tr><th>My bank (back of my card)</th><th>Someone I trust</th></tr>{rows}</table>
      <p style="font-size:11pt;color:var(--muted)">General education, not legal or financial advice. Free weekly scam alerts: [newsletter link]. Examples are fictional.</p>""",
              2, "handout")
    return doc("Handout", [p1, p2])


TIERS = [
    ("Community talk", "$150", "45-minute talk with Q&A, slides, and the large-print handout as a PDF for you to print. In person (within [distance] of [town]) or on Zoom."),
    ("Talk + printed handouts", "$225", "Everything above, plus printed handouts for up to 40 people and a sign-up sheet for free weekly scam alerts."),
    ("Workshop", "$300", "75 minutes: the talk plus hands-on help, setting up silence-unknown-callers, blocking and spam-text reporting on people's own phones. Up to 25 people; we recommend 1 volunteer helper per 8."),
    ("Free talk with the pack", "$0", "No speaking fee if the venue offers the $7 Scam Decoded for Seniors pack at the end (one short mention, no pressure), or buys a $49 group print license so you can print the pack for everyone."),
]


def pricing_sheet() -> str:
    tiers = "".join(f'<div class="tier"><span class="p">{esc(p)}</span><h3>{esc(n)}</h3><p style="margin:0">{esc(d)}</p></div>'
                    for n, p, d in TIERS)
    p1 = page(f"""<div class="kicker">Scam Decoded · for libraries, senior centers and churches</div>
      <h2>Scam awareness talks</h2><p class="lede">A friendly, plain-English session on phone, text and online scams, for older adults and their families. Nobody is made to feel foolish.</p>
      {tiers}
      <h3>Every talk includes</h3><ul><li>The 3 warning signs, the scams going around right now, and practice saying the hang-up lines out loud</li>
      <li>Three real-life practice scenarios and time for questions</li><li>A 2-page large-print handout with official numbers</li></ul>
      <p style="font-size:12pt">Nonprofit or tight budget? Ask: we'd rather give the talk than not. Travel beyond [distance]: [mileage rate]. Book: [email] · [phone]</p>""", None, "pricing")
    return doc("Pricing sheet", [p1])


def to_pdf(text: str, name: str) -> None:
    src = DIST / f".{name}.html"
    src.write_text(text)
    from contentfactory.business.pdf import html_to_pdf
    if not html_to_pdf(src, DIST / f"{name}.pdf"):
        raise SystemExit(f"PDF render failed for {name}")
    src.unlink()


def main() -> None:
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    deck = DIST / "Dont-Get-Scammed-Talk.pptx"
    TB.build_pptx(deck)
    docs = {"Handout": handout(), "Pricing-Sheet": pricing_sheet()}
    if "--no-pdf" in sys.argv:
        for name, text in docs.items():
            (DIST / f"{name}.html").write_text(text)
    else:
        TB.DIST = DIST
        TB.pptx_to_pdf(deck)
        for name, text in docs.items():
            to_pdf(text, name)
    for p in sorted(DIST.iterdir()):
        print(f"{p.name:34s} {p.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
