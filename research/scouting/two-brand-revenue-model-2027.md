# 12-month revenue model for the two-brand plan (Money Made Simple + Scam Decoded)

Written 2026-11-07. **Docs only.** The spreadsheet is `two-brand-revenue-model-2027.xlsx`, and the script
that builds it is `revenue_model_two_brands.py`. The spreadsheet uses live formulas: change a yellow
cell on **Inputs** and every month recalculates. The committed copy was recalculated in LibreOffice, so it
opens with numbers showing. It covers Nov 2026 to Oct 2027, with MMS launching Mon 16 Nov and Scam
Decoded around Mon 30 Nov (`DHRUV_DECISIONS.md` row 2b).

**What's left out:** the ad studio (PR #3 and PR #12 have their own model), B2B (PR #13), 1099 Money and
Dinero Simple. This is just the two content brands, organic only. The four-brand model
(`revenue-model-2027.md`) is the wider picture. This one is smaller and more cautious, and it matches the
targets in `growth-90-days-two-brands.md`.

## The answer

| | Low | Base | High |
|---|---:|---:|---:|
| **Year-1 revenue, both brands** | **$454** | **$4,827** | **$65,821** |
| Costs (domains, API, mailbox, Etsy fees, and Sender once the lists pass 2,500) | $152 | $212 | $751 |
| **Net, year 1** | **$302** | **$4,614** | **$65,070** |
| Net in month 12 (Oct 2027) | $73 | $896 | $13,536 |
| MMS share of revenue | 74% | 73% | 71% |

**Where the base case's money comes from:** affiliates $2,313, products from email $1,346, and Etsy plus
Gumroad Discover $1,168. **YouTube, TikTok, Instagram and Pinterest pay $0 directly.**

## Why the platforms pay $0 in the low and base cases

| Platform | Gate (Nov 2026) | Does any case reach it? |
|---|---|---|
| YouTube long-form ads | 1,000 subscribers plus 4,000 watch hours until 31 Jan 2027, then **8,000 hours** (or 20M Shorts views) for new applicants | Only the high case: MMS in **Apr 2027**, Scam Decoded in **Jul 2027** |
| YouTube Shorts ad share | **10M Shorts views in 90 days** | No case. Even the high case peaks around 1.5-2M a month |
| TikTok Creator Rewards | 10K followers, 100K views in 30 days, a personal account, original videos **over 1 minute**, and not fully AI | Only the high case. Our Shorts are under a minute, so only the 60-90 second cuts count |
| Instagram | Reels bonuses are invite-only, and there's no per-view pay at our size | $0. Instagram is a traffic source |
| Pinterest | We found no open US pay-per-view program | $0. Pinterest is a traffic source |

## The inputs that matter most

The high case is roughly 14 times the base case, because a few inputs compound. These are the ones to
replace with real numbers at day 30, 60 and 90:

1. **Affiliate clicks a month** (MMS base: 400 by month 12). This is the biggest base-case stream. It
   depends on the site and tools getting search traffic, not on social followers.
2. **Email subscribers** (MMS base: 1,500 by month 12). They drive product sales and, above 2,500,
   sponsors.
3. **Long-form YouTube views** (MMS base: 20,000 a month by month 12). Below about 30,000 a month, the
   8,000-hour gate isn't reached in year 1.
4. **Conversion rates.** The welcome sequence is set at 2% of new subscribers buying, consistent with
   MailerLite's 0.42% per automated email across about 8 emails. Broadcasts are set at 0.2% of the list
   per send, below MailerLite's 0.32% campaign average, because our prices are low and the lists are new.

## Sources

The spreadsheet's **Sources** sheet gives the link for each input. The main ones:
[YouTube Official Blog, YPP updates for 2027](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/) (10 Aug 2026);
[YouTube Help: YPP eligibility](https://support.google.com/youtube/answer/72851);
[ttcalculator.net: TikTok Creator Rewards](https://ttcalculator.net/guides/creator-rewards-program/) (updated 10 Jul 2026; US RPM about $0.50-2.00, creator-reported);
[MailerLite: email conversion rates](https://www.mailerlite.com/blog/email-marketing-conversion-rate) (20 Apr 2026; 300M+ emails);
[OutlierKit RPM benchmarks](https://outlierkit.com/resources/youtube-rpm-benchmarks/) (19 Aug 2026).
Affiliate payouts come from `affiliate-answers-five-programs.md`, sponsor rates from
`newsletter-sponsorship-benchmarks.md`, and fees from `free-tool-limits.md`. The growth inputs are our
estimates, and the Inputs sheet marks each one "est".
