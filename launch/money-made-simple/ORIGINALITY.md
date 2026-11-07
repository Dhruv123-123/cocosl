# Originality pass: Money Made Simple months 1–5 and the YouTube series

Why: YouTube's "inauthentic content" rule judges whole channels and names "slideshows that all have the same narration" as its example (research/scouting/youtube-monetization.md, PR #2). Our videos are stills, captions and one TTS voice, so the scripts themselves have to vary in structure, and every long video needs one thing a template can't make.

## What was measured

Each of the 137 videos (109 Shorts, 28 long) got a structural signature: format, number of beats, hook shape (number-first, question, "you", statement), title shape and format label. Each video was then compared with the 20 videos before it in posting order, as the research's fix 3 suggests. Text overlap was already checked by `check_originality`; this catches the same video with the numbers swapped.

| | Before | After |
|---|---|---|
| Average share of the previous 20 with the same structure | 17.6% | 5.6% |
| Videos matching 40%+ of the previous 20 | 26 | 0 |
| Worst single video | 100% | 25% |

## What changed

- **34 Shorts re-formatted** (the most repetitive 25% of all videos, plus 6 in month 5 so no format is more than half a month). The facts, sources and claims are the same; the structure, spoken hook and on-screen text are new, and TikTok cuts were rebuilt where needed.
- **2 long videos restructured:** the month-4 W-4 explainer is now a myth-vs-fact episode, and the month-4 Rate My Budget long is a countdown from least risky to most expensive plan. Chapters were regenerated.
- **Every video now has a `format_style`**, and every long video has an **`original_element`** (type, what it is, and which chapter it sits in).
- `tests/test_originality.py` keeps it that way: each new format used at least 4 times, no format over half a month's Shorts, every long video with an original element, and no video matching more than half of the 20 before it.

## The five new formats

| Format | What it looks like on screen | Shorts using it |
|---|---|---|
| on-screen-calculation | The math is written out beat by beat (× ÷ =), one step per beat, ending on the answer | 8 |
| myth-vs-fact | MYTH / FACT split card per beat, three myths, then the verdict | 8 |
| question-reply | Opens on a "Common question" card, then the answer. Not presented as a real viewer comment; swap in real comments once they exist | 7 |
| countdown | Podium graphic counting down to number 1, biggest last | 7 |
| real-numbers | One fictional example followed line by line or month by month, with a running total | 4 |

Full mix across all videos:

| Format | Shorts | Long |
|---|---|---|
| countdown | 7 | 2 |
| explainer | 46 | 4 |
| list | 9 | 0 |
| myth-vs-fact | 8 | 2 |
| on-screen-calculation | 8 | 4 |
| question-reply | 7 | 2 |
| rate-my-budget | 20 | 1 |
| real-numbers | 4 | 4 |
| scorecard | 0 | 1 |
| walkthrough | 0 | 8 |

## Re-formatted Shorts

| Month | Title | New format |
|---|---|---|
| month-1 | The Black Friday cost-per-use test | on-screen-calculation |
| month-1 | The 1% raise rule | on-screen-calculation |
| month-1 | The two-minute call that can lower your APR | on-screen-calculation |
| month-3 | $2,500: the student loan deduction people miss | on-screen-calculation |
| month-5 | Rate My Budget #21: $1,000 a month on one car | on-screen-calculation |
| month-2 | $16,100: why you probably won't itemize | on-screen-calculation |
| month-1 | What a hard inquiry actually costs you | myth-vs-fact |
| month-1 | Your first market drop is normal | myth-vs-fact |
| month-1 | The HSA is a secret retirement account | myth-vs-fact |
| month-1 | Do a W-4 check before January | myth-vs-fact |
| month-1 | Cash back vs points, honestly | myth-vs-fact |
| month-2 | 3 'IRS' messages that are always scams | myth-vs-fact |
| month-1 | Pay-in-4 without the hangover | question-reply |
| month-1 | Find all your federal student loans in 5 minutes | question-reply |
| month-3 | 1 question to ask before you move in together | question-reply |
| month-3 | 3 debt numbers to share with your partner | question-reply |
| month-2 | 1099-K, 1099-NEC: 3 things side hustlers should know | question-reply |
| month-2 | 3 weeks in and the budget broke? Restart in 3 steps | question-reply |
| month-3 | 3 signs your tax preparer is a scam | countdown |
| month-3 | 3 romance scam red flags | countdown |
| month-2 | 3 free ways to file your taxes | countdown |
| month-3 | 2 reasons to file your taxes early | countdown |
| month-3 | 21 days: when your tax refund usually shows up | countdown |
| month-2 | 1 in 5 who qualify for this tax credit miss it | countdown |
| month-1 | Your one money number | real-numbers |
| month-1 | Pay yourself first, literally on payday | real-numbers |
| month-2 | Rate My Budget #6: $78K, saving 2%, $180 in subscriptions | real-numbers |
| month-2 | 1 number to pick on January 1: your savings rate | real-numbers |
| month-5 | A tax extension gives you 6 more months to file, not to pay | myth-vs-fact |
| month-5 | Can't pay your taxes? File anyway: 5% vs 0.5% | on-screen-calculation |
| month-5 | Paying the IRS? The free way vs the 2% way | on-screen-calculation |
| month-5 | How long to keep tax papers: 3 years for most | question-reply |
| month-5 | Your 401(k) beneficiary form can beat your will | myth-vs-fact |
| month-5 | 5 bank fees you can stop paying this month | countdown |

## Original element in each long video

The three kinds the research names: a **worked-example chart** drawn from the video's own numbers (the renderer's charts module), a **screen recording** of a real official tool (landing pages and test inputs only, never personal data), or a **human segment** Dhruv records himself. Human segments must stay truthful: say what he really does, or present it plainly as a suggestion.

| Video | Format | Original element | Chapter |
|---|---|---|---|
| month-1: Holiday spending without the January regret: a complete plan | walkthrough | **worked-example-chart**: The four-category holiday budget chart built from the video's $600 example, filled in live | Four categories |
| month-1: Credit scores explained from zero | explainer | **screen-recording**: Screen recording of AnnualCreditReport.com: requesting all three reports and where the account list sits (no personal data on screen) | Check your reports |
| month-1: Your 401(k), explained: match, vesting, funds and fees | walkthrough | **worked-example-chart**: Match chart: the video's salary example at 3%, 6% and 10% contribution showing where the match stops | The match |
| month-1: 10 money moves to make before January 1 | countdown | **screen-recording**: Screen recording of the IRS Tax Withholding Estimator start page and a credit freeze page (test inputs only) | 3. Withholding |
| month-2: The 2027 money reset: a complete plan in one sitting | walkthrough | **human-segment**: Dhruv records the 'When it breaks' chapter on camera or as his own voice: one honest, true restart tip | When it breaks |
| month-2: Rate My Budget: 3 budgets, fully broken down | scorecard | **worked-example-chart**: Scorecard chart: the five questions as bars for each fictional budget, before and after the fix | The scorecard |
| month-2: Your first tax return, start to finish | walkthrough | **screen-recording**: Screen recording of the IRS Free File landing page and the 'Do you need to file?' interactive tool | Free filing |
| month-2: Side hustle taxes explained: 1099s, quarterly payments, deductions | explainer | **worked-example-chart**: Chart: the video's side-income example split into set-aside, self-employment tax and income tax | Self-employment tax |
| month-3: How tax brackets actually work, with real math | on-screen-calculation | **worked-example-chart**: Bracket staircase chart for the $60K example, layer by layer, with the effective rate marked | Step 1 |
| month-3: Rate My Budget: a teacher, a retail worker and a $90K renter | rate-my-budget | **worked-example-chart**: Side-by-side spending bars for the three fictional budgets with the fix applied | Budget 1 |
| month-3: 401(k), IRA or HSA: which account gets your money first? | real-numbers | **worked-example-chart**: Account-order chart: the same $500 a month routed through 401(k) match, HSA and IRA, with the tax effect of each | Real math |
| month-3: Money and relationships: how to combine finances without fighting | question-reply | **human-segment**: Dhruv records the 'Money date' chapter in his own voice, with his real check-in routine if he has one, or a plainly-stated suggestion | Money date |
| month-4: What to do with your tax refund: a plan with real numbers | real-numbers | **worked-example-chart**: Waterfall chart of the $2,800 refund flowing into buffer, debt, sinking funds and a treat | The split |
| month-4: Your W-4, explained: stop overpaying (or owing) every April | myth-vs-fact | **screen-recording**: Screen recording of the IRS Tax Withholding Estimator with made-up inputs, ending on the suggested W-4 entries | Real numbers: refund |
| month-4: Rate My Budget: four refunds, four plans | countdown | **worked-example-chart**: Podium graphic ranking the four fictional refund plans with each one's cost of doing nothing | Number 1: the tax bill |
| month-4: Where's my tax refund? How refunds work, and what slows them down | explainer | **screen-recording**: Screen recording of Where's My Refund on IRS.gov (logged-out, entry screen only) and the IRS2Go app's status screen | How it works |
| youtube-series: How to Make a Budget That Actually Works (Step by Step for Beginners) | walkthrough | **worked-example-chart**: The four-number budget filled in live on screen from the $3,200 example, ending at $425 (about $100 a week) | Step 5: the number you can actually spend |
| youtube-series: Debt Snowball vs Avalanche: We Ran the Real Numbers | real-numbers | **worked-example-chart**: Month-by-month payoff chart from the video's own simulation: snowball vs avalanche balances, payoff months 5/14/24 vs 19/21/24 | Side by side |
| youtube-series: How to Build an Emergency Fund (Even on a Tight Budget) | walkthrough | **screen-recording**: Screen recording of the FDIC BankFind tool checking a bank's insurance (any public bank) and setting a recurring transfer in a demo banking screen | Where to keep it |
| youtube-series: How Credit Scores Actually Work (and How to Raise Yours) | myth-vs-fact | **screen-recording**: Screen recording of AnnualCreditReport.com and the dispute page of one bureau (no personal data), plus a utilization bar chart | Check and dispute your report free |
| youtube-series: How to Start Investing With $100 a Month (Beginner's Guide) | on-screen-calculation | **worked-example-chart**: Growth curve for $100/month at a hypothetical 7% (10, 20, 30 years) and the 0.03% vs 1% fee gap, drawn from the script's numbers | What $100 a month can become |
| youtube-series: Roth vs Traditional IRA: Which One Should You Pick? | on-screen-calculation | **worked-example-chart**: The $1,000 Roth vs traditional side-by-side: $1,000 → $4,000 → $3,200 vs $800 → $3,200 | The $1,000 example |
| youtube-series: 401(k) Match Explained: Don't Leave Free Money on the Table | on-screen-calculation | **worked-example-chart**: Match chart for the $50,000 salary: 50%-up-to-6% vs 100%-up-to-4%, with the per-paycheck cost | Match formula 1: 50% up to 6% |
| youtube-series: High-Yield Savings Accounts Explained: Are They Safe, and Are They Worth It? | explainer | **screen-recording**: Screen recording of FDIC BankFind, plus a $5,000 interest bar chart at 0.5% vs 4% (hypothetical) | Is it safe? |
| youtube-series: Budgeting App vs Spreadsheet: Which One Should You Use? | question-reply | **human-segment**: Dhruv records 'Try it for 30 days' in his own voice, saying truthfully which method he uses (or that he's choosing one now) | Try it for 30 days |
| youtube-series: How to Pay Off Credit Card Debt Fast (The Minimum Payment Trap, in Real Numbers) | real-numbers | **worked-example-chart**: Payoff-time chart for $5,000 at 24%: minimum vs $150, $200, $300, $400 a month, from the script's simulation | Fix the payment |
| youtube-series: Sinking Funds Explained: Stop 'Surprise' Expenses From Wrecking Your Budget | walkthrough | **worked-example-chart**: The $3,000-a-year irregular costs list turning into twelve $250 monthly bars | Step 2: do the math |
| youtube-series: How to Freeze Your Credit (Free, 15 Minutes, All 3 Bureaus) | walkthrough | **screen-recording**: Screen recording of each bureau's official freeze page (landing pages only, no personal data entered) | Step by step: Equifax, Experian, TransUnion |

## Still to do outside the scripts

- **Render the original elements.** Charts can come from `media/charts.py`; screen recordings and the three human segments need a person. A long video without its element shouldn't go up.
- **Vary the look, not just the words:** a different layout every few videos, and some licensed B-roll (research fix 2).
- **Code-level sameness check** (research fix 3) belongs in the factory itself. The test here covers the launch content; the factory check would cover anything generated later.
