# YouTube SEO playbook, late 2026: Shorts and long videos

Researched 2026-11-07 from YouTube Help pages (linked) and dated trade press where YouTube has no page.
**Docs only.** Section 6 checks every pack on the four brand branches against it, and section 7 lists
factory changes for the factory thread. Nothing here has been uploaded or changed in Studio.

## TL;DR

1. **New channels get found through search first, and browse later.** Search ranks on relevance (title,
   description, content), engagement for that query, and quality (expertise and trust for the topic).
   None of that needs an audience history, which is why our search-led long videos (`mms-youtube-series.md`)
   are the right start. Browse and Suggested come once YouTube knows who watches us.
2. **Titles: the search phrase in the first 40-60 characters, 70 at most.** Our MMS series titles mostly do
   this. **Scam Decoded's Shorts titles are long quote-style lines: 98 of 243 are over 60 characters.**
3. **Chapters: the factory already does them right.** It rebuilds them from the real beat timings after
   rendering and drops the writer's guessed timestamps (`media/chapters.py`). Nothing to change.
4. **End screens and playlists are missing everywhere.** No pack plans either, and the API can't set end
   screens. Each long video needs a **20-second end slate** built into the render, a by-hand end screen in
   Studio, and a series playlist.
5. **Shorts: links in descriptions aren't clickable** (since 31 Aug 2023). Use the **related video** link on
   every Short, pointing to the matching long video. It's set by hand in Studio.
6. **Tags barely matter** ("tags play a minimal role"), so don't spend time on them. The factory's
   category is People & Blogs (22). **Education (27)** fits our brands better.

## 1. How discovery works for a new channel

**Search** ([How YouTube search works](https://support.google.com/youtube/answer/16090438)):
- **Relevance:** how well "the title, tags, description, and video content match your search query".
- **Engagement:** "the watch time of a particular video for a particular query".
- **Quality:** "which channels demonstrate expertise, authoritativeness, and trustworthiness on a given
  topic".
- Results are personalised, and placement can't be bought.

**Browse and Suggested** (home feed, "up next"):
- These are recommendations. They're driven by what each viewer watches, likes and skips, and by
  satisfaction (surveys, "Not interested").
- A new channel has none of that history yet. It's the reason small channels see little browse traffic at
  first. That's our inference from how recommendations work, not a YouTube statement.

**What this means for us:**

| Phase | Lead with | Measure in Studio → Analytics → Reach → Traffic source |
|---|---|---|
| Months 1-3 | **Search-led long videos** on evergreen "how to" questions (budget, emergency fund, quarterly tax, freeze credit), plus Shorts that point to them | YouTube search %, impressions click-through rate on search, average view duration |
| Month 3+ | As Browse/Suggested grows, test more curiosity titles and series that viewers binge (playlists) | Browse + Suggested %, returning viewers |
| Always | Finance is a trust topic, so show the work: our own numbers, sources in the description, a real person's voice and screen | Comments asking follow-ups, subscribers per video |

Seasonal search peaks we already plan around: **January** (budgets, 1099s, scam season), **15 Jan, 15 Apr,
15 Jun, 15 Sep** (quarterly tax for 1099 Money), **tax season** (Scam Decoded's IRS pack). Publish
**1-2 weeks before** each peak so the video has some watch history when searches spike.

## 2. Titles

| Rule | Why | Source |
|---|---|---|
| Put the search phrase in the first 40-60 characters ("How to build an emergency fund..."), then the twist ("...even on a tight budget") | Relevance is matched against the title; mobile and search results cut long titles | Search page above |
| **70 characters at most**, 100 is the hard limit | `publish/youtube.py` truncates at 100 with "…", which looks broken | factory code |
| Match the thumbnail, don't repeat it. The title says what; the 2-5 thumbnail words say the payoff | Our `thumbnail_text` field already does this | — |
| No bait the video doesn't pay off ("They don't want you to know") | Engagement for the query drops when viewers leave fast; YouTube's spam policy covers misleading metadata | [Spam, deceptive practices](https://support.google.com/youtube/answer/2801973) |
| **Test & compare**: up to 3 titles (and thumbnails) on long videos. Winner is by **watch time share**, not CTR. Desktop Studio only, needs Advanced features, **not for Shorts** | Free A/B test once a video has traffic | [vidIQ, 25 Jul 2025](https://vidiq.com/blog/post/youtube-launches-new-title-testing-tool) |
| Shorts titles: short and readable, the topic first | Shorts can rank in search too; long quote-titles are cut off in the Shorts player | — |

## 3. Descriptions, hashtags and tags

**Description structure for long videos** (5,000 bytes max, handled by `fit_caption`):
1. **Lines 1-2 (about 150 characters):** a plain sentence with the search phrase and the payoff. This is
   what shows above "more" and in search snippets.
2. **Chapters** (inserted by the factory after the first paragraph).
3. **Links:** the free lead magnet and the product, each with UTM tags. Affiliate links need the disclosure
   line next to them.
4. **Sources:** the 2-4 official pages the numbers came from (IRS, CFPB, FTC). This supports "quality" for a
   trust topic, and our scripts already carry `sources`.
5. **Disclosures:** AI disclosure (already appended), "Educational content, not financial advice".
6. **2-3 hashtags** at the end, related to the video ("#budgeting #personalfinance"). Up to three appear
   above the title, and **over 60 hashtags means all are ignored**. Unrelated hashtags can get a video removed
   ([Hashtags](https://support.google.com/youtube/answer/6390658)).

**Tags:** "Tags can be useful if the content of your video is commonly misspelled. Otherwise, tags play a
minimal role" ([Tags](https://support.google.com/youtube/answer/146402)). Our tags are the hashtag list
(`fit_tags`, 500 characters). That's fine. Just add common misspellings where they exist ("ira" vs "IRA" is
the same; "1099 nec" vs "1099-NEC" is worth adding).

**Shorts descriptions:**
- Links in Shorts descriptions and comments **stopped being clickable on 31 Aug 2023**.
- Instead, each Short can have **one related video link** to another video on the same channel. It's added in
  Studio on desktop, under Details
  ([Search Engine Journal](https://searchenginejournal.com/youtube-adds-shorts-links-limits-links-elsewhere/495463)).
- So "link in bio" means the channel's profile links, and "link below" doesn't work on Shorts. None of our
  Shorts say "link in the description" (checked, section 6).

## 4. Chapters

YouTube's rules ([Video chapters](https://support.google.com/youtube/answer/9884579)): first timestamp
`00:00`, "at least three timestamps listed in ascending order", each chapter at least **10 seconds**.
Automatic chapters are on by default for new uploads, but "not all eligible videos will have" them, and
channels with active strikes lose chapters.

**On `main`:** `media/chapters.py` builds chapters from the rendered beat start times, merges anything under
10 seconds, needs at least three, and `with_chapters` **removes the writer's guessed timestamp lines**
before inserting the real list. Every long pack in section 6 has guessed timestamps in its description, and
the pipeline replaces them on upload. **No change needed.** Chapter titles come from segment headings, so:

- Write headings as **search phrases**, not labels. "How much to save first" beats "Step 2". Headings show in
  search as "key moments".
- Keep the intro under 30 seconds, so chapter 2 starts quickly.

## 5. End screens and playlists

**End screens** ([End screens](https://support.google.com/youtube/answer/6388789)):
- Video at least **25 seconds**. Shown in the **last 5-20 seconds**. Up to **4 elements** on 16:9.
- Elements: a video or playlist (including "best for viewer"), subscribe, channel. **Link** elements need the
  YouTube Partner Program.
- Not on made-for-kids videos or mobile web.
- **The Data API has no end-screen endpoint**, so they're set by hand in Studio. Use "Import from video" to
  copy one layout to each new upload in a few seconds.

**Plan for every long video:**
1. **Render a 20-second end slate:** the brand background, space for 2 video tiles and the subscribe
   circle, and one spoken line ("If you're building a budget, watch this next"). The current long scripts end
   on a **110-130 word CTA beat** (about 45 seconds of narration), so an end screen would cover the
   explanation. **Factory change 1** below.
2. **End screen layout** (one template per brand, imported each time):
   - Left: the **next video in the series** (specific video).
   - Right: "best for viewer".
   - Subscribe.
3. **Shorts → long:** set the related video link on every Short to its long video. The packs already pair
   many Shorts with a long topic; record the pairing in the pack (**factory change 3**).

**Playlists** (no YouTube Help page states a ranking effect, so the reason is binge-watching, not SEO):
- **One playlist per series**, in order, with a search-phrase title ("Budgeting for beginners: start here")
  and a 2-3 sentence description.
  - MMS: "Money basics" and the 12-video series.
  - 1099 Money: "Quarterly taxes", "Deductions".
  - Scam Decoded: "IRS and tax scams", "Bank and text scams".
  - Dinero Simple: "Finanzas básicas", "Estafas".
- **Plus one "Start here" playlist** of the 3-5 best videos, featured on the channel home page.
- Use the playlist as the end-screen target from the second video onward.
- Playlists can be made through the Data API (`playlists.insert`, `playlistItems.insert`). Our existing
  `youtube.force-ssl` scope covers it, so the factory could add each upload to its series playlist
  (**factory change 2**). Until then, do it by hand in Studio, about 30 seconds per upload.

## 6. Our packs, checked

Script `yt_audit.py` (run in the scratchpad, not committed) read every `content.json` on the four brand
branches, deduplicated by format and title.

| Brand (branch) | Shorts | Long | Titles over 60 / 70 chars | "Link in description" on a Short | Hashtags per post | End screen or playlist planned |
|---|---|---|---|---|---|---|
| MMS (#4) | 28 | 4 | Long: 1 over 70 ("How to start investing with $100 a month (complete beginner walkthrough)") | 0 | 6-10 (fine as tags) | No |
| MMS YouTube series (#5) | — | 20 checked | 3 over 70 (75-80 chars): "High-Yield Savings Accounts Explained: Are They Safe, and Are They Worth It", "How to Pay Off Credit Card Debt Fast (The Minimum Payment Trap...)", "Sinking Funds Explained..." | — | 6 | No |
| Scam Decoded (#9) | 243 | 31 | **Shorts: 98 over 60, 52 over 70.** Long: 27 over 60, 16 over 70 | 0 | 6+ | No |
| 1099 Money (#10) | 156 | 28 | Long: 11 over 60, 3 over 70 | 0 | 6+ | No |
| Dinero Simple (#11) | 122 | 14 | Long: 7 over 60, 5 over 70 (the "(guía completa)" suffix) | 0 | up to 10 | No |

**What's already right:**
- Every long description has more than 200 characters and the title's key words in its first 150.
- Chapters get fixed at upload.
- The MMS series titles are search-led ("How to...", "X vs Y", "...Explained").
- Scripts carry sources.

**Fixes, by thread (each about 30-60 minutes of edits):**
1. **Scam Decoded (#9):** shorten Shorts titles to **60 characters or less** with the scam type first. For
   example, "'You're owed $412 from the breach settlement, pay a $25 fee': 0 real claims charge you" becomes
   "Breach settlement scam: real claims never charge a fee". Keep the quote as on-screen text, where it works
   well. Same for the 16 long titles over 70.
2. **All brands:** trim long titles to 70 or less. Drop "(complete guide)" or "(guía completa)" suffixes,
   which cost 15-17 characters and add nothing searchers type.
3. **All long scripts:** make the last 20 seconds an end-slate beat (spoken "watch this next" line only) and
   move the rest of the CTA earlier.
4. **All Shorts:** add `related_video` (the content ID of the matching long video) so Dhruv knows which link
   to set.
5. **YouTube descriptions:** put 2-3 hashtags at the end and keep the full list as tags.

## 7. Factory changes (for the factory thread, not made here)

| # | Change | Effort |
|---|---|---|
| 1 | `media/render.py`: for `long`, append a **20-second end slate** (brand colours, empty tile areas, no burned-in captions) after the last beat, so a Studio end screen never covers content. The writer's `long` spec gets "end with a one-sentence 'watch next' line" | Medium |
| 2 | `publish/youtube.py`: optional `playlist` per post (pack field or brand default per pillar). After upload, call `playlistItems.insert`, already covered by `youtube.force-ssl` | Small |
| 3 | Pack schema: `related_video` on Shorts, shown in `factory review` and Today as "Set related video in Studio: <title>" (the API doesn't expose it) | Small |
| 4 | `YT_CATEGORY_ID` default 22 → **27 (Education)** for finance brands, or a per-brand setting | Tiny |
| 5 | `launch_check.py`: yellow flag for YouTube titles over 70 characters, and for long scripts whose last beat is over 40 words | Small |
| 6 | Description builder: add 2-3 of the post's hashtags at the end of YouTube descriptions | Tiny |

## 8. Weekly routine, by hand in Studio (about 5 minutes per long video)

- [ ] End screen: import the brand template, set the left tile to the next video in the series.
- [ ] Add to the series playlist (until factory change 2).
- [ ] Every Short from that week: set the related video link.
- [ ] Once the video has a few hundred views, start a Test & compare with 2-3 titles (long videos only).
- [ ] Monthly: check Traffic source → YouTube search terms. Add the top phrases to the description's first
      line if they're missing, and turn new phrases into the next month's video ideas.
