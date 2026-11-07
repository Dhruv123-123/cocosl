# YouTube monetization and AI-disclosure policies (Nov 2026), checked against our packs

Reviewed 2026-11-07 from YouTube's own blog and Help Center, plus an audit of every content pack on the
four brand branches (MMS PR #5, Scam Decoded #9, 1099 Money #10, Dinero Simple #11). **Docs only.**
Follows `youtube-monetization.md` (Oct round), whose YPP-threshold caveat is now resolved below.

## TL;DR

1. **The new YPP thresholds are confirmed by YouTube** (announced 10 Aug 2026, effective **1 Feb 2027**).
   Our channels launch in Nov 2026 and won't reach 1,000 subscribers before February, so they apply under
   the new rules: **1,000 subs + 8,000 public watch hours in 12 months, or 20M Shorts views in 90 days.**
2. **Shorts ad revenue now needs 10M qualified Shorts views per 90 days** on top of YPP. The financial
   model's best case is about 5M Shorts views a month *across all platforms*, so **plan on $0 YouTube Shorts
   revenue in 2027.** Shorts are for reach and subscribers; long videos and products pay.
3. **AI disclosure: no label needed for any current pack.** Every visual prompt is flat vector
   illustration with "no real people", and `realistic_synthetic_media` is false for all four brands. Keep it
   that way, and never clone another person's voice.
4. **The real risk is "inauthentic content", not disclosure.** **23 of Scam Decoded's 39 long videos have
   no original element** (no chart, screen recording or human segment), and they average only 543 words
   (about 3.5-4 minutes). That's the closest thing we have to "templated storylines... with minimal
   narrative". Fix before launch (section 4).
5. **No pack has real footage yet** (`footage` is empty everywhere). Dhruv's screen recordings (Actual
   tutorials, receipt kit) are the cheapest proof that a person makes these channels.

## 1. YPP thresholds (official)

| Item | Before 1 Feb 2027 | From 1 Feb 2027 | Source |
|---|---|---|---|
| Full YPP (ad revenue) | 1,000 subs + 4,000 watch hours (12 mo) or 10M Shorts views (90 days) | **1,000 subs + 8,000 watch hours or 20M Shorts views** | YouTube Official Blog, 10 Aug 2026 |
| **Shorts ad revenue share** | Included with YPP | **Only for channels with 10M qualified Shorts views in 90 days.** Others keep long-form ad revenue | same |
| Fan funding (memberships, Super Thanks) and Shopping | Lower tier (500 subs...) | **Unchanged.** Shopping gets bonuses for channels below the Shorts threshold | same |
| Existing YPP members | — | Not affected | same |

**What this means for us:**
- 8,000 hours is about 160,000 views of a 3-minute average watch. That's realistic only through long
  videos with good retention, so **the long video each week is the monetization engine**, not the 5 Shorts.
- The financial model (PR #3, `docs/FINANCIAL_MODEL.md`) already uses 8,000 hours. It should also set
  YouTube Shorts ad revenue to $0 for 2027 in every scenario.
- The lower fan-funding tier is still useful: memberships aren't our plan, but **YouTube Shopping
  (affiliate products) stays reachable** and is where the Etsy and Gumroad products could appear later
  (check eligibility for digital products when we get there).

## 2. AI disclosure (Help Center answer 14328491)

**Required only when content is realistic and could be mistaken for real:** a real person saying or
doing something they didn't, altered footage of real events or places, or realistic scenes that didn't
happen.

**Not required:** production help (outlines, scripts, thumbnails, titles, infographics), clearly
unrealistic or animated content, colour and beauty fixes, and **cloning your own voice for voiceover**.

**YouTube may label for you:** it applies labels when content was made with YouTube's AI tools, carries
C2PA metadata, or is detected. **A creator can't remove a label applied from C2PA data or after manual
review.** Repeatedly not disclosing can lead to removal or YPP suspension. Disclosing does not by itself
reduce monetization.

**Our packs against the rule:**

| Check | Result |
|---|---|
| Visual prompts | All flat vector or illustrated ("Clean/Warm flat vector illustration ... No text, no logos, no real people"). Three grep hits for "realistic" were false positives (e.g. "a realistic budget") |
| `realistic_synthetic_media` in brand yaml | **false** for all 4 brands, so `publish/youtube.py` sends `containsSyntheticMedia=false` |
| `ai_disclosure` text | Present in every brand yaml (description footer) |
| Voices | Brand yaml comments say "your own cloned voice or a licensed stock voice". Both are fine: Dhruv's own clone is exempt, and a stock or Kokoro voice isn't a real person. **Never clone anyone else's voice** (that would need disclosure and consent) |
| C2PA | `gpt-image-1` adds C2PA to stills. Whether it survives our ffmpeg render isn't verified. Even if YouTube auto-labels a video, the label is harmless for illustrated content |

**Rule to add to every pack's `require_human_review` checklist:** if a video ever uses realistic AI
imagery (a photoreal scene, a lookalike person, AI "footage"), set `realistic_synthetic_media: true` for
that post. Scam Decoded is the brand most tempted by this ("what the fake bank caller looks like"). Use
illustrations or real, licensed screenshots of scam texts instead.

## 3. Inauthentic content (answer 1311392)

Renamed from "repetitious content" on 15 Jul 2025, with no 2026 text changes listed. It applies to **the
channel as a whole**, not one video. Two examples matter for us:
- "Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or
  educational value."
- "AI-generated content made with generic or unoriginal templates giving the impression of mass
  production."

Using AI is allowed. What's judged is whether each video adds real value and differs meaningfully from
the others. See `youtube-monetization.md` for the Jan 2026 enforcement wave, where some human-run faceless
channels were caught because their format looked automated.

## 4. Pack audit (all four branches)

Common to every brand: 5 Shorts + 1 long video a week, at most 2 posts per platform per day, and
`require_human_review: true`. That cadence is moderate and not a risk on its own.

| Brand | Long videos | Avg words | With an original element | Element types | Risk |
|---|---|---|---|---|---|
| MMS | 44 | 1,033 | **40** (4 missing) | worked-example chart 22, screen recording 12, human segment 6 | Low. Fill the 4 gaps |
| **Scam Decoded** | 39 | **543** | **16 (23 missing)** | free-text notes only | **High.** Short, illustrated, same structure each week |
| 1099 Money | 28 | 1,295 | **28** | worked-example chart 14, screen recording 9, human segment 5 | Low |
| Dinero Simple | 14 | 809 | **14** (all have charts) | chart | Low |

Counts come from the post-level `original_element` field and script-level `chart` entries. "Screen
recording" and "human segment" are **planned**: `footage` is empty in every pack, so none exist yet.

**Fixes, for the content threads (Dhruv approves):**
1. **Scam Decoded (PR #9):** give each of the 23 long videos an original element: a real (redacted,
   reported) scam text or email annotated on screen, a phone-settings screen recording ("turn on spam
   filtering"), or a decision-flow chart. Lengthen the thinnest scripts to 900+ words with a worked
   example of how the scam unfolds. Vary the structure (not every video "here's the text, here's the
   trick, here's what to do").
2. **MMS (PR #5):** add an element to the 4 long videos missing one.
3. **All brands:** record the planned screen recordings before the channel's first 10 long videos go up.
   A channel's newest and most-watched videos are what review looks at first.
4. **Titles:** keep the `youtube-seo-playbook.md` fix (98 of 243 Scam Decoded Shorts titles are over 60
   characters). Identical title patterns across many videos read as templated.
5. **Financial model (PR #3):** YouTube Shorts ad revenue = $0 for 2027.

## 5. Factory changes (small, optional)

- `factory pack-check`: warn when a long video has no `original_element` or chart, or under 700 words.
- `factory pack-check`: warn when a visual prompt contains "photo", "photoreal" or "realistic" while
  `realistic_synthetic_media` is false.

## Sources

- YouTube Official Blog, YPP update, 10 Aug 2026 (blog.youtube).
- YouTube Help: "Disclosing use of altered or synthetic content" (answer 14328491).
- YouTube Help: "YouTube channel monetization policies", inauthentic content (answer 1311392).
- Earlier sources and enforcement examples: `youtube-monetization.md`.

## Open questions for Dhruv

1. OK to send the Scam Decoded fixes (23 long videos) to the Scam Decoded thread? It's the biggest
   launch risk found.
2. When can you record the first screen recordings? They fix the biggest gap on three brands.
