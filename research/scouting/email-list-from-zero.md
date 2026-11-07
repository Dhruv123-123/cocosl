# Growing an email list from zero with the free apps and tools

Written 2026-11-07. **Docs only.** This builds on `first-100-subscribers.md` (lead magnets per brand,
communities, swaps) and `sender-setup-guide.md` (groups, double opt-in, footer). It answers two questions:
which freebies convert best for money content, and where the signup should go on the free apps (PR #8's
`apps/`, read today on its branch).

## TL;DR

1. **The best freebie is the visitor's own result, kept.** On a calculator page, the offer that matches
   intent is "email me my numbers and a printable plan", not "join the newsletter". No neutral study ranks
   lead magnet types for finance. Every ranking we found comes from a vendor selling that type, so we
   don't quote one. What the data does support is relevance. Popupsmart's 28,674-campaign report found an
   offer (a discount code) nearly doubled the signup rate, 1.46% vs 0.75%, so a concrete thing beats a
   generic ask. For content sites, the concrete thing is the result or a printable.
2. **Never gate the result.** Show the answer first, then offer to send it. A gated calculator loses
   search traffic and trust, and the result is what earns the email.
3. **Where the signup goes:**
   - Right under the result (the main spot).
   - Once at the end of each guide.
   - On the thank-you page of each product.
   - Desktop only: an exit-intent popup.

   **No full-screen popup on mobile pages that people reach from Google.** Google's intrusive
   interstitials rule demotes those pages. Exit intent, desktop popups and popups on later pages are allowed.
4. **What "good" looks like:**
   - Across sites, signup boxes convert about **2-4% of viewers** (BDOW/Sumo: 2.1% floor, 3-8% well
     optimised; Popupsmart: median 0.83% of displays, top quarter 1.96%).
   - Finance had the highest median in Popupsmart's data, **2.22%**, but that's only 38 campaigns.
   - On a calculator page, aim for **3% of people who see a result**. `launch_thresholds.json` already
     flags anything under 2% of site visitors after 200 visits.
5. **The one real gap in the apps today: signups don't reach the email tool.** The apps post to
   **Netlify Forms** by default (`apps/scam-checker/signup.js`, `provider: 'netlify'`). That's free and
   unlimited on Netlify's credit plans, but it only stores the address. Nobody gets the welcome email
   until the addresses are moved into Sender's signup group, where the double opt-in automation runs. Fix
   it before launch; see "The plumbing" below.

## What to offer, per tool (all already built; only the wording and delivery change)

| Tool (PR #8) | Today's box | Change the offer to | Brand list |
|---|---|---|---|
| Money calculators (emergency fund, debt payoff, take-home pay, compound interest, 401(k) fees, student loans, rent vs buy, savings interest, tax refund, Roth vs Traditional) | The 7-Day Money Reset (`config.js` pitch), in a box under the calculator | **"Email me this plan"**: the inputs and result, plus the matching printable (emergency fund → the 8-week $1,000 plan; debt payoff → avalanche vs snowball sheet). The weekly email is the second line, not the headline | MMS |
| Credit card minimum calculator | Same | "Send me my payoff date and a 1-page payoff plan" | MMS |
| Budget app (`apps/budget`) | Pro upsell | A free "monthly money date" reminder email on the 1st, which also brings people back to the app | MMS |
| Scam checker (`apps/scam-checker`) | Signup in `signup.js` | **"Get 1 scam alert a week, short enough to forward to your parents"** (`first-100-subscribers.md`). Offer it after the check result, whatever the verdict | Scam Decoded |
| `/quiz/` and `/breached/` (Scam site) | Score, then signup | Keep it. Add "send my 5-step lock-down list" on `/breached/` | Scam Decoded |
| Freelance tax calculator, invoices (`apps/freelance-invoices`) | Signup | "Remind me 7 days before each quarterly deadline" | 1099 Money (when it launches) |
| Remittance cost and the Spanish calculators (`es/`) | Signup | Hold. Dinero Simple is paused, and the Spanish copy needs review first | Dinero |

**Copy rules for every box** (from `first-100-subscribers.md` and `thank-you-offers.md`):
- Say exactly what arrives and how often.
- Ask for an email only.
- Put the privacy line next to the button.
- On the thank-you page, show the freebie immediately as well as emailing it. Double opt-in delays the
  email, and people shouldn't wait for what they asked for.

## Where it goes on the page

| Spot | Why | Notes |
|---|---|---|
| **Directly under the result** | The moment of highest intent | Pre-fill the result into a hidden field, so the welcome email can include it if the tool supports it later |
| End of every guide or article | People who read to the end are the warmest | One box only. Don't add a sidebar box too |
| Product thank-you pages (Gumroad, Etsy delivery PDFs) | Buyers are the best subscribers | Etsy forbids off-site links in listings, but the PDF can carry the site URL (the products thread already handles Etsy's rules) |
| Desktop exit-intent popup | Allowed by Google's rule, and the most-converting trigger in BDOW's chart (3.8%) | Once per visitor per 30 days. **Never on mobile entry pages** |
| Link in bio and pinned posts | Social traffic, covered in `first-100-subscribers.md` | Link to the most popular calculator, not the home page |

**Mobile:** Popupsmart found mobile popups convert better than desktop (1.02% vs 0.57%), but Google's rule
is about mobile pages reached from search. So on mobile, use the inline box under the result. A small
bottom bar is acceptable only if it covers little of the screen and closes easily.

## The plumbing (fix before launch)

Pick one:

1. **Simplest:** set each app's `config.js` email provider to the email tool's own signup form.
   `signup.js` already posts to `email.action` for any provider other than Netlify. The config lists
   Buttondown, Kit, MailerLite and Formspree, **but not Sender**, which `newsletter-tool-decision.md`
   recommends. So check that Sender's embedded form accepts a plain form post; if it doesn't, use option 2.
   Done right, every signup lands in Sender's signup group and gets the double opt-in email. Test it with
   one address per brand.
2. **Keep Netlify Forms and forward:** a small Netlify Function adds each submission to the Sender group
   through Sender's API. This keeps the spam honeypot. It's code, so it belongs to the apps thread.
3. **By hand (not recommended):** export the Netlify Forms CSV weekly and import it to Sender. Untick
   "trigger automations" only for people who already got a welcome, per `sender-setup-guide.md`. People
   who never confirmed must get the double opt-in. Slow, and the welcome email arrives days late.

Option 1 or 2 before launch. Option 3 only as a stopgap.

## Measuring it

- Count **signups ÷ people who saw a result** per tool weekly (Netlify Forms gives the signups; the page
  view count gives a proxy for the denominator).
- After 200 result views, keep any box over 3%, and rewrite the offer on any box under 1.5% (BDOW's
  "below average" line).
- Test one thing at a time: the offer wording first, then the placement. The button colour last.

## Sources

Read 2026-11-07:
[Popupsmart popup conversion benchmark report](https://popupsmart.com/blog/popup-conversion-benchmark-report) (28,674 campaigns, Jan 2024-Sep 2026, updated 25 Sep 2026);
[BDOW (formerly Sumo): email signup rate benchmarks](https://bdow.com/stories/email-signup-benchmarks/) (10 Jun 2026; its 2.1% average is from Omnisend's 1.24B popup displays);
[Smashing Magazine: Google's intrusive interstitials guidelines](https://www.smashingmagazine.com/2017/05/intrusive-interstitials-guidelines-avoid-google-penalty/);
[Netlify credit-based pricing plans](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/) (form submissions unlimited, no credit cost);
PR #8's `apps/` (branch `claude/project-thread-3r16y2`, read today); `first-100-subscribers.md`,
`sender-setup-guide.md`, `thank-you-offers.md`, `launch_thresholds.json` on PR #2.
