# Scam of the week alerts

A short email for when a scam spikes mid-week. The Thursday newsletter is the long read; an alert is the 60-second
version: the message, 3 tells, 3 steps, and what to do if it already happened.

## Make one

    python3 new_alert.py "Fake toll texts are back"      # from sites/scam-decoded/

That copies `_TEMPLATE.md` to the next numbered file here with today's date. Fill in every field (the build stops
and names any field you missed), then run `python3 build.py`. You get:

- `public/alerts/<slug>/email.html` and `email.txt`: paste into the email tool (links are absolute)
- `public/alerts/<slug>/`: a public page with a sign-up form, listed at `/alerts/`
- `public/alerts/alerts.json`: every alert with its subject, preheader, HTML and text

## Draft one from a pasted message

    python3 new_alert.py --text "paste the scam text here"

It guesses the scam type, circles up to 3 giveaways (`flags`), borrows the tells, steps and official source from the
newest alert of the same type, and picks the next free weekday. The file gets `status: draft` (the build skips it) and
a card marked DRAFT goes to `launch/scam-decoded/alert-cards/drafts/`. Check every line against the source, rewrite the
example so it's clearly made up, delete the `status` line, then run `python3 build.py` and `python3 make_alert_cards.py`.

## Cards

`python3 make_alert_cards.py` turns every alert into a 1080x1350 "scam alert of the day" card in
`launch/scam-decoded/alert-cards/`, with captions and the weekday plan in `CARDS.md`. Every alert needs `flags`.
Alerts now run every weekday from Nov 16 2026 to Jan 29 2027 (not Dec 24–25 or Jan 1).

## Fields

- `severity`: `watch` (teal), `warning` (amber) or `urgent` (red). Use urgent only for something hitting lots of people right now.
- `example`: always made up, never a real person's message or number. Use 555-01xx numbers.
- `explainer`: optional slug from `/scams/`. It adds a "How it works" link.
- `source_url`: an official source (FTC, FBI/IC3, IRS, a state AG). Every alert needs one.

The weekly "scam of the week" email (`../weekly/`) reuses these: one alert leads, up to 3 more get a line each.

## Rules

- Send at most one alert a week, and only when there's a real spike. Most weeks the newsletter is enough.
- The email tool adds the unsubscribe link and postal address (CAN-SPAM). Never send without them.
- Nothing here sends anything. Dhruv pastes and sends by hand.

This README and `_TEMPLATE.md` have no `alert_date`, so they aren't published.
