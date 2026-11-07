# 1099 Money for couples: one W-2 spouse, one freelancer

A mini-pack for married couples where one spouse has a W-2 job and the other freelances (files Schedule C).
**Couples week: Mon Jul 12 – Sun Jul 18, 2027**, right after month 7 and the 6-week YouTube plan. Month 8 starts Jul 19.

`content.json`: 6 Shorts, 3 carousels and one 8-minute long video (with a chart drawn from its numbers).

| Date | Format | Title |
|---|---|---|
| Mon Jul 12 | Short | My spouse has a W-2 job. Do I still pay quarterly? |
| Mon Jul 12 | Carousel | W-2 + freelancer couple: the tax plan in 6 steps |
| Tue Jul 13 | Short | Married to a W-2 earner? Your tax rate is higher |
| Wed Jul 14 | Short | Cover freelance tax from your spouse's paycheck |
| Wed Jul 14 | Carousel | Quarterly payments vs extra withholding |
| Thu Jul 15 | Short | 2 myths about estimated taxes for married couples |
| Fri Jul 16 | Short | $355 a paycheck: the W-4 math for a freelance spouse |
| Fri Jul 16 | Carousel | Three couples, one freelancer each: the tax gap |
| Sat Jul 17 | Short | 3 things that change when your spouse freelances |
| Sun Jul 18 | Long | Married, one W-2 and one freelancer: how to handle the taxes |

Render: `factory pack export --brand 1099-money --file launch/1099-money/couples/content.json --start 2027-07-12 --days 7 --short-days mon,tue,wed,thu,fri,sat --carousel-days mon,wed,fri --out <folder>`

## The worked example (2026 federal figures, fictional couple)

Jordan earns **$70,000** in wages. Riley has **$40,000** of freelance profit. Married filing jointly, standard
deduction **$32,200**, no other income. Computed with the site's tax model (`apps/freelance-tax/lib/tax.js`).

| Step | Amount |
|---|---|
| Riley's self-employment tax (15.3% × 92.35% of profit; per person) | $5,652 |
| Adjusted gross income ($70,000 + $40,000 − half of SE tax $2,826) | $107,174 |
| − standard deduction (MFJ) | $32,200 |
| − qualified business income deduction (20% of $37,174) | $7,435 |
| Taxable income | $67,539 |
| Income tax (10% to $24,800, then 12%) | $7,609 |
| **Total federal tax** | **$13,261** |
| Tax on Jordan's wages alone (assumed withholding) | $4,040 |
| **Gap: tax caused by Riley's profit** | **$9,221 (23.1%)** |
| Riley alone, filing single, same profit | $7,427 (18.6%) |

**Ways to cover the gap**
- **Joint estimated payments** (Form 1040-ES, both names): to reach 90% of this year's tax, $13,261 × 90% − $4,040 = **$7,895**, or **$1,974 a quarter**. Or 100% of last year's joint tax (110% if last year's AGI was over $150,000).
- **Extra withholding** on Jordan's Form W-4, step 4(c): **$355** per biweekly paycheck for the full gap ($9,221 ÷ 26), **$304** to reach the 90% line, or **$710** from July (13 paychecks left). Withholding is treated as paid evenly through the year, so it can cover earlier quarters.
- **Both:** a fixed extra amount withheld, plus a top-up payment.

**Other couples (same method):** $50K wages + $25K profit → $5,623 (22.5%); $90K + $60K → $13,992 (23.3%).

**Also covered:** the self-employed health insurance deduction isn't allowed for months Riley was eligible for an
employer-subsidized plan, including Jordan's; retirement limits are per person (Riley's SEP at $40K ≈ $7,435);
filing separately is rarely better and lowers the 110% line to $75,000; state estimated payments.

## Sources

- Estimated taxes and the safe harbor: https://www.irs.gov/businesses/small-businesses-self-employed/estimated-taxes, Publication 505 (https://www.irs.gov/publications/p505), Form 2210 instructions
- Form 1040-ES (joint estimated payments): https://www.irs.gov/forms-pubs/about-form-1040-es
- Form W-4 and the IRS Tax Withholding Estimator: https://www.irs.gov/forms-pubs/about-form-w-4, https://www.irs.gov/individuals/tax-withholding-estimator
- Schedule SE: https://www.irs.gov/forms-pubs/about-schedule-se-form-1040
- Self-employed health insurance deduction (Form 7206): https://www.irs.gov/forms-pubs/about-form-7206
- 2026 brackets and standard deduction: IRS Rev. Proc. 2025-32

**Assumption to check:** Jordan's actual withholding. It depends on the W-4 and payroll tables; use a recent pay stub
or the IRS estimator. Educational content, not tax advice. Nothing here is posted automatically.
