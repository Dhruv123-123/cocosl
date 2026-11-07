# Newsletter tool at $0: Kit vs Sender vs beehiiv for our five lists, and one recommendation

Written 2026-11-07, as a decision page for Dhruv. **Docs only.** It updates the comparison in
`newsletter.md` with three facts checked today: Sender's one-account rule, beehiiv's one-publication
limit, and Kit Free's automation limit. The five lists are Money Made Simple, Scam Decoded, 1099 Money,
Dinero Simple (Spanish), and a fifth (Tiny Histories or the B2B sample list). The fifth is the least urgent.

## The recommendation

**Use Sender Free Forever, in one account, with one group and one sender identity per brand.** Split into
separate accounts only after Sender support confirms in writing that separate brands are allowed.

Why:

1. **It's the only $0 plan that runs our welcome sequences.** Sender Free has **unlimited automation
   workflows**. Kit Free allows **one basic automation (one trigger, one action), and multi-email sequences
   are locked**. beehiiv Free doesn't publish an automation allowance we could confirm. Every brand's funnel
   depends on a 5-10 email welcome sequence with a day-7 product pitch.
2. **One account is what Sender's terms safely allow.** Terms 4.2: "You are only allowed to have one
   Sender account sending the same or similar content." Four finance brands, including a Spanish sister
   of Money Made Simple, could be read as "similar". One account avoids that question. Groups and sender
   identities keep each brand's emails, names and unsubscribes separate.
3. **The shared cap is fine for months 1-3.** Sender Free covers **2,500 active subscribers and 15,000
   emails a month** across the account. If you store more than 2,500, campaigns stop. Our revenue model's
   base case doesn't put all lists together near 2,000 until well into 2027. Two weekly issues for 2,000
   people, plus welcomes, fit in 15,000.
4. **Spanish works.** Sender's template setting switches the unsubscribe and browser links to Spanish
   (`newsletter.md`), and `factory newsletter --for sender` already exports drafts for it (on `main`).

## The three options at $0

| | **Sender Free Forever** | **Kit Free (Newsletter)** | **beehiiv Free** |
|---|---|---|---|
| Subscribers | 2,500 per account (stop sending above it) | **10,000 per account** | 2,500 |
| Emails | 15,000 a month | Unlimited broadcasts | Not stated |
| Welcome sequences | **Unlimited automations** | **No** (1 single-step automation; sequences need Creator, $33-39 a month) | Not confirmed on the free plan |
| Several brands | One account "sending the same or similar content" (terms 4.2), so use groups | Not addressed on the pages read; one account per brand is common practice | **1 publication per Free account** (Lite 3, Pro 10) |
| Branding | Sender logo on emails and forms | "Powered by Kit" badge | beehiiv branding |
| Spanish | Unsubscribe and browser links in Spanish | Form and email text editable | Not checked |
| Own domain (SPF/DKIM) | Yes | Yes | Yes |
| Earning on $0 | SparkLoop partner links | SparkLoop partner links. Kit Ads exist (Kit keeps 23.5%) | Ad Network and Boosts need a paid plan |
| Works with our site today | Needs the `sender` form route (`newsletter.md`) | Yes | No |

## When to change the plan

| Trigger | Do |
|---|---|
| Sender support says yes to one account per brand | Split each brand into its own Sender account (each gets 2,500 and 15,000) |
| Total subscribers near **2,000** | Either Sender Standard (from about $9 a month at 500 subscribers, more at higher tiers), or move the largest list to **Kit Free** for broadcasts (10,000 cap). On Kit, the welcome runs from the factory's own sequence engine (SMTP, `worker.py`) |
| One list passes the paid-ads gate (`paid-acquisition.md`) or 5,000 subscribers | Compare Sender Standard, Kit Creator and beehiiv Lite on that day's prices. beehiiv only if its Ad Network would earn more than the plan costs (`newsletter-sponsorship-benchmarks.md`) |

## Before signing up (5 minutes)

1. Email Sender support: "I run four separate newsletters under different brand names, with different
   topics and audiences (budgeting, scam awareness, freelancer taxes, and Spanish-language finance). May I
   use one Free account per brand?" Keep the reply.
2. Create one account with `hello@<main domain>`. Add one group and one sender identity per brand, and
   authenticate each brand's domain.

## Sources

[Sender Free Forever limits](https://www.sender.net/help/account-settings-and-billing/free-forever-plan-limits),
[Sender terms of service, 4.2](https://www.sender.net/terms-of-service/),
[beehiiv: adding multiple publications](https://www.beehiiv.com/support/article/14492955390871),
[PassiveKit: Kit Free limits, verified Jul 2026](https://www.passivekit.com/kit-free-plan-limits/), and
`newsletter.md` for Kit's Sep 2026 change and Spanish support. All read 2026-11-07.
