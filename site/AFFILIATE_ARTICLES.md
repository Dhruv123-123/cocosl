# Affiliate-keyword articles (19): handoff to the site

Nineteen articles in `content/blog/` that sit **under** the eight Compare pages (`content/compare/`, PR #4).
They follow the site's builder format: blog front matter (`title`, `seo_title`, `description`, `date`,
`pillar`, `keyword`, `sources`), a `## Common questions` FAQ, internal links and `{{signup}}`.

## How they fit with the Compare pages

The Compare pages own the "best X" searches. No article targets a Compare page's keyword (a test checks
this). Overlapping articles became supporting pieces with their own keyword and a link up to the Compare
page near the top.

| Compare page | Supporting articles (keyword) |
|---|---|
| `/compare/best-high-yield-savings-accounts/` | how-to-open-a-high-yield-savings-account ("how to open a high yield savings account", was "best HYSA"), sofi-review, cit-bank-review, ally-bank-review, high-yield-savings-vs-money-market |
| `/compare/best-budgeting-apps/` | how-to-choose-a-budgeting-app ("how to choose a budgeting app", was "best budgeting apps"), ynab-review, monarch-money-review |
| `/compare/rocket-money-vs-ynab-vs-monarch/` | rocket-money-review, ynab-review, monarch-money-review (monarch-vs-ynab is retired by `blog_redirects`) |
| `/compare/best-robo-advisors/` | are-robo-advisors-worth-it ("are robo advisors worth it", fee maths over 30 years; was "best robo advisor for beginners"), betterment-review, acorns-review, empower-review |
| `/compare/best-identity-theft-protection/` | aura-review |
| `/compare/best-credit-builder-cards/` | self-credit-builder-review |
| `/compare/best-bill-negotiation-services/` | rocket-money-review |
| `/compare/best-balance-transfer-cards/` | none yet |

## Articles with no Compare page (they stand alone)

| Article | Keyword | Pillar | Notes |
|---|---|---|---|
| where-to-open-a-roth-ira | where to open a roth ira | investing | `compliance: review`; 2026 IRA limit $7,500 |
| freetaxusa-review | freetaxusa review | money-tools | |
| best-tax-software-for-simple-returns | best tax software for simple returns | money-tools | VITA and Free File first |
| best-bank-account-for-college-students | best bank account for college students | money-tools | |

A future "best tax software" Compare page would make the two tax articles its supporting pieces.

## Links

Affiliate links are `/go/<slug>/` links from `site/go-links.json`, the single place to paste approved
tracking links (the build also copies them into `site.json > programs`, so the Compare pages update too).
Every article with a `/go/` link sets `affiliate: yes`, so it shows the affiliate notice.

## Before publishing (human review)

- [ ] **Check every price, fee and rate against the company's own page.** They were checked in Nov 2026
      by web search only (the build container can't open the sites). The ones that change most often:
      Rocket Money Premium and its negotiation fee, Monarch and YNAB pricing, Betterment's $4/month rule,
      Acorns tiers, CIT's $5,000 tier, SoFi's APY conditions, FreeTaxUSA's state fee, Self's plans, Aura's plans.
- [ ] Update the 2027 IRA limit in where-to-open-a-roth-ira once the IRS announces it.
- [ ] Check IRS Direct File for the 2027 season (it wasn't offered in 2026), and the VITA and Free File limits.
- [ ] Have someone review the `compliance: review` articles (investing) against FINRA 2210 and the SEC
      Marketing Rule before any adviser or broker link earns a commission.
- [ ] Source URLs weren't link-checked; open each one.

None of the reviews claims we used the product. Keep it that way unless someone really has.
