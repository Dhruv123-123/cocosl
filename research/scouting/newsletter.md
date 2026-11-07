# Newsletter platform: beehiiv vs Kit vs MailerLite, setup, and swap partners

Researched 2026-11-07 from the platforms' own help pages and pricing write-ups (sources are linked next to
each figure). Prices change often, and beehiiv changed its plans on 1 Oct 2026, so **check each pricing
page on the day you sign up**. Anything marked *unverified* couldn't be confirmed from a source this round.

## Our four newsletters and what they already have

| Newsletter | Lead magnet | Welcome sequence (already written) | Weekly issue | Where it lives |
|---|---|---|---|---|
| **Money Made Simple** | The 7-Day Money Reset (PDF) | 10 emails, days 0, 1, 3, 5, 7, 9, 12, 15, 18, 21. Pitch on day 7 (The 20-Minute Budget) | 7 issues written | `site/content/emails/`, `site/content/newsletter/` (PR #4); factory copy in `brands/sequences/money-made-simple.yaml` on main |
| **Scam Decoded** ("Scam Alert") | Scam-Proof Checklist | 7 emails, days 0, 1, 3, 5, 7, 10, 14. Pitch on day 7 (Family Scam-Proofing Kit, $9) | 6 issues, every Thursday from 4 Feb 2027 | `sites/scam-decoded/content/emails/` and `/newsletter/` |
| **1099 Money** | 2027 Freelancer Tax Calendar (form `tax-calendar`) | 7 emails, days 0, 2, 4, 6, 8, 11, 14, plus a 3-email **buyers** sequence | none yet | `apps/freelance-tax/emails/` |
| **Dinero Simple** (Spanish) | none yet | none yet | none yet | `brands/dinero-simple.yaml`, `launch/dinero-simple/` |

Every site form can already post to Kit, MailerLite or Buttondown by changing one setting
(`site.json` > `email.provider`, or `config.js` for 1099 Money). Nothing has to be rebuilt to switch.

## 1. Cost, ad network and paid recommendations

### Monthly cost per newsletter

| Subscribers | **Kit** | **beehiiv** | **MailerLite** |
|---|---|---|---|
| 0-250 | $0 (Newsletter plan) | $0 (Free) | $0 (Free: 250 subscribers, 2,500 emails/month) |
| 1,000 | $0, or Creator $39 | $0 | Comfort $19, Power $39 |
| 2,500 | $0 | $0 (Free plan's cap) | *between the 1k and 5k tiers* |
| 5,000 | $0, or Creator $89 | Lite: *unverified* (tier table is an image) | Comfort $49, Power $69 |
| 10,000 | $0, or Creator $139 | Lite $139 monthly / $119 billed yearly | Comfort $89, Power $129 |
| **All 4 at 10k** | **$0** (four free accounts) | **~$476-556** | **$356-516** |

Sources: Kit, [EmailVendorSelection, updated 9 Aug 2026](https://www.emailvendorselection.com/kit-pricing/)
(free plan up to 10,000 subscribers with 1 sequence and 1 visual automation; Creator adds unlimited);
beehiiv, [PPC Land on the 1 Oct 2026 change](https://ppc.land/beehiiv-faces-complaints-as-lite-plan-rises-30-at-10-000-subscribers/)
(Launch became Free up to 2,500, Scale became Lite, Max became Pro; existing customers move at renewals
from 1 Nov 2026) and [beehiiv's own pricing post](https://www.beehiiv.com/blog/beehiiv-pricing-2026);
MailerLite, [EmailVendorSelection](https://www.emailvendorselection.com/mailerlite-pricing/) (the free
plan is now 250 subscribers, much smaller than it used to be).

### Ways each one pays you

| | **Kit** | **beehiiv** | **MailerLite** |
|---|---|---|---|
| Free recommendations (swap with similar newsletters) | Creator Network | Free recommendations, all plans | none built in |
| Paid recommendations (another newsletter pays you per reader you send) | Creator Network paid recommendations, run by **SparkLoop** (Kit owns SparkLoop) | Paid recommendations (renamed from "Boosts" in Oct 2026), **paid plans only** | none built in; SparkLoop Upscribe may work with it (*unverified*) |
| Ad network | *Unverified this round* (Kit has a sponsor product; terms not confirmed) | beehiiv Ad Network, **paid plans only**, CPM per 1,000 unique opens or CPC; paid on the 20th for the prior month | none; third-party Paved connects by API key |
| Paid subscriptions | Yes | Yes, 0% fee from beehiiv | Yes, via Stripe |

Sources: [Kit help: paid recommendations](https://help.kit.com/en/articles/7973490-how-to-enable-paid-recommendations-in-the-creator-network);
[beehiiv: Boosts to paid recommendations, updated 20 Oct 2026](https://www.beehiiv.com/support/article/41790356251159);
[beehiiv Ad Network FAQ](https://www.beehiiv.com/support/article/17507491038231-ad-network-faq.md);
[SparkLoop Grow & Earn](https://sparkloop.app/grow-and-earn); [Paved + MailerLite](https://www.paved.com/help/articles/9579826-monetize-on-mailerlite-unlock-sponsorships-with-paved).

### Realistic money per subscriber

**Paid recommendations** are the first money a small list can make. They pay once, when a new subscriber
of ours also signs up to a newsletter we recommend on the thank-you page.

- **What the other newsletter pays:** "$1 to $4+" per referred subscriber
  ([Kit help](https://help.kit.com/en/articles/7973490-how-to-enable-paid-recommendations-in-the-creator-network)).
  Finance is near the top of that range. One write-up gives a 20k-subscriber finance newsletter paying
  $3.20 per subscriber on beehiiv and $2.10 on SparkLoop
  ([EarnifyHub](https://earnifyhub.com/blog/beehiiv-boosts-vs-sparkloop); a single example, not a benchmark).
- **Fees:** SparkLoop keeps 20% plus a 3.5% transaction fee (Kit help; SparkLoop says "20% commission plus a
  small processing fee", paid monthly). beehiiv's fee wasn't stated on its pages this round.
- **Verification:** referrals have to pass a quality check. beehiiv tags them "Rec: Pending Verification /
  Verified / Failed Verification", and failed ones don't pay.
- **Take rate:** beehiiv's own illustration assumes 30% of new subscribers pick a recommendation
  ([beehiiv](https://www.beehiiv.com/blog/how-much-money-can-you-make-from-1-000-newsletter-subscribers-in-2025)).
  That's optimistic for a cold list from short-form video.

**Our working estimate: $0.30-0.70 per new subscriber,** worked out as $2-3 per referral × 20-30% who pick
one × ~76% after fees × ~80% that pass verification. At 1,000 new subscribers a month across the four
brands, that's about **$300-700 a month**, earned once per subscriber. Scam Decoded and Dinero Simple
will sit at the low end: there are fewer paying partners in those niches.

**Ad network CPMs:** not confirmed this round. The beehiiv FAQ explains how payouts work (advertisers set a
CPM or CPC per offer) but gives no typical rates, and the third-party CPM pages didn't load before the
fetch limit. **Don't plan on ad income below about 5,000 engaged readers.** At 1,000 opens, even a
good CPM is tens of dollars per send. Our own products and affiliate links will earn more per reader
until then (the sequences already pitch the $9-15 products on day 7).

### Verdict

**Use Kit, with one free account per newsletter.**

1. **$0 up to 10,000 subscribers each.** beehiiv's free plan stops at 2,500, and its ad network and paid
   recommendations both need a paid plan. Four beehiiv Lite plans at 10k cost about $476-556 a month.
2. **Recommendations earn from about 500 subscribers, without a paid plan,** through SparkLoop's Partner
   Network partner links, which is the only network income a list under 5k realistically makes.
   *Correction (2026-11-07):* Kit's own paid recommendations need the Creator plan ($33/mo at 1k); Free
   gets unpaid swaps only. See `thank-you-offers.md`.
3. **The free plan's limit fits what we built** (*to confirm in the app: Kit's pricing page now marks sequences and automations as paid on Free; see `thank-you-offers.md`*). One sequence and one visual automation per account is
   exactly one welcome sequence plus the automation that routes people around it (below). 1099 Money's
   buyers sequence moves to Gumroad's own post-purchase emails, so it doesn't need a second sequence.
4. **The sites already support it:** `email.provider: kit` plus the form URL.

**Decision (2026-11-07): start on Kit.**

> **Open question for Dhruv:** should a newsletter move to beehiiv once it has about 5,000 engaged
> readers? That's roughly when beehiiv's ad network could earn more than the Lite plan costs (about $139
> a month at 10k). Kit exports CSVs and beehiiv imports them, so the move takes one afternoon either way.
> Until you decide, everything stays on Kit.
MailerLite only wins if you want a website builder too, and the sites already handle that.

## 2. Exact Kit setup (repeat once per newsletter)

Do Money Made Simple first. Each step takes minutes. Menu names are Kit's as of the sources above;
if a label has moved, Kit's search box finds it.

### A. Account and sending (once per brand)

1. Sign up at kit.com with the brand's own address (for example `hello@<brand domain>`), on the free
   **Newsletter** plan. Use one account per brand so each list, sender name and reputation stays separate.
2. **Settings > Email:** add the sending domain and add the DNS records Kit shows (SPF, DKIM) at your domain
   host. Add a DMARC record too if the domain doesn't have one (`v=DMARC1; p=none; rua=mailto:<you>`).
   Don't send from a Gmail address: it won't authenticate.
3. **Settings > Email > Address:** enter the business postal address (CAN-SPAM). This fills the footer
   that the sequence READMEs ask for. Same value as `BUSINESS_ADDRESS` in the factory's `.env`.
4. Sender name: `Money Made Simple` (or the brand). Reply-to: an inbox someone actually reads. Every
   welcome email asks for a reply.

### B. Form and double opt-in

5. **Grow > Landing pages & forms > New > Form > Inline.** Name it after the lead magnet
   (`mms-7-day-reset`, `scam-proof-checklist`, `tax-calendar`, `dinero-<magnet>`).
6. In the form's settings:
   - **Incentive email: on** (this is the double opt-in confirmation). Subject: "Confirm and get your
     checklist". Set the confirmation button to redirect to the site's thanks page
     (`/free/thanks/` on Money Made Simple).
   - **After subscribing:** redirect to the same thanks page, so people who are already confirmed land
     there too.
   - Don't attach the PDF here. Email 1 of the sequence delivers it, as written, so the PDF only goes
     to confirmed addresses.
7. Copy the form ID from the embed code and point the site at it:
   - Money Made Simple: `site.json` > `email.provider: "kit"`, `email.action:
     "https://app.kit.com/forms/<FORM_ID>/subscriptions"` (or the `EMAIL_PROVIDER` /
     `EMAIL_FORM_ACTION` variables on GitHub Pages). Rebuild and deploy.
   - Scam Decoded: the same keys in its site config.
   - 1099 Money: `config.js` > `email.provider = "kit"` with the same URL shape.
8. Test it with a real address: submit, confirm, check you land on the thanks page, and check the
   subscriber shows as **Confirmed** in Kit.

### C. Tags (free, unlimited)

9. Create these tags: `lead:<magnet>`, `in-welcome`, `buyer`, `src:instagram`, `src:tiktok`,
   `src:youtube`, `src:other`. If you want the platform tag set automatically, add a hidden form field
   named `fields[utm_source]` and fill it from the page's `utm_source` (the tagged links already carry
   it). That needs a matching custom field in Kit. *(Check this works on the free plan before relying on
   it. If not, Plausible already shows which platform sent each signup.)*

### D. The welcome sequence

10. **Send > Sequences > New sequence**, named `Welcome`. Add one email per file, in order, using each
    file's `subject` and `preheader`. Paste the built `email.txt` (plain text, links already absolute;
    build with the real site URL first), or the HTML from `email.html` if your plan's editor accepts it.
11. Set the delays. Kit counts each delay **from the previous email**, not from signup *(verify on the
    first email you set up; if Kit shows "days after subscribing", use the `day` values as they are)*:

    | Newsletter | `day` in the files | Delay to enter in Kit |
    |---|---|---|
    | Money Made Simple | 0, 1, 3, 5, 7, 9, 12, 15, 18, 21 | 0, 1, 2, 2, 2, 2, 3, 3, 3, 3 |
    | Scam Decoded | 0, 1, 3, 5, 7, 10, 14 | 0, 1, 2, 2, 2, 3, 4 |
    | 1099 Money | 0, 2, 4, 6, 8, 11, 14 | 0, 2, 2, 2, 2, 3, 3 |

12. Replace the placeholders before saving: 1099 Money's `{{download_url}}`, `{{calculator_url}}`,
    `{{tracker_url}}`, `{{price}}`; Money Made Simple's product link and the launch code only if the
    launch is really on (no countdowns or ended discounts). Send each email to yourself first with
    Kit's **Preview > Send test**.
13. Sequence settings: **Exclude subscribers tagged `buyer`**, so buyers stop getting the pitch emails.
    Set the send window to the morning in the reader's time zone if Kit offers it.

### E. The one visual automation

14. **Automate > Visual automations > New**, named `Welcome flow`:

    ```
    Entry:   Joins form <the form>
      -> Add tag  lead:<magnet>
      -> Add tag  in-welcome
      -> Subscribe to sequence  Welcome
      -> Event: completes sequence Welcome
      -> Remove tag  in-welcome
    ```

    The weekly issue goes to everyone **without** `in-welcome` (step 17), so nobody gets a broadcast and a
    welcome email on the same day. That matches the factory's own `min_gap_hours` rule.

### F. Buyers (sales are on Gumroad)

15. Add the `buyer` tag on purchase in one of two ways:
    - **Zapier (free tier):** Gumroad "New Sale" > Kit "Tag Subscriber" (`buyer`, plus `bought:<slug>`).
    - **No Zapier:** once a week, export Gumroad customers to CSV and import them into Kit with
      **Import > CSV > Add tag `buyer`**. Kit matches existing subscribers by email.
16. **1099 Money buyers sequence:** put its 3 emails in **Gumroad > Workflows** on the Quarterly Tax
    Tracker product (day 0, 3, 7), not in Kit. Gumroad sends them to buyers for free, so Kit's single
    sequence stays the welcome one. If 1099 Money later moves to Kit Creator ($39 at 1k), move them across.

### G. Weekly issues

17. **Send > Broadcasts > New:** paste the week's issue (`site/content/newsletter/` for Money Made Simple,
    `sites/scam-decoded/content/newsletter/` for Scam Decoded, which sends on Thursdays). Recipients:
    **all subscribers, excluding tag `in-welcome`**. Schedule a week ahead. Re-check every number and
    official URL in the issue that week, as the newsletter README asks.

### H. Recommendations (the money part)

18. **Grow > Creator Network:** fill in the profile (one line on who it's for, the niche, the cadence)
    and turn on recommendations, which show on the thank-you step after someone confirms.
19. Recommend 3 newsletters we'd honestly send a friend to (start from the swap list below). Only list
    ones that fit: anything that sells trading signals or "get rich" content breaks our own guardrails.
20. **Paid recommendations (Creator plan only; on Free use SparkLoop partner links, `thank-you-offers.md`):** in the Creator Network settings, enable paid recommendations, connect
    SparkLoop and a Stripe account, and wait for approval (usually within a day). Only add paid partners
    who pass the same check as step 19. Being paid doesn't change the rule.
21. Ask the newsletters you recommend to recommend you back (free swap). That's the point of the list.

### I. Keep the factory from sending twice

22. Brands that use Kit keep the factory's own sequence engine (`brands/sequences/*.yaml`,
    `factory sequence-*`) in **dry-run**, which is the default. Leave `FACTORY_DRY_RUN` unset for them so
    the same person never gets the welcome from both. Anyone who signed up through the factory's
    `/subscribe/` endpoint can be moved over with the factory's CSV export and **Kit > Import**
    (confirmed subscribers only, tagged `lead:<magnet>`).

### J. Dinero Simple

23. Do the same in a separate Kit account, with the form text, incentive email and footer in Spanish
    (all editable in Kit). It has no lead magnet or sequence yet. The Scam Decoded sequence translated
    and re-checked by a native speaker is the quickest start, since the draft community posts already
    lead with scams.

## 3. 20 newsletters for cross-promotion swaps

Found 2026-11-07 on newsletter directories (InboxReads, Reletter) and the newsletters' own pages. Subscriber
counts are only given where a source published one; the directories hide the rest behind a paywall.
**Nothing has been sent to anyone.** Open each one, read two recent issues, and check it's still sending
before you ask.

**How a swap works:** a free one is a mutual recommendation (Kit Creator Network, beehiiv recommendations or
Substack recommendations) or one line in each other's issue. Ask newsletters within about 3x of our size;
the big ones are listed as later targets. Never swap with anyone selling trading signals, "guaranteed"
returns or debt-settlement promises. Recommending them would break our own guardrails.

### Money Made Simple (budgeting, debt, first investing)

| # | Newsletter | Who / platform | Size and cadence (source) | Why it fits |
|---|---|---|---|---|
| 1 | **Blogging Away Debt** | James Hendrickson; beehiiv | Daily ([InboxReads](https://inboxreads.co/n/blogging-away-debt)) | Debt payoff and budgeting: our day-9 avalanche/snowball audience |
| 2 | **Saving Advice** | Same publisher as #1; beehiiv | Daily ([InboxReads](https://inboxreads.co/n/saving-advice)) | Personal finance and retirement tips. One contact covers #1 and #2 |
| 3 | **Grocery Coupon Guide** | beehiiv | Not stated ([InboxReads](https://inboxreads.co/new-beehiiv-personal-finance-newsletters)) | Spending-cut readers, the 7-Day Reset's day-2 crowd |
| 4 | **Money Tips Money Hacks** | Not stated | Not stated (InboxReads; [Reletter](https://reletter.com/publications/money-tips-money-hacks)) | "Earn more, save more" general money tips |
| 5 | **Front of the Check** | Not stated | Not stated (InboxReads) | Income-first money: also fits 1099 Money |
| 6 | **Break Your Budget** (Michela Allocca) | Substack | Creator with ~911K on TikTok (see `creators.md`) | Budgeting and credit for young adults, our exact audience. Later target |
| 7 | **Humphrey Yang's newsletter** | Free newsletter on his site | Creator with ~3.4M on TikTok (`creators.md`) | "Money basics explained simply". Later target |
| 8 | **Young Money** (Jack Raines) | beehiiv | 35,000+ in Mar 2023, weekly; got 600 readers in 4 days from recommendations ([beehiiv case study](https://www.beehiiv.com/blog/case-study-young-money-jack-raines)) | Young people, money and careers. Later target, and proof that recommendations work |
| 9 | **Clever Girl Finance** | Weekly on Tuesdays | 50,000+ women aged 25-65, 50% average open rate ([sponsor page](https://www.clevergirlfinance.com/sponsor/)) | Budgeting and debt for women. Sells sponsorships; later target |
| 10 | **Money with Katie** | Katie Gatti Tassin; weekly | Not published ([Reletter](https://reletter.com/publications/money-with-katie)) | The best-known millennial finance letter. Aspirational only |

### Scam Decoded (scam awareness)

| # | Newsletter | Who / platform | Size and cadence (source) | Why it fits |
|---|---|---|---|---|
| 11 | **Safe Not Scammed** | Rebecca Morris; **Kit** | Weekly ([InboxReads](https://inboxreads.co/n/safe-not-scammed)) | Same niche, same platform: the easiest Creator Network swap on the list |
| 12 | **ScamBrief** | Andrea Rogers; beehiiv | Weekly ([InboxReads](https://inboxreads.co/n/scambrief)) | Trending scams, red flags, text/email/phone threats. Closest match to Scam Alert |
| 13 | **Cyber Safe Center** | Cassie Crossley; beehiiv | Weekly; last issue seen 23 Feb 2026, so check it's still active ([site](https://cybersafecenter.beehiiv.com)) | Everyday security and scams |
| 14 | **Senior Scam Alerts** | Seth Combs; beehiiv, plus a podcast and YouTube | Irregular; last issue seen 10 Nov 2025 ([site](https://senior-scam-alerts.beehiiv.com/)) | Over-60s and their families: our "Protect Your Parents" angle. Swap only if it's active again |
| 15 | **ScamBusters** | Breakthrough Consulting; own site | Free weekly ([page](https://scambusters.org/get-our-weekly-scambusters-newsletter)) | A long-running scam letter. Ask for a mention, not a platform swap |

### 1099 Money (freelancer taxes)

| # | Newsletter | Who / platform | Size and cadence (source) | Why it fits |
|---|---|---|---|---|
| 16 | **The Quarterly** | JTFM ("Just the Facts, Ma'am"); beehiiv | New: welcome post 18 Apr 2026 ([post](https://thequarterly.beehiiv.com/p/welcome-to-the-quarterly)) | Freelancer tax tips and quarterly deadline reminders. Same size as us, the ideal first swap |
| 17 | **Thriving Freelance: Gigs & Growth** | Harlow (freelancer software); beehiiv | Weekly ([post, 3 Dec 2025](https://meetharlow.beehiiv.com/p/stressed-about-taxes)) | Freelancers, creators, entrepreneurs; already writes about tax stress |

### Dinero Simple (Spanish)

| # | Newsletter | Who / platform | Size and cadence (source) | Why it fits |
|---|---|---|---|---|
| 18 | **Dinero en Español: El Boletín** | Miguel Gómez, CFP and EA, a planner for Latino business owners; Substack | Weekly; 55 issues, last one ~3 months before the listing was captured ([Reletter](https://reletter.com/publications/dinero-en-espanol-el-boletin)) | US Latino money in Spanish, written by a credentialed planner. The best fit for Dinero Simple |
| 19 | **Invierte Joven** | Spanish | 12,900+ subscribers (its own description), Sundays and Thursdays ([InboxReads](https://inboxreads.co/n/invierte-joven)) | Personal finance and investing basics for young readers |
| 20 | **Lectura Financiera** | beehiiv; weekly on Mondays | Not shown ([InboxReads](https://inboxreads.co/n/lectura-financiera)) | "Finanzas sin complicar." Spain-focused (ECB, Spanish mortgages), so use it for the mention, not for US advice |

**More partners as we grow:** once each list is live, the Kit Creator Network lists newsletters in the
same category that are looking for swaps. That's a better source than any directory, so
check it every month and add the good ones here.

### Swap request (draft, not sent)

> Subject: Recommendation swap? ({our newsletter} + {theirs})
>
> Hi {name}, I write {our newsletter}, a weekly {one-line description} for about {N} readers. I've been
> reading {theirs} (the {specific recent issue} one was great) and I think our readers would like it.
> Would you be up for a mutual recommendation? I'll add you to our sign-up recommendations this week
> either way. No pressure if it doesn't fit.
>
> {signoff}

Fill in the brackets with true details only: a real issue you read, and our real subscriber count.
