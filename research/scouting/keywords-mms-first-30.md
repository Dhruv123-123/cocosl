# Money Made Simple: search phrases for the first 30 videos and pins

Written 2026-11-07. **Docs only.** The sheet is `keywords-mms-first-30.csv` (one row per video, with a blank
`confirmed_in_autocomplete` column). It covers the 30 videos in posting order: the 16 in `content.json`
(launch days 1-14) and the 14 in `content-weeks-3-4.json` (days 15-28, plus two banked shorts). Then it
covers the first 30 Money Made Simple pins from PR #4.

## How the phrases were picked, and the one hand check left

**YouTube and Pinterest autocomplete can't be reached from this environment.** Google's suggest
endpoints return no connection here, and Pinterest's typeahead is an internal API we shouldn't call. So
each **target phrase** is the plain-English way people ask about that topic. It's backed where possible
by public trend data:
- Coventry Direct's Google Trends study, May 2026: "net worth" and "what is a good credit score" are
  among the most-searched money terms and questions by state.
- Rising Trends' Nov 2026 table: BNPL, split pay, credit scoring and IRS Free File are rising year on year.
- Fortune's daily rate table: top high-yield savings rates were up to 4.70% on 4 Nov 2026.
- Pinterest's own topic pages (e.g. "cash stuffing and budgeting ideas").

**Before scheduling, Dhruv (or the MMS thread) confirms each phrase by hand.** It takes about 10 minutes:
1. Type the first two or three words into YouTube's search box (logged out or in a private window) and
   into Pinterest's.
2. If the phrase or a close variant appears in the dropdown, write `yes` in the CSV's last column.
3. If a different wording appears, use that wording in the title instead.

Typing into the search box is normal use. Nothing is automated.

## TL;DR

- **9 of 30 titles already lead with a searched phrase**, 11 are close, and **10 are pure hooks with no
  search phrase** ("The fee that eats $18,000", "That 'surprise' bill was on the calendar"). Hooks are
  fine on TikTok and Reels, where the feed decides. On YouTube, and above all for long videos and pins,
  the title should **start with the phrase and keep the hook after it** (`youtube-seo-playbook.md`: search
  phrase first, 70 characters at most).
- **Easiest wins:** the long video "Feel behind on money? A 30-day reset plan" becomes "How to get your
  finances in order: a 30-day money reset". "The one-fund retirement option" becomes "Target date funds: ...".
  "That 'surprise' bill..." becomes "Sinking funds: ...".
- **The same video can carry two titles.** Keep the hook as the on-screen text and the TikTok/Reels
  caption's first line, and use the search title only on YouTube and Pinterest.
- **Gaps (searched, but no script in the first 30):** "net worth" (one of the top searched money terms in
  the Coventry study), "what is a good credit score" (the carousel on what a score is made of covers
  half of it), "how much house can I afford" (the rent pin covers rent only), "IRS free file" (rising, and
  tax season starts in late January), and "best high yield savings account" with the current rate. Rates
  move after each Fed decision, so a dated "HYSA rates this month" Short is a repeatable search format.
  Suggested scripts for the MMS thread are below.

## The 30 videos

Fit: **match** means the title already contains the phrase; **partial** means it has the topic but not
the words people type; **gap** means a pure hook.

| Day | Format | Current title | Target phrase | Fit | Suggested title |
|---|---|---|---|---|---|
| D1 | short | The two-account trick that stops overdrafts | how to avoid overdraft fees | partial | Stop overdraft fees: the two-account trick |
| D2 | short | Freeze your credit for free tonight | how to freeze your credit | match | keep |
| D2 | long | Feel behind on money? A 30-day reset plan | how to get your finances in order | gap | How to get your finances in order: a 30-day money reset |
| D3 | short | Budget weekly, not monthly | weekly budget | match | keep |
| D4 | short | The raise you're ignoring: your 401(k) match | 401k match explained | partial | 401(k) match explained: the raise you're ignoring |
| D5 | short | Paid in full, score still dropped? | why did my credit score drop | partial | Why did my credit score drop after paying in full? |
| D6 | short | Is your savings app actually insured? | is my money fdic insured | partial | Is your savings app FDIC insured? Check in 1 minute |
| D7 | short | The fee that eats $18,000 | 401k fees / expense ratio explained | gap | The expense ratio that eats $18,000 |
| D8 | short | That 'surprise' bill was on the calendar | sinking funds | gap | Sinking funds: the 'surprise' bill was on the calendar |
| D9 | short | Roth IRA money isn't locked away | can i withdraw from my roth ira | partial | Can you withdraw from a Roth IRA? Your contributions, yes |
| D9 | long | How to start investing with $100 a month (complete beginner walkthrough) | how to start investing with little money | match | keep |
| D10 | short | $60 vs $150 on a $3,000 card | credit card minimum payment | gap | Minimum payment vs $150 on a $3,000 card |
| D11 | short | Set these 3 bank alerts today | bank alerts | partial | 3 bank alerts to turn on today |
| D12 | short | Don't cancel that old card yet | should i close my old credit card | partial | Should you close an old credit card? Not yet |
| D13 | short | The one-fund retirement option | target date fund explained | gap | Target date funds: the one-fund retirement option |
| D14 | short | Find your forgotten subscriptions in 10 minutes | how to cancel subscriptions | partial | How to find and cancel forgotten subscriptions |
| D15 | short | Pay for December in November | holiday budget | gap | Holiday budget: pay for December in November |
| D16 | short | APR vs APY: the sneaky difference | apr vs apy | match | keep |
| D16 | long | High-yield savings accounts, explained properly | high yield savings account explained | match | keep (add 'how they work' in the description) |
| D18 | short | Buy now, pay later: the stacking problem | buy now pay later | match | keep |
| D19 | short | Your savings account pays you 50 cents | savings account interest rate | gap | Your savings account pays 50 cents: switch to high-yield |
| D21 | short | The 72-hour cart rule | how to stop impulse buying | partial | How to stop impulse buying: the 72-hour rule |
| D23 | short | Is a balance transfer worth the 3% fee? | is a balance transfer worth it | match | keep |
| D23 | long | Build your whole budget in one evening (step by step) | how to make a budget | partial | How to make a budget (step by step, in one evening) |
| D24 | short | Why $55k isn't $4,583 a month | 55k a year is how much a month after taxes | partial | $55k a year: how much a month after taxes? |
| D25 | short | Why there's never anything left to save | how to save money when you're broke | gap | How to save money when there's never anything left |
| D27 | short | Why your card charged interest on today's coffee | why was i charged interest on my credit card | gap | Why was I charged interest? Losing your grace period |
| D28 | short | Money market account vs money market fund | money market account vs money market fund | match | keep |
| wk3-4 bank | short | The 50/30/20 budget on $3,200 | 50/30/20 rule | match | keep |
| wk3-4 bank | short | The free student loan rate cut | student loan autopay discount | gap | Student loan autopay discount: the free rate cut |

`c#` is `content.json`, `w#` is `content-weeks-3-4.json`. If the month-1 pack replaces the days 15-28
plan, the same phrases apply to its posts on the same topics.

## The first 30 pins (PR #4's `pins.csv`, rows 1-30)

Pins are pure search, so every pin title should open with the phrase. Most of these already do.

| Pin (rows) | Current title opens with | Target phrase | Change |
|---|---|---|---|
| 1-2 quiz | "What's your money personality?" | money personality quiz | Fine as is |
| 3, 15-16 budgeting apps | "Budgeting apps compared" / "Best budgeting apps" | best budgeting apps | Fine |
| 4, 19-20 HYSA | "How to pick a high-yield savings account" / "Best high-yield savings accounts" | best high yield savings account | Fine. Add the date ("Nov 2026") to the description, not the title, so the pin doesn't go stale |
| 5, 25-26 app comparison | "Rocket Money vs YNAB vs Monarch" | ynab vs monarch | Fine (people type brand vs brand) |
| 6, 11-12 balance transfer | "0% balance transfer" / "Balance transfer cards" | balance transfer explained | Fine |
| 7 | "How to budget on a $50,000 salary" | budget for 50k salary | Fine |
| 8 | "How much rent can you afford?" | how much rent can i afford | Fine. A twin pin for "how much house can I afford" is a gap |
| 9 | "5 money kits in one" | budget printables | **Lead with "Budget printables bundle: ..."**. Nobody searches "money kits" |
| 10 | "12 printable savings challenges" | savings challenge printable | Fine |
| 13-14 | "Bill negotiation services vs doing it yourself" | how to lower your bills | **Lead with "How to lower your bills: ..."** |
| 17-18 | "Best credit-builder cards..." | how to build credit | **Lead with "How to build credit from zero: ..."** |
| 21-22 | "Identity theft protection services" | is identity theft protection worth it | Fine |
| 23-24 | "Best robo-advisors for beginners" | robo advisor for beginners | Fine |
| 27-28 | "The raise you're ignoring: how a 401(k) match works" | 401k match explained | **Swap: "401(k) match explained: the raise you're ignoring"** |
| 29-30 | "Acorns: round-ups..." | acorns review | Fine |

## Five scripts to add (gaps)

| Phrase | Format | Why now |
|---|---|---|
| net worth: how to calculate yours | Short + carousel | A top searched money term (Coventry, May 2026). January is the classic "check your net worth" month, and it pairs with the net-worth dashboard gap in `competitor-product-gaps.md` |
| what is a good credit score | Short | A top searched money question. Add one line on the score ranges to the existing "made of" carousel too |
| best high yield savings rates (this month) | Short, monthly | A dated format that's searched after each Fed decision. Pull the top rate from a public rate table on the day, and drop the illustrative 3.5% APY in older scripts if it's out of date (it's well below the 4.70% top rate on 4 Nov 2026) |
| how much house can i afford | Short + pin | A twin of the rent pin; mortgage-rate questions are the most-searched money question group by state (Coventry) |
| irs free file / how to file taxes for free | Short + long, late Jan | Rising (Rising Trends, Nov 2026). Check irs.gov for the 2027 Free File opening date before scripting |

## Sources

Read 2026-11-07:
[Coventry Direct: most-googled money questions by state](https://www.coventrydirect.com/blog/most-googled-money-questions/) (Google Trends, published 26 May 2026);
[Rising Trends: personal finance trends 2026](https://www.risingtrends.co/trends/personal-finance-trends-2026) (updated 2 Nov 2026; its method isn't published, so treat it as directional);
[Fortune: top high-yield savings rates, 4 Nov 2026](https://fortune.com/article/best-savings-account-rates-11-4-2026/);
[Pinterest topic page: cash stuffing and budgeting](https://www.pinterest.com/cashstuffing/cash-stuffing/);
`youtube-seo-playbook.md`, `pinterest-playbook-2026.md`, `competitor-product-gaps.md` on PR #2.
