# Kit tutorials, rendered and waiting for a voiceover

Five tutorials from `self-serve-kits/tutorials/TUTORIALS.md` (project files), set up so the only thing left
is your voice. The screen footage was recorded by script (headless browser driving each maker with the
fictional practice photos), so there's nothing to screen-record.

| Spec | Video | Length (planned) | Where it goes |
|---|---|---|---|
| `lite-90s.yaml` | Your first listing video, free | ~1 min | Lite Gumroad page, kit email 1, pinned TikTok |
| `listing-kit.yaml` | Make a listing video from your photos | ~2½ min | Listing Video Kit page, YouTube |
| `pin-maker.yaml` | Pins and video pins from your photos | ~2 min | Pin Maker page, YouTube |
| `seasonal-sale.yaml` | Holiday sale posts from your photos | ~2 min | Seasonal Sale Kit page, YouTube |
| `which-one-60s.yaml` | Which kit do I need? | ~45 s | Bundle page, TikTok |

Why these five: they're the ones every product page and the email funnel link to. The Shop Refresh and
Cover Kit videos can follow the same pattern later.

## Use

```bash
F=/mnt/project-files/content-factory/ai-ad-studio-v2/self-serve-kits/tutorials/render/footage
factory tutorial-render launch/ugc-service/kits-tutorials/lite-90s.yaml --footage $F/lite-90s
```

That writes `output/tutorials/lite-90s/preview.mp4` (silent, with captions of the script),
`TELEPROMPTER.md` and `RECORD.md`. Record `voice/tutorials/lite-90s/beat-01.wav`, `beat-02.wav`, ...
(one per line) or one `full.wav`, run the same command again, and you get `final.mp4`.

Rendered previews of all five are already in the project files at
`self-serve-kits/tutorials/render/out/<id>/` (with their TELEPROMPTER.md and RECORD.md).

## Rules
- Your own voice. If you ever use a synthetic voice, set `ai_voice: true` in the spec: the video then carries an "AI voice" label the whole way through.
- The practice shops (Pebble & Co., Thistle & Pine) are fictional. Say "example shop" once, or leave the captions as they are.
- No sales numbers, no "this will boost your sales", no testimonials. The scripts show what the tools do.
- Etsy and Pinterest screens aren't recorded (we don't log into anyone's account); those beats are plain cards with the menu path.
