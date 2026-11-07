# Money Made Simple at Work (employer financial-wellness newsletter)

A monthly, white-label financial-wellness newsletter that HR sends to employees under the employer's
own name. Built from Money Made Simple's evergreen library and 1099 Money's tax content, rewritten for
employees. **Education only:** no fund, account or product recommendations, no affiliate links.

**$59 / $129 / $249 a month** by headcount (Starter up to 100, Growth 100 to 499, Plus 500+). Two
months free for the first 3 employers. Annual plans get 2 months free.

| File | What it is |
|---|---|
| `issues.json`, `samples/month-1..12.md` | 12 issues, Jan to Dec 2027. May to Dec: starter emergency fund, subscription audit, paying down debt, mid-year paycheck checkup, scams that target employees, open enrollment, holiday spending and BNPL, year-end checklist. Jan to Apr: new-year money reset, tax season (withholding, side income, IRS scams), credit scores, retirement plan in 10 minutes (Financial Literacy Month). |
| `brands/example.json` | **Fictional** employer "Sample Outfitters Co." used for the sample pack. |
| `product.json` | Labels and formats. Brand slots: `{{EMPLOYER_SHORT}}`, `{{BENEFITS_CONTACT}}`, `{{BENEFITS_PORTAL}}`, `{{RETIREMENT_PLAN}}`, `{{MATCH_LINE}}`, `{{EAP_LINE}}`, plus HR's own note and sender line. |
| `sales-sheet.html` | One-page sales sheet (renders to `out/sales-sheet.pdf`). |
| `COMPLIANCE_NOTE.md` | Education vs advice (ERISA, DOL Interpretive Bulletin 96-1), tax, privacy, accessibility, what the employer must supply. |
| `COLD_EMAILS.md` | Emails for HR managers, SHRM chapters and benefits brokers; follow-ups; replies. |
| `PROSPECTS.csv`, `PROSPECTS.md` | 51 prospects: 11 partners (8 HR associations, 2 benefits brokers, 1 PEO) and 40 employers from public "Top Workplaces" and "Top Companies" lists in Montana and Idaho, each with a 1–5 `fit_score` and reason. |

Each issue builds into: employee email (HTML + text), an intranet, Teams or Slack post with a
1080×1080 image, a 1920×1080 breakroom screen slide, a letter breakroom flyer (Growth and Plus), manager
talking points (Growth and Plus) and a sources page.

## Different from the credit union workflow

Follow `../credit-union-alert/DELIVERY_WORKFLOW.md`, with these changes:
- **Monthly**, delivered **2 weeks** before the send date (HR often routes it past a broker or legal).
- Topics follow the HR calendar: January reset, February tax season, April Financial Literacy Month,
  summer vacation spending, back-to-school, open enrollment (Oct–Nov), year-end FSA deadline.
- Never write plan-specific facts yourself. Match, vesting, HSA/FSA rules and deadlines come only from
  the employer's brand file, in HR's exact wording.
- Check every dollar limit (401(k), HSA, IRA) against IRS.gov each year before using it; the samples
  deliberately quote none.
