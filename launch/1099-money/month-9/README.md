# 1099 Money month 9: Thu Aug 19 – Sat Sep 18, 2027

Follows month 8 (ends Wed Aug 18). It has 23 Shorts, 13 carousels and 4 Sunday long videos, and fills every day using the brand's
default slots. Every long video carries a worked-example chart, so none of them wait on footage.

| Dates | Theme | Sunday long |
|---|---|---|
| Aug 19–21 | HSAs (bronze plans are HSA-eligible from 2026) | Aug 22 · HSA for freelancers: the triple tax break, with three real examples |
| Aug 23–28 | Quitting a job to freelance | Aug 29 · Quitting your job to freelance: the numbers to run first |
| Aug 30–Sep 4 | Creator taxes | Sep 5 · Creator taxes: brand deals, gifted products and the gear you can deduct |
| Sep 6–11 | Sep 15 run-up and emergency funds | Sep 12 · How big should a freelancer's emergency fund be? Three real examples |
| Sep 13–18 | Sep 15 (the "Tomorrow" Short lands on Sep 14), what's next, and year-end planning | none |

## Figures

The tax figures are 2026 federal, for a single filer with no other income, from `apps/freelance-tax/lib/tax.js`.

| Example (fictional) | Result |
|---|---|
| $4,400 HSA at $35K / $60K / $100K profit | saves $367 / $422 / $774 (family $8,750: $715 / $840 / $1,540) |
| Morgan, $70K salary | $58,075 kept after federal income tax ($6,570) and payroll tax ($5,355) |
| Profit to match Morgan's salary | $73,150 for taxes alone; $82,920 after $6,000 of health premiums (deducted) and a $2,100 match |
| Revenue and rate for Morgan | $87,920 of revenue with $5,000 of costs → about $88/hour at 1,000 billable hours |
| Remy, creator | $38K in − $9K costs = $29K profit → $4,966 federal (SE $4,098, income tax $868), about $1,240 a quarter |
| Emergency fund at $3,500 a month | 6 / 9 / 12 months = $21,000 / $31,500 / $42,000 |

## Check before posting

- **HSA limits.** The scripts use the 2026 figures ($4,400 / $8,750, $1,000 catch-up). Add the 2027 figures from irs.gov.
- **Dates.** Q4 2027 is due Tue Jan 18, 2028: Jan 15 is a Saturday and Jan 17 is MLK Day. The 2027 return is due Tue Apr 18, 2028: Apr 15 is a Saturday and DC Emancipation Day is observed Mon Apr 17. Confirm both on irs.gov.
- **Open enrollment.** 2028 coverage opens Nov 1. Check healthcare.gov for the end date, which can differ by state.
- **Gifted products.** The scripts say products received in exchange for content are generally income at fair market value (Pub 525), and that unsolicited items are less clear.

Export:

```
factory pack export --brand 1099-money --file launch/1099-money/month-9/content.json --start 2027-08-19 --days 31 --out <dir>
```
