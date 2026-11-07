#!/usr/bin/env python3
"""Write a one-page services agreement and an invoice template for every offer.

    cd launch/b2b && python3 paperwork.py && python3 build.py   # build renders them to out/onboarding/*.pdf

Output: <product>/onboarding/services-agreement.html and <product>/onboarding/invoice.html. They're
TEMPLATES: every party, price and date is a {{TOKEN}}, and the agreement must be checked by a lawyer in
Dhruv's state before anyone signs it. Nothing here is legal advice. Payment links stay placeholders.
Edit the OFFERS table below (or the shared wording) and rerun; don't hand-edit the generated files.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

OFFERS = {
    "credit-union-alert": dict(
        service="Weekly Scam Alert", what="white-label member education", color="#1F5C8B",
        cadence="one issue a week", lead="7 days", audience="its members",
        deliverables="member email (HTML and text), social image and caption, lobby screen slide, sources page; "
                     "branch poster and staff brief on Standard and Plus",
        unit="month", rate_word="Monthly fee", term="month to month",
        extra="The Client is responsible for its own regulatory review (including NCUA and state rules on advertising "
              "and member communications) before each send."),
    "employer-wellness": dict(
        service="Money Made Simple at Work", what="white-label employee financial education", color="#2E6B4F",
        cadence="one issue a month", lead="14 days", audience="its employees",
        deliverables="employee email (HTML and text), intranet or chat post with image, breakroom slide; flyer and "
                     "manager talking points on Growth and above",
        unit="month", rate_word="Monthly fee", term="month to month",
        extra="Content is general education only. Plan details (retirement plan, match, EAP) appear only in the "
              "Client's own wording, and the Client confirms them. Nothing is investment, tax or legal advice, and the "
              "Provider never sees employee data. Where a broker refers the Client, any referral fee is disclosed in "
              "writing."),
    "community-scam-watch": dict(
        service="Scam Watch (large print)", what="scam-awareness materials for older adults", color="#6B3FA0",
        cadence="one pack a month", lead="21 days", audience="its patrons and members",
        deliverables="large-print handout, bulletin board flyer, screen slide, 10-minute talk guide, newsletter "
                     "blurb and social post",
        unit="month", rate_word="Monthly fee", term="month to month",
        extra="The Client may print and copy the materials freely for its own sites. Where a credit union sponsors "
              "the Client, the sponsor line is the only sponsor content, and the sponsor sees no patron data."),
    "freelancer-client-letter": dict(
        service="Freelancer Money Notes", what="white-label client newsletter", color="#9A5B13",
        cadence="one issue a month", lead="14 days", audience="its clients",
        deliverables="client email (HTML and text), social image and caption, sources page; printable client "
                     "handout and team notes on Standard and Plus",
        unit="month", rate_word="Monthly fee", term="month to month",
        extra="Content is general education only and makes no claims about the Client's services. The Client reviews "
              "each issue against its own professional standards (including Circular 230 and its state board's "
              "rules where they apply) before sending."),
    "schools": dict(
        service="Money Made Simple for Schools", what="weekly financial literacy mini-lessons", color="#1F5F4A",
        cadence="one lesson a week during the school year", lead="14 days", audience="its students",
        deliverables="lesson page (HTML and text), class slide, student handout, LMS image, teacher notes and "
                     "sources",
        unit="school year", rate_word="Annual fee", term="for the school year named above, renewing only by a new "
                                                            "order or purchase order",
        extra="The Provider collects, receives and stores no student data: no names, emails, logins or tracking. "
              "The Client's teachers post the lessons themselves. A sponsor, if any, appears only in the credit "
              "line and never in lesson content. The Client may require its own vendor forms, W-9 and purchase "
              "order, which control payment terms where they differ."),
}

BASE_CSS = """
@page{size:8.5in 11in;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,Helvetica,sans-serif;color:#17202a;background:#fff}
.page{width:8.5in;height:10.98in;overflow:hidden;padding:.45in .55in .4in;display:flex;flex-direction:column}
.warn{background:#fdecec;border:1px solid #e3a5a5;color:#7a1f1f;font-size:10px;font-weight:700;padding:6px 9px;border-radius:5px;margin-bottom:10px}
"""

AGREEMENT = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Services agreement: {service}</title>
<!-- Generated by ../../paperwork.py. TEMPLATE ONLY: have a lawyer review it before use. Fill every {{{{TOKEN}}}}
     in a copy kept outside the repo (clients/), then print to PDF. -->
<style>{css}
h1{{font-size:21px;color:{color};margin-bottom:2px}}
.sub{{font-size:12px;color:#41505e;margin-bottom:10px;line-height:1.4}}
ol{{padding-left:16px}}
li{{font-size:11.5px;line-height:1.45;margin-bottom:6px}}
li b{{color:{color}}}
.sig{{display:flex;gap:28px;margin-top:auto;padding-top:8px;border-top:1px solid #dfe4e9}}
.sig div{{flex:1;font-size:11px;line-height:2.1}}
</style></head><body><div class="page">
<div class="warn">TEMPLATE, NOT LEGAL ADVICE. Have a lawyer licensed in {{{{GOVERNING_STATE}}}} review and adapt this before anyone signs it.</div>
<h1>Services agreement: {service}</h1>
<p class="sub">Between <b>{{{{YOUR_BUSINESS_NAME}}}}</b>, {{{{YOUR_ADDRESS}}}} (the "Provider"), and <b>{{{{CLIENT_LEGAL_NAME}}}}</b>, {{{{CLIENT_ADDRESS}}}} (the "Client"). Effective {{{{START_DATE}}}}.</p>
<ol>
<li><b>Services.</b> The Provider supplies {what} branded for the Client: {cadence}, each with {deliverables}. Plan: {{{{PLAN}}}}. Each issue is delivered at least {lead} before its scheduled date.</li>
<li><b>Review and approval.</b> The Client reviews each issue and may request edits; the Provider makes reasonable edits within 1 business day. Nothing is used until the Client approves it in writing (email is enough). Silence is not approval.</li>
<li><b>The Client sends it.</b> The Client distributes each issue to {audience} from its own systems. The Provider sends nothing on the Client's behalf and receives no personal data about {audience}. {extra}</li>
<li><b>Fees.</b> {rate_word}: {{{{FEE}}}} per {unit}, invoiced {{{{BILLING: monthly in advance / annually}}}}, due within 30 days of invoice. {{{{PILOT_TERMS_OR_DELETE: e.g. the first 2 months are free under the founding pilot.}}}} Prices are fixed for 12 months from the effective date.</li>
<li><b>Term and ending it.</b> This agreement runs {term}. Either party may end it with 30 days' written notice. Fees for issues already delivered remain due; nothing else is owed.</li>
<li><b>Content license.</b> The Provider owns the content and grants the Client a non-exclusive license to use, edit and distribute each delivered issue to {audience}, under the Client's brand, during the term and afterward for issues delivered while the agreement was in force. The Client may not resell or relicense the content to others.</li>
<li><b>The Client's brand.</b> The Client grants the Provider a limited license to use its name, logo and supplied details only to produce the Client's issues. The Provider will not name the Client as a customer without written permission.</li>
<li><b>Accuracy and AI disclosure.</b> Each issue is general education, not financial, tax, legal or investment advice. The Provider drafts content with AI help, and a person checks every fact against the cited public sources before delivery. Each issue carries a short AI disclosure, which the Client may reword but not remove. If a fact turns out wrong, the Provider sends a correction promptly at no charge.</li>
<li><b>No guarantees, and a cap.</b> The Provider doesn't promise any result (for example, fewer fraud losses or enrollments). Except for a party's gross negligence or willful misconduct, each party's total liability under this agreement is limited to the fees paid in the 3 months before the claim, and neither party is liable for indirect or consequential damages.</li>
<li><b>General.</b> The Provider is an independent contractor. This is the whole agreement, and changes must be in writing and signed by both. {{{{GOVERNING_STATE}}}} law governs. Notices go to the emails below.</li>
</ol>
<div class="sig">
  <div><b>Provider:</b> {{{{YOUR_BUSINESS_NAME}}}}<br>Signature: ______________________<br>Name and title: {{{{YOUR_NAME}}}}<br>Email: {{{{YOUR_EMAIL}}}}<br>Date: ____________</div>
  <div><b>Client:</b> {{{{CLIENT_LEGAL_NAME}}}}<br>Signature: ______________________<br>Name and title: {{{{CLIENT_SIGNER}}}}<br>Email: {{{{CLIENT_EMAIL}}}}<br>Date: ____________</div>
</div>
</div></body></html>
"""

INVOICE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Invoice {{{{INVOICE_NUMBER}}}}: {service}</title>
<!-- Generated by ../../paperwork.py. Copy it per invoice (outside the repo, e.g. clients/invoices/), fill every
     {{{{TOKEN}}}}, then print to PDF (Letter, no margins, background graphics on). {{{{PAYMENT_LINK}}}} stays a
     placeholder until a payment account exists. Spend nothing to set one up. -->
<style>{css}
.top{{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:4px solid #E0A526;padding-bottom:14px}}
.from b{{font-size:18px;display:block;margin-bottom:4px}}
.from,.meta{{font-size:12.5px;line-height:1.55;color:#41505e}}
h1{{font-size:34px;letter-spacing:.06em;color:{color};text-align:right}}
.meta{{text-align:right;margin-top:6px}}
.meta b{{color:#17202a}}
.parties{{display:flex;gap:30px;margin-top:22px}}
.parties div{{flex:1;font-size:12.5px;line-height:1.55}}
.label{{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{color};margin-bottom:4px}}
table{{width:100%;border-collapse:collapse;margin-top:26px}}
th,td{{font-size:12.5px;padding:10px 8px;text-align:left;border-bottom:1px solid #dfe4e9;vertical-align:top}}
th{{background:#f1f4f7;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em}}
td.n,th.n{{text-align:right;white-space:nowrap}}
.subl{{color:#41505e;font-size:11.5px;display:block;margin-top:3px}}
.totals{{margin-left:auto;width:3.2in;margin-top:10px}}
.totals div{{display:flex;justify-content:space-between;font-size:13px;padding:6px 8px}}
.totals .due{{background:{color};color:#fff;font-weight:700;font-size:15px;border-radius:6px;margin-top:4px}}
.pay{{margin-top:26px;background:#fff6dc;border-left:5px solid #E0A526;padding:12px 14px;font-size:12.5px;line-height:1.6}}
.notes{{margin-top:18px;font-size:11.5px;color:#41505e;line-height:1.55}}
.foot{{margin-top:auto;border-top:1px solid #dfe4e9;padding-top:8px;font-size:11px;color:#41505e;display:flex;justify-content:space-between}}
</style></head><body><div class="page">
<div class="top">
  <div class="from"><b>{{{{YOUR_BUSINESS_NAME}}}}</b>{{{{YOUR_NAME}}}}<br>{{{{YOUR_ADDRESS}}}}<br>{{{{YOUR_EMAIL}}}} · {{{{YOUR_PHONE}}}}</div>
  <div><h1>INVOICE</h1><div class="meta"><b>Invoice no.</b> {{{{INVOICE_NUMBER}}}}<br><b>Date</b> {{{{INVOICE_DATE}}}}<br><b>Due</b> {{{{DUE_DATE}}}} (Net 30)<br><b>PO / vendor no.</b> {{{{CLIENT_PO_NUMBER}}}}</div></div>
</div>
<div class="parties">
  <div><div class="label">Bill to</div><b>{{{{CLIENT_LEGAL_NAME}}}}</b><br>Attn: {{{{CLIENT_AP_CONTACT}}}}<br>{{{{CLIENT_ADDRESS}}}}<br>{{{{CLIENT_AP_EMAIL}}}}</div>
  <div><div class="label">Service</div>{service}: {what}<br>Plan: <b>{{{{PLAN}}}}</b><br>Service period: {{{{PERIOD_START}}}} to {{{{PERIOD_END}}}}</div>
</div>
<table>
  <tr><th>Description</th><th class="n">Qty</th><th class="n">Rate</th><th class="n">Amount</th></tr>
  <tr><td>{service}, {{{{PLAN}}}} plan<span class="subl">{cadence_cap} for {{{{PERIOD_START}}}} to {{{{PERIOD_END}}}}: {deliverables}.</span></td>
    <td class="n">{{{{QTY}}}} ({unit}s)</td><td class="n">{{{{RATE}}}}</td><td class="n">{{{{LINE_TOTAL}}}}</td></tr>
  <tr><td>{{{{OPTIONAL_LINE: e.g. Founding pilot (no charge)}}}}<span class="subl">Delete this row if it doesn't apply.</span></td>
    <td class="n">{{{{OPTIONAL_QTY}}}}</td><td class="n">{{{{OPTIONAL_RATE}}}}</td><td class="n">{{{{OPTIONAL_AMOUNT}}}}</td></tr>
</table>
<div class="totals"><div><span>Subtotal</span><span>{{{{SUBTOTAL}}}}</span></div><div><span>Tax</span><span>{{{{TAX_OR_NONE}}}}</span></div><div class="due"><span>Amount due</span><span>{{{{AMOUNT_DUE}}}}</span></div></div>
<div class="pay"><b>How to pay:</b> {{{{PAYMENT_LINK}}}} (card or ACH), or a check payable to {{{{YOUR_BUSINESS_NAME}}}} at the address above. Please put the invoice number on your payment.</div>
<p class="notes">Under the services agreement dated {{{{AGREEMENT_DATE}}}}. Questions about this invoice: {{{{YOUR_EMAIL}}}}. {{{{W9_NOTE_OR_DELETE: A W-9 is attached for your vendor file.}}}}</p>
<div class="foot"><span>{{{{YOUR_BUSINESS_NAME}}}} · {{{{YOUR_ADDRESS}}}}</span><span>Thank you.</span></div>
</div></body></html>
"""


def main() -> None:
    for product, o in OFFERS.items():
        d = ROOT / product / "onboarding"
        d.mkdir(exist_ok=True)
        cadence_cap = o["cadence"][0].upper() + o["cadence"][1:]
        (d / "services-agreement.html").write_text(AGREEMENT.format(css=BASE_CSS, **o))
        (d / "invoice.html").write_text(INVOICE.format(css=BASE_CSS, cadence_cap=cadence_cap, **o))
        print(f"wrote {product}/onboarding/services-agreement.html and invoice.html")


if __name__ == "__main__":
    main()
