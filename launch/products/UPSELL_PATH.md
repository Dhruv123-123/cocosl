# Money Made Simple: product ladder and upsell path

Six products, one path. Every product ends with a "next step" page that sells the next rung, every
thank-you email repeats it with a $5-off code, and the bundle sits at the top as the anchor.

## The ladder

| Rung | Product | Price | Who it's for | Next step it sells |
|---|---|---|---|---|
| Free | Free reset / lead magnet (link-in-bio page, email list) | $0 | Followers | The Bill Cut Kit (thank-you page + email 2) |
| 1. Tripwire | **The Bill Cut Kit** | $5 | Anyone who feels broke | The 20-Minute Budget, code `BILLCUT5` ($5 off, so the kit pays for itself) |
| 2. Core | **The 20-Minute Budget** (existing) | $12 | Wants a system | Debt-Free Date Planner (`BUDGET5`) or the investing kit |
| 2b. Entry | **The Credit Report Audit Kit** | $9 | Credit-score viewers, about to apply for credit | Debt-Free Date Planner (`AUDIT5`) |
| 3a. Core | **The Debt-Free Date Planner** | $17 | Has debt | Start Investing (`DEBTFREE5`) |
| 3b. Core | **Start Investing With $100 a Month** | $19 | Debt handled, has a cushion | 20-Minute Budget (`INVEST5`) or the bundle |
| Top | **The Money Made Simple Toolkit** (bundle) | $39 | Wants everything | (end of ladder) |

Separately the five kits cost $62; the bundle is $39 (saves $23, about 37%).

```
 Free reset ──> Bill Cut Kit $5 ──> 20-Minute Budget $12 ──┬──> Debt-Free Date Planner $17 ──> Start Investing $19
                                                           │                                         │
 Credit content ──> Credit Report Audit Kit $9 ────────────┘                                         │
                                                                                                     v
                    every product page and checkout ─────────────────────────────────────> Toolkit bundle $39
```

## Which content feeds which product

| Content in the launch pack | Point the CTA at |
|---|---|
| Videos 01, 02, 10, 11, 14; carousels 15, 21 (budgeting, subscriptions, bills) | Bill Cut Kit ($5) or 20-Minute Budget |
| Videos 06, 07, 13; carousel 19 (credit) | Credit Report Audit Kit |
| Video 08; carousel 20 (avalanche vs snowball); carousel 16 (emergency fund) | Debt-Free Date Planner |
| Videos 03, 04, 05, 09, 12, 23; carousels 17, 18, 22 (investing) | Start Investing With $100 a Month |
| Video 24 (30-day reset) | The bundle (its Start Here map is a 30-day plan) |

## Discount codes to create (Gumroad: Checkout > Discounts)

Restrict each code to the one product named, unlimited uses, no expiry. These are printed inside the PDFs, so
create them **before** the first sale.

| Code | Amount | Valid on | Printed in |
|---|---|---|---|
| `BILLCUT5` | $5 off | The 20-Minute Budget | Bill Cut Kit, page 9 + thank-you email |
| `BUDGET5` | $5 off | The Debt-Free Date Planner | Debt Planner listing + 20-Minute Budget thank-you email (add it) |
| `AUDIT5` | $5 off | The Debt-Free Date Planner | Credit Audit Kit, page 12 + email |
| `DEBTFREE5` | $5 off | Start Investing With $100 a Month | Debt Planner, page 10 + email |
| `INVEST5` | $5 off | The 20-Minute Budget | Investing kit, page 12 + email |
| `LAUNCH` | see each LISTING.md | Each product during its first 7 days only | Social posts |

**Bundle upgrade promise.** The investing kit and the bundle page say: "Already bought one? Email your receipt and
we'll send a code for the difference." When someone emails, create a single-use code on the bundle worth what they
paid (e.g. $17 off) and reply with it. Honour it every time.

## Gumroad setup, in order

1. Create the five products from each folder's `LISTING.md` (title, description, price, tags, thank-you message,
   cover). Upload the `.zip` from each product folder as the content.
2. Create the discount codes above.
3. **Upsells at checkout** (Gumroad: Checkout > Upsells). Add:
   - On the Bill Cut Kit: offer The 20-Minute Budget at $9 ("add the budget system for $9").
   - On The 20-Minute Budget: offer the Debt-Free Date Planner at $12.
   - On the Debt Planner and the investing kit: offer the bundle, discounted by the price of the product in the cart.
   - Keep it to one upsell per product. More than one at checkout costs more sales than it adds.
4. **Bundle:** either upload the bundle zip as its own product (simplest), or use Gumroad's Bundle product type
   with the five products inside (buyers then get updates to each).
5. **Workflows** (Gumroad: Workflows, or your email tool via the webhook in `integrations/`): one email 3 days
   after purchase of each product. Drafts are below.
6. Replace `[your store link]` in each guide's last page (`launch/products/<slug>/guide.html`) with your real
   store URL, then rebuild with `python launch/products/build.py --check` and re-upload the zips. Replace the
   `example.gumroad.com` URLs in `site/content/products/*.md` and `brands/money-made-simple.yaml`, and delete the
   `status: coming-soon` line from each product page once it's live.

## Post-purchase emails (3 days after purchase)

Send from your own address. Plain text. One link. No fake urgency.

**After The Bill Cut Kit**
> Subject: How much did you find?
>
> Hi [first name], quick check-in: did you get through the audit? Most people find at least one charge they'd
> forgotten. Reply with your yearly total if you like; I read every reply.
>
> The next step is giving that money a job so it doesn't quietly disappear. That's what The 20-Minute Budget does:
> bills and savings on autopilot, and one weekly spending number. Your code BILLCUT5 takes $5 off, so the kit pays
> for itself: [link]

**After The 20-Minute Budget** (add to its existing workflow)
> Subject: Your weekly number, and what's next
>
> Hi [first name], how did your first 20-minute check-in go? If you've got debts, the next move is putting a date
> on them. The Debt-Free Date Planner handles up to 10 debts, avalanche or snowball, and tells you whether a
> balance transfer would actually save money. BUDGET5 takes $5 off: [link]

**After The Credit Report Audit Kit**
> Subject: Did your disputes go out?
>
> Hi [first name], if you sent disputes, the bureaus generally have about 30 days to answer. The tracker's
> Disputes tab shows each due date. While you wait: lowering card balances is the other big lever. The Debt-Free
> Date Planner turns them into a dated plan. AUDIT5 takes $5 off: [link]

**After The Debt-Free Date Planner**
> Subject: What's your date?
>
> Hi [first name], what debt-free date did the planner give you? Write it somewhere you'll see it. When that day
> comes, keep the payment going, to yourself. Start Investing With $100 a Month shows exactly where to put it.
> DEBTFREE5 takes $5 off: [link]

**After Start Investing With $100 a Month**
> Subject: Did the money get invested?
>
> Hi [first name], one common snag: money moved into an IRA sits as cash until you buy a fund (guide, chapter 6,
> step 3). Worth a 30-second check. If you want the rest of the system, the full toolkit has the budget, debt,
> credit and bill kits too, and if you email me your receipt I'll send a code for what you've already paid: [link]

**After the bundle**
> Subject: Start with week 1
>
> Hi [first name], open Start-Here-Toolkit-Map.pdf first; week 1 is the Bill Cut Kit, about an hour. Reply if
> anything's unclear or broken.

## Rules that keep this honest (and keep the accounts safe)

- Only say "launch price" while it's true; end it on time. No fake countdowns, no "only 3 left".
- No testimonials or results until real buyers give them, quoted with permission. No income or score promises.
- Every growth figure says "assumed return, not guaranteed". Every product says "educational, not advice".
- 14-day no-questions refund on everything. On $5 to $39 products it costs little and removes hesitation.
