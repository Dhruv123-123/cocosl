# Broker partner kit: Money Made Simple at Work

Benefits brokers and consultants already advise the employers we want to reach. One broker who uses
this can open 10 or 20 employer clients. This kit is everything needed to pitch and sign one.
**Nothing here has been sent, and every fee and contact detail is a placeholder.**

| File | Use it |
|---|---|
| `broker-one-pager.html` → `../out/broker/broker-one-pager.pdf` | The one-pager to attach when a broker replies. |
| `../brands/broker-cobrand.json` → `../out/sample-outfitters-broker-cobrand.zip` | The co-branded sample: the fictional employer's 4 issues with a credit line for a fictional broker, "Sample Benefits Group". This is what a broker's client would actually receive. |
| `../out/demo-packet.pdf` | The employer demo packet (sales sheet and 3 issues), if they want the plain version too. |
| `../COLD_EMAILS.md` → "Email 1: benefits broker" | First contact. |

## Decide before quoting (placeholders in the one-pager)

| Placeholder | What to decide | A starting point (proposal only) |
|---|---|---|
| `{{REFERRAL_FEE}}` | What a broker earns for each referred employer | 20% of the client's first-year fees |
| `{{REFERRAL_PAYMENT_TERMS}}` | When you pay it | quarterly, after the client has paid |
| `{{REFERRED_CLIENT_DISCOUNT}}` | What the referred employer saves | 2 months free, as in the founding pilot |
| `{{BROKER_WHOLESALE_RATE}}` | Per-client monthly rate billed to the broker (5+ clients) | $39 a client a month |

These match the proposals already in `../COLD_EMAILS.md` (20% off, or $39 a client for 5+). **They're
proposals: pick your numbers, then fill them in and rebuild** (`python3 build.py employer-wellness`).
Spend nothing to set up payouts until a broker signs.

## Making a broker's co-branded pack

1. Copy `../brands/broker-cobrand.json` to `../clients/<employer>-<broker>.json`.
2. Fill in the employer's details as for any client, then set `credit_line` to the broker's wording,
   for example: "Provided to [Employer] employees by [Broker], your benefits advisor · [phone]".
3. Build: `python3 build.py employer-wellness --brand employer-wellness/clients/<file>.json`. The
   credit line prints on the email, the intranet image, the breakroom slide and the flyer.
4. For the "include it in your service" model with many clients, make one brand file per employer and
   keep the same `credit_line`.

## Things the broker's compliance team will ask (answer plainly)

- **Is it advice?** No. It's general education. It never recommends a plan, fund, carrier or amount, and
  plan details come only from the employer's own wording (ERISA notes in `../COMPLIANCE_NOTE.md`).
- **Is it a gift or inducement?** That's for them to decide. State insurance laws differ on the
  value-added services a licensed producer may give clients. Many states now allow services related to
  the insurance, with limits. Offer both models (refer, or include it) and let them choose. Don't
  give an opinion on their state's rules.
- **Do you see employee data?** No. The employer sends it from its own systems.
- **Referral fees:** if they take one, they may need to disclose it to the employer. Put it in writing,
  in your agreement with them.

## Pitch order

1. The 2 brokers in `../PROSPECTS.csv` (Leavitt Great West, Leavitt Select) first.
2. Then brokers named on local SHRM chapter sponsor pages, which are public. Take their contact from
   the broker's own website, never a guessed address.
3. After the first reply, send the one-pager and the co-branded zip. Offer a 15-minute call, and go
   through the "Decide before quoting" table before it.
