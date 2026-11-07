# Scam Decoded: launch kit

Brand #2 from research/04-adjacent-niches.md (scams, fraud and identity theft). Working name was "Scam Shield";
renamed because T-Mobile sells an anti-scam app called Scam Shield (and there's a SCAMSHIELD trademark filing).
Check @scamdecoded is free on Instagram, TikTok and YouTube before creating accounts.

| File | What |
|---|---|
| `../../brands/scam-decoded.yaml` | Brand profile: pillars, voice, palette, accounts, affiliates, AI disclosure |
| `content.json` | 14 Shorts (30–45s), 14 TikTok cuts (60–90s, second worked example each), 8 carousels. Every hook opens with a number. |
| `lead-magnet.json` | Free checklist for the link-in-bio email signup |
| `product/` | The Family Scam-Proofing Kit: PDF, source HTML, store listing |
| `POSTING_PLAN.md` | 14-day schedule |
| `weeks-3-6.json`, `POSTING_PLAN_WEEKS_3-6.md` | Nov 21 – Dec 18: 12 Shorts, 12 TikTok cuts, 8 carousels, 4 YouTube long-form (holiday-season scams) |

Build the postable pack (slides, thumbnails, captions, brand kit, link page) and queue everything for review:

```bash
factory pack launch/scam-decoded/content.json --brand scam-decoded --out dist/scam-decoded
```

Without a voice key, videos come out as thumbnail + caption + script in `videos-need-voice/`. With a real voice
(Piper, ElevenLabs or OpenAI; docs/CREDENTIALS.md §4) the same command renders narrated MP4s into `videos/`.

## Affiliates (placeholders until approved)

| Offer | Network | Pays | Placed in | Notes |
|---|---|---|---|---|
| Aura (identity theft protection) | Impact | $65+ per enrollment, 60-day cookie | #1/#15, #29, #31 captions; link page | Always say a credit freeze is free and doesn't need a paid service. Never imply Aura prevents identity theft. |
| 1Password | FlexOffers | 25% of first payment, 45-day cookie | #21, #32 | Say any reputable password manager works. |
| NordVPN | Direct | up to 40% new sales, 30-day cookie | #32 | Keep VPN claims modest: an extra layer on public Wi-Fi, not a scam shield. |

1. Apply on Impact (Aura) and FlexOffers (1Password); NordVPN applies direct. Approval needs a live account with posts, so
   apply after week one.
2. Replace the `example.com/go/...` URLs in `brands/scam-decoded.yaml`, then `factory links sync` and `factory linkpage scam-decoded`.
3. Every affiliate caption already carries the FTC disclosure ("affiliate link… we may earn a commission"). Keep it in
   the caption body, not only the bio.

## Guardrails specific to this brand

- Example texts, names, numbers and links are fictional. Before posting, check that no slide shows a real phone number,
  domain or person.
- No "you've been hacked" panic hooks; the tone is calm and protective.
- Don't name a real company as a scammer. Name the brand being impersonated only when an official source says so.
- Numbers in hooks (e.g. "$110 million+ at Bitcoin ATMs") come from FTC/FBI releases listed under each piece; check for a
  newer figure before posting.
