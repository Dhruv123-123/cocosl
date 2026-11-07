# AI-content disclosure rules, November 2026: seven platforms checked against our packs

Written 2026-11-07. **Docs only.** It brings together the platform AI rules scattered across
`youtube-policy-review-nov-2026.md` (YouTube), `tiktok-instagram-monetization.md` (TikTok and Instagram) and
`pinterest-seo.md` (Pinterest). It adds Facebook, Etsy's **new 22 Oct 2026 rules**, Gumroad and Amazon KDP,
and then checks the publishers in `src/contentfactory/publish/` and the listing copy on the project drive.

## TL;DR: four gaps

1. **Our caption disclosure says something that isn't true.** Every brand's `ai_disclosure` says "Script
   **written** and fact-checked by a human" ("Guion escrito… por una persona" in Spanish). The scripts are
   drafted by an AI writer (`writer.write_script`), and our own Etsy listings say "AI tools helped draft the
   text". A disclosure that understates AI use is the one thing every platform's rules and the FTC's
   deception standard agree is wrong. **Fix:** "Visuals and voice made with AI tools. Script drafted with AI
   help and fact-checked by a person." Keep "written by a human" only if a person really writes each script.
   (This is Dhruv's call, in the brand yamls.)
2. **Etsy now bans "AI-generated functional guides"** (22 Oct 2026): "patterns, recipes, or instructions,
   where the information buyers rely on must be the seller's own work." About 15 of our Etsy listings are
   guides or kits (The 20-Minute Budget, Debt-Free Date Planner, Start Investing With $100 a Month, Bill Cut
   Kit, Credit Report Audit Kit, Rate & Contract Kit, the Dinero Simple guides…), and their listings
   honestly say AI helped draft the text. Etsy's examples are crafts and recipes, and it hasn't said whether
   money guides count. **Safest:** on Etsy, list only the printable trackers and planners. Sell the guides on
   Gumroad and our sites, or have Dhruv rewrite them so they really are his own work before listing them on
   Etsy.
3. **Facebook has no AI-label field in the API, but Meta's rule covers "realistic-sounding audio".** Meta
   requires its AI label for organic posts with "a photorealistic video or realistic-sounding audio that was
   digitally created or altered". Our Reels use a natural TTS voice. `publish/instagram.py` sends
   `is_ai_generated`, but `publish/facebook.py` can only put the disclosure in the caption. **Fix:** tick
   "AI info" by hand in Meta Business Suite for Facebook Reels with a TTS voice (or post Reels to Facebook
   from Instagram's cross-post, which carries the label). Add it to the Facebook manual checklist.
4. **Etsy photo rule:** digital downloads need "a visual preview or excerpt of the content buyers will
   receive". Ours use page renders, which pass. Never use an AI-generated mock-up as the only image of a
   printable.

Everything else is already covered: YouTube (`containsSyntheticMedia` only for realistic content, false for
our illustrated videos), TikTok (`is_aigc` on every post), Instagram and Threads (`is_ai_generated` /
`is_made_with_ai`), KDP (disclosure answers in `kdp/KDP_NOTES.md`), and the AI line in every Etsy and
Gumroad listing.

## 1. The rules, platform by platform

| Platform | What has to be labelled | Where and how | Our setting | Gap? |
|---|---|---|---|---|
| **YouTube** | Realistic altered or synthetic content a viewer could mistake for real (real people saying things they didn't, realistic events). Not needed for clearly unrealistic or animated content, or AI used for scripts and captions | "Altered or synthetic content" toggle in Studio, or `status.containsSyntheticMedia` in the API. Auto-labels from C2PA can't be removed | `containsSyntheticMedia` = `realistic_synthetic_media` (false for all brands) | No (see `youtube-policy-review-nov-2026.md`) |
| **TikTok** | Realistic AI-generated content; TikTok also auto-labels from C2PA metadata | AI-generated content toggle, or `is_aigc` in the Content Posting API | `is_aigc` true on every post | No. The "fully AI content can't earn Creator Rewards" point is in `tiktok-instagram-monetization.md` |
| **Instagram / Threads** | Photorealistic video or realistic-sounding audio that was digitally created or altered; Meta also auto-labels "AI info" from industry signals. AI-generated *people* in a profile need the "AI-generated profile" label (31 Aug 2026) | "AI label" toggle, or `is_ai_generated` / `is_made_with_ai` in the API | Sent on every post | No |
| **Facebook** | Same Meta rule | "AI info" toggle in the composer or Business Suite. **No API field for Page posts** (our `facebook.py` docstring) | Caption disclosure only | **Yes**, gap 3 |
| **Pinterest** | Pinterest applies "AI modified" itself on image Pins its classifiers or metadata flag (since 2025). No creator self-label | Automatic; appeal if wrong | Chart pins aren't AI images; FLUX pins may get the label | No, and the label is harmless |
| **Etsy** | Disclose when an item is "created using AI"; never call AI work handmade. **New 22 Oct 2026:** no AI-generated functional guides; at least one unedited photo for physical items; digital downloads need a real preview; note AI photo edits in the description | Listing description (no fixed wording) | Every listing has a "made with the help of AI tools" line (9 Dinero Simple listings say it in Spanish) | **Yes**, gap 2 |
| **Gumroad** | No AI-specific rule found in its terms (the Aug 2026 change was about multiple accounts). The FTC's deception rules still apply | Product description | AI line on storefront copy | No |
| **Amazon KDP** | AI-generated text, images or translations must be declared in the KDP dashboard (enforced since Apr 2026, per WriteO); AI-*assisted* editing needn't be | KDP upload form; not shown to buyers | `kdp/KDP_NOTES.md` answers yes for text and images | No |
| **All, from 1 Jan 2027** | California SB 1050: ads that prominently feature an AI-generated synthetic *performer* may need a disclosure (per Etsy's handbook) | In the ad or listing | We use no synthetic people | No, but keep avatars out |

## 2. The caption line, by brand (gap 1)

| Brand | Now | Suggested |
|---|---|---|
| Money Made Simple | "Visuals and voice made with AI tools. Script written and fact-checked by a human. Not financial advice." | "Visuals and voice made with AI tools. Script drafted with AI help and fact-checked by a person. Not financial advice." |
| Scam Decoded | "…Script written and fact-checked by a human. All example messages, names and numbers are fictional." | "…Script drafted with AI help and fact-checked by a person. All example messages, names and numbers are fictional." |
| 1099 Money | "…Script written and fact-checked by a human. Educational only…" | "…Script drafted with AI help and fact-checked by a person. Educational only…" |
| Dinero Simple | "Imágenes y voz hechas con herramientas de IA. Guion escrito y verificado por una persona…" | "Imágenes y voz hechas con herramientas de IA. Guion redactado con ayuda de IA y verificado por una persona…" (needs the fluent review) |

`guardrails.AI_DISCLOSURE` matches "AI tools" and "made with AI", so the new wording still passes the
check. `brands/_template.yaml` and `config.py`'s default should change the same way.

## Sources

- Etsy Seller Handbook, [22 Oct 2026 announcement](https://www.etsy.com/seller-handbook/article/1522733284810), and
  [Listing Image Requirements](https://www.etsy.com/legal/policy/listing-image-requirements/253962679005), read 2026-11-07;
  [Digital Commerce 360, 26 Oct 2026](https://www.digitalcommerce360.com/2026/10/26/etsy-ai-policy/amp/).
- Meta's rule: [Android Authority on Meta's AI labels](https://www.androidauthority.com/meta-ai-labels-3411262/) (quoting Meta);
  Meta's help page blocks automated reading.
- Pinterest: [Small Business Trends, May 2025](https://smallbiztrends.com/pinterest-gen-ai-content-labels/).
- KDP: [WriteO, Aug 2026](https://writeo.app/news/amazon-kdp-ai-disclosure-enforcement-2026) (secondary).
- Gumroad: [terms change record, 4 Aug 2026](https://conductatlas.com/change/2026-08-04-gumroad-gumroad-terms-of-service-4169/).
- YouTube, TikTok and Instagram: the sources in `youtube-policy-review-nov-2026.md` and `tiktok-instagram-monetization.md`.
- Our side: `src/contentfactory/publish/*.py`, `brands/*.yaml` on each brand branch, and 81 `LISTING*.md` files on the drive.
