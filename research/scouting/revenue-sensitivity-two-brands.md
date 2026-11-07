# Which inputs move the two-brand base case, and the free way to move each

Written 2026-11-07. **Docs only. Nothing is spent.** This goes with the **Sensitivity** sheet in
`two-brand-revenue-model-2027.xlsx`. Each input was moved 25% down and 25% up for both brands, with everything
else held at Base. The base case's year-1 net is **$4,614**. The numbers come from a Python copy of the
spreadsheet's formulas in `revenue_model_two_brands.py`, and LibreOffice gave the same result on a test change
($5,469 from both). **B2B isn't in this model**, so the B2B close rate isn't ranked here. It's in
`revenue-model-2027.md`.

## The ranking

| Rank | Lever (inputs) | ±25% moves year-1 net by | The cheapest no-spend action |
|---|---|---|---|
| 1 | **Affiliate earnings**: clicks × click-to-signup rate × payout. Each of the three moves net by the same amount, because they multiply | **±$578 each** (12.5%) | Put **one matched offer box on the results page of the three most-used free tools** (scam checker → Aura or a password manager; subscription audit → a bill-cutting or HYSA link; tax tools → Keeper). Use the program with the higher payout where two fit (Aura's $65 beats a $20 bank bounty). Add the disclosure line next to the box. And apply to Impact and CJ this week, because every month without approval is a month at $0 |
| 2 | **Net per email order** (the price mix of what the welcome sequence sells) | −$336 / +$336 | Make the **day-7 welcome offer the bundle**, with the $5 single as the fallback link, rather than the other way round. This needs no new product: the bundles already exist in the catalog |
| 3 | **Email list size** | −$336 / +$277 | **"Email me this plan"** under every free tool result, and fix the gap where the apps post to Netlify Forms but nothing sends people on to Sender's double opt-in (`email-list-from-zero.md`). The upside is smaller than the downside because 25% more subscribers takes the two lists past **2,500 together**, and that's when Sender starts charging. It's a good problem, but plan for it |
| 4 | **Etsy and Gumroad orders** | ±$292 | **Fix the listings before January**: name the item in the first line of the description, add photos 4-5, and shorten the 8 long titles (`etsy-seo-playbook.md`). January is the peak for budget templates, and these fixes are free |
| 5 | **Long-form YouTube views** (MMS 20,000 a month by month 12) | $0 / **+$250** | **Search-first titles** on the long videos (`keywords-mms-first-30.md`), end screens on every long video, and each Short's related-video link pointing at a long one. The effect is lopsided: 25% fewer views costs nothing (we're not in YPP either way), but 25% more gets MMS into YPP. **2.5× the views is worth +$939** |

Just outside the top 5: broadcast conversion and broadcast count (±$211 each) and welcome-sequence
conversion (±$126). YouTube RPM, subscribers, every TikTok input, Shorts and sponsor rates all show
**$0**, because no 25% change gets either brand through YPP, Creator Rewards or the 2,500-subscriber
sponsor floor in the base case. Working on those first would be working on the wrong thing.

## Changes in timing and behaviour (the "What-ifs" table on the sheet)

| What-if | Year-1 net | Change |
|---|---:|---:|
| **Faster early growth** (growth curve exponent 1.0, not 1.5) | $5,850 | **+$1,235** |
| **Slower early growth** (exponent 2.0) | $3,904 | **−$711** |
| Long-form views ×2.5 | $5,553 | +$939 |
| **Broadcasts doubled to 8 a month** | $5,458 | **+$843** |
| Scam Decoded launches with MMS, not two weeks later | $4,897 | +$282 |
| Affiliate approval two months late (month 5) | $4,484 | −$131 |
| Affiliate approval a month early (month 2) | $4,640 | +$25 |

The biggest single swing is **how fast the first three months go**, not any one rate. That favours
posting every day without gaps and replying in the first hour (`growth-90-days-two-brands.md`) over adding
platforms. **Doubling broadcasts** is the cheapest big lever. The factory already writes them, so a second
weekly email costs only review time. Watch unsubscribes: if they go above 0.5% per send, go back to weekly
(`launch_thresholds.json`). The +$282 for launching both brands together is **not** a recommendation. The
two-week gap is there to protect Dhruv's time (`DHRUV_DECISIONS.md` row 2b).

## The top 3 actions (also in `DHRUV_DECISIONS.md`, rows 22a-22c)

1. **Offer boxes on the three most-used free tool result pages**, with disclosure, plus the Impact and CJ
   applications this week. This covers lever 1, worth about **$580** for each 25% change in clicks, conversion or payout.
2. **Day-7 welcome offer leads with the bundle**, and **a second broadcast each week** if unsubscribes stay
   under 0.5%. These cover levers 2 and 6, worth about **$340 + $840**.
3. **"Email me this plan" on every tool result**, plus the Netlify Forms → Sender fix. This covers lever 3,
   worth about **$280-340**.

These overlap, so don't add the dollar figures together. Each one is the change on its own, with
everything else at Base.
