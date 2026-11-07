# Gig-driver series: 10 Shorts for Uber, Lyft, DoorDash, Uber Eats and Instacart drivers

`content.json` holds 10 Shorts (script, on-screen text, visuals, caption, hashtags, sources and claims to
check). They pair with the free **driver mileage calculator** on the site (`apps/freelance-tax/mileage/`),
which the captions point to as "in the link in bio". No links in captions.

Every figure is 2026 federal: the 72.5¢ standard mileage rate, the $2,000 1099-NEC threshold, the
$20,000 / 200-payment 1099-K threshold. The worked example everywhere is the same one the calculator
uses: $30,000 of payouts, 15,000 logged miles, single, no W-2 job → a $10,875 deduction, about $2,840 of
federal tax instead of about $5,180, about 9.5% of payouts or 95¢ a delivery over 3,000 deliveries.

## When to post

The main 1099 Money calendar already uses Mon, Tue, Thu, Fri and Sat for Shorts, so this series goes out
on **Wednesdays**, January to March 2027, when drivers are opening their tax forms. Forms come first.

| # | Date | Short | Where drivers will see it (from distribution.md) |
|---|---|---|---|
| 1 | Wed Jan 6 | No 1099 from DoorDash or Uber? You still owe | r/doordash_drivers, r/InstacartShoppers; FB groups in January |
| 2 | Wed Jan 13 | Why your rideshare 1099-K looks too high | Rideshare FB groups (Uber/Lyft); r/couriersofreddit only if asked |
| 3 | Wed Jan 20 | What 15,000 delivery miles are worth at tax time | r/doordash_drivers, r/UberEatsDrivers; FB driver-support groups |
| 4 | Wed Jan 27 | The app's miles aren't all your miles | r/doordash_drivers, r/InstacartShoppers, r/couriersofreddit |
| 5 | Wed Feb 3 | When should a delivery driver start the mileage log? | r/couriersofreddit, r/doordash_drivers |
| 6 | Wed Feb 10 | Running two apps at once? Log the miles once | r/couriersofreddit, r/UberEatsDrivers |
| 7 | Wed Feb 17 | Driver deductions besides mileage | r/InstacartShoppers, r/doordash_drivers |
| 8 | Wed Feb 24 | Delivery tips are income, and there's a new deduction | r/UberEatsDrivers, r/doordash_drivers |
| 9 | Wed Mar 3 | How much to set aside per delivery | r/InstacartShoppers, r/doordash_drivers; FB groups before each deadline |
| 10 | Wed Mar 10 | Full-time driver? You probably owe quarterly taxes | FB driver-support groups before Jan 15 and Apr 15; r/doordash_drivers |

## Rules for the driver communities

- **Post the Short on YouTube, TikTok and Instagram as usual.** In subreddits and Facebook groups, don't
  drop the video link: write the point as a text answer (the answer bank in `../distribution/ANSWER_BANK.md`
  has driver answers ready) and link the calculator only when someone asks for a tool.
- Read each subreddit's rules first. r/doordash_drivers, r/UberEatsDrivers, r/InstacartShoppers and
  r/couriersofreddit are driver-run and remove self-promotion fast.
- Say who you are if it comes up: "I make a small channel about freelancer taxes". Never "DM me".
- Facebook driver-support groups are busiest in January and the week before each quarterly deadline.

## Claims to re-check before posting

- The qualified-tips deduction (Short "Delivery tips are income…"): confirm on irs.gov that the final
  occupation list covers rideshare and delivery drivers, and the $25,000 cap and $150,000 / $300,000
  phase-out, before posting.
- 1099-K contents for rideshare (gross fares vs payouts) differ by platform. Keep the "can show" wording.

Render the cards and voice-ready files as a pack. The pack spreads them over the brand's usual Short days; ignore its dates and post on the Wednesdays above:

```
factory pack export --brand 1099-money --file launch/1099-money/drivers/content.json --start 2027-01-06 --days 14 --out drivers/
```
