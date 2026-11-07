# Money Made Simple: the first 14 days

Everything for the first 14 days on one page: every post, the bio for each platform, what to pin, and the first Pinterest pins. All times are America/New_York.

- **Content:** `content.json`, 24 scripts. `#n` below is its position in the file, counting from 0.
- **Fact-check:** done (`FACTCHECK_FIRST_14_DAYS.md`). Two fixes went in. The three "check on the day" lines are listed there.
- **Dated packs:** month 1, the holiday add-on, the savings challenge and Myth vs Math are tied to real dates (Black Friday, December). They start on their own dates whatever Day 1 is, and the table below merges them in.
- **Recording:** `RECORD_FIRST_14_DAYS.md` is the one 30-minute sheet of what these 14 days need from Dhruv.

## Before the first post

1. **Bios.** Paste the bios below into each platform. Set the link-in-bio page first; it needs the free 7-Day Money Reset, The 20-Minute Budget ($12, our own product) and the HYSA comparison page.
2. **Captions.** Each caption gets the AI disclosure from the brand file: "Visuals and voice made with AI tools. Script drafted with AI help and fact-checked by a person. Not financial advice." Turn on the platform's AI label where it applies (TikTok, YouTube "altered or synthetic", Instagram/Facebook "AI info").
3. **Product and affiliate posts.** Product posts say "It's our own product". Affiliate posts carry the affiliate line. Don't add UTM tags to affiliate links.
4. **Human review.** Every post gets a human review in the dashboard, and someone ticks CHECK BEFORE POSTING.
5. **Dates.** `scripts/launch_week.py` also writes each launch piece's day into `content.json` (`"date"`), so `factory import launch/money-made-simple/content.json` then approving keeps the days in the table, whatever order you approve in. The swap-ins have no date. If Day 1 changes, rerun the script and then `factory import` again, which updates the dates on posts that are already imported.

## The 14 days

**Day 1 is a setting, and it's Dhruv's call.** No accounts exist yet, so nothing goes out until the accounts are set up and Day 1 is picked. The default is **Mon Nov 16, 2026**, the Monday after the Nov 14 recording session. To change it, run `python scripts/launch_week.py --day1 YYYY-MM-DD`. That rewrites the table below with real dates, per-platform times and the hand-off to the dated packs. It refuses a calendar where any platform has two posts at the same minute or more than 2 in a day. A test keeps this table in sync with the default.

Shorts go to YouTube Shorts, Instagram Reels and Facebook Reels at 12:30, and to TikTok at 18:00. Carousels go to Instagram at 19:00 and Pinterest at 11:00. Long videos go to YouTube at 19:00, with the Pinterest pin at 11:30. TikTok-only challenge videos go at 19:00. Titles lead with the phrase people search for. On TikTok and Reels, the old hook (`title_variants[0]`) can open the caption instead.

<!-- launch-week:start -->

**Day 1 = Mon Nov 16, 2026** (Dhruv's call; change it with `python scripts/launch_week.py --day1 YYYY-MM-DD`, which rewrites this section). Window: Mon Nov 16 – Sun Nov 29. All times America/New_York.

The launch set runs Days 1–4. From Fri Nov 20 the dated packs take over (the holiday add-on's Black Friday kickoff, then month 1 from Nov 21, the savings challenge and Myth vs Math), because they're tied to Black Friday and December.

| Day | Date | Time | Platform(s) | From | Format | Piece |
|---|---|---|---|---|---|---|
| 1 | Mon Nov 16 | 11:00 | pinterest | launch #14 | carousel | The 20-minute monthly money date |
| 1 | Mon Nov 16 | 12:30 | instagram, youtube, facebook | launch #0 | short | Stop overdraft fees: the two-account trick |
| 1 | Mon Nov 16 | 18:00 | tiktok | launch #0 | short | Stop overdraft fees: the two-account trick |
| 1 | Mon Nov 16 | 19:00 | instagram | launch #14 | carousel | The 20-minute monthly money date |
| 2 | Tue Nov 17 | 11:30 | pinterest | launch #23 | long | How to get your finances in order: a 30-day money reset |
| 2 | Tue Nov 17 | 12:30 | instagram, youtube, facebook | launch #6 | short | Freeze your credit for free tonight |
| 2 | Tue Nov 17 | 18:00 | tiktok | launch #6 | short | Freeze your credit for free tonight |
| 2 | Tue Nov 17 | 19:00 | youtube | launch #23 | long | How to get your finances in order: a 30-day money reset |
| 3 | Wed Nov 18 | 11:00 | pinterest | launch #15 | carousel | $1,000 emergency fund in 8 weeks |
| 3 | Wed Nov 18 | 12:30 | instagram, youtube, facebook | launch #1 | short | Budget weekly, not monthly |
| 3 | Wed Nov 18 | 18:00 | tiktok | launch #1 | short | Budget weekly, not monthly |
| 3 | Wed Nov 18 | 19:00 | instagram | launch #15 | carousel | $1,000 emergency fund in 8 weeks |
| 4 | Thu Nov 19 | 12:30 | instagram, youtube, facebook | launch #3 | short | 401(k) match explained: the raise you're ignoring |
| 4 | Thu Nov 19 | 18:00 | tiktok | launch #3 | short | 401(k) match explained: the raise you're ignoring |
| 5 | Fri Nov 20 | 11:00 | pinterest | holiday | carousel | Black Friday trap checklist: 7 tricks to spot |
| 5 | Fri Nov 20 | 12:30 | instagram, youtube, facebook | holiday | short | 5 Black Friday tricks, counting down |
| 5 | Fri Nov 20 | 18:00 | tiktok | holiday | short | 5 Black Friday tricks, counting down |
| 5 | Fri Nov 20 | 19:00 | instagram | holiday | carousel | Black Friday trap checklist: 7 tricks to spot |
| 6 | Sat Nov 21 | 12:30 | instagram, youtube, facebook | month 1 | short | The 24-hour cart rule |
| 6 | Sat Nov 21 | 18:00 | tiktok | month 1 | short | The 24-hour cart rule |
| 6 | Sat Nov 21 | 19:00 | instagram | Myth vs Math | carousel | Myth vs Math: is 0% for 12 months really free? |
| 7 | Sun Nov 22 | 12:30 | instagram, youtube, facebook | holiday | short | 3 Black Friday 'deals' that often aren't |
| 7 | Sun Nov 22 | 18:00 | tiktok | holiday | short | 3 Black Friday 'deals' that often aren't |
| 7 | Sun Nov 22 | 19:00 | instagram | holiday | carousel | Gift tracker: 5 columns that keep you on budget |
| 7 | Sun Nov 22 | 19:00 | tiktok | savings challenge | mid | $300 by New Year's Eve, week 2: the 72-hour cart pause |
| 7 | Sun Nov 22 | 19:00 | youtube | month 1 | long | Holiday spending without the January regret: a complete plan |
| 8 | Mon Nov 23 | 11:00 | pinterest | month 1 | carousel | Your holiday spending plan in 4 numbers |
| 8 | Mon Nov 23 | 12:30 | instagram, youtube, facebook | month 1 | short | Say no to the store card at checkout |
| 8 | Mon Nov 23 | 18:00 | tiktok | month 1 | short | Say no to the store card at checkout |
| 8 | Mon Nov 23 | 19:00 | instagram | month 1 | carousel | Your holiday spending plan in 4 numbers |
| 9 | Tue Nov 24 | 12:30 | instagram, youtube, facebook | month 1 | short | Debit or credit for online shopping? |
| 9 | Tue Nov 24 | 18:00 | tiktok | month 1 | short | Debit or credit for online shopping? |
| 10 | Wed Nov 25 | 11:00 | pinterest | month 1 | carousel | Is it really a deal? 6 checks before you buy |
| 10 | Wed Nov 25 | 12:30 | instagram, youtube, facebook | holiday | short | Free shipping at $75? The add-on math |
| 10 | Wed Nov 25 | 18:00 | tiktok | holiday | short | Free shipping at $75? The add-on math |
| 10 | Wed Nov 25 | 19:00 | instagram | month 1 | carousel | Is it really a deal? 6 checks before you buy |
| 11 | Thu Nov 26 | 12:30 | instagram, youtube, facebook | month 1 | short | The Black Friday cost-per-use test |
| 11 | Thu Nov 26 | 18:00 | tiktok | month 1 | short | The Black Friday cost-per-use test |
| 12 | Fri Nov 27 | 11:00 | pinterest | month 1 | carousel | How your credit score is actually calculated |
| 12 | Fri Nov 27 | 12:30 | instagram, youtube, facebook | month 1 | short | Pay-in-4 without the hangover |
| 12 | Fri Nov 27 | 18:00 | tiktok | month 1 | short | Pay-in-4 without the hangover |
| 12 | Fri Nov 27 | 19:00 | instagram | month 1 | carousel | How your credit score is actually calculated |
| 13 | Sat Nov 28 | 11:00 | pinterest | Myth vs Math | carousel | Myth vs Math: does the extended warranty pay off? |
| 13 | Sat Nov 28 | 12:30 | instagram, youtube, facebook | month 1 | short | Your holiday gift budget is one number |
| 13 | Sat Nov 28 | 18:00 | tiktok | month 1 | short | Your holiday gift budget is one number |
| 13 | Sat Nov 28 | 19:00 | instagram | Myth vs Math | carousel | Myth vs Math: does the extended warranty pay off? |
| 14 | Sun Nov 29 | 12:30 | instagram, youtube, facebook | holiday | short | A $600 holiday budget, line by line |
| 14 | Sun Nov 29 | 18:00 | tiktok | holiday | short | A $600 holiday budget, line by line |
| 14 | Sun Nov 29 | 19:00 | instagram | holiday | carousel | Cyber Monday: the 4-step price check |
| 14 | Sun Nov 29 | 19:00 | tiktok | savings challenge | mid | $300 by New Year's Eve, week 3: 1 subscription, 1 sale |
| 14 | Sun Nov 29 | 19:00 | youtube | month 1 | long | Credit scores explained from zero |

**Notes:**

- savings challenge: "$300 by New Year's Eve: day 1 (the plan)" was dated Sun Nov 15, before Day 1. Post it on Day 1 or drop it.
- Pinterest skipped (4-a-week start): Sat Nov 21 carousel "Myth vs Math: is 0% for 12 months really free?" posts on its other platforms only.
- Pinterest skipped (4-a-week start): Sun Nov 22 carousel "Gift tracker: 5 columns that keep you on budget" posts on its other platforms only.
- Pinterest skipped (4-a-week start): Sun Nov 22 long "Holiday spending without the January regret: a complete plan" posts on its other platforms only.
- Pinterest skipped (4-a-week start): Sun Nov 29 carousel "Cyber Monday: the 4-step price check" posts on its other platforms only.
- Pinterest skipped (4-a-week start): Sun Nov 29 long "Credit scores explained from zero" posts on its other platforms only.

**Launch pieces that don't fit before the dated packs start** (swap-ins; use one when a dated post is pulled in review):

- #5 short: Why did my credit score drop after paying in full?
- #18 carousel: Check your credit report like an auditor
- #8 short: Is your savings app FDIC insured? Check in 1 minute
- #4 short: The expense ratio that eats $18,000
- #17 carousel: What you actually own in an index fund
- #10 short: Sinking funds: the 'surprise' bill was on the calendar
- #2 short: Can you withdraw from a Roth IRA? Your contributions, yes
- #16 carousel: Roth or Traditional IRA? One question
- #22 long: How to start investing with $100 a month (beginner walkthrough)
- #7 short: Minimum payment vs $150 on a $3,000 card
- #9 short: 3 bank alerts to turn on today
- #19 carousel: Avalanche vs snowball, with real math
- #12 short: Should you close an old credit card? Not yet
- #21 carousel: Opening your first investment account
- #11 short: Target date funds: the one-fund retirement option
- #13 short: How to find and cancel forgotten subscriptions
- #20 carousel: App vs spreadsheet vs notebook

<!-- launch-week:end -->


## Bios

Each bio fits its platform's character limit. None of them promises results. Each one names AI use and that some links earn money.

| Platform | Limit | Bio |
|---|---|---|
| TikTok | 80 | Money explained in 60 seconds. Budgeting, credit, first investing. AI-assisted. |
| Instagram | 150 | Plain-English money: budgets, credit, saving and first-time investing. Made with AI help, fact-checked by a person. Not advice. Free reset ↓ |
| YouTube (channel description) | 1,000 | Money Made Simple explains everyday money in plain English: how to budget without a spreadsheet obsession, fix and protect your credit, build an emergency fund, and start investing with small amounts. New Shorts most days and a longer walkthrough on Sundays.

How we make videos: visuals and voice are made with AI tools; scripts are drafted with AI help and fact-checked by a person against official sources (IRS, CFPB, FTC, FDIC, SEC). Examples are fictional or hypothetical and labelled.

Education only, not financial, tax or investment advice. Some links are affiliate links, which means we may earn a commission at no cost to you; we also sell our own templates. Both are labelled. |
| Facebook Page (intro) | 101 | Plain-English money tips: budgeting, credit, saving, investing basics. AI-assisted, fact-checked. |
| Pinterest (about) | 500 | Simple budgeting, saving and credit guides, plus beginner investing explained without jargon. Printable budget planners, savings challenges and debt payoff trackers. Made with AI help and checked by a person; education, not financial advice. Some pins link to our own products or affiliate partners, always labelled. |

Link in bio: one page with three links, in this order. The free 7-Day Money Reset (email sign-up). The 20-Minute Budget ($12, "our own product"). The HYSA comparison page (it carries the affiliate disclosure).

## What to pin

Pin each post once it's live, on the day it goes out.

| Platform | Pin | Why |
|---|---|---|
| YouTube | **Channel trailer and featured video:** #23 "How to get your finances in order: a 30-day money reset" (launch Day 2) | It's the broadest search phrase, and it links to the free reset |
| TikTok | Pin 3: #6 "Freeze your credit for free tonight", #3 "401(k) match explained" and #1 "Budget weekly, not monthly" | They're evergreen how-tos that don't date. After 30 days, swap the weakest for the best performer |
| Instagram | Pin 3: #14 money-date carousel (product), #15 "$1,000 emergency fund in 8 weeks" carousel, #6 freeze Reel | Carousels get saved, and saves are the signal to grow |
| Facebook | Pin #6, the freeze Reel | It's the most broadly useful post, and Facebook pins only one |
| Pinterest | Profile showcase: the boards "Budgeting for beginners", "Saving money tips" and "Investing for beginners" | Showcase keyword boards, not single pins |

## Pinterest: 4 pins a week for the first two weeks

This follows scouting's playbook (PR #2, `research/scouting/pinterest-playbook-2026.md`): start a new account at 3–5 pins a week.

- **The table above already holds them.** Carousels and long videos also go to Pinterest. `scripts/launch_week.py` keeps the first 4 a week, at 11:00 (long-video pins at 11:30). The rest post on their other platforms only, and the notes list them. `factory manual` still builds a pin package for every carousel and long video, so in the first 14 days post only the pins in the table and skip the packages the notes list. (The other option, taking carousel and long out of the Pinterest account's formats for the fortnight, would also drop the 4 pins a week the table keeps.)
- **From week 3,** rise to 1–2 pins a day. Start with these site pins (PR #4, `site/pins/`). Each links to its own page and leads with the search phrase:
  - "Money personality quiz: find your budget style in 1 minute" → /quiz/
  - "How to freeze your credit for free (and check your report like an auditor)" → /blog/how-to-freeze-your-credit/
  - "401(k) match explained: the raise you're ignoring" → /blog/401k-match-explained/
  - "How to build a $1,000 emergency fund in 8 weeks" → /blog/how-to-build-an-emergency-fund/
  - "Sinking funds: how to stop 'surprise' expenses wrecking your budget" → /blog/sinking-funds-explained/
  - "How to find and cancel forgotten subscriptions in 10 minutes" → /blog/find-and-cancel-subscriptions/
  - "How to start investing with $100 a month" → /blog/how-to-start-investing-with-100-a-month/
  - "Expense ratios explained: the fee that can cost you $18,000" → /blog/expense-ratios-explained/
- **The site's own pin schedule** (`site/pins/schedule.csv`) starts Mon Nov 30, week 3 after Day 1. These 8 pins go first, in this order, and no page gets a second pin within 7 days. If Day 1 moves, ask for the schedule to move with it.
- **Domain:** the site's pins print moneymadesimple.netlify.app in their footer, the same as every link, and the channel pins print no domain at all. Claim moneymadesimple.netlify.app in Pinterest (or the custom domain, if Dhruv buys one before Day 1). Every page these pins link to is live by Nov 16. **Still check each page loads on the live site before pinning it.**

## After Day 14

- **Which pillar won:** compare saves and follows by pillar, and weight the swap-ins and month 2 toward the winner.
- **Search titles:** check each launch title's phrase by hand in the YouTube and Pinterest search boxes (scouting's `keywords-mms-first-30.csv` has a `confirmed_in_autocomplete` column). If autocomplete suggests different words, use them.
- **Judge pins at 30 days,** not 3.
