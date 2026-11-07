# Recording session prep: Saturday, December 5, 2026

Two screen recordings, about 30 minutes.

| # | Clip | Brand | Type | Length | Posts |
|---|---|---|---|---|---|
| 1 | "3 products, 6 videos, 4 working days" (Shop Trio) | Ad studio (Post 19) | screen recording, sped up | 20–30 s finished | Thu Dec 10 |
| 2 | Starting a report on IdentityTheft.gov | Scam Decoded | screen recording | 10–30 s | Sun Dec 13 |

## Print these

1. **Clip 1** (`CONTENT_PLAN_4_WEEKS.md`, Post 19). Hook: "3 products, 6 videos, 4 working days". Show three
   products going through one batch: plan → shots → a listing cut and a social cut each, in a matching style.
   Use three samples from `etsy-shopify-line/samples/` (e.g. Fernhollow mug, Knotwork hanger, Marigold
   bandana), not client work.
2. **Clip 2 narration** (it plays over your recording):
   > "Step three, report it at IdentityTheft dot gov. It's the FTC's official site. You answer questions about
   > what happened, and it creates an FTC Identity Theft Report plus a personalised recovery plan with
   > pre-filled letters …"
   Source: `weeks-3-6.json`, *Identity theft recovery, step by step (what to do in the first week)*, beat 5.

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

**1 · Ad studio, Shop Trio batch** (≈ 20 min). Record the real batch at normal speed, then speed it up to
20–30 s and add the hook. Caption: "The Shop Trio: three of your products, each with a listing cut and a
social cut, in a matching style. $99." Say they're sample products.

**2 · Scam Decoded, IdentityTheft.gov** (≈ 10 min). Type identitytheft.gov yourself, start a report, pick a
category, and **stop before any personal details**.

## Export and save

| Clip | Export | Save as | Then |
|---|---|---|---|
| 1 | MP4 (H.264), 1080×1920, 20–30 s, a licensed music bed | `ai-ad-studio-v2/social-posts/19-shop-trio.mp4` | post Thu Dec 10 with Post 19's caption |
| 2 | MP4 (H.264), 1080p, 10–30 s | `footage/scam-decoded/identity-theft-recovery-step-by-step-wha--3-report.mp4` | picked up from beat 5 at render |

## Afterwards (10 minutes)

1. `factory recordings`: the items above should be gone (it also shows the current file name for any long
   video, if one changed since this sheet was written on Nov 7).
2. If you used `factory batch-record`, run `factory batch-record attach <session folder>`.
3. Re-render each long video with `factory rerender <post id>` and check it in Review.
4. `factory launch-check`: no original-element block left on those videos.

