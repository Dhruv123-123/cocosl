# Pinterest playbook for our pins, with an audit of the 206 Money Made Simple pins (PR #4)

Written 2026-11-07 from Pinterest's own Help Center, Business site and creator community, plus one
Pinterest marketing partner. **Docs only.** Nothing has been pinned. This extends section 3 of
`pinterest-seo.md`, which covers fresh pins, AI labels and how to post. The site thread (PR #4) owns
`site/pins/` and `site/tools/make_pins.py`.

**What was audited:** `site/pins/pins.csv` and `site/pins/schedule.csv` on PR #4: 206 pins across 44 URLs
and 6 boards, scheduled from 9 Nov 2026 to 7 Jan 2027.

## TL;DR

The pins are well built: 2:3 at 1000×1500, alt text on every pin, UTM tags on every link, no page pinned
before it goes live, and honesty rules. There are five problems, in this order:

1. **118 of 206 pins (57%) all link to one page, `/shop/`.** A pin about the Bill Cut Kit should land on
   the Bill Cut Kit, not on a list of every product. That means a product page or anchor
   (`/shop/bill-cut-kit/`), or the Etsy or Gumroad listing.
2. **104 pin titles are just "Product name ($price)"**, e.g. "The Bill Cut Kit ($5)". Pinterest is a
   search engine: Pinterest says to put "relevant keywords in your Pin title, Pin descriptions, board titles,
   board descriptions". People search "how to lower bills", not "Bill Cut Kit".
3. **98 titles and descriptions are duplicates.** Each URL's "a" and "b" designs share the same text.
   Pinterest warns against uploading "content that already exists on Pinterest". Give every design its
   own title and description.
4. **Pins for the same URL go out 0-1 days apart** (75 of 87 repeat gaps). Space them **at least 7 days
   apart**. At 2-3 pins a day, the schedule can hold that.
5. **"Idea pins vs standard" is no longer a choice.** Pinterest merged Idea Pins into Pins in May 2023,
   and any pin, image or video, can now carry a link. The real choice is **image or video**.
   Recommendation: images for traffic now, and a few short videos for reach once the image pins have
   data.

Also: 70 of the 206 pins have no date yet. Write board descriptions for all 6 boards (the CSV has none),
and add 2 seasonal boards (below).

## 1. The playbook (Pinterest's own guidance first)

### What Pinterest says drives distribution

From [Pin performance and distribution](https://help.pinterest.com/en/business/article/pin-performance-and-distribution)
(Pinterest Help, undated) and [How to Create Pins for Business](https://business.pinterest.com/how-to-make-pins/):

| Factor | Pinterest's words | What we do |
|---|---|---|
| Fresh content | "Publish your own Pins with fresh, new content" | A new design for each pin, never a re-upload of the same image |
| Keywords | "include relevant keywords in your Pin title, Pin descriptions, board titles, board descriptions" | Search phrase first in the title; 2-3 phrases in the description; keyword board names and descriptions |
| Boards | "save your content to a relevant board" | One best-fit board per pin; never the same pin on unrelated boards |
| Consistency | "Create Pins frequently and consistently"; new original Pins "at least once a week" | 1 a day per brand once the account is 2 weeks old (below) |
| Duplicates | "Try not to repeatedly save the same Pins or upload content that already exists on Pinterest" (can be flagged as spam) | Unique image **and** unique title and description per pin |
| Format | "high quality images or videos", 2:3, mostly seen on mobile | 1000×1500 (already); text at least 30 px (already in `PINS.md`) |
| Links | Add a URL to each Pin to drive traffic | One specific page per pin, not a hub page |

**Idea Pins no longer exist.** On 11 May 2023 Pinterest said "Idea Pins are now Pins". Links, scheduling
and editing work on video and image pins alike, and multi-page pins became videos
([Pinterest creator community, May 2023](https://community.pinterest.biz/t/pin-creation-announcement-and-faq/1847)).
Older advice to "use Idea Pins for reach and standard pins for clicks" now means **video pins for reach
and image pins for clicks**. The ratios quoted in `pinterest-seo.md` (about 3× impressions for video,
2.5× click-through for images) come from a scheduler's blog. Treat them as direction, and measure our own.

### Keywords

- **Where to find them:** Pinterest search autocomplete (type "budget", read the suggestions) and Pinterest
  Trends (trends.pinterest.com, US, "Finance"). Both are free and used by hand, so no scraping.
- **Title (up to 100 characters):** the search phrase first, then the promise. "How to lower your bills:
  7 scripts that work" beats "The Bill Cut Kit ($5)". The price can go on the image and in the description.
- **Description (up to 500 characters; ours use 91-207):** 2-3 natural sentences with 2-3 related phrases
  ("lower monthly bills, negotiate internet bill, cancel subscriptions"). No hashtag stuffing.
- **Alt text:** describe the image. Ours already do.
- **Board names and descriptions:** keyword phrases, written once (drafts below).

### Board structure (Money Made Simple)

The CSV uses 6 boards, and none has a description. Proposed descriptions, and 2 seasonal additions:

| Board | Pins now | Description (draft) |
|---|---:|---|
| Budget printables | 88 | Free and printable budget planners, bill trackers, savings challenges and budget binder pages. Simple monthly and paycheck budgets you'll actually use. |
| Money apps and tools | 44 | Honest comparisons of budgeting apps, high-yield savings accounts, credit-builder tools and bill negotiation services, including when you don't need to pay for one. |
| Debt payoff | 25 | Debt snowball and avalanche plans, payoff trackers, balance transfer maths and how to set a debt-free date. |
| Saving money tips | 21 | Easy ways to save money each month: cutting bills, sinking funds, emergency funds and savings challenges. |
| Investing for beginners | 18 | Investing basics for beginners: starting with $100 a month, index funds, Roth IRA and 401(k) explained simply. Education, not advice. |
| Budgeting for beginners | 10 | How to make a budget for the first time: the 20-minute budget, money personality quiz and simple budgeting methods. |
| **New: Savings challenges** | — | 52-week, 100-envelope and no-spend challenges, plus printable trackers. **Pin from 1 Dec**, ahead of the January peak. |
| **New: 2027 budget planner** | — | Dated 2027 budget planner pages and New Year money goals. **Pin now through January.** |

Keep it to about 8 boards. Pinterest asks for relevance, not volume, and each board needs a steady flow
of pins to look alive.

### Cadence

- **Weeks 1-2 (new account):** 3-5 pins a week, the advice for new accounts in `pinterest-seo.md`
  (Tailwind). The current schedule starts at 1 a day from 9 Nov, which is fine if the account already
  exists. If it's created that week, start at every other day.
- **From week 3:** 1-2 fresh pins a day per brand. Rising to 3 a day (the schedule's late-November rate) is
  fine once the account is a month old.
- **Same URL:** at least 7 days between pins, and at most 10 boards per pin over its life (Tailwind).
- **Seasonal:** pin seasonal content **30-45 days before** the peak. Pinterest users plan ahead, and pins
  take weeks to gain distribution. So savings challenges and 2027 planners from 1 December, and tax
  season from mid-January.
- **Judge a pin at 30 days, not 3.** Pinterest distribution is slow compared with Instagram or TikTok
  (see the metrics plan, `launch-metrics-30-days.md`).

## 2. Audit of the 206 pins (PR #4)

| Check | Result | Fix |
|---|---|---|
| Size and shape | 1000×1500 (2:3) per `PINS.md` | None |
| Alt text | 206 of 206, 47-128 characters | None |
| UTM | 206 of 206, each with a unique campaign | None |
| Pinned before the page is live | 0 | None |
| Title length (≤100) | 17-85 characters | None |
| **Pins linking to `/shop/`** | **118** (57%) | Link each product pin to its own page. Either add `/shop/<slug>/` pages to the site (best for rich pins and analytics), or link to the Etsy or Gumroad listing |
| **Titles that are only "Name ($price)"** | **104** | Lead with the problem or search phrase: "Bill Cut Kit ($5)" → "How to lower your bills: scripts and a subscription audit" |
| **Duplicate titles and descriptions** | **98** (the a/b designs share text) | Write a second angle for each "b" design. E.g. "a" = how-to, "b" = the number ("Save $40 a month on bills") |
| **Same-URL pins 0-1 days apart** | **75 of 87** gaps | `make_pins.py --all`: interleave URLs so the same URL repeats no sooner than 7 days |
| Unscheduled pins | 70 (40 shop, 29 blog, 1 compare) | Schedule them after 7 Jan, at 1-2 a day |
| Board descriptions | None in the CSV | Use the drafts above |
| Domain | Every link is `moneymadesimple.netlify.app`, but the pin footer says `moneymadesimple.co` | Decide the domain before scheduling (`pinterest-seo.md` open question). Claiming the domain enables rich pins and site analytics in Pinterest |
| Hashtags | None | None (keywords matter, hashtags don't) |
| Video pins | None | Add 4-6 short videos (6-15 s page flip-throughs of the printables, or a calculator demo) in December, for reach. Compare them with image pins at 30 days |

**Order for the site thread:** (1) product links and (2) keyword titles first, since both change what each
pin is for. Then (3) unique text for the b designs and (4) re-run the scheduler with the 7-day spacing.
That's a change in `make_pins.py`, then regenerate `pins.csv` and `schedule.csv`.

## Sources

- Pinterest Help: [Pin performance and distribution](https://help.pinterest.com/en/business/article/pin-performance-and-distribution).
- Pinterest Business: [How to Create Pins for Business](https://business.pinterest.com/how-to-make-pins/).
- Pinterest creator community: [Pin Creation Announcement and FAQ](https://community.pinterest.biz/t/pin-creation-announcement-and-faq/1847) (May 2023, Idea Pins merged into Pins).
- Cadence and repeat limits: Tailwind and TryMyPost via `pinterest-seo.md`.
- Pins audited: PR #4, `site/pins/pins.csv`, `site/pins/schedule.csv`, `site/PINS.md`.
