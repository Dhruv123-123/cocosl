# Official news feeds for Scam Decoded and 1099 Money

Written 2026-11-07. **Docs only. Nothing is subscribed or built.** This lists the public RSS feeds and
official subscription lists that the two brands could watch for story ideas. It's for main to decide
whether a small `factory news` digest is worth building after the merge freeze.

**How the URLs were checked.** This session's network blocks direct requests to most .gov hosts, so each
URL comes from the agency's own feeds page where we could read one (FTC). Otherwise it comes from a feed
directory that showed recent items, which is noted in the table. Before building anything, open each URL
once in a browser. A feed that returns HTML instead of XML has moved.

## Feeds to watch

| # | Feed | URL | Brand | Status | What it gives us |
|---|---|---|---|---|---|
| 1 | **FTC Consumer Alerts** (consumer blog) | `https://www.consumer.ftc.gov/blog/gd-rss.xml` | Scam | Listed on the [FTC RSS page](https://www.ftc.gov/news-events/stay-connected/ftc-rss-feeds) | Plain-English scam alerts, several a week. **The best single source for Scam Decoded** |
| 2 | **FTC Consumer Protection press releases** | `https://www.ftc.gov/feeds/press-release-consumer-protection.xml` | Scam | FTC RSS page | Lawsuits, settlements and refund checks ("FTC sends $X to people who lost money to...") |
| 3 | **FTC Data Spotlight** | `https://www.ftc.gov/feeds/data-spotlight.xml` | Scam | FTC RSS page | Consumer Sentinel numbers (losses by scam type, by age). A few a year, and each one is a ready-made data video |
| 4 | **FTC Business Blog** | `https://www.ftc.gov/feeds/blog-business.xml` | 1099 | FTC RSS page | Rules on fake reviews, earnings claims and the gig economy. Useful for freelancers and small sellers |
| 5 | **CFPB Newsroom** | `https://www.consumerfinance.gov/about-us/newsroom/feed/` | Both | A feed directory showed an item from 14 Oct 2026 | Enforcement, rules and reports on banks, payment apps, credit reports and debt collection |
| 6 | **IC3 public service announcements** (FBI) | `https://www.ic3.gov/PSA/RSS` | Scam | A feed directory showed an item from 23 Oct 2026 | FBI warnings on new scams (impostors, crypto, "phantom hacker") |
| 7 | IC3 industry alerts | `https://www.ic3.gov/CSA/RSS` | — | A feed directory showed an item from 5 Nov 2026 | Mostly technical alerts for businesses. **Skip** unless the PSA feed goes quiet |
| 8 | **SEC Investor Alerts and Bulletins** | `https://www.sec.gov/rss/investor/alerts` | Both | Found through a feed directory | Investment and crypto scams (Scam Decoded), plus bulletins on retirement accounts (1099 Money) |
| 9 | **IRS Newswire** and **IRS Tax Tips** | No RSS listed. Email subscription only: [IRS News Bulletins](https://irs.gov/newsroom/irs-news-bulletins) → GovDelivery | 1099 (and Scam in tax season) | The IRS page lists email lists, not RSS | Deadlines, rule changes, and the yearly "Dirty Dozen" scam list. **The best single source for 1099 Money** |
| 10 | **SSA OIG scam alerts** | Web page: [oig.ssa.gov/scam-alerts](https://oig.ssa.gov/scam-alerts/). No RSS confirmed | Scam | Page checked; no feed found | Social Security impostor warnings, a big topic for the 35-70 audience |
| 11 | **BBB Scam Tracker** | **No public RSS or API found** | Scam | [BBB scam resources](https://bbb.org/scamresources) offer no feed | Check the site by hand once a week. Don't scrape it: BBB's terms don't allow it, and we've only used official feeds |

**Also worth knowing:** IRS Criminal Investigation has an email list ("ICYMI: Top IRS-CI Stories") on the same
IRS page. It's good for "how they got caught" stories.

## How a `factory news` digest could use these

If main builds it, this is the smallest version we'd suggest:

1. **Feeds 1, 2, 3, 5, 6 and 8** as RSS, read once a day using only the Python standard library
   (`urllib` and `xml.etree`), with no new dependency.
2. **IRS (feed 9):** send the GovDelivery emails to the shared inbox and read them by hand. Don't parse the inbox.
3. Output: one Markdown file a day (`out/news/YYYY-MM-DD.md`) listing the title, agency, date and link,
   tagged `scam`, `1099` or `both` by the table above. Nothing is drafted or posted automatically: a person
   picks a story and runs the normal content flow.
4. Store the last-seen item ID per feed so each item appears once.
5. **Rules for the content:** link the agency's page in every post that uses it. Quote short facts only
   (US federal government works are public domain, but logos and seals are not). Never imply the agency
   endorses the brand.

**Worth building?** Probably yes for Scam Decoded, because the FTC and IC3 feeds alone give 3-6 fresh
topics a week. For 1099 Money it's less useful: the IRS has no RSS, and its calendar is mostly known ahead of
time (`launch/` tax-season packs). That decision is main's.

## Sources

- [FTC RSS feeds](https://www.ftc.gov/news-events/stay-connected/ftc-rss-feeds) and [FTC Stay Connected](https://www.ftc.gov/stay-connected) (read 7 Nov 2026)
- [IRS News Bulletins](https://irs.gov/newsroom/irs-news-bulletins) and [IRS e-News subscriptions](https://www.irs.gov/newsroom/e-news-subscriptions)
- The CFPB newsroom feed through [Feeder](https://feeder.co/discover/bee9f75085/consumerfinance-gov-about-us-newsroom)
- The IC3 feeds through Feeder ([PSA](https://feeder.co/discover/bd9cb40010/ic3-gov), [CSA](https://feeder.co/discover/4c9be32565/ic3-gov))
- The SEC investor alerts feed through [Feeder](https://feeder.co/it/discover/9bb2e79381/sec-gov-investor-alerts)
- [SSA OIG scam alerts](https://oig.ssa.gov/scam-alerts/) and [BBB scam resources](https://bbb.org/scamresources)
