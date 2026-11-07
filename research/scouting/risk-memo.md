# What could go wrong: an honest risk memo for the whole business

Written 2026-11-07 for Dhruv. **Docs only.** It pulls together the risks found across 55 research files
and adds the FTC review rule and the Copyright Office's AI ruling. Each risk gets a likelihood and an
impact (our judgment), what would trigger it, and what's already in place or still needed. Nothing here
is legal advice. Section 4 lists the risks that need a lawyer's read (`spanish-and-legal-review-options.md`
has the $35 route).

## TL;DR: the five that matter most

| # | Risk | Likelihood | Impact | The one thing to do |
|---|---|---|---|---|
| 1 | **Burnout / not enough time.** Four brands, each needing about 15 minutes of replies a day, on top of reviews, uploads by hand (TikTok) and listings | **High** | **High**: everything stops | **Launch two brands, not four** (1099 Money and MMS first, `launch-playbook.md`). Add a brand only when the first two run in under an hour a day for 4 weeks |
| 2 | **A platform restricts or ends an account** for unoriginal or mass-produced content | Medium | High | One original element per long video (`youtube-policy-review-nov-2026.md`); never reupload across accounts; check Account Status weekly |
| 3 | **A misleading money claim** (a wrong number, "guaranteed", an FDIC-insured fintech, an ITIN statement) | Medium | High (complaints, FTC exposure, lost trust) | `claims_to_verify` in every sequence and pack; link the official source; the lawyer's read on the ITIN and credit pages |
| 4 | **Undisclosed affiliate links or fake social proof** | Low (if the rules are followed) | **High**: the FTC review rule allows up to **$51,744 per violation** | Disclosure beside every affiliate mention (in Spanish for Dinero Simple), and no bought followers, reviews or likes, ever |
| 5 | **Nothing sells for months** | **High** in year 1 | Medium (it's time, not money; the spend is about $45) | The revenue model already plans for it: conservative case about $1.3K in year 1. Judge at months 3 and 6 against `launch_thresholds.json` |

## 1. Platform risk

| Risk | Trigger | Already in place | Still needed |
|---|---|---|---|
| YouTube strikes or termination (3 in 90 days) | "Using automated tools or AI to churn out high volumes of similar content with minimal changes"; comment spam; misleading thumbnails | Hook library rotates structures; originality review of the packs | Fix Scam Decoded's 23 long videos with no original element **before** they upload |
| TikTok For You ineligibility | Unoriginal uploads, watermarks, QR codes, engagement bait | No QR codes; brand captions use plain asks (checked on MMS) | Same caption check on the other brands' packs (`first-100-followers-2026.md`) |
| Instagram "not recommended" | Reposts, watermarks, recommendation-guideline breaches | Originals only | Weekly Account Status check |
| Etsy delisting | AI-generated "functional guides" banned since 22 Oct 2026; fake "was" prices | `ai-disclosure-rules-nov-2026.md` flagged about 15 listings; BFCM plan avoids "was" prices | Move or rewrite those 15 listings **before** the shop opens |
| API access lost | TikTok won't approve a "utility" upload tool; Pinterest Standard access needs a demo video | Post TikToks by hand; YouTube personal-use OAuth | Nothing new. Don't build anything that depends on TikTok's API |
| **Concentration** | One platform changes its rules or pays less (e.g. YPP's 8,000 hours from 1 Feb 2027) | Products and email are the biggest revenue line in every case | **Grow the email list first.** It's the only audience we own (`first-100-subscribers.md`) |

## 2. Legal and regulatory risk

| Risk | What the rule says | Mitigation |
|---|---|---|
| **FTC endorsements and reviews** | The Consumer Reviews and Testimonials Rule (16 CFR 465, effective 21 Oct 2024) bans fake reviews, buying positive reviews, undisclosed insider reviews, and buying "fake indicators of social media influence". Up to $51,744 per violation, inflation-adjusted | Never buy followers, likes or reviews. Never post reviews of our own products as a "customer". Disclose affiliates next to the link, in the post's language (`affiliates-for-new-creators.md`) |
| **CAN-SPAM** | Postal address, a working opt-out honoured within 10 business days, and no misleading headers or subjects. Up to $53,088 per email (FTC, Jan 2024 figure) | Sender's footer plus a PO box address; never import a list we didn't collect (`sender-setup-guide.md`) |
| **Investment content** | Personalised investment advice for pay can make you an investment adviser. General, impersonal education is the safe side. The SEC Marketing Rule applies to advisers' ads (`affiliates-for-new-creators.md`) | Keep content general ("what an index fund is"), never "buy X". `footer_note` says it isn't financial advice |
| **Banking claims** | FDIC Part 328: don't call a fintech a bank or "FDIC-insured" loosely | The MMS welcome already says "check the account is FDIC or NCUA insured". Keep that wording |
| **Immigration-adjacent content** | Only attorneys and accredited representatives may give immigration legal advice. Scams by unauthorised "notarios" are a known harm | Dinero Simple explains and links to IRS, CFPB and USCIS Spanish pages; no individual guidance; a lawyer's read of the ITIN and credit pages (flagged on PR #11) |
| **Tax content** | Explaining the rules is fine; preparing returns for pay is regulated | 1099 Money stays educational, with "check with a tax pro or VITA" lines |
| **Trademarks** | SCAMSHIELD is a live T-Mobile mark (`domains-and-names.md`) | Brand is Scam Decoded. No bank or card logos in B-roll (`free-tools-round4.md`) |
| **Dhruv's own taxes** | Business income here is self-employment income | Ironically, 1099 Money's own Quarterly Tax Tracker covers it. Use it, and set aside a share of every payout |

## 3. Copyright and AI risk

| Risk | What applies | Mitigation |
|---|---|---|
| **Our AI-made assets aren't ours to protect** | The Copyright Office (Part 2 report, 29 Jan 2025): prompts alone don't make you the author. Human selection, arrangement and modification can be protected | That's fine for content, which we don't need to own exclusively. For **products**, add real human work (the layout, the worked examples, the editing), and don't promise buyers exclusive rights |
| Someone else's copyright in our videos | Music, fonts, stock clips, other creators' videos | Licensed fonts only; Pexels and Pixabay terms (`free-tools-round4.md`); Stitch or Remix only through the platforms' own tools; a `credits.json` per video |
| Non-commercial model weights | F5-TTS, MusicGen and ctc-forced-aligner's MMS model are non-commercial (`pipeline-tools-round3.md`) | Kokoro (Apache-2.0) for voice; the avoid list in each tools file |
| Copyleft code in the product | AGPL or GPL tools vendored into anything we sell or host | The avoid lists (etro, clips-studio, OpenMontage); TaxHacker is MIT, so the receipt-tracker pack keeps its notices (`receipt-tracker-plan.md`) |
| **AI disclosure wording is wrong** | Every brand's caption says "Script written and fact-checked by a human", but the scripts are AI-drafted (`ai-disclosure-rules-nov-2026.md`) | Change it to "drafted with AI help and fact-checked by a person". **This is the one open item that's simply untrue today.** Dhruv's call, but it should be fixed before launch |

## 4. Business and operational risk

| Risk | Mitigation |
|---|---|
| **Burnout** (see TL;DR #1) | Two brands first. Batch reviews weekly. The engagement routine is capped at 15 minutes a brand. Stop rules in `launch-playbook.md` include "launch fewer brands" |
| Review bottleneck (Spanish 116-175 hours; legal) | Dinero Simple is already paused to a lean set. A paid two-hour test with a student reviewer before committing (`spanish-and-legal-review-options.md`) |
| Email deliverability (spam complaints) | Double opt-in, own domains with SPF and DKIM, and the 0.1% complaint threshold in `launch_thresholds.json` |
| Payment holds or account reviews on Gumroad and Etsy | Clear product descriptions, no off-site links on Etsy (the products thread already strips them), and refunds handled quickly |
| One person, one laptop | Factory data backups (`main` has `backup.py`), and passwords in a manager, not in the repo |
| Spending creep | The only planned spend is about $45 a year for domains. Every other spend (reviewers, a Sender upgrade, ads) waits for its gate (`paid-acquisition.md`) |

## 5. What to decide before launch (in order)

1. **Launch two brands or four?** The research supports two.
2. **Fix the AI-disclosure wording** in the brand files.
3. **Move or rewrite the ~15 Etsy guide listings** affected by Etsy's AI rule.
4. **Book one $35 lawyer consult** for the Dinero ITIN and credit pages, when Dinero resumes.
5. **Get a PO box or virtual mailbox** for the CAN-SPAM footer (the address must be real).

## Sources

Read 2026-11-07:
[FTC Consumer Reviews and Testimonials Rule, via Morgan Lewis](https://www.morganlewis.com/pubs/2024/08/ftc-issues-final-rule-on-consumer-reviews-and-testimonials);
[US Copyright Office: AI report Part 2](https://copyright.gov/newsnet/2025/1060.html) (29 Jan 2025);
[FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business);
[YouTube spam policy](https://support.google.com/youtube/answer/2801973);
[TikTok For You feed standards](https://www.tiktok.com/community-guidelines/en/fyf-standards);
and the research files named in each row (all on PR #2).
