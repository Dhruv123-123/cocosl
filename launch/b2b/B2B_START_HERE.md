# B2B: start here (one page)

Five white-label offers are ready. Nothing has been sent; you send every email yourself, by hand, from your
one inbox. That inbox is shared with the ad studio, and from **Tue 1 Dec 2026, 4 of its 10 daily sends are
B2B** (at most 2 new first emails). The full plan is in `OUTREACH_DATES.md`, and the setup (names,
address, `{{YOUR_...}}` fields) is in `LAUNCH_CHECKLIST.md` sections 1–2. Do those first, in about 40 minutes.

## Which offer first: accounting firms

**Freelancer Money Notes, to small CPA and bookkeeping firms**, because:
- they have to hear from you **before mid-January**, when tax season closes their inbox until Apr 19;
- it's the cheapest yes ($39–$129 a month) and the owner decides alone;
- the December pitch has a true, timely hook: the Jan 15 payment and 1099 Money's tax-season series
  (use `freelancer-client-letter/TAX_SEASON_LEAD_IN.md` for email 1).

Then credit unions from January (time pilots to National Consumer Protection Week, Feb 28 – Mar 6, and offer the $149 week-only package in `ncpw-sponsor/` to any that say weekly is too much; orders close Jan 29), Scam
Watch in February, schools in spring, employers from June. That order is already in `OUTREACH_DATES.md`.

## The first 20 sends (Dec 1 – Dec 10), under the 4-a-day cap

Highest fit score first. Before each Email 1, open the firm's own site, fill `website` and `contact_route` in
`freelancer-client-letter/PROSPECTS.csv`, and write one true `{Personal line}`. Skip any firm that's closed or
already sends a client newsletter, and move the next one up.

| Day | Sends |
|---|---|
| Tue Dec 1 | Email 1: Coulston Accounting PC (MT) · Orazem Tax & Financial (MT) |
| Wed Dec 2 | Email 1: Berrett Tax & Finance (ID) · Idaho Tax & Bookkeeping Services (ID) |
| Thu Dec 3 | Email 1: Bates Bean Counting (ID) · Northwest Tax Advisors (ID) |
| Fri Dec 4 | Email 1: Iron Oak Accounting (ID) · Middleton Accounting & Tax Services (ID) |
| Mon Dec 7 | Follow-up 1: Coulston · Orazem · Berrett · Idaho Tax & Bookkeeping |
| Tue Dec 8 | Follow-up 1: Bates Bean Counting · Northwest Tax Advisors · Iron Oak · Middleton |
| Wed Dec 9 | Email 1: Atticus Accounting (ID) · Bookkeeping by CHOICE (ID) |
| Thu Dec 10 | Email 1: Elite Accounting (ID) · Kane Tax & Accounting (ID) |

That's 20 emails: 12 first emails and 8 follow-ups. From Fri Dec 11, follow `OUTREACH_DATES.md` day by day. Follow-up 1 is in
`freelancer-client-letter/README.md`; follow-up 2 (day 10) is in `TAX_SEASON_LEAD_IN.md`. If someone replies,
skip their later rows.

## When someone replies

| They say | You do | Files |
|---|---|---|
| "Yes, send the sample" | Reply the same day. Attach `out/demo-packet.pdf`; send `out/demo-packet.zip` if they want every format. Offer a free version with their logo. Then use the after-sample sequence if they go quiet. | `<offer>/out/`, `<offer>/FOLLOW_UP_SEQUENCE.md` |
| "Make one with our logo" | Run `python3 deliver.py <offer> --month 2027-01 --name "..." --logo <file> --set ...` and send the zip. Ask them to check every detail. | `README.md` (deliver.py) |
| "What does it cost?" / "Talk to compliance" / "We already have something" | Use the ready replies. Never promise results (fewer frauds, more enrollments). | `<offer>/COLD_EMAILS.md` → Replies (freelancer and schools: their `README.md`) |
| "Yes, let's do it" | Send the services agreement (**have a lawyer check it once first**), then the kickoff email and brand intake. First invoice after their approval. | `<offer>/onboarding/services-agreement.html`, `credit-union-alert/onboarding/README.md`, `<offer>/onboarding/invoice.html` |
| "Not now" | Ask which month suits them, note it in `PROSPECTS.csv`, and write then. | |
| "No thanks" / "unsubscribe" | Reply "Understood, I won't write again." Mark it in the CSV. Never email them again, from any offer. | `PROSPECTS.csv` |

**Every email carries your name, your mailing address and an opt-out line.** Don't add links or attachments
to a first email, don't guess an address, and don't buy a list.

Track every send and reply in `PIPELINE.xlsx` (`python3 pipeline_tracker.py`), and use `OBJECTIONS.md` for pushback.
