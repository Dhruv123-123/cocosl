# Ten more products and tiny apps, ranked by effort against demand

Written 2026-11-07. **Docs only. Nothing built or listed.** This is round 2 after `competitor-product-gaps.md`
(GoodNotes planner, wedding sheet, ADHD-friendly budget, Spanish Sheet, net-worth dashboard) and
`product-ideas-beyond-content.md`. It checks each idea against the 121-row catalog (`launch/PRODUCTS_CATALOG.csv`
on PR #6) so nothing here duplicates what we already make.

**Demand signals used (all public):**
- **Etsy:** RankHero keyword pages give monthly Etsy searches, listing counts, median price and a
  12-month trend. Their two counts per top listing aren't labelled (probably reviews and sales), so we
  only say "large" or "small".
- **App Store:** GetAppNiche's 28 Oct 2026 snapshot of iOS Finance apps, which counts apps earning $1K+
  a month per keyword. It shows supply only, with no search volume.

No marketplace publishes raw sales. Treat every figure as directional.

## TL;DR: the ranking

Demand is Etsy searches a month (or App Store winners). Effort is our estimate in hours, using the
factory's PDF and Sheets builders.

| # | Idea | Brand | Demand signal | Effort | Price | Verdict |
|---|---|---|---|---|---|---|
| 1 | **"If something happens to me" planner** (accounts, bills, insurance, passwords-location, wishes) | MMS | "end of life planner": **6,600** searches, **+50%** in a year, 3,792 listings, median **$12.96** | Low (6-8 h, PDF + fillable) | $12-15 | **Build first** |
| 2 | **Moving kit**: moving checklist + moving budget | MMS | "moving checklist": **14,800** searches, **+50%**, only 6,532 listings, keyword difficulty 27 (easy), median $4.99 | Low (4-6 h; the budget reuses the wedding sheet) | $5 checklist, $9 with budget | **Build second**, before the May-Aug moving peak (`seasonal-demand-feb-jun-2027.md`) |
| 3 | **Sinking funds Google Sheet + Notion** (we only have a $4 printable) | MMS | "sinking funds": **27,100** searches, keyword difficulty 30 (easy), peak 40,500 in January; median $4.99. "sinking funds spreadsheet" itself is only 70 | Low (3-4 h) | $7 | **Build by 20 Dec** for the January peak |
| 4 | **Mileage log** (printable + Sheet with the IRS rate cell) | 1099 Money | "mileage log": **2,400** searches, 67% US, 7,497 listings, median $7.50; peak in March (tax season) | Low (3-4 h) | $5 printable, $9 Sheet | **Build when 1099 launches**; the driver mileage page already exists |
| 5 | **Household emergency binder** (contacts, documents, medical, utilities, fraud-alert numbers) | Scam Decoded / MMS | "emergency binder": 590 searches, **+50%**, median $12; "family binder" 170. Top listings have very large counts | Low (5-6 h) | $12 | Build, or fold into #1 as a $19 bundle |
| 6 | **Large-print password and account log** | Scam Decoded | "password log": 1,300 searches, only **2,703** listings (searches high relative to listings) | Low (2-3 h; KDP and PDF) | $5 PDF; KDP paperback | Build, with the safety note below |
| 7 | **Kids' chore and allowance chart** ("earn, save, spend, give") | MMS | "chore chart": **18,100** searches but **50,894** listings (crowded); "allowance tracker" 170 searches, 1,447 listings | Low (3 h) | $4 | Maybe. Only as a money-lesson angle, not a generic chore chart |
| 8 | **Subscription tracker, web first** (reminders before renewals) | MMS (apps) | iOS: "subscription tracker" has **12 apps earning $1K+/mo**, with a median of only **52 ratings**, the smallest incumbents in the list | Medium (the budget app already has `subscriptions.html`; reminders need email) | Free lead magnet first | Build as a free tool. An iOS app needs Apple's $99/yr developer fee, which is spend |
| 9 | **Bill reminder calendar, web first** | MMS (apps) | iOS: "bills" has **17 winners**, median **80 ratings** | Medium | Free, then Pro | After #8 if #8 gets signups |
| 10 | **Solo 401(k) / SEP-IRA contribution calculator** | 1099 Money (apps) | Weak public signal (a listicle; no data we can verify). It fits the freelance-tax app's audience | Low-medium (the calculator framework exists; the 2027 limits must be checked on irs.gov) | Free | Only with 1099 Money; it's a lead magnet, not a product |

**Parked:** a kids' allowance app (25 iOS apps, 2 earning $1K+, median 14 ratings, so tiny on both sides).
Apps for children also raise COPPA duties. A Spanish moving or emergency kit waits for the reviewer,
like all Spanish copy.

## Notes per idea

1. **"If something happens to me" planner.** The fastest-rising search we found. It's a fill-in
   organiser, not a will. The listing and every page must say so: "This isn't a legal document. Talk to an
   estate lawyer about a will." No state-specific legal forms. The fill-in pages are ours; any explanatory
   text must be written or rewritten by a person, under Etsy's 22 Oct 2026 rule on AI-generated functional
   guides (`ai-disclosure-rules-nov-2026.md`).
2. **Moving kit.** Demand is rising and competition is low: 2.3 searches per listing, compared with 0.36
   for chore charts. It pairs with the May-Aug moving peak and Scam Decoded's rental-scam posts. Pin it
   from April.
3. **Sinking funds Sheet.** The searches are mostly for the concept, and the top related tags are savings
   tracker and cash stuffing. Our printable already ranks for the tag. A Sheet and a Notion version are a
   cheap upsell and add a Gumroad item. Bundle it into the January Reset Bundle.
4. **Mileage log.** 1099 Money's driver content already points here. Keep the IRS standard mileage rate in
   one labelled cell, to update each January (check irs.gov). No tax advice beyond "keep a log".
5. **Emergency binder.** It overlaps #1, so test them as two listings and a bundle. Scam Decoded's angle is
   a "fraud-alert contacts" page: the bureaus' freeze pages, the bank's number from the back of the card,
   and reportfraud.ftc.gov. All real organisations, with no phone numbers printed that could go stale.
6. **Password log.** Security experts prefer password managers, and our own posts say so. Sell it honestly
   as "for people who won't use an app", with tips on the cover page: keep it at home, never in a wallet,
   and turn on two-step logins. Large print suits the Scam Decoded for Seniors line. It's also a classic
   KDP low-content format.
7. **Chore and allowance chart.** Chore charts are crowded, so only the money angle stands out. Make it a
   companion to an MMS "money lessons for kids" post. Low priority.
8-9. **Web-first apps.** The App Store evidence says small apps in these keywords earn with small
   incumbents. We don't have to pay Apple to test the idea: ship it in `apps/budget` as a free tool, and
   use the "email me before it renews" reminder as the signup (`email-list-from-zero.md`). Consider iOS
   only after the web tool has users. That's Dhruv's $99 call.
10. **Solo 401(k) calculator.** Self-employed retirement limits change every year. Check the 2027 figures on
   irs.gov when the IRS publishes them, and label it "estimate".

## Build order, if the product thread takes these on

| By | Build | Why then |
|---|---|---|
| 20 Dec 2026 | #3 sinking funds Sheet + Notion | January is the peak (40,500 searches) |
| 15 Jan 2027 | #1 "if something happens to me" planner, #5 emergency binder | Steady demand. Searches peaked in May and August, so list early to build reviews |
| 1 Mar 2027 | #2 moving kit | The moving peak runs May-Aug, and Etsy listings need time to rank |
| With 1099 Money | #4 mileage log, #10 calculator | Brand 3 (`two-brand-launch-plan.md`); mileage searches peak in March |
| Any time | #6 password log (KDP + PDF) | Low effort; fits the Seniors line |
| After list growth | #8, #9 web tools | Lead magnets first |

## Sources

Read 2026-11-07:
[RankHero: end of life planner](https://www.rankhero.com/keywords/end-of-life-planner) (3 Oct 2026);
[moving checklist](https://www.rankhero.com/keywords/moving-checklist) (3 Sep 2026);
[sinking funds](https://www.rankhero.com/keywords/sinking-funds) (8 Aug 2026);
[mileage log](https://www.rankhero.com/keywords/mileage-log) (20 Oct 2026);
[emergency binder](https://www.rankhero.com/keywords/emergency-binder) (31 Aug 2026);
[family binder](https://www.rankhero.com/keywords/family-binder) (4 Jul 2026);
[password log](https://www.rankhero.com/keywords/password-log);
[chore chart](https://www.rankhero.com/keywords/chore-chart) (16 Oct 2026);
[allowance tracker](https://www.rankhero.com/keywords/allowance-tracker);
[bill tracker](https://www.rankhero.com/keywords/bill-tracker) (17 Aug 2026);
[debt tracker](https://www.rankhero.com/keywords/debt-tracker) (25 Oct 2026; we already sell several);
[GetAppNiche: finance app keywords](https://getappniche.com/guides/best-finance-app-keywords-low-competition) (snapshot 28 Oct 2026);
[EHunt: best budget planners](https://ehunt.ai/etsy-competitor-research/best-etsy-budget-planner) (1 Nov 2026);
[BigIdeasDB: app ideas](https://bigideasdb.com/profitable-mobile-app-ideas-2026) (23 Oct 2026; used only as a weak signal for #10);
PR #6 `launch/PRODUCTS_CATALOG.csv` (121 rows).
