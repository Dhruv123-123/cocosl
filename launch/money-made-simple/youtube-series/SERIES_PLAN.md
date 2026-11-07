# Money Made Simple: YouTube long-form series

Twelve 8–12 minute videos built for search, one per week. Every script is complete: narration split into chapters, on-screen text, an illustration prompt per chapter, title plus two A/B variants, hook plus two variants, thumbnail text, a YouTube description with chapters and UTM-tagged links, sources and the claims a human must check.

Content: `content.json` (format `long`, `series: youtube-long-form`). It runs through the normal pack export:

```
factory pack export --brand money-made-simple --file launch/money-made-simple/youtube-series/content.json \
  --start 2027-03-21 --days 84 --out out/youtube-series
```

That fills the Sunday long-form slot for months 5–7 (Sun Mar 21 – Sun Jun 6, 2027). These are evergreen and search-led, so they also work earlier as a second weekly upload (e.g. Wednesdays) if you want them indexing sooner; that goes over the brand's `long_per_week: 1`, so raise it first.

| # | Date | Title | Searches it targets | Length* | Thumbnail |
|---|---|---|---|---|---|
| 1 | Sun Mar 21 | How to Make a Budget That Actually Works (Step by Step for Beginners) | how to make a budget, budgeting for beginners, how to budget money | ~10.7 min (1607 words) | 4 numbers. That's the budget. / Budget in 20 minutes |
| 2 | Sun Mar 28 | Debt Snowball vs Avalanche: We Ran the Real Numbers | debt snowball vs avalanche, debt avalanche method, debt snowball method | ~8.5 min (1274 words) | Snowball vs Avalanche: real math / $327 difference |
| 3 | Sun Apr 4 | How to Build an Emergency Fund (Even on a Tight Budget) | how to build an emergency fund, how much emergency fund, emergency fund | ~8.6 min (1289 words) | $1,000 first. Then this. / Emergency fund math |
| 4 | Sun Apr 11 | How Credit Scores Actually Work (and How to Raise Yours) | how credit scores work, how to raise credit score, how to build credit | ~8.5 min (1268 words) | 65% of your score is this / Credit score, explained |
| 5 | Sun Apr 18 | How to Start Investing With $100 a Month (Beginner's Guide) | how to start investing, investing for beginners, how to invest 100 dollars | ~8.5 min (1280 words) | $100/month → $122k? / Start investing with $100 |
| 6 | Sun Apr 25 | Roth vs Traditional IRA: Which One Should You Pick? | roth vs traditional ira, roth ira explained, traditional ira | ~8.7 min (1299 words) | Roth or Traditional? 1 question / Tax now or later? |
| 7 | Sun May 2 | 401(k) Match Explained: Don't Leave Free Money on the Table | 401k match explained, how does 401k match work, 401k for beginners | ~8.4 min (1255 words) | Free money: $1,500/year / 401(k) match, decoded |
| 8 | Sun May 9 | High-Yield Savings Accounts Explained: Are They Safe and Worth It? | high yield savings account, what is a high yield savings account, are high yield savings accounts safe | ~8.7 min (1302 words) | Your savings could earn 8x / Is it safe? |
| 9 | Sun May 16 | Budgeting App vs Spreadsheet: Which One Should You Use? | best budgeting app, budgeting app vs spreadsheet, how to track spending | ~8.8 min (1320 words) | App or spreadsheet? / 3 questions decide it |
| 10 | Sun May 23 | How to Pay Off Credit Card Debt Fast: The Minimum Payment Trap | how to pay off credit card debt, pay off credit card debt fast, minimum payment | ~8.4 min (1256 words) | 19 years vs 3 years / The minimum payment trap |
| 11 | Sun May 30 | Sinking Funds Explained: Stop 'Surprise' Expenses Wrecking Budgets | sinking funds, sinking funds explained, irregular expenses budget | ~8.4 min (1259 words) | 'Surprise' bills = $250/month / Sinking funds, explained |
| 12 | Sun Jun 6 | How to Freeze Your Credit (Free, 15 Minutes, All 3 Bureaus) | how to freeze your credit, credit freeze, freeze credit equifax experian transunion | ~8.4 min (1255 words) | Free. 15 minutes. Do it. / Freeze your credit |

*At about 150 words a minute. Real voiceover runs a little longer with pauses and B-roll.

## Before each upload

- **Chapters**: timestamps are estimated from word counts. After the voiceover is cut, update them to the real times (YouTube needs the first at 0:00, at least 3, each 10s or longer).
- **Links**: every own-site link carries `utm_source=youtube&utm_medium=social&utm_campaign=yt-series-NN` (docs/UTM.md, campaign = content id). The description links no affiliate URLs directly; videos that link to Compare pages include the commission note. The blog, Compare and /budget/ pages come from the site PR, so check each link resolves on the live site before publishing.
- **Facts**: work through `claims_to_verify` for each video. Contribution limits, income limits and rates are deliberately not stated as numbers in the scripts; the scripts point people to IRS.gov or say "check current pricing".
- **Examples**: every person and number in the examples is fictional or hypothetical, and the scripts say so. Investment videos (5, 6, 7) carry the risk line.
- **Disclosure**: keep the AI line in the description and turn on YouTube's altered/synthetic content toggle where it applies.

## Playlist and end screens

Put the series in one playlist, "Money basics, step by step", in this order: 1 budget → 11 sinking funds → 3 emergency fund → 8 high-yield savings → 10 credit card debt → 2 snowball vs avalanche → 4 credit scores → 12 credit freeze → 7 401(k) match → 6 Roth vs traditional → 5 investing with $100 → 9 app vs spreadsheet. Each video's end screen points to the next one in that order.

## Shorts that feed the series

Each long video has 2–3 chapters that work as a Short on their own (e.g. 2 "Side by side", 10 "The minimum payment trap", 12 "What a freeze does"). Cut them with the related-video link set to the full video.
