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
| 1 | Nov 19 2026 | Holiday deliveries: "package on hold" texts, marketplace payment emails, Black Friday shops · /checker/ | Holiday pack #0, #2, #3 |
| 2 | Dec 3 2026 | Year-end giving: fake charity texts, boss gift card texts, tampered gift cards · /checker/ | Holiday pack #4–#8 |
| 3 | Dec 10 2026 | Fake shops in social ads, shipping-confirm emails, discounted gift cards | Holiday pack |
| 4 | Dec 17 | Home for the holidays: canceled-flight texts, the scam talk · /holiday/ guide + /seniors/ ($7) | Holiday guide |
| 5 | Dec 24 | Short holiday edition: gift card balance texts, new phones for parents | Christmas Eve |
| 6 | Dec 31 | New Year 15-minute reset, fake auto-renewal emails · Family kit | New Year's |
| 7 | Jan 7 2027 | Fake return/refund emails, new device setup | Returns season |
| 8 | Jan 14 | Task and recruiter job scams for January job hunters | Job hunting season |
| 9 | Jan 21 | Wrong-number texts that become crypto 'investments' | FTC social media data |
| 10 | Jan 28 | Data Privacy Day: fake breach settlements, 3 locks | Data Privacy Day |
| 11 | Feb 4 2027 | IRS "verify your account" texts, arrest calls · IP PIN | Shorts #0, #2 |
| 12 | Feb 11 | Valentine's gift-card asks, flower text, fake soldier · teen sextortion talk | Safer Internet Day, Valentine's Day |
| 13 | Feb 18 | Erroneous refund "send it back", tax relief ads | Shorts #1, #6 |
| 14 | Feb 25 | "Hi Mom" new number, AI voice, 1099-K text · safe word · Protect Your Parents | Shorts #10, #12 |
| 15 | Mar 4 | Slam the Scam Day: government imposters · Family kit | Slam the Scam Day |
| 16 | Mar 11 | Spring break rentals, March Madness picks, utility shutoff · /compare/ (affiliate) | Shorts #16, #15 |

Issues 5 (Christmas Eve) and 6 (New Year's Eve) land on holidays: send them in the morning, or skip and renumber.

Before sending:

- The email tool adds the unsubscribe link and your postal address (CAN-SPAM). Don't send without them.
- Check the dates: Slam the Scam Day is set by SSA's inspector general each year (confirm at ssa.gov/scam). Safer Internet Day 2027 is assumed to be Tue Feb 9.
- Re-check any number or official URL in the issue against the source that week.
- Every example message is fictional. Keep it that way: never paste a real person's message without permission and redaction.
