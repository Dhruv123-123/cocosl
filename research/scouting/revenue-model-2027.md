# Revenue model for the four brands, months 1-12 (Nov 2026 to Oct 2027)

Written 2026-11-07. **These are scenarios built on stated assumptions, not forecasts.** The tables are
printed by [`revenue_model.py`](revenue_model.py) (`python3 revenue_model.py`), so change an input and
re-run it rather than editing numbers by hand. All figures are **monthly US dollars after platform fees**,
before running costs and tax.

This complements the earlier model in PR #3 (`docs/FINANCIAL_MODEL.md`). That one covers MMS plus the AI
ad studio and the running costs. This one splits the **content business by brand**, sets **YouTube Shorts
revenue to $0** (`youtube-policy-review-nov-2026.md`), and adds the products, the B2B lines and the email
list. **The ad studio is left out here**: it's a separate service business, and PR #3 models it.

## TL;DR

| Scenario | Month 12 (Oct 2027), all brands | Year 1 total | Rough chance (judgment, not data) |
|---|---:|---:|---|
| **Conservative** | **about $200** | **about $1,300** | The most likely outcome for new faceless channels |
| **Base** | **about $3,100** | **about $18,500** | Maybe 1 in 4, and only if every launch step happens on time |
| **Optimistic** | **about $23,000** | **about $140,000** | 1 in 20 or less |

1. **Products are the biggest line in every scenario** (about half to three-quarters of year 1). Etsy search and the
   email list sell them without needing YPP. The product thread's work matters more than any other.
2. **YouTube ad revenue is $0 in the conservative and base cases for year 1.** Under the 2027 rule (8,000
   watch hours), the base case only reaches YPP for MMS in month 12. Long videos still matter: they build
   the subscribers, the email list and the watch hours that pay in year 2.
3. **Affiliates come second** once programs approve us (from about month 3). Most of that money is MMS
   (bank and budgeting offers) and 1099 Money in tax season (Jan-Apr).
4. **B2B is the only line priced per customer, not per person:** Scam Decoded's credit-union alerts
   ($99/month average) and the $99 team pack add about $1,600 in the base year. It depends entirely on
   Dhruv sending the emails.
5. **Newsletter sponsors don't pay until about 2,500 subscribers.** At 2,500 with 40% opens and $25 per
   1,000 opens, four sends earn about $100 a month. Thank-you page referrals (SparkLoop-style, from 500
   subscribers) pay earlier and more.
6. **Dinero Simple is the smallest brand** in every case (lower RPM, smaller list, products from December).
   Keep it, but it's a long bet.

## 1. Which monetization paths work for each brand in 2027

| Path | MMS | Scam Decoded | 1099 Money | Dinero Simple | Evidence |
|---|---|---|---|---|---|
| **YouTube long-form ads** | Year 2. Finance RPM about $8-14 | Year 2. Lower RPM (assumed $5-8: consumer topic, older viewers) | Year 2. Tax and business RPM similar to finance | Year 2+. Assumed $3-6 (mixed US and Latin America viewers) | Finance CPM $15-25 (Virlo, Apr 2026, via OutlierKit Aug 2026), times YouTube's 55% gives $8.25-13.75. Faceless finance "$10-15" commonly reported (GoFaceless, Oct 2026). **No public data for scam or Spanish finance RPM**, so those are our assumptions |
| **YouTube Shorts ads** | $0 | $0 | $0 | $0 | Needs 10M Shorts views per 90 days from 1 Feb 2027 (YouTube blog) |
| **TikTok Creator Rewards** | $0 in year 1 | $0 | $0 | $0 | Needs 10K followers and videos over 1 minute. Our Shorts are under 1 minute (`tiktok-instagram-monetization.md`) |
| **Products (Etsy, Gumroad)** | **Main line.** About 50 Etsy listings ($3-39) + Gumroad ladder | Kit $9 → Protect Your Parents $29 → team pack $99; seniors pack $7 on Etsy | Tracker $15 → kit $29 → bundle $49; 2027 planner $12 | Spanish editions $12-29, from 7 Dec | `PRODUCTS_CATALOG.md`, `LADDER.md`, `UPSELL_PATH.md` |
| **Affiliates** | **Strong**: bank, HYSA, budgeting apps (needs approval; placeholder links today) | Weak: identity-protection offers, low payouts | **Seasonal**: tax software, freelancer banking | Only after a compliance review | `affiliate-kit-and-articles` (31 programs, PR #5) |
| **Email: referrals** | From 500 subs | From 500 | From 500 | From 500 | Kit's paid recs need the Creator plan; SparkLoop partner links work on any plan (`thank-you-offers.md`) |
| **Email: sponsors** | From about 2,500 subs | Same | Same | Same | Finance newsletters $18-30 per 1,000 opens (SenderCircle, 2026). Small lists usually go through networks; flat rates for under 5K aren't published |
| **Subscription** | — | — | **Quarterly Tax Club** $5/mo or $39/yr from Jan 2027, if 50+ join the waitlist | — | `product-ideas-beyond-content.md` #3 |
| **B2B** | Park (employer wellness) | **Credit-union weekly alert** ($49-149/mo), team pack $99, paid talks | Park | — | `product-ideas-beyond-content.md` #1 |
| **Sponsorships (video)** | After the `sponsor-kit.md` gate (about 1K+ subscribers and steady views) | Same | Same | Same | Not modelled in year 1. Treat any deal as upside |

## 2. Assumptions (month-12 levels; everything ramps up from month 1)

Growth follows a curve, `(month/12)^1.5`, so month 6 is about 35% of month 12. Seasonal multipliers: MMS Etsy
+40% in January; 1099 Money views, Etsy sales and affiliates up 40-100% in January-April; Scam Decoded and
Dinero Simple Etsy +30% in December.

| Input (month 12) | MMS C / B / O | Scam Decoded C / B / O | 1099 Money C / B / O | Dinero Simple C / B / O |
|---|---|---|---|---|
| Long-form views per month | 3K / 25K / 150K | 2K / 15K / 80K | 2K / 15K / 90K | 1K / 10K / 60K |
| Average watch time | 4 min | 3.5 min | 5 min | 4 min |
| RPM after YPP | $8 / $10 / $13 | $5 / $6 / $8 | $8 / $10 / $14 | $3 / $4 / $6 |
| Email subscribers | 300 / 2,500 / 12,000 | 200 / 1,500 / 8,000 | 200 / 1,800 / 9,000 | 100 / 800 / 4,000 |
| Product revenue per new subscriber | $0.50 / $1.00 / $1.50 | $0.40 / $0.90 / $1.30 | $0.80 / $1.50 / $2.20 | $0.40 / $0.80 / $1.20 |
| Etsy orders per month (net per order) | 10 / 60 / 250 ($5) | 3 / 15 / 60 ($5) | 3 / 20 / 80 ($8) | 2 / 15 / 60 ($5) |
| Affiliate clicks per month × conversion × payout | 50 / 500 / 3,000 × 2% × $30-50 | 20 / 200 / 1,500 × 1.5% × $20-30 | 30 / 300 / 2,000 × 3% × $15-25 | 0 / 100 / 600 × 2% × $20, from month 6 |
| Other | — | Credit unions paying from month 8: 0 / 3 / 6 at $99. Team pack 0 / 1 / 4 a month from month 4 | Tax Club from January: 0 / 40 / 250 members at $4.50 net | Products from month 2 |

**Rules in the model:**
- **YPP** starts the month *after* a brand passes 8,000 long-form watch hours (cumulative), and not before
  February 2027. We assume the 1,000 subscribers come before the hours.
- **Referrals**: $0.30 per new subscriber once the list passes 500 (base and optimistic only).
- **Sponsors**: from 2,500 subscribers, 4 sends a month × 40% opens × $25 per 1,000 opens.
- **Product revenue per subscriber** is booked in the month they join. That's a simplification: some buy
  later, which pushes revenue into year 2.
- **Etsy net per order** is after Etsy's fees ($0.20 listing, 6.5% transaction, 3% + $0.25 payment). A $3
  printable nets about $2.26, so the $5 average assumes some $12-39 bundles in the mix.

**When YPP arrives:**

| Brand | Conservative | Base | Optimistic | Watch hours in year 1 (base) |
|---|---|---|---|---:|
| MMS | Not in year 1 | **Month 12 (Oct)**, paid from month 13 | Month 6 (Apr) | 8,850 |
| Scam Decoded | Not in year 1 | Not in year 1 | Month 8 (Jun) | 4,650 |
| 1099 Money | Not in year 1 | Not in year 1 (just short) | Month 6 (Apr) | 7,225 |
| Dinero Simple | Not in year 1 | Not in year 1 | Month 8 (Jun) | 3,540 |

## 3. Monthly revenue by brand

### Conservative

| Brand | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Year 1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MMS | 11 | 14 | 23 | 26 | 33 | 41 | 49 | 58 | 68 | 78 | 88 | 98 | **588** |
| Scam Decoded | 4 | 6 | 8 | 9 | 12 | 14 | 17 | 19 | 22 | 25 | 28 | 31 | **195** |
| 1099 Money | 7 | 11 | 18 | 23 | 29 | 35 | 31 | 36 | 41 | 46 | 52 | 57 | **387** |
| Dinero Simple | 0 | 4 | 4 | 5 | 6 | 7 | 8 | 9 | 11 | 12 | 13 | 15 | **93** |
| **All brands** | **23** | **35** | **52** | **63** | **79** | **97** | **106** | **123** | **142** | **161** | **181** | **201** | **1,263** |

### Base

| Brand | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Year 1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MMS | 105 | 155 | 255 | 309 | 437 | 522 | 611 | 702 | 797 | 894 | 994 | 1,198 | **6,979** |
| Scam Decoded | 44 | 74 | 98 | 142 | 189 | 273 | 322 | 409 | 496 | 582 | 670 | 757 | **4,055** |
| 1099 Money | 89 | 143 | 255 | 334 | 418 | 553 | 539 | 613 | 688 | 763 | 839 | 916 | **6,150** |
| Dinero Simple | 0 | 43 | 48 | 58 | 69 | 95 | 110 | 126 | 167 | 185 | 204 | 223 | **1,327** |
| **All brands** | **238** | **415** | **656** | **843** | **1,112** | **1,443** | **1,583** | **1,850** | **2,147** | **2,425** | **2,707** | **3,094** | **18,511** |

### Optimistic

| Brand | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Year 1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MMS | 621 | 1,138 | 1,868 | 2,299 | 2,925 | 3,500 | 4,963 | 5,770 | 6,611 | 7,484 | 8,388 | 9,323 | **54,888** |
| Scam Decoded | 295 | 622 | 858 | 1,141 | 1,422 | 1,811 | 2,114 | 2,448 | 3,201 | 3,612 | 4,030 | 4,455 | **26,009** |
| 1099 Money | 572 | 1,086 | 1,923 | 2,505 | 3,107 | 3,858 | 4,307 | 4,945 | 5,596 | 6,262 | 6,943 | 7,638 | **48,742** |
| Dinero Simple | 0 | 270 | 387 | 462 | 540 | 698 | 792 | 887 | 1,320 | 1,474 | 1,632 | 1,794 | **10,255** |
| **All brands** | **1,488** | **3,114** | **5,036** | **6,407** | **7,993** | **9,867** | **12,177** | **14,050** | **16,728** | **18,832** | **20,993** | **23,210** | **139,894** |

## 4. Year 1 by stream

### Conservative

| Brand | YouTube long-form | Products | Affiliates | Email (referrals, sponsors) | Tax Club | B2B | Total | Month 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MMS | 0 | 431 | 157 | 0 | 0 | 0 | **588** | 98 |
| Scam Decoded | 0 | 164 | 31 | 0 | 0 | 0 | **195** | 31 |
| 1099 Money | 0 | 303 | 83 | 0 | 0 | 0 | **387** | 57 |
| Dinero Simple | 0 | 93 | 0 | 0 | 0 | 0 | **93** | 15 |

### Base

| Brand | YouTube long-form | Products | Affiliates | Email (referrals, sponsors) | Tax Club | B2B | Total | Month 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MMS | 0 | 4,187 | 2,087 | 706 | 0 | 0 | **6,979** | 1,198 |
| Scam Decoded | 0 | 1,769 | 391 | 329 | 0 | 1,566 | **4,055** | 757 |
| 1099 Money | 0 | 3,656 | 1,108 | 395 | 990 | 0 | **6,150** | 916 |
| Dinero Simple | 0 | 1,032 | 185 | 109 | 0 | 0 | **1,327** | 223 |

### Optimistic

| Brand | YouTube long-form | Products | Affiliates | Email (referrals, sponsors) | Tax Club | B2B | Total | Month 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MMS | 8,342 | 25,027 | 15,653 | 5,866 | 0 | 0 | **54,888** | 9,323 |
| Scam Decoded | 2,104 | 12,076 | 3,522 | 3,824 | 0 | 4,482 | **26,009** | 4,455 |
| 1099 Money | 5,390 | 23,626 | 9,237 | 4,302 | 6,188 | 0 | **48,742** | 7,638 |
| Dinero Simple | 1,184 | 6,316 | 1,112 | 1,644 | 0 | 0 | **10,255** | 1,794 |

**Running costs** (from PR #3): about $30-45 a month lean, $80-130 standard. In the conservative case that
means **the content business roughly breaks even in year 1**, which is why PR #3 leads with the ad studio.

## 5. What moves these numbers most

1. **Products live on time and the email list growing.** Products are more than half of every scenario.
   Each brand's lead magnet, welcome sequence and thank-you page (all drafted) need to be live from launch.
2. **Affiliate approvals.** MMS's affiliate line is $0 until programs approve us and the placeholder links
   are replaced. Apply as soon as the sites are live (`affiliate-kit-and-articles`).
3. **Long-video retention.** Watch hours, not uploads, decide YPP. An extra minute of average watch time
   on MMS moves YPP from month 12 to month 11 in the base case (about 11,000 hours in year 1 instead of 8,850). The Scam Decoded fixes in
   `youtube-policy-review-nov-2026.md` matter for this too.
4. **B2B outreach.** Three credit unions at $99 a month equal about 60 Etsy orders a month. Dhruv sends every
   email.
5. **1099 Money's tax season.** January to April is a quarter of its year. The Tax Club waitlist and the 15
   Jan payment content must be live by late December.

## 6. Check against reality

At months 3 and 6, replace the inputs with actuals from `factory report`, Etsy stats, Gumroad and the
email tool, and re-run `revenue_model.py`. Rule of thumb: if month 3 is below the conservative line on
email subscribers and Etsy orders, change formats and products before adding volume.

## Sources

- RPM: [OutlierKit RPM benchmarks, 19 Aug 2026](https://outlierkit.com/resources/youtube-rpm-benchmarks/)
  (Virlo personal finance CPM $15-25); [GoFaceless, 13 Oct 2026](https://www.gofaceless.ai/blog/faceless-youtube-long-form-video-rpm).
- Newsletter sponsors: [SenderCircle finance rates, 2026](https://sendercircle.com/guides/finance-newsletter-advertising-rates)
  ($18-30 per 1,000 opens); [Dupple, rebuilt 4 Nov 2026](https://dupple.com/learn/newsletter-advertising-cost-2026)
  (market range $10-150 CPM, no small-list rates published).
- YPP and Shorts thresholds: YouTube Official Blog, 10 Aug 2026 (`youtube-policy-review-nov-2026.md`).
- Etsy fees and pricing norms: `bfcm-plan-2026.md`. Product prices: PRs #6, #9, #10, #11.
