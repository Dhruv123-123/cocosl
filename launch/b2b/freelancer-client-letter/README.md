# Freelancer Money Notes: client newsletter for CPA and bookkeeping firms (white label)

A monthly newsletter that small CPA, tax and bookkeeping firms send to their **self-employed and 1099
clients**, under the firm's own name. Content comes from 1099 Money: the Jan 15 deadline, the new
1099 thresholds, what to bring for a return, quarterly payments and the safe harbor. **$39 / $79 /
$129 a month**, with 2 free months for the first 3 firms.

**Nothing has been sent.** Dhruv sends every email by hand. Payment links are placeholders, and
nothing was bought.

| File | What it is |
|---|---|
| `product.json` | Labels, call to action (firm phone + booking link) and formats: email, social image, printable handout. |
| `issues.json` | 3 sample issues: Jan 5 (Jan 15 payment, fewer 1099s), Feb 2 (what to bring), Mar 2 (2027 quarterly payments and the safe harbor). Delivered to the firm 2 weeks early. |
| `brands/example.json` | A **fictional** firm ("Sample Ledger & Tax Co.", 555 phone, example.com). |
| `brands/placeholders.json` | Every brand slot shown as a token, for the firm's review. |
| `samples/month-1.md` … `month-3.md` | Readable master copy of each issue. |
| `sales-sheet.html` | One-page sales sheet with the 3 plans; `../build.py` writes `out/sales-sheet.pdf`. |
| `PROSPECTS.csv` | 30 firms in Montana (15) and Idaho (15). |

Build from `launch/b2b/`: `python3 build.py freelancer-client-letter` (or `--brand freelancer-client-letter/clients/<slug>.json` for a client).

## Plans

| Plan | Includes | Per month |
|---|---|---|
| Essentials | Client email, social post, sources | $39 |
| Standard | Essentials plus the printable client handout and notes for the firm's team | $79 |
| Plus | Standard plus 2 custom issues a year, and exclusivity in the firm's town | $129 |

## Why the firm reviews every issue

The firm sends this to its own clients, so it carries the firm's professional name. Keep it simple:

- **Education only.** Every issue states rules that apply to everyone, links each one to IRS.gov, and
  sends the client back to the firm for their own situation. No advice on a specific person's return.
- **The firm checks the figures.** The thresholds and safe-harbor percentages in the samples are for
  2026 payments and the 2027 filing season. Check each issue against IRS.gov at delivery, and update
  it whenever the IRS publishes new figures.
- **CPAs have their own advertising rules.** The IRS (Circular 230) and state boards of accountancy
  don't allow false or misleading claims in a firm's marketing. The copy makes no claims about the
  firm, but the firm should read it with that in mind. This isn't legal advice; their own rules apply.
- **No client data.** The firm sends from its own email platform. Its client list never comes to us.

## Prospects (`PROSPECTS.csv`)

30 firms from public directory listings: the Montana CPA lists on cpadirectory.com for Missoula and
Bozeman, the Lantern Boise-area accounting listing, Lantern Twin Falls listings, and the Coeur d'Alene
Chamber member directory. Each row's `listed_in` column links the page. National chains (Jackson
Hewitt, Liberty Tax, H&R Block) and franchise offices were left out, because local owners can't buy.

**Directory listings go stale.** Before writing, open each firm's own website, check it's active and
serves self-employed or small-business clients, and fill in `website` and `contact_route` from that
site. Skip any firm that already sends a client newsletter, and never guess an email address.

## Cold emails

Follow the sending rules in `../credit-union-alert/COLD_EMAILS.md`: 5 to 8 new firms a day, plain
text, no attachment or link in email 1, your name, mailing address and an opt-out line in every
email, and stop at the first "no". **Don't email during tax season's last weeks (mid-March to April
15)**: firms won't read it. The best windows are now through early January, and late April to June.

**Email 1 (day 0)**
Subject: A monthly note for your freelance clients, under your name

> Hi {First name},
>
> {Personal line: one true sentence from their site, e.g. they work with contractors or small businesses.}
>
> I write a monthly newsletter that accounting firms send to their self-employed clients under their
> own name: the Jan 15 payment, what's changed with 1099s, what to bring in February, setting up
> quarterly payments. Each issue comes 2 weeks early for you to review, with your logo, phone number
> and booking link already on it.
>
> Would a free 3-month sample be useful? It's made for a fictional firm, so you can see exactly what
> your clients would get.
>
> {Your name}
> {Your mailing address} · Reply "no thanks" and I won't write again.

**Follow-up 1 (day 4, same thread):** "Hi {First name}, just checking this reached you. Happy to send
the sample if it's useful, or I'll leave it there." Sign it with the same two lines as email 1
(`{Your name}`, then `{Your mailing address} · Reply "no thanks" and I won't write again.`).

**Follow-up 2 (day 10): give something useful.** Paste the January issue's "Do it this month" steps
as plain text and say: "Feel free to send that to your clients as it is. If you'd like one like it every
month with your branding, the first 3 firms get 2 months free." Sign it with the same two lines
as email 1. Then stop.

**When they reply "yes" or "send it":** send `out/sample-ledger.zip` and `out/sales-sheet.pdf`. When
they want to go ahead, use `../credit-union-alert/onboarding/` and change the product name. The
intake asks for the firm phone, booking link and client portal name instead of the credit union fields.
