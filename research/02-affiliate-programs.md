# Affiliate programs worth joining (Nov 2026)

Payouts below come from affiliate directories and the programs' own pages as of Nov 2026. **They change
often and several sources contradict each other** (flagged where they do). Confirm the live terms in the
network dashboard after you're approved, then put the real numbers in the brand YAML `affiliates:` block.

## How finance affiliate money actually works for a small creator

- Most finance programs pay a **flat bounty (CPA)** per approved lead or funded account, not a percentage.
- Almost all run through **Impact** or **CJ Affiliate**; FlexOffers and PartnerStack cover the rest.
  Join Impact and CJ first: one application each unlocks most of the list.
- Banks and brokers **manually approve** affiliates and want a real site or channel with original finance
  content and a mainly US audience. Apply after ~10 posts are live and the link-in-bio page is up, not
  on day one.
- Typical payout threshold: **$50**, monthly, net-30.
- Credit card issuers mostly work through large comparison sites (Bankrate, NerdWallet). Direct card
  programs (Amex via eBay Partner Network) exist but have 7-day cookies and strict ad rules. Skip cards
  until the brand has traffic and a disclosure process the issuer will accept.

## Tier 1: apply first (fit the current Money Made Simple pillars)

| Program | What you're paid | Cookie | Network | Fit | Notes |
|---|---|---|---|---|---|
| **SoFi** (banking, invest, loans) | $100–$150 per lead | 30 days | Direct / Impact | HYSA, student loans | Directory lists a $10,000/yr cap; "lead" vs "sale" wording is inconsistent. Confirm qualifying action. |
| **CIT Bank** (savings) | ~$100 per order | 30 days | CJ | HYSA / emergency fund | Good replacement for the placeholder "Example HYSA" link. |
| **Empower** (formerly Personal Capital) | ~$115 per lead | 30 days | Impact | Net worth tracking, retirement | Requires a personal-finance site with original content. |
| **Betterment** | $25–$1,250 per referral (tiered by deposit) | 30 days | Impact | Index funds, IRAs | Brokerage/adviser: FINRA/SEC rules apply (see below). |
| **M1 Finance** | $46–$56 per sale | 30 days | Impact | Investing basics | M1 was fined $850K by FINRA (2024) over influencer posts; expect strict review of your content. |
| **Acorns** | ~$10 per lead | 30 days | Impact | Beginner investing | Low payout, easy conversion. |
| **Robinhood** | $5 per lead / up to $20 per funded account | 30 days | Impact | Investing | Third-party figures, inconsistent. Email creators@robinhood.com if you already have Impact. |
| **Ally Invest** | $25–$50 per sale | 45 days | CJ | Investing | Manual approval, US audience. |
| **Rocket Money** | $4–$10 per action | n/a | Impact | Subscriptions, budgeting apps | Matches video #14 ("forgotten subscriptions"). Audience 23–55, US. |
| **Monarch Money** | Not published (see Impact) | n/a | Impact | Budgeting apps | Honest app comparisons are a pillar; Monarch is the main YNAB alternative. |
| **YNAB** | Invite-only | n/a | Direct | Budgeting | Email pr@ynab.com once you have numbers to show. |
| **FreeTaxUSA** | 50% per sale | 90 days | Direct | Tax season (Jan–Apr) | Seasonal spike; queue content in January. |
| **Aura** (identity theft protection) | $65 per enrollment (page metadata says "up to $125") | 60 days | Impact | Credit freeze, fraud | Matches video #07 ("freeze your credit"). Net-30 monthly. |

## Tier 2: for the adjacent niches (see `04-adjacent-niches.md`)

| Program | What you're paid | Cookie | Network | Niche |
|---|---|---|---|---|
| **NordVPN** | Up to 40% new, 30% renewals (source contradicts itself on renewals) | 30 days | Direct | Scam / security |
| **1Password** | 25% of first payment, $2 minimum (directory headline says 40%) | 45 days | FlexOffers | Scam / security |
| **Aura** | $65+ per enrollment | 60 days | Impact | Scam / security |
| **FreshBooks** | $88 per sale, $8 per trial lead | 120 days | Impact | Freelancer money |
| **QuickBooks** | 10% per sale | 45 days | Impact | Freelancer money |
| **Gusto** | $50–$100 per lead | 120 days | Gusto network | Freelancer money (once they hire) |
| **Novo** (business banking) | Not published | n/a | PartnerStack | Freelancer money |
| **TaxAct** | 15% per sale | 45 days | CJ | Freelancer money (quarterly taxes) |
| **Lively** (HSA) | $10 per sale | 14 days | Impact | Freelancer benefits |

## Tier 3: creator-tool SaaS (recurring, fits the AI Ad Studio and a possible "AI tools" brand)

Recurring percentages beat one-off finance bounties over time, and the factory already uses these tools,
so the content is honest by default.

| Program | Commission | Recurring for | Cookie | Network | Catch |
|---|---|---|---|---|---|
| ElevenLabs | 22% | 12 months | 90 days | PartnerStack | Business plans 11%, enterprise 0 |
| HeyGen | 35% | 3 months | 30 days | In-house | Needs 5,000+ followers and original video |
| Synthesia | 25% | 12 months | 60 days | Rewardful | |
| OpusClip | 25% | 12 months | n/a | In-house | Deactivates accounts with no traffic in 6 months |
| CapCut | 35% | Recurring | n/a | Impact | US/UK/DE/FR only, $15K cap |
| Descript | $25 flat | One-time | n/a | PartnerStack | |
| Notion | $50 per signup + 20% | Year one | 180 days | PartnerStack | Clawback on refunds within 2 months |
| Submagic / Fliki / Simplified | 30–40% | Lifetime | 30 days (Fliki) | In-house | Smaller brands, lifetime recurring |
| beehiiv Partner Program | 50% | 12 months | 60 days | Direct | We'd be using beehiiv anyway (see `05-income-streams.md`) |

## Compliance that matters more in finance than anywhere else

The guardrails already block an affiliate link without a disclosure. Finance adds three more things:

1. **FTC**: "#ad" or "affiliate link" in the caption *and* said or shown in the video when the video
   recommends the product. Already in the brand `ai_disclosure`; add affiliate wording per post.
2. **FINRA Rule 2210** (brokers: Robinhood, M1, Ally Invest, Betterment's broker arm): when a firm pays
   you, your post becomes *their* communication. It must be fair and balanced, no performance promises,
   and many firms will want to **pre-approve** scripts. TradeZero was fined $250K and M1 $850K in 2024
   for not supervising influencers. Expect contracts that require script review: plan for a 2–5 day lag.
3. **SEC Marketing Rule** (advisers: Betterment, Wealthfront, Empower): compensation and conflicts must be
   disclosed; written agreements required.

Practical rule for the factory: **banking and budgeting-app links are low-friction; brokerage and adviser
links need a "compliance review" flag on the post** before it can be approved. Worth adding to
`guardrails.py` later (outside this research PR).

## Suggested first applications (this week)

1. Impact account → apply to SoFi, Empower, Rocket Money, Monarch, Aura, Acorns.
2. CJ account → CIT Bank, Ally Invest.
3. Replace the placeholder `Example HYSA` in `brands/money-made-simple.yaml` with whichever HYSA approves
   first.

## Sources

- [Lasso: banking affiliate programs](https://getlasso.co/niche/banking/) · [financial programs](https://getlasso.co/niche/financial/) · [SoFi](https://getlasso.co/affiliate/sofi/) · [1Password](https://getlasso.co/affiliate/1password/)
- [Rocket Money affiliates](https://framer.rocketmoney.com/affiliates) · [YNAB affiliate program](https://www.ynab.com/partners/affiliate-program) · [Monarch on Affilitizer](https://www.affilitizer.com/programs/monarchmoney.com) · [Aura affiliate program](https://www.aura.com/affiliate-program)
- [Wealthfront referral programs](https://support.wealthfront.com/hc/en-us/articles/209353126-What-are-the-Wealthfront-referral-programs) (client referrals only; no public creator program found)
- [Creator Hero: Robinhood](https://www.creator-hero.com/blog/robinhood-affiliate-program-affiliate-program-in-depth-review-pros-and-cons) · [NordVPN](https://www.creator-hero.com/blog/nordvpn-affiliate-program-in-depth-review-pros-and-cons)
- [zPlatform: AI affiliate programs compared](https://zplatform.ai/ai-affiliate-programs/)
- [Awisee: SEC and FINRA rules for finfluencers](https://awisee.com/blog/regulation-of-financial-influencers) · [FINRA fines M1 Finance $850K](https://www.businesswire.com/news/home/20240318038016/en/FINRA-Fines-M1-Finance-%24850000-for-Violations-Regarding-Use-of-Social-Media-Influencer-Program)
