# Search-gap scripts: five topics people search that the launch set didn't cover

These come from scouting's keyword sheet (`research/scouting/keywords-mms-first-30.md`, PR #2). There are 5 Shorts, each with a 55–90 s TikTok cut, and 2 carousels. Every title leads with the search phrase.

| Posts (ET) | Piece | Search phrase |
|---|---|---|
| Wed Jan 6, 2027 | Net worth: how to calculate yours in 4 lines (Short) | net worth: how to calculate yours |
| Sun Jan 10 | How to calculate your net worth (worksheet) (carousel and pin) | net worth worksheet |
| Wed Jan 13 | What is a good credit score? The 5 FICO ranges (Short) | what is a good credit score |
| Sun Jan 17 | How much house can I afford? A 5-step check (carousel and pin, the rent pin's twin) | how much house can i afford |
| Wed Jan 20 | Best high-yield savings rates: how to check this month's (Short) | best high yield savings rates |
| Wed Jan 27 | IRS Free File: 3 ways to file your taxes for free (Short) | irs free file / how to file taxes for free |
| Wed Feb 3 | How much house can I afford? The 28/36 math (Short) | how much house can i afford |

**Why these dates:** they're the open Wednesday Short slots and the open Sunday carousel slots in months 2–3, so no platform goes over 2 posts a day. A combined check of all 22 MMS packs finds no platform with two posts at the same minute. January is the "check your net worth" month, and IRS Free File usually opens in January.

**Before posting:**

- Three scripts carry **DATED** lines in CHECK BEFORE POSTING:
  - **HYSA rates:** look up the FDIC national rate and the top APYs on the day.
  - **IRS Free File:** confirm the 2027 opening date and income limit on IRS.gov. The limit is reported as $89,000 for the 2026 season, and the script doesn't quote a number.
  - **Credit score ranges:** these are FICO's. Other models use different cut-offs.
- Re-shoot the HYSA Short every month or two with that month's numbers. It's a repeatable search format.
- Then confirm each phrase in the YouTube and Pinterest search boxes, as the keyword sheet describes.

Export:

```
factory pack export --brand money-made-simple --file launch/money-made-simple/search-gaps/content.json \
  --start 2027-01-06 --days 32 --short-days wed --carousel-days sun --out search-gaps/
```
