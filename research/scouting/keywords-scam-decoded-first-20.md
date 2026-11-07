# Scam Decoded: search phrases and news hooks for the first 20 posts

Written 2026-11-07. **Docs only.** The sheet is `keywords-scam-decoded-first-20.csv`. It covers the first
20 posts in Scam Decoded's 14-day plan (PR #9's `POSTING_PLAN.md`): the 14 topics that each go out as a
Short/Reel plus a TikTok cut, and 6 of the carousels. Titles are from PR #9's `content.json` as of today,
after `TITLE_RENAMES_2026-11-07.json`.

Each phrase is how people search for that scam, chosen the same way as `keywords-mms-first-30.md`.
Autocomplete can't be reached from here, so the CSV's last column is for the same 10-minute check by hand
in YouTube's and Pinterest's search boxes. **The news hooks are real and dated:** FTC consumer alerts
(read today) and BBB alerts.

## TL;DR

- **8 of 20 titles already contain the searched phrase and 10 are close.** Scam titles fare better than
  MMS because people search by the scam's own name ("toll text scam", "bitcoin atm scam"). The fix is
  mostly word order: **put the scam's name first, then the number hook**. For example, "Task job scam: 0
  real jobs make you pay to get paid". That also cuts the long Shorts titles flagged in
  `youtube-seo-playbook.md`.
- **Five news hooks fit posts we already have:**
  - SIM-swap post: the FTC's **22 Oct 2026** alert, "The FTC is not calling to deactivate your phone number".
  - Parking-QR post: the FTC's **3 Sep 2026** alert, "See a QR code parked somewhere? Don't scan it…yet!".
  - Parents carousel: the FTC's **4 Nov 2026** report on protecting older adults.
  - Bank-impostor post: the FTC's **2 Nov 2026** request to report impostor ads.
  - Task-job post: employment scams were #3 in BBB Chicago's 2026 top-10, and their reports more than doubled.
- **Five scams are in the news this week with no post in the first 20.** Each becomes a Short:
  - **Ghost tapping** (BBB, 3 Nov 2026): a contactless charge rung up for much more than quoted, e.g. a
    $15 purchase that became $1,500.
  - **Fake ads impersonating companies and agencies** (FTC, 2 Nov).
  - **Fake charity sweepstakes** (FTC, 26 Oct). Giving Tuesday is 1 Dec.
  - **Open-enrollment health insurance scams** (FTC, 28 Sep and 29 Oct). Marketplace open enrollment runs
    to 15 Jan.
  - **Hidden fees on holiday travel bookings** (FTC, 3 Nov). This one is junk fees, not a scam, so it fits MMS better.
- **Online purchase scams are BBB Chicago's #1 for the sixth year running.** The Black Friday fake-shop
  alert card (23 Nov) covers it. Give it a search title: "fake online store scam: 3 checks before you buy".

## The 20 posts

| Day | # | Current title | Target phrase | Fit | Suggested title | In the news |
|---|---|---|---|---|---|---|
| D1 | #1/#15 | $0 and 10 minutes: freeze your credit tonight | how to freeze your credit | match | keep | Evergreen; FTC older-adults report (4 Nov 2026) |
| D2 | #3/#17 | 1 family safe word beats an AI voice clone | ai voice cloning scam | partial | AI voice clone scam: 1 family safe word stops it | BBB/FTC family-emergency alerts; our 19 Nov alert card |
| D3 | #2/#16 | That $3.95 'unpaid toll' text is a trap | toll text scam | match | keep | Ongoing toll-text wave |
| D4 | #4/#18 | 0 real banks ask you to move money to keep it safe | bank impersonation scam | partial | Bank impersonation scam: 0 real banks ask you to move money | FTC impersonator ads alert (2 Nov 2026) |
| D5 | #12/#26 | $110 million+ lost at Bitcoin ATMs in one year | bitcoin atm scam | match | keep | FTC older-adults report (4 Nov 2026) |
| D6 | #7/#21 | Read back a 6-digit code and you hand over your account | verification code scam | partial | Verification code scam: never read back a 6-digit code | BBB marketplace-code alert; our 18 Nov card |
| D7 | #0/#14 | 3 ways to pay that only scammers insist on | gift card scam | partial | Gift card scam: 3 ways only scammers ask to be paid | Holiday gift-card draining (our 16 Nov card) |
| D8 | #9/#23 | 2 minutes to lock your number against SIM swaps | sim swap scam | match | keep; add a line on the fake 'FTC deactivating your number' call | FTC: 'not calling to deactivate your phone number' (22 Oct 2026) |
| D9 | #6/#20 | 1 question kills the fake delivery text | usps text scam | partial | Fake USPS delivery text: 1 question kills it | Holiday delivery texts (our 24 Nov card) |
| D10 | #10/#24 | 0 real jobs make you pay to get paid | task job scam | partial | Task job scam: 0 real jobs make you pay to get paid | BBB Chicago: employment scams #3, reports more than doubled |
| D11 | #8/#22 | The $500 overpayment check that bounces on you | fake check scam | partial | Fake check overpayment scam: the $500 that bounces | Marketplace selling season |
| D12 | #11/#25 | 1 pop-up, 1 phone number, 0 real tech companies | tech support scam | partial | Fake virus pop-up? The tech support scam explained | Our 26 Nov alert card |
| D13 | #5/#19 | 7726: the free number to forward scam texts to | how to report scam texts | match | keep | FTC 'Did you spot a scam?' (28 Aug 2026) |
| D14 | #13/#27 | 2 checks before you scan a parking meter QR code | qr code scam | match | keep | FTC: 'See a QR code parked somewhere?' (3 Sep 2026) |
| D3 | #28 | 5 red flags in one scam text | how to spot a scam text | partial | How to spot a scam text: 5 red flags | BBB Chicago: phishing #2 |
| D5 | #30 | 7 scams aimed at your parents right now | scams targeting seniors | partial | 7 scams targeting seniors right now | FTC older-adults report to Congress (4 Nov 2026) |
| D12 | #31 | Scammed? The first 60 minutes, in order | what to do if you get scammed | match | keep | FTC 'Did you spot a scam?' |
| D8 | #32 | 5 locks every account should have | how to protect your accounts | gap | How to protect your accounts: 5 locks to turn on | Evergreen |
| D7 | #33 | 6 questions before you send money to anyone | is this a scam | gap | Is this a scam? 6 questions before you send money | BBB Chicago: online purchase scams #1 |
| D10 | #34 | The 'wrong number' text that ends in a fake crypto app | wrong number text scam | match | keep | Ongoing |

## New Shorts for the scams in the news (for the Scam Decoded thread)

| Target phrase | Hook source | Angle | When |
|---|---|---|---|
| ghost tapping scam | [BBB alert, 3 Nov 2026](https://www.aol.com/articles/bbb-consumer-alert-ghost-tapping-160000000.html) | "Check the amount and the merchant name before you tap", plus transaction alerts. The BBB adds that an RFID sleeve doesn't help when you hand over your own card | Before Black Friday (markets, pop-ups, charity collectors) |
| fake ads scam / impostor ads | [FTC, 2 Nov 2026](https://consumer.ftc.gov/consumer-alerts/2026/11/tell-ftc-about-imposter-ads-online) | An ad that looks like your bank or a government agency. Go to the site yourself, and report it to the FTC | Any week |
| charity sweepstakes scam | FTC, 26 Oct 2026 | "You won a charity's sweepstakes, pay the fee". Real prizes never cost money | The week of Giving Tuesday (1 Dec); pair it with the 25 Nov fake-charity alert card |
| health insurance scam open enrollment | FTC, 28 Sep and 29 Oct 2026 | Only HealthCare.gov or your state's marketplace. Watch for "plans" that aren't insurance | Before 15 Dec (the deadline for 1 Jan coverage; check HealthCare.gov) |
| fake online store | BBB Chicago 2026 top 10 (#1) | Domain age, payment method, and reviews off the site | Already on the 23 Nov card. Make a searchable Short from it |

**Rules unchanged:** no real phone numbers or links on any slide, figures cited to the alert, and each
alert linked in the description.

## Sources

Read 2026-11-07:
[FTC consumer alerts](https://consumer.ftc.gov/consumer-alerts) (titles and dates for 22 Oct, 26 Oct, 2 Nov, 3 Nov, 4 Nov, 3 Sep and 28 Aug 2026);
[FTC: Tell the FTC about imposter ads online](https://consumer.ftc.gov/consumer-alerts/2026/11/tell-ftc-about-imposter-ads-online);
[FTC: The FTC is not calling to deactivate your phone number](https://consumer.ftc.gov/consumer-alerts/2026/10/ftc-not-calling-deactivate-your-phone-number);
[FTC: New report on protecting older adults](https://consumer.ftc.gov/consumer-alerts/2026/11/new-report-ftcs-work-protect-older-adults);
[BBB consumer alert: ghost tapping](https://www.aol.com/articles/bbb-consumer-alert-ghost-tapping-160000000.html) (3 Nov 2026);
[BBB Chicago top 10 scams for 2026](https://www.yahoo.com/news/articles/bbb-research-reveals-top-10-150424702.html);
PR #9's `POSTING_PLAN.md`, `content.json` and alert cards.
