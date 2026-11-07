# What the free tools cost, and when they'd start charging

Written 2026-11-07. **Docs only.** One page on the free plans the launch depends on. Each limit is from the
provider's own docs where they loaded; secondary sources are marked.

## TL;DR

| Tool | Free plan | What we'll hit first | When | What it costs then |
|---|---|---|---|---|
| **Netlify** (sites and apps) | **300 credits a month per account, hard limit**. Production deploy 15 credits, bandwidth 20 credits per GB, 10,000 requests 2 credits, form submissions free | **Deploys.** 300 credits is **20 production deploys a month in total**, across every site on the account | **Month 1**, see the warning below | Personal plan: 1,000 credits, with optional top-ups of 500 credits for $5. Netlify's docs don't state the plan price, so check the pricing page |
| **Sender** (email) | **2,500 subscribers and 15,000 emails a month**, Sender branding, automations included | Subscribers, across all brands in one account | At about 2,500 total (`newsletter-tool-decision.md` puts that after month 3 in the base case) | Standard is priced by subscriber tier on a slider, with 12× your subscriber count in emails. Check it in Billing |
| **Gumroad** (products) | No monthly fee | Nothing. It's per sale | Every sale | **10% + $0.50** per direct sale, **30%** on sales Gumroad's Discover finds. Gumroad is the merchant of record and handles sales tax. Payouts to a bank are free; PayPal payouts cost 2% (secondary source). One secondary source also lists 2.9% + $0.30 card processing on top, so check `gumroad.com/pricing` before pricing |
| **Cloudflare** (domains, DNS) | DNS and CDN free; Pages 500 builds a month, 20,000 files a site; Workers 100,000 requests a day | Nothing at our size | Not in year 1 | Domains at cost: about $11.17 a year per .com after 1 Nov 2026 (`domain-plan.md`), ~$45 a year for four. That's the only planned spend |
| Etsy (for reference) | No monthly fee | Per listing and per sale | Every listing and renewal | $0.20 a listing (renewed every 4 months or on sale), 6.5% transaction fee, 3% + $0.25 processing (`template-pricing-jan-2027.md`) |

## The Netlify warning: the daily rebuild alone goes over the free plan

- **The MMS site's rebuild workflow runs daily.** It's on the site thread's branch
  (`.github/workflows/netlify-rebuild.yml`), and it publishes scheduled articles on their date. The file's
  own comment says "every Thursday", but the cron is `0 13 * * *`, which is every day.
- **The arithmetic:** 30 deploys × 15 credits = **450 credits a month**, against 300 free. And on the free
  plan **the limit is hard**: no overage billing, just nothing more until the next month. Netlify's docs
  don't say exactly what happens at the limit. Expect deploys to stop around **day 20**, and possibly
  the sites to pause.
- **Pushes make it worse.** Each Netlify site linked to `cocosl` deploys on every push to `main`, unless
  the site has a build-ignore rule. Four sites (the MMS site, the Scam Decoded site, the apps, the
  freelance-tax app) on one busy repo would use the 20 deploys in days.

**Fixes, cheapest first (for the site and apps threads):**
1. **Rebuild weekly, not daily** (4 × 15 = 60 credits), and date articles to that day. That's what the
   workflow's comment already says.
2. **Add a build-ignore rule per site** (`[build] ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- site/"`
   or the site's own folder), so a push that doesn't touch the site doesn't deploy it. Netlify's docs say
   failed and preview deploys aren't metered; check that ignored builds count the same way.
3. **Or move the static sites to Cloudflare Pages** (500 builds a month free, no bandwidth credit), and
   keep Netlify only where Netlify Forms is used. If signups go straight to Sender
   (`email-list-from-zero.md`, option 1), nothing needs Netlify at all.

Bandwidth is fine for now: 300 credits is 15 GB a month with nothing else, and static pages are small.
Images and PDFs served from the site count, though, so host big downloads on Gumroad.

## When each one starts costing money (a rough order)

1. **Domains:** at launch (~$45 a year; Dhruv's OK needed).
2. **Gumroad and Etsy:** on the first sale. A fee per sale, not a bill.
3. **Netlify:** in month 1 unless fixed (above). With the fixes, it's not expected in year 1.
4. **Sender:** at about 2,500 subscribers across the brands. That's the first real monthly bill, and a
   good problem. Before then, remove people who haven't opened in 90 days (they still count toward 2,500).
5. **Cloudflare:** not expected.

**Paid things already flagged elsewhere, for completeness:** the Apple developer account ($99 a year) for
any iOS app, the Chrome Web Store fee ($5 once) for the scam extension, a Spanish reviewer ($200-500 for
the lean set), and a $35 lawyer consult. Each waits for Dhruv's OK.

## Sources

Read 2026-11-07:
[Netlify credit-based pricing plans](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/);
[Sender: how pricing works](https://www.sender.net/help/account-settings-and-billing/how-sender-pricing-works/);
[Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits);
[Costbench: Cloudflare free plan](https://costbench.com/software/cdn-edge/cloudflare/free-plan/) (Workers 100,000 requests a day; verified 5 Nov 2026, secondary);
[Dodo Payments: Gumroad fees 2026](https://dodopayments.com/blogs/gumroad-fees-explained) (secondary; the 10% + $0.50 and 30% Discover figures match `gumroad.com/pricing` as read for `template-pricing-jan-2027.md`);
site thread branch `.github/workflows/netlify-rebuild.yml`.
