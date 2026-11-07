# Onboarding kit: the first credit union client

Everything to go from "yes" to the first member send in about **3 weeks**, without a call you didn't
plan for. Nothing here is sent automatically; Dhruv sends every email himself.

| File | Use it |
|---|---|
| `KICKOFF_EMAIL.md` | The kickoff email (the day they say yes), plus the 4 emails that follow it: intake reminder, branded preview, "you're live", and the pilot-ending note. |
| `BRAND_INTAKE.md` | The brand intake form, attached to the kickoff email. The table further down shows which answers go into `clients/<slug>.json`. Builds to `out/onboarding/BRAND_INTAKE.pdf`. |
| `APPROVAL_WORKFLOW.md` | How each weekly issue gets approved: who reviews, the Friday edit deadline, what counts as a sign-off, emergency pulls, and the sign-off log. |
| `approval-log.csv` | The sign-off log, one row per issue per client. Keep it; it's the record if anyone asks who approved what. |
| `invoice.html` | Invoice template with `{{PAYMENT_LINK}}` and the other fields as placeholders. Builds to `out/onboarding/invoice.pdf`. |
| `../CONTENT_CALENDAR.md` | The 12 weeks of topics after the samples. Send the client the next 4 weeks of it with the preview. |

## The timeline

Dates assume they say yes on a Tuesday, three weeks before the first member send. Shift everything
together if not.

| Day | What | Who | File |
|---|---|---|---|
| **Yes (day −21)** | Send the kickoff email with the intake form, the compliance note and the content calendar. | Dhruv | `KICKOFF_EMAIL.md` §1 |
| Day −18 | If the intake isn't back, send the reminder. | Dhruv | `KICKOFF_EMAIL.md` §2 |
| Day −16 (latest) | Intake back. Copy `brands/example.json` to `clients/<slug>.json` and fill it from the form. | Dhruv | Mapping table below |
| Day −15 | Build the 4 sample issues in their branding: `python3 build.py credit-union-alert --brand credit-union-alert/clients/<slug>.json` (from `launch/b2b/`). Check every file by eye: logo, colors, phone number, footer. | Dhruv | |
| Day −14 | Send the branded preview. Their compliance reviewer approves the **template** once (footer, promise line, colors). | Dhruv, then client | `KICKOFF_EMAIL.md` §3 |
| Day −10 | Template sign-off back. Log it as issue `TEMPLATE` in `approval-log.csv`. | Client, Dhruv | `APPROVAL_WORKFLOW.md` |
| **Day −7** | First real issue delivered; weekly cycle starts. | Dhruv | `APPROVAL_WORKFLOW.md` |
| **Day 0** | First member send. Send the "you're live" email the next morning. | Client, Dhruv | `KICKOFF_EMAIL.md` §4 |
| Pilot day 45 | Pilot-ending note with the first invoice (if they're a founding-pilot client). | Dhruv | `KICKOFF_EMAIL.md` §5, `invoice.html` |

## Where each intake answer goes in `clients/<slug>.json`

| Answer | Brand file field |
|---|---|
| 1.1 | `name`, `tokens.CU_NAME` |
| 1.2 | `tokens.CU_SHORT`; `initials` (2 letters, for the badge when there's no logo) |
| 2.1 | `logo` (URL or local path in `clients/`) |
| 2.2, 2.3 | `color`, `accent` |
| 3.1 | `tokens.CU_PHONE` |
| 3.2 | `tokens.CU_WEBSITE` |
| 3.3 | `promise` |
| 3.4 to 3.6 | `footer_lines` (one line each) |
| 4.2 | `unsubscribe` |
| 5.1 | `tier` (`essentials`, `standard` or `plus`) |
| 1.3 to 1.6, 4.3, 5.2 to 5.6 | Not in the brand file: keep them in your client notes and `approval-log.csv`. |

## Before the kickoff email goes out

- [ ] Fill `{{YOUR_NAME}}`, `{{YOUR_EMAIL}}`, `{{YOUR_PHONE}}` in the emails, `invoice.html` and the sales sheet.
- [ ] Decide your business name for invoices (`{{YOUR_BUSINESS_NAME}}`) and mailing address.
- [ ] Have a W-9 ready: credit unions usually ask for one before paying a new vendor.
- [ ] Expect a **vendor due-diligence questionnaire**. The honest answers are short: you never receive
      member data, never log in to their systems, and send nothing to members yourself
      (`COMPLIANCE_NOTE.md` §GLBA/vendor). Answer it; don't guess at certifications you don't have.
- [ ] Payment links stay as placeholders until you set them up. Don't create a payment account just
      for the kickoff; the first invoice isn't due until the pilot ends.

## Rules that carry over

- Never use the client's name or logo in your own marketing without written permission.
- Never log in to their email platform or social accounts, and never send to members.
- `clients/` is gitignored. Keep brand files and logos out of the repo.
