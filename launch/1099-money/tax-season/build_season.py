"""Tax-season text posts for 1099 Money (Jan 19 - Apr 14, 2027), the follow-on to q4/.

Videos (months 2-5), pins and the newsletter already cover this window; these are for LinkedIn,
Threads/X and Facebook freelancer groups. Formats rotate (myth-vs-fact, worked-math, common-question,
countdown, real-numbers, checklist) so no two posts in a row share a structure.
Run: python3 launch/1099-money/tax-season/build_season.py && node launch/1099-money/q4/render_cards.mjs tax-season
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
SITE = "1099money.netlify.app"
NTA = "Educational, not tax advice. 2026 federal figures."
IRS = "https://www.irs.gov"
LINKS = {"calc": f"Free quarterly tax calculator (link in profile): {SITE}/",
         "finder": f"Free deduction finder, 2 minutes (link in profile): {SITE}/deduction-finder/",
         "mileage": f"Driver mileage calculator (link in profile): {SITE}/mileage/"}

P = []
def post(date, fmt, topic, title, card, linkedin, short, facebook, sources, claims, link="calc"):
    P.append(dict(date=date, format=fmt, topic=topic, title=title, card=card, linkedin=linkedin.strip(),
                  short=short, facebook=facebook, sources=sources, claims=claims, link=link))

post("2027-01-19", "checklist", "filing", "Before you file: the freelancer folder",
 ["Before you file:", "one folder", "7 things in it"],
 """Before you open tax software, make one folder for your 2026 return. Seven things go in it:

1. Every 1099-NEC and 1099-K you received.
2. Your own income total for 2026, from your invoices or bank deposits. This, not the forms, is your income.
3. Business expenses, totaled by category.
4. Your mileage log total.
5. Home office measurements, if you have one.
6. Every 2026 estimated payment, with dates (your IRS online account lists them).
7. Health insurance premiums and any retirement or HSA contributions.

Most forms arrive by February 1, but some come later or get corrected. So build the folder now and file once it's complete, usually mid-February to March.""",
 "Before filing as a freelancer, one folder: every 1099, your OWN income total, expenses by category, mileage total, home office measurements, all 2026 estimated payments, health/retirement/HSA amounts. Then file once.",
 "Something that makes filing as a freelancer easier: one folder with every 1099, your own income total, expenses by category, mileage, home office measurements, the estimated payments you made, and health insurance and retirement amounts. Then file once it's complete.",
 [IRS + "/businesses/small-businesses-self-employed/recordkeeping"], ["(process, no figures)"])

post("2027-01-22", "myth-vs-fact", "filing", "Freelance filing myths",
 ["Filing myths", "Myth: no 1099, no tax", "Fact: all income counts"],
 """Three freelance filing myths, and what's true.

Myth: if a client didn't send a 1099, you don't report that income.
Fact: all your income is taxable. For 2026 payments, clients only have to send a 1099-NEC at $2,000 or more, so plenty of income comes with no form.

Myth: you can just enter the totals from your 1099s.
Fact: your income is what you actually received. A 1099-K shows gross before fees, and some clients count invoices in the wrong year. Use your own records, and make sure every form is covered.

Myth: freelancers have to file in January to avoid trouble.
Fact: the deadline is April 15, 2027. Filing before every form arrives is how amended returns happen.""",
 "Freelance filing myths: ❌ no 1099 = no tax (all income counts; for 2026 clients only must send one at $2,000+). ❌ just copy your 1099 totals (use your own records). ❌ file in January (deadline Apr 15; wait for all forms).",
 "Common mix-up this time of year: income with no 1099 is still taxable (for 2026 payments, clients only have to send one at $2,000+). Use your own income records as the total, and wait until all forms are in before filing.",
 [IRS + "/forms-pubs/about-form-1099-nec", IRS + "/businesses/understanding-your-form-1099-k"],
 ["1099-NEC threshold $2,000 for 2026 payments", "Filing deadline Apr 15, 2027"])

post("2027-01-26", "worked-math", "schedulec", "Schedule C in four lines",
 ["Schedule C", "in 4 lines", "income − expenses = profit"],
 """Schedule C looks long. The math is four lines. A worked example, fictional freelancer, 2026:

Line 1, gross receipts: $68,000 (everything clients paid, including amounts on 1099-Ks)
Line 28, total expenses: $9,200 (software, equipment, fees, mileage, phone share...)
Line 30, home office: $800 (160 sq ft × $5, simplified method)
Line 31, net profit: $68,000 − $9,200 − $800 = $58,000

That $58,000 is the number everything else runs on: self-employment tax on Schedule SE, then income tax on Form 1040, and your safe harbor for next year. The rest of Schedule C is categories and a few yes/no questions.""",
 "Schedule C is 4 lines of math: Line 1 gross receipts ($68,000) − Line 28 expenses ($9,200) − Line 30 home office ($800) = Line 31 net profit ($58,000). That one number drives SE tax AND income tax.",
 "If Schedule C looks intimidating: it's really gross receipts (line 1), minus total expenses (line 28), minus home office (line 30), equals net profit (line 31). Everything else is putting expenses in the right categories.",
 [IRS + "/forms-pubs/about-schedule-c-form-1040"], ["Schedule C line numbers 1, 28, 30, 31", "Simplified home office $5/sq ft"])

post("2027-02-02", "common-question", "deductions", "Can I deduct my phone?",
 ["Common question:", "Can I deduct my phone?", "the business share"],
 """A common question: can I deduct my phone bill as a freelancer?

Short answer: the business share of it, yes.

How to work out the share: pick a typical month and estimate how much of your calls, messages and data are for work. If it's 40%, deduct 40% of the plan, and 40% of the phone itself if you bought one in 2026.

What makes it hold up: write down how you got the percentage, once, and keep it with your records. "About half, because I use it for client calls, scheduling and two work apps" is fine. "100%" for the only phone you own usually isn't.

The same logic works for home internet, and you don't need a home office to take it.""",
 "Q: Can freelancers deduct their phone? A: the business share. Estimate it from a typical month (say 40%), deduct 40% of the plan and phone, and write down how you got the number. 100% of your only phone rarely holds up.",
 "On deducting a phone as a freelancer: it's the business-use share of the plan and the phone. Estimate it from a typical month and jot down how you got the percentage. Same for home internet, even without a home office.",
 [IRS + "/publications/p334"], ["Business-use percentage approach for mixed-use property"], link="finder")

post("2027-02-05", "countdown", "deductions", "4 deductions freelancers miss",
 ["Commonly missed:", "4 deductions", "#1 is automatic"],
 """Four deductions freelancers commonly miss, counting down to the one that's automatic.

4. Payment platform fees. A 1099-K shows the gross, before PayPal, Stripe or Upwork took their cut. The fees are a business expense.
3. Self-employed health insurance. If you paid your own premiums and weren't eligible for an employer plan, they generally come off your income (Form 7206).
2. Business mileage. 72.5 cents a mile for 2026: client meetings, supply runs, the post office. A rebuilt log from your calendar beats no log.
1. Half of your self-employment tax. Automatic, but only if your return actually includes Schedule SE. Check that your software filled it in.

And one bonus: the 20% qualified business income deduction, which most freelancers below about $200,000 of taxable income get.""",
 "Commonly missed by freelancers: 4) platform fees (1099-K is gross), 3) self-employed health insurance (Form 7206), 2) mileage at 72.5¢/mi, 1) half of SE tax (automatic, if Schedule SE is on your return). Bonus: the 20% QBI deduction.",
 "A few deductions freelancers often miss: platform fees (your 1099-K is before fees), self-employed health insurance premiums, business mileage at 72.5 cents a mile, and the 20% QBI deduction. Worth double-checking before filing.",
 [IRS + "/forms-pubs/about-form-7206", IRS + "/tax-professionals/standard-mileage-rates", IRS + "/forms-pubs/about-form-8995"],
 ["Form 7206 SE health insurance", "72.5 cents 2026", "QBI threshold ~ $200K single"], link="finder")

post("2027-02-09", "real-numbers", "homeoffice", "Home office: simplified vs regular",
 ["Home office:", "$600 vs $2,484", "same room, two methods"],
 """Same room, two methods. A fictional renter, Priya, with a 120 sq ft office in a 1,000 sq ft apartment:

Simplified method: 120 × $5 = $600. Done.

Regular method: the office is 12% of the home.
- Rent: $18,000 a year × 12% = $2,160
- Utilities: $2,400 × 12% = $288
- Renter's insurance: $300 × 12% = $36
Total: $2,484.

So for Priya, the regular method is worth about four times as much, for the price of Form 8829 and keeping the bills.

The calculation changes for homeowners: the regular method brings in depreciation, which can mean tax when you sell. That's why many owners stick with simplified. Either way, the room has to be used regularly and only for work.""",
 "Home office, same 120 sq ft room: simplified = 120 × $5 = $600. Regular (renter, 12% of home): 12% of rent + utilities + insurance ≈ $2,484. Renters often win with regular; owners should weigh depreciation first.",
 "For renters weighing the home office methods: the simplified method is $5 a square foot (max 300 sq ft), but the regular method (your office percentage of rent, utilities and renter's insurance) is often much bigger for renters. Homeowners have a depreciation catch to consider.",
 [IRS + "/businesses/small-businesses-self-employed/home-office-deduction", IRS + "/publications/p587"],
 ["Simplified $5/sq ft up to 300", "Regular method % of rent/utilities/insurance", "Owner depreciation recapture"])

post("2027-02-16", "myth-vs-fact", "homeoffice", "Home office myths",
 ["Home office myths", "Myth: it's an audit flag", "Fact: unsupported is"],
 """Home office myths that cost freelancers money.

Myth: claiming a home office triggers an audit.
Fact: there's no rule like that. What causes trouble is a claim you can't support: a space that isn't used only for work, or no measurements.

Myth: it needs to be a separate room.
Fact: a clearly separate part of a room can qualify, if it's used regularly and only for your business.

Myth: you can't claim it if you also have a coworking desk.
Fact: you can, if home is still your principal place of business. It gets harder if most of your work happens elsewhere.

Myth: the simplified method is always best.
Fact: it's easiest. Renters with high rent often get more from the regular method.""",
 "Home office myths: ❌ audit trigger (unsupported claims are the problem) ❌ needs a separate room (a dedicated area can qualify) ❌ no coworking allowed (it depends where you mainly work) ❌ simplified is always best (renters: compare).",
 "On the home office deduction: it doesn't need a separate room (a clearly separate area used only for work can qualify), and claiming it isn't a red flag by itself. What matters is exclusive, regular use and having measurements.",
 [IRS + "/publications/p587"], ["Exclusive and regular use", "Principal place of business"])

post("2027-02-19", "common-question", "mileage", "Is driving to the post office deductible?",
 ["Common question:", "Which drives count?", "commute ≠ business"],
 """A common question: which drives can a freelancer deduct?

Usually yes:
- To a client's office or a job site
- To the post office, bank or supply store for the business
- Between two business stops

Usually no:
- Commuting to a regular workplace, like a coworking space you go to every day
- Personal errands, even if you stop at a client on the way (only the business part counts)

The home office twist: if your home is your principal place of business, trips from home to clients are business trips, not a commute.

For 2026 it's 72.5 cents a business mile. Keep a log with date, destination, purpose and miles. A log rebuilt honestly from your calendar is far better than none.""",
 "Q: Which drives can freelancers deduct? A: client sites, business errands, between business stops. Not: commuting to a regular workplace or personal errands. If home is your principal place of business, home → client counts. 72.5¢/mi for 2026.",
 "On mileage for freelancers: trips to clients and business errands count, commuting to a regular workplace doesn't. If your home office is your principal place of business, drives from home to clients generally count too. It's 72.5 cents a mile for 2026.",
 [IRS + "/publications/p463", IRS + "/tax-professionals/standard-mileage-rates"], ["Home office makes home->client trips deductible", "72.5 cents"], link="mileage")

post("2027-02-23", "worked-math", "mileage", "What a mileage log is worth",
 ["Mileage log:", "2,400 miles", "= $1,740 deduction"],
 """What a mileage log is worth, worked out. A fictional freelance photographer, 2026:

Client shoots: 2 a week × 30 miles round trip × 40 weeks = 2,400 miles
2,400 × $0.725 = $1,740 deduction

At $60,000 of profit, a Schedule C deduction saves roughly 23 cents per dollar in federal income and self-employment tax:
$1,740 × 0.23 ≈ $400 less tax

Without a log, the IRS can disallow the whole thing. With one (date, where, why, miles), it's routine.

If you didn't keep one in 2026, rebuild it from your calendar, invoices and map distances, and note that it's reconstructed. Then start a real one this month.""",
 "Mileage log math: 2 shoots/week × 30 mi × 40 weeks = 2,400 mi × 72.5¢ = $1,740 deduction ≈ $400 less federal tax at $60K profit. No log, no deduction. Rebuild 2026 honestly from your calendar.",
 "If you're unsure whether tracking mileage is worth it: two 30-mile round trips a week for 40 weeks is 2,400 miles, a $1,740 deduction at 72.5 cents a mile. A log with date, destination, purpose and miles is what makes it stick.",
 [IRS + "/tax-professionals/standard-mileage-rates", IRS + "/publications/p463"],
 ["2,400 × 0.725 = 1,740", "~23% marginal at $60K"], link="mileage")

post("2027-03-02", "countdown", "schedulec", "Schedule C mistakes",
 ["Schedule C:", "3 costly mistakes", "#1: missing income"],
 """Three Schedule C mistakes that lead to IRS letters, counting down to the most common.

3. Round numbers. $5,000 for supplies and $3,000 for phone look estimated, and estimates are hard to defend. Use your real totals.

2. Personal costs in business categories. Groceries as "meals", the family phone at 100%, your draw recorded as an expense. Each one lowers profit and raises questions.

1. Income that doesn't match the forms. The IRS compares every 1099-NEC and 1099-K with your return. If your gross receipts are lower than the forms add up to, expect a CP2000 letter. Report at least what the forms show (then deduct fees and refunds) unless part of it truly isn't business income, and keep records that show why.""",
 "Schedule C mistakes that bring IRS letters: 3) round-number expenses 2) personal costs as business (incl. owner's draws) 1) gross receipts lower than your 1099s add up to, the classic CP2000 trigger. Report gross, then deduct fees.",
 "Before filing: make sure your Schedule C gross receipts are at least what your 1099s add up to (then deduct fees and refunds as expenses). A mismatch is the most common reason freelancers get a CP2000 letter.",
 [IRS + "/individuals/understanding-your-cp2000-notice", IRS + "/forms-pubs/about-schedule-c-form-1040"],
 ["CP2000 from information-return mismatch"])

post("2027-03-05", "real-numbers", "filing", "From profit to tax bill",
 ["$60,000 profit →", "$12,037 tax", "here's every step"],
 """From Schedule C profit to the tax bill, every step. Single filer, 2026, $60,000 of profit, no other income:

1. Self-employment tax: $60,000 × 92.35% × 15.3% = $8,477
2. Half of that comes off income: $60,000 − $4,239 = $55,761 (AGI)
3. Standard deduction: $55,761 − $16,100 = $39,661
4. QBI deduction, 20%: about $7,932 → taxable income ≈ $31,729
5. Income tax on that: about $3,560
6. Total: $8,477 + $3,560 = $12,037, about 20% of profit

Then subtract what you paid in estimated tax for 2026. What's left is due April 15.

Notice which number is bigger: self-employment tax. That's why "I'm in the 12% bracket" undersells what freelancers owe.""",
 "$60K freelance profit, single, 2026: SE tax $8,477 + income tax ≈ $3,560 = $12,037 (≈20%). SE tax is the bigger piece, which is why \"I'm in the 12% bracket\" undersells it.",
 "For anyone wondering why freelance taxes are so high: on $60,000 of profit (single, 2026), self-employment tax is about $8,477 and income tax about $3,560, roughly $12,000 total. The self-employment part is usually the bigger one.",
 [IRS + "/forms-pubs/about-schedule-se-form-1040", IRS + "/forms-pubs/about-form-8995"],
 ["$60K single 2026 = $12,037 total", "SE $8,477; standard deduction $16,100"])

post("2027-03-09", "checklist", "deductions", "Deduction checklist, 2 minutes",
 ["2-minute check:", "18 yes/no questions", "your deduction list"],
 """A two-minute deduction check before you file. Tick each one that's true for 2026:

☐ Part of your home is used regularly and only for work
☐ You drove to clients or on business errands
☐ You used your phone or home internet for work
☐ You paid for software or subscriptions for work
☐ You bought equipment or furniture for work
☐ Clients paid through a platform that took fees
☐ You paid your own health insurance
☐ You paid for courses that build skills for your current work
☐ You paid other freelancers
☐ You traveled overnight for business
☐ You paid for business insurance, a website or ads

Each tick is a deduction with its own rules. The deduction finder turns your ticks into a list with the rule for each and where it goes on your return.""",
 "2-minute deduction check before filing: home office? business drives? phone/internet? software? equipment? platform fees? own health insurance? courses? contractors? business travel? insurance/website/ads? Each yes = a deduction with its own rules.",
 "Quick checklist before filing: home office, business drives, phone and internet share, software, equipment, platform fees, your own health insurance, courses for your current work, contractors, business travel, insurance, website and ads. Each one has its own rules, but it's easy to forget one.",
 [IRS + "/publications/p334"], ["(checklist; rules on the finder page)"], link="finder")

post("2027-03-16", "common-question", "q1", "Two payments on April 15?",
 ["Common question:", "Why 2 payments", "on April 15?"],
 """A common question from first-year freelancers: why do I owe two payments on April 15?

Because two different years meet on that day:
1. The balance due on your 2026 return. Whatever your 2026 tax is, minus what you paid during 2026.
2. The first estimated payment for 2027, covering January to March.

When you pay online, these are two separate payments with two different reasons: "balance due" for tax year 2026, and "estimated tax" (1040-ES) for tax year 2027. Mixing them up is how a payment ends up on the wrong year.

If this is your first year, the double hit is normal. From next year on, quarterly payments spread it out.""",
 "Why 2 IRS payments on Apr 15? 1) 2026 balance due (reason: balance due, tax year 2026). 2) Q1 2027 estimate (reason: estimated tax, 1040-ES, tax year 2027). Separate payments, separate years.",
 "For first-year freelancers surprised by April: you may owe the 2026 balance AND the first 2027 estimated payment on the same day. Pay them separately, choosing the right reason and tax year for each.",
 [IRS + "/payments/direct-pay", IRS + "/forms-pubs/about-form-1040-es"], ["Apr 15, 2027: 2026 balance + Q1 2027 estimate"])

post("2027-03-19", "worked-math", "q1", "Your Q1 2027 payment",
 ["Q1 2027:", "$12,037 ÷ 4", "= $3,010"],
 """Your first 2027 estimated payment, worked out from the return you just filed.

The safe harbor: pay 100% of your 2026 total tax over four on-time 2027 payments (110% if your 2026 AGI was over $150,000), and you generally avoid the underpayment penalty, however 2027 goes.

Example: 2026 total tax was $12,037.
$12,037 ÷ 4 = $3,009.25, so about $3,010 by April 15, June 15 and September 15, 2027, and January 18, 2028 (January 15 is a Saturday and the 17th is a holiday).

If 2027 income will clearly be lower, 90% of this year's tax can be the smaller target. If it'll be higher, the safe harbor still protects you from the penalty, but save the difference for next April.""",
 "Q1 2027 estimate from your 2026 return: total tax ÷ 4. $12,037 → ≈ $3,010 by Apr 15, Jun 15, Sep 15, 2027 and Jan 18, 2028. (110% if 2026 AGI > $150K.) Earning more in 2027? Still save the gap.",
 "Tip for working out your first 2027 estimated payment: take the total tax from your 2026 return and divide by four (use 110% of it if your AGI was over $150,000). Paying that by each deadline generally avoids the underpayment penalty.",
 [IRS + "/forms-pubs/about-form-1040-es"], ["Safe harbor 100%/110%", "Jan 18, 2028 Q4 date (Jan 15 Sat, Jan 17 MLK Day)"])

post("2027-03-23", "myth-vs-fact", "filing", "Extension myths",
 ["Extension myths", "Myth: more time to pay", "Fact: to file only"],
 """Tax extension myths, before April 15.

Myth: an extension gives you more time to pay.
Fact: it gives you until October 15 to file. Payment is still due April 15. Pay your best estimate of the 2026 balance by then, or interest and late-payment penalties apply.

Myth: you need a form or an accountant.
Fact: you can extend by paying through IRS Direct Pay or your online account and choosing "extension" as the reason. Or file Form 4868 free.

Myth: extensions look bad.
Fact: millions of people file one every year. A complete, correct return in May beats a rushed one in April.

Myth: the extension moves your Q1 2027 payment too.
Fact: it doesn't. That's still due April 15.""",
 "Extension myths: ❌ more time to pay (only to file, until Oct 15) ❌ needs a form (pay via Direct Pay, reason: extension) ❌ looks bad (common) ❌ moves the Q1 2027 payment (still due Apr 15).",
 "If you're thinking about an extension: it moves the filing deadline to October 15 but not the payment, so pay your best estimate by April 15. Paying through Direct Pay with 'extension' as the reason counts as the extension.",
 [IRS + "/forms-pubs/about-form-4868", IRS + "/payments/direct-pay"], ["Extension to Oct 15, 2027", "Payment with extension reason = automatic extension"])

post("2027-03-30", "countdown", "deductions", "Last-minute moves that still count for 2026",
 ["Still time for 2026:", "3 moves", "before you file"],
 """Already in 2027, and some moves still count for your 2026 taxes. Counting down to the biggest:

3. HSA contribution. If you had an HSA-eligible plan in 2026: up to $4,400 self-only or $8,750 family, until April 15.

2. IRA contribution. Traditional or Roth, for 2026, until April 15. A traditional IRA may be deductible, depending on income and other coverage.

1. SEP-IRA. Open and fund it until your filing deadline, including extensions: roughly 20% of net self-employment earnings. At $60,000 of profit, about $11,000.

All three lower income tax, not self-employment tax. And tell the provider the contribution is for 2026, not 2027.""",
 "Still counts for 2026: 3) HSA (until Apr 15; $4,400/$8,750) 2) IRA (until Apr 15) 1) SEP-IRA (until your filing deadline incl. extensions; ≈20% of net SE earnings). Tell the provider: \"for 2026\".",
 "Reminder that some contributions made now still count for 2026: HSA and IRA until April 15, and a SEP-IRA until your filing deadline including extensions. Make sure the provider records them as 2026 contributions.",
 [IRS + "/publications/p969", IRS + "/retirement-plans/plan-sponsor/simplified-employee-pension-plan-sep"],
 ["HSA 2026 limits $4,400/$8,750", "SEP by extended deadline"])

post("2027-04-02", "real-numbers", "q1", "April 15 for a first-year freelancer",
 ["First year:", "April 15 =", "$12,037 + $3,010"],
 """April 15 for a fictional first-year freelancer, Dev, who made no estimated payments in 2026 and had no job withholding.

2026 profit: $60,000. 2026 total tax: $12,037.
Paid during 2026: $0.

Payment 1, the 2026 balance: $12,037, plus a modest underpayment penalty (it works like interest on each missed quarter). If Dev owed no tax for 2025, there may be no penalty at all.
Payment 2, Q1 2027 estimate: $3,010 (the safe harbor: $12,037 ÷ 4).
Total due April 15: about $15,000+.

Dev can't pay it all? File on time anyway, pay what he can, and set up a payment plan online. And from now on, move a set percentage of every client payment into a tax account the day it arrives.""",
 "First-year freelancer, $60K profit, no 2026 payments: Apr 15 = 2026 balance $12,037 (+ a small penalty, unless 2025 tax was $0) + Q1 2027 estimate ≈ $3,010. Can't pay it all? File anyway, pay what you can, set up a plan.",
 "For anyone in their first freelance year who didn't pay quarterly: April 15 can mean last year's full balance plus the first estimated payment for this year. If it's more than you can pay, file on time anyway and set up a payment plan online.",
 [IRS + "/payments/payment-plans-installment-agreements", IRS + "/forms-pubs/about-form-2210"],
 ["$12,037 / $3,010 example", "No penalty if prior-year tax was zero (full-year, citizen/resident)"])

post("2027-04-06", "checklist", "q1", "The April 15 checklist",
 ["April 15:", "the 5-item list", "file, pay, pay"],
 """The April 15, 2027 checklist for freelancers:

☐ File your 2026 return, or extend (Form 4868, or a Direct Pay payment marked "extension").
☐ Pay the 2026 balance. Direct Pay → "balance due" → tax year 2026.
☐ Pay the first 2027 estimate. Direct Pay → "estimated tax" → 1040-ES → tax year 2027.
☐ Make any last 2026 IRA or HSA contributions, marked for 2026.
☐ Check your state: most states with an income tax have their own return and a Q1 estimate on or near the same day.

Save every confirmation number in one folder. Then set your 2027 set-aside percentage from your real 2026 numbers: total tax ÷ profit.""",
 "Apr 15, 2027 freelancer checklist: ☐ file or extend ☐ pay 2026 balance (tax year 2026) ☐ pay Q1 2027 estimate (1040-ES, tax year 2027) ☐ last 2026 IRA/HSA ☐ state return + state Q1. Save confirmations.",
 "April 15 checklist for anyone self-employed: file or extend, pay the 2026 balance, pay the first 2027 estimate (different reason and tax year), make any last 2026 IRA or HSA contributions, and check your state's dates.",
 [IRS + "/payments/direct-pay", IRS + "/forms-pubs/about-form-4868"], ["Apr 15, 2027 deadlines"])

post("2027-04-09", "common-question", "filing", "Can't pay by April 15?",
 ["Common question:", "Can't pay it all?", "file anyway"],
 """A common question this week: what if I can't pay my whole tax bill by April 15?

File on time anyway. The penalty for filing late is about 5% of the unpaid tax per month; for paying late it's 0.5% a month, plus interest. Filing is the cheap part.

Then:
- Pay what you can by April 15. Interest and penalties are figured on what's unpaid.
- If you can clear it within 180 days, a short-term plan is usually available online with no setup fee.
- If not, individuals owing up to $50,000 can generally set up a monthly installment plan online. There's a setup fee, lower with direct debit.

Ignore anyone offering to settle your debt "for pennies on the dollar" over the phone. And raise your set-aside for 2027.""",
 "Can't pay your full tax bill? FILE ON TIME anyway: failure to file ≈ 5%/month vs failure to pay 0.5%/month. Pay what you can, then a short-term (≤180 days) or monthly plan online. Ignore \"pennies on the dollar\" calls.",
 "If you owe more than you can pay this year: still file on time (the late-filing penalty is about ten times the late-payment one), pay what you can, and set up a payment plan on irs.gov. Be wary of anyone calling offering to settle tax debt cheaply.",
 [IRS + "/payments/payment-plans-installment-agreements", IRS + "/payments/failure-to-file-penalty"],
 ["FTF 5%/mo, FTP 0.5%/mo", "Short-term 180 days", "Online installment up to $50K"])

post("2027-04-14", "worked-math", "q1", "Tomorrow: your set-aside for 2027",
 ["Tomorrow: April 15", "your 2027 rate:", "tax ÷ profit"],
 """April 15 is tomorrow. Once the payments are made, one more number is worth two minutes: your real tax rate for 2026.

Total tax (Form 1040) ÷ Schedule C profit = your rate.

Example: $12,037 ÷ $60,000 = 20.1%.

Add your state's rate if it has an income tax, round up, and that's the percentage to move into your tax account from every 2027 client payment. For this example in a state with a 5% tax: about 25%.

If 2027 will look different (a big new client, a lost one, a move), adjust it at each quarterly payment. The point isn't precision; it's never meeting April without the money already set aside.""",
 "After you pay tomorrow: your 2027 set-aside = 2026 total tax ÷ Schedule C profit, + state rate, rounded up. $12,037 ÷ $60,000 = 20% → ~25% with a 5% state tax. Move it from every payment.",
 "Once the April payments are done: divide your 2026 total tax by your Schedule C profit and add your state rate. That's a good percentage to set aside from every payment this year.",
 [IRS + "/forms-pubs/about-form-1040-es"], ["$12,037 / $60,000 = 20.1%"])


def build():
    out = []
    for i, p in enumerate(P, 1):
        out.append({**p, "n": i, "card_file": f"cards/season-{i:02d}.png",
                    "linkedin": p["linkedin"] + "\n\n" + LINKS[p["link"]] + "\n\n" + NTA})
    (HERE / "posts.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    md = ["# 1099 Money: tax-season posts (Jan 19 – Apr 14, 2027)", "",
          f"{len(out)} text posts, the follow-on to `../q4/`, for the platforms the video calendar, pins and newsletter",
          "don't cover. Each has three versions, ready to paste:", "",
          "- **LinkedIn** (long, link at the end).",
          "- **Threads / X** (short, fits one X post; put the link in a reply or your profile).",
          "- **Facebook groups** (no link, no brand, help first; check each group's rules).", "",
          "Formats rotate so no two posts in a row share a structure: " + ", ".join(sorted({p['format'] for p in out})) + ".",
          "Cards (1080×1080) are in `cards/`. Post on the date, 8–10am Eastern. 2026 federal figures: check `claims` first.", "",
          "Rebuild: `python3 launch/1099-money/tax-season/build_season.py && node launch/1099-money/q4/render_cards.mjs tax-season`.", ""]
    for p in out:
        md += [f"## {p['n']}. {p['date']} · {p['title']} ({p['format']})", "", f"Card: `{p['card_file']}` ({' / '.join(p['card'])})", "",
               "**LinkedIn**", "", "```", p["linkedin"], "```", "", "**Threads / X**", "", "```", p["short"], "```", "",
               "**Facebook groups**", "", "```", p["facebook"], "```", "",
               "Sources: " + ", ".join(p["sources"]), "", "Check before posting: " + "; ".join(p["claims"]), ""]
    (HERE / "POSTS.md").write_text("\n".join(md))
    return out


if __name__ == "__main__":
    print(len(build()), "posts")
