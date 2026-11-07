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
- [ ] Analytics: Plausible (cookieless) is on every page, set by `site.json` > `analytics.plausible_domain` (default `moneymadesimple.netlify.app`; env `PLAUSIBLE_DOMAIN` overrides, empty turns it off). Add that site in Plausible with goals `Product Click`, `Affiliate Click`, `Signup` and `Outbound Link: Click` (see `docs/UTM.md` section 3). Buy buttons and affiliate links carry the event classes; signups send `Signup` with a `form` property.
- [ ] Only set `sale_price` on a product while a launch price is actually running. No fake countdowns.
- [ ] Submit `https://<your-site>/sitemap.xml` in Google Search Console and Bing Webmaster Tools.
- [ ] Proofread the facts: every article lists its sources. Contribution limits and rates change; re-check
      the IRS limits each November.

## Comparison pages (affiliate)

`content/compare/` holds 8 comparison pages at `/compare/` (high-yield savings, budgeting apps, credit-builder
cards, robo-advisors, bill negotiation, identity theft protection, balance transfer cards, Rocket Money vs YNAB
vs Monarch). Each has a side-by-side table, an FTC disclosure box at the top, and a "Checked as of" date with
a note to verify rates. Update `as_of` whenever you re-check a page.

Links are written as `[text](aff:sofi)`. The key points to `site.json` > `programs`:

- `affiliate_url` empty (now): the link goes to the provider's official site, with no commission and no
  "sponsored" label, and the disclosure says we earn nothing from the page.
- Paste your approved link into `affiliate_url`: the link becomes `rel="sponsored"`, sends a Plausible
  `Affiliate Click`, and the disclosure names that company automatically.
- Payout notes from `research/02-affiliate-programs.md` are kept beside each program for reference.
- `compliance_review: required` (robo-advisors): the build prints a reminder when a broker/adviser link
  is paid, because FINRA/SEC rules mean the firm may need to approve the page first.

## Start here, resources and the quiz

- `/start/` (`content/pages/start.md`): hub page with five "sounds like me" paths into articles, comparisons and the reset.
- `/resources/`: built from `site.json` > `programs` (with `category`, `blurb`, `compare`) plus `free_tools`. Each
  tool shows "affiliate" or "no affiliation" from its affiliate slot, so the page stays truthful as you join programs.
- `/quiz/` (`content/quiz.json` + `static/quiz.js`): "What's your money personality?", 6 questions, 4 results
  (Avoider, Spender, Juggler, Cautious Saver), each with three linked moves and the 7-Day Money Reset signup.
  Signups are tagged `quiz-<result>` so you can segment emails; Plausible gets a `Quiz Complete` event.
  Linked from the home hero, the link-in-bio page and the footer.

## Social sharing and Pinterest

Every page has Open Graph and Twitter tags (title, description, image with size and alt text).
Articles and comparisons add `article:published_time`, `article:modified_time`, `article:author` and
`article:section`; products add `product:price:amount`/`currency` and availability. That's what Pinterest
reads for article and product rich pins: claim the domain in Pinterest, then rich pins apply automatically.

## Affiliate articles from the content thread

19 review and how-to articles from the content thread are in `content/blog/` (this PR is now the only copy;
see `AFFILIATE_ARTICLES.md` for the pre-publish checklist). Three of them (how to open a high-yield savings
account, how to choose a budgeting app, are robo-advisors worth it) target "how to" keywords so they feed the
comparison pages instead of competing with them. They link out through `/go/<slug>/` redirect pages made from `go-links.json`.

- **One place for approved links:** paste a tracking link into `go-links.json` > `affiliate_url` and run
  `python3 site/tools/make_go_links.py`. The build also copies it into the matching `site.json` program, so
  comparison pages, the resources page and their disclosures update too.
- **No duplicates:** `site.json` > `blog_redirects` retires blog slugs a comparison page already covers
  (best budgeting apps, best HYSAs, best robo-advisors, Monarch vs YNAB). Those articles are skipped even if
  present, links to them are rewritten, and the old URL 301-redirects (`_redirects` on Netlify, a noindex
  stub elsewhere).
- **Cross-links:** `site.json` > `article_compare` adds a "Compare your options" box to an article and a
  "Go deeper" list on the comparison page.

## Newsletter archive

Each weekly issue is a Markdown file in `content/newsletter/` (front matter: `issue`, `date` = send date,
`title`, optional `seo_title`, `description`, `subject`, `preheader`). The build makes:

- `/newsletter/`: the archive (an honest "first issue goes out on ..." note until one has been sent), with signup.
- `/newsletter/<slug>/`: one page per issue, with older/newer links, Article JSON-LD and the signup box.
- `/newsletter/feed.xml`: RSS 2.0 with the full issue in `content:encoded`, for feed readers and for
  RSS-to-email (Kit, MailerLite and Buttondown can all send from a feed). The articles feed stays at `/feed.xml`.
- `public/emails/newsletter/<slug>/email.html`: a paste-ready email of every issue, scheduled ones included.

An issue only goes public on a build on or after its `date`, so write ahead, send it from your email provider
that day, and let the site catch up. Netlify rebuilds only on a push, so add a build hook and save it as the
repo secret `NETLIFY_BUILD_HOOK`; `.github/workflows/netlify-rebuild.yml` pings it every Thursday. The
GitHub Pages workflow has the same weekly schedule. Preview scheduled issues locally with
`NEWSLETTER_SHOW_SCHEDULED=1 python3 site/build.py`, or pretend it's another day with `BUILD_DATE=2026-11-20`.

Seven issues are written and scheduled (weekly, Nov 12 to Dec 24, 2026). They aren't in the welcome sequence; send
them to everyone on the list.

## Budget by salary and cost of living by city

`pseo.py` builds 47 pages from two data files, so every number on them is computed, not typed:

- `/budget/<salary>-salary/` for 20 salaries ($25k to $200k) plus the `/budget/` hub: 2026 take-home pay
  (federal maths identical to the take-home pay calculator), Texas / North Carolina / California / NYC
  side by side, a four-line monthly plan, which of the 25 cities' rents fit, emergency fund and 401(k) maths,
  bracket explanation, FAQ schema.
- `/cost-of-living/<city>/` for the 25 largest US cities plus the `/cost-of-living/` hub: HUD fair market
  rent, salary needed at 30% of gross, take-home after state and city tax at six salaries, a monthly budget,
  rank against the other 24 cities, FAQ schema and sources.

Every page links to the take-home pay calculator (PR #8), pre-filled with the page's salary and state rate.
Set its address in `site.json` > `calculators_url` (default `https://moneymadesimple.netlify.app/calculators`,
the same URL as the calculator's own `config.js`). If the calculators end up somewhere else, change it there.

**Update every year:** `content/data/tax_rules.json` each November (federal, state and city tax rules) and
`content/data/cities.json` each October, when HUD publishes new fair market rents. **Before promoting these
pages:** the rents were read from sites that republish HUD's tables (HUD's own site was unreachable from the
build machine), so spot-check a few against HUD's FMR tool. Oklahoma City and Las Vegas are still FY2026
figures, and Indianapolis uses Marion County's long-standing 2.02% rate; confirm both.

## Money questions (/ask/)

`content/ask.md` is one page of 30 short Q&As (`## Group`, then `### Question` and the answer), with a jump list,
a link to each answer and FAQPage schema. The questions were picked so they don't repeat an article, a comparison
page, a newsletter issue or any article FAQ; `tests/test_site.py` checks every new question against those titles
and FAQs, so the build stays free of near-duplicates. Tokens in answers: `{month:50000}` / `{paycheck:50000}`
(take-home from `pseo.py`, so the numbers match the salary pages), `(calc:take-home-pay)` / `(calc:debt-payoff)`
(the calculators), `(shop:<slug>)` (that card on /shop/; unknown slugs fail the build). Every answer ends with a
"Tools:" line.

## Pinterest pin images

`python3 tools/make_pins.py` renders the 10 designs in `PINS.md` to `pins/NN-<campaign>.png` (1000×1500) and
writes `pins/pins.csv` with each pin's title, description, alt text, board and tracked link, ready for Pinterest's
bulk upload or to paste by hand. The $50k numbers come from `pseo.py`; re-run after the tax data or shop prices
change. Needs Playwright and Chromium (`pip install playwright && python -m playwright install chromium`).

## Shop

`/shop/` lists the products thread's whole catalog (PR #6): the guide-and-spreadsheet kits and the Google
Sheets / Notion templates (Gumroad), the printables (Etsy), and the bundles first, with "save $X" against buying
separately. Every buy button sends a Plausible `Product Click` with `product` and `store` properties.

- The catalog lives in `content/shop.json`, made by `python3 site/tools/import_shop.py <content-factory folder>`
  from `products/`, `templates/` and `etsy/` (it also makes the 360px card images in `static/img/shop/`).
  Re-run it when the products thread changes a name, price or blurb.
- **Store links are placeholders** until the stores exist: Gumroad items link to
  `site.json > stores.gumroad` + `/l/<slug>`, Etsy items to `stores.etsy` + a shop search. Set the two store
  URLs in `site.json`, and paste exact listing links into `shop.json` as `url` (Gumroad) or `etsy_url`;
  the import tool keeps links you've pasted.

## Debt payoff timelines

`/debt-payoff/<amount>-debt/` for $2,500 to $50,000 (10 pages) plus the `/debt-payoff/` hub, built by
`pseo.py`. Each page uses a hypothetical mix of cards and loans (bigger amounts add a personal loan, car loan
and student loan) and simulates both strategies month by month with the same maths as the calculators' debt
payoff tool: results at five payment levels, which debt is cleared when, a yearly balance schedule, the monthly
payment for debt-free in two or three years, and FAQ schema. The "Run these numbers" button opens the debt payoff
calculator pre-filled with the page's debts.

## Email-capture A/B test

`site.json > ab_test` runs a two-by-two test on the signup offer: two hero versions on the home page
(headline + offer line) and two lead-magnet titles (in the home hero, the `/free/` page and every
"Free download" box). Each visitor is assigned one of four combinations (AA, AB, BA, BB) at random, stored for
90 days in a first-party cookie `mms_ab` (the privacy page says so). Without JavaScript everyone sees A.

**Reading the result in Plausible:** add the goals `AB Exposure` and `Signup`, then the custom properties
`variant`, `hero`, `magnet` and `test`. Open the `Signup` goal and break it down by `variant`, and compare
with the `AB Exposure` count per variant: signup rate = Signups / Exposures. Compare `hero` A vs B and
`magnet` A vs B the same way. As a rule of thumb, wait for at least ~100 signups per arm before calling it;
small differences on a few dozen signups are noise.

**Preview** a variant with `?ab=ba` (hero B, magnet A); previews don't set the cookie. **End the test:** set
`active` to `false`, put the winning copy in the `a` slots (and in `lead_magnet.title` if title B wins),
and start a new test by changing `id`. The PDF and welcome email still say "The 7-Day Money Reset"; if title B
wins, rename them too.

## Accessibility

The site targets WCAG 2.2 AA. Two layers of checks:

- **Every build** (`tools/check_site.py`, so Netlify, GitHub Pages and CI): `<html lang>`, alt text on every
  image (`alt=""` for decoration), a label on every form field, no empty links, buttons or table headers, no
  duplicate ids. `tests/test_site.py` also checks the colour tokens in `style.css` against AA contrast.
- **Full audit** (`tests/test_a11y_browser.py`, run by `.github/workflows/a11y.yml` on PRs that touch `site/`):
  axe-core on every page at 1280px and 390px, no sideways scrolling on phones, keyboard-only use (skip link,
  a visible focus ring on every control, the quiz), and 44px tap targets for the nav, forms and buttons.
  Run it locally with Playwright and `AXE_PATH` (see the test's docstring).

When you add a table, an image or a form field in Markdown or `site.json`, the build will tell you if
something's missing. Pinterest pin designs for the main pages are in `PINS.md`.

## Deploy check

`python3 site/tools/check_site.py` runs after every build on Netlify and GitHub Pages, and in the tests.
It fails the deploy on broken internal links or #anchors, missing title/description/canonical/og:image/h1,
insecure assets, or a page over budget (HTML 100 KB; HTML + same-site CSS/JS/images 350 KB; any image
200 KB), and prints the five heaviest pages. It warns on long or duplicate titles and descriptions.
Add `--external` locally to HEAD-check every outbound link.

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
