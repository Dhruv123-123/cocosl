# Pinterest launch playbook for Money Made Simple

Written 2026-11-07. **Docs only.** This turns `pinterest-playbook-2026.md` (keywords, the 8-board plan,
cadence, the audit of 206 pins) into a launch checklist. It adds two things that file didn't cover: **how
many fresh pins a week the free schedulers let us post**, and which pin formats to make first. Dates
follow `two-brand-launch-plan.md`, where MMS accounts open in week 1 (from 16 Nov).

## TL;DR

- **Use Pinterest's own scheduler, which is free but holds only 10 future pins, up to 30 days ahead**
  (Buffer's and TimeToPost's write-ups, Aug-Sep 2026; Pinterest's Help Center didn't load here). Topping it
  up twice a week supports **1-2 fresh pins a day**, which is the rate the playbook recommends anyway.
  Tailwind's own guide now says "about 1-5 fresh pins a day", and calls the old 15-25 a day outdated.
- **The free third-party schedulers don't add much:** Buffer Free queues 10 posts per channel, Publer Free
  10 per account, Metricool Free 20 posts a month. None beats the native queue for one Pinterest account.
  The source doesn't confirm Pinterest is included on any of those free tiers, so check before relying on one.
  The factory's own Pinterest API route needs Standard access and a demo video (`meta-pinterest-api.md`).
- **Fresh pins per week:** weeks 1-2: **4 a week**; weeks 3-4: **7 a week**; from week 5: **10-14 a week**
  (2 a day at most). The 206 pins in PR #4 cover about 15-20 weeks at that rate. Don't post them faster.
- **Formats to lead with (finance):** a 2:3 image with a number or checklist on it (1000×1500), then a
  9:16 video (1080×1920, 720p+) cut from the Shorts, then collages for "5 printables" product pins.
  Pinterest's own fundamentals page recommends a mix of image, video and collage, vertical formats, and
  keywords in the title and description.

## Launch checklist (week 1, about 45 minutes)

1. **Business account** with the brand email; name "Money Made Simple: budgeting & saving"; short bio with
   the search phrase "budgeting for beginners". 5 min
2. **Claim the website** (Settings > Claimed accounts). Needs the final domain (`domain-plan.md`). It
   attributes saves and clicks to us. 10 min
3. **Create the 8 boards** from `pinterest-playbook-2026.md`, with its draft descriptions. Leave the two
   seasonal boards secret until 1 Dec. 15 min
4. **First pins: 4 this week**, one per evergreen board, each linking to the page it promises (not
   `/shop/`): the 20-Minute Budget page, the emergency-fund calculator, the savings challenges, the
   budgeting-apps comparison. Use the search-first titles in `keywords-mms-first-30.md`. 15 min

## Pin formats that work for money content now

| Format | Make it from | Why | Share of pins |
|---|---|---|---|
| **Checklist or number image** (2:3) | Carousel slide 1, the "number on the image" style | Saved for later, which is Pinterest's core use. The playbook found titles of only "Name ($price)" don't get searched | ~60% |
| **Short video** (9:16, 6-15 s, no music needed) | The first 10 seconds of each Short, with the title on screen | Pinterest suggests video for tutorials and step-by-steps. It's also our cheapest fresh content | ~25% |
| **Product collage** (2:3, 3-5 page previews) | Etsy/Gumroad listing images | For printables: show the pages, the price in the description, and the link to that listing | ~15% |

**Rules carried over from the playbook:** the same URL no more than once every 7 days, 10 boards at most
per pin over its life, unique text for each design, and seasonal pins 30-45 days ahead. Judge a pin at
30 days.

## The first 8 weeks

| Week (from) | Fresh pins | Focus |
|---|---|---|
| 1 (16 Nov) | 4 | One per evergreen board (above) |
| 2 (23 Nov) | 4 | Holiday budget, BNPL, 72-hour rule (match the week's Shorts) |
| 3 (30 Nov) | 7 | Open the **Savings challenges** and **2027 budget planner** boards (1 Dec) |
| 4 (7 Dec) | 7 | Sinking funds, a no-spend January, the 52-week challenge |
| 5 (14 Dec) | 10 | January reset; the 2027 planner; video pins start |
| 6 (21 Dec) | 10 | Queue two weeks ahead before the holidays (the native queue's 10-pin cap means two top-ups) |
| 7 (28 Dec) | 10-14 | New year budget, net worth (a gap in `keywords-mms-first-30.md`) |
| 8 (4 Jan) | 10-14 | Peak "budget planner" month. Judge week 1-4 pins (30-day rule) |

**Time:** about 10 minutes, twice a week, to top up the native queue: copy the title, description and
link from PR #4's `pins.csv` and upload the image.

## Sources

Read 2026-11-07:
[Pinterest: content fundamentals](https://create.pinterest.com/fundamentals) (formats, sizes, cadence);
[Buffer: how to schedule Pinterest posts](https://buffer.com/resources/schedule-pinterest/) (native scheduler: 30 days ahead, 10 future pins);
[TimeToPost: Pinterest native scheduler limits](https://timetopost.co/blog/pinterest-native-scheduler-limits/) (24 Aug 2026; same limits);
[Tailwind: Pinterest scheduling guide](https://support.tailwindapp.com/en/articles/15621048-pinterest-scheduling-with-tailwind-the-complete-guide) (1-5 fresh pins a day; pin spacing);
[The Stacc: free scheduler limits](https://thestacc.com/best/free-social-media-scheduling-tools/) (5 Nov 2026: Buffer, Publer, Metricool free limits);
`pinterest-playbook-2026.md`, `meta-pinterest-api.md` on PR #2; PR #4 `pins.csv`.
