# 1099 Money: tax season push (Sun Jan 3 – Sun Apr 11, 2027)

15 Shorts, one every Sunday, in three series. Sundays in Jan–Apr 2027 carry only the YouTube long video, so these
**add** a Short without bumping anything and stay under the 2-posts-a-day cap.

1. **Jan 15 reminders (2):** first-time estimated payers, and the file-by-Feb-1 alternative. The Tax Jar Challenge
   already covers Direct Pay (Jan 4) and payment day (Jan 15), so these don't repeat them.
2. **1099 season (4):** the $2,000 1099-NEC threshold for 2026 payments, 1099-K back to $20,000 and 200 payments,
   the same payment on a 1099-K and a 1099-NEC, and income that never gets a form.
3. **Deduction Hunt (9):** one commonly missed deduction a week until Apr 15, each priced with the site's tax model
   for one fictional freelancer (single, $60,000 profit, 2026 federal figures). The finale adds them up: about $2,080.

| Post on | Series | Title | Style |
|---|---|---|---|
| Sun Jan 3 | Jan 15 reminder 1/2 | Never paid estimated tax? What to do before Jan 15 | question-reply |
| Sun Jan 10 | Jan 15 reminder 2/2 | The little-known way to skip the Jan 15 payment | explainer |
| Sun Jan 17 | 1099 season 1/4 | No 1099 this year? The income still counts | myth-vs-fact |
| Sun Jan 24 | 1099 season 2/4 | 1099-K is back to $20,000 and 200 payments | explainer |
| Sun Jan 31 | 1099 season 3/4 | Got the same payment on two 1099s? Count it once | how-to |
| Sun Feb 7 | 1099 season 4/4 | 3 kinds of freelance income that never get a 1099 | countdown |
| Sun Feb 14 | Deduction Hunt 1/9 | The Deduction Hunt: one category a week until April 15 | challenge-day-1 |
| Sun Feb 21 | Deduction Hunt 2/9 | Your 2026 miles get two rates: 72.5¢, then 76¢ | real-numbers |
| Sun Feb 28 | Deduction Hunt 3/9 | Hunt week 3: the subscriptions hiding on your card | how-to |
| Sun Mar 7 | Deduction Hunt 4/9 | Hunt week 4: your phone bill's business share, worked out | on-screen-calculation |
| Sun Mar 14 | Deduction Hunt 5/9 | Hunt week 5: does your kitchen table count? | question-reply |
| Sun Mar 21 | Deduction Hunt 6/9 | Hunt week 6: the fees your 1099-K doesn't subtract | explainer |
| Sun Mar 28 | Deduction Hunt 7/9 | Hunt week 7: health insurance you paid for yourself | myth-vs-fact |
| Sun Apr 4 | Deduction Hunt 8/9 | Hunt week 8: an IRA for 2026, until April 15 | deadline-alert |
| Sun Apr 11 | Deduction Hunt 9/9 | Deduction Hunt results: about $2,080 less tax, worked out | real-numbers |

## Render

```
FACTORY_LLM=offline FACTORY_TTS=silent FACTORY_IMAGES=cards factory pack export --brand 1099-money \
  --file launch/1099-money/tax-season-push/content.json --start 2027-01-03 --days 99 --short-days sun --out <dir>
```

0 blocks; warnings are the usual "a human fact-checks these claims" notes.

## Before posting

- Mileage uses both 2026 rates: 72.5¢ to Jun 30 (Notice 2026-10), 76¢ from Jul 1 (Announcement 2026-11).
- Pin Deduction Hunt 1/9 (Feb 14) for the run of the challenge, like the Tax Jar Challenge.
- Recheck the 2026 IRA limit ($7,500, $8,600 at 50+) and the Feb 1 filing exception in Pub 505 (2027 edition).
