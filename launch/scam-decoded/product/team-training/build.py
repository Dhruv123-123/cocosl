"""Build the Spot It, Stop It training pack.

    python3 build.py            # writes everything into dist/
    python3 build.py --no-pdf   # PPTX + HTML only (no Chromium / LibreOffice needed)

Outputs (dist/):
  Spot-It-Stop-It-Slides.pptx     editable deck, 16:9, speaker notes on every slide
  Spot-It-Stop-It-Slides.pdf      same deck as PDF (LibreOffice)
  Facilitator-Guide.pdf           prep, agenda, scenario answers, policy template, follow-up emails, attendance log
  Quiz.pdf / Answer-Key.pdf       12 questions, pass mark 10
  Certificate.pptx / .pdf         editable name/date certificate
  Poster-Verify-Before-You-Pay.pdf
"""
from __future__ import annotations

import html
import shutil
import subprocess
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

import content as C

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"
SHARED_CSS = (HERE.parent / "shared.css").read_text()
esc = html.escape

INK, CREAM, TEAL, TEAL_D, AMBER, MUTED, PAPER, WHITE = (
    RGBColor(0x0D, 0x1B, 0x2A), RGBColor(0xF4, 0xF1, 0xEA), RGBColor(0x2E, 0xC4, 0xB6), RGBColor(0x17, 0x8A, 0x80),
    RGBColor(0xFF, 0x9F, 0x1C), RGBColor(0x4A, 0x58, 0x68), RGBColor(0xFF, 0xFD, 0xF9), RGBColor(0xFF, 0xFF, 0xFF))
FONT = "Inter"


# ------------------------------------------------------------------ pptx helpers
def _bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _text(slide, x, y, w, h, text, size, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    lines = text if isinstance(text, list) else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size, r.font.bold, r.font.name = Pt(size), bold, FONT
        r.font.color.rgb = color
    return box


def _rect(slide, x, y, w, h, color, radius=True, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line:
        shp.line.color.rgb = line
        shp.line.width = Pt(1.5)
    else:
        shp.line.fill.background()
    if radius:
        shp.adjustments[0] = 0.06
    shp.shadow.inherit = False
    return shp


def _bullets(slide, x, y, w, h, items, size=22, color=INK, numbered=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(12)
        lead = p.add_run()
        lead.text = f"{i + 1}  " if numbered else "■  "
        lead.font.size, lead.font.bold, lead.font.name = Pt(size if numbered else size * 0.6), True, FONT
        lead.font.color.rgb = TEAL_D if not numbered else AMBER
        r = p.add_run()
        r.text = item
        r.font.size, r.font.name = Pt(size), FONT
        r.font.color.rgb = color
    return box


def _footer(slide, n, total, dark=False):
    c = RGBColor(0x9F, 0xB0, 0xC0) if dark else MUTED
    _text(slide, 0.6, 7.0, 8, 0.3, f"{C.TITLE} · Scam Decoded", 10, c)
    _text(slide, 11.2, 7.0, 1.5, 0.3, f"{n} / {total}", 10, c, align=PP_ALIGN.RIGHT)


def _kicker_title(slide, kicker, title, dark=False):
    _rect(slide, 0.6, 0.62, 0.45, 0.07, AMBER, radius=False)
    _text(slide, 1.15, 0.45, 10, 0.4, kicker.upper(), 13, TEAL if dark else TEAL_D, bold=True)
    _text(slide, 0.6, 0.9, 12.1, 1.3, title, 34, CREAM if dark else INK, bold=True)


def build_pptx(path: Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    total = len(C.SLIDES)
    for n, s in enumerate(C.SLIDES, 1):
        sl = prs.slides.add_slide(blank)
        kind = s["kind"]
        if kind == "title":
            _bg(sl, INK)
            _rect(sl, 0.9, 1.3, 0.9, 1.0, TEAL)
            _text(sl, 0.9, 2.7, 11.5, 1.6, s["title"], 60, CREAM, bold=True)
            _text(sl, 0.9, 4.3, 11.5, 0.8, s["body"], 24, AMBER)
            _footer(sl, n, total, dark=True)
        elif kind == "section":
            _bg(sl, TEAL)
            _text(sl, 0.9, 1.5, 11.5, 2.3, s["title"], 54, INK, bold=True, anchor=MSO_ANCHOR.BOTTOM)
            _text(sl, 0.9, 4.0, 11.5, 0.8, s["body"], 24, INK)
            _footer(sl, n, total)
        elif kind in ("bullets", "report"):
            _bg(sl, CREAM)
            _kicker_title(sl, s["kicker"], s["title"])
            items = s["body"]
            if kind == "report":
                _rect(sl, 0.6, 2.35, 12.1, 1.0, AMBER)
                _text(sl, 0.85, 2.4, 11.6, 0.9, items[0], 22, INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
                _bullets(sl, 0.7, 3.7, 11.8, 3.1, items[1:], 22)
            else:
                _bullets(sl, 0.7, 2.4, 11.8, 4.4, items, 24)
            _footer(sl, n, total)
        elif kind == "rules":
            _bg(sl, INK)
            _kicker_title(sl, s["kicker"], s["title"], dark=True)
            _bullets(sl, 0.7, 2.4, 11.8, 4.4, s["body"], 24, CREAM, numbered=True)
            _footer(sl, n, total, dark=True)
        elif kind == "email":
            _bg(sl, CREAM)
            _kicker_title(sl, s["kicker"], s["title"])
            e = s["email"]
            _rect(sl, 0.6, 2.3, 6.9, 4.5, WHITE, line=RGBColor(0xD8, 0xD3, 0xC7))
            _text(sl, 0.85, 2.45, 6.4, 0.4, "From: " + e["sender"], 13, MUTED)
            _text(sl, 0.85, 2.85, 6.4, 0.7, e["subject"], 18, INK, bold=True)
            _text(sl, 0.85, 3.6, 6.4, 3.1, e["body"].split("\n"), 15, INK)
            _text(sl, 7.9, 2.3, 4.9, 0.4, "RED FLAGS", 13, AMBER, bold=True)
            _bullets(sl, 7.8, 2.75, 5.0, 4.1, s["body"], 17)
            _footer(sl, n, total)
        elif kind == "scenario":
            _bg(sl, INK)
            _kicker_title(sl, s["kicker"], s["title"], dark=True)
            _rect(sl, 0.6, 2.35, 12.1, 3.2, RGBColor(0x1B, 0x2D, 0x40))
            _text(sl, 0.95, 2.6, 11.4, 2.8, s["body"], 24, CREAM)
            _text(sl, 0.6, 5.85, 12, 0.8, "What do you do? Talk it through in pairs for 60 seconds.", 22, AMBER, bold=True)
            _footer(sl, n, total, dark=True)
        sl.notes_slide.notes_text_frame.text = s["notes"]
    prs.save(path)


def build_certificate_pptx(path: Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(11), Inches(8.5)
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(sl, PAPER)
    _rect(sl, 0.4, 0.4, 10.2, 7.7, PAPER, line=INK)
    _rect(sl, 0.6, 0.6, 9.8, 0.25, TEAL, radius=False)
    _text(sl, 0.9, 1.3, 9.2, 0.5, "CERTIFICATE OF COMPLETION", 18, TEAL_D, bold=True, align=PP_ALIGN.CENTER)
    _text(sl, 0.9, 1.9, 9.2, 1.0, C.TITLE + ": Scam Awareness Training", 34, INK, bold=True, align=PP_ALIGN.CENTER)
    _text(sl, 0.9, 3.1, 9.2, 0.5, "This certifies that", 18, MUTED, align=PP_ALIGN.CENTER)
    _text(sl, 0.9, 3.7, 9.2, 0.8, "[Participant name]", 36, INK, bold=True, align=PP_ALIGN.CENTER)
    _text(sl, 0.9, 4.6, 9.2, 0.9, ["completed a 45-minute scam awareness session covering phishing, business email",
                                   "compromise, payment fraud, phone and AI voice scams, verification and reporting."],
          15, MUTED, align=PP_ALIGN.CENTER)
    for x, label in ((1.3, "[Organization]"), (4.3, "[Date]"), (7.3, "[Facilitator]")):
        _rect(sl, x, 6.55, 2.4, 0.03, INK, radius=False)
        _text(sl, x, 6.65, 2.4, 0.4, label, 13, MUTED, align=PP_ALIGN.CENTER)
        _text(sl, x, 6.0, 2.4, 0.5, "", 16, INK, align=PP_ALIGN.CENTER)
    prs.save(path)


# ------------------------------------------------------------------ html docs
def page(body: str, n: int | None, label: str = "Facilitator Guide") -> str:
    folio = f'<div class="folio"><span>{esc(C.PRODUCT)} · {label}</span><span>{n}</span></div>' if n else ""
    return f'<section class="page">{body}{folio}</section>'


def doc(title: str, pages: list[str], extra_css: str = "") -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{SHARED_CSS}{extra_css}</style></head><body>{''.join(pages)}</body></html>")


def facilitator_guide() -> str:
    agenda_rows = "".join(
        f"<tr><td>{i}</td><td>{esc(s['title'])}</td><td>{s['minutes'] or '–'}</td></tr>"
        for i, s in enumerate(C.SLIDES, 1))
    scen = "".join(
        f"<h3>{esc(s['kicker'])}: {esc(s['title'])}</h3><p><em>{esc(s['body'])}</em></p><p><strong>Model answer.</strong> {esc(s['notes'].removeprefix('Answer: '))}</p>"
        for s in C.SLIDES if s["kind"] == "scenario")
    cover = f"""<section class="page cover"><div class="badge"></div>
      <div class="kicker" style="color:var(--amber)">Scam Decoded · team training pack</div>
      <h1>Spot It, <span>Stop It</span></h1>
      <p class="sub">Facilitator guide for a 45-minute scam awareness session for small businesses and teams. No security background needed.</p>
      <ul><li>Editable slide deck with speaker notes (PPTX + PDF)</li><li>This guide: prep, agenda, scenario answers, templates</li>
      <li>12-question quiz and answer key</li><li>Editable certificate and a "Verify before you pay" poster</li></ul>
      <div class="foot">Licensed for internal use by one organization (any number of employees). Please don't resell or publish the materials.
      General education, not legal, security-compliance or financial advice. All example emails, names and domains are fictional.</div></section>"""
    p2 = page(f"""<div class="kicker">Before the session</div><h2>Prep checklist (30 minutes)</h2>
      <p class="lede">Most of the value comes from tailoring three slides to your company.</p>
      <ul class="check">
        <li><strong>Slide 18 · Reporting:</strong> replace the placeholder with how people report here (an email address, a Slack channel, a phone extension).</li>
        <li><strong>Slide 9 · Invoice fraud:</strong> say who gives the second approval for new payees and bank changes. No rule yet? Use the policy template on page 5.</li>
        <li><strong>Slide 2 · Why this matters:</strong> check the latest FBI IC3 annual report figure for business email compromise and say it out loud.</li>
        <li><strong>Ask a manager</strong> to attend and say, during slide 16, "Calling me to check a request is exactly what I want."</li>
        <li><strong>Print</strong> the quiz (one per person), certificates, and the poster for the break room or near whoever pays invoices.</li>
        <li><strong>Optional:</strong> collect one real (anonymised) scam message your company received. Real examples land best.</li>
      </ul>
      <h3>Who should attend</h3><p>Everyone with an email address, and especially anyone who pays invoices, runs payroll, manages suppliers, or has admin access. New hires should take it in their first month. Repeat it once a year.</p>
      <h3>Room and setup</h3><p>Any screen works. In person is best for the scenario discussions; on a video call, use breakout rooms of 2–3 for the scenarios. Open the PPTX in presenter view so you can see the speaker notes.</p>
      <div class="box tip"><strong>Tone matters most.</strong> Nobody should leave feeling foolish. Celebrate anyone who shares a near miss. The aim is a team that reports fast, without fear.</div>""", 2)
    p3 = page(f"""<div class="kicker">Running order</div><h2>Agenda: 45 minutes</h2>
      <table><tr><th>#</th><th>Slide</th><th>Min</th></tr>{agenda_rows}</table>""", 3)
    p4 = page(f"""<div class="kicker">Scenarios</div><h2>Scenario answers</h2>
      <p class="lede">Read the scenario, give pairs 60 seconds, take two or three answers, then share the model answer.</p>{scen}
      <div class="box warn"><strong>If someone shares a real incident:</strong> thank them, keep details anonymous, and don't let the room judge. Follow up privately if it's not yet reported.</div>""", 4)
    p5 = page("""<div class="kicker">Template · adapt and adopt</div><h2>Payment and data verification policy</h2>
      <p class="lede">A one-page policy most small businesses can adopt as-is. Fill in the blanks and share it after the session.</p>
      <ol>
        <li><strong>Bank detail changes.</strong> Any change to a supplier's, customer's or employee's bank details is confirmed by phone using contact details we already hold, never details in the request. The person who verified it records the date, the number called and who they spoke to.</li>
        <li><strong>New payees and changes</strong> are approved by a second person: <span class="fill"></span></li>
        <li><strong>Payments over $<span class="fill" style="min-width:0.8in"></span></strong> need a second approval, however urgent the request.</li>
        <li><strong>Gift cards</strong> are never bought because of an email or text request. Gift card purchases need written approval from <span class="fill"></span></li>
        <li><strong>Employee data</strong> (W-2s, pay slips, Social Security numbers) is only sent after confirming the request in person or by phone.</li>
        <li><strong>Codes and sign-in prompts.</strong> Nobody at this company, including IT, will ask you for a one-time code or to approve a sign-in you didn't start.</li>
        <li><strong>Reporting.</strong> Report suspicious messages and mistakes to <span class="fill"></span> as soon as possible. Reporting early is always the right thing to do. Nobody is disciplined for reporting a mistake in good faith.</li>
      </ol>
      <p>Approved by <span class="fill"></span> &nbsp; Date <span class="fill" style="min-width:1.2in"></span></p>""", 5)
    p6 = page("""<div class="kicker">After the session</div><h2>Follow-up emails (copy and paste)</h2>
      <h3>Same day · "Thanks, and the 5 rules"</h3>
      <div class="box tip"><p>Thanks for joining today's scam awareness session. The five rules, for your desk:</p>
      <ol><li>Two tells (rush, secrecy, unusual request)? Stop.</li><li>Verify on a channel you already have.</li><li>Never share a code or approve a prompt you didn't start.</li><li>Bank changes and new payees: phone check + second approval.</li><li>Report fast. No blame.</li></ol>
      <p>Report anything suspicious to [reporting route].</p></div>
      <h3>Two weeks later · "One question"</h3>
      <div class="box tip"><p>Quick check-in from the scam awareness session: has anyone had a suspicious message since? If you reported one, thank you. If you weren't sure whether to report something, the answer is always yes: [reporting route].</p></div>
      <h3>Monthly · "Scam of the month"</h3>
      <div class="box tip"><p>This month's scam to watch for: [one-line description]. The tell: [the giveaway]. What to do: verify on a known channel and report to [reporting route].</p>
      <p style="font-size:9pt;color:var(--muted);margin:0">Tip: Scam Decoded posts one scam decoded every day; pick one that fits your business.</p></div>""", 6)
    log_rows = "".join("<tr><td class='blank'></td><td></td><td></td><td></td></tr>" for _ in range(14))
    p7 = page(f"""<div class="kicker">Records</div><h2>Attendance and quiz log</h2>
      <p class="lede">Keep a simple record of who completed training. Some insurers and clients ask for it.</p>
      <p>Session date <span class="fill" style="min-width:1.4in"></span> &nbsp; Facilitator <span class="fill"></span></p>
      <table><tr><th>Name</th><th style="width:16%">Quiz score</th><th style="width:16%">Certificate</th><th style="width:22%">Notes</th></tr>{log_rows}</table>
      <h3>Sources</h3><p style="font-size:9pt">FBI IC3 annual reports and PSAs on business email compromise, payroll diversion and AI-generated voice/video (ic3.gov); FTC business guidance on phishing and scams (ftc.gov/business-guidance); CISA phishing guidance (cisa.gov); IRS guidance on W-2 phishing (irs.gov). Check figures before each session. General education, not legal, compliance or financial advice.</p>""", 7)
    return doc("Spot It, Stop It: Facilitator Guide", [cover, p2, p3, p4, p5, p6, p7])


def quiz(with_answers: bool) -> str:
    letters = "ABCD"
    items = []
    for i, (q, opts, ans, why) in enumerate(C.QUIZ, 1):
        if with_answers:
            items.append(f"<li><strong>{esc(q)}</strong><br><span style='color:var(--teal-d);font-weight:700'>{letters[ans]}. {esc(opts[ans])}</span><br><span style='color:var(--muted)'>{esc(why)}</span></li>")
        else:
            o = "".join(f"<div>☐ {letters[k]}. {esc(t)}</div>" for k, t in enumerate(opts))
            items.append(f"<li style='margin-bottom:8px;break-inside:avoid'><strong>{esc(q)}</strong>{o}</li>")
    head = ("<div class='kicker'>Answer key</div><h2>Quiz answers and why</h2><p class='lede'>Pass mark: 10 out of 12. Read these out together after the quiz.</p>"
            if with_answers else
            "<div class='kicker'>Spot It, Stop It</div><h2>Scam awareness quiz</h2><p>Name <span class='fill'></span> &nbsp; Date <span class='fill' style='min-width:1.3in'></span> &nbsp; Score ____ / 12</p>")
    css = ".qz{font-size:9.6pt;padding-left:18px} .qz div{margin-left:6px}"
    half = 6
    pages = [page(head + f"<ol class='qz'>{''.join(items[:half])}</ol>", 1, "Answer key" if with_answers else "Quiz"),
             page(f"<ol class='qz' start='{half + 1}'>{''.join(items[half:])}</ol>", 2, "Answer key" if with_answers else "Quiz")]
    return doc("Quiz answer key" if with_answers else "Quiz", pages, css)


def certificate_html() -> str:
    css = ("@page{size:11in 8.5in;margin:0} .cert{width:11in;height:8.5in;background:var(--paper);position:relative;padding:0.6in;margin:0 auto;box-sizing:border-box}"
           ".cert .frame{border:3px solid var(--ink);height:100%;padding:0.5in;text-align:center;position:relative}"
           ".cert .bar{position:absolute;left:0;right:0;top:0;height:16px;background:var(--teal)} .cert h1{font-size:34pt;margin:16px 0 26px}"
           ".sig{display:flex;justify-content:space-around;position:absolute;left:0.5in;right:0.5in;bottom:0.6in}.sig div{width:2.4in;border-top:1.5px solid var(--ink);padding-top:6px;color:var(--muted);font-size:10pt}")
    body = f"""<div class="cert"><div class="frame"><div class="bar"></div>
      <div class="kicker" style="margin-top:0.5in;font-size:12pt">Certificate of completion</div>
      <h1>{esc(C.TITLE)}: Scam Awareness Training</h1>
      <p style="color:var(--muted);font-size:14pt">This certifies that</p>
      <div style="border-bottom:1.5px solid var(--ink);width:6in;margin:28px auto 18px;height:40px"></div>
      <p style="color:var(--muted);font-size:12pt;max-width:7.5in;margin:0 auto">completed a 45-minute scam awareness session covering phishing, business email compromise, payment fraud, phone and AI voice scams, verification and reporting.</p>
      <div class="sig"><div>Organization</div><div>Date</div><div>Facilitator</div></div></div></div>"""
    return doc("Certificate", [body], css)


def poster_html() -> str:
    body = page("""<div class="fridge" style="margin-top:0.2in;padding:34px 36px">
      <div class="kicker" style="font-size:12pt">Spot It, Stop It</div>
      <h2 style="font-size:40pt;margin-bottom:18px">Verify before you pay.</h2>
      <ol style="font-size:19pt;line-height:1.35">
        <li><strong>Rush, secrecy, unusual request?</strong> Two of three: stop.</li>
        <li><strong>Verify</strong> on a number or channel you already have. Never the one in the message.</li>
        <li><strong>Never share a code</strong> or approve a sign-in you didn't start.</li>
        <li><strong>Bank changes and new payees:</strong> phone check + second approval.</li>
        <li><strong>Report fast. No blame.</strong></li>
      </ol>
      <p style="font-size:16pt;margin-top:22px"><strong>Report to:</strong> <span class="fill" style="min-width:4.2in"></span></p></div>""", None)
    return doc("Poster", [body])


def to_pdf(html_text: str, name: str) -> Path:
    src = DIST / f".{name}.html"
    src.write_text(html_text)
    out = DIST / f"{name}.pdf"
    from contentfactory.business.pdf import html_to_pdf
    if not html_to_pdf(src, out):
        raise SystemExit(f"PDF render failed for {name}")
    src.unlink()
    return out


def pptx_to_pdf(pptx: Path) -> Path:
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(DIST), str(pptx)],
                   check=True, capture_output=True, timeout=180)
    return pptx.with_suffix(".pdf")


def main() -> None:
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    slides = DIST / "Spot-It-Stop-It-Slides.pptx"
    build_pptx(slides)
    cert = DIST / "Certificate.pptx"
    build_certificate_pptx(cert)
    if "--no-pdf" in sys.argv:
        for name, text in (("Facilitator-Guide", facilitator_guide()), ("Quiz", quiz(False)),
                           ("Answer-Key", quiz(True)), ("Certificate", certificate_html()),
                           ("Poster-Verify-Before-You-Pay", poster_html())):
            (DIST / f"{name}.html").write_text(text)
    else:
        pptx_to_pdf(slides)
        to_pdf(facilitator_guide(), "Facilitator-Guide")
        to_pdf(quiz(False), "Quiz")
        to_pdf(quiz(True), "Answer-Key")
        to_pdf(certificate_html(), "Certificate")
        to_pdf(poster_html(), "Poster-Verify-Before-You-Pay")
    for p in sorted(DIST.iterdir()):
        print(f"{p.name:40s} {p.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
