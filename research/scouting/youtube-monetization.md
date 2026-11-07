# YouTube money beyond AdSense: sponsors, the AI-content rules, Shopping and Amazon

Researched 2026-11-07. Policy facts come from YouTube's own statements as quoted by the trade press and
from Google's API docs (linked inline). Sponsor data comes from SponsorRadar (which reads sponsor
mentions out of public videos), brands' own creator pages and rate guides. **Small creators almost
never publish their media kits**, so the per-integration rates below come from rate guides that pool
creator-reported deals, plus SponsorRadar's estimates for what these brands pay bigger channels.

## TL;DR

1. **The biggest risk to our channels is the "inauthentic content" rule, not AI labels.** Our videos are
   stills with a Ken Burns move, captions and an AI voice. That's the format YouTube names as its example
   ("slideshows that all have the same narration"), and it judges whole channels. Fixes are in section 2.
2. **Sponsors don't buy 1k-10k finance channels directly.** The brands that fit (Aura, Incogni, Monarch)
   buy at 50k-1M subscribers. At our size, the money comes from **affiliate/CPA programs from the same
   brands**, plus $50-500 flat deals once the views are steady.
3. **YouTube Shopping affiliate opens at 500 subscribers** in the US (since 27 Mar 2026), but it pays
   on physical products, so it's a side income for us. The scam channel fits it best (security keys,
   shredders, safes).
4. **Fixed in this PR:** a sponsored YouTube upload now always stays private until someone ticks
   "includes paid promotion" in Studio. Before this change, the factory set the flag on TikTok but
   ignored it on YouTube.

## 1. Sponsors for 1k-10k finance-adjacent channels

### What small channels actually get paid

From [1of10's 2026 rate guide](https://1of10.com/blog/youtube-sponsorship-rates/) (published 24 Aug 2026,
based on publicly reported creator rates and marketplace listings; no sample size given):

| | 1k-10k subscribers ("nano") |
|---|---|
| Per sponsored video | **$50-500**, often a fee plus product. Free product alone isn't payment |
| Finance and investing CPM | **$35-50+ per 1,000 expected views** (vs $10-20 for gaming) |
| Format multipliers (60-90 s integration = 1.0x) | Dedicated video 2-4x; 30 s mention 0.5-0.7x; sponsored Short 0.25-0.5x; community post 0.1-0.2x; description link + pinned comment +5-10% |

**Worked example:** a long video averaging 5,000 views at a $35 CPM is worth about $175 to a sponsor
for a 60-90 second read. Quote $150-250. A sponsored Short is about $50-100.

### Brands that fit, and how a small channel gets them

| Brand | Fits | What they do on YouTube (SponsorRadar, Nov 2026) | Route in at 1k-10k |
|---|---|---|---|
| **Aura** (identity theft protection) | Scam Decoded, Money Made Simple | 642 channels, 2,864 videos; usually 50k-250k subs; ~$1.1-2.1k per video ([page](https://sponsorradar.com/brands/aura)) | [Influencer program](https://www.aura.com/influencer-program): no minimum stated, **primarily US audience**, wants long-term partners and **firsthand experience** with the product. Email influencers@aura.com with channel links, US audience %, and a media kit |
| **Incogni** (data-broker removal) | Scam Decoded | 1,207 channels, 3,864 videos; usually 250k-1M; ~$934-1.9k per video; repeat buyer (3.2 videos per creator) ([page](https://sponsorradar.com/brands/incogni)) | No public application. Pitch once the channel is bigger, using SponsorRadar's data |
| **DeleteMe** (data-broker removal) | Scam Decoded | not checked | [Creator page](https://joindeleteme.com/influencers): "every Creator is welcome", apply by form, offer comes back if you fit. **The easiest first sponsor for Scam Decoded** |
| **Monarch Money** (budgeting app) | Money Made Simple | 149 channels, 508 videos; usually 50k-250k; ~$365-728 per video ([page](https://sponsorradar.com/brands/monarch-money)) | Affiliate program first; pitch at ~50k |
| **Rocket Money** | Money Made Simple | not checked | Affiliate: $4-10 per signup ([creator-hero, May 2026](https://www.creator-hero.com/blog/top-10-best-us-budgeting-influencer-affiliate-programs)) |
| **YNAB** | Money Made Simple | not checked | Affiliate: $6-10 per trial signup (the same page also says $6 per lead and $20 per conversion, so check the current terms) |
| **Qube Money**, **FamZoo**, **CalendarBudget** | Money Made Simple | not checked | Affiliates: $15 per referral; 25% per subscription; 75% of the first sale (creator-hero) |
| **YouTube Creator Partnerships** (BrandConnect renamed in 2026) | All | Brands find you | Shows up in Studio > Earn once you're in YPP (entry tier 500 subs), 18+, in a supported country, with no strikes. Nothing to apply for; click "Interested" on fitting briefs ([ainfluencer](https://ainfluencer.com/youtube-brandconnect/)). "A channel of demand, not a plan." |

**What to do:** join the affiliate programs now (most are already in the affiliate application kit, PR #5) and
apply to DeleteMe as soon as Scam Decoded has a few months of uploads. Build a one-page media kit from
the factory's own numbers (`factory report`): median views per video for the last 10, audience country %
from YouTube Analytics, and the one-line pitch. Pitch Aura and Monarch at ~50k.

**Two guardrails that apply here:**
- Aura wants **firsthand experience**. Our presenter is faceless and the factory blocks "I used this"
  claims (fake-testimonial guardrail). Only take that deal if Dhruv really uses the product and the
  script says so truthfully. Otherwise stick to the affiliate link with a plain description.
- Keep away from trading apps and anything "guaranteed". That matches `creators.md`'s "what not to copy".

## 2. YouTube's AI and inauthentic-content rules, and our pipeline against them

### The rules as of November 2026

| Rule | What it says | Source |
|---|---|---|
| **Inauthentic content** (YPP) | Renamed from "repetitious content" on 15 Jul 2025. Mass-produced or repetitive content isn't monetizable. Examples: "narrated stories with only superficial differences between them" and "slideshows that all have the same narration". AI use is fine "regardless of how the content was made" | [PPC Land quoting Google](https://ppc.land/google-clarifies-youtube-monetization-policies-amid-creator-confusion/) |
| **Channel-level review** | Mostly automated. Looks at titles, thumbnails and descriptions, plus the channel's "main theme, most viewed videos, newest videos, biggest proportion of watch time" | same |
| **Enforcement wave** | Jan 2026: 16 channels with 35M subscribers combined lost YPP or were terminated. Some **human-run** faceless channels were caught because their format looked automated; one creator lost 7 of 12 AI-assisted faceless channels in one review | [TechTimes, 15 Jul 2026](https://www.techtimes.com/articles/320629/20260715/youtube-wiped-35m-subscribers-over-ai-slop-now-its-judging-your-taste.htm) |
| **"Unsatisfying or off-putting"** | New 2026 monetization category: emotionally manipulative formulas, videos that feel interchangeable even when they aren't copies. A March 2026 pilot asked viewers if a video "feels like AI slop" | same |
| **AI disclosure** | Required for **realistic** AI: real people saying or doing things they didn't, altered real footage, realistic scenes. **Not required** for AI scripts, captions, thumbnails, colour fixes, unrealistic content, or **AI/TTS narration over original content**. Since 27 May 2026 YouTube labels undisclosed photorealistic AI itself (C2PA/SynthID). Repeated non-disclosure can cost YPP | [minimatters, May 2026](https://minimatters.com/youtube-ai-content-labeling-update-in-may-2026/), [AIR timeline](https://air.io/en/monetization/youtube-monetization-policy-changes-2026-a-complete-dated-timeline) |
| **Inactivity** | Channels inactive for 6+ months can lose monetization. Community posts count as activity | AIR timeline |
| **YPP thresholds** | Announced 10 Aug 2026, effective **1 Feb 2027**: new applicants need 1,000 subs plus 8,000 watch hours (12 months) or 20M Shorts views (90 days), up from 4,000 hours or 10M. Terms must be accepted by 31 Jan 2027 | AIR timeline (*check against YouTube's own announcement before planning around it*) |
| **API flag** | `status.containsSyntheticMedia` can be set on `videos.insert`/`update` (since 30 Oct 2024) | [API revision history](https://developers.google.com/youtube/v3/revision_history) |

### Audit: what our pipeline does today

| Area | What the code does | Risk |
|---|---|---|
| AI label | `publish/youtube.py` sets `containsSyntheticMedia` from `brand.realistic_synthetic_media` (false for our faceless brands). Captions carry the AI disclosure | **Low.** Correct as-is: our visuals aren't realistic, and TTS narration is exempt. Keep `realistic_synthetic_media: false` only while no realistic people or scenes are generated |
| Visual format | `media/video.py`: every beat is a still image with a Ken Burns move, a headline overlay and burned-in captions, joined with the narration | **High.** This is the "slideshow with the same narration" pattern, and the check is per channel. Charts (`media/charts.py`) help because they're drawn from each script's own numbers |
| Voice | One TTS voice per brand, every video | **Medium.** Allowed, but the same voice over the same template is what "superficial differences" means in practice |
| Originality check | `guardrails.check_originality`: 3-word shingle overlap with the brand's last 200 scripts; warns at 35%, blocks at 60% | **Medium.** Catches copied *text*, not copied *structure*. Two scripts can share no sentences and still be the same video with the numbers swapped |
| Hook library (this PR) | Suggests 4 templates per script, one per mechanic, varied by title | **Medium.** It helps variety per video but pulls the channel towards the same 30 openings over time. Needs a rotation check (fix 4) |
| Volume | Cadence cap of 2 posts a day per platform | **Low-medium.** Two a day of near-identical format is still a mass-production signal. One long video plus one Short a day is safer |
| Human review | `require_human_review: true` by default, and `factory doctor` warns if it's off | **Good.** Keep it on for YouTube. A person editing each script is the strongest defence |
| Titles and thumbnails | Generated per post from one brand template | **Medium.** Reviewed alongside the video; identical thumbnail layouts read as templated |
| Sponsored videos | Set the TikTok/Postiz brand-content toggle, but **ignored on YouTube** | **Fixed in this PR** (see below) |
| Cross-brand reuse | Dinero Simple translates Money Made Simple scripts | **Low-medium.** Fine on separate channels if the Spanish version is adapted (examples, prices, US-Latino context), not just translated |

### Fixes, most important first

1. **Give every video one thing a template can't make.** For long videos: a worked example with the
   video's own numbers (a chart, which already exists), a screen recording of a real tool (the IRS
   payment page, a credit freeze page, a bank's alert settings), or one segment recorded by a person.
   Add an `original_element` field to the script schema, and have review refuse a long video without one.
2. **Mix the formats within each channel.** The renderer already supports `short`, `long` and
   `carousel`. Add per-video variety: B-roll from Pexels (licensed, already in the repo plan),
   real-screen beats, a different layout every few videos. No two videos in a row should look identical
   with the sound off.
3. **Add a channel-level sameness check** next to `check_originality`. Compare the new script's
   *structure* (beat count, beat lengths, hook template id, title pattern) against the last 20 on the
   channel, and warn when it matches more than half of them. Each hook template already has an id; record
   the ones the writer used in `posts.meta` so this check (and fix 4) can see them.
4. **Rotate hook templates:** suggest no template used in the brand's last 10 posts.
5. **Slow YouTube to one long video and one Short a day per channel** until each channel is in YPP, then
   raise it only if the analytics hold up. Fewer, better videos also suit the 8,000-hour rule coming in Feb 2027.
6. **Keep the AI label honest:** if any brand starts generating realistic people or scenes (`images.py`
   with a photoreal model), set `realistic_synthetic_media: true`. YouTube now labels undisclosed
   photoreal AI itself, and repeated misses can cost YPP.
7. **Post a weekly community post** (a poll or a one-line tip) on each channel. It counts as activity
   and gives the channel some signs of a person behind it.

### The fix in this PR

`publish/youtube.py`: when a post is marked sponsored (`meta.sponsored`, the same flag TikTok and Postiz
already use), the upload is **always private** with no `publishAt`, and the result says so in
`raw["needs_studio"]`. A person then ticks **"includes paid promotion"** in Studio and publishes. The
Data API documents `paidProductPlacementDetails.hasPaidProductPlacement` only as a response field
([videos reference](https://developers.google.com/youtube/data/reference/rest/v3/videos)), so an
automatic upload can't set the box reliably. Test: `test_youtube_sponsored_stays_private_for_studio`.

## 3. YouTube Shopping and the Amazon Influencer Program

### YouTube Shopping affiliate

From [PPC Land, 27 Mar 2026](https://ppc.land/youtube-opens-shopping-affiliate-program-to-creators-with-500-subscribers/):

- **Eligibility:** in YPP (the expanded tier starts at 500 subscribers; before this it was 10,000+),
  in a supported country (**US** included, plus KR, ID, TH, VN, MY, PH, IN, SG, BR, TW, JP). Music channels
  and Made for Kids channels can't join.
- **Pay:** each brand sets its own rate and attribution window per product (one screenshot shows
  8.5-11.2% on beauty items). Paid through AdSense **60-120 days after purchase**, and returns reverse it.
- **For us:** tag real products only where the video is genuinely about them. That fits Scam Decoded best:
  hardware security keys, cross-cut shredders, a home safe for documents, RFID-blocking wallets (say
  plainly that the RFID risk is small). For Money Made Simple: budget planners, calculators, books. Never
  tag a financial product; Shopping is for physical goods.
- Shopping also lets a channel connect its own store, but Gumroad isn't a supported store as far as this
  research found (*unverified*). Keep selling our products from the description link.

### Amazon Influencer Program

From [Jungle Scout](https://www.junglescout.com/resources/articles/amazon-influencer-program/) (written
in 2024, so **check Amazon's current terms**):

- **Eligibility:** apply with a YouTube, Instagram, TikTok or Facebook account. **No published follower
  minimum**; Amazon looks at engagement as well as size.
- **What you get:** a storefront (`amazon.com/shop/<handle>`) holding all our recommendations, plus
  "onsite commissions" for shoppable videos posted on Amazon product pages, which need a **separate
  approval**.
- **Rates:** fixed per category, roughly 1-10% (Luxury Beauty 10%; Grocery and Health 1%).
- **For us:** apply with Scam Decoded once it has steady engagement, and build one storefront list
  ("Scam-proof your home: what we'd actually buy"). The onsite videos could be the factory's own
  product explainers, which also earn while the YouTube channel is small. Any Amazon link in a description
  needs the "As an Amazon Associate I earn from qualifying purchases" line, and the disclosure guardrail
  should check for it.

## Open questions for Dhruv

- Do you use Aura, DeleteMe or a budgeting app yourself? That decides whether we can honestly take
  "firsthand experience" sponsor deals or only plain affiliate links.
- Is one long video plus one Short a day per channel acceptable until YPP, instead of the current cap of 2?
