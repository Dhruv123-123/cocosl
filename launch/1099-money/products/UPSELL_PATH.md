# 1099 Money product ladder and upsell path

| Step | Product | Price | Where people meet it |
|---|---|---|---|
| Free | 2027 Freelancer Tax Calendar + quarterly tax calculator | $0 | `apps/freelance-tax/` (`free/`, calculator), link in bio, Shorts |
| 1 | The Quarterly Tax Tracker | $15 | Email sequence (emails 4–7), thank-you page, tax videos |
| 2 | The Rate & Contract Kit | $29 | Rate / invoicing / contract content, tracker buyers' email 3, thank-you page |
| 3 | The Freelancer Money Bundle (both + Client Email Scripts) | $49 | Checkout upsell, buyers' emails, thank-you page |

## Codes to create in the store before selling

| Code | Product | Effect | Who gets it |
|---|---|---|---|
| `LAUNCH` | each product | $6 / $10 / $10 off, first 7 days only | Public launch posts |
| `TRACKER15` | Bundle | $15 off ($34) | Tracker buyers (buyers' email 3, tracker guide p. 10 if you add it) |
| `KIT29` | Bundle | $29 off ($20) | Kit buyers (kit purchase email) |
| `TRACKER5` | Kit | $5 off ($24) | Tracker buyers who don't want the bundle |

These upgrade codes make the bundle cost the difference, so nobody pays twice.
Keep them out of public posts.

## Checkout upsells (Gumroad: Checkout > Upsells; Lemon Squeezy: checkout add-on)

- **On the tracker's checkout:** offer "Upgrade to the Freelancer Money Bundle for $34 more" (the bundle with `TRACKER15`).
- **On the kit's checkout:** offer "Upgrade to the Freelancer Money Bundle for $20 more" (the bundle with `KIT29`).
- One upsell per checkout. No pre-ticked boxes, no countdown timers.

## After purchase

- Tracker buyers get the 3-email buyers' sequence in `apps/freelance-tax/emails/buyers/`
  (welcome + setup on day 0, the first-payment walkthrough on day 3, the bundle upgrade on day 7).
- The thank-you page `apps/freelance-tax/free/thanks/` shows each product whose URL in `config.js` is filled in.

## Rules

- Value claims add up exactly ($15 + $29 = $44; the bundle is $49 because of the bonus scripts). No "worth $99".
- 14-day refunds on everything, said the same way everywhere.
- No testimonials until real buyers give them, quoted with permission.
