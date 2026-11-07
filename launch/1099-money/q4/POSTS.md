# 1099 Money: Q4 and year-end posts (Nov 20, 2026 – Jan 15, 2027)

15 text posts for the platforms the video calendar doesn't cover. Each has three versions, ready to paste:

- **LinkedIn** (long, with the calculator link at the end; LinkedIn allows it).
- **Threads / X** (short; put the link in a reply or your profile, not the post).
- **Facebook groups** (no link, no brand, help first; check each group's rules, and only post where
  self-promotion rules allow even a mention).

Each post has a square card in `cards/` (1080×1080) to attach on LinkedIn and Threads.
Post on the date, 8–10am Eastern. Every figure is 2026 federal; check `claims` against the sources first.
This is a separate stream from the newsletter (`channels/config.json`) and the Shorts, so there's
some topic overlap by design; the wording is new.

Rebuild after edits: `python3 launch/1099-money/q4/build_q4.py && node launch/1099-money/q4/render_cards.mjs`.

## 1. 2026-11-20 · Your 4th payment covers 4 months

Card: `cards/q4-01.png` (The Jan 15 payment / covers Sep → Dec / the biggest quarter)

**LinkedIn**

```
The quarterly tax "quarters" aren't quarters.

For 2026 income, US freelancers pay estimated tax on:
- April 15 for January to March (3 months)
- June 15 for April and May (2 months)
- September 15 for June to August (3 months)
- January 15, 2027 for September to December (4 months)

That last one covers a third of the year, and it lands right after the holidays, often in a slow month.

If your income picked up this fall, the January payment may be your biggest. Two things to do this week:
1. Add up your profit since September 1.
2. Check your tax savings account against it.

Eight weeks is plenty of time to fill a gap. Two days isn't.

January 15 calculator (link in profile): 1099money.netlify.app/q4/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
The "quarterly" tax periods are 3, 2, 3 and 4 months. The Jan 15, 2027 payment covers Sep–Dec 2026: a third of the year, due right after the holidays. Check your tax savings against your fall income now, not on Jan 14.
```

**Facebook groups**

```
Reminder for anyone paying quarterly: the January 15 payment covers September through December, four months, not three. If fall was busy, it may be your biggest payment. Worth checking your savings against it now while there's time.
```

Sources: https://www.irs.gov/businesses/small-businesses-self-employed/estimated-taxes

Check before posting: Periods: Jan-Mar, Apr-May, Jun-Aug, Sep-Dec; Q4 2026 payment due Jan 15, 2027

## 2. 2026-11-24 · Work out your Jan 15 number

Card: `cards/q4-02.png` (Jan 15 number: / smaller of 2 tests / 100% of 2025 · 90% of 2026)

**LinkedIn**

```
How much should your January 15 payment be? There are two tests, and you only need to meet the smaller one.

Test 1, the safe harbor: by January 15, your 2026 estimated payments add up to 100% of your 2025 total tax (110% if your 2025 AGI was over $150,000).

Test 2: they add up to 90% of your 2026 tax.

Example: 2025 total tax was $6,500. You've paid $4,875 so far this year (three payments of $1,625). The safe harbor needs $6,500 by January 15, so the last payment is $1,625, even if 2026 profit is $60,000 and the full bill is about $12,000. The rest is due in April.

If you missed a payment, January's amount includes the catch-up. Pay it now, because the penalty keeps growing until the shortfall is paid.

January 15 calculator (link in profile): 1099money.netlify.app/q4/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Jan 15 payment = whatever brings your 2026 payments up to the SMALLER of: 100% of 2025's total tax (110% if 2025 AGI > $150K), or 90% of 2026's tax. Already on track? It's one quarter's worth. Behind? It includes the catch-up.
```

**Facebook groups**

```
If you're working out your January 15 payment: you need your 2026 payments to reach the smaller of 100% of last year's total tax (110% if your AGI was over $150K) or 90% of this year's tax. Last year's number is on your 2025 Form 1040, total tax line.
```

Sources: https://www.irs.gov/forms-pubs/about-form-1040-es, https://www.irs.gov/forms-pubs/about-form-2210

Check before posting: Safe harbor 100%/110% over $150K AGI; 90% current-year test; Example: $6,500 prior-year tax, $4,875 paid -> $1,625

## 3. 2026-11-27 · The Black Friday write-off math

Card: `cards/q4-03.png` ($1,000 laptop / saves ≈ $230 / still costs $770)

**LinkedIn**

```
Black Friday, and someone will tell you to "buy it for the write-off."

The math at $60,000 of freelance profit (single, 2026):
- A $1,000 business purchase lowers income tax and self-employment tax.
- Together that's roughly 23 cents per dollar.
- So the $1,000 laptop saves about $230 in federal tax.
- You're still out $770.

A deduction is a discount, not a refund. If you didn't need the laptop, you're just poorer.

The real year-end move: if you were going to buy it in January anyway, buying it and starting to use it for work before December 31 moves the deduction into 2026. Same purchase, tax savings a year earlier.

Keep the receipt and note what share is business use.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Black Friday "write-off" math at $60K profit: a $1,000 laptop saves ≈ $230 of federal tax. You're still out $770. Only worth it if you needed it anyway, then buy before Dec 31 to pull the deduction into 2026.
```

**Facebook groups**

```
Quick reality check on Black Friday "write-offs": at a typical freelance income, a $1,000 business purchase saves roughly $230 in federal tax. It's a discount, not free. If you were going to buy it in January anyway, buying before Dec 31 does move the deduction into this year.
```

Sources: https://www.irs.gov/publications/p946, https://www.irs.gov/publications/p334

Check before posting: Marginal saving ≈ 23% at $60K single (12% income tax after QBI + SE tax); Placed in service by Dec 31 for 2026 deduction

## 4. 2026-12-01 · Equipment before Dec 31: the 3 rules

Card: `cards/q4-04.png` (Buying gear in Dec? / In use by Dec 31 / ≤ $2,500/item: expense it)

**LinkedIn**

```
Buying equipment for your freelance business this month? Three rules decide whether it counts for 2026.

1. It has to be in use by December 31. "Placed in service" means set up and used for work, not just ordered. A laptop delivered January 3 is a 2027 deduction.

2. Small items can be expensed right away. With the de minimis safe harbor election on your return, items up to $2,500 each are deducted in full this year.

3. Bigger items can usually be written off in one year too, through Section 179 or bonus depreciation, which is back at 100% for property acquired after January 19, 2025.

And one limit on all of it: only the business-use share counts. A camera used 70% for client work is a 70% deduction.

Need it? Buy it, set it up, and keep the receipt with a note on what it's for. Don't need it? Keep the money.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Buying gear for the business in December? It must be set up and in use by Dec 31 to count for 2026. Up to $2,500 per item: expense it (de minimis election). Bigger: usually Section 179 or 100% bonus depreciation. Business-use share only.
```

**Facebook groups**

```
For anyone buying work equipment this month: it has to be delivered and in use by December 31 to count for 2026, not just ordered. Items up to $2,500 each can usually be deducted right away. Only the business-use share counts.
```

Sources: https://www.irs.gov/publications/p946, https://www.irs.gov/businesses/small-businesses-self-employed/tangible-property-final-regulations

Check before posting: Placed-in-service rule; De minimis safe harbor $2,500 per item/invoice (no AFS); 100% bonus depreciation restored for property acquired after Jan 19, 2025 (OBBBA)

## 5. 2026-12-04 · SEP-IRA or Solo 401(k)?

Card: `cards/q4-05.png` (SEP-IRA or Solo 401(k)? / SEP: simple / Solo 401(k): more at lower incomes)

**LinkedIn**

```
SEP-IRA or Solo 401(k)? Both let a self-employed person save a lot for retirement and cut income tax. The difference shows up at moderate incomes.

SEP-IRA:
- Only "employer" contributions: roughly 20% of net self-employment earnings.
- At $60,000 of profit, that's about $11,000.
- Easiest to open, and you can open and fund it as late as your filing deadline, including extensions.

Solo 401(k) (no employees except a spouse):
- You contribute as the employee (up to $24,500 for 2026, more if you're 50+) plus the same ~20% as the employer.
- At $60,000 of profit, that's potentially $35,000+, not $11,000.
- More paperwork, and once assets pass $250,000 there's an annual Form 5500-EZ.

Rule of thumb: want to save less than ~20% of profit? A SEP is simpler. Want to save more? Look at a Solo 401(k), and ask your provider about its setup deadline now, before the holidays.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
SEP-IRA vs Solo 401(k) at $60K profit: SEP ≈ $11K max (≈20% of net SE earnings), can be opened up to your filing deadline. Solo 401(k): employee deferral (up to $24,500 for 2026) + the same employer share. More room, more paperwork.
```

**Facebook groups**

```
Comparing SEP-IRA vs Solo 401(k)? Short version: a SEP is simplest and can be opened up to your filing deadline, but it's capped at roughly 20% of net self-employment earnings. A Solo 401(k) adds an employee contribution on top, so it allows much more at moderate incomes. Ask the provider about setup deadlines before year end.
```

Sources: https://www.irs.gov/retirement-plans/plan-sponsor/simplified-employee-pension-plan-sep, https://www.irs.gov/retirement-plans/one-participant-401k-plans, https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-401k-and-profit-sharing-plan-contribution-limits

Check before posting: 2026 401(k) elective deferral limit $24,500; SEP ≈ 20% of net SE earnings for sole props; $60K profit -> ≈ $11,150; 5500-EZ over $250K assets; SEP can be established by filing deadline incl. extensions

## 6. 2026-12-08 · Year-end deduction checklist

Card: `cards/q4-06.png` (Before Dec 31: / 5 deduction checks / cash method = paid by 12/31)

**LinkedIn**

```
On the cash method (most freelancers), an expense counts in the year you pay it. So December 31 is a real line. Five checks before then:

1. Mileage: add up your 2026 log now, while you can still rebuild a missing week from your calendar. 72.5 cents a business mile to June 30, 76 cents from July 1.
2. Software and subscriptions: renewals you'd pay in January anyway can be paid in December.
3. Phone and internet: work out your business-use percentage and write down how you got it.
4. Home office: measure the space and photo it. $5 a square foot up to 300 square feet with the simplified method.
5. Retirement and health: if you pay your own health insurance, those premiums may be deductible. A SEP can wait until you file; some other plans can't.

Not on the list: buying things you don't need. A deduction saves a fraction of what you spend.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Year-end, cash-method freelancers: expenses count when PAID. Before Dec 31: total your mileage log (72.5¢/mi to Jun 30, 76¢ after), prepay renewals you'd pay in Jan anyway, set your phone/internet business %, measure the home office. Don't buy stuff you don't need.
```

**Facebook groups**

```
Year-end checklist worth ten minutes: total the mileage log while you can still fill gaps from your calendar, pay any business renewals due early January before the 31st, write down your phone/internet business percentage, and measure and photograph your home office space.
```

Sources: https://www.irs.gov/publications/p334, https://www.irs.gov/tax-professionals/standard-mileage-rates, https://www.irs.gov/businesses/small-businesses-self-employed/home-office-deduction

Check before posting: Cash method: deduct when paid; Prepaid expenses within the 12-month rule; 2026 mileage 72.5¢ Jan–Jun, 76¢ Jul–Dec; Simplified home office $5/sq ft up to 300 sq ft

## 7. 2026-12-11 · Retirement deadlines: what can wait

Card: `cards/q4-07.png` (Retirement for 2026: / IRA & SEP can wait / check 401(k) timing now)

**LinkedIn**

```
Which retirement moves for 2026 have to happen by December 31, and which can wait until you file?

Can wait until April 15, 2027:
- Traditional or Roth IRA contributions for 2026.
- An HSA contribution for 2026, if you had an HSA-eligible health plan.

Can wait until your filing deadline, including extensions:
- Opening and funding a SEP-IRA for 2026.

Check now:
- A Solo 401(k). If you already have one and want to make employee contributions for 2026, your provider may need your election by December 31. If you're opening a new one, the rules for setting it up after year end changed recently, and providers handle them differently. Ask yours this week.

The rest can wait for your return. December's job is just making sure nothing with a hard deadline slips.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
2026 retirement deadlines: IRA and HSA → Apr 15, 2027. SEP-IRA → filing deadline incl. extensions. Solo 401(k) employee contributions → ask your provider NOW; elections or setup may need to happen by Dec 31.
```

**Facebook groups**

```
Sorting out retirement contributions for 2026: IRA and HSA contributions can wait until April 15, 2027, and a SEP-IRA until you file (extensions included). If you have or want a Solo 401(k), ask the provider about their deadlines this week, because some need paperwork by December 31.
```

Sources: https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-ira-contribution-limits, https://www.irs.gov/retirement-plans/one-participant-401k-plans, https://www.irs.gov/publications/p969

Check before posting: IRA/HSA prior-year contributions until April 15; SEP by filing deadline incl. extensions; Solo 401(k) deferral election timing varies by provider; SECURE 2.0 first-year rule

## 8. 2026-12-15 · Health insurance deadline today

Card: `cards/q4-08.png` (Dec 15: / last day for Jan 1 coverage / premiums may be deductible)

**LinkedIn**

```
For freelancers buying their own health insurance: today, December 15, is the last day to enroll on HealthCare.gov for coverage starting January 1. Some states that run their own marketplace have later dates, so check yours.

Two tax notes while you're choosing:
1. Premiums you pay as a self-employed person, for you, your spouse and dependents, are generally deductible as the self-employed health insurance deduction (Form 7206), as long as you weren't eligible for an employer plan. It lowers income tax, not self-employment tax.
2. Your subsidy is based on the income you estimate now. Freelance income is hard to guess, so update the estimate during the year when it changes, or you may repay part of it when you file.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Dec 15: last day on HealthCare.gov for coverage from Jan 1 (state marketplaces vary). Self-employed? Premiums are generally deductible (Form 7206) if you weren't eligible for an employer plan. Update your income estimate when it changes.
```

**Facebook groups**

```
Reminder for anyone buying their own health insurance: December 15 is the last day on HealthCare.gov for coverage starting January 1 (some state marketplaces run later). If you're self-employed, the premiums are generally deductible.
```

Sources: https://www.healthcare.gov/quick-guide/dates-and-deadlines/, https://www.irs.gov/forms-pubs/about-form-7206

Check before posting: Dec 15 deadline for Jan 1 coverage on HealthCare.gov; SE health insurance deduction via Form 7206, not available if eligible for employer plan

## 9. 2026-12-18 · Late-December invoices and the cash method

Card: `cards/q4-09.png` (Paid Jan 2? / It's 2027 income / cash method)

**LinkedIn**

```
A question that comes up every December: if a client pays my December invoice on January 2, which year is it?

On the cash method, which most freelancers use, income counts when you receive it. Paid January 2, 2027? It's 2027 income, even though you did the work and sent the invoice in 2026.

Two things follow:
- Your client may still put it on your 2026 1099 if they count it by invoice date. If so, ask them for a corrected form, and keep the bank record that shows when it arrived.
- "Received" includes money that's available to you. A check that arrived December 30 and sat in a drawer is 2026 income.

This isn't a reason to stall clients' payments. It's just the rule your books and 1099s need to match.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Cash-method freelancers: income counts when RECEIVED. Client pays your Dec invoice on Jan 2? It's 2027 income. A check that arrived Dec 30 but wasn't deposited? 2026. If a 1099 says otherwise, ask for a correction.
```

**Facebook groups**

```
For anyone with invoices outstanding at year end: on the cash method, income counts in the year you receive it. A December invoice paid January 2 is next year's income. If a client's 1099 puts it in the wrong year, ask for a corrected form.
```

Sources: https://www.irs.gov/publications/p538

Check before posting: Cash method: income when actually or constructively received; Constructive receipt: check received Dec 30

## 10. 2026-12-22 · Write down 5 numbers on Dec 31

Card: `cards/q4-10.png` (Dec 31: / write down 5 numbers / your 2026 in one note)

**LinkedIn**

```
The most useful 10 minutes of the freelance year: on December 31, write down five numbers.

1. Total income received in 2026.
2. Total business expenses.
3. Profit (1 minus 2).
4. Estimated tax paid so far for 2026.
5. What's in your tax savings account.

With those, you can:
- work out the January 15 payment in a minute,
- see whether April will be a bill or a refund,
- set your 2027 set-aside percentage from real numbers,
- and hand your preparer a clean starting point.

If one of them is hard to find, that's the thing to fix in 2027.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Dec 31, write down 5 numbers: 2026 income, expenses, profit, estimated tax paid, tax savings balance. That's your Jan 15 payment, your April preview and your 2027 set-aside rate, all in one note.
```

**Facebook groups**

```
One habit worth starting: on Dec 31, write down your income, expenses, profit, estimated tax paid, and what's in your tax savings. It makes the January payment and the April return much less stressful.
```

Sources: https://www.irs.gov/businesses/small-businesses-self-employed/recordkeeping

Check before posting: (habit, no numeric claims)

## 11. 2026-12-29 · Skip Jan 15 by filing early?

Card: `cards/q4-11.png` (Skip Jan 15? / Only if you file + pay / by Feb 1, 2027)

**LinkedIn**

```
There is a legal way to skip the January 15 payment: file your 2026 return and pay the whole balance by February 1, 2027 (January 31 is a Sunday).

When it works:
- Your books are closed, every 1099 has arrived and nothing's likely to change.
- You'd rather do the return once than pay an estimate and then the rest in April.

When it doesn't:
- Some 1099s arrive at the very end of January, and corrected ones later. Filing before they arrive risks an amended return.
- It removes the penalty for the fourth quarter only. If you underpaid in April, June or September, that penalty still applies.

For most freelancers, paying on January 15 and filing calmly in February or March is the lower-stress option.

January 15 calculator (link in profile): 1099money.netlify.app/q4/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
You can skip the Jan 15 payment if you FILE your 2026 return and PAY everything by Feb 1, 2027. It only covers Q4's penalty, and 1099s can arrive late, so for most people paying Jan 15 is calmer.
```

**Facebook groups**

```
Someone asked about skipping the January estimated payment: you can, if you file your 2026 return and pay the full balance by February 1, 2027. It doesn't fix underpayments from earlier in the year, and late 1099s can force an amendment, so it suits people with simple, finished books.
```

Sources: https://www.irs.gov/forms-pubs/about-form-1040-es

Check before posting: File and pay by Feb 1, 2027 instead of Jan 15 payment (Jan 31 Sunday); Only relieves Q4 penalty

## 12. 2027-01-05 · How to read a 1099-NEC

Card: `cards/q4-12.png` (Your 1099-NEC: / Box 1 = what they paid / check it against your log)

**LinkedIn**

```
1099-NECs start arriving this month (clients must send them by February 1, 2027). How to read one in a minute:

- Payer: the client's name and taxpayer ID.
- Recipient: your name and the ID you gave them (SSN or EIN). Check it's right.
- Box 1, nonemployee compensation: what they paid you in 2026. This is the number to check.
- Box 4, federal income tax withheld: usually empty. If not, it counts as tax you've paid.
- State boxes: only if they withheld state tax.

Two 2026 changes: clients only have to send one if they paid you $2,000 or more (it was $600). And no form doesn't mean no tax: all your income goes on Schedule C, form or not.

Check Box 1 against your own income log. If it's wrong, ask for a corrected form.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Reading a 1099-NEC: Box 1 = what the client paid you in 2026. Box 4 = federal tax withheld (usually blank). Check your name/ID. For 2026 payments, clients only must send one at $2,000+, but ALL income is taxable, form or not.
```

**Facebook groups**

```
For anyone getting 1099-NECs this month: Box 1 is what the client says they paid you in 2026, so check it against your own records. For 2026 payments the threshold for clients to send one went up to $2,000, but income without a form is still taxable.
```

Sources: https://www.irs.gov/forms-pubs/about-form-1099-nec

Check before posting: 1099-NEC due to recipients by Feb 1, 2027 (Jan 31 Sunday); Threshold $2,000 for payments made in 2026; Box 1 / Box 4 meanings

## 13. 2027-01-08 · How to read a 1099-K

Card: `cards/q4-13.png` (Your 1099-K: / gross, not profit / fees & refunds are on you)

**LinkedIn**

```
A 1099-K from a payment app or marketplace often looks too high. That's usually because of what it counts.

- Box 1a is the gross amount of payments processed for you, before fees, refunds and chargebacks.
- Boxes 5a to 5l split it by month, handy for checking against your records.
- Platforms must send one when payments top $20,000 and 200 transactions. Many send them below that anyway.

How to report it:
1. Put your real gross receipts on Schedule C. It should be at least what the 1099-K shows, unless part of it isn't business income.
2. Deduct the platform's fees and any refunds as business expenses.
3. If it includes personal money (friends paying you back, or personal items you sold at a loss), keep records and follow the IRS 1099-K guidance on reporting it, rather than just leaving it off.

Don't type in only your net payout. The IRS matches the gross.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
1099-K Box 1a is GROSS (before fees and refunds). Report gross on Schedule C, then deduct fees and refunds. Required at $20K + 200 payments, but often sent below that. Personal money in it? Keep records; see the IRS 1099-K page.
```

**Facebook groups**

```
If your 1099-K looks higher than what you received: Box 1a is the gross before fees and refunds. Report the gross and deduct the fees and refunds as expenses, rather than entering the net. The IRS page on understanding the 1099-K covers personal payments mixed in.
```

Sources: https://www.irs.gov/businesses/understanding-your-form-1099-k

Check before posting: Box 1a gross; 5a-5l monthly; Threshold $20,000 and 200 transactions; Personal items sold at a loss reporting per IRS guidance

## 14. 2027-01-12 · When a 1099 doesn't match your books

Card: `cards/q4-14.png` (1099 ≠ your books? / 3 normal reasons / 1 to fix)

**LinkedIn**

```
Your 1099s won't always add up to your bank deposits. Three normal reasons, and one that needs fixing.

Normal:
1. Fees. A 1099-K shows gross; your bank shows the payout after fees.
2. Clients below the threshold. No form, but still income, so your total should be higher than the forms.
3. Timing. A client who paid by card through a platform may show up on the platform's 1099-K, not the client's 1099-NEC. Count it once.

Needs fixing:
4. A wrong amount or year on a form, like a January 2027 payment counted as 2026. Ask the client for a corrected form now. If they won't, report the right amount and keep the records that show why.

Your own income log is the source of truth. The forms are what the IRS will compare it with.

Free quarterly tax calculator (link in profile): 1099money.netlify.app/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
1099s ≠ bank deposits? Normal: fees (1099-K is gross), clients under the threshold (no form, still income), the same payment on a 1099-K instead of a 1099-NEC (count once). Fix: wrong amount or year → ask for a corrected form.
```

**Facebook groups**

```
Tip if your 1099s don't match your bank deposits: fees, clients who didn't send a form, and card payments that show on a platform's 1099-K instead of the client's 1099-NEC are all normal. A wrong amount or wrong year is worth asking the client to correct.
```

Sources: https://www.irs.gov/businesses/understanding-your-form-1099-k, https://www.irs.gov/forms-pubs/about-form-1099-nec

Check before posting: Card/platform payments reported on 1099-K not 1099-NEC; Corrected 1099 process

## 15. 2027-01-14 · Tomorrow: the Jan 15 payment

Card: `cards/q4-15.png` (Due tomorrow: / Q4 estimated tax / pick tax year 2026)

**LinkedIn**

```
The 4th estimated payment for 2026 is due tomorrow, Friday, January 15, 2027.

The free way to pay, in about five minutes:
1. irs.gov/payments → IRS Direct Pay, or your IRS online account.
2. Reason: Estimated Tax. Form: 1040-ES.
3. Tax year: 2026. Not 2027. This is the mistake that makes it look like you skipped a quarter.
4. Save the confirmation number with your tax records.

Not sure of the amount? It's whatever brings your 2026 payments up to 100% of your 2025 total tax (110% if your 2025 AGI was over $150,000) or 90% of your 2026 tax, whichever is smaller.

And check your state: most with an income tax have a January payment too.

Can't pay it all? Pay what you can tomorrow. The penalty is figured on what's late, for as long as it's late.

January 15 calculator (link in profile): 1099money.netlify.app/q4/

Educational, not tax advice. 2026 federal figures.
```

**Threads / X**

```
Due tomorrow (Fri Jan 15): the 4th estimated payment for 2026. irs.gov/payments → Direct Pay → Estimated Tax → 1040-ES → tax year 2026 (not 2027!). Save the confirmation. Can't pay it all? Pay what you can.
```

**Facebook groups**

```
Reminder: the last estimated payment for 2026 is due tomorrow, Friday January 15. If you pay through IRS Direct Pay, choose tax year 2026, not 2027. And if you can't pay the whole amount, paying part of it still cuts the penalty.
```

Sources: https://www.irs.gov/payments/direct-pay, https://www.irs.gov/payments

Check before posting: Jan 15, 2027 is a Friday; Direct Pay options and tax year selection
