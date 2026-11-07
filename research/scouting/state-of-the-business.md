# State of the business: one page for Dhruv

As of **2026-11-07, 06:50 UTC** (merge status from `GO_LIVE.md`'s 06:30 UTC check). Nothing has been posted, sent, charged or signed up for. Every step that
touches the outside world is yours to press. The full step-by-step checklist is `docs/GO_LIVE.md` (PR #7);
this page is the short version and adds the open decisions from the scouting research (PR #2).

## What's built

| Area | What exists | Where |
|---|---|---|
| **The factory** | Scripts with guardrails and fact-check flags, a free Kokoro voice or your own recorded voice, word-accurate captions, charts, renders, a review and approve queue, one calendar for every brand, official-API publishers for YouTube, Instagram, Facebook and Threads, TikTok posting packages for posting by hand, `factory launch-check`, `factory stats`, and a local `/today` page | `main` (already merged) |
| **Four brands** | **Money Made Simple:** site, lead magnet, 10-email welcome sequence. **Scam Decoded:** content through 31 Jan, site, products. **1099 Money:** 5 months of content, calculators, products. **Dinero Simple:** Spanish support and the brand | PRs #4, #9, #10, #11 |
| **Products** | Six Money Made Simple products ($5-39), plus product ladders for Scam Decoded and 1099 Money, Etsy listings and printables | PRs #6, #9, #10 |
| **Ad studio** (fastest money) | A portfolio, a $49/$99 listing-video order page, and written leads and pitches | PR #12, `docs/GO_LIVE.md` stage 2 |
| **Money plan** | Financial model, affiliate application kit, and 20 affiliate articles | PRs #3, #5 |
| **Research** | 42 research files: platform rules, email tool, launch playbook, API access, sponsors, competitors, open-source tools, Instagram growth, YouTube SEO, Actual Budget tutorials, forkable apps, product ideas, a receipt tracker plan, Nov 2026 formats, a Black Friday plan, a YouTube policy review, a revenue model by brand with a B2B scenario, an Etsy SEO playbook and listing audit, a Pinterest playbook and pin audit, a 30-day metrics plan, free pipeline tools round 3, a Spanish creator landscape for Dinero Simple, affiliates that accept new creators, newsletter sponsor benchmarks, a January pricing check, AI-label rules on 7 platforms, B2B pricing benchmarks, faceless Instagram and TikTok accounts | PR #2 |

**12 pull requests are open and none are merged yet.** `docs/GO_LIVE.md` lists a merge order. PR #2 is now
up to date with `main` and passes its tests.

## Blocked on you (decisions only you can make)

| # | Decision | Recommendation | Why it blocks |
|---|---|---|---|
| 1 | **Merge the PRs** (#1 → #3 → #2 → #4 → #5 → #6 → #8 → #9 → #11 → #10 → #12 → #7) | **Safe now, in this order: #1, #3, #2, #4, #8, #12, #7.** They were merged together on top of `main` and all tests passed (`GO_LIVE.md`, 06:30 UTC check). Hold #5, #6, #9, #11 and #10 until GitHub shows them green; their threads are fixing conflicts | Most of the work above isn't on `main` until you do |
| 2 | **Brand names**: Scam Decoded (not "Scam Shield", which is a T-Mobile trademark)? Keep "Money Made Simple" (a crowded name)? | Yes to Scam Decoded. Keep MMS as a content brand, but don't trademark it | Domains, handles and the email setup all wait on the names |
| 3 | **Domains**: did you register `1099money.com` or `getmoneymadesimple.com`? If not, buy the free alternatives | `mymoneymadesimple.com`, `getscamdecoded.com`, `the1099money.com`, `eldinerosimple.com` (unregistered on 7 Nov) | Email authentication, Search Console and the Pinterest claim all need the final domain |
| 4 | **Email tool**: Kit's free plan no longer runs welcome sequences | **Sender Free** (2,500 subscribers and full automations free), or Kit Creator at $33/mo per brand | The welcome sequences carry the day-7 product pitch |
| 5 | **Your time**: about 15 minutes per brand per day for replies, and about 2 minutes per TikTok to post it by hand | If that's too much, launch 2 brands this month, not 4 | The launch playbook assumes it |
| 6 | **Your voice**: record narration for the TikTok and long-video cuts? | Yes, for the first videos of each brand | It's the cleanest fix for TikTok's AI-only and YouTube's inauthentic-content risks |
| 7 | **Ad budget**: organic only for now? | Organic until the 5-point gate in `paid-acquisition.md` passes | It stops spending before the numbers support it |
| 8 | **Smaller calls:** merge the salary and debt pages (an SEO risk)? Which sponsor-relevant products do you really use? Is the $75 sponsor floor right? | Yes to the merge. The other two are yours to answer | These are site-thread work and later sponsor pitches |

## Top 5 actions, in order

1. **Merge #1, #3, #2, #4, #8, #12 and #7, in that order.** About 15 minutes. The other five (#5, #6, #9,
   #11, #10) have conflicts or failing site tests that their threads are fixing; merge them after, in the
   `GO_LIVE.md` order, once GitHub shows them green.
2. **Set up identity and payments** (`GO_LIVE.md` stage 1): business email with 2FA, a postal address you're OK
   publishing (CAN-SPAM requires one), and Gumroad and Stripe verified with payout and tax forms. About 1 hour
   15 minutes, and verification can take a day or two, so start tonight.
3. **Decide the names, then register the four domains and reserve the handles** (decisions 2 and 3,
   `domains-and-names.md`). About 45 minutes. Everything downstream points at the domain.
4. **Start the ad studio pitches and list the six products** (`GO_LIVE.md` stages 2 and 3). Those are the two
   ways to earn this month. Pitches start Tue 10 Nov, about an hour a day. Create the Gumroad discount codes
   before the first sale.
5. **Launch 1099 Money and Money Made Simple first** (`launch-playbook.md` week 1):
   - Pick the email tool (decision 4) and authenticate the domain.
   - Make the accounts in the playbook's order.
   - Set up YouTube's API as a personal-use app (`api-applications.md`: no audit needed since 2 Nov).
   - Post the first week by hand at half cadence.

   1099 Money first, because the 15 Jan 2027 tax payment is its best moment.

## What happens without you, and what doesn't

The threads keep fixing PR conflicts, writing content and researching. Nothing goes live, nothing is sent,
and no money comes in until steps 1-5 are done. The first dollar is most likely an ad studio order or a $5-12
product sale in week 1-2 after launch. Platform payouts (YouTube, TikTok) come months later.

## What the content business could earn in year 1

From `revenue-model-2027.md` (all four brands, after platform fees, ad studio not included; PR #3 models it):

| | Conservative | Base | Optimistic |
|---|---:|---:|---:|
| Content, month 12 (Oct 2027) | about $200/mo | about $2,800/mo | about $22,600/mo |
| Content, year 1 | about $1,300 | about $17,600 | about $138,000 |
| B2B packs (PR #13), year 1 | about $50 | about $700 | about $6,700 |

- **Products are the biggest line** in every case. YouTube Shorts pays $0 (10M views per 90 days needed),
  and YouTube long-form ads are $0 in year 1 in the conservative and base cases: new YPP applicants need
  8,000 watch hours from 1 Feb 2027 (YouTube blog, 10 Aug 2026; it's 4,000 until then).
- **B2B cold email closes slowly:** public benchmarks put it near 1 paying customer per 350 emails. The base
  case (1 per 250) gives about 2 paying organizations by Oct 2027. Referrals from partners are the lever.
- What moves it most: products and email live at launch, affiliate approvals, long-video watch time, and
  the B2B emails you send.
