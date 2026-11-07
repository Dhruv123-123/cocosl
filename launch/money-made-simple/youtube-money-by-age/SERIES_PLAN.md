# Money Moves by Age: YouTube series (5 parts)

A five-part long-form series that goes decade by decade, from your 20s to your 60s. Each part follows one fictional person or couple, uses a different format, and draws its own chart from that person's numbers. It follows straight on from Your First $1,000 Invested, which ends Oct 10, 2027. No titles repeat any other pack.

- **All 5 parts are written**, in `content.json`, at about 8 minutes each. Each has chapters, UTM-tagged links (`utm_campaign=yt-age-NN`), the AI line ("Script drafted with AI help and fact-checked by a person."), and the investing risk line in the description.
- **No specific securities, funds, tickers or providers** are named or shown anywhere. Target-date funds, 529 plans, HSAs and term life are named only as categories.
- **Original element per video:** every part has a worked-example chart on its chart chapter, with the chart note saying the numbers are fictional or hypothetical.
- **Yearly limits aren't quoted on screen.** Catch-up, IRA, HSA and earnings-test limits change most years, so the narration sends viewers to IRS.gov and SSA.gov. The Social Security percentages (70% at 62, 124% at 70 for a full retirement age of 67) and the RMD age of 75 for people born in 1960 or later are rules, not yearly figures, but check them in the month of posting.
- **Schedule:** Sundays at 19:00 ET, **Oct 17 – Nov 14, 2027**, on YouTube (19:00) with a Pinterest pin at 11:30.
- **Examples** (Maya, Priya and Dev, Chris, Denise, Ray) are fictional and labelled. There are no income promises or testimonials.

| # | Sunday | Title | Format | Original element | Status |
|---|---|---|---|---|---|
| 1 | Sun Oct 17, 2027 | **Money in Your 20s: 5 Moves That Matter Most** | countdown | worked-example-chart: Bar chart of $200 a month at a hypothetical 7%: about $525,000 if started at 25 vs about $244,000 if started at 35, both to 65 (chapter "The chart: 25 vs 35") | Written: 1,296 words, about 8 min |
| 2 | Sun Oct 24, 2027 | **Money in Your 30s: Kids, a House, and Retirement on Track** | real-numbers | worked-example-chart: Bar chart of the fictional Priya and Dev's $8,000 monthly plan: housing $2,400, childcare $1,400, other bills $1,200, savings goals $800, spending $2,200 (chapter "The chart: their monthly plan") | Written: 1,264 words, about 8 min |
| 3 | Sun Oct 31, 2027 | **Money in Your 40s: Are You on Track? Do the Math** | on-screen-calculation | worked-example-chart: Line chart of the fictional Chris's retirement savings from 44 to 67 at a hypothetical 6% with $12,000 a year added: $120,000 at 44, about $254,000 at 50, $407,000 at 55, $613,000 at 60 and $1.02M at 67 (chapter "The chart: 44 to 67") | Written: 1,242 words, about 8 min |
| 4 | Sun Nov 7, 2027 | **Money in Your 50s: Catch-Up Contributions and the Last Stretch** | walkthrough | worked-example-chart: Bar chart of new contributions for the fictional Denise from 53 to 67 at a hypothetical 6%: $12,000 a year grows to about $252,000 vs $18,000 a year to about $378,000 (chapter "The chart: $12k vs $18k") | Written: 1,272 words, about 8 min |
| 5 | Sun Nov 14, 2027 | **Money in Your 60s: When to Claim Social Security, Explained** | explainer | worked-example-chart: Bar chart of the fictional Ray's monthly Social Security benefit by claiming age: about $1,400 at 62, $2,000 at 67 (full retirement age) and $2,480 at 70 (chapter "The chart: 62, 67 or 70") | Written: 1,239 words, about 8 min |

## Export

```
FACTORY_DB=/tmp/age.db factory pack export --brand money-made-simple --file launch/money-made-simple/youtube-money-by-age/content.json --start 2027-10-17 --days 29 --long-days sun --out out/money-by-age
```
