# Originality pass: 1099 Money (launch, months 1–5 and the driver series)

Why: YouTube's "inauthentic content" rule judges whole channels, and its example is "slideshows that all
have the same narration" (research/scouting/youtube-monetization.md, PR #2). These videos are stills,
captions and one TTS voice, so the scripts have to vary in structure, and every long video needs one thing
a template can't make. Same method as the Money Made Simple pass (`launch/money-made-simple/ORIGINALITY.md`, PR #5).

## What was measured

All 158 videos (134 Shorts, 24 long) got a structural signature: format, number of beats, hook shape
(number-first, question, "you", statement), title shape and format label. Each was compared with the 20
videos before it in posting order. Before the pass, 125 of the 134 Shorts had exactly six beats.

| | Before | After |
|---|---|---|
| Average share of the previous 20 with the same structure (with format labels) | 6.5% | 2.6% |
| Same, ignoring the labels (beats, hook and title only) | 14.3% | 7.9% |
| Videos matching 40%+ of the previous 20 (ignoring labels) | 12 | 0 |
| Worst single video (ignoring labels) | 50% | 33% |
| Shorts with exactly 6 beats | 125 | 101 |

The "ignoring labels" rows matter most: they show the scripts themselves changed, not just their tags.

## What changed

- **36 Shorts re-formatted** (the most repetitive, plus enough per batch that no format is more than half of a
  month). Facts, sources, captions and claims to verify are unchanged. The structure, spoken hook, beats and
  on-screen text are new. Beat counts now run from 4 to 7.
- One fix while rewriting: the month-1 SEP IRA Short no longer says a Solo 401(k) "has stricter setup
  deadlines", which isn't reliably true since SECURE 2.0.
- **Every video now has a `format_style`**, and every long video has an **`original_element`** (type, what it
  is, and which chapter it sits in). Long videos weren't restructured: their chapters already differ widely.
- `tests/test_1099_originality.py` keeps it that way: each new format used at least 4 times, no format over
  half of any batch's Shorts, myth/fact, question and countdown Shorts actually built that way, every long
  video with an original element (all three kinds used), and no video matching more than half of the 20 before it.

## The five new formats

| Format | What it looks like on screen | Re-formatted Shorts |
|---|---|---|
| on-screen-calculation | The math written out beat by beat (× ÷ =), ending on the answer | 6 (plus 5 existing math Shorts labeled as such) |
| myth-vs-fact | MYTH / FACT split card per beat, three myths, then the verdict | 9 |
| question-reply | Opens on a "Common question" card, then the answer. Not presented as a real viewer comment; swap in real comments once they exist | 10 |
| countdown | Podium graphic counting down to number 1, the most important last | 6 |
| real-numbers | One fictional freelancer followed line by line, with a running total | 5 |

Full mix:

| Format | Shorts | Long |
|---|---|---|
| comparison | 3 | 1 |
| countdown | 6 | 3 |
| deadline-alert | 20 | 0 |
| explainer | 53 | 3 |
| how-to | 8 | 0 |
| list | 9 | 0 |
| myth-vs-fact | 9 | 1 |
| on-screen-calculation | 11 | 3 |
| question-reply | 10 | 0 |
| real-numbers | 5 | 4 |
| scorecard | 0 | 1 |
| walkthrough | 0 | 8 |

## Re-formatted Shorts

| Batch | Title | New format | Beats |
|---|---|---|---|
| launch | Stop paying clients into your personal account | myth-vs-fact | 5 |
| launch | The home office deduction, honestly | on-screen-calculation | 7 |
| launch | Your car is a deduction if you log it | on-screen-calculation | 5 |
| launch | Stop putting your SSN on W-9s | question-reply | 5 |
| launch | The 3-account system for freelancers | real-numbers | 7 |
| month-1 | Don't buy a laptop just for the tax write-off | on-screen-calculation | 6 |
| month-1 | It's not too late to cut your 2026 tax | question-reply | 5 |
| month-1 | Your 1099 might be wrong. Here's what to do. | countdown | 6 |
| month-1 | Freelance income dries up in December. Plan for it. | real-numbers | 7 |
| month-1 | An LLC won't lower your taxes | myth-vs-fact | 5 |
| month-1 | The upside of self-employment tax | on-screen-calculation | 6 |
| month-2 | Your 2027 safe harbor is already set | on-screen-calculation | 6 |
| month-2 | Skipped a quarterly payment? Pay now, not April | question-reply | 4 |
| month-2 | Your coworking membership is deductible. Your gym isn't. | myth-vs-fact | 6 |
| month-2 | Don't rush to file in January | myth-vs-fact | 5 |
| month-2 | You can still fund an HSA for 2026 | question-reply | 4 |
| month-3 | Home office: the 'exclusive use' rule | countdown | 6 |
| month-3 | No mileage log? How to rebuild one honestly | countdown | 6 |
| month-3 | Is your side hustle a hobby to the IRS? | myth-vs-fact | 5 |
| month-3 | Lost money in your first year freelancing? | real-numbers | 7 |
| month-3 | The 20% deduction most freelancers don't know they get | on-screen-calculation | 6 |
| month-3 | Owe more than you can pay? Do this. | countdown | 6 |
| month-3 | Got a letter from the IRS? Don't panic. | question-reply | 5 |
| month-4 | S corp for 2027? The deadline is March 15 | myth-vs-fact | 5 |
| month-4 | Getting a big refund as a freelancer? Read this. | question-reply | 5 |
| month-4 | Made a mistake after filing? Use Form 1040-X | countdown | 5 |
| month-4 | Owed no tax last year? You may owe no penalty this year | question-reply | 5 |
| month-4 | Most of your income comes late in the year? Read this. | real-numbers | 7 |
| month-5 | Free help with your taxes (if you qualify) | question-reply | 5 |
| month-5 | Lost a big client? You might pay less tax this quarter | real-numbers | 6 |
| month-5 | Paying yourself isn't a business expense | myth-vs-fact | 5 |
| month-5 | You can change health plans mid-year if this happens | countdown | 7 |
| month-5 | Got a CP2000? It's a proposal, not a bill | myth-vs-fact | 5 |
| month-5 | Bought a laptop for work? You can usually deduct it now | question-reply | 5 |
| drivers | Delivery tips are income, and there's a new deduction | myth-vs-fact | 5 |
| drivers | Running two apps at once? Log the miles once | question-reply | 4 |

## Original element in each long video

Three kinds: a **worked-example chart** drawn from the video's own numbers (the renderer's charts module), a
**screen recording** of a real official tool (landing pages and made-up inputs only, never personal data),
or a **human segment** Dhruv records himself. Human segments must stay truthful: say what he really does,
or present it plainly as a suggestion.

| Video | Format | Original element | Chapter |
|---|---|---|---|
| launch: Your first year freelancing: the complete money setup | walkthrough | **human-segment**: Dhruv records the monthly money hour in his own voice: the routine he actually runs, or plainly framed as the routine he's starting now | Monthly hour |
| launch: Quarterly estimated taxes, explained with one real-numbers year | real-numbers | **worked-example-chart**: Sam's four payments charted against Sam's profit by quarter, drawn from the script's numbers, with the safe-harbor line marked | Sam's year |
| month-1: Year-end tax moves for freelancers (and the ones to skip) | walkthrough | **worked-example-chart**: Bar chart of the $1,000 purchase: $230 of tax saved next to the $770 still spent, from the script's example | Write-off math |
| month-1: LLC, S corp or sole proprietor? What actually changes | comparison | **worked-example-chart**: S corp savings vs running costs at several profit levels, drawn from the script's numbers, showing where the lines cross | Numbers |
| month-1: How to set your freelance rate (with the tax math) | on-screen-calculation | **worked-example-chart**: Stacked bar from target pay plus costs plus tax down to the hourly rate, built from the script's example | Rate |
| month-1: Your freelancer tax season plan: January to April | walkthrough | **screen-recording**: Screen recording of IRS Direct Pay's start page, showing the reason, form and tax-year choices for an estimated payment (nothing submitted, no personal data) | Jan 15 |
| month-2: Freelance taxes at $30K, $60K and $120K: three real examples | real-numbers | **worked-example-chart**: Side-by-side bars for $30K, $60K and $120K split into SE tax, income tax and state, with the set-aside rate on each | Set aside |
| month-2: Your 1099s explained: every form, every mistake, every fix | explainer | **screen-recording**: Screen recording of the IRS 'Understanding your Form 1099-K' page, scrolling to the thresholds and what to do if a form is wrong | 1099-K |
| month-2: Every freelancer deduction, ranked by what it saves | countdown | **worked-example-chart**: Ranked bar chart of what each deduction saves at $60K of profit, using the script's figures, revealed bar by bar as the countdown runs | How much |
| month-2: Get your freelance taxes ready to file in one weekend | walkthrough | **human-segment**: Dhruv films his own Friday-night prep on screen or at his desk: downloading statements into one folder, using a demo account clearly labeled as a demo if he doesn't want to show his own | Prep |
| month-3: Schedule C explained, section by section, for freelancers | walkthrough | **screen-recording**: Screen recording of the blank Schedule C PDF from irs.gov, scrolled section by section with Jo's fictional numbers overlaid | Header |
| month-3: The home office deduction: every rule, both methods, real numbers | on-screen-calculation | **worked-example-chart**: Simplified vs regular method chart for the renter and owner examples in the script, with the bigger deduction highlighted | Choose |
| month-3: The mileage deduction: logs, rates, commuting rules and mistakes | explainer | **screen-recording**: Screen recording of a demo mileage log being filled in, plus the IRS standard mileage rates page showing the 2026 rate | The log |
| month-3: From Schedule C to Form 1040: how a freelance tax return fits together | walkthrough | **worked-example-chart**: Flow diagram of the example's numbers moving from Schedule C to Schedule SE, Schedule 1 and Form 1040, drawn from the script | Example |
| month-3: 12 freelance tax mistakes that lead to IRS letters | countdown | **human-segment**: Dhruv reads the pre-filing routine in his own voice, saying truthfully whether he uses it or presenting it plainly as a suggestion | Before you file |
| month-4: How to file your freelance tax return, step by step | walkthrough | **screen-recording**: Screen recording of the IRS Free File landing page and the online account's payment history view (logged-out or demo screens only) | Step one |
| month-4: Owe the IRS more than you expected? Every option, explained | explainer | **screen-recording**: Screen recording of the IRS Online Payment Agreement landing page, showing short-term vs long-term options (nothing submitted) | Long |
| month-4: Still time to lower your 2026 tax: what works in March | countdown | **worked-example-chart**: Before/after chart of the example's tax as each move (IRA, HSA, SEP) is added, from the script's numbers | Example |
| month-4: April 15, 2027: your two tax payments, worked out | real-numbers | **worked-example-chart**: Chart of Priya's two April 15 payments, the 2026 balance and the Q1 2027 estimate, side by side from the script's figures | Priya numbers |
| month-5: Tax extensions for freelancers: how, when, and what they really cost | myth-vs-fact | **screen-recording**: Screen recording of IRS Direct Pay showing the 'extension' reason option (nothing submitted, no personal data) | How one |
| month-5: Day job, side gig or working spouse: freelance tax without quarterly payments | on-screen-calculation | **screen-recording**: Screen recording of the IRS Tax Withholding Estimator with made-up inputs, ending on the suggested extra withholding for line 4(c) | How |
| month-5: What your 2026 tax return says about your freelance business | scorecard | **worked-example-chart**: Scorecard chart of the ten numbers for the example freelancer across two fictional years, with arrows for direction | Compare |
| month-5: Mid-year tax planning for freelancers: project 2027 now and fix it early | walkthrough | **human-segment**: Dhruv records the check-in routine in his own voice, saying truthfully when he does his own mid-year check, or plainly that he's starting one | Repeat |
| month-5: The June 15 payment, worked out for three freelancers | real-numbers | **worked-example-chart**: Bars for Ana, Sam and Jo: safe-harbor payment vs 90%-of-this-year payment, from the script's figures | Safe harbor |

## Still to do outside the scripts

- **Make the original elements.** Charts can come from `media/charts.py`; the screen recordings and the four
  human segments need a person. A long video without its element shouldn't go up.
- **Packs:** all seven packs (launch, months 1–5, drivers) were re-rendered after this pass with 0 blocks,
  and the copies in project files replaced. Anything already recorded from an old pack needs the new
  script for the 36 re-formatted Shorts.
- **Vary the look too:** a different card layout every few videos, and some licensed B-roll.
