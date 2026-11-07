# Recording session prep: Saturday, November 14, 2026

Three clips, about 60 minutes including setup. Record them in this order, so the two screen recordings share
one browser setup and the camera only goes on once, at the end.

| # | Clip | Brand | Type | Length | Posts |
|---|---|---|---|---|---|
| 1 | Checking an unfamiliar store | Scam Decoded | screen recording | 10–30 s | Sun Nov 22 |
| 2 | How a $49 listing video gets made | Ad studio | screen recording, sped up | 20–30 s finished | Thu Nov 19 |
| 3 | The monthly money hour | 1099 Money | on camera, your own voice | ≈ 17 s (+10 s spare) | Sun Nov 22 |

## Print these (or keep them open on a second screen)

1. **Clip 1 narration** (it plays over your recording, so you don't read it aloud; it tells you what to show):
   > "Number one, fake online stores. They show up in social media ads with huge discounts … The fix: search
   > the store name plus the word scam, look for a real address and phone number, and always pay with a
   > credit card."
   Full text: `launch/scam-decoded/weeks-3-6.json`, video *9 holiday scams that peak before New Year*, beat 2.
2. **Clip 2 beats** (on-screen text you'll add): "Step 1: a 3-line plan you approve" → "Step 2: your photos
   become 4 shots" → "Step 3: text for silent playback" → "Step 4: one Etsy cut, one vertical cut".
   Source: `ai-ad-studio-v2/CONTENT_PLAN_4_WEEKS.md`, Post 4.
3. **Clip 3 script** (you say this, in your own words):
   > "Here's the monthly hour that runs it all. Label the business bank statement. Check that tax savings are
   > on track. Log any mileage you missed. Move your paychecks. And four times a year, make the estimated
   > payment from the tax account. That's the whole system."
   Only describe a routine you actually run. If you're starting it now, say so: "This is the routine I'm
   starting this month." Source: `launch/1099-money/RECORDINGS.md`.

## Setup (10 minutes)

- **Screen:** 1920×1080, browser zoom 125%, a private window, logged out of everything, bookmarks bar hidden,
  notifications off (Do Not Disturb). Close every tab you don't need.
- **Never show personal data.** Type nothing real into any form, and blur anything that slips in.
- **Recorder:** macOS Screenshot (Shift-Cmd-5 → Record Selected Portion) or OBS; Windows: Xbox Game Bar
  (Win-G). 1080p or better, 30 fps.
- **Camera (clip 3 only):** landscape 1920×1080, eye level, window light from the side, quiet room, laptop
  closed or turned away. Phone camera is fine.
- **Have open:** for clip 2, one sample project from `ai-ad-studio-v2/etsy-shopify-line/samples/`
  (e.g. the Fernhollow mug: its plan in `BREAKDOWNS.md`, poster in `posters/`, finished cut in `listing/`)
  and your video editor.

## The three clips

**1 · Scam Decoded, "Checking an unfamiliar store"** (≈ 10 min)
Search a made-up or unfamiliar store name plus "scam", then plus "reviews"; open a store's Contact page and its
Returns page. Pause 2 seconds on anything you'd point at. Don't name or accuse a real small shop: use a search
that returns general advice, or an obviously fictional name.

**2 · Ad studio, "How a $49 listing video gets made"** (≈ 25 min)
Record your real workflow on the sample project: the 3-line plan doc → the 4 shots made from the photos → the
text layer → exporting the Etsy cut and the vertical cut. Record it at normal speed (3–5 minutes), then speed
it up to 20–30 s in your editor and add the four step captions. It's a spec sample, so the caption must say
it's for a made-up shop.

**3 · 1099 Money, "The monthly money hour"** (≈ 10 min)
Two or three takes of the script, eye level, talking the way you would to a friend. Optional 5 s cutaway: your
hand writing "Monthly hour" on a calendar or sticky note.

## Export and wire in (15 minutes)

All paths are inside your factory home folder (the one `factory init` created).

| Clip | Export | Save as | Then |
|---|---|---|---|
| 1 | MP4 (H.264), 1080p, trim to 10–30 s | `footage/scam-decoded/9-holiday-scams-that-peak-before-new-year-and-ho-beat2.mp4` | it's already listed in the video's beat 2, so it's picked up at render |
| 2 | MP4 (H.264), **1080×1920 vertical**, 20–30 s, music bed from `etsy-shopify-line/samples/reel/music/` (licences in `MUSIC_LICENSES.md`) | `ai-ad-studio-v2/social-posts/04-process.mp4` | post Thu Nov 19 on Instagram Reels and TikTok with Post 4's caption |
| 3 | MP4 (H.264), 1080p landscape, the best take, ≈ 17 s (+10 s spare) | `footage/1099-money/your-first-year-freelancing-the-complete-money-s.mp4` | in `launch/1099-money/content.json`, set `"footage"` on the "Monthly hour" segment to that path |

Then:

1. If you used `factory batch-record`, save the files under the names its shot list gives and run
   `factory batch-record attach <session folder>` instead of editing paths by hand.
2. Re-render the two long videos with `factory rerender <post id>` (the ids are in `factory recordings`),
   then check them in Review.
3. Run `factory recordings`: the three items should be gone, and the Nov 21 session's three are next.
4. `factory launch-check`: neither long video should show the original-element block any more.
