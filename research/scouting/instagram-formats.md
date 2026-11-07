# Instagram: formats and accounts that are growing (Nov 2026)

## 1. The rules changed in 2026, and they decide which "slop" still works

| Date | Change | What it means for us | Source |
|---|---|---|---|
| 13 Mar 2026 | Meta "Rewarding Original Creators on Facebook": unoriginal content (watch-alongs, stitched clips, narrating others' content, re-uploads, minor edits like borders/captions/speed) is deprioritized; pages that mostly post it can be made non-recommendable and demonetized. Original Reels views and watch time roughly doubled in H2 2025 vs H2 2024. | Cross-posting our own original Reels to a Facebook Page is fine and is where Meta is paying. Anything built from other people's clips is not. | [Meta Newsroom](https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/) |
| 30 Apr 2026 | Instagram stops recommending photos and carousels from aggregator accounts. An account is an aggregator if most of its posts in a rolling 30 days are reposts. Explicitly counted as original: photo series, how-to guides, visual stories. | Our how-to carousels are named as the kind of thing Instagram wants. Meme/repost pages, the classic theme-page playbook, lose Explore reach. | [Social Media Today](https://www.socialmediatoday.com/news/instagram-updates-algorithm-to-benefit-original-creators/819016/) |
| 31 Aug 2026 | Profiles that "feature an AI-generated person" must use the "AI-generated profile" label (it replaces the optional "AI creator" label). Unlabelled ones get limited reach. | Don't build an AI presenter or AI "money coach" persona. A faceless brand with illustrations and voice-over is not an AI person; we keep the per-post `is_ai_generated` flag the publisher already sends. | [Engadget](https://www.engadget.com/2246914/instagram-will-demote-ai-generated-influencers-if-they-dont-clearly-label-their-account/) |
| Ongoing | Graph API publishing supports `is_ai_generated` per post (not on carousel children) and `trial_params` for Trial Reels (`graduation_strategy`: `MANUAL` or `SS_PERFORMANCE`). Carousels: 10 items max through the API (the app allows 20). 400 containers per 24h. | Trial Reels is a free, official way to A/B test hooks on non-followers. Our publisher doesn't use it yet. | [IG User Media reference](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media) |
| Jan 2026 | YouTube's CEO named reducing AI slop and detecting deepfakes as 2026 priorities. | Same direction on YouTube Shorts: originality and disclosure. | CNBC, 21 Jan 2026, via [Wikipedia: AI slop](https://en.wikipedia.org/wiki/AI_slop) |

**Bottom line:** the 2023-2025 "slop" playbook (repost pages, stock-clip compilations, AI influencers,
mass-produced narrated stock footage) is being demoted on Meta's platforms. What's being rewarded is
original, useful, labelled content. That's what cocosl already makes.

## 2. Format data

Socialinsider 2026 Instagram benchmark, 67.5M organic posts from ~579K business accounts with 1K-1M
followers ([source](https://www.socialinsider.io/social-media-benchmarks/instagram)):

| Format | Engagement 2024 | 2025 | Q3 2026 | Views/post (100K-1M accounts, 2025) | Posts/month 2025 |
|---|---|---|---|---|---|
| Carousels | 0.55% | 0.55% | **0.50%** | **35,370** | 5 |
| Reels | 0.50% | 0.52% | 0.48% | 16,035 | 8 |
| Images | 0.45% | 0.37% | 0.35% | 22,900 | 7 |

Read with care: engagement is (likes + comments) ÷ followers, saves and shares aren't in it, and the
page has small internal inconsistencies. But two things hold up across years: carousels match or beat
Reels on engagement, and accounts are posting more Reels while carousels stay under-supplied.

Buzzlytics' Nov 2026 finance Reels list puts typical finance-creator engagement at 3.0% against 4.6% for
all Reels creators ([source](https://www.buzzlytics.io/top/instagram/finance)). Finance is a lower-
engagement niche, so judge our numbers against finance, not against all of Instagram.

## 3. Account types that are growing, and whether to copy them

| Type | Examples (public, third-party figures) | Is it growing? | Fit for Money Made Simple |
|---|---|---|---|
| **Saveable how-to carousels** (checklists, "do this, not that", worked numbers) | Finance personal creators like @investarters (302K, 1,795 posts) post heavy carousel/infographic mixes ([Buzzlytics](https://www.buzzlytics.io/top/instagram/finance)) | Yes. Instagram names how-to guides as original; best views/post in benchmark | **Core format.** Already built (`media/carousel.py`). Do more. |
| **Faceless text-and-voice Reels** (kinetic captions, simple illustrations, one idea per Reel) | Many small accounts; no reliable public growth data | Yes, when the script is original | **Core format.** Already built. Needs a real voice (see integration plan #1). |
| **Big quote / infographic theme pages** | @wealth (15M), @thegoodquote (23M), @entrepreneurshipquote (3M); revenue estimates of $8K-$200K/month on [faceless.my](https://faceless.my/instagram/top-faceless-instagram-pages/) | Mature; repost-heavy ones lose Explore reach after 30 Apr 2026 | Learn the packaging (bold headline, one stat), not the reposting. Revenue numbers there are formula estimates (followers × rate × 2-3 deals), not reported earnings. |
| **Stickman / whiteboard animated explainers** | GitHub's `kaomei/stickman-video-director` (4.6K stars in 3 months) shows how much demand there is for this style on faceless YouTube | Popular on YouTube, crossing to Reels | **Worth a test.** Cheap to make with our art pipeline; clearly original; good for "how X works" topics. |
| **Screen-recorded demos** (spreadsheet, calculator, app walkthrough) | Common among finance creators | Steady | **Worth a test**, using our own budget template as the demo. Real footage of our product, so it's original and sells it. |
| **AI persona / AI influencer** | Many in 2025-26 | Being demoted unless labelled (31 Aug 2026) | **Don't.** In finance, an AI "advisor" undermines trust, and FTC rules on fake testimonials apply. |
| **Absurdist AI "brain rot" series** | Fruit Love Island: 3M+ TikTok followers in 9 days, 300M+ views, episodes removed by TikTok and series ended after 15 days ([Wikipedia](https://en.wikipedia.org/wiki/Fruit_Love_Island)) | Viral spikes, short lifespans | **Don't.** No path to affiliate or product revenue in our niche; removal risk. |
| **Stock-footage + TTS compilations** (MoneyPrinter-style) | The default output of most "faceless generator" repos | Being demoted as unoriginal on Meta and YouTube | **Don't** as the main format. Stock B-roll is fine as a supporting layer under an original script. |

## 4. What this means for the weekly plan

Current playbook target: 5 Shorts/Reels, 3 carousels, 1 long video per week. Suggested change:

- **5 carousels** (up from 3). Checklist, worked-example and myth/fact styles get saved most.
- **4 Reels**, each one idea, posted as Trial Reels first once the publisher supports it, so weak hooks never hit our followers' feeds.
- **1 long video** (YouTube), repurposed into the Reels above as it already is.
- Test **one stickman explainer** and **one screen-recorded template demo** in the first month.
- Cross-post original Reels to a Facebook Page (Meta is paying originals there).

## 5. Things I couldn't verify

- Real follower growth over time for specific faceless finance accounts. No reliable public source tracks it,
  and scraping would break Instagram's terms. `watchlist.py` fixes this going forward with the official API.
- The CNBC and MediaPost articles on Meta's 2026 creator payouts and the AI-label reach limits wouldn't load,
  so payout amounts are unknown.
- Most "how much faceless pages earn" articles are SEO content from tool vendors. Treat their numbers as marketing.
