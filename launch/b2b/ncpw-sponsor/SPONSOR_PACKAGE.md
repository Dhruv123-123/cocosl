# Consumer Protection Week package for credit unions (Feb 28 – Mar 6, 2027)

A one-time, five-day package: one white-label member alert a day, Mon Mar 1 to Fri Mar 5, 2027, for
[National Consumer Protection Week](https://consumer.ftc.gov/ncpw) (the FTC's week "to talk about frauds,
scams, and consumer rights"). It's an easy first yes for a credit union that isn't ready for a weekly
subscription, and a natural lead-in to one. Nothing here has been sent. Prices are proposals, contacts and
payment links are placeholders.

**Lined up with Scam Decoded's own NCPW week** (PR #9, alerts #53–#57): same five topics on the same days, and
the same wording for the key facts (below). The client copy is written separately and never names Scam Decoded,
so a credit union's members see only the credit union.

| Day | Topic | Key fact, worded the same in both packs | Source |
|---|---|---|---|
| Mon Mar 1 | Recovery fees | "Never pay upfront for a refund or help with a refund." Real agencies won't ask for money or account numbers, or promise your money back. | [FTC](https://consumer.ftc.gov/articles/refund-and-recovery-scams) |
| Tue Mar 2 | "FTC" calls | The FTC will never call you to demand money, never threaten you with arrest, never promise you a prize. | [FTC alert 2023/07](https://consumer.ftc.gov/consumer-alerts/2023/07/ftc-wont-demand-money-threaten-you-or-promise-you-prize) |
| Wed Mar 3 | Free trials | Read the cancel terms before you give your card; dispute charges you didn't agree to. | [FTC 2019](https://consumer.ftc.gov/consumer-alerts/2019/09/free-trials-and-tribulations), [FTC 2023](https://consumer.ftc.gov/consumer-alerts/2023/05/how-stop-subscriptions-you-never-ordered) |
| Thu Mar 4 | Fake debt collectors | No threats of arrest. Within 5 days of first contact, the creditor and amount in writing; 30 days to dispute. | [FTC](https://consumer.ftc.gov/articles/fake-abusive-debt-collectors), [FTC 2025](https://consumer.ftc.gov/consumer-alerts/2025/05/getting-calls-debt-collector-you-have-rights), [CFPB](https://www.consumerfinance.gov/ask-cfpb/what-is-an-unfair-deceptive-or-abusive-practice-by-a-debt-collector-en-1401/) |
| Fri Mar 5 | Credit repair | Can't charge before they help; no one can remove accurate, current information. | [FTC](https://consumer.ftc.gov/articles/fixing-your-credit-faqs) |

If Scam Decoded changes a fact or a date, change it in `issues.json` too (and the reverse).

## What the credit union gets

- **Five daily packs** (`python3 build.py ncpw-sponsor`): member email (HTML + text), social post and caption,
  lobby slide, branch poster, staff huddle brief, sources page. All under the credit union's brand.
- **Press note** and **board line** (templates below).
- **Library add-on ($249 option):** `library-handout.html` (large print, one page, "shared by" the credit union)
  for up to 3 local libraries or senior centers, plus the talk outline below. Pair it with Scam Watch prospects
  in the same town (`community-scam-watch/PROSPECTS.csv`).

## Price (proposal)

| Option | Price |
|---|---|
| Week package | $149 one-time |
| Week package + library add-on (up to 3 venues) | $249 one-time |
| Weekly Scam Alert Standard or Plus subscribers | Included |
| Starts the weekly alert within 60 days | Package price credited against month 1 |

Why $149: about 1.5 months of the Standard plan for a week of daily content, below most small credit unions'
sign-off threshold for a one-off marketing buy. Payment link: `{{PAYMENT_LINK_NCPW}}` (leave it; invoice instead
with `credit-union-alert/onboarding/invoice.html`, changing the line item).

## Timeline

| When | What |
|---|---|
| Dec 1 – Jan 29 | Pitch (below). Fits the 4-a-day B2B slots after the accounting firms; send it to the credit union rows in `OUTREACH_DATES.md` that fall before Jan 29, or as a P.S. in their Follow-up 2. |
| **Jan 29, 2027** | Last day to order. |
| Feb 1–12 | Branding: run `python3 deliver.py ncpw-sponsor --month 2027-03 --name ... --logo ... --set CU_PHONE=...`. |
| **Feb 15** | Packs delivered (`deliver_by` in issues.json). Two weeks for compliance. |
| Feb 28 – Mar 6 | NCPW. The credit union sends Mon–Fri. Its weekly Mar 2 issue (government imposters) fits too, if it subscribes. |
| Mar 9 | Ask: "How did members respond? Want the weekly alert from April?" |

## Pitch email (plain text, no links or attachments)

> **Subject:** Consumer Protection Week, Mar 1–5
>
> Hi {First name},
>
> {Personal line: one true thing about their credit union.}
>
> National Consumer Protection Week runs Feb 28 to Mar 6 this year. I write a ready-made member alert for each
> day of it, Monday to Friday, under your credit union's name: email, social post, lobby slide and a short staff
> brief, every claim sourced to the FTC or CFPB. It's delivered by Feb 15 so compliance has two weeks.
>
> It's $149 for the week. Would a free sample day with your logo on it be useful?
>
> {Your name}
> {Your business name} · {Your mailing address}
> If this isn't for you, just reply "no thanks" and I won't write again.

**Follow-up (day 4, same thread):** "Quick nudge on the Consumer Protection Week alerts. Orders close Jan 29 so
packs are with you by Feb 15. Happy to send the sample day either way." + the same opt-out line.

**Already pitched the weekly alert?** Add one line to Follow-up 2: "If weekly is too much right now, there's also
a five-day Consumer Protection Week package (Mar 1–5) for $149."

## Press note template (for the credit union to send, not you)

> **{CU_NAME} shares a scam tip a day for National Consumer Protection Week**
>
> {CITY}, {STATE}, {DATE}: During National Consumer Protection Week, Feb 28 to Mar 6, {CU_NAME} will share one
> short alert a day with members and the community, covering refund "recovery" scams, government imposters,
> free-trial traps, fake debt collectors and up-front credit repair. "{Quote from the CEO or a branch manager.}"
> The alerts are on {CU_NAME}'s website and social channels, and in branches. Anyone who thinks they've been
> targeted can report it free at ReportFraud.ftc.gov. Contact: {name, phone, email}.

Don't say the FTC partners with or endorses the credit union.

**Board line:** "During National Consumer Protection Week we sent members five daily fraud alerts by email,
social and in branches{, and supported scam talks at N local libraries}."

## Talk outline for libraries and senior centers (20 minutes)

1. **(2 min)** Why this week: NCPW, and that anyone can be targeted.
2. **(12 min)** The five scams, one per handout row. For each: the made-up example from that day's alert, then the
   one rule. Ask "has anyone had a call like this?"
3. **(4 min)** What to do: hang up, call your bank or credit union on the number on your card, report at
   ReportFraud.ftc.gov.
4. **(2 min)** Hand out the large-print sheet. Credit union staff may say who they are; no selling, no sign-ups.

## Checks before sending anything

- [ ] Re-check the five source pages in January (the FTC posts its NCPW materials then).
- [ ] Confirm Scam Decoded's dates haven't moved (PR #9, alerts 53–57).
- [ ] Fill `{{YOUR_...}}` in `sales-sheet.html` and the `{{SPONSOR_...}}`/`{{VENUE_NAME}}` tokens in the handout per client.
