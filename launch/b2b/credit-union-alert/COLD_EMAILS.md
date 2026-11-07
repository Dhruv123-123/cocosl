# Cold-email pack: Weekly Scam Alert for credit unions

**You send every one of these yourself, by hand, from your own inbox. Nothing here has been sent.**

## Before the first email (one-time)

1. Build a sample pack with the prospect's name on it? **No.** Use the fictional *Sample Community Credit
   Union* pack (`out/sample-community-cu.zip`) for first contact. Branding a pack with a real credit
   union's name and logo before they ask can look like you're using their brand without permission.
   Offer to make one with their logo once they reply.
2. Fill `{{YOUR_NAME}}`, `{{YOUR_EMAIL}}`, `{{YOUR_PHONE}}` in `sales-sheet.html` and re-render the PDF.
3. Decide your mailing address for the footer (CAN-SPAM needs a valid postal address in commercial
   email; a PO box you already have is fine). Don't buy anything just for this; use what you have.
4. Payment: the sheet says "Invoiced; ACH or card". Keep the payment links as placeholders
   (`{{PAYMENT_LINK_ESSENTIALS}}`, `{{PAYMENT_LINK_STANDARD}}`, `{{PAYMENT_LINK_PLUS}}`) until a credit
   union says yes. Most will want an invoice anyway.

## Who to write to

Small credit unions rarely publish named staff emails. In order of preference:

1. **Marketing or member experience manager**, if their own site lists a name and email.
2. **CEO or president** at credit unions under about $150M in assets (they often own marketing).
3. **General contact email** from their own site (info@, memberservices@), addressed to marketing.
4. **Contact form** on their own site (short version below).
5. **LinkedIn**, typed by hand to one person you found on the credit union's own site or news
   release (connection note below). No automation tools.

Never guess an email address, buy a list, or scrape a directory.

## Sending rules

- 5 to 8 new credit unions a day, Tuesday to Thursday mornings. Follow-ups count separately.
- Plain text, no images, no attachment and no link in email 1 (it keeps you out of spam folders).
- Stop at the first "no" or "unsubscribe" and mark it in `PROSPECTS.csv` → `notes`.
- Every email ends with your name, mailing address and an opt-out line.
- Log every send in the tracker columns you add to `PROSPECTS.csv` (sent, follow-up 1, follow-up 2,
  reply, outcome).

Tokens: `{First name}`, `{CU name}`, `{City}`, `{Personal line}` (one true sentence from their site or
news, such as a merger, a new branch, a fraud warning they posted), `{Your name}`, `{Your mailing address}`.

---

## Email 1: the sample offer (day 0)

**Subject options** (pick one):
- `Weekly scam alert for {CU name} members`
- `A done-for-you scam alert for {City} members`
- `Question about member fraud education at {CU name}`

> Hi {First name},
>
> {Personal line}
>
> I write Scam Decoded, a weekly plain-English scam alert. I've started making a version that credit
> unions send under their own name: one scam a week, with a member email, a social post and a lobby
> screen slide, each with your logo and phone number. Every pack arrives 7 days early so your
> compliance team can review it, and you never share member data with me.
>
> Imposter scams were the most-reported fraud in the US last year, with more than $3.5 billion lost
> (FTC, March 2026). When members get a strange call, they call you.
>
> Can I send you a free 4-week sample pack? It's built for a made-up credit union so you can see
> exactly what members would get.
>
> Thanks,
> {Your name}
> Scam Decoded · {Your mailing address}
> If you'd rather not hear from me again, just reply "no thanks" and I won't write again.

## Email 1, CEO version (small credit unions)

**Subject:** `Scam alerts for {CU name} members, without adding to your team's work`

> Hi {First name},
>
> {Personal line}
>
> Most credit unions your size don't have someone writing fraud education every week, but members
> still need it. I make a weekly scam alert credit unions send under their own name: a member email,
> a social post and a lobby slide, delivered 7 days early for review. $49 to $99 a month, and the first
> 3 credit unions get 2 months free.
>
> Want me to send the 4-week sample?
>
> {Your name}
> Scam Decoded · {Your mailing address}
> Reply "no thanks" and I won't write again.

## Contact-form version (under 600 characters)

> Hi, I'm {Your name} from Scam Decoded. I make a weekly scam alert that credit unions send to members
> under their own brand (email, social post and lobby slide, delivered 7 days early for compliance
> review, no member data shared). Could you pass this to whoever handles marketing or member
> education? I'd be glad to send a free 4-week sample. {Your email}

## LinkedIn connection note (under 300 characters)

> Hi {First name}, I make a weekly scam alert credit unions send to members under their own brand,
> reviewed by their compliance team before it goes out. Happy to share a free sample if it's useful
> for {CU name}.

---

## Follow-up 1 (day 4, same thread)

> Hi {First name}, just floating this back up. Happy to send the 4-week sample if it's useful; if
> someone else handles member education, I'd be grateful for their name.
>
> {Your name}

## Follow-up 2 (day 10, same thread): give something useful

> Hi {First name},
>
> One last note, with something you can use either way. The scam we'd cover first is the fake
> "fraud department" call: caller ID shows the credit union's name, and the caller asks the member to
> read back a code "to block a charge". That code is a sign-in or payment approval. The FTC has
> warned about it: https://consumer.ftc.gov/consumer-alerts/2024/06/got-call-about-fraud-activity-your-bank-account-it-could-be-scammer
>
> A one-line reminder in your next newsletter, "we will never ask you to read back a code", stops a
> lot of it. If you'd like the full weekly version with your branding, the first 3 credit unions get
> 2 months free.
>
> {Your name}
> Scam Decoded · {Your mailing address}
> Reply "no thanks" and I won't write again.

## Final note (day 21): only if they opened a conversation and went quiet

> Hi {First name}, I'll stop following up here. If member scam education comes up later this year,
> the offer stands. Wishing the {CU name} team a quiet fraud season.

---

## Replies

**"Yes, send the sample."**
> Here it is: the 4-week sample (emails, social images, lobby slides, posters, staff briefs and
> sources) for a made-up credit union, plus a one-page overview and our compliance note. If you send
> me your logo, brand color and member service number, I'll make a version with your branding so your
> team can see it as members would.

Attach: `sample-community-cu.zip`, `sales-sheet.pdf`, `COMPLIANCE_NOTE.pdf` (print the markdown to PDF).

**"Send me the branded version."** Make `clients/<slug>.json` (see `DELIVERY_WORKFLOW.md`), run
`python3 build.py credit-union-alert --brand credit-union-alert/clients/<slug>.json` (from `launch/b2b/`), and send the zip. Ask them to confirm the "never ask"
line is accurate for them.

**"What does it cost?"**
> Essentials is $49 a month (email, social post, lobby slide); Standard is $99 (adds a branch poster,
> a staff huddle brief and the topic calendar a quarter ahead); Plus is $149 (adds a Spanish edition,
> local exclusivity and 2 custom issues a year). The first 3 credit unions get 2 months free and keep
> their price for a year.

**"Compliance would have to review."**
> Of course. Every pack arrives 7 days before its send date for exactly that, and edits come back
> within a business day. I've attached the note we give compliance teams: how we source things and
> what we never say. Happy to answer their questions directly.

**"We already get content from [our league / a vendor / our core provider]."**
> Makes sense. Does it give you something new every week, with your branding, ready to send? If it
> covers that, keep it. If there are gaps (lobby screens, social posts, or a faster weekly rhythm),
> the 2 free months are a low-risk way to compare.

**"No budget."**
> Understood. The Essentials plan is $49 a month, and the 2-month pilot is free with no contract, so
> you'd have results to show before it costs anything. If timing's the issue, when should I check
> back?

**"Who are you?"**
> I run Scam Decoded, an independent scam-education publisher. Every alert is checked against
> official sources (FTC, FBI, IRS, CFPB) before it ships, and the sources are listed in each issue.
> I'm not a lawyer and don't give legal advice; your team has final say on everything.

**"Does this make us compliant / count as our training?"**
> I can't say that. It's member education content, and how it fits your program is your team's call.

**"No thanks" / "unsubscribe"** → Reply "Understood, I won't write again." Mark it in the tracker and never
contact them again.
