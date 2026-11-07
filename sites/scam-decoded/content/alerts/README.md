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

## Fields

- `severity`: `watch` (teal), `warning` (amber) or `urgent` (red). Use urgent only for something hitting lots of people right now.
- `example`: always made up, never a real person's message or number. Use 555-01xx numbers.
- `explainer`: optional slug from `/scams/`. It adds a "How it works" link.
- `source_url`: an official source (FTC, FBI/IC3, IRS, a state AG). Every alert needs one.

## Rules

- Send at most one alert a week, and only when there's a real spike. Most weeks the newsletter is enough.
- The email tool adds the unsubscribe link and postal address (CAN-SPAM). Never send without them.
- Nothing here sends anything. Dhruv pastes and sends by hand.

This README and `_TEMPLATE.md` have no `alert_date`, so they aren't published.
