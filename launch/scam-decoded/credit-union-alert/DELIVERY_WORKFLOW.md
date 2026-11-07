# Delivery workflow: how a weekly issue is made and sent

About **2 to 3 hours a week** for the first client, plus about **10 minutes a week for each extra
client** (the content is shared; only the branding changes). Members get each issue on a **Tuesday**.
The credit union gets it **7 days earlier**.

## The weekly calendar

| When (relative to member send) | What | Who |
|---|---|---|
| **Day −21** | Pick the topic for the issue 3 weeks out. | You |
| **Day −14** | Write the issue in `issues.json`. | You (AI-assisted draft) |
| **Day −10** | Fact-check against the list in `COMPLIANCE_NOTE.md` §3. | You |
| **Day −8** | Build every client's pack: `python3 build.py --brand clients/<slug>.json --issue <id>`. | You |
| **Day −7 (Tuesday)** | Email each client their pack (the delivery email is below). | You |
| Day −7 to −4 | Client's compliance review. | Client |
| **Day −4 (Friday)** | Edit deadline. Apply edits, rebuild, resend within 1 business day. | You |
| **Day 0 (Tuesday)** | Client sends the email and posts the social image; lobby slide goes up. | Client |
| Day +1 | Note any member questions the client passes on: they're next month's topics. | You |

Keep **at least 2 issues finished ahead** so a sick week doesn't break the schedule.

## 1. Pick the topic (day −21)

Choose one scam that members are likely to meet in the send week. In order:

1. **A client's request** (Plus clients get 2 custom issues a year; any client's member questions count).
2. **The season**: tax season (Jan to Apr), holidays and delivery scams (Nov to Dec), back to school
   (Aug), Medicare open enrollment (Oct to Dec), summer travel and rentals.
3. **New official warnings**: FTC consumer alerts, FBI IC3 public service announcements, CFPB, IRS.
4. **The Scam Decoded calendar**: the newsletter (`sites/scam-decoded/content/newsletter/` on the
   Scam Decoded branch) already has issues planned through mid-2027. Reuse the research, not the text.
5. **Evergreen fillers** when nothing is pressing: fraud department calls, fake checks, gift card
   payment requests, account takeover, romance, grandparent and "Hi Mom" calls, P2P payment scams.

Don't repeat a topic within 8 weeks. Write the topic, the member send date and the source issue in
a new `issues.json` entry.

## 2. Write it (day −14)

Copy the shape of an existing entry in `issues.json`. Rules for credit union editions:

- **Rewrite**, don't paste, the Scam Decoded issue. Members of a credit union need "call us", not
  "check our site".
- Every "what to do" step that involves money says **call us at `{{CU_PHONE}}`**.
- No Scam Decoded links, products, affiliates or "From Scam Decoded" sections.
- Example messages are labelled made up.
- Keep the email at about 300 to 400 words.
- Lobby headline under 8 words; 3 bullets under 8 words each.
- Social caption under 450 characters, ending with the credit union's number.
- Staff brief: one thing members ask, one thing to say, one escalation line that defers to the
  credit union's own procedures.
- At least 2 sources per issue, official first.

Set `never_ask: true` only for issues where the promise box matters (impersonation of the credit
union itself).

## 3. Fact-check (day −10)

Run the 8-point list in `COMPLIANCE_NOTE.md` §3. Open every source link. Update `reviewed` at the top
of `issues.json` to today's date.

## 4. Build (day −8)

```bash
cd launch/scam-decoded/credit-union-alert
python3 build.py                                          # rebuilds the sample + placeholder master
python3 build.py --brand clients/<slug>.json --issue <id> # one client, one issue
```

Each build writes `out/<slug>/week-N-<id>/` (email.html, email.txt, social.png + social.txt,
lobby.png, poster.pdf, staff-brief.txt, sources.md) and `out/<slug>.zip`. It **fails** if any
`{{TOKEN}}` is left unfilled. PNG and PDF need Node with Playwright (`render.mjs`); without them you
get the HTML only.

Open `email.html` in a browser and look at `social.png` and `lobby.png` for every client before you
send. Check the logo, the color and the phone number.

Tier contents: Essentials clients get `email.*`, `social.*`, `lobby.png` and `sources.md`. Standard
and Plus also get `poster.pdf` and `staff-brief.txt`. Set `"tier": "essentials"` in the client's brand
file and the build leaves the extras out.

## 5. Deliver (day −7)

Email each client's contact (marketing, plus compliance if they asked to be copied):

> **Subject:** Scam Alert for {send date}: {topic}
>
> Hi {name}, here's the pack for {send date}: {one-line topic}. Files attached (or: in your shared
> folder). Edits by Friday and I'll send updated files within a business day. Sources are in
> sources.md.

Attach the zip if it's under 10 MB, otherwise share a folder link from your own Google Drive. Keep a
copy of exactly what was sent in `out/` (or your Drive) as the record of what each client approved.

## 6. Edits and corrections

- **Client edits** (wording, removing a quick hit, a different headline): make the change in that
  client's copy only. If the client wants a change every week (for example, a fixed sentence about
  their own fraud line), put it in their brand file instead.
- **Factual corrections** (a source changes, an address is wrong): fix `issues.json`, rebuild for
  every client, and email them all the same day, even if they've already sent it.

## Onboarding a new client (once, about 30 minutes)

1. Ask for: full name, short name used in copy, member service phone, website, logo (PNG or SVG, at
   least 400 px tall), brand color (hex), accent color, the "we will never ask" sentence their
   compliance team approves, footer lines (address, insurance statement), the unsubscribe merge tag
   from their email platform (for example `*|UNSUB|*` in Mailchimp), their tier, and the send day they want.
2. Copy `brands/example.json` to `clients/<slug>.json` and fill it in. The `logo` field takes a URL
   (their own website's logo image) or a path; leave it empty to use the initials badge.
   `clients/` is gitignored on purpose.
3. Build the 4 sample issues with their branding and send them as their "first month preview".
4. Agree the start date, tier and invoice details. Payment links stay as placeholders
   (`{{PAYMENT_LINK_<TIER>}}`) until you set them up; most credit unions will ask for an invoice.
5. Add them to your delivery list for the next Tuesday.

## Spanish edition (Plus tier)

Translate the finished English issue (AI-assisted is fine), then have a fluent Spanish speaker read it
before delivery; don't ship an unreviewed translation. The Dinero Simple brand's style notes apply.
Put the Spanish text in a second `issues.json` file and build it the same way, with a brand file whose
copy lines are in Spanish.

## What not to do

- Don't send anything to members yourself or log in to a client's email platform or social accounts.
- Don't use a client's name or logo in your own marketing without written permission.
- Don't add tracking pixels, link shorteners or UTM tags to credit union editions.
- Don't promise a client the content meets a regulatory requirement.
