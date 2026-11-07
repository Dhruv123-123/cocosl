# Adjacent niches the factory could spin up next

Three picks, ranked. Each reuses the factory's strengths (research grounding, fact-check gate, carousels,
long-form explainers) and has affiliate programs that pay. Per the playbook, only start a second brand
once Money Made Simple runs in under 30 minutes a day.

## Summary

| Rank | Brand idea | Why now | Money | Overlap with MMS | Risk |
|---|---|---|---|---|---|
| 1 | **Scam Shield**: scam, fraud and identity-theft explainers | Americans reported a record $15.9B in fraud losses in 2025 (+27%); older adults ~$3B; investment scams via social media lead | Cybersecurity CPM is among YouTube's highest ($20–30); Aura $65+/enrollment, NordVPN up to 40%, 1Password; sponsor-friendly | Shares credit-freeze, bank-alert, "is your app insured" topics | Must never show real victims' data; no fear-mongering |
| 2 | **Dinero Simple**: Money Made Simple in Spanish for US Hispanic households | Spanish-language finance described as less saturated with higher funnel conversion; 500M+ Spanish speakers | Same US banking/budget affiliates (US audience), own products translated | Near-total: translate + localise existing scripts | Needs a native-speaker reviewer; don't machine-translate unchecked |
| 3 | **1099 Money**: money for freelancers and side hustlers | ~27.6M full-time US independent workers (MBO Partners 2025), up from 13.6M in 2020 | Tax/business RPM ($13–19); FreshBooks $88/sale, Gusto $50–100/lead, QuickBooks 10%, FreeTaxUSA 50%; templates sell well | Shares budgeting and tax pillars; product spin-off of the 20-Minute Budget | Tax content must be accurate and dated each year |

Runner-up: **AI tools for small business**. Best recurring affiliates (ElevenLabs 22% x 12 months,
Synthesia 25% x 12 months, OpusClip, Notion) and it feeds the AI Ad Studio pipeline, but it's the most
crowded niche of 2026 and tool reviews go stale in weeks. Better as a newsletter section than a channel.

## 1. Scam Shield

- **Audience:** adults 35–70 and their adult children ("send this to your parents"). The share-to-family
  mechanic is built in.
- **Promise:** "One scam, explained in 60 seconds, so you spot it first."
- **Pillars:** text/email scams decoded; investment and crypto scams on social media; identity theft and
  credit freezes; protecting older parents; account security basics (passwords, 2FA, SIM swap).
- **Formats:** "Anatomy of a scam text" carousels (real-looking but fictional messages, annotated);
  60s explainers; monthly long-form "scams of the month" roundup sourced from FTC/FBI IC3 alerts.
- **Ideas engine:** FTC consumer alerts, FBI IC3 PSAs, r/Scams. All public and citable, which suits the
  research-grounding step.
- **Money:** Aura, NordVPN, 1Password, credit monitoring; sponsors (security brands buy a lot of creator
  ads); a "family scam-proofing checklist" PDF product.
- **Guardrails:** fictional examples only; never real phone numbers, names or screenshots with personal
  data; no "you've been hacked" panic hooks.

## 2. Dinero Simple

- **Audience:** Spanish-dominant and bilingual US households; first-generation earners building credit.
- **Promise:** "Un paso con tu dinero cada semana, sin rodeos."
- **Pillars:** same as MMS, plus building credit from zero, ITIN banking, sending money home (fees
  compared), helping parents with US paperwork.
- **Production:** run existing approved MMS scripts through translation + a localisation pass (examples,
  prices, institutions), then **native-speaker review** in the queue before approval. Separate Spanish
  voice. Separate accounts per platform (one brand = one niche).
- **Money:** same US affiliates (the audience is US-based); translated 20-Minute Budget ("El Presupuesto
  de 20 Minutos").
- **Why it's cheap:** most of the research and fact-checking is already done for the English version.

## 3. 1099 Money

- **Audience:** freelancers, creators, gig workers and side hustlers who just got their first 1099.
- **Promise:** "Get paid, keep more, never fear April."
- **Pillars:** quarterly estimated taxes; what's deductible (with sources); separating business money;
  invoicing and getting paid; retirement and health insurance without an employer (SEP IRA, Solo 401(k), HSA).
- **Formats:** "real math" carousels (e.g. "$60K freelance income: what you actually owe"); quarterly-deadline
  Shorts (Jan 15, Apr 15, Jun 15, Sep 15); long-form "first year freelancing" guides.
- **Money:** FreshBooks, QuickBooks, Gusto, Novo, FreeTaxUSA/TaxAct, Lively HSA; a "Freelancer Tax
  Tracker" spreadsheet product (variant of the existing template). It also cross-sells the AI Ad Studio:
  freelancers and small businesses are the studio's buyers.
- **Guardrails:** state "not tax advice"; date every tax figure; re-check numbers each January.

## Brand YAML stubs (copy into `brands/` when ready)

```yaml
name: Scam Shield
niche: plain-English scam and identity-theft explainers
audience: adults 35-70 and the adult kids who look out for them
promise: one scam explained in 60 seconds so you spot it first
pillars: [text and email scams decoded, investment and crypto scams on social media, identity theft and credit freezes, protecting older parents, account security basics]
seed_topics: [credit freeze, phishing text, sim swap, romance scam, fake investment app, tech support scam]
avoid_topics: [real victims' personal data, hacking how-tos, panic headlines]
subreddits: [Scams, IdentityTheft, personalfinance]
voice: {tone: calm, protective, specific, persona: a friend who works in fraud prevention}
```

```yaml
name: 1099 Money
niche: money and taxes for freelancers and side hustlers
audience: first-year freelancers, creators and gig workers in the US
promise: get paid, keep more, never fear April
pillars: [quarterly estimated taxes, deductions with sources, separating business money, invoicing and getting paid, benefits without an employer]
seed_topics: [quarterly estimated taxes, self employment tax, sep ira, solo 401k, business bank account, home office deduction]
avoid_topics: [tax evasion, aggressive write-off hacks, state-specific advice without sources]
subreddits: [freelance, tax, smallbusiness, sidehustle]
voice: {tone: calm, practical, numbers-first, persona: a friend who's an accountant for creators}
```

## Sources

- [FTC: Americans lost a record $15.9B to scams in 2025 (via Pulse)](https://www.pulse.bot/personal-finance/news/ftc-says-americans-lost-record-159-b-to-scams-in-2025-up-27-from-2024-b068f185-7d07-4221-9a0c-c801d47062da)
- [FTC: Annual report to Congress on protecting older adults (Oct 2026)](https://www.ftc.gov/node/338049)
- [Opus: Faceless YouTube niches 2026 (cybersecurity CPM $20–30)](https://www.opus.pro/blog/faceless-youtube-niches-2026)
- [OutlierKit: finance niche gaps incl. Spanish-language finance](https://outlierkit.com/resources/youtube-finance-niche-creators/)
- [2btube: Spanish-speaking YouTube audiences 2026](https://2btube.com/en/?p=16957)
- [Staffing Industry Analysts: MBO Partners independent workforce count](https://www.staffingindustry.com/news/global-daily-news/number-of-independent-workers-rises-again-mbo-partners)
- Affiliate terms: see `02-affiliate-programs.md`
