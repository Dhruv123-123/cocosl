# Compliance built into the factory

Every rule below is enforced in code, not just written down. Where it's a judgment call the factory
warns and the human decides; where it's a clear violation it blocks.

| Risk | Rule it comes from | What the factory does | Where |
|---|---|---|---|
| Repetitive, mass-produced uploads | YouTube "inauthentic content" (Jul 2025), Meta unoriginal content (Jul 2025), Instagram repost rule (Apr 2026) | Compares each script with the brand's last 200 posts (3-word shingles). Warns at 35% overlap, blocks at 60%. Repurposed Shorts are rewritten, not trimmed. | `guardrails.check_originality`, `repurpose.py` |
| Flooding | Platform spam policies | Per-platform daily cap per brand; scheduler never exceeds it; one account per platform per brand. | `scheduler.py`, `guardrails.check_cadence` |
| Undisclosed AI | YouTube altered/synthetic disclosure, TikTok AI labels, Meta AI info, EU AI Act Art. 50 | Brand disclosure appended to every caption/description. YouTube `containsSyntheticMedia` and TikTok `is_aigc` set via API. Blocks posts with realistic synthetic media and no label. | `guardrails.check_disclosures`, publishers |
| Fake testimonials | FTC rule on fake reviews (16 CFR 465, Oct 2024) | Detects first-person product claims; blocks them when an AI presenter is used, warns otherwise. Ad scripts are spokesperson/demo only. | `guardrails.TESTIMONIAL_PATTERNS`, `business/ugc.py` |
| Hidden affiliate links | FTC Endorsement Guides | Blocks posts with an affiliate link and no disclosure; helper adds one. | `guardrails.check_disclosures`, `business/affiliates.py` |
| Risky claims | Platform ad policies, FTC | Warns on "guaranteed", "cure", "get rich", income claims. | `guardrails.HYPE_PATTERNS` |
| Engagement bait / fake engagement | Platform policies, FTC rule bans buying fake indicators | Warns on bait phrasing. No code exists to like, follow, comment, DM or buy engagement. | `guardrails.ENGAGEMENT_BAIT` |
| Reposting others' media | Copyright, platform originality rules | Every asset carries provenance (generated, own, licensed); unknown sources block the post. No scrapers or downloaders. | `guardrails.check_assets_licensed`, `media/` |
| Likeness and voice | Right of publicity, Tennessee ELVIS Act | Prompts forbid real people; voice config notes "your own or licensed voice only". | `writer.SYSTEM`, `media/tts.py` |
| Unofficial posting tools | Platform terms | Publishers use only official APIs (Graph API, YouTube Data API, TikTok Content Posting API, Threads API, Postiz). | `publish/` |
| Unchecked facts | Accuracy, YouTube misinformation policy | Writer lists claims to verify; dashboard won't approve until each is ticked. | `writer.py`, dashboard |
| Cold email | CAN-SPAM | Outreach is drafts only, with real sender identity, address and opt-out line. Nothing auto-sends. | `business/pitch.py` |
| Auto-publishing without a human | Your own reputation | `require_human_review: true` by default; the daily job never approves; dry run is on until you turn it off. | `pipeline.py`, `.env` |

Switching any of these off means editing code. That's deliberate.
