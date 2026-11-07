# Money Made Simple website and email funnel

A complete static site for the brand, a free lead magnet, and a 10-email welcome and nurture sequence
that sells the products. No server, no database, no monthly cost: it deploys free to Netlify or GitHub Pages.

```
Social post / link in bio ──> /links/ or any article
            │
            ▼
   /free/  "The 7-Day Money Reset" (email form on every page)
            │  signup goes to your email provider
            ▼
   /free/thanks/  instant PDF download + product cards
            │
            ▼
   10 emails over 21 days (provider automation) ──> /products/the-20-minute-budget/ ──> Gumroad checkout
            │
            ▼
   weekly newsletter
```

## What's here

| Path | What it is |
|---|---|
| `build.py` | The site generator. Python standard library only; `python3 site/build.py` writes `site/public/`. |
| `site.json` | Brand name, site URL, social links, **email provider**, lead magnet copy, affiliate links. |
| `content/blog/` | 13 SEO articles (Markdown). Each has a target keyword, sources, FAQ (becomes FAQ rich results), and internal links. |
| `content/products/` | Product pages. One `.md` per product; add a file to add a product. |
| `content/pages/` | About, Disclosures, Privacy, Terms. |
| `content/emails/` | The 10-email sequence (subject, preview text, send day, body). |
| `lead-magnet/` | Source for the free PDF (HTML, printed to PDF by `tools/make_assets.py`). |
| `static/` | CSS, JS, images, and `downloads/the-7-day-money-reset.pdf`. |
| `public/` | The built site, committed so you can also drag-and-drop it to Netlify Drop. |

Pages built: home, `/blog/` plus one page per topic, 13 articles, `/products/` and each product, `/free/`
(lead magnet landing page), `/free/thanks/` (download page), `/links/` (link-in-bio page that replaces
the old one), about and legal pages, `404.html`, `sitemap.xml`, `robots.txt`, `feed.xml` (RSS), and
`/emails/` (a private, unlinked, noindexed preview of the sequence).

SEO built in: one target keyword per article, title and description tags, canonical URLs, Open Graph
and Twitter cards, Article + Breadcrumb + FAQ + Product + Organization structured data, sitemap,
internal links between related articles, fast pages (no frameworks, ~10 KB CSS+JS).

## 1. Deploy it (free), pick one

### Netlify (recommended: signups work with zero setup)

1. Log in at netlify.com > **Add new site > Import an existing project** > GitHub > pick `cocosl`.
2. Netlify reads `netlify.toml` at the repo root (base `site`, command `python3 build.py`, publish `public`).
   Click **Deploy**.
3. Site settings > **Domain management** to rename it (e.g. `moneymadesimple.netlify.app`) or add your own domain.
4. Forms > **Enable form detection**, then redeploy once. Signups now appear under Forms, and you can
   turn on email notifications or a Zapier/Make hook to push them into your email provider.

No Git? Run `python3 site/build.py` locally and drag `site/public/` onto app.netlify.com/drop.

### GitHub Pages

1. Repo **Settings > Pages > Source: GitHub Actions**.
2. Merge to `main`. `.github/workflows/pages.yml` builds and publishes to
   `https://<user>.github.io/cocosl/` (sub-paths are handled).
3. GitHub Pages can't receive form posts, so set an email provider first (step 2 below) via
   **Settings > Secrets and variables > Actions > Variables**: `EMAIL_PROVIDER` and `EMAIL_FORM_ACTION`
   (and `SITE_URL` if you add a custom domain).

## 2. Connect an email provider (this is what sends the 10 emails)

The forms post to whichever provider you set in `site.json` > `email.provider` (or the env vars
`EMAIL_PROVIDER` / `EMAIL_FORM_ACTION`, which win). After any signup the visitor lands on `/free/thanks/`
and gets the PDF immediately.

| `provider` | `action` to paste | Notes |
|---|---|---|
| `netlify` (default) | none | Captures emails on Netlify. Forward them to a provider for the sequence. |
| `mailerlite` | the form's `action` URL from MailerLite's embedded form HTML | Free plan has included automations; check the current subscriber cap. |
| `kit` | `https://app.kit.com/forms/<FORM_ID>/subscriptions` (copy from Kit's form embed code) | Field `email_address` is set automatically. Check whether your plan includes sequences/automations. |
| `buttondown` | `https://buttondown.com/api/emails/embed-subscribe/<username>` | Simple and privacy-friendly; check its free-tier limits. |
| `factory` | `https://studio.<your-domain>/subscribe/money-made-simple` | The factory server in this repo: double opt-in, CSV export to any provider. |

Plan limits change; check the provider's pricing page before choosing. Whichever you use, turn on
**double opt-in**, and put your **postal address** in the provider's footer (required by CAN-SPAM).

## 3. Load the sequence

Every email exists three ways after a build:

- `public/emails/sequence.json`: all 10, with `send_on_day`, subject, preheader, HTML and plain text.
- `public/emails/<name>/email.html` and `email.txt`: paste straight into the provider's HTML or text editor.
  Links are absolute (they use your site URL), so **build with the real URL first**
  (`SITE_URL=https://your-site python3 site/build.py`).
- `https://<your-site>/emails/`: a private preview of all 10 for proofreading.

In the provider, create an automation: trigger "subscribes to form", then emails 1-10 with these delays:

| # | Day | Subject | Job |
|---|---|---|---|
| 1 | 0 | Your 7-Day Money Reset is here | Deliver the PDF, ask for a reply |
| 2 | 1 | The number most people get wrong | Day 1-2 of the reset |
| 3 | 3 | Why your last budget died in week three | The weekly-number idea, soft product mention |
| 4 | 5 | Car registration isn't an emergency | Sinking funds |
| 5 | 7 | The full system (if you want it done for you) | **Main pitch: The 20-Minute Budget** |
| 6 | 9 | Avalanche vs snowball: the real difference was $106 | Debt payoff, debt planner mention |
| 7 | 12 | Paid in full, score still dropped? | Credit value email |
| 8 | 15 | $100 a month doesn't sound like investing | Investing value email |
| 9 | 18 | "Will a spreadsheet actually work for me?" | **Objections + second pitch** |
| 10 | 21 | Three weeks in: what to do next | Recap, last mention, hand off to weekly newsletter |

Tip: add a rule that skips emails 5, 9 and the product line of 10 for people who've already bought
(most providers can tag buyers via a Gumroad/Lemon Squeezy/Stripe integration or Zapier).

## 4. Before you go live: replace the placeholders

- [ ] `content/products/the-20-minute-budget.md` > `buy_url`: your real Gumroad / Lemon Squeezy link.
- [ ] `site.json` > `url`, `contact_email`, `socials`, and `affiliates` (leave empty until you have real, approved affiliate links; they render with an "affiliate" label and `rel="sponsored"`).
- [ ] `site.json` > `email` provider (step 2).
- [ ] Optional analytics: paste a privacy-friendly snippet (e.g. Plausible, GoatCounter, Cloudflare Web Analytics) into `site.json` > `analytics_snippet`.
  For Plausible, set `plausible_domain` instead: it loads the outbound-links + tagged-events script and tags buy buttons (`Product Click`), affiliate links (`Affiliate Click`) and signups (`Signup`). `utm_emails: true` adds UTM to the site links in the exported emails.
- [ ] Only set `sale_price` on a product while a launch price is actually running. No fake countdowns.
- [ ] Submit `https://<your-site>/sitemap.xml` in Google Search Console and Bing Webmaster Tools.
- [ ] Proofread the facts: every article lists its sources. Contribution limits and rates change; re-check
      the IRS limits each November.

## Everyday edits

- **New article:** copy any file in `content/blog/`, change the front matter (`title`, `description`, `date`,
  `pillar`, `keyword`, `sources`), write Markdown. `{{signup}}` drops in the lead magnet box,
  `{{product:the-20-minute-budget}}` a product card. A `## Common questions` section with `###` questions
  becomes FAQ structured data automatically.
- **New product:** add `content/products/<slug>.md` (copy the existing one). `status: coming-soon` shows a
  waitlist form instead of a buy button; `status: draft` hides it; `order` sets the position.
- **Preview locally:** `SITE_URL=http://localhost:8080 python3 site/build.py --serve`.
- **Change the PDF or images:** edit `lead-magnet/the-7-day-money-reset.html` or `tools/make_assets.py`, then
  `pip install playwright && playwright install chromium && python3 site/tools/make_assets.py`.
- **Tests:** `python -m pytest tests/test_site.py` builds the site at a root URL and a sub-path and checks
  every internal link and asset resolves.

## Compliance notes

Same rules as the rest of the factory (`docs/COMPLIANCE.md`): affiliate links labelled, AI use disclosed
in the footer and on `/disclosures/`, no testimonials until real buyers give permission, no income or
return promises (all projections are labelled hypothetical), "not financial advice" on every page and email,
honest refund policy, unsubscribe and postal address in every email.
