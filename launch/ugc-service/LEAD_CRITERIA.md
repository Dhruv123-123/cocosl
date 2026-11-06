# Finding 30 good leads in one evening (by hand)

Goal: 30 qualified small businesses in `leads.csv` in about 2.5 hours, each with a published business email
and one specific, true thing you can say about them. That's ~5 minutes per lead. Quality beats volume:
10 well-researched pitches beat 100 generic ones.

**Rules:** only information the business published itself. No scraping tools, no buying lists, no
guessing personal emails, no LinkedIn/Instagram automation. Open each site, look, and copy by hand.

## What a good lead looks like (score each 0–1, keep 4+ out of 6)

| # | Signal | Why it matters |
|---|---|---|
| 1 | **Physical, visual product** (or a visual local service) that's easy to demo in 20 seconds | Demo ads need something to show |
| 2 | **Small**: roughly 1–20 people, founder-run, no in-house creative team | Big brands have agencies; small ones answer their own email |
| 3 | **Already selling online**: working store, prices, checkout, recent activity | They have money coming in and a reason to advertise |
| 4 | **Some marketing effort, but thin video**: active Instagram/TikTok with few or tired videos, or running ads with 1–3 creatives | They see the value; you fill a gap |
| 5 | **Published business email** (contact page, footer, "wholesale/press") | You need a legitimate way to reach them |
| 6 | **Price point $20–150** or a local service people book often | Paid social works best in this range; easy story to tell |

**Skip / red flags:** supplements making health claims, CBD, weight loss, "get rich" courses, crypto, firearms,
adult, anything regulated (alcohol, gambling, medical devices, financial products), dropshipping stores with
copied photos and 3-week shipping, stores with no contact email, anyone whose site says "no solicitations",
and big brands (100+ staff, national retail).

**Good niches to start:** home & kitchen gadgets, pet products, outdoor/camping gear, eco/reusable goods,
stationery and desk accessories, candles and home fragrance, kids' toys (non-electronic), fitness accessories,
skincare **without** medical claims, coffee/tea, local cafes, gyms and studios, salons, detailers, cleaners.

---

## Where to look (with a time budget)

### 1. Meta Ad Library: brands already paying for ads (45 min → ~10 leads), the best source
1. Go to **facebook.com/ads/library**, choose your country, Ad category **All ads**.
2. Search a niche keyword: "dog harness", "reusable bottle", "planner", "candle", "coffee subscription".
3. Look for advertisers with **1–5 active ads**, simple creatives (static image or one basic video),
   and a small page. Many active ads with polished video = they already have an agency, skip.
4. Click through to their website. Check the 6 signals, find the contact email.
5. In `notes`, write the hook/first line of one of their current ads (you'll use it in Email 2).

### 2. Shopify stores via public directories and search (45 min → ~10 leads)
- **Google:** `"powered by shopify" {niche}`, `{niche} "free shipping" "our story"`,
  `site:myshopify.com {niche}` (stores still on their default domain are often very small).
- **Shopify's own lists**: Shopify blog customer stories / "examples of Shopify stores" posts.
- **Product Hunt** (producthunt.com) and **Kickstarter/Indiegogo** "successfully funded" physical products:
  founders who just launched and now need ongoing ads.
- Small-business marketplaces/directories in your country (e.g. "buy local", "black-owned business",
  "women-owned business" directories) list many independent DTC brands with websites.

### 3. Etsy shops that also have their own website (30 min → ~5 leads)
- Search Etsy for your niche, sort by relevancy, look for shops with **1,000+ sales** and a polished brand.
- Check the shop's "About" section and the shop owner's linked website or Instagram.
- Only pitch via email published on **their own website**. Don't cold-pitch through Etsy messages: Etsy
  messaging is for buying, and unsolicited promotion there breaks Etsy's rules.

### 4. Local businesses (30 min → ~5 leads)
- **Google Maps:** search "{category} near {your area}" (cafe, gym, pilates, barber, nail salon, car detailing,
  bakery, florist, dog groomer). Pick ones with **4.3+ rating, 50+ reviews**, an active website and Instagram,
  but few or no Reels in the last month.
- Their website contact page or the email listed on their Google profile.
- Local is great for your first client: you can mention your area, and they understand "4 videos for $249".

---

## The 5-minute lead routine (repeat 30 times)

1. **Open the website** (1 min). Is it real, small, selling, visual? If no, close it, don't log it.
2. **Find the email** (1 min). Contact page, footer, About, Wholesale, Press. No email → skip, or log with
   `source` and `notes: "contact form only"` if it's a great fit.
3. **Find the contact name** (1 min). About page / "Our story" usually names the founder. Otherwise leave blank
   and use "Hi there".
4. **Find one specific, true thing** (1–2 min): a product you like, a recent launch, a current ad's hook,
   a value they care about. Write it in `notes`. This becomes your first line.
5. **Score 0–6**, write the score at the start of notes, e.g. `5/6 · ...`. Keep 4+.

## Log format: `leads.csv`

Columns (these import directly on the factory's **Clients** page → CSV import):

```
name,contact_name,email,website,niche,source,notes
```

- `name`: business/brand name
- `contact_name`: person's name if published, else empty
- `email`: business email exactly as published
- `website`: full URL
- `niche`: short category, e.g. `pet accessories`
- `source`: `meta-ad-library`, `google-shopify`, `etsy`, `google-maps`, `product-hunt`, `kickstarter`
- `notes`: `score/6 · the specific thing · product to use for the sample · status`

Status words to add to `notes` as you go: `pitched YYYY-MM-DD`, `fu1 YYYY-MM-DD`, `replied`, `sample sent`,
`won`, `lost`, `do_not_contact` (anyone who says no or asks you to stop; never email them again).

The three rows in `leads.csv` marked EXAMPLE use the reserved `.example` domain and are not real
businesses. Delete them before importing.

## Evening checklist

- [ ] 10 from Meta Ad Library
- [ ] 10 from Shopify/search/launch sites
- [ ] 5 from Etsy (own website + email)
- [ ] 5 local businesses
- [ ] Every row: email published by them, one specific note, score 4+
- [ ] Sort by score; the top 10 get pitched tomorrow
