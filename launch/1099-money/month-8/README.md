# 1099 Money month 8: Mon Jul 19 – Wed Aug 18, 2027

Starts the Monday after the couples week (Jul 12–18). 22 Shorts, 14 carousels and 4 Sunday long videos fill every day
with the brand's default slots (Shorts Mon/Tue/Thu/Fri/Sat, carousels Mon/Wed/Fri, longs Sun). Every long video carries
a worked-example chart, so none of them wait on footage.

| Week | Theme | Sunday long |
|---|---|---|
| Jul 19–25 | Mortgages for freelancers | Jul 25 · Getting a mortgage as a freelancer: what lenders see on your tax return |
| Jul 26–Aug 1 | Foreign clients and working abroad | Aug 1 · Foreign clients and working abroad: how a US freelancer's taxes work |
| Aug 2–8 | Roth vs traditional IRA | Aug 8 · Roth IRA or traditional IRA? Three freelancers, real numbers |
| Aug 9–18 | The Sep 15 payment | Aug 15 · The September 15 tax payment, worked out for three freelancers |

## Figures (2026 federal, single, no other income, from `apps/freelance-tax/lib/tax.js`)

| Example (fictional) | Result |
|---|---|
| Sep 15 payment, $40K / $75K / $120K profit | total tax $7,427 / $15,495 / $28,462 → a quarter: $1,857 / $3,874 / $7,115 |
| $7,500 traditional IRA at $35K / $60K / $100K profit | saves $615 / $720 / $1,320 (the QBI deduction shrinks too) |
| Priya, $60K profit, half from foreign clients | $12,037 living in the US; $8,478 of SE tax still due abroad with the exclusion |
| Alex's mortgage income | ($48,000 + $62,000) ÷ 2 = $55,000 a year, ≈ $4,583 a month, on $85,000 billed |
| June payment 92 days late | $3,874 × 7% × 92 ÷ 365 ≈ $68 (check the current IRS rate) |

## Check before posting

- **2027 limits.** The scripts use 2026 IRA ($7,500), 401(k) ($24,500) and Roth phase-out ($153K single, $242K joint)
  figures. The IRS publishes 2027 limits around October–November 2026; check irs.gov and update the Roth and IRA scripts if they changed.
- **Q4 date.** Jan 15, 2028 is a Saturday and Jan 17 is Martin Luther King Jr. Day, so the scripts say Tue Jan 18, 2028.
  Confirm against the 2027 Form 1040-ES.
- **Mortgage rules** come from Fannie Mae's Selling Guide (B3-3.2-01) and Form 1084; the scripts say lender rules vary.
- **Interest rate.** The IRS underpayment rate changes quarterly; recheck the 7% before Aug 14.

Export:

```
factory pack export --brand 1099-money --file launch/1099-money/month-8/content.json --start 2027-07-19 --days 31 --out <dir>
```
