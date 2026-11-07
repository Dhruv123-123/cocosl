# Recording session prep: Saturday, November 21, 2026

Two items, about 30 minutes. Phone clips first while the light is good, then the phone screen recording.

| # | Clip | Brand | Type | Length | Posts |
|---|---|---|---|---|---|
| 1 | "5 phone clips that make any product video better" | Ad studio (Post 7) | phone footage, 5 clips | 2 s each in the edit | Tue Nov 24 |
| 2 | Phone settings that stop scam calls | Scam Decoded | phone screen recording | 10–30 s | Sun Nov 29 |

## Print these

1. **Clip 1 beats** (`ai-ad-studio-v2/CONTENT_PLAN_4_WEEKS.md`, Post 7). Hook on screen: "5 phone clips that
   make any product video better". The five clips, each filmed 3–5 s, cut to 2 s:
   1) slow 360° turn · 2) your hand holding it, for scale · 3) close-up of the texture · 4) it in use ·
   5) the packaging or an unboxing.
   Use **your own item** (a mug on a windowsill is the plan's example).
2. **Clip 2 narration** (it plays over your recording; it tells you what to show):
   > "Step three, the phone. While you're there, turn on the phone's built-in spam call filtering, and
   > silence unknown callers if your parent is comfortable with that. Set an account PIN with their carrier
   > and turn on number lock or port-out protection if offered. Update the phone's software. And look for
   > remote access apps they didn't install on purpose …"
   Source: `launch/scam-decoded/weeks-3-6.json`, *How to protect your parents from scams: the complete guide*, beat 5.

## Setup (10 minutes)

Same as the Nov 14 sheet (`docs/RECORDING_PREP_2026-11-14.md`):

- **Screen:** 1920×1080, browser zoom 125%, a private window, logged out of everything, bookmarks bar hidden,
  notifications off. **Phone screen recordings:** Do Not Disturb on, and hide the status bar's carrier name
  and notifications if you can.
- **Never show personal data.** Type nothing real into any form; blur numbers, codes and names afterwards.
- **Recorder:** macOS Shift-Cmd-5, OBS, or Windows Game Bar (Win-G); on a phone, the built-in screen recorder.
  1080p or better, 30 fps.
- **Phone camera clips:** natural side light, phone held still (lean on something), 3–5 s per clip.

## The clips

**1 · Ad studio, five product clips** (≈ 15 min). Film each clip three times and keep the steadiest. Then cut
a 1080×1920 vertical video: 2 s per clip, the hook as text over clip 1, one of the studio's music beds
(`etsy-shopify-line/samples/reel/music/`, licences in `MUSIC_LICENSES.md`).

**2 · Scam Decoded, phone settings** (≈ 10 min). On your own phone: the setting that silences unknown callers,
your carrier's spam filter, and adding a contact as a favorite (use a made-up contact). Blur your number and any
real names afterwards.

## Export and save

| Clip | Export | Save as | Then |
|---|---|---|---|
| 1 | MP4 (H.264), 1080×1920, ≈ 12 s | `ai-ad-studio-v2/social-posts/07-five-phone-clips.mp4` | post Tue Nov 24 with Post 7's caption |
| 2 | MP4 (H.264), 1080p or the phone's native size, 10–30 s | `footage/scam-decoded/how-to-protect-your-parents-from-scams-t--phone-settings.mp4` | picked up from beat 5 at render |

## Afterwards (10 minutes)

1. `factory recordings`: the items above should be gone (it also shows the current file name for any long
   video, if one changed since this sheet was written on Nov 7).
2. If you used `factory batch-record`, run `factory batch-record attach <session folder>`.
3. Re-render each long video with `factory rerender <post id>` and check it in Review.
4. `factory launch-check`: no original-element block left on those videos.

