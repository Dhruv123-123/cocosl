# Scam Alert: the weekly newsletter

One scam a week, every Thursday. Each issue follows `TEMPLATE.md`:

1. Two-line intro: why this scam, this week
2. **This week's scam**, with a made-up example message
3. **The tell**: the one rule that gives it away
4. **What to do**: 3 steps (safe move, already clicked, report)
5. **Quick hits**: 3 one-liners
6. **Your 5-minute job this week**
7. **From Scam Decoded**: optional, at most one product or affiliate mention. Affiliate mentions carry the disclosure line. Skip it some weeks.
8. Sign-off + P.S. asking for replies (replies help deliverability)

`python build.py` renders each issue to `public/newsletter/<slug>/email.html` and `email.txt` (absolute links, ready to paste into the email tool), a public archive page per issue, and `public/newsletter/issues.json`. `README.md` and `TEMPLATE.md` aren't published (no `issue:` number).

| # | Send (Thu) | Topic | Ties into |
|---|---|---|---|
| 1 | Feb 4 2027 | IRS "verify your account" texts, arrest calls · IP PIN | Shorts #0, #2 |
| 2 | Feb 11 | Valentine's gift-card asks, flower text, fake soldier · teen sextortion talk | Safer Internet Day, Valentine's Day |
| 3 | Feb 18 | Erroneous refund "send it back", tax relief ads | Shorts #1, #6 |
| 4 | Feb 25 | "Hi Mom" new number, AI voice, 1099-K text · safe word · Protect Your Parents | Shorts #10, #12 |
| 5 | Mar 4 | Slam the Scam Day: government imposters · Family kit | Slam the Scam Day |
| 6 | Mar 11 | Spring break rentals, March Madness picks, utility shutoff · /compare/ (affiliate) | Shorts #16, #15 |

Before sending:

- The email tool adds the unsubscribe link and your postal address (CAN-SPAM). Don't send without them.
- Check the dates: Slam the Scam Day is set by SSA's inspector general each year (confirm at ssa.gov/scam). Safer Internet Day 2027 is assumed to be Tue Feb 9.
- Re-check any number or official URL in the issue against the source that week.
- Every example message is fictional. Keep it that way: never paste a real person's message without permission and redaction.
