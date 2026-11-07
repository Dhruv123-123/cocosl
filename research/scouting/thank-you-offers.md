# Thank-you page offers and paid newsletter recommendations

Researched 2026-11-07. **Docs only. Nothing has been signed up for, changed or spent.** Sources are the
Kit, SparkLoop and beehiiv help and pricing pages (linked). Where a page didn't say something, this doc
says so instead of guessing. The thank-you pages themselves are already built on each brand's branch;
this doc picks the offer and writes the copy for the site threads to drop in.

## TL;DR

1. **Correction to `newsletter.md`: Kit's free plan can't earn paid recommendations.** Kit's pricing page
   lists paid recommendations on Creator ($33/mo at 1,000 subscribers) and Pro only, with a 23.5% fee.
   Free recommendations (unpaid swaps) are on every plan. So "paid recommendations from day one on the free
   plan" was wrong. `newsletter.md` is fixed in this round.
2. **There's a $0 route that does pay: SparkLoop's Partner Network.** It's free to join, pays $2-7 per
   confirmed subscriber for most newsletters (up to $20), and you place it yourself with partner links:
   on our own thank-you page, in an email, or on social. It doesn't depend on the Kit plan. SparkLoop
   suggests waiting until a list has **500-1,000 subscribers**, and wants a mostly English-speaking audience
   in North America or Western Europe, so **Dinero Simple likely won't qualify**.
3. **beehiiv's paid recommendations need a paid beehiiv plan** plus Stripe identity checks. Not relevant
   while we're on Kit; it's part of the open "move at 5k?" question.
4. **The thank-you page is the better first earner.** All four sites already have a `/free/thanks/` page
   showing products. The change is: one offer instead of a grid, the download always first, and a short
   honest pitch. Copy for all four brands is in section 4.
5. **Kit Free can't run the welcome sequence.** Kit's Free-plan help article (23 Sep 2026) says sequences
   and visual automations need a paid plan. `newsletter.md` now compares free tools that can, and recommends
   Sender. Switching is Dhruv's call.

## 1. Paid recommendations: the three networks

| | Kit Creator Network | SparkLoop Partner Network | beehiiv paid recommendations |
|---|---|---|---|
| **What it is** | Up to 5 newsletters shown to a new subscriber right after they sign up on a Kit form or landing page | You join other newsletters' partner programs and send readers to them with tracked partner links | Recommend publications from beehiiv's marketplace and get each one's set price per verified subscriber |
| **Plan needed** | Free recommendations: all plans. **Paid: Creator or Pro only** ([Kit pricing](https://kit.com/pricing)) | Free to join, no fixed fee ([SparkLoop](https://sparkloop.app/partner-network)) | **A paid beehiiv plan** ([beehiiv](https://www.beehiiv.com/support/article/41831000051735)) |
| **Minimum list size** | None stated. You must recommend at least one creator yourself (unpaid) before others can recommend you ([Kit help](https://help.convertkit.com/en/articles/7240475-what-is-the-creator-network)) | No hard minimum, but "we recommend waiting until you have at least 500-1000 subscribers" | None stated |
| **Pay per subscriber** | Set by the newsletter paying; Kit's earlier copy said "$1 to $4+" | "Typically **$2-7** per confirmed referral" ([pricing guide](https://help.sparkloop.app/en/articles/9184574-the-ultimate-guide-to-sparkloop-pricing)); the network page says $2-20 | Each offer's set CPA; one finance example paid $3.20 ([EarnifyHub](https://earnifyhub.com/blog/beehiiv-boosts-vs-sparkloop), a single example) |
| **Fee** | 23.5% of earnings (Kit pricing) | 20% plus 3.5% | Not stated in the help article |
| **When it counts** | Not stated on Kit's page; it runs on SparkLoop, see next column | After a **7-14 day screening period**; anyone who unsubscribes in it doesn't count ([quality guide](https://help.sparkloop.app/en/articles/7005560-partner-program-subscriber-quality-guide)) | Once verified; shown as "Subscribers in verification" until then |
| **Payout** | Monthly, through SparkLoop and Stripe | Monthly ("on time, every single month"); no minimum stated | To your beehiiv Wallet, then the bank via Stripe Express |
| **Audience rules** | Not stated | Majority English-speaking, in North America or Western Europe. Fraud gets every referral rejected, confirmed ones included, and a permanent ban | Some offers only pay for certain countries |

Kit tags anyone who joins through a recommendation with the form "Creator Network", so those readers can
be segmented. If SparkLoop's Upscribe widget is used on a form, Kit says to hide it there before joining,
because the Creator Network replaces it.

### What a subscriber earns us from recommendations

Unchanged from `newsletter.md`: **about $0.30-0.70 per new subscriber**, from $2-3 per referral, 20-30% of
new readers picking one, about 76% kept after fees and about 80% passing screening. Treat it as a planning
number until the dashboard shows real ones.

### When a Kit upgrade pays for itself

Kit Creator costs $33/mo at 1,000 subscribers. At $0.30-0.70 a new subscriber, paid recommendations alone
cover it at **roughly 50-110 new subscribers a month per list**. Below that, use SparkLoop partner links
(free) and free Creator Network swaps. Above it, the upgrade is worth asking Dhruv about. It's spending, so
it's his call under the organic-only rule.

## 2. Setup, step by step

### A. Free Creator Network swaps (Kit, any plan, day 1)

1. In Kit, open the Creator Network settings (under Grow). Fill in the profile: who it's for, the niche,
   how often it sends.
2. Recommend at least one newsletter (it has to be an unpaid one). Use the swap list in `newsletter.md`,
   e.g. Safe Not Scammed for Scam Decoded, which is also on Kit.
3. Pick the form the recommendations show on (each brand's main sign-up form) and leave
   recommendations on.
4. Ask each one you recommend to recommend you back.

Section A only applies if we stay on Kit. On Sender, skip it: SparkLoop partner links (B) work with any tool.

**Also check the redirect:** our sites already post to Kit and then send people to `/free/thanks/`.
If turning on Creator Network recommendations makes Kit show its own recommendation screen instead of our
redirect, choose which one wins. Our thank-you page (the download plus the offer) should win. Put the
recommendations in the day-1 email instead. *Not verified: Kit's pages don't say how the two interact.*

### B. SparkLoop Partner Network (free; join a list once it reaches about 500)

1. Apply at [sparkloop.app/partner-network](https://sparkloop.app/partner-network). SparkLoop pre-approves
   within about 24 hours.
2. Follow the email to set a password and connect payout details (Stripe).
3. In the partner dashboard, open each newsletter's program. Each one shows its pay per subscriber before
   you join. Join only those that pass our own rule: one we'd send a friend to, and nothing selling trading
   signals, "get rich" schemes or anything our guardrails ban.
4. Copy each program's **partner link**. SparkLoop requires its links to be used, so don't type a plain URL.
5. Put up to 3 links in the "Readers also like" box on the thank-you page (copy below), and mention one in
   the day-3 email.
6. Check the dashboard weekly. Drop any program whose subscribers fail screening often, since that suggests
   the fit is wrong.

### C. Kit paid recommendations (only after an upgrade to Creator)

1. Upgrade the list to Creator.
2. In the Creator Network settings, turn on paid recommendations. Connect SparkLoop and Stripe.
3. Wait for approval, usually within a day.
4. Add paid partners using the same check as B3.

### D. beehiiv paid recommendations (only if a list moves to beehiiv)

1. Upgrade to a paid plan (Lite or above).
2. Complete Stripe Identity Verification and link a bank account through Stripe Express.
3. Open **Paid recommendations > Marketplace** and join the Recommendation Network if asked.
4. Search, filter, and click Recommend or Apply on each publication's card.
5. Track earnings under **Outgoing recommendations**.

## 3. The thank-you page offer: how it works and the rules we keep

**The flow:** someone signs up on the site, our form posts to Kit and lands them on `/free/thanks/`. There
they get the free download, one paid offer, and a "Readers also like" box. Kit sends the first email with
the same download link.

**Where it already exists:** all four thank-you pages are built.
- Money Made Simple: `site/build.py`, the `/free/thanks/` block, currently a 2-product grid.
- Scam Decoded: `sites/scam-decoded/content/pages/thanks.md`, which already offers the $9 kit.
- 1099 Money: `apps/freelance-tax/free/thanks/`, which loops the tracker and the upsells from `config.js`.
- Dinero Simple: `sites/dinero-simple`, the `/free/thanks/` page, currently a 2-product grid.

The changes are copy and layout, for the site threads to make.

**The rules** (they follow our guardrails, and none of them are optional):
1. **The free download comes first and is never held back.** The download button sits above the offer,
   and there's no "wait, before you go" screen.
2. **One offer.** One product, so the choice is "yes or not now". Showing one is our judgement, not a
   measured result. A/B test it against the grid once there's traffic.
3. **The real price.** The price is what the product always costs: no countdowns, no "only today", no
   crossed-out price nobody ever paid. A new-subscriber discount is fine only as a code that never expires,
   and that's skipped for now to keep it simple.
4. **An easy no.** A plain "No thanks, take me to the blog" link, as visible as the buy button.
5. **No income or results claims,** and no "guaranteed". Say what's in the product and how long it takes.
6. **The refund line,** using the same days Gumroad is set to.
7. **Disclose paid recommendations.** If any link in "Readers also like" pays us, the box says so.
8. **Tracking:** add a Plausible event on the offer button (`Thanks+Offer+Click`) so the dashboard can show
   the take rate, which today is only an assumption of 5-10%.

**Which product goes on the page:** the cheapest useful next step after the freebie, and **not** the
product the day-7 email pitches, so the sequence isn't repeating the page. Where the day-7 pitch is the
same product (Scam Decoded and 1099 Money each have one main product), the thank-you page is a soft first
mention, and day 7 is the full case.

| Brand | Freebie | Thank-you offer | Net per sale | Why |
|---|---|---|---|---|
| Money Made Simple | The 7-Day Money Reset | **Bill Cut Kit, $5** | $3.56 | Day 1 of the reset is "find your real number"; cutting bills is the obvious next move. $5 is an easy yes, and the $12 budget stays for day 7 |
| Scam Decoded | The Scam-Proof Checklist | **Family Scam-Proofing Kit, $9** | $7.04 | Already on the page; tighten the copy and add the easy no |
| 1099 Money | 2027 Freelancer Tax Calendar | **Quarterly Tax Tracker** (price from `config.js`, $15 or the $9 launch price) | $12.26 at $15 | The calendar says *when* to pay, and the tracker says *how much*. Show only the tracker, not the upsells, so checkout is the only place the $49 bundle appears |
| Dinero Simple | Tu dinero en orden en 7 días | **El Kit para Recortar Gastos, $5** | $3.56 | Same logic as MMS, in Spanish |

1099 Money's "$9 launch" price is fine on the thank-you page only if it's the price everyone pays
everywhere at that moment. When the launch ends, the page has to change with it. `config.js` drives both,
so they stay in sync.

## 4. The copy

Placeholders in `{braces}` come from each site's config, so a price change updates every page.

### Money Made Simple (`/free/thanks/`)

> **You're in. Here's your reset.**
> Your download is below. Your first email is on its way too (check Promotions or Spam if you don't see it in a few minutes).
>
> **[Download The 7-Day Money Reset (PDF)]**
>
> Start with Day 1 today. It takes about 15 minutes, and you'll need your banking app.
>
> ---
>
> **Optional: the next step after Day 1**
>
> **Bill Cut Kit · {price}**
> Day 1 shows you where the money goes. This kit helps you pay less every month: a 10-minute
> scan for repeat charges, a cancel-or-keep list, and word-for-word scripts to
> lower the bills you keep. {pages}-page guide plus a tracking sheet. Instant download, {refund_days}-day refund.
>
> **[Get the Bill Cut Kit]**  ·  [No thanks, take me to the blog](/blog/)

### Scam Decoded (`/free/thanks/`, replaces the current product block)

> **Here's your checklist**
> {thanks_note}
>
> **[Download The Scam-Proof Checklist]**
>
> Start with section 1 tonight. It takes about 10 minutes and costs nothing.
>
> ---
>
> **Optional: put the whole family on the same page**
>
> **{kit_name} · {kit_price}**
> The checklist protects you. The kit is for everyone else at the kitchen table: a scripted family
> meeting, freeze trackers for every family member, the 12-scam decoder, a fridge card and wallet
> cards for parents. {kit_pages} printable pages. Instant download, {kit_refund_days}-day refund.
>
> **[See what's inside]**  ·  [No thanks, show me this week's scams](/alerts/)

*Check: the link `/alerts/` stands in for wherever the site lists recent scams; use the real path.*

### 1099 Money (`free/thanks/`)

> **You're in. Here's your calendar.**
> It's also on its way to your inbox. Print page 5 and put it where you'll see it.
>
> **[Download the PDF]**
>
> **Do this now (2 minutes)**
> 1. Add the bold dates on page 2 to your phone calendar, with a reminder one week before.
> 2. Run your numbers in the free quarterly tax calculator so you know what Jan 15 should be.
> 3. Open a separate savings account for tax money if you don't have one.
>
> ---
>
> **Optional: know the amount, not just the date**
>
> **{product.name} · {product.price}**
> The calendar tells you when each payment is due. The tracker tells you how much: log each payment
> you get, and it sets aside a percentage, totals the quarter, and shows what to send by the next deadline.
> Sheets and Excel, works for any 1099 work. Instant download, 14-day refund.
>
> **[Get the tracker]**  ·  [No thanks, open the calculator](/)
>
> <small>Educational content, not tax, legal or financial advice.</small>

*Check: the tracker description must match what the product really does. Edit the second sentence to its
real features before publishing.*

### Dinero Simple (`/free/thanks/`)

**Needs a review by a native Spanish speaker before it goes live.** It's written in neutral US-Latino
Spanish (tú) to match the site.

> **Ya estás dentro. Aquí está tu guía.**
> Tu descarga está abajo. Tu primer correo ya va en camino (si en unos minutos no lo ves, revisa Promociones o Spam).
>
> **[Descarga Tu dinero en orden en 7 días (PDF)]**
>
> Empieza hoy con el Día 1. Toma unos 15 minutos y vas a necesitar la app de tu banco.
>
> ---
>
> **Opcional: el siguiente paso después del Día 1**
>
> **El Kit para Recortar Gastos · {price}**
> El Día 1 te muestra a dónde se va tu dinero. Este kit te ayuda a pagar menos por las cuentas que te
> quedas: encuentra cada cobro que se repite en 10 minutos, cancela lo que no usas y baja las cuentas que te
> quedas con guiones palabra por palabra. Guía de 9 páginas + hoja de control.
> Descarga inmediata, reembolso en {refund_days} días.
>
> **[Quiero el kit]**  ·  [No, gracias, llévame a los artículos](/blog/)

### "Readers also like" box (all brands, under the offer)

Start it with free swap partners. Add SparkLoop partner links once the list reaches about 500 and is approved.

> **Newsletters our readers also like**
> - **{Name}**: {one honest line on what it covers and how often}. [Subscribe]({partner_link})
> - **{Name}**: {one line}. [Subscribe]({partner_link})
>
> <small>We only list newsletters we read. Some of these links pay us a small fee if you subscribe, at no
> cost to you.</small>

Spanish: **Boletines que también leen nuestros lectores** … <small>Solo recomendamos boletines que leemos.
Algunos de estos enlaces nos pagan una pequeña comisión si te suscribes, sin costo para ti.</small> (Dinero
Simple's box stays free swaps only unless SparkLoop approves a Spanish-language list.)

### Day-1 email line (all brands)

One line under the download link in the first email, not a second pitch:

> P.S. If you finish Day 1 and want the next step, the {offer name} ({price}) is here: {link}. If not,
> no problem: the next email is free and so is everything in it.

## 5. What it's worth

Using the take-rate assumption from `paid-acquisition.md` (5-10% buy a small offer right after signing
up), per 100 new subscribers:

| Brand | Offer net | 5 sales | 10 sales |
|---|---|---|---|
| Money Made Simple / Dinero Simple | $3.56 | $17.80 | $35.60 |
| Scam Decoded | $7.04 | $35.20 | $70.40 |
| 1099 Money | $12.26 at $15 | $61.30 | $122.60 |

That's $0.18-1.23 per subscriber from the page alone, before recommendations. The take rate is the number to
measure first: the Plausible event in section 3 gives it within the first few hundred sign-ups.

## Open questions for Dhruv

1. **Email tool:** stay on Kit (Creator, $33/mo per brand, for the sequences) or switch to Sender Free? See
   `newsletter.md`.
2. **Kit Creator upgrade:** OK to revisit at about 100 new subscribers a month on one list, or stay
   SparkLoop links only until you say otherwise?
