"""Build the 1099 Money product ladder above the $15 Quarterly Tax Tracker.

    python launch/1099-money/products/build_kit.py            # build everything
    python launch/1099-money/products/build_kit.py --check    # build into a temp dir and sanity-check

Builds:
  rate-contract-kit/Rate-and-Invoice-Kit.xlsx  rate calculator, project pricer, invoice, invoice log
  rate-contract-kit/templates/*.docx            proposal, services agreement, change order, invoice
  bundle/Client-Email-Scripts.docx              bundle-only bonus: 14 client emails
The guides (HTML -> PDF) are built by build_guides.py.

The rate calculator grosses a take-home target up for 2026 federal tax with a lookup table (hidden
"Grossup" sheet) so the workbook stays formula-only and works in Excel, Google Sheets and Numbers.
Its tax math is the same as the tracker's and apps/freelance-tax/lib/tax.js.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "product"))
from build_tracker import (BODY, BOLD, BOX, BRACKETS, CORAL_T, DATE, H2, INPUT, MUTED, PCT, SS_BASE,  # noqa: E402
                           STD, TINT, USD, USD0, header, put, title)

STATUSES = list(BRACKETS)
GROSSUP_ROWS = 400  # profit $1,000 .. $400,000


def _note(ws, ref, text):
    ws[ref] = text
    ws[ref].font = MUTED
    ws[ref].alignment = Alignment(wrap_text=True, vertical="top")


def build_xlsx(out: Path) -> Path:
    wb = Workbook()

    # ------------------------------------------------------------ Start Here
    ws = wb.active
    ws.title = "Start Here"
    title(ws, "The Freelancer Rate & Invoice Kit", "1099 Money · part of the Rate & Contract Kit · 2026 tax figures")
    ws.column_dimensions["B"].width = 110
    lines = [
        ("How to use it", H2),
        ("1. Rate Calculator: type what you want to take home, your benefits and costs, and your real billable hours. "
         "It works out the profit you need after 2026 federal tax (and a flat state rate), the revenue, and your hourly floor.", BODY),
        ("2. Project Pricer: list the tasks in a project, estimate hours honestly and get a project price with a revision "
         "buffer and a deposit.", BODY),
        ("3. Invoice: fill in the yellow cells, then File > Download/Export as PDF. Copy the tab for each new invoice.", BODY),
        ("4. Invoice Log: one row per invoice. It flags anything overdue and shows how long clients take to pay.", BODY),
        ("", BODY),
        ("Yellow cells are inputs. Everything else calculates. The example numbers match our video "
         "'How to set your freelance rate': $55,000 take-home → about $84,000 profit → $75/hour.", BODY),
        ("", BODY),
        ("Limits", H2),
        ("Federal tax uses 2026 figures for a sole proprietor (Schedule C) with no other income: self-employment tax, "
         "standard deduction and the 20% QBI deduction. It ignores credits, itemizing and the QBI limits above about "
         "$200,000 (single). State tax is a flat rate you choose. Health insurance and retirement are treated as paid "
         "from after-tax money, which slightly overstates the tax (a safe direction for pricing).", BODY),
        ("Update the Tax Tables tab each January.", BODY),
        ("", BODY),
        ("Educational tool, not tax, legal or financial advice. © 1099 Money. For your own business use; please don't resell.", MUTED),
    ]
    for i, (t, f) in enumerate(lines, start=5):
        ws.cell(row=i, column=2, value=t).font = f
        ws.cell(row=i, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    # ------------------------------------------------------------ Tax Tables
    tt = wb.create_sheet("Tax Tables")
    title(tt, "Tax tables (2026 federal)", "Update each January from IRS and SSA announcements.")
    for col, w in zip("BCDE", (34, 16, 16, 16)):
        tt.column_dimensions[col].width = w
    header(tt, 5, ["Bracket starts at", "Single", "Married filing jointly", "Rate"])
    for i in range(7):
        r = 6 + i
        put(tt, f"B{r}", f"Bracket {i + 1}")
        put(tt, f"C{r}", BRACKETS["Single"][i][0], USD0, INPUT)
        put(tt, f"D{r}", BRACKETS["Married filing jointly"][i][0], USD0, INPUT)
        put(tt, f"E{r}", BRACKETS["Single"][i][1], "0%", INPUT)
    # Marginal-rate differences for the SUMPRODUCT bracket formula.
    put(tt, "F5", "Rate step", font=BOLD)
    put(tt, "F6", "=E6", "0%")
    for r in range(7, 13):
        put(tt, f"F{r}", f"=E{r}-E{r - 1}", "0%")
    rows = [("Standard deduction · Single", STD["Single"], USD0), ("Standard deduction · MFJ", STD["Married filing jointly"], USD0),
            ("Social Security wage base", SS_BASE, USD0), ("SE earnings factor", 0.9235, "0.0000"),
            ("Social Security rate (SE)", 0.124, PCT), ("Medicare rate (SE)", 0.029, PCT), ("QBI deduction rate", 0.20, "0%")]
    for i, (lbl, v, f) in enumerate(rows):
        put(tt, f"B{15 + i}", lbl)
        put(tt, f"C{15 + i}", v, f, INPUT)
    tt["B23"] = "Sources: IRS Rev. Proc. 2025-32 (2026 inflation adjustments), SSA 2026 contribution and benefit base."
    tt["B23"].font = MUTED

    # ------------------------------------------------------------ Rate Calculator
    rc = wb.create_sheet("Rate Calculator", 1)
    title(rc, "Rate calculator", "Work backwards from what you want to take home. Yellow = your numbers.")
    rc.column_dimensions["B"].width = 52
    rc.column_dimensions["C"].width = 18
    rc.column_dimensions["D"].width = 64
    header(rc, 5, ["Your numbers", "", "Notes"])
    inputs = [
        ("Take-home pay you want per year (after tax)", 55000, USD0, "What you want to live on."),
        ("Health insurance per year", 6000, USD0, "What an employer used to cover. 0 if you're on a partner's plan."),
        ("Retirement savings per year", 5000, USD0, "SEP IRA / Solo 401(k) / IRA."),
        ("Business costs per year", 6000, USD0, "Software, equipment, insurance, fees, coworking."),
        ("Filing status", "Single", None, "Single or Married filing jointly (assumes no other household income)."),
        ("State income tax (flat estimate)", 0, PCT, "0% matches the video example. Most states: 3–7%."),
        ("Working weeks per year", 48, "0", "52 minus holidays, vacation and sick days."),
        ("Billable hours per week", 25, "0", "Hours clients pay for. Not admin, sales or email."),
        ("Hours in a billable day (for a day rate)", 6, "0", ""),
    ]
    for i, (lbl, v, f, note) in enumerate(inputs):
        r = 6 + i
        put(rc, f"B{r}", lbl)
        put(rc, f"C{r}", v, f, INPUT)
        _note(rc, f"D{r}", note)
    dv = DataValidation(type="list", formula1='"Single,Married filing jointly"', allow_blank=False)
    rc.add_data_validation(dv)
    dv.add("C10")

    header(rc, 16, ["What you need", "", "How it's worked out"])
    gp, ga = f"Grossup!$B$2:$B${GROSSUP_ROWS + 1}", f"Grossup!$G$2:$G${GROSSUP_ROWS + 1}"
    outs = [
        ("After-tax money needed", "=C6+C7+C8", USD0, "Take-home + health + retirement."),
        ("Profit needed (rounded up to $1,000)",
         f'=IFERROR(INDEX({gp},MATCH(C17,{ga},1)+1),"Over $400K: see a pro")', USD0,
         "Smallest profit that leaves the after-tax amount once federal and state tax are paid."),
        ("Federal tax on that profit", "=IFERROR(INDEX(Grossup!$F$2:$F$401,MATCH(C18,Grossup!$B$2:$B$401,0)),\"\")", USD0,
         "Self-employment tax + income tax, 2026."),
        ("State tax (flat estimate)", "=IFERROR(C18*C11,\"\")", USD0, ""),
        ("Left after tax", "=IFERROR(C18-C19-C20,\"\")", USD0, "Should be at or just above the first line."),
        ("Revenue needed per year", "=IFERROR(C18+C9,\"\")", USD0, "Profit + business costs."),
        ("Billable hours per year", "=C12*C13", "#,##0", ""),
        ("Your hourly floor", "=IFERROR(C22/C23,\"\")", USD, "The least you can charge and still hit your target."),
        ("Day rate", "=IFERROR(C24*C14,\"\")", USD0, ""),
        ("Revenue needed per month", "=IFERROR(C22/12,\"\")", USD0, ""),
        ("Revenue needed per working week", "=IFERROR(C22/C12,\"\")", USD0, ""),
        ("Tax set-aside % of profit", "=IFERROR((C19+C20)/C18,\"\")", PCT, "Move this % to tax savings the day each payment lands."),
    ]
    for i, (lbl, fml, f, note) in enumerate(outs):
        r = 17 + i
        put(rc, f"B{r}", lbl, bold=r in (18, 24))
        put(rc, f"C{r}", fml, f, CORAL_T if r == 24 else TINT, bold=r in (18, 24))
        _note(rc, f"D{r}", note)
    _note(rc, "B30", "Your hourly floor is a minimum, not a goal. Compare it with what experienced people in your niche "
                     "charge. If the market pays less than your floor, sharpen your niche or your offer before you cut the rate.")
    rc.merge_cells("B30:D31")

    # ------------------------------------------------------------ Grossup (hidden)
    gs = wb.create_sheet("Grossup")
    for c, h in zip("BCDEFG", ["Profit", "SE tax", "AGI before SD", "Taxable income", "Federal tax", "After fed + state"]):
        gs[f"{c}1"] = h
    T = "'Tax Tables'!"
    sd = f'IF(\'Rate Calculator\'!$C$10="Single",{T}$C$15,{T}$C$16)'
    for i in range(GROSSUP_ROWS):
        r = 2 + i
        gs[f"B{r}"] = 1000 * (i + 1)
        gs[f"C{r}"] = (f"=MIN(B{r}*{T}$C$18,{T}$C$17)*{T}$C$19+B{r}*{T}$C$18*{T}$C$20")
        gs[f"D{r}"] = f"=B{r}-C{r}/2"
        gs[f"E{r}"] = f"=MAX(0,D{r}-{sd})-MIN({T}$C$21*D{r},{T}$C$21*MAX(0,D{r}-{sd}))"
        sp = "SUMPRODUCT(--(E{r}>{t}),(E{r}-{t}),{T}$F$6:$F$12)"
        gs[f"F{r}"] = (f"=C{r}+IF('Rate Calculator'!$C$10=\"Single\"," + sp.format(r=r, t=f"{T}$C$6:$C$12", T=T)
                       + "," + sp.format(r=r, t=f"{T}$D$6:$D$12", T=T) + ")")
        gs[f"G{r}"] = f"=B{r}-F{r}-B{r}*'Rate Calculator'!$C$11"
    gs.sheet_state = "hidden"

    # ------------------------------------------------------------ Project Pricer
    pp = wb.create_sheet("Project Pricer", 2)
    title(pp, "Project pricer", "Estimate honestly, then add a buffer. Price the result, not just the hours.")
    for col, w in zip("BCDE", (46, 12, 16, 50)):
        pp.column_dimensions[col].width = w
    put(pp, "B5", "Project")
    put(pp, "C5", "Brand identity for [client]", fill=INPUT)
    pp.merge_cells("C5:D5")
    put(pp, "B6", "Hourly rate to price at")
    put(pp, "C6", "=ROUNDUP('Rate Calculator'!C24/5,0)*5", USD0, INPUT)
    _note(pp, "E6", "Starts at your hourly floor, rounded up to $5. Type over it to use a higher rate.")
    header(pp, 8, ["Task", "Hours", "Cost", "Notes"])
    tasks = [("Discovery call + brief", 2), ("Research and moodboard", 4), ("Three initial concepts", 12),
             ("Two rounds of revisions", 6), ("Final files and brand sheet", 4), ("Project management + email", 3)]
    for i in range(12):
        r = 9 + i
        name, hrs = tasks[i] if i < len(tasks) else (None, None)
        put(pp, f"B{r}", name, fill=INPUT)
        put(pp, f"C{r}", hrs, "0.0", INPUT)
        put(pp, f"D{r}", f'=IF(C{r}="","",C{r}*$C$6)', USD0)
        put(pp, f"E{r}", None, fill=INPUT)
    rows = [("Total hours", "=SUM(C9:C20)", "0.0"), ("Cost at your rate", "=SUM(D9:D20)", USD0),
            ("Revision / risk buffer", 0.15, PCT), ("Rush surcharge (0 if not a rush)", 0, PCT),
            ("Project price (rounded up to $50)", "=ROUNDUP(C23*(1+C24+C25)/50,0)*50", USD0), ("Deposit %", 0.5, PCT),
            ("Deposit (due before you start)", "=C26*C27", USD0), ("Balance (due on delivery)", "=C26-C28", USD0)]
    for i, (lbl, v, f) in enumerate(rows):
        r = 22 + i
        put(pp, f"B{r}", lbl, bold=r == 26)
        put(pp, f"C{r}", v, f, INPUT if r in (24, 25, 27) else (CORAL_T if r == 26 else TINT), bold=r == 26)
    _note(pp, "B31", "Put the scope and what's not included in your proposal. Anything outside it becomes a paid change order.")

    # ------------------------------------------------------------ Invoice
    iv = wb.create_sheet("Invoice", 3)
    title(iv, "INVOICE", "[Your name or business name] · [email] · [phone] · [address]")
    for col, w in zip("BCDE", (50, 10, 14, 16)):
        iv.column_dimensions[col].width = w
    meta = [("Invoice #", "2027-001", None), ("Invoice date", "=TODAY()", DATE), ("Payment terms (days)", 14, "0"),
            ("Due date", "=C6+C7", DATE)]
    for i, (lbl, v, f) in enumerate(meta):
        put(iv, f"B{5 + i}", lbl)
        put(iv, f"C{5 + i}", v, f, INPUT if i < 3 else TINT)
        iv.merge_cells(f"C{5 + i}:D{5 + i}")
    put(iv, "B10", "Bill to")
    put(iv, "C10", "[Client name, company, address, email]", fill=INPUT)
    iv.merge_cells("C10:E10")
    put(iv, "B11", "Project / PO")
    put(iv, "C11", "[Project name and any PO number]", fill=INPUT)
    iv.merge_cells("C11:E11")
    header(iv, 13, ["Description", "Qty", "Rate", "Amount"])
    items = [("Brand identity: final files and brand sheet (per proposal dated [date])", 1, 2700),
             ("Deposit received [date]", 1, -1350)]
    for i in range(10):
        r = 14 + i
        d, q, rt = items[i] if i < len(items) else (None, None, None)
        put(iv, f"B{r}", d, fill=INPUT)
        put(iv, f"C{r}", q, "0.##", INPUT)
        put(iv, f"D{r}", rt, USD, INPUT)
        put(iv, f"E{r}", f'=IF(OR(C{r}="",D{r}=""),"",C{r}*D{r})', USD)
    put(iv, "D25", "Total due", bold=True)
    put(iv, "E25", "=SUM(E14:E23)", USD, CORAL_T, bold=True)
    pay = ["How to pay: [bank transfer details / pay-now link]. Please include the invoice number.",
           "Due by the date above. Late payments are subject to the late fee in our agreement, where allowed by law.",
           "Thank you for your business."]
    for i, t in enumerate(pay):
        iv[f"B{27 + i}"] = t
        iv[f"B{27 + i}"].font = BODY if i < 2 else BOLD
    iv.print_area = "A1:E30"

    # ------------------------------------------------------------ Invoice Log
    lg = wb.create_sheet("Invoice Log", 4)
    title(lg, "Invoice log", "One row per invoice. Status updates itself. Chase anything overdue the same day.")
    cols = ["Invoice #", "Client", "Amount", "Sent", "Terms (days)", "Due", "Paid on", "Days to pay", "Status"]
    widths = [12, 26, 14, 14, 12, 14, 14, 12, 20]
    for i, w in enumerate(widths):
        lg.column_dimensions[chr(66 + i)].width = w
    header(lg, 9, cols)
    ex = [("2027-001", "Example Studio", 1700, "2027-01-04", 14, "2027-01-15"),
          ("2027-002", "Example Co", 2400, "2027-01-11", 14, None)]
    from datetime import date as _d
    for i in range(200):
        r = 10 + i
        e = ex[i] if i < len(ex) else None
        put(lg, f"B{r}", e[0] if e else None, fill=INPUT)
        put(lg, f"C{r}", e[1] if e else None, fill=INPUT)
        put(lg, f"D{r}", e[2] if e else None, USD0, INPUT)
        put(lg, f"E{r}", _d.fromisoformat(e[3]) if e else None, DATE, INPUT)
        put(lg, f"F{r}", e[4] if e else None, "0", INPUT)
        put(lg, f"G{r}", f'=IF(OR(E{r}="",F{r}=""),"",E{r}+F{r})', DATE)
        put(lg, f"H{r}", _d.fromisoformat(e[5]) if e and e[5] else None, DATE, INPUT)
        put(lg, f"I{r}", f'=IF(OR(E{r}="",H{r}=""),"",H{r}-E{r})', "0")
        put(lg, f"J{r}", f'=IF(B{r}="","",IF(H{r}<>"","Paid",IF(TODAY()>G{r},"OVERDUE "&(TODAY()-G{r})&" days","Open")))')
    summ = [("Outstanding (not paid)", '=SUMIFS(D10:D209,H10:H209,"",B10:B209,"<>")', USD0),
            ("Overdue", '=SUMPRODUCT((B10:B209<>"")*(H10:H209="")*(G10:G209<>"")*(TODAY()>G10:G209)*D10:D209)', USD0),
            ("Average days to pay", '=IFERROR(AVERAGE(I10:I209),"")', "0")]
    for i, (lbl, f, fm) in enumerate(summ):
        put(lg, f"B{5 + i}", lbl)
        lg.merge_cells(f"B{5 + i}:C{5 + i}")
        put(lg, f"D{5 + i}", f, fm, CORAL_T if i == 1 else TINT, bold=True)

    wb.move_sheet("Tax Tables", offset=len(wb.sheetnames))
    wb.move_sheet("Grossup", offset=len(wb.sheetnames))
    for s in wb.worksheets:
        s.sheet_properties.tabColor = "FF7A45" if s.title in ("Rate Calculator", "Invoice") else "14213D"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


# ------------------------------------------------------------------ docx templates
def _doc(title_text, subtitle):
    from docx import Document
    from docx.shared import Pt, RGBColor
    d = Document()
    st = d.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(11)
    h = d.add_heading(title_text, 0)
    for r in h.runs:
        r.font.color.rgb = RGBColor(0x14, 0x21, 0x3D)
    p = d.add_paragraph(subtitle)
    p.runs[0].italic = True
    return d


def _para(d, text, bold_lead=None):
    p = d.add_paragraph()
    if bold_lead:
        p.add_run(bold_lead).bold = True
    p.add_run(text)
    return p


TEMPLATE_NOTE = ("Template from the 1099 Money Rate & Contract Kit. Replace everything in [brackets]. "
                 "This is a starting point, not legal advice: laws differ by state and country, so have a lawyer "
                 "review your agreement before relying on it, especially for large projects.")


def build_docs(folder: Path) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    out = []

    # Proposal
    d = _doc("Proposal: [Project name]", f"Prepared for [Client] by [Your name / business] · [date] · valid for 30 days")
    for head, body in [
        ("The goal", "[One or two sentences in the client's words: what they want to achieve and why now.]"),
        ("What I'll do", "[3–6 bullet points describing the work. Describe outcomes, not just tasks.]"),
        ("What you'll get", "[Exact deliverables: files, formats, quantities, number of concepts.]"),
        ("Not included", "[Anything that's easy to assume but isn't in the price: extra concepts, copywriting, printing, "
                         "ongoing support. Anything here can be added as a change order.]"),
        ("Revisions", "[Two] rounds of revisions are included. Further rounds are billed at [$rate]/hour or quoted in advance."),
        ("Timeline", "Kickoff: [date, after deposit]. First draft: [date]. Revisions: [dates]. Final delivery: [date]. "
                     "Dates assume feedback within [3] business days."),
        ("Investment", "[$Project price] total. [50]% deposit ([$amount]) to book the start date; the balance is due on "
                       "delivery, payable within [14] days of invoice. [Optional: Option B, a smaller scope at $X.]"),
        ("What I need from you", "[Brand assets, logins, a single point of contact, feedback by the dates above.]"),
        ("Why me", "[Two or three sentences: relevant results, a short testimonial or a link to similar work.]"),
        ("Next steps", "Reply to accept, and I'll send the agreement and the deposit invoice. Once both are done, "
                       "your start date is reserved."),
    ]:
        d.add_heading(head, 2)
        d.add_paragraph(body)
    d.add_paragraph(TEMPLATE_NOTE).runs[0].italic = True
    out.append(folder / "1-Proposal-Template.docx")
    d.save(out[-1])

    # Agreement
    d = _doc("Freelance Services Agreement", "Between [Your legal name or business] (\"Freelancer\") and [Client legal name] (\"Client\")")
    _para(d, "Effective date: [date]. Project: [project name], as described in the proposal dated [date] (the \"Proposal\"), "
             "which is part of this agreement.")
    clauses = [
        ("1. Services and scope", "Freelancer will provide the services and deliverables described in the Proposal. Work "
         "not described there is outside the scope and will be quoted separately and agreed in writing (a \"Change Order\") "
         "before it starts."),
        ("2. Timeline", "Freelancer will use reasonable efforts to meet the timeline in the Proposal. Dates depend on Client "
         "providing materials and feedback on time; delays on Client's side move the timeline by at least the same amount."),
        ("3. Fees and payment", "Client will pay the fees in the Proposal. A non-refundable deposit of [50]% is due before "
         "work begins and reserves Freelancer's time. Invoices are due within [14] days. Payments more than [7] days late "
         "may incur a late fee of [1.5]% per month on the unpaid amount, or the maximum allowed by law if lower. Freelancer "
         "may pause work while any invoice is overdue."),
        ("4. Expenses", "Pre-approved expenses (for example stock images, fonts, travel) are billed at cost [plus [10]%]."),
        ("5. Revisions", "The Proposal states the number of revision rounds included. Additional rounds are billed at "
         "[$rate] per hour or as quoted."),
        ("6. Client responsibilities", "Client will provide accurate materials, access and timely feedback, and confirms it "
         "has the right to use anything it provides to Freelancer."),
        ("7. Ownership", "When Client has paid all fees in full, Freelancer assigns to Client the rights to the final "
         "deliverables. Freelancer keeps ownership of drafts, unused concepts, and pre-existing tools, templates and "
         "know-how, and grants Client a license to use any of these that are built into the final deliverables. Until "
         "full payment, Client may not use the deliverables."),
        ("8. Portfolio", "Freelancer may show the final work in a portfolio and mention Client as a client, unless Client "
         "asks in writing not to, or the work is confidential."),
        ("9. Confidentiality", "Each party will keep the other's non-public business information confidential and use it "
         "only for this project."),
        ("10. Independent contractor", "Freelancer is an independent contractor, not an employee, and is responsible for "
         "their own taxes, insurance, tools and working hours. Client will provide a W-9 request if it needs one; "
         "Freelancer will provide a W-9."),
        ("11. Cancellation", "Either party may end this agreement with [7] days' written notice. Client will pay for all "
         "work done up to the end date, at the project rate or [$rate] per hour, and the deposit is not refunded. "
         "[Optional kill fee: if Client cancels after [stage], Client pays [25]% of the remaining fee.]"),
        ("12. Warranties and liability", "Freelancer will perform the services in a professional manner. Except as stated "
         "here, the work is provided without other warranties. Neither party is liable for indirect or consequential "
         "damages. Freelancer's total liability under this agreement is limited to the fees paid under it."),
        ("13. General", "This agreement and the Proposal are the whole agreement and can only be changed in writing. "
         "Governing law: [state/country]. If any part is unenforceable, the rest still applies. Electronic signatures "
         "count as originals."),
    ]
    for head, body in clauses:
        d.add_heading(head, 2)
        d.add_paragraph(body)
    d.add_heading("Signatures", 2)
    for who in ("Freelancer", "Client"):
        _para(d, " ______________________   Name: [ ]   Title: [ ]   Date: [ ]", f"{who}:")
    d.add_paragraph(TEMPLATE_NOTE).runs[0].italic = True
    out.append(folder / "2-Freelance-Services-Agreement.docx")
    d.save(out[-1])

    # Change order
    d = _doc("Change Order #[1]", "Project: [project name] · Agreement dated [date] · [date of this change order]")
    for head, body in [
        ("What's changing", "[Describe the new or changed work in plain words.]"),
        ("Why it's outside the original scope", "[Reference the Proposal: e.g. 'The Proposal includes 3 concepts; this adds a 4th.']"),
        ("Cost", "[$amount] [or [hours] hours at [$rate]/hour]. Invoiced [now / with the final invoice]."),
        ("Timeline impact", "[New delivery date, or 'no change'.]"),
        ("Approval", "Reply \"Approved\" to this email or sign below. Work on the change starts once it's approved."),
    ]:
        d.add_heading(head, 2)
        d.add_paragraph(body)
    _para(d, " ______________________   Date: [ ]", "Client approval:")
    d.add_paragraph(TEMPLATE_NOTE).runs[0].italic = True
    out.append(folder / "3-Change-Order.docx")
    d.save(out[-1])

    # Invoice
    d = _doc("INVOICE", "[Your name / business] · [email] · [phone] · [address] · [EIN, optional]")
    t = d.add_table(rows=5, cols=2)
    for i, (a, b) in enumerate([("Invoice #", "[2027-001]"), ("Invoice date", "[date]"), ("Due date", "[date + 14 days]"),
                                ("Bill to", "[Client name, company, address]"), ("Project / PO", "[project, PO number]")]):
        t.cell(i, 0).text, t.cell(i, 1).text = a, b
    d.add_paragraph()
    t = d.add_table(rows=5, cols=4)
    t.style = "Table Grid"
    for j, h in enumerate(["Description", "Qty", "Rate", "Amount"]):
        t.cell(0, j).text = h
    for i, row in enumerate([("[Deliverable, per proposal dated ...]", "1", "[$]", "[$]"),
                             ("[Deposit received on ...]", "1", "[−$]", "[−$]"), ("", "", "", ""), ("", "", "Total due", "[$]")], 1):
        for j, v in enumerate(row):
            t.cell(i, j).text = v
    d.add_paragraph()
    d.add_paragraph("How to pay: [bank transfer details / pay-now link]. Please include the invoice number.")
    d.add_paragraph("Due by the date above. Late payments are subject to the late fee in our agreement, where allowed by law.")
    d.add_paragraph("Thank you for your business.").runs[0].bold = True
    out.append(folder / "4-Invoice-Template.docx")
    d.save(out[-1])
    return out


EMAILS = [
    ("New inquiry: reply", "Re: [their subject]",
     "Hi [Name],\n\nThanks for getting in touch about [project]. It sounds like the goal is [goal in their words]. "
     "A few quick questions so I can give you a useful quote:\n\n1. What does success look like in [3] months?\n"
     "2. What's your timeline, and is there a hard deadline?\n3. Do you have a budget range in mind?\n\n"
     "If it's easier, here's a link to book a 20-minute call: [link].\n\n[Your name]"),
    ("Sending a proposal", "Proposal: [project]",
     "Hi [Name],\n\nAs promised, here's the proposal for [project]: [link/attachment]. It covers scope, timeline and two "
     "options, [A] at [$] and [B] at [$].\n\nIf it looks right, reply \"go\" and I'll send the agreement and deposit "
     "invoice to lock in a [date] start.\n\n[Your name]"),
    ("Proposal follow-up (3–4 days later)", "Re: Proposal: [project]",
     "Hi [Name],\n\nChecking in on the proposal for [project]. Any questions I can answer, or anything you'd like "
     "adjusted? I'm holding [date] for the start for now; I can keep it until [date].\n\n[Your name]"),
    ("Scope creep, politely", "Re: [thread]",
     "Hi [Name],\n\nHappy to help with [new request]. It's outside what we agreed in the proposal, so I'll send a quick "
     "change order: [$ / hours], and it would move delivery to [date]. Want me to go ahead, or keep it for a later phase?\n\n[Your name]"),
    ("Raising your rate (existing client)", "An update to my rates from [date]",
     "Hi [Name],\n\nI've loved working on [projects] with you. From [date, 30–60 days out], my rate for new work will be "
     "[$new] (currently [$old]). Anything booked before then stays at the current rate.\n\nThank you for being a great "
     "client, and I'm looking forward to [next thing].\n\n[Your name]"),
    ("Sending an invoice", "Invoice [#] for [project], due [date]",
     "Hi [Name],\n\nAttached is invoice [#] for [project]: [$amount], due [date]. You can pay here: [pay-now link].\n\n"
     "Thanks again, it was great working on this.\n\n[Your name]"),
    ("Friendly reminder (3 days before due)", "Reminder: invoice [#] due [date]",
     "Hi [Name],\n\nA quick reminder that invoice [#] ([$amount]) is due on [date]. Here's the payment link again: "
     "[link].\n\nThanks!\n[Your name]"),
    ("Overdue: day 1", "Invoice [#] is now due",
     "Hi [Name],\n\nInvoice [#] for [$amount] was due yesterday. Could you check it's in your payment run? If it's already "
     "on its way, thank you and please ignore this. Payment link: [link].\n\n[Your name]"),
    ("Overdue: day 7", "Invoice [#]: 7 days overdue",
     "Hi [Name],\n\nInvoice [#] ([$amount]) is now a week overdue. Can you let me know when it will be paid? If something's "
     "wrong with the invoice, tell me and I'll fix it today. Under our agreement, a late fee applies from [date].\n\n[Your name]"),
    ("Overdue: day 21, pausing work", "Invoice [#]: pausing work until paid",
     "Hi [Name],\n\nInvoice [#] for [$amount] is now three weeks overdue and I haven't heard back. As set out in our "
     "agreement, I'm pausing work on [project] until it's paid. I'd really like to keep going, so please pay at [link] "
     "or reply with a date.\n\n[Your name]"),
    ("Final notice", "Final notice: invoice [#]",
     "Hi [Name],\n\nThis is a final notice for invoice [#] ([$amount] plus [$late fee]), now [X] days overdue. If it isn't "
     "paid or a payment plan agreed by [date, 7 days], I'll pass it to [small claims court / a collections service]. "
     "I'd much rather sort this out directly.\n\n[Your name]"),
    ("Asking for a testimonial", "A quick favour?",
     "Hi [Name],\n\nNow that [project] is live, would you be willing to write two or three sentences about working "
     "together? What was the problem, and what changed? I'll use it on my site with your name and company, unless you'd "
     "prefer initials. Totally fine to say no.\n\n[Your name]"),
    ("Project wrap-up", "[Project]: final files + what's next",
     "Hi [Name],\n\nEverything for [project] is here: [link]. Quick recap: [what was delivered]. The final invoice "
     "is attached.\n\nIf you need [related service] later, I'd love to help, and I keep a few slots each month for past "
     "clients.\n\n[Your name]"),
    ("Saying no (wrong fit or below your floor)", "Re: [project]",
     "Hi [Name],\n\nThank you for thinking of me for [project]. At the budget you mentioned, I'm not the right fit, and I'd "
     "rather say so now than do a rushed job. [Optional: For [$], I could do [smaller scope]. / You might try [resource].]\n\n"
     "Best of luck with it,\n[Your name]"),
]


def build_emails(path: Path) -> Path:
    d = _doc("Client Email Scripts", "14 emails for the whole client cycle: inquiry to final notice. From the 1099 Money Freelancer Money Bundle.")
    d.add_paragraph("Copy, paste, replace the [brackets], and make each one sound like you. Keep them short: "
                    "every email should have one job and one clear next step.")
    for i, (name, subj, body) in enumerate(EMAILS, 1):
        d.add_heading(f"{i}. {name}", 2)
        _para(d, subj, "Subject: ")
        for chunk in body.split("\n\n"):
            d.add_paragraph(chunk)
    d.add_paragraph("Late fees and collections rules differ by state and country: check what your agreement and local law "
                    "allow before charging or escalating. Not legal advice.").runs[0].italic = True
    path.parent.mkdir(parents=True, exist_ok=True)
    d.save(path)
    return path


def build_all(root: Path = HERE) -> list[Path]:
    kit = root / "rate-contract-kit"
    files = [build_xlsx(kit / "Rate-and-Invoice-Kit.xlsx")]
    files += build_docs(kit / "templates")
    files.append(build_emails(root / "bundle" / "Client-Email-Scripts.docx"))
    return files


if __name__ == "__main__":
    if "--check" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            fs = build_all(Path(tmp))
            assert all(f.stat().st_size > 5000 for f in fs), fs
            print("ok", len(fs), "files")
    else:
        for f in build_all():
            print(f.relative_to(HERE))
