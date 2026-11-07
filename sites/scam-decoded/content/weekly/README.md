# Weekly "scam of the week" email

A short weekly email built from the alerts in `../alerts/`. You don't write the scam twice: pick this week's alert as the
lead (shown in full: the message, 3 tells, 3 steps, what to do if it already happened, the source) and up to three older
alerts for "Also going around" (one line each, linking to their alert page). Add an optional quiz question and a line
of your own.

The Thursday newsletter (`../newsletter/`) stays the long read. Use this one on weeks when there's no time for a full
issue, or as a short Monday email next to it. Don't send both on the same day.

## Make one

    python3 new_weekly.py                       # from sites/scam-decoded/
    python3 new_weekly.py --date 2027-01-18 --lead unpaid-toll-texts

`new_weekly.py` copies `_TEMPLATE.md` to the next numbered file here. By default it leads with the newest alert no
weekly email has used yet, fills "also" with the next newest ones, picks a quiz question nobody has used, and fills
the subject and preheader from the alert. You write the `intro` line. Then run `python3 build.py`. You get:

- `public/weekly/<slug>/email.html` and `email.txt`: paste into the email tool (links are absolute)
- `public/weekly/weekly.json`: every weekly email with its subject, preheader, HTML and text

There are no public pages for these: each alert already has its own page at `/alerts/<slug>/`.

## Fields

- `lead`: one alert's slug (its file name without the number, e.g. `unpaid-toll-texts`). Required.
- `also`: up to 3 other alert slugs, comma-separated. Optional.
- `quiz`: a question number (1–12) from `content/quiz.json`. The email shows the message and links to `/quiz/` for the answer. Optional.
- Anything under the front matter is added after the quiz as extra Markdown, e.g. a reply from a reader (with their permission).

The build stops and names the field if anything still has `[template text]`, or if a slug doesn't match an alert.

## Rules

- The email tool adds the unsubscribe link and postal address (CAN-SPAM). Never send without them.
- Nothing here sends anything. Dhruv pastes and sends by hand.
