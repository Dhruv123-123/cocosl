# 1099 Money: 6-week YouTube long-form plan (Jun 6 – Jul 11, 2027)

Six long videos for the Sunday slot after month 6, one a week. Scripts are in `content.json`, in the same
format as the monthly packs. Every video has:

- **An original element** (`original_element`): a chart from the video's own numbers, your own screen recording,
  or you on camera. The chapter it belongs to is named, so you know where to put it.
- **A real chart** on one beat (`segments[].chart`), drawn by the factory with the exact numbers, so the pack's
  original-element check passes even before you add footage.
- **A 20-second end slate**: the last beat (`End slate`), about 51 words of narration (≈ 20 s at 160 wpm),
  with the mascot on the left third and the right two thirds empty for YouTube end-screen cards.
  `end_slate` lists the cards: next week's video, the subscribe button and the series playlist.
  YouTube end screens can be 5–20 seconds long and sit in the last 20 seconds, so set them to the full 20.
- 8+ minutes (≈ 8:05–8:20 at 160 wpm), so mid-roll ads are allowed. Chapters are in each description.

| Date | Title | Format | Length | Original element | Chart | End slate points to |
|---|---|---|---|---|---|---|
| Sun Jun 6 | SEP IRA or Solo 401(k)? Freelance retirement accounts with real numbers | comparison | 8:18 | worked-example-chart: Bar chart of the maximum SEP IRA and Solo 401(k) contributions at $60,000 and $120,000 of profit, computed in the video from 2026 limits | "Max contribution, 2026" (Comparison chart) | How much of every freelance payment to set aside for taxes |
| Sun Jun 13 | How much of every freelance payment to set aside for taxes | real-numbers | 8:19 | worked-example-chart: Bar chart of the federal set-aside percentage at $30K, $60K, $90K and $120K of profit, computed with the free calculator's 2026 method | "Federal set-aside, 2026" (Rate chart) | S corp or not? Three freelancers run the numbers |
| Sun Jun 20 | S corp or not? Three freelancers run the numbers | on-screen-calculation | 8:05 | screen-recording: Your own 40-second screen recording of the free S corp calculator: type Jordan's $100,000 profit and $60,000 salary, then drag the salary to $50,000 and back | "$100K profit, $60K salary" (Jordan's chart) | A 30-minute monthly bookkeeping routine for freelancers |
| Sun Jun 27 | A 30-minute monthly bookkeeping routine for freelancers | walkthrough | 8:05 | screen-recording: Your own 60-second screen recording of the monthly spreadsheet with made-up transactions: categorize three rows, then show the summary tab totals | "The 30-minute routine" (Where the time goes) | Irregular income: how to pay yourself a steady freelance salary |
| Sun Jul 4 | Irregular income: how to pay yourself a steady freelance salary | explainer | 8:07 | human-segment: You on camera for about a minute walking through your own three accounts (balances blurred): the salary day, how you picked the amount, what you'd change | "Buffer at month end" (Buffer chart) | Freelance records: what to keep, for how long, and 5 myths |
| Sun Jul 11 | Freelance records: what to keep, for how long, and 5 myths | myth-vs-fact | 8:06 | human-segment: You on camera for about 45 seconds with your own receipts folder or app (no personal details): where a receipt goes, how you note the purpose, where the backup lives | "How long to keep records" (Retention chart) | SEP IRA or Solo 401(k)? Freelance retirement accounts with real numbers |

## Before you record

1. Check every line in `claims_to_verify` against the linked sources (2026 limits and IRS pages).
2. Weeks 3 and 4: record the screen recording named in `original_element` and set it as `footage` on that beat.
   Weeks 5 and 6: film the short on-camera segment. The chart beats already work without you.
3. Re-render the pack: `factory pack export --brand 1099-money --file launch/1099-money/youtube-6wk/content.json --start 2027-06-06 --days 36 --out <folder>`.
4. In YouTube Studio, add the end-screen cards listed in `end_slate` to the last 20 seconds, and make a playlist
   called "Freelance money, start here" with all six.

Nothing here is posted automatically. Upload by hand.

Week 3 uses the free S corp calculator (`apps/freelance-tax/s-corp-calculator/`), and its three cases are the
calculator's own output: $60K → about −$400, $100K → about $76, $150K → about $848 a year.
