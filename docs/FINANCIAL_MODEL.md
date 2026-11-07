# Financial model: what it costs and what it could make

Written 2026-11-07. These are estimates with ranges, not promises. Every price below is from the
vendor's public pricing as best known on this date; **check each one before you pay**, because SaaS
prices change often. Revenue numbers are scenario models built on stated assumptions, and the
assumptions are the part to argue with.

Sources inside this repo: `docs/CREDENTIALS.md` (what accounts and keys exist), `brands/money-made-simple.yaml`
(cadence: 5 Shorts, 1 long video and 3 carousels a week; one $12 product), `launch/ugc-service/RATE_CARD.md`
(ad studio prices), `src/contentfactory/config.py` (default model `claude-opus-5-5`), and the research in
PR #1 (`research/`) for RPMs and affiliate payouts.

---

## 1. The short version

| | Lean start | Comfortable start |
|---|---|---|
| **Upfront (one-time)** | **≈ $40–60** | **≈ $200–400** |
| **Monthly running cost** | **≈ $30–45** | **≈ $80–130** |

| Monthly revenue around month 12 | Conservative | Base | Pops off |
|---|---|---|---|
| Total (gross) | **$0–500** | **$2,000–5,000** | **$20,000–45,000** |
| Rough chance (my judgment, not data) | most likely outcome | maybe 1 in 4 | maybe 1 in 20 or less |

The single most controllable line is the **AI ad studio**: it can pay in month 1, and one Starter sale
($249) covers about six months of lean running costs. Content income (ads, affiliates, products) is
slower and much more uncertain, and most faceless channels never reach the YouTube Partner Program.

---

## 2. Upfront costs (one-time)

| Item | Lean | Comfortable | Notes |
|---|---|---|---|
| Domain name | $10–15/yr | $10–15/yr | For the link page, `/go/` tracked links, webhooks, and email SPF/DKIM. |
| Anthropic API credit | $5–10 | $20–25 | Prepaid; the factory writes placeholder drafts without it. |
| First month of voice | $0 (Piper, free) | $5–22 | ElevenLabs Starter or Creator. Clone your own voice only. |
| First month of VPS | $5 | $10 | Any Docker VPS; Caddy or a Cloudflare Tunnel in front for HTTPS. |
| Mailing address for CAN-SPAM | $0 if you use an address you already have | $10–15 | Virtual mailbox or PO box. Every outreach email and newsletter needs one. |
| USB microphone (only for recording your voice clone samples) | $0 (phone in a quiet room) | $50–100 | Optional. |
| Paid ad test | $0 | $50–200 | Optional. I'd keep this at $0 until a post proves itself organically, then boost that one. |
| LLC / business registration | $0 (sole proprietor) | $50–500 by state | Optional. Ask a local accountant; not needed to start. |
| Accounts: Stripe, Gumroad, Meta, YouTube, TikTok developer apps, Impact/CJ affiliate networks | $0 | $0 | All free to open. |
| **Total** | **≈ $40–60** | **≈ $200–400** | The comfortable column is mostly optional items. |

---

## 3. Monthly running costs

### What the content uses

At the brand cadence that's about 20 Shorts, 4 long videos, 12 carousels and 4 newsletters a month,
plus ad studio scripts and pitch drafts.

**Writing (Anthropic API).** Claude Opus 5.5 is $4 per million input tokens and $20 per million output
tokens. A script with research context and thinking runs roughly 5–10k input and 5–15k output tokens,
so about $0.10–0.35 each. 40–60 pieces a month plus ad studio work is about **$10–40/month**. Switching
bulk work (captions, hook variants) to Claude Sonnet 5.5 ($2/$10) would cut that roughly in half.

**Voice.** Shorts are about 900 characters of narration and a 10-minute long video is about 9,000, so
the channel needs roughly 55–60k characters a month. That fits ElevenLabs Creator (about $22/month,
100k characters) but not Starter (about $5, 30k). Piper is free and local but sounds flatter. Ad studio
clients add more characters; at 2+ retainers expect the next tier up (about $99).

| Item | Lean | Standard | At scale (ad studio busy, list growing) |
|---|---|---|---|
| Anthropic API | $10–20 | $20–40 | $50–100 |
| Voice | $0 (Piper) – $5 | $22 | $99 |
| VPS (dashboard, link page, media, webhooks) | $5–6 | $10–12 | $20–40 |
| Domain (amortized) | $1 | $1 | $1 |
| Transactional email (Resend / Postmark / SES) | $0 (free tiers) | $0–15 | $20 |
| Newsletter (if you move to Beehiiv / ConvertKit) | $0 (free under ~2,500 subs) | $0 | $40–60 |
| Mailing address | $0–10 | $10–15 | $10–15 |
| Images (built-in art is free; OpenAI / Replicate optional) | $0 | $0–10 | $10–30 |
| Music licence (YouTube Audio Library is free) | $0 | $0–17 | $17 |
| Scheduler (Postiz self-hosted) | $0 | $0 | $0 |
| AI presenter tool for ads (optional; the rate card allows voice over the client's own footage instead) | $0 | $0 | $30–90 |
| **Total** | **≈ $30–45** | **≈ $80–130** | **≈ $300–450** |

### Fees taken from each sale

| Where | Fee (verify on the platform) |
|---|---|
| Gumroad direct sale | 10% + $0.50, and Gumroad may add card processing (about 2.9% + $0.30) on top; check the current fee page. Sales via Gumroad Discover cost more (about 30%). A $12 template nets roughly $9.60–10.30. |
| Stripe invoice (ad studio) | 2.9% + $0.30 per card payment. A $249 Starter nets about $241; a $799 retainer about $775. |
| Affiliate networks (Impact, CJ) | Free to you; payouts usually monthly, net-30, $50 minimum. |
| YouTube | Creator keeps 55% of long-form ad revenue and 45% of Shorts pool revenue; the RPMs below are already after that cut. |

### Taxes

Put aside **25–30% of profit** for income and self-employment tax (US). Platforms will issue 1099s.
This isn't tax advice; an accountant is worth one hour once money starts coming in.

---

## 4. Revenue scenarios

All three assume you keep the cadence above for 12 months, the review gate stays on (quality over
volume), and you personally send the ad studio pitches. Numbers are **monthly, around month 12**.

### Assumptions by scenario

| Assumption | Conservative | Base | Pops off |
|---|---|---|---|
| YouTube Partner Program | Not reached by month 12 | Reached around month 8–10 | Reached by month 4–6 |
| Long-form views per month | under 5k | 20k | 300k |
| Long-form RPM (finance, after YouTube's cut) | — | $13–16 | $16–22 |
| Shorts views per month (all platforms) | 50k | 300k | 5M |
| Shorts RPM | — | $0.04–0.08 | $0.06–0.12 |
| Link-in-bio / tracked-link clicks per month | 100 | 800 | 8,000 |
| Affiliate conversion (click → approved lead or funded account) | 2% | 2.5% | 3% |
| Average affiliate payout | $30 | $50 | $70 |
| Product sales per month (net ≈ $10–20 each) | 5 | 40 | 300 |
| Ad studio clients | 0–1 Starter a month | 2 retainers + 2 one-off packages | 8 retainers + 4 one-off packages |
| Sponsorships | none | none | 1–3 integrations at $1,000–2,000 |

Where these come from:
- **RPMs**: research PR #1 cites finance long-form at $13–26 and Shorts at $0.04–0.32. I used the
  lower part of both ranges, because new channels and international viewers pull RPM down.
- **Affiliate payouts**: SoFi lists $100–150 per lead, Empower about $115, Acorns about $10, M1 $46–56,
  Robinhood $5–20 (research PR #1). A mix of easy low-payout and hard high-payout offers lands at
  $30–70. Some programs cap annual payouts (SoFi's directory lists $10k/yr).
- **Ad studio**: 76 pitches are drafted. Cold outreach to small brands typically gets 1–5% replies and
  maybe a quarter of replies buy. That's roughly 1–4 clients per 100 pitches, which is why steady
  outreach matters more than any other number here. Your hours are the ceiling: at 8 retainers
  (96 ads a month) you'd be doing this full-time.

### Monthly revenue at month 12

| Stream | Conservative | Base | Pops off |
|---|---|---|---|
| YouTube long-form ads | $0 | $260–320 | $4,800–6,600 |
| Shorts ads (YouTube) | $0 | $12–24 | $300–600 |
| Instagram / TikTok creator payouts | $0 | $0–100 | $500–1,500 |
| Affiliates | $30–90 | $700–1,200 | $10,000–17,000 |
| Digital products | $50 | $400–600 | $4,000–6,000 |
| AI ad studio (after Stripe fees) | $0–250 | $2,000–2,400 | $7,000–8,000 |
| Sponsorships | $0 | $0 | $1,000–6,000 |
| **Total (gross)** | **$80–400** | **$3,400–4,600** | **$27,000–46,000** |
| Minus running costs | ≈ $40 | ≈ $110 | ≈ $400 |
| **Before tax** | **≈ $40–360** | **≈ $3,300–4,500** | **≈ $27,000–45,000** |

Rounded in the summary to $0–500, $2,000–5,000 and $20,000–45,000 to leave room for things going
somewhat worse than the assumptions.

### First-year total

Income ramps, it doesn't start at the month-12 rate. If it grows steadily, year one is about 5–6× the
month-12 figure, or about 3–4× if it takes off late:

| | Conservative | Base | Pops off |
|---|---|---|---|
| Year-one revenue | **$500–3,000** | **$12,000–25,000** | **$80,000–200,000** |
| Year-one costs (lean → standard) | ≈ $400–600 | ≈ $1,000–1,500 | ≈ $2,500–4,000 |

---

## 5. What moves the numbers most

1. **Ad studio outreach volume.** It's the only stream that doesn't depend on an algorithm. Sending
   15–20 pitches a week is worth more than any other single habit.
2. **Long-form video.** One long finance video at $15 RPM earns what roughly 200 Shorts at $0.07 do.
   From **Feb 1, 2027** new YouTube Partner applicants need 8,000 watch hours (or 20M Shorts views), up
   from 4,000, so long-form matters for getting monetized at all.
3. **Real affiliate links.** The HYSA link in `brands/money-made-simple.yaml` is still a placeholder,
   so affiliate income is $0 until Impact/CJ approve you and the links are added.
4. **Email list.** Product and affiliate sales convert several times better from the newsletter than
   from a caption. The list is the asset that survives an algorithm change.

## 6. What could make it worse

- **Platform policy.** YouTube, Meta and Instagram de-monetize mass-produced or reposted content. The
  human review gate and original scripts are what keep the channel eligible; skipping them to post more
  is the fastest way to the conservative column.
- **Finance compliance.** Brokerage and adviser offers (Robinhood, M1, Betterment) need careful wording
  (FINRA 2210 / SEC Marketing Rule); a rejected or banned affiliate account removes that income.
- **Clawbacks and caps.** Some affiliate leads reverse within 30–120 days, and some programs cap yearly
  payouts.
- **Seasonality.** Ad RPMs are highest in Q4 and drop sharply in January. Tax affiliates (FreeTaxUSA,
  TaxAct) spike January to April.
- **Your time.** Every scenario assumes you review content and send outreach every week. The software
  removes most of the work, not all of it.

## 7. Recommendation

Start lean (≈ $50 upfront, ≈ $40/month): Piper or ElevenLabs Starter, a $5 VPS, free email tiers, no
paid ads. Upgrade voice to ElevenLabs Creator the week the first ad studio client pays. Revisit this
model at month 3 with real numbers from `factory report` and replace the assumptions with actuals.
