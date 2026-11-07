# Recording session prep: Saturday, November 28, 2026

Three items, about 40 minutes. Send the permission request first so the seller has days to answer, then two
screen recordings.

| # | Item | Brand | Type | Length | Posts |
|---|---|---|---|---|---|
| 1 | A real seller's OK to rate their listing | Ad studio (Post 13) | written permission | n/a | Wed Dec 2 |
| 2 | "What you actually get for $49" | Ad studio (Post 14) | screen recording | 15–25 s finished | Thu Dec 3 |
| 3 | Finding a credit bureau's freeze page | Scam Decoded | screen recording | 10–30 s | Sun Dec 6 |

## Print these

1. **Item 1** (`CONTENT_PLAN_4_WEEKS.md`, Post 13). Use a seller's listing **only if they asked and agreed in
   writing** (a DM or email saying yes is enough; save a screenshot). If nobody has by Tue Dec 1, use the
   fallback in the plan: rate the `loamy-days-pot` sample again from a new angle ("round 2"). Nothing to record today.
2. **Item 2 beats** (Post 14). Hook: "What you actually get for $49". Show: the delivery folder opening
   (`listing_etsy.mp4`, `social_9x16.mp4`, captions, the how-to note) → uploading the video to an Etsy listing
   in the editor. Use a demo account or your own test listing, never a client's.
3. **Item 3 narration** (it plays over your recording):
   > "The credit freeze. It stops lenders from pulling your credit report, so most new credit accounts can't be
   > opened in your name. It's free at Equifax, Experian and TransUnion by federal law …"
   Source: `weeks-3-6.json`, *Credit freeze vs fraud alert vs monitoring: what you actually need*, beat 2.

## Setup (10 minutes)

Same as the Nov 14 sheet (`docs/RECORDING_PREP_2026-11-14.md`):

- **Screen:** 1920×1080, browser zoom 125%, a private window, logged out of everything, bookmarks bar hidden,
  notifications off. **Phone screen recordings:** Do Not Disturb on, and hide the status bar's carrier name
  and notifications if you can.
- **Never show personal data.** Type nothing real into any form; blur numbers, codes and names afterwards.
- **Recorder:** macOS Shift-Cmd-5, OBS, or Windows Game Bar (Win-G); on a phone, the built-in screen recorder.
  1080p or better, 30 fps.
- **Phone camera clips:** natural side light, phone held still (lean on something), 3–5 s per clip.

## The recordings

**2 · Ad studio, the $49 delivery** (≈ 20 min). Make a demo delivery folder from a sample project in
`etsy-shopify-line/samples/` (e.g. the Fernhollow mug's `listing/` cut and a vertical cut). Record opening it
and uploading the listing video to a test listing; stop before publishing. Speed it up to 15–25 s and add the
hook as text. Caption must say it's a demo with a sample product.

**3 · Scam Decoded, freeze page** (≈ 10 min). Type one bureau's address yourself (don't click an ad), find the
freeze button, **stop at sign-in**. Pause 2 s on the button.

## Export and save

| Item | Export | Save as | Then |
|---|---|---|---|
| 2 | MP4 (H.264), 1080×1920, 15–25 s, a licensed music bed | `ai-ad-studio-v2/social-posts/14-what-you-get.mp4` | post Thu Dec 3 with Post 14's caption |
| 3 | MP4 (H.264), 1080p, 10–30 s | `footage/scam-decoded/credit-freeze-vs-fraud-alert-vs-monitori--freeze.mp4` | picked up from beat 2 at render |

## Afterwards (10 minutes)

1. `factory recordings`: the items above should be gone (it also shows the current file name for any long
   video, if one changed since this sheet was written on Nov 7).
2. If you used `factory batch-record`, run `factory batch-record attach <session folder>`.
3. Re-render each long video with `factory rerender <post id>` and check it in Review.
4. `factory launch-check`: no original-element block left on those videos.

