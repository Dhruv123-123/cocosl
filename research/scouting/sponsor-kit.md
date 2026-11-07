# Sponsor-readiness kit: thresholds, rate card, media kits, 40 brands, emails

Written 2026-11-07. **Docs only. Nobody has been contacted.** Dhruv sends every email himself, and only
once a brand's channel passes the thresholds in section 1. Sponsor evidence comes from SponsorRadar's
public channel pages. Those detections are "deduced from evidence, not confirmed by the channel or brand",
so treat each one as a lead, not a fact. Rates build on `youtube-monetization.md`.

## TL;DR

1. **Don't pitch until a channel passes the gate:** 1,000+ subscribers, 10+ long videos in the last 90
   days, a median of 1,000+ views on the last 10, a mostly US audience, and no strikes. Before that, a
   pitch spends the one first impression a brand gives you.
   - **DeleteMe is the exception.** Its creator page says "every Creator is welcome", so Scam Decoded can
     apply through the form earlier (`youtube-monetization.md`).
2. **Price from views, not subscribers:** price = median views of the last 10 long videos × CPM ÷ 1,000 ×
   format multiplier. Use a $35 CPM for finance at our size, with a $75 floor. At 2,000 median views, a
   60-90 second integration is $75. At 5,000 it's $175. At 20,000 it's $700.
3. **The best first targets are brands already paying faceless money channels again and again:**
   **Monarch** (How Money Works and Wall Street Millennial), **DeleteMe** (both), **Ground News** (10 videos
   on Wall Street Millennial), **Policygenius** (24 on WhiteBoard Finance), **Brilliant** (17 on How
   Money Works), **Seeking Alpha** and **Cloaked**.
4. **Tell sponsors up front that narration and visuals are AI-assisted and a person checks every script.**
   Some will say no. That's better than finding out after the video is live.

## 1. The gate: when Dhruv may start sending

A brand's channel may be pitched only when **all** of these are true. Check them in YouTube Studio
(Analytics → Advanced) and `factory report`.

| # | Threshold | Why |
|---|---|---|
| 1 | **1,000+ subscribers** on the channel | Brands and tracker tools filter on it first. It's also roughly the YouTube Partner Program bar, which unlocks YouTube's own Creator Partnerships (the renamed BrandConnect) |
| 2 | **10+ long videos published in the last 90 days** | Proves a schedule. Brands buy future videos, not the archive |
| 3 | **Median views of the last 10 long videos ≥ 1,000** (median, not average, so one hit doesn't inflate it) | Below that the fee is under the $75 floor, and the brand's time costs more than the slot |
| 4 | **US audience ≥ 50%**, by viewer country | Most of these brands sell mainly in the US. Aura asks for a "primarily US audience". For Dinero Simple, use Spanish-speaking US viewers instead |
| 5 | **No Community Guidelines strikes and no "reused content" or inauthentic-content notices** in 90 days | A sponsor's legal team will check, and our risk audit (`youtube-monetization.md`) depends on it |
| 6 | **The brand passes our fit rules** (section 4): nothing in the "don't pitch" list, nothing the guardrails ban | Being paid doesn't change the rules |
| 7 | **For any "I use this" claim, Dhruv really uses the product** | The factory's fake-testimonial guardrail blocks invented experience. Without it, the read describes features, never experience |

**Exceptions:**
- Brands with open creator forms and no minimum (**DeleteMe**) can be applied to once thresholds 2, 5 and 6
  are met.
- Inbound offers can be answered any time, using the rate card.
- **The email list** is sold separately. Wait for **1,000+ subscribers** with a 40%+ open rate over the last 4
  issues. Open rates are inflated by Apple Mail Privacy Protection, so use clicks as the check (2%+ click
  rate).

## 2. Rate card formula

### Inputs (fill in from data, never guess)

| Input | Where it comes from |
|---|---|
| `V` = median views of the last 10 long videos at 30 days | YouTube Studio, or `factory metrics` |
| `S` = median views of the last 20 Shorts at 30 days | same |
| `CPM` = $35 at 1k-10k subscribers, $40 at 10k-50k, $50 above, for finance | 1of10 2026 rate guide: finance and investing $35-50+ (`youtube-monetization.md`) |
| `E` = email list size, `O` = average unique opens over the last 4 issues | Kit or Sender report |

### Prices

| Format | Formula | Floor |
|---|---|---|
| **Integration, 60-90 s, in a long video** | `V × CPM ÷ 1000 × 1.0` | $75 |
| Short mention, about 30 s | `V × CPM ÷ 1000 × 0.6` | $50 |
| **Dedicated video** (the whole video about the product) | `V × CPM ÷ 1000 × 3.0` | $250. Only for products we'd cover anyway, with editorial control kept |
| Sponsored Short | `S × CPM ÷ 1000 × 0.35` | $40 |
| Add-on: link in the description + pinned comment | +10% | — |
| Add-on: community or Instagram story post | +15% | — |
| **Bundle of 3 integrations over 3 months** | 3 × integration price × 0.85 | — |
| **Newsletter sponsored section** (one block, top of the email) | `O × $30 ÷ 1000` (*assumption: a common newsletter CPM per open; replace it with a real market check before quoting*) | $50 |
| Exclusivity (no competitor for 30 days) | +25% (*practice, not sourced*) | — |
| Usage rights (the brand reuses our clip in its ads) | +30% per 30 days (*practice*), and only if the AI-voice disclosure travels with it | — |

The 1.0 / 0.5-0.7 / 2-4× / 0.25-0.5 multipliers and the "+5-10%" for a description link come from the
1of10 guide, as quoted in `youtube-monetization.md`. The newsletter, exclusivity and usage numbers are
planning assumptions.

### Worked examples (integration, 60-90 s, $35 CPM)

| Median views `V` | Integration | Dedicated | Bundle of 3 |
|---|---|---|---|
| 1,000 | $75 (floor; formula gives $35) | $250 (floor) | $191 |
| 2,000 | $75 (floor; formula gives $70) | $250 (floor) | $191 |
| 5,000 | $175 | $525 | $446 |
| 10,000 | $350 | $1,050 | $893 |
| 20,000 | $700 | $2,100 | $1,785 |

A $75 floor at 1,000-2,000 views is above the formula. That's on purpose: a sponsor read takes a script
rewrite, a review and a slot. If a brand won't pay the floor, offer the **affiliate link** instead (most
of these brands have one), and let the results set the price.

**Performance deals** (CPA, or a flat fee plus CPA): accept them only with a flat floor, and only from brands
whose affiliate payout we can see. CPA-only is fine for affiliate programs, but it isn't a sponsorship.

## 3. Media kit template (one per brand)

Make it a one-page PDF or a hidden page on the brand's site (`/media-kit/`, `noindex`). Every number
comes from Studio, `factory report` or the email tool, **dated**. Leave out any row that doesn't have a
real number yet. Don't round up.

```
<BRAND> · Media kit · updated <YYYY-MM-DD>

<One-line positioning>
<Who watches: one sentence, from YouTube Analytics age/gender/country, not a guess>

AUDIENCE (last 90 days)
YouTube        <subs> subscribers · median <V> views per long video (last 10) · <S> per Short
               Watch time <hours> h · Top countries <US x%, ...> · Ages <top two brackets>
Instagram      <followers> · <median reach per post>
TikTok         <followers> · <median views per post>
Email          <E> subscribers · <O> avg unique opens · <click rate>% clicks (last 4 issues)

BEST WORK
1. <title> · <views> · <link>
2. <title> · <views> · <link>
3. <title> · <views> · <link>

FORMATS AND RATES (valid 30 days)
60-90 s integration in a long video    $<V×CPM/1000, floor $75>
Dedicated video                         $<×3, floor $250>
Sponsored Short                         $<S×CPM/1000×0.35, floor $40>
Newsletter top block                    $<O×30/1000, floor $50>
3-month bundle (3 integrations)         $<×3×0.85>

HOW WE WORK
- Every sponsorship is disclosed: YouTube's "includes paid promotion" box, a spoken
  "this video is sponsored by", and #ad / Paid partnership labels elsewhere.
- Narration and visuals are AI-assisted. A person writes or approves every script,
  and AI-made visuals are labelled where platforms ask.
- You review the sponsor segment for accuracy before it goes live. We keep editorial
  control of the rest of the video.
- We don't promise results, earnings or "guaranteed" anything, and we don't pretend to
  have used a product we haven't.

PAST PARTNERS   <only real ones, or leave this section out>
CONTACT         <name> · <brand inbox> · <site>
```

### Per-brand lines to fill in the template

| Brand | One-line positioning | Audience to state (only once Analytics confirms it) | Categories that fit | Never promote |
|---|---|---|---|---|
| **Money Made Simple** | "One money move a week, explained in under a minute: budgeting, debt, credit and first investing." | US adults in their 20s and 30s starting out | Budgeting apps, credit-builders, high-yield savings, bill-cutting (mobile plans), insurance comparison, money courses | Trading apps, crypto lending, gold IRAs, payday or "instant cash" loans |
| **Scam Decoded** | "Weekly scam alerts and plain checks that stop them, for you and the parents you look out for." | US adults; often people protecting older relatives | Data-broker removal, identity protection, password managers, email/phone masking, privacy carriers, news-literacy | VPNs that market "total anonymity" claims, anything sold by fear-pricing, crypto |
| **1099 Money** | "Taxes, rates and money for freelancers and gig workers, so April isn't scary." | US freelancers, contractors, gig drivers | Payroll and invoicing, LLC formation, bookkeeping, tax software, job boards, freelancer tools, print-on-demand | Tax "loophole" services, debt relief, anything promising refunds |
| **Dinero Simple** | "Tu dinero en orden, un paso a la vez, en español." | Spanish-speaking adults in the US | Remittances with clear fees, budgeting apps with Spanish support, credit-builders, insurance in Spanish | Remittance services with hidden FX markups, tandas apps without licensing, crypto |

## 4. 40 finance-adjacent brands that sponsor faceless channels

**Evidence key** (SponsorRadar channel pages, all updated Oct-Nov 2026 unless noted):
- **HMW** = How Money Works (1.8M; 117 deals)
- **WSM** = Wall Street Millennial (371K; 60 brands)
- **EE** = Economics Explained (2.89M; 53 deals)
- **WBF** = WhiteBoard Finance (1.03M; 60 sponsored videos)
- **MMBA** = Modern MBA (845K)
- **MM** = MagnatesMedia (1.86M; page updated Sep 2025)
- **Brand page** = SponsorRadar's page for the brand itself, quoted in `youtube-monetization.md`

Numbers in brackets are detected sponsored videos on that channel.

**Route** says how to get in. Where it says "creator page", find the brand's own influencer or creator
page on its website. **No email addresses are given here unless the brand publishes one.** Look up the
current contact on the day.

| # | Brand | What it is | Evidence | Fits | Route |
|---|---|---|---|---|---|
| 1 | **Monarch** | Budgeting app | HMW (6 + 3 as "Monarch Money"), WSM (6 + 1) | MMS, Dinero | Affiliate first; creator page; pitch with the bundle |
| 2 | **DeleteMe** | Data-broker removal | HMW (3), WSM (3) | Scam Decoded | [Creator form](https://joindeleteme.com/influencers), "every Creator is welcome" |
| 3 | **Policygenius** | Insurance comparison | WBF (24) | MMS, 1099, Dinero | Creator page; mention the WhiteBoard Finance-style recurring slot |
| 4 | **Ground News** | News comparison app | WSM (10 + 2), EE (3 + 2) | Scam Decoded, MMS | Creator page |
| 5 | **Brilliant** | Learning (maths, data) | HMW (17), WSM (5) | MMS, 1099 | Creator page |
| 6 | **Seeking Alpha** | Investing research | WBF (most recent, Sep 2026), WSM (2) | MMS (investing basics only) | Creator page; keep it to research, not stock picks |
| 7 | **Cloaked** | Email/phone masking | HMW (Sep 2026), WSM (1) | Scam Decoded | Creator page |
| 8 | **Cape** | Privacy-first mobile carrier | HMW (4 + 3), WSM (1) | Scam Decoded | Creator page |
| 9 | **NordPass** | Password manager | WSM (3) | Scam Decoded | Creator page or affiliate |
| 10 | **Surfshark** | VPN | EE (7) | Scam Decoded | Creator page. Read the claims carefully; no "makes you anonymous" lines |
| 11 | **Saily** | Travel eSIM | EE (5) | MMS (travel money) | Creator page |
| 12 | **Holafly** | Travel eSIM | WSM (1) | MMS, Dinero | Creator page |
| 13 | **Mint Mobile** | Low-cost mobile plan | WSM (Oct 2026, most recent) | MMS (Bill Cut Kit topic) | Creator page |
| 14 | **Kikoff** | Credit-builder | WBF (2) | MMS, Dinero | Creator page; check the fee and APR wording |
| 15 | **Chime** | Banking app | EE (21 Oct 2026, most recent) | MMS, Dinero | Creator page |
| 16 | **Bilt** | Rent-rewards card | WSM (2) | MMS | Creator page; card terms need the issuer's disclosures |
| 17 | **Remitly** | Remittances | MMBA (1) | **Dinero Simple** | Creator page; fees and exchange rate must be shown on screen |
| 18 | **Gusto** | Payroll and contractor payments | MMBA (1) | 1099 | Creator page |
| 19 | **Bizee** | LLC formation | MM (3) | 1099 | Creator page |
| 20 | **Odoo** | Business software (invoicing, accounting) | HMW (15) | 1099 | Creator page |
| 21 | **Zapier** | Automation | MMBA (1) | 1099 | Creator page |
| 22 | **GoDaddy** | Domains and websites | WSM (2) | 1099 | Creator page |
| 23 | **Grammarly** | Writing assistant | EE (3) | 1099 | Creator page |
| 24 | **Printify** | Print-on-demand | WSM (3) | 1099 | Creator page; no income claims |
| 25 | **ZipRecruiter** | Job board | WSM (2) | 1099, MMS | Creator page |
| 26 | **TripleTen** | Career bootcamp | WSM (1) | MMS | Creator page; no salary promises |
| 27 | **FSA Store** | Health spending account store | WSM (1) | MMS, 1099 (HSA/FSA topics) | Creator page |
| 28 | **Masterclass** | Online classes | WSM (1) | MMS | Creator page |
| 29 | **Storyblocks** | Stock media | WBF, WSM (6), MM (5) | 1099 (creators who freelance) | Creator page |
| 30 | **Dropbox** | Cloud storage | MM (1) | 1099 | Creator page |
| 31 | **NetSuite** | Business ERP | MMBA (8) | 1099 (later, bigger audience) | Agency route; a long shot at our size |
| 32 | **ShipStation** | Shipping software | MM (2) | 1099 (sellers) | Creator page |
| 33 | **Scribe** | Documentation tool | WSM (1) | 1099 | Creator page |
| 34 | **Superhuman** | Email app | MMBA (Jul 2026) | 1099 | Creator page |
| 35 | **Investing Pro** | Investing research | WSM (2) | MMS (investing basics) | Creator page; research only, no picks |
| 36 | **Aura** | Identity theft protection | Brand page: 642 channels, ~$1.1-2.1k a video | Scam Decoded, MMS | `influencers@aura.com` (published on its [influencer page](https://www.aura.com/influencer-program)). Wants firsthand use and a primarily US audience |
| 37 | **Incogni** | Data-broker removal | Brand page: 1,207 channels, 3.2 videos per creator | Scam Decoded | No public form. Pitch at a larger size |
| 38 | **Rocket Money** | Subscription cancelling and budgeting | Affiliate ($4-10 a signup), no faceless sponsorship found | MMS | Affiliate first |
| 39 | **YNAB** | Budgeting app | Affiliate, no faceless sponsorship found | MMS | Affiliate first |
| 40 | **Branch** | (Several companies use this name, so confirm which one before pitching) | WSM (2) | — | Confirm first |

### Don't pitch (seen on these channels, but against our rules)

| Brand or type | Seen on | Why not |
|---|---|---|
| Trading 212, Moomoo | EE (5), WSM (3) | Trading apps. Our guardrails keep away from trading and "get rich" framing |
| Nexo | WBF (2) | Crypto lending |
| JM Bullion, Gold Standard IRA | WBF (7, 3) | Gold and precious-metals IRAs, sold with fear-of-collapse marketing |
| BetterWealth | MM (1) | Sells "infinite banking" whole-life insurance strategies. Too close to the "guaranteed" framing we avoid |
| Differentiated Analytics | WSM (71) | Looks like the channel's own product, not an outside sponsor |
| BetterHelp, Zocdoc, MANSCAPED, Raycon, Flexispot, AI-tool brands | various | Not finance-adjacent. Fine for some creators, off-topic for ours |

## 5. Email drafts

Plain text, short, one ask. Send from the brand inbox. Fill every `<>`, and delete any line without a real number.

### A. First pitch (cold)

> **Subject:** <Brand> × <Our brand>: <topic> video for <their customer>
>
> Hi <name or "partnerships team">,
>
> I run <Our brand>, a faceless YouTube channel that explains <one line>. Our last 10 long videos have a
> median of <V> views, <US %>% from the US, mostly <age range>. Media kit: <link>.
>
> I'm planning a video on <specific topic that genuinely needs their product category>, going live
> around <date>. A 60-90 second <Brand> segment would fit naturally where we cover <the step>.
>
> Rates are in the kit (<price> for one, or <bundle price> for three over three months). Every sponsorship
> is clearly disclosed. Our narration and visuals are AI-assisted, and a person writes and checks every
> script. You'd review your segment for accuracy before it goes live.
>
> Would <Brand> be open to a first video?
>
> <Dhruv> · <Our brand> · <site>

### B. Follow-up (7 days later, once only)

> **Subject:** Re: <original subject>
>
> Hi <name>, following up once on this. The <topic> video is locked for <date>, so I can hold the
> sponsor slot until <date − 7 days>. If now's not right, is there a better person or time? Thanks either
> way.

### C. Affiliate to sponsor (when an affiliate link is already earning)

> **Subject:** <Our brand> has sent <N> <signups/trials> through our <Brand> link: a sponsored slot?
>
> Hi <name>, our <Brand> affiliate link has driven <N> <conversions> since <month>, from <X> videos. We'd
> like to give <Brand> a proper 60-90 second segment in an upcoming video on <topic>: <price>, or
> <bundle> for three. Media kit: <link>. Happy to keep the affiliate link in the description alongside.

### D. Renewal or series (after a sponsored video has run)

> **Subject:** <Brand> results + next three videos
>
> Hi <name>, here's how the <date> video did: <views> views at 30 days, <clicks> clicks on the link,
> <conversions if they shared them>. We'd like to make <Brand> a regular. Three integrations over the next
> three months at <bundle price>, on <topic 1>, <topic 2>, <topic 3>. Want me to send dates?

### E. Reply to an inbound offer

> Hi <name>, thanks for reaching out. Our rates are in the media kit: <link> (<price> for a 60-90 second
> integration based on our current median of <V> views). Two things to know first: every sponsorship is
> disclosed, and our narration and visuals are AI-assisted with a person writing or checking every
> script. If that works for <Brand>, which product and timing do you have in mind?

### F. Spanish (Dinero Simple, first pitch; needs a native speaker's review)

> **Asunto:** <Marca> × Dinero Simple: video sobre <tema> para hispanohablantes en EE. UU.
>
> Hola <nombre>:
>
> Hago Dinero Simple, un canal de YouTube en español sobre <una línea>. La mediana de nuestros últimos 10
> videos largos es de <V> vistas, <US %>% desde EE. UU. Kit de medios: <enlace>.
>
> Preparo un video sobre <tema> para el <fecha>, y un segmento de 60-90 segundos de <Marca> encajaría donde
> explicamos <el paso>. Las tarifas están en el kit. Todo patrocinio se indica con claridad. La narración
> y las imágenes se hacen con ayuda de IA, y una persona revisa cada guion.
>
> ¿Les interesaría un primer video?

## 6. When a deal comes through: the checklist

1. **Written terms first:** fee, format, length, live date, review rounds (one), payment date (net 30 at
   most), usage rights (none by default), exclusivity (none by default).
2. **Script:** the sponsor segment goes through the factory's normal review. Add the sponsor's required
   claims only if we can check them, and add our own disclosure line.
3. **Mark the post sponsored** (`meta.sponsored: true`). The YouTube publisher then uploads it as **private**
   and returns `needs_studio`. Tick "includes paid promotion" in Studio before publishing (this PR).
4. **Other platforms:** TikTok's commercial content toggle ("Branded content" → "Paid partnership"),
   Instagram's Paid partnership label, and "#ad" in the first line of the caption.
5. **Report back at 30 days** with email D, and log the deal in the brand's media kit under "Past partners".

## Open questions for Dhruv

1. Is the $75 floor right? The alternative is to accept less from brands that fit very well.
2. Does Dhruv personally use any of the "I use this" products (Monarch, a password manager, DeleteMe,
   Aura)? That decides which reads can say so truthfully.
